"""Accès WeatherNext (Google) : sondes et lecture Open-Meteo.

FR : WeatherNext 3 (août 2026) n'est pas dans Open-Meteo. Google le
diffuse sur BigQuery / Earth Engine / GCS après inscription. WeatherNext 2
(64 membres, 0,25°) est sur l'Ensemble API Open-Meteo. On mesure la
couverture réelle, on n'invente rien. J0 et J-1 restent séparés.

EN : Probe WeatherNext 3 (Google Cloud allowlist) and WeatherNext 2
(Open-Meteo). Coverage is measured, never assumed.
"""
from __future__ import annotations

import json
import os
import time
from datetime import date
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import requests

from src.config import USER_AGENT
from src.truth.lst_window import daily_extreme_lst
from src.weather.ensemble_api import MemberSeries, parse_members
from src.weather.open_meteo import OpenMeteoClient

WN3_LABEL = "WeatherNext 3"
WN2_LABEL = "WeatherNext 2"
WN2_OM_MODEL = "google_weathernext2_ensemble"

# Noms Open-Meteo essayés pour la v3. Aucun n'est documenté ; on les
# sonde pour que le blocage soit mesuré, pas supposé.
WN3_OM_CANDIDATES: list[str] = [
    "google_weathernext3_ensemble",
    "google_weathernext_3",
    "google_weathernext3",
    "weathernext3",
    "weathernext_3",
    "google_weathernext",
]

ENSEMBLE_BASE = "https://ensemble-api.open-meteo.com/v1/ensemble"
HISTORICAL_FORECAST_BASE = "https://historical-forecast-api.open-meteo.com/v1/forecast"
PREVIOUS_RUNS_BASE = "https://previous-runs-api.open-meteo.com/v1/forecast"
SINGLE_RUNS_BASE = "https://single-runs-api.open-meteo.com/v1/forecast"

GCS_URLS: list[str] = [
    "https://storage.googleapis.com/storage/v1/b/weathernext3_spatial",
    "https://storage.googleapis.com/storage/v1/b/weathernext3_statistics_spatial",
    "https://storage.googleapis.com/storage/v1/b/weathernext",
    "https://storage.googleapis.com/weathernext3_spatial/",
    "https://storage.googleapis.com/weathernext/weathernext_2_0_0/zarr/",
]

# Formulaire officiel (décembre 2026 docs Google).
WN3_ACCESS_FORM = "https://developers.google.com/weathernext/guides/access-forecast"
WN3_BQ_TABLE = "weathernext_3_0_0_0p05deg"


def member_fill_summary(hourly: dict, variable: str) -> dict:
    """Compte les cellules remplies, par jour UTC. Rien n'est interpolé."""
    times = hourly.get("time") or []
    keys = [
        k for k, vals in hourly.items()
        if k != "time" and k.startswith(variable) and isinstance(vals, list)
    ]
    days: dict[str, dict] = {}
    n_cells = n_filled = 0
    members_any: dict[str, set] = {}
    hours_any: dict[str, set] = {}
    sample = None
    for key in keys:
        vals = hourly[key]
        for t, v in zip(times, vals):
            day = str(t)[:10]
            rec = days.setdefault(day, {"hours_on_axis": 0, "hours_any_member": 0,
                                        "members_with_any": 0, "n_filled_cells": 0,
                                        "n_cells": 0})
            rec["n_cells"] += 1
            n_cells += 1
            if v is not None:
                n_filled += 1
                rec["n_filled_cells"] += 1
                members_any.setdefault(day, set()).add(key)
                hours_any.setdefault(day, set()).add(t)
                if sample is None:
                    sample = {"key": key, "time": t, "value": v}
    hour_count: dict[str, int] = {}
    for t in times:
        hour_count[str(t)[:10]] = hour_count.get(str(t)[:10], 0) + 1
    for day, rec in days.items():
        rec["hours_on_axis"] = hour_count.get(day, 0)
        rec["hours_any_member"] = len(hours_any.get(day, ()))
        rec["members_with_any"] = len(members_any.get(day, ()))
    filled_days = [d for d, rec in sorted(days.items()) if rec["hours_any_member"] > 0]
    return {
        "n_member_keys": len(keys),
        "n_times": len(times),
        "n_cells": n_cells,
        "n_filled_cells": n_filled,
        "filled_days": filled_days,
        "first_filled": filled_days[0] if filled_days else None,
        "last_filled": filled_days[-1] if filled_days else None,
        "n_filled_days": len(filled_days),
        "sample": sample,
        "days": days,
    }


def lead_name(lead: int) -> str:
    """J0 = même jour (lead 0), J-1 = la veille (lead 1). Autre = autre."""
    if lead == 0:
        return "J0"
    if lead == 1:
        return "J-1"
    return f"lead_{lead}"


