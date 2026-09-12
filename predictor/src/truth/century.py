"""Climatologie longue par station et jour de calendrier / Long station climatology.

FR : Pour une date cible, on regarde uniquement les années STRICTEMENT
antérieures. On compte ce qui s'est passé le même jour (et les jours
voisins) à la même station. Rien n'est inventé.

EN : Point-in-time calendar-day distribution on the official station
series. Previous years only.

La tendance est une pente descriptive : moyenne annuelle des années assez
complètes (≥ 300 jours) contre l'année. Ce n'est pas une étude climatique.
Un déménagement d'instrument ou la ville qui chauffe peuvent produire la
même pente.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from datetime import date, timedelta
from typing import Iterable, Optional

from .ghcn_daily import GhcnDay
from .synthetic_bins import Bin

MIN_DOY_OBS = 15
MIN_TREND_YEARS = 15
COMPLETE_YEAR_DAYS = 300
LAPLACE = 0.5


def _value(d: GhcnDay, variable: str) -> Optional[int]:
    if variable == "temp_max":
        return d.high_f
    if variable == "temp_min":
        return d.low_f
    raise ValueError(f"variable inconnue: {variable}")


def md_key(d: date) -> str:
    return f"{d.month:02d}-{d.day:02d}"


def window_dates(target: date, year: int, window_days: int) -> list[date]:
    """Jours de `year` à ±window_days du (mois, jour) cible. 29 fév → 28 fév."""
    try:
        anchor = target.replace(year=year)
    except ValueError:
        anchor = date(year, 2, 28)
    out: list[date] = []
    for k in range(-window_days, window_days + 1):
        try:
            out.append(anchor + timedelta(days=k))
        except OverflowError:
            continue
    return [d for d in out if d.year == year or window_days >= 0]


def index_by_date(days: Iterable[GhcnDay]) -> dict[date, GhcnDay]:
    return {d.valid: d for d in days}


def values_for_window(
    by_date: dict[date, GhcnDay], variable: str, target: date,
    window_days: int, before_year: int, years_back: Optional[int] = None,
) -> list[int]:
    """Valeurs des années < before_year, fenêtre calendrier autour de target.

    `years_back` borne la fenêtre aux `years_back` années juste avant
    before_year (pour comparer siècle vs 30 ans récents).
    """
    vals: list[int] = []
    years = sorted({d.year for d in by_date if d.year < before_year})
    if years_back is not None:
        years = [y for y in years if y >= before_year - years_back]
    for y in years:
        for dt in window_dates(target, y, window_days):
            rec = by_date.get(dt)
            if rec is None:
                continue
            v = _value(rec, variable)
            if v is not None:
                vals.append(v)
    return vals


def describe(vals: list[float]) -> Optional[dict]:
    if len(vals) < MIN_DOY_OBS:
        return None
    s = sorted(vals)
    n = len(s)

    def pct(p: float) -> float:
        if n == 1:
            return float(s[0])
        k = (n - 1) * p
        lo, hi = int(math.floor(k)), int(math.ceil(k))
        if lo == hi:
            return float(s[lo])
        return float(s[lo] * (hi - k) + s[hi] * (k - lo))

    sd = statistics.pstdev(s) if n >= 2 else 0.0
    return {
        "n": n,
        "mean": statistics.fmean(s),
        "median": statistics.median(s),
        "std": sd,
        "p10": pct(0.10),
        "p90": pct(0.90),
        "min": float(s[0]),
        "max": float(s[-1]),
    }


def empirical_prob(vals: list[int], b: Bin, laplace: float = LAPLACE) -> Optional[float]:
    """Fréquence historique du bin, lissage Laplace. None si trop peu d'obs."""
    if len(vals) < MIN_DOY_OBS:
        return None
    n_yes = sum(1 for v in vals if b.contains(float(v)))
    return (n_yes + laplace) / (len(vals) + 2 * laplace)


def doy_table(days: list[GhcnDay], variable: str, window_days: int = 0,
              before_year: Optional[int] = None) -> dict[str, dict]:
    """Stats par (mois-jour). `before_year` exclu (point-in-time)."""
    buckets: dict[str, list[int]] = defaultdict(list)
    for d in days:
        if before_year is not None and d.valid.year >= before_year:
            continue
        v = _value(d, variable)
        if v is None:
            continue
        if window_days == 0:
            buckets[md_key(d.valid)].append(v)
        else:
            # regroupé plus tard via values_for_window ; ici exact calendar day
            buckets[md_key(d.valid)].append(v)
    out: dict[str, dict] = {}
    for key, vals in buckets.items():
        desc = describe([float(x) for x in vals])
        if desc:
            out[key] = desc
    return out


