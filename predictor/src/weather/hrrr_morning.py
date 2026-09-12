"""HRRR du matin même : run 12 h UTC, heures encore dans le jour LST.

FR : Ce n'est pas la prévision de la veille (`temperature_2m_previous_day1`).
Ce n'est pas non plus le champ `temperature_2m` sans heure d'émission
(jour 0 recousu, quasi une analyse). Ici on demande le run unique du
matin (12 h UTC) via l'API Single Runs d'Open-Meteo, modèle `gfs_hrrr`.
Les heures manquantes restent manquantes. Archive : depuis le 2 avril 2026.

EN : Same-day 12Z HRRR via Open-Meteo Single Runs (`run=`). Not yesterday's
previous_day1 series, not the stitched day-0 field. Missing hours stay
missing. Archive starts 2026-04-02.
"""
from __future__ import annotations

import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests

from src.config import DATA_DIR, USER_AGENT
from src.truth.iem_cli import kalshi_stations

SINGLE_RUNS_BASE = "https://single-runs-api.open-meteo.com/v1/forecast"
HRRR_DIR = DATA_DIR / "hrrr_morning"
CACHE_DIR = HRRR_DIR / "cache"
EXTRACTED_PATH = HRRR_DIR / "extracted.json"
HRRR_MODEL = "gfs_hrrr"
CYCLE_HOUR = 12
SOURCE = "hrrr_morning_12z"
FORECAST_HOURS = 48
# HRRR 12Z est en général public vers 13 h UTC (fichier S3 du 3 août 2026 :
# Last-Modified 13:08). On ne note un prix que s'il est pris après ça.
AVAILABLE_AFTER_UTC = 13
HRRR_NOTE = (
    "HRRR du matin même = run 12 h UTC du jour, API Single Runs Open-Meteo, "
    "modèle gfs_hrrr, champ temperature_2m. Ce n'est pas la veille "
    "(previous_day1). Ce n'est pas le jour 0 recousu. Archive depuis le "
    "2 avril 2026. Aucune heure manquante n'est inventée."
)


def issued_12z(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, CYCLE_HOUR, tzinfo=timezone.utc)


def available_at(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, AVAILABLE_AFTER_UTC, tzinfo=timezone.utc)


class HrrrMorningClient:
    """Un run 12Z par jour, points station, cache disque."""

    def __init__(
        self,
        cache_dir: Path = CACHE_DIR,
        extracted_path: Path = EXTRACTED_PATH,
        sleep_s: float = 0.25,
        timeout_s: float = 90.0,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_path = Path(extracted_path)
        self.extracted_path.parent.mkdir(parents=True, exist_ok=True)
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})

    def _cache_path(self, day: date) -> Path:
        return self.cache_dir / f"hrrr12z_{day.isoformat()}.json"

    def fetch_day(
        self,
        day: date,
        stations: dict[str, dict],
        use_cache: bool = True,
    ) -> tuple[dict[str, dict], Optional[str]]:
        """{icao: {times, values, issued}} pour le run 12Z de `day`."""
        path = self._cache_path(day)
        order = sorted(stations)
        if use_cache and path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("error"):
                    return {}, str(data.get("error"))
                out = {}
                for row in data.get("stations") or []:
                    icao = row.get("station")
                    if icao in stations:
                        out[icao] = {
                            "times": list(row.get("times") or []),
                            "values": list(row.get("values") or []),
                            "issued": row.get("issued") or issued_12z(day).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        }
                if out:
                    return out, None
            except (json.JSONDecodeError, TypeError, ValueError):
                pass

        lats = [stations[k]["lat"] for k in order]
        lons = [stations[k]["lon"] for k in order]
        params = {
            "latitude": ",".join(f"{x:.4f}" for x in lats),
            "longitude": ",".join(f"{x:.4f}" for x in lons),
            "hourly": "temperature_2m",
            "temperature_unit": "fahrenheit",
            "timezone": "GMT",
            "forecast_hours": FORECAST_HOURS,
            "models": HRRR_MODEL,
            "run": f"{day.isoformat()}T{CYCLE_HOUR:02d}:00",
        }
        time.sleep(self.sleep_s)
        try:
            resp = self.session.get(SINGLE_RUNS_BASE, params=params, timeout=self.timeout_s)
        except requests.RequestException as e:
            return {}, f"réseau : {e}"
        if resp.status_code == 400:
            try:
                reason = (resp.json() or {}).get("reason") or resp.text[:200]
            except ValueError:
                reason = resp.text[:200]
            path.write_text(json.dumps({
                "day": day.isoformat(), "error": reason, "stations": [],
            }), encoding="utf-8")
            return {}, reason
        try:
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError) as e:
            return {}, str(e)

        blocks = payload if isinstance(payload, list) else [payload]
        issued = issued_12z(day).strftime("%Y-%m-%dT%H:%M:%SZ")
        out: dict[str, dict] = {}
        stored = []
        for i, icao in enumerate(order):
            if i >= len(blocks):
                break
            hourly = (blocks[i] or {}).get("hourly") or {}
            times = list(hourly.get("time") or [])
            values = list(hourly.get("temperature_2m") or [])
            row = {"station": icao, "issued": issued, "times": times, "values": values}
            stored.append(row)
            out[icao] = {"times": times, "values": values, "issued": issued}
        path.write_text(json.dumps({
            "day": day.isoformat(), "error": None, "stations": stored,
        }), encoding="utf-8")
        return out, None

    def fetch_range(
        self,
        start: date,
        end: date,
        stations: Optional[dict[str, dict]] = None,
        use_cache: bool = True,
    ) -> tuple[dict[tuple[str, date], dict], list[dict]]:
        """{(icao, jour d'émission): {times, values}}. Un run, un jour."""
        stations = stations or kalshi_stations()
        series: dict[tuple[str, date], dict] = {}
        failures: list[dict] = []
        d = start
        n_days = (end - start).days + 1
        i = 0
        while d <= end:
            i += 1
            print(f"[HRRR 12Z] {d.isoformat()} ({i}/{n_days}) ...", flush=True)
            got, err = self.fetch_day(d, stations, use_cache=use_cache)
            if err:
                failures.append({"day": d.isoformat(), "error": err})
                print(f"   échec : {err}", flush=True)
            else:
                n_ok = sum(
                    1 for s in got.values()
                    if any(v is not None for v in s.get("values") or [])
                )
                print(f"   {n_ok}/{len(stations)} villes avec au moins une heure", flush=True)
                for icao, s in got.items():
                    series[(icao, d)] = {
                        "times": s["times"],
                        "values": s["values"],
                        "issued": s.get("issued"),
                    }
            d += timedelta(days=1)
        return series, failures

    def persist_extracted(self, series: dict[tuple[str, date], dict]) -> Path:
        compact = []
        for (icao, day), s in sorted(series.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            compact.append({
                "station": icao,
                "issued_date": day.isoformat(),
                "issued": s.get("issued") or issued_12z(day).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "times": s.get("times") or [],
                "values": s.get("values") or [],
            })
        self.extracted_path.write_text(json.dumps(compact), encoding="utf-8")
        return self.extracted_path

    def load_extracted(self) -> dict[tuple[str, date], dict]:
        if not self.extracted_path.exists():
            return {}
        data = json.loads(self.extracted_path.read_text(encoding="utf-8"))
        out: dict[tuple[str, date], dict] = {}
        for row in data:
            day = date.fromisoformat(row["issued_date"])
            out[(row["station"], day)] = {
                "times": row.get("times") or [],
                "values": row.get("values") or [],
                "issued": row.get("issued"),
            }
        return out
