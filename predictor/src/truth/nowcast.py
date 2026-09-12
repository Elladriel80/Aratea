"""Nowcast same-day : thermomètre déjà vu + risque du reste du jour.

FR : À une heure h, le max (ou le min) final est
  final = max(max_déjà_vu, reste)   ou   min(min_déjà_vu, reste)
où `reste` vient de la prévision horaire HRRR si elle est là, sinon
d'une largeur simple selon les heures encore ouvertes. On ne fabrique
pas le thermomètre : s'il manque, on s'arrête.

EN : Same-day high/low = observed extreme so far combined with remaining
risk (HRRR hourly if present, else a documented hours-left width).
"""
from __future__ import annotations

import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from .lst_window import standard_utc_offset
from .synthetic_bins import Bin, _normal_cdf

MIN_EMPIRICAL = 20
ROUNDING_SIGMA = 0.5
FALLBACK_BASE_F = 3.0
FALLBACK_HOURS = 12.0


def lst_day_end_utc(target: date, tz_name: str) -> datetime:
    """Premier instant UTC après la fin du jour climatologique LST."""
    off = standard_utc_offset(tz_name)
    nxt = datetime(target.year, target.month, target.day, tzinfo=timezone.utc) + timedelta(days=1)
    return nxt - off


def hours_left(target: date, tz_name: str, as_of: datetime) -> float:
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)
    end = lst_day_end_utc(target, tz_name)
    return max(0.0, (end - as_of).total_seconds() / 3600.0)


def fallback_sigma(hours: float) -> float:
    """Largeur documentée si HRRR manque. Ce n'est pas une observation.

    3 °F quand il reste 12 h, 0,5 °F (arrondi) quand la journée est finie.
    """
    if hours <= 0:
        return ROUNDING_SIGMA
    return max(ROUNDING_SIGMA, FALLBACK_BASE_F * min(1.0, hours / FALLBACK_HOURS))


def _norm_prob_between(mu: float, sigma: float, lo: Optional[float], hi: Optional[float]) -> float:
    if sigma <= 1e-12:
        if lo is not None and mu < lo:
            return 0.0
        if hi is not None and mu > hi:
            return 0.0
        return 1.0
    p_lo = _normal_cdf((lo - mu) / sigma) if lo is not None else 0.0
    p_hi = _normal_cdf((hi - mu) / sigma) if hi is not None else 1.0
    return max(0.0, min(1.0, p_hi - p_lo))


def prob_bin_nowcast(
    obs_so_far: float,
    rem_mu: float,
    rem_sigma: float,
    b: Bin,
    kind: str,
) -> float:
    """P(final dans le bin) avec final = max(obs, R) ou min(obs, R), R ~ N.

    Formule C1 : si le thermomètre a déjà dépassé le bin, la chance est 0.
    Si le thermomètre est déjà dans le bin, il reste dedans sauf si le
    reste de la journée le fait sortir. Si le thermomètre est encore
    en dessous (max) ou au-dessus (min), il faut que le reste y arrive
    sans trop dépasser.
    """
    lo = float(b.lower) - 0.5 if b.lower is not None else None
    hi = float(b.upper) + 0.5 if b.upper is not None else None
    if kind == "max":
        if hi is not None and obs_so_far > hi:
            return 0.0
        if lo is not None and obs_so_far >= lo:
            # déjà dans le bin (ou au-dessus du bas) : on perd si R > hi
            if hi is None:
                return 1.0
            return _norm_prob_between(rem_mu, rem_sigma, None, hi)
        # obs encore sous le bin : R doit tomber dans le bin
        return _norm_prob_between(rem_mu, rem_sigma, lo, hi)
    # min
    if lo is not None and obs_so_far < lo:
        return 0.0
    if hi is not None and obs_so_far <= hi:
        if lo is None:
            return 1.0
        return _norm_prob_between(rem_mu, rem_sigma, lo, None)
    return _norm_prob_between(rem_mu, rem_sigma, lo, hi)


def remaining_params(
    obs_so_far: float,
    hours: float,
    hrrr: Optional[dict],
    empirical: Optional[tuple[float, float]],
    hrrr_sigma: Optional[float] = None,
) -> tuple[float, float, str]:
    """(mu, sigma, source) du reste de journée. Jamais une fausse lecture."""
    if hours <= 0:
        return obs_so_far, ROUNDING_SIGMA, "day_closed"
    if hrrr is not None:
        sig = hrrr_sigma if hrrr_sigma is not None else 1.5
        return float(hrrr["extreme_f"]), max(ROUNDING_SIGMA, sig), "hrrr_previous_day1"
    if empirical is not None:
        rise, sig = empirical
        return obs_so_far + rise, max(ROUNDING_SIGMA, sig), "empirical_train"
    return obs_so_far, fallback_sigma(hours), "hours_left_width"


class EmpiricalRemaining:
    """Hausse (ou baisse) encore possible, apprise sur les jours TRAIN.

    Pour un max : rise = max(0, officiel − max_déjà_vu).
    Pour un min : drop = min(0, officiel − min_déjà_vu)  (négatif = encore plus bas).
    Groupé par (station, variable, heure UTC de la capture).
    """

    def __init__(self):
        self.pairs: dict[tuple, list[float]] = defaultdict(list)
        self.global_pairs: dict[tuple, list[float]] = defaultdict(list)

    def add(self, station: str, variable: str, utc_hour: int, obs_so_far: float,
            official: float) -> None:
        if variable == "temp_max":
            delta = max(0.0, official - obs_so_far)
        else:
            delta = min(0.0, official - obs_so_far)
        self.pairs[(station, variable, utc_hour)].append(delta)
        self.global_pairs[(variable, utc_hour)].append(delta)

    def get(self, station: str, variable: str, utc_hour: int) -> Optional[tuple[float, float]]:
        vals = self.pairs.get((station, variable, utc_hour), [])
        if len(vals) < MIN_EMPIRICAL:
            vals = self.global_pairs.get((variable, utc_hour), [])
        if len(vals) < MIN_EMPIRICAL:
            return None
        mu = statistics.fmean(vals)
        sig = statistics.pstdev(vals) if len(vals) > 1 else FALLBACK_BASE_F
        return mu, max(ROUNDING_SIGMA, sig)


def kind_for_variable(variable: str) -> str:
    if variable == "temp_max":
        return "max"
    if variable == "temp_min":
        return "min"
    raise ValueError(f"variable inconnue pour le nowcast : {variable}")
