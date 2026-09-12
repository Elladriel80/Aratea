"""Comparaison jour par jour ERA5 (archive Open-Meteo) vs CLI station.

FR : Même calcul que l'audit A1. Si la requête longue échoue ou revient
vide, on découpe par année. Une station sans aucune paire comparable
est renvoyée avec une erreur lisible, jamais comme un tableau vide
silencieux.

EN : Day-by-day ERA5 vs CLI. Year-chunk fallback when the long request
fails or is empty. Empty comparisons are explicit errors.
"""
from __future__ import annotations

import statistics
from collections import defaultdict
from datetime import date
from typing import Optional

from src.truth.iem_cli import CliDay
from src.weather.open_meteo import DailyObservation, OpenMeteoClient


def _span_days(start: date, end: date) -> int:
    return (end - start).days + 1


def _fetch_era5(
    om: OpenMeteoClient,
    lat: float,
    lon: float,
    start: date,
    end: date,
    tz_name: str,
) -> tuple[list[DailyObservation], Optional[str]]:
    last_err: Optional[str] = None
    expected = _span_days(start, end)
    try:
        obs = om.historical_observations(lat, lon, start, end, timezone=tz_name)
        # Une série trop courte (rate-limit, coupure silencieuse) n'est pas
        # une mesure : on retente année par année.
        if obs and len(obs) >= int(0.8 * expected):
            return obs, None
        if obs:
            last_err = f"série ERA5 trop courte ({len(obs)} jours sur {expected})"
        else:
            last_err = "réponse Open-Meteo vide"
    except Exception as e:  # noqa: BLE001 — on retente par année
        last_err = str(e)

    collected: list[DailyObservation] = []
    year_errors: list[str] = []
    for year in range(start.year, end.year + 1):
        a = max(start, date(year, 1, 1))
        b = min(end, date(year, 12, 31))
        try:
            chunk = om.historical_observations(lat, lon, a, b, timezone=tz_name)
            collected.extend(chunk)
        except Exception as e:  # noqa: BLE001
            year_errors.append(f"{year}: {e}")
    if collected:
        return collected, None
    extra = "; ".join(year_errors)
    if extra:
        last_err = f"{last_err}; {extra}" if last_err else extra
    return [], last_err or "aucune observation ERA5"


def compare_era5_to_cli(
    om: OpenMeteoClient,
    meta: dict,
    truth: list[CliDay],
    start: date,
    end: date,
) -> dict:
    """Renvoie les stats par variable, ou {"error": ...} si rien à comparer."""
    obs, fetch_err = _fetch_era5(om, meta["lat"], meta["lon"], start, end, meta["tz"])
    era5 = {o.date: o for o in obs}
    rows: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for d in truth:
        o = era5.get(d.valid)
        if o is None:
            continue
        for var, cli_v, era_v in (
            ("high", d.high_f, o.temperature_max),
            ("low", d.low_f, o.temperature_min),
        ):
            if cli_v is None or era_v is None:
                continue
            rows[f"{var}:{d.valid.month:02d}"].append((era_v, float(cli_v)))
            rows[f"{var}:all"].append((era_v, float(cli_v)))

    if not rows:
        reason = fetch_err or (
            f"aucune date commune ERA5/CLI (ERA5 n={len(obs)}, CLI n={len(truth)})"
        )
        return {"error": reason}

    out: dict = {}
    for k, pairs in sorted(rows.items()):
        diffs = [e - c for e, c in pairs]
        exact = sum(1 for e, c in pairs if round(e) == c)
        out[k] = {
            "n": len(pairs),
            "bias_era5_minus_cli_f": round(statistics.fmean(diffs), 2),
            "mae_f": round(statistics.fmean(abs(x) for x in diffs), 2),
            "sd_f": round(statistics.pstdev(diffs), 2) if len(diffs) > 1 else None,
            "exact_share": round(exact / len(pairs), 3),
            "share_off_by_2_or_more": round(
                sum(1 for x in diffs if abs(x) >= 2) / len(pairs), 3
            ),
        }
    return out
