"""HRRR horaire via Open-Meteo Previous Runs (piste C1).

FR : Le run HRRR du matin même (12 h UTC) est sur S3 NOAA, mais il faut
eccodes pour lire le GRIB. Cet outil n'est pas dans l'environnement.
On prend donc le run de la veille (`temperature_2m_previous_day1`),
déjà public, heure par heure, pour le reste de la journée. Ce n'est
pas une observation. Si une heure manque, elle reste manquante.

EN : Same-day 12Z HRRR on S3 needs eccodes, which is not installed.
We use yesterday's HRRR hourly from Open-Meteo Previous Runs as the
remaining-day forecast. Missing hours stay missing.
"""
from __future__ import annotations

import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

import requests

from src.config import DATA_DIR, USER_AGENT
from src.truth.iem_cli import kalshi_stations
from src.truth.lst_window import lst_date

PREVIOUS_RUNS_BASE = "https://previous-runs-api.open-meteo.com/v1/forecast"
HRRR_DIR = DATA_DIR / "hrrr"
CACHE_DIR = HRRR_DIR / "cache"
EXTRACTED_PATH = HRRR_DIR / "extracted.json"
MAX_DAYS = 31
HRRR_MODEL = "gfs_hrrr"
HRRR_NOTE = (
    "HRRR horaire = run de la veille (Open-Meteo Previous Runs, modèle "
    "gfs_hrrr, champ temperature_2m_previous_day1). Le run du matin même "
    "est sur S3 mais illisible ici sans eccodes. Aucune heure manquante "
    "n'est inventée."
)


def parse_hour(raw: str) -> Optional[datetime]:
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def remaining_extreme(
    times: Iterable[str],
    values: Iterable[Optional[float]],
    tz_name: str,
    target: date,
    as_of: datetime,
    kind: str,
) -> Optional[dict]:
    """Max ou min prévu après `as_of` encore dans le jour LST `target`."""
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)
    picked: list[tuple[datetime, float]] = []
    for t, v in zip(times, values):
        if v is None:
            continue
        dt = parse_hour(t)
        if dt is None or dt <= as_of:
            continue
        if lst_date(dt, tz_name) != target:
            continue
        picked.append((dt, float(v)))
    if not picked:
        return None
    vals = [v for _, v in picked]
    extreme = max(vals) if kind == "max" else min(vals)
    return {
        "extreme_f": extreme,
        "n_hours": len(picked),
        "first": picked[0][0],
        "last": picked[-1][0],
        "source": "hrrr_previous_day1",
    }


class HrrrHourlyClient:
    """Archive horaire HRRR (veille) + cache disque par station et mois."""

    def __init__(
        self,
        cache_dir: Path = CACHE_DIR,
        extracted_path: Path = EXTRACTED_PATH,
        sleep_s: float = 0.25,
        timeout_s: float = 60.0,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_path = Path(extracted_path)
        self.extracted_path.parent.mkdir(parents=True, exist_ok=True)
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})

    def _cache_path(self, icao: str, start: date, end: date) -> Path:
        return self.cache_dir / f"hrrr_{icao}_{start.isoformat()}_{end.isoformat()}.json"

    def fetch_chunk(self, lat: float, lon: float, start: date, end: date,
                    icao: str, use_cache: bool = True) -> tuple[list[str], list[Optional[float]]]:
        path = self._cache_path(icao, start, end)
        if use_cache and path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                hourly = data.get("hourly") or {}
                return list(hourly.get("time") or []), list(hourly.get("temperature_2m_previous_day1") or [])
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "hourly": "temperature_2m_previous_day1",
            "temperature_unit": "fahrenheit",
            "timezone": "GMT",
            "models": HRRR_MODEL,
        }
        time.sleep(self.sleep_s)
        resp = self.session.get(PREVIOUS_RUNS_BASE, params=params, timeout=self.timeout_s)
        resp.raise_for_status()
        data = resp.json()
        path.write_text(json.dumps({
            "station": icao, "start": start.isoformat(), "end": end.isoformat(),
            "hourly": data.get("hourly") or {},
        }), encoding="utf-8")
        hourly = data.get("hourly") or {}
        return list(hourly.get("time") or []), list(hourly.get("temperature_2m_previous_day1") or [])

    def fetch_range(self, icao: str, lat: float, lon: float, start: date, end: date,
                    use_cache: bool = True) -> dict:
        times: list[str] = []
        values: list[Optional[float]] = []
        cur = start
        while cur <= end:
            chunk_end = min(end, cur + timedelta(days=MAX_DAYS - 1))
            t, v = self.fetch_chunk(lat, lon, cur, chunk_end, icao, use_cache=use_cache)
            times.extend(t)
            values.extend(v)
            cur = chunk_end + timedelta(days=1)
        return {"station": icao, "times": times, "values": values}

    def persist_extracted(self, series: dict[str, dict]) -> Path:
        compact = []
        for icao, s in sorted(series.items()):
            compact.append({
                "station": icao,
                "times": s["times"],
                "values": s["values"],
            })
        self.extracted_path.write_text(json.dumps(compact), encoding="utf-8")
        return self.extracted_path

    def load_extracted(self) -> dict[str, dict]:
        if not self.extracted_path.exists():
            return {}
        data = json.loads(self.extracted_path.read_text(encoding="utf-8"))
        out = {}
        for row in data:
            out[row["station"]] = {"times": row["times"], "values": row["values"]}
        return out


def default_station_coords() -> dict[str, dict]:
    return kalshi_stations()
