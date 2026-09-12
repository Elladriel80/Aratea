"""Jonction vérité CLI × ledger paper × prévisions déjà stockées.

FR : Construit un index (station, jour) → max/min officiels, puis le colle
sur les lignes du ledger paper et sur les points de prévision déjà écrits
dans data/truth/skill/forecast_points.json. N'invente rien : une ligne
sans jour CLI, sans valeur, ou sur une ancienne station (KORD / KIAH /
KDAL) est marquée non jointe avec une raison.

EN : Index CLI days by (station, date) and attach them to paper-ledger
rows and stored forecast points. Unjoinable rows keep an explicit reason.
"""
from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Optional

from src.config import LEDGER_DIR
from src.kalshi.resolution import infer_variable
from src.truth.iem_cli import CITY_TO_ICAO, kalshi_stations, station_for_series

PAPER_LEDGER = LEDGER_DIR / "paper_bets.csv"
BACKTEST_LEDGER = LEDGER_DIR / "paper_bets_backtest.csv"
FORECAST_POINTS = Path(__file__).resolve().parents[2] / "data" / "truth" / "skill" / "forecast_points.json"


def index_cli_days(days: Iterable[dict]) -> dict[tuple[str, str], dict]:
    """{(station, valid_iso): compact CLI day}."""
    out: dict[tuple[str, str], dict] = {}
    for d in days:
        station = d.get("station")
        valid = d.get("valid")
        if not station or not valid:
            continue
        out[(str(station).upper(), str(valid)[:10])] = d
    return out


def cli_value_for(rec: Optional[dict], variable: Optional[str]) -> Optional[int]:
    if rec is None or not variable:
        return None
    if variable == "temp_max":
        v = rec.get("high")
    elif variable == "temp_min":
        v = rec.get("low")
    else:
        return None
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _mean_models(per_model: dict) -> Optional[float]:
    vals = [float(v) for v in (per_model or {}).values() if v is not None]
    if not vals:
        return None
    return round(statistics.fmean(vals), 2)


def join_ledger_rows(
    rows: Iterable[dict],
    cli: dict[tuple[str, str], dict],
    source: str,
) -> list[dict]:
    """Attache le max/min CLI à chaque ligne de ledger."""
    out: list[dict] = []
    for r in rows:
        event = r.get("event_ticker") or r.get("market_ticker") or ""
        series = (r.get("series") or event.split("-")[0]).strip()
        station = station_for_series(series)
        variable = infer_variable(series)
        target = (r.get("target_date") or "")[:10]
        rec = cli.get((station, target)) if station and target else None
        value = cli_value_for(rec, variable)
        if not station:
            reason = "serie_inconnue"
        elif rec is None:
            reason = "pas_de_jour_cli"
        elif value is None:
            reason = "cli_sans_valeur"
        else:
            reason = None
        out.append({
            "source": source,
            "event_ticker": event,
            "series": series,
            "target_date": target or None,
            "station": station,
            "variable": variable,
            "cli_high": None if rec is None else rec.get("high"),
            "cli_low": None if rec is None else rec.get("low"),
            "cli_value": value,
            "joined": reason is None,
            "reason": reason,
            "resolution": r.get("resolution") or None,
            "outcome": r.get("outcome") or None,
            "method": r.get("method") or r.get("model") or None,
        })
    return out


def read_csv_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def join_forecast_points(
    points: Iterable[dict],
    cli: dict[tuple[str, str], dict],
    current_stations: Optional[set[str]] = None,
) -> list[dict]:
    """Attache la valeur CLI aux prévisions déjà stockées (station + jour)."""
    known = current_stations if current_stations is not None else set(kalshi_stations())
    out: list[dict] = []
    for p in points:
        station = str(p.get("station") or "").upper()
        target = str(p.get("target") or "")[:10]
        variable = p.get("variable")
        if station and station not in known:
            reason = "ancienne_station"
            rec = None
            value = None
        else:
            rec = cli.get((station, target)) if station and target else None
            value = cli_value_for(rec, variable)
            if rec is None:
                reason = "pas_de_jour_cli"
            elif value is None:
                reason = "cli_sans_valeur"
            else:
                reason = None
        mu = _mean_models(p.get("per_model") or {})
        err = None if (mu is None or value is None) else round(mu - value, 2)
        out.append({
            "station": station or None,
            "variable": variable,
            "target": target or None,
            "lead": p.get("lead"),
            "forecast_mean_f": mu,
            "cli_value": value,
            "error_f": err,
            "joined": reason is None,
            "reason": reason,
        })
    return out


def summarize_joins(ledger_rows: list[dict], forecast_rows: list[dict]) -> dict:
    """Comptes uniquement. Aucun chiffre d'écart ici."""
    def _counts(rows: list[dict]) -> dict:
        reasons: dict[str, int] = defaultdict(int)
        stations: dict[str, int] = defaultdict(int)
        for r in rows:
            if r.get("joined"):
                st = r.get("station") or "?"
                stations[st] += 1
            else:
                reasons[r.get("reason") or "inconnu"] += 1
        return {
            "n": len(rows),
            "n_joined": sum(1 for r in rows if r.get("joined")),
            "n_not_joined": sum(1 for r in rows if not r.get("joined")),
            "by_station_joined": dict(sorted(stations.items())),
            "not_joined_reasons": dict(sorted(reasons.items())),
        }

    return {
        "schema": "cli_join_summary/1",
        "ledger": _counts(ledger_rows),
        "forecasts": _counts(forecast_rows),
        "city_to_icao": dict(CITY_TO_ICAO),
    }


def forecast_vs_cli_by_station(forecast_rows: list[dict]) -> dict[str, dict]:
    """Écart prévision stockée − CLI, seulement sur les lignes jointes.

    Ce n'est pas l'audit ERA5. C'est l'écart des prévisions Previous Runs
    déjà en mémoire contre la station, pour le dataset de jonction.
    """
    buckets: dict[str, list[float]] = defaultdict(list)
    for r in forecast_rows:
        if not r.get("joined") or r.get("error_f") is None:
            continue
        key = f"{r['station']}:{r['variable']}"
        buckets[key].append(float(r["error_f"]))
    out: dict[str, dict] = {}
    for key, errs in sorted(buckets.items()):
        out[key] = {
            "n": len(errs),
            "bias_forecast_minus_cli_f": round(statistics.fmean(errs), 2),
            "mae_f": round(statistics.fmean(abs(x) for x in errs), 2),
        }
    return out