def station_spread_summary(doy: dict[str, dict]) -> Optional[dict]:
    """Médiane, sur les 366 jours, de la moyenne et de l'écart-type."""
    if not doy:
        return None
    means = [r["mean"] for r in doy.values()]
    stds = [r["std"] for r in doy.values()]
    ns = [r["n"] for r in doy.values()]
    return {
        "n_calendar_days": len(doy),
        "typical_mean_f": statistics.median(means),
        "median_daily_std_f": statistics.median(stds),
        "p90_daily_std_f": sorted(stds)[int(round(0.9 * (len(stds) - 1)))],
        "median_n_per_doy": statistics.median(ns),
    }


def annual_means(days: list[GhcnDay], variable: str,
                 min_days: int = COMPLETE_YEAR_DAYS) -> list[tuple[int, float, int]]:
    """(année, moyenne, n) pour les années assez complètes. Pas d'année inventée."""
    by_year: dict[int, list[int]] = defaultdict(list)
    for d in days:
        v = _value(d, variable)
        if v is not None:
            by_year[d.valid.year].append(v)
    out: list[tuple[int, float, int]] = []
    for y in sorted(by_year):
        vals = by_year[y]
        if len(vals) >= min_days:
            out.append((y, statistics.fmean(vals), len(vals)))
    return out


def linear_slope(pairs: list[tuple[int, float]]) -> Optional[dict]:
    """Pente des moindres carrés : y = a + b·année. b en °F / an."""
    if len(pairs) < MIN_TREND_YEARS:
        return None
    xs = [float(x) for x, _ in pairs]
    ys = [float(y) for _, y in pairs]
    n = len(xs)
    xbar = statistics.fmean(xs)
    ybar = statistics.fmean(ys)
    varx = sum((x - xbar) ** 2 for x in xs)
    if varx <= 0:
        return None
    cov = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys))
    b = cov / varx
    a = ybar - b * xbar
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    sse = sum(r ** 2 for r in resid)
    sst = sum((y - ybar) ** 2 for y in ys)
    r2 = 1.0 - sse / sst if sst > 0 else 0.0
    return {
        "n_years": n,
        "first_year": int(xs[0]),
        "last_year": int(xs[-1]),
        "slope_f_per_year": b,
        "slope_f_per_decade": b * 10.0,
        "intercept": a,
        "r_squared": r2,
        "mean_first_half": statistics.fmean(ys[: n // 2]),
        "mean_second_half": statistics.fmean(ys[n // 2:]),
    }


def trend_report(days: list[GhcnDay], variable: str) -> dict:
    """Pente sur années complètes + écart 30 premières / 30 dernières si possible."""
    series = annual_means(days, variable)
    slope = linear_slope([(y, m) for y, m, _ in series])
    out: dict = {
        "variable": variable,
        "n_complete_years": len(series),
        "method": (
            f"moyenne annuelle des années avec au moins {COMPLETE_YEAR_DAYS} jours "
            "mesurés ; pente des moindres carrés (année → moyenne). "
            "Descriptive seulement."
        ),
        "slope": slope,
        "early30_vs_late30": None,
    }
    if len(series) >= 60:
        early = [m for _, m, _ in series[:30]]
        late = [m for _, m, _ in series[-30:]]
        out["early30_vs_late30"] = {
            "early_years": [series[0][0], series[29][0]],
            "late_years": [series[-30][0], series[-1][0]],
            "early_mean_f": statistics.fmean(early),
            "late_mean_f": statistics.fmean(late),
            "late_minus_early_f": statistics.fmean(late) - statistics.fmean(early),
        }
    elif series:
        out["early30_vs_late30"] = {
            "note": "moins de 60 années complètes : pas de comparaison 30 vs 30",
            "n_complete_years": len(series),
        }
    return out


# Seuil simple pour « le marché est bien plus sûr que l'histoire ».
# Favori marché ≥ 65 % alors que l'histoire met ce contrat à ≤ 40 %.
FADE_MARKET_MIN = 0.65
FADE_HIST_MAX = 0.40


def fade_trigger(market_p: float, hist_p: Optional[float]) -> bool:
    if hist_p is None:
        return False
    return market_p >= FADE_MARKET_MIN and hist_p <= FADE_HIST_MAX