def gcp_env_status() -> dict:
    """Présence de credentials Google, sans les afficher."""
    cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or ""
    return {
        "GOOGLE_APPLICATION_CREDENTIALS_set": bool(cred),
        "CLOUDSDK_CONFIG_set": bool(os.environ.get("CLOUDSDK_CONFIG")),
        "gcloud_config_dir_exists": Path.home().joinpath(".config/gcloud").exists(),
    }


def http_probe(url: str, timeout: float = 40.0) -> dict:
    """GET : status + extrait du corps. Les 401/403/400 sont un résultat."""
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        text = (r.text or "")[:400]
        return {"url": url, "status": r.status_code, "body": text, "error": None}
    except requests.RequestException as e:
        return {"url": url, "status": None, "body": "", "error": str(e)}


def open_meteo_probe(base: str, model: str, extra: Optional[dict] = None,
                     lat: float = 33.6367, lon: float = -84.4281) -> dict:
    """Une requête Open-Meteo pour un nom de modèle. Corps d'erreur conservé."""
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m",
        "models": model,
        "timezone": "GMT",
        "temperature_unit": "fahrenheit",
        "forecast_days": 2,
    }
    if extra:
        params.update(extra)
    url = f"{base}?{urlencode(params)}"
    out = http_probe(url)
    out["model"] = model
    out["base"] = base
    if out["status"] == 200:
        try:
            data = json.loads(out["body"] + "\n")  # may be truncated
        except json.JSONDecodeError:
            data = None
        # Re-fetch full JSON for fill counts when the short body is 200.
        try:
            r = requests.get(url, timeout=60, headers={"User-Agent": USER_AGENT})
            data = r.json() if r.status_code == 200 else None
            out["status"] = r.status_code
            if data is not None:
                hourly = data.get("hourly") or {}
                variable = params["hourly"].split(",")[0]
                out["fill"] = member_fill_summary(hourly, variable)
                out["body"] = (r.text or "")[:200]
        except requests.RequestException as e:
            out["error"] = str(e)
    return out


def member_daily_values(
    members: list[MemberSeries],
    tz_name: str,
    target: date,
    kind: str,
    min_hours: int = 18,
) -> list[float]:
    """Extrêmes LST par membre. Un membre sans assez d'heures est omis."""
    out: list[float] = []
    for s in members:
        x = daily_extreme_lst(s.times_utc, s.values, tz_name, target, kind,
                              min_hours=min_hours)
        if x is not None:
            out.append(float(x))
    return out


class WeatherNextOpenMeteo:
    """Télécharge WeatherNext 2 via Open-Meteo (historique / veille / live)."""

    def __init__(self, cache_dir: Path, sleep_s: float = 0.2):
        self.sleep_s = sleep_s
        self._om = OpenMeteoClient(cache_dir=cache_dir)
        self.failures: dict[str, str] = {}

    def _get(self, base: str, params: dict, cache_kind: str, cache_key: str) -> dict:
        def fetcher() -> dict:
            time.sleep(self.sleep_s)
            return self._om._get(base, params)
        return self._om.cached_or_fetch(cache_kind, cache_key, fetcher)

    def fetch_historical(self, lat: float, lon: float, start: date, end: date,
                         model: str = WN2_OM_MODEL) -> list[MemberSeries]:
        params = {
            "latitude": lat, "longitude": lon,
            "hourly": "temperature_2m",
            "models": model,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "timezone": "GMT",
            "temperature_unit": "fahrenheit",
        }
        key = f"{lat:.4f}_{lon:.4f}_{model}_{start}_{end}_hist"
        try:
            data = self._get(HISTORICAL_FORECAST_BASE, params, "wn_hist", key)
        except requests.RequestException as e:
            self.failures[f"hist:{lat:.4f},{lon:.4f}"] = str(e)
            return []
        return parse_members(data, "temperature_2m", model)

    def fetch_previous_day(self, lat: float, lon: float, start: date, end: date,
                           lead: int = 1, model: str = WN2_OM_MODEL) -> list[MemberSeries]:
        if lead < 1 or lead > 7:
            raise ValueError("lead Previous Runs must be 1..7")
        variable = f"temperature_2m_previous_day{lead}"
        params = {
            "latitude": lat, "longitude": lon,
            "hourly": variable,
            "models": model,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "timezone": "GMT",
            "temperature_unit": "fahrenheit",
        }
        key = f"{lat:.4f}_{lon:.4f}_{model}_{start}_{end}_prev{lead}"
        try:
            data = self._get(PREVIOUS_RUNS_BASE, params, "wn_prev", key)
        except requests.RequestException as e:
            self.failures[f"prev{lead}:{lat:.4f},{lon:.4f}"] = str(e)
            return []
        return parse_members(data, variable, model)
