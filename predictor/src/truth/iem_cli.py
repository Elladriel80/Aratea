"""Client IEM pour les rapports CLI du NWS / IEM client for NWS CLI reports.

FR : L'Iowa Environmental Mesonet archive chaque rapport climatologique
quotidien (CLI) émis par le NWS et l'expose en JSON :
    https://mesonet.agron.iastate.edu/json/cli.py?station=KNYC&year=2026
Chaque enregistrement porte la date, le max, le min, l'heure du max/min,
les précipitations et la neige tels qu'ils apparaissent dans le produit
qui résout les marchés Kalshi. C'est la seule vérité terrain légitime pour
le predictor ; ERA5 (grille 25 km) n'en est qu'une approximation biaisée.

EN : The Iowa Environmental Mesonet archives every NWS Daily Climate
Report (CLI) and serves it as JSON. Each record carries the date, high,
low, time of high/low, precipitation and snowfall exactly as printed in
the product that settles Kalshi markets. It is the only legitimate ground
truth for the predictor; ERA5 (25 km grid) is a biased approximation.

Parsing is deliberately defensive: IEM encodes missing values as "M",
trace precipitation as "T", and field names have drifted over the years.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

import requests

from src.config import DATA_DIR, USER_AGENT
from src.kalshi.resolution import NWS_STATIONS, SERIES_TO_STATION

IEM_CLI_BASE = "https://mesonet.agron.iastate.edu/json/cli.py"
TRUTH_DIR = DATA_DIR / "truth"

_SAFE_RE = re.compile(r"[^A-Za-z0-9._-]")


@dataclass(frozen=True)
class CliDay:
    """Un jour de rapport CLI / One CLI report day."""
    station: str                 # ICAO, ex "KNYC"
    valid: date                  # jour climatologique (LST)
    high_f: Optional[int]        # °F entier tel qu'imprimé
    low_f: Optional[int]
    high_time: Optional[str]     # "3:05 PM" tel qu'imprimé, None si absent
    low_time: Optional[str]
    precip_in: Optional[float]   # pouces ; trace = 0.0 avec flag
    precip_trace: bool
    snow_in: Optional[float]
    snow_trace: bool
    product: Optional[str]       # identifiant produit AFOS (pour audit)

    def value_for(self, variable: str) -> Optional[float]:
        """Valeur au sens ContractSpec.variable / value in ContractSpec terms."""
        if variable == "temp_max":
            return None if self.high_f is None else float(self.high_f)
        if variable == "temp_min":
            return None if self.low_f is None else float(self.low_f)
        if variable == "precip_in":
            return self.precip_in
        if variable == "snow_in":
            return self.snow_in
        raise ValueError(f"variable inconnue: {variable}")


def _to_int(x) -> Optional[int]:
    if x is None or x == "" or x == "M":
        return None
    try:
        return int(round(float(x)))
    except (TypeError, ValueError):
        return None


def _to_inches(x) -> tuple[Optional[float], bool]:
    """Renvoie (valeur, trace). "T" → (0.0, True). "M"/None → (None, False)."""
    if x is None or x == "" or x == "M":
        return None, False
    if isinstance(x, str) and x.strip().upper() == "T":
        return 0.0, True
    try:
        return float(x), False
    except (TypeError, ValueError):
        return None, False


def _parse_date(s) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def parse_cli_record(rec: dict, station_hint: Optional[str] = None) -> Optional[CliDay]:
    """Parse un enregistrement JSON IEM en CliDay. None si date ou station illisible."""
    valid = _parse_date(rec.get("valid"))
    station = rec.get("station") or station_hint
    if valid is None or not station:
        return None
    precip, precip_t = _to_inches(rec.get("precip"))
    snow, snow_t = _to_inches(rec.get("snow"))
    return CliDay(
        station=str(station).upper(),
        valid=valid,
        high_f=_to_int(rec.get("high")),
        low_f=_to_int(rec.get("low")),
        high_time=rec.get("high_time") or None,
        low_time=rec.get("low_time") or None,
        precip_in=precip,
        precip_trace=precip_t,
        snow_in=snow,
        snow_trace=snow_t,
        product=rec.get("product") or None,
    )


# Fuseau IANA de chaque station de résolution (pour la fenêtre LST du CLI).
STATION_TZ: dict[str, str] = {
    "KAUS": "America/Chicago", "KNYC": "America/New_York", "KORD": "America/Chicago",
    "KMDW": "America/Chicago", "KMIA": "America/New_York", "KLAX": "America/Los_Angeles",
    "KBOS": "America/New_York", "KDEN": "America/Denver", "KPHL": "America/New_York",
    "KSFO": "America/Los_Angeles", "KSAT": "America/Chicago", "KPHX": "America/Phoenix",
    "KOKC": "America/Chicago", "KMSP": "America/Chicago", "KIAH": "America/Chicago",
    "KSEA": "America/Los_Angeles", "KLAS": "America/Los_Angeles", "KDCA": "America/New_York",
    "KATL": "America/New_York", "KDAL": "America/Chicago", "KHOU": "America/Chicago", "KDFW": "America/Chicago",
}


# Clé ville (CITIES, open_meteo.py) → ICAO de la station de résolution.
CITY_TO_ICAO: dict[str, str] = {
    "ATLANTA": "KATL", "AUSTIN": "KAUS", "BOSTON": "KBOS", "CHICAGO": "KMDW",
    "DALLAS": "KDFW", "DENVER": "KDEN", "HOUSTON": "KHOU", "LASVEGAS": "KLAS",
    "LOSANGELES": "KLAX", "MIAMI": "KMIA", "MINNEAPOLIS": "KMSP", "NYC": "KNYC",
    "PHILADELPHIA": "KPHL", "PHOENIX": "KPHX", "SANANTONIO": "KSAT",
    "SANFRANCISCO": "KSFO", "SEATTLE": "KSEA", "WASHINGTON": "KDCA",
}


def kalshi_stations() -> dict[str, dict]:
    """{ICAO: {lat, lon, tz, city_key}} pour les 18 villes Kalshi couvertes."""
    from src.weather.open_meteo import CITIES  # import tardif : évite un cycle
    out: dict[str, dict] = {}
    for city_key, icao in CITY_TO_ICAO.items():
        c = CITIES.get(city_key)
        if c is None:
            continue
        out[icao] = {"lat": c["lat"], "lon": c["lon"],
                     "tz": STATION_TZ.get(icao, c["tz"]), "city_key": city_key}
    return out


def station_for_series(series_ticker: str) -> Optional[str]:
    """Série Kalshi → ICAO de la station de résolution (via resolution.py)."""
    cli = SERIES_TO_STATION.get(series_ticker)
    if cli is None:
        return None
    st = NWS_STATIONS.get(cli)
    return st.icao if st else None


class IEMCliClient:
    """Lecture + cache disque des rapports CLI d'une station par année.

    Cache : data/truth/cli_<ICAO>_<year>.json. L'année en cours est
    re-téléchargée si le cache a plus de `stale_hours` heures ; les années
    passées sont considérées figées (le NWS corrige rarement un CLI après
    la fin de l'année, et jamais silencieusement).
    """

    def __init__(self, cache_dir: Path = TRUTH_DIR, stale_hours: float = 12.0,
                 sleep_s: float = 0.5):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.stale_hours = stale_hours
        self.sleep_s = sleep_s
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})

    def _cache_path(self, station: str, year: int) -> Path:
        key = _SAFE_RE.sub("_", f"{station}_{year}")
        return self.cache_dir / f"cli_{key}.json"

    def _fetch_year_raw(self, station: str, year: int) -> dict:
        params = {"station": station, "year": year, "fmt": "json"}
        last: Optional[BaseException] = None
        for attempt in range(3):
            try:
                resp = self.session.get(IEM_CLI_BASE, params=params, timeout=60)
                if resp.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                return resp.json()
            except (requests.RequestException, ValueError) as e:
                last = e
                time.sleep(1 + attempt)
        raise RuntimeError(f"IEM CLI fetch failed for {station} {year}: {last}")

    def fetch_year(self, station: str, year: int, use_cache: bool = True) -> list[CliDay]:
        station = station.upper()
        path = self._cache_path(station, year)
        today = date.today()
        if use_cache and path.exists():
            fresh = True
            if year >= today.year:
                age_h = (time.time() - path.stat().st_mtime) / 3600.0
                fresh = age_h < self.stale_hours
            if fresh:
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    return self._parse(data, station)
                except json.JSONDecodeError:
                    pass
        time.sleep(self.sleep_s)
        data = self._fetch_year_raw(station, year)
        path.write_text(json.dumps(data), encoding="utf-8")
        return self._parse(data, station)

    @staticmethod
    def _parse(data: dict, station: str) -> list[CliDay]:
        results = data.get("results") if isinstance(data, dict) else data
        out: list[CliDay] = []
        for rec in results or []:
            d = parse_cli_record(rec, station_hint=station)
            if d is not None:
                out.append(d)
        # Un même jour peut apparaître deux fois (CLI intermédiaire puis
        # final). On garde le dernier produit émis pour chaque date.
        by_day: dict[date, CliDay] = {}
        for d in out:
            by_day[d.valid] = d
        return [by_day[k] for k in sorted(by_day)]

    def fetch_range(self, station: str, start: date, end: date) -> list[CliDay]:
        days: list[CliDay] = []
        for year in range(start.year, end.year + 1):
            days.extend(d for d in self.fetch_year(station, year) if start <= d.valid <= end)
        return days

    def fetch_many(self, stations: Iterable[str], start: date, end: date) -> dict[str, list[CliDay]]:
        return {s.upper(): self.fetch_range(s, start, end) for s in stations}
