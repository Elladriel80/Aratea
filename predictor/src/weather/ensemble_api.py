"""Client Open-Meteo Ensemble API / Open-Meteo Ensemble API client.

FR : L'Ensemble API renvoie TOUS les membres des systèmes de prévision
d'ensemble (ECMWF IFS 51 membres, ECMWF AIFS ENS 51, GEFS 31, GEM 21...),
gratuit, sans clé. C'est une vraie distribution de prévision, là où
l'ensemble « maison » de src/predictors/ensemble.py approxime une gaussienne
sur 5 sorties déterministes. Un contrat Kalshi étant un bin de 2 °F, la forme
de la distribution est toute la valeur.

Chaque modèle est demandé séparément : un nom de modèle refusé (400) ne fait
pas tomber les autres, et la couverture réelle est mesurée, jamais supposée.
Fuseau GMT pour permettre l'agrégation en heure standard locale du CLI
(src/truth/lst_window.py). Cache disque par (lat, lon, modèle, jour).

EN : Serves every member of the ensemble systems exposed by Open-Meteo's
Ensemble API (free, no key). One request per model so a rejected model name
does not sink the others; GMT so daily extremes follow the CLI LST window;
disk cache per (lat, lon, model, day). Response key layouts vary (single vs
multi-model, control member without suffix), so parsing is pattern-based.
"""
from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import requests

from src.config import FORECASTS_DIR
from src.weather.open_meteo import OpenMeteoClient

ENSEMBLE_BASE = "https://ensemble-api.open-meteo.com/v1/ensemble"

# Modèles d'ensemble Open-Meteo (noms API). Réglable via ARATEA_ENS_MEMBER_MODELS.
DEFAULT_MEMBER_MODELS: list[str] = ["ecmwf_ifs025", "ecmwf_aifs025", "gfs025"]
MEMBER_MODEL_LABELS: dict[str, str] = {
    "ecmwf_ifs025": "ECMWF IFS ENS (51)",
    "ecmwf_aifs025": "ECMWF AIFS ENS (51)",
    "gfs025": "NOAA GEFS (31)",
    "gfs05": "NOAA GEFS 0.5° (31)",
    "gem_global": "ECCC GEM (21)",
    "icon_seamless": "DWD ICON EPS",
    "bom_access_global_ensemble": "BOM ACCESS-GE",
    "ukmo_global_ensemble_20km": "UKMO MOGREPS-G",
}

_MEMBER_SUFFIX_RE = re.compile(r"^_member(\d+)$")


def member_models_from_env() -> list[str]:
    raw = os.environ.get("ARATEA_ENS_MEMBER_MODELS", "")
    models = [m.strip() for m in raw.split(",") if m.strip()]
    return models or list(DEFAULT_MEMBER_MODELS)


@dataclass
class MemberSeries:
    model: str
    member: int                 # 0 = contrôle
    times_utc: list[str] = field(default_factory=list)
    values: list[Optional[float]] = field(default_factory=list)


def parse_members(data: dict, variable: str, model: str) -> list[MemberSeries]:
    """Extrait les membres d'une réponse (mono-modèle) de l'Ensemble API.

    Clés observées : `temperature_2m` (contrôle), `temperature_2m_member01`
    ... et, en multi-modèle, un suffixe `_<model>`. On accepte les deux.
    """
    hourly = (data or {}).get("hourly") or {}
    times = hourly.get("time") or []
    out: list[MemberSeries] = []
    for key, vals in hourly.items():
        if key == "time" or not isinstance(vals, list) or not key.startswith(variable):
            continue
        rest = key[len(variable):]
        if rest.endswith("_" + model):
            rest = rest[: -(len(model) + 1)]
        if rest == "":
            num = 0
        else:
            m = _MEMBER_SUFFIX_RE.match(rest)
            if not m:
                continue
            num = int(m.group(1))
        out.append(MemberSeries(model, num, list(times), list(vals)))
    out.sort(key=lambda s: s.member)
    return out


class EnsembleMembersClient:
    def __init__(self, cache_dir: Path = FORECASTS_DIR, models: Optional[list[str]] = None,
                 sleep_s: float = 0.15):
        self.models = list(models or member_models_from_env())
        self.sleep_s = sleep_s
        self._om = OpenMeteoClient(cache_dir=cache_dir)
        self.failures: dict[str, str] = {}

    def fetch(self, lat: float, lon: float, days: int = 7,
              variable: str = "temperature_2m") -> dict[str, list[MemberSeries]]:
        """{model: [MemberSeries]} pour les `days` prochains jours (UTC, °F)."""
        days = max(1, min(16, int(days)))
        today = date.today().isoformat()
        out: dict[str, list[MemberSeries]] = {}
        for model in self.models:
            params = {"latitude": lat, "longitude": lon, "hourly": variable, "models": model,
                      "timezone": "GMT", "temperature_unit": "fahrenheit", "forecast_days": days}
            key = f"{lat:.4f}_{lon:.4f}_{model}_{variable}_d{days}_{today}"

            def fetcher(p=params) -> dict:
                time.sleep(self.sleep_s)
                return self._om._get(ENSEMBLE_BASE, p)

            try:
                data = self._om.cached_or_fetch("ensemble_members", key, fetcher)
            except requests.RequestException as e:
                self.failures[model] = str(e)
                continue
            members = parse_members(data, variable, model)
            if members:
                out[model] = members
            else:
                self.failures[model] = "no member series in response"
        return out
