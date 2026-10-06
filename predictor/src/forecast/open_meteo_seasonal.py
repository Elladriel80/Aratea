"""Open-Meteo Seasonal (ECMWF SEAS5 ensemble mean).

FR : Accès déjà branchable, sans compte CDS. L'API publique garde
past_days ≤ 92 et refuse start_date historique (mesuré 2026-09-12).
Les 51 membres ne sont gardés qu'un mois ; la moyenne d'ensemble
est gardée plus longtemps.

EN : No CDS account. Historical hindcasts are not served.
"""
from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode

import requests

from src.config import DATA_DIR, USER_AGENT

SEASONAL_API = "https://seasonal-api.open-meteo.com/v1/seasonal"
CACHE = DATA_DIR / "forecasts" / "open_meteo_seasonal_cache"

# Catalogue name. Do not rename.
FORECAST_NAME = "Open-Meteo Seasonal"
# Measured 2026-09-12: start_date outside this window is rejected.
ALLOWED_START = date(2025, 9, 1)
ALLOWED_END = date(2027, 4, 16)

# One point inside each USDA hub (Des Moines, Phoenix). Not a product.
HUB_POINTS = {
    "Midwest": {"lat": 41.6, "lon": -93.6, "label": "Des Moines IA"},
    "Southwest": {"lat": 33.45, "lon": -112.07, "label": "Phoenix AZ"},
}


class OpenMeteoSeasonalClient:
    def __init__(self, cache_dir: Path = CACHE, timeout: int = 60):
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})

    def fetch_monthly(
        self,
        lat: float,
        lon: float,
        *,
        past_days: int = 92,
        forecast_days: int = 183,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        allow_network: bool = True,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "latitude": lat,
            "longitude": lon,
            "monthly": "precipitation_mean,precipitation_anomaly",
            "models": "ecmwf_seas5_ensemble_mean",
        }
        if start_date and end_date:
            params["start_date"] = start_date.isoformat()
            params["end_date"] = end_date.isoformat()
        else:
            params["past_days"] = past_days
            params["forecast_days"] = forecast_days
        key = urlencode(params)
        path = self.cache_dir / f"{key.replace('/', '_')}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        if not allow_network:
            raise FileNotFoundError(f"Open-Meteo Seasonal cache missing: {path}")
        time.sleep(0.2)
        r = self.session.get(SEASONAL_API, params=params, timeout=self.timeout)
        payload: dict[str, Any]
        try:
            payload = r.json()
        except Exception:
            payload = {"error": True, "reason": r.text[:400], "http_status": r.status_code}
        if r.status_code >= 400 and "error" not in payload:
            payload = {"error": True, "reason": r.text[:400], "http_status": r.status_code}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return payload


def monthly_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    monthly = payload.get("monthly") or {}
    times = monthly.get("time") or []
    means = monthly.get("precipitation_mean") or [None] * len(times)
    anoms = monthly.get("precipitation_anomaly") or [None] * len(times)
    rows = []
    for t, mu, anom in zip(times, means, anoms):
        rows.append({
            "month": t,
            "precipitation_mean": mu,
            "precipitation_anomaly": anom,
        })
    return rows
