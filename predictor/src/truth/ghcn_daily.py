"""Client GHCN-Daily (NCEI) pour les 18 stations de résolution Kalshi.

FR : GHCN-Daily publie le max et le min quotidiens de la même famille de
stations USW que le rapport CLI. C'est la plus longue série officielle
disponible. On ne colle pas une autre station plus ancienne (aéroport
déménagé, ville vs aéroport) : ce ne serait plus le même thermomètre.

EN : GHCN-Daily TMAX/TMIN for the USW station that matches the Kalshi
resolution site. Predecessor / city-office IDs are not spliced in.

TMAX/TMIN sont en dixièmes de °C. On convertit en °F entier avec le même
arrondi half-up que le NWS (voir apply_nws_rounding). Les valeurs avec un
drapeau qualité (QFLAG) sont rejetées, jamais inventées.

Fichiers .dly : https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/{ID}.dly
Inventaire des IDs : ghcnd-stations.txt, apparié par coordonnées (2026-09-12).
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

import requests

from src.config import DATA_DIR, USER_AGENT
from src.kalshi.resolution import apply_nws_rounding

GHCN_DLY_BASE = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all"
GHCN_CACHE = DATA_DIR / "truth" / "ghcn_cache"
MISSING = -9999

# ICAO Kalshi → ID GHCN-Daily USW, vérifié le 2026-09-12 contre
# ghcnd-stations.txt (plus proche USW au point NWS de resolution.py).
# name = libellé GHCN tel quel. On n'invente pas d'année de début ici.
ICAO_TO_GHCN: dict[str, dict[str, str]] = {
    "KATL": {"ghcn_id": "USW00013874", "ghcn_name": "ATLANTA HARTSFIELD-JACKSON INT"},
    "KAUS": {"ghcn_id": "USW00013904", "ghcn_name": "AUSTIN BERGSTROM INTL AP"},
    "KBOS": {"ghcn_id": "USW00014739", "ghcn_name": "BOSTON"},
    "KMDW": {"ghcn_id": "USW00014819", "ghcn_name": "CHICAGO MIDWAY AP"},
    "KDFW": {"ghcn_id": "USW00003927", "ghcn_name": "DAL-FTW WSCMO AP"},
    "KDEN": {"ghcn_id": "USW00003017", "ghcn_name": "DENVER INTL AP"},
    "KHOU": {"ghcn_id": "USW00012918", "ghcn_name": "HOUSTON WILLIAM P HOBBY AP"},
    "KLAS": {"ghcn_id": "USW00023169", "ghcn_name": "MCCARRAN INTL AP"},
    "KLAX": {"ghcn_id": "USW00023174", "ghcn_name": "LOS ANGELES INTL AP"},
    "KMIA": {"ghcn_id": "USW00012839", "ghcn_name": "MIAMI INTL AP"},
    "KMSP": {"ghcn_id": "USW00014922", "ghcn_name": "MINNEAPOLIS-ST PAUL INTL AP"},
    "KNYC": {"ghcn_id": "USW00094728", "ghcn_name": "NY CITY CNTRL PARK"},
    "KPHL": {"ghcn_id": "USW00013739", "ghcn_name": "PHILA INTL AP"},
    "KPHX": {"ghcn_id": "USW00023183", "ghcn_name": "PHOENIX AP"},
    "KSAT": {"ghcn_id": "USW00012921", "ghcn_name": "SAN ANTONIO INTL AP"},
    "KSFO": {"ghcn_id": "USW00023234", "ghcn_name": "SAN FRANCISCO INTL AP"},
    "KSEA": {"ghcn_id": "USW00024233", "ghcn_name": "SEATTLE TACOMA AP"},
    "KDCA": {"ghcn_id": "USW00013743", "ghcn_name": "WASHINGTON REAGAN NATL AP"},
}


def tenths_c_to_f(tenths: int) -> int:
    """Dixièmes de °C → °F entier, arrondi half-up NWS."""
    f = (tenths / 10.0) * 9.0 / 5.0 + 32.0
    return int(apply_nws_rounding(f, "nearest_int"))


def tenths_mm_to_inches(tenths: int) -> float:
    """Dixièmes de mm GHCN → pouces. Trace et manquant sont exclus en amont."""
    return (tenths / 10.0) / 25.4


@dataclass(frozen=True)
class GhcnDay:
    """Un jour GHCN-Daily / One GHCN-Daily day."""
    station: str          # ICAO
    ghcn_id: str
    valid: date
    high_f: Optional[int]
    low_f: Optional[int]
    precip_in: Optional[float] = None


def parse_dly(text: str, station: str, ghcn_id: str,
              elements: tuple[str, ...] = ("TMAX", "TMIN", "PRCP")) -> list[GhcnDay]:
    """Parse un fichier .dly. Ignore QFLAG non vide et les jours calendaires impossibles."""
    wanted = set(elements)
    by_date: dict[date, dict[str, int]] = {}
    for raw in text.splitlines():
        if len(raw) < 21:
            continue
        elem = raw[17:21]
        if elem not in wanted:
            continue
        try:
            year = int(raw[11:15])
            month = int(raw[15:17])
        except ValueError:
            continue
        for day in range(1, 32):
            base = 21 + (day - 1) * 8
            if base + 8 > len(raw):
                break
            try:
                val = int(raw[base:base + 5])
            except ValueError:
                continue
            qflag = raw[base + 6:base + 7]
            if val == MISSING or qflag.strip():
                continue
            try:
                valid = date(year, month, day)
            except ValueError:
                continue
            by_date.setdefault(valid, {})[elem] = val
    out: list[GhcnDay] = []
    for valid in sorted(by_date):
        rec = by_date[valid]
        tmax = rec.get("TMAX")
        tmin = rec.get("TMIN")
        prcp = rec.get("PRCP")
        out.append(GhcnDay(
            station=station, ghcn_id=ghcn_id, valid=valid,
            high_f=None if tmax is None else tenths_c_to_f(tmax),
            low_f=None if tmin is None else tenths_c_to_f(tmin),
            precip_in=None if prcp is None else tenths_mm_to_inches(prcp),
        ))
    return out


class GhcnDailyClient:
    """Télécharge et cache les .dly GHCN-Daily (un fichier par station)."""

    def __init__(self, cache_dir: Path = GHCN_CACHE, stale_hours: float = 24.0,
                 sleep_s: float = 0.4):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.stale_hours = stale_hours
        self.sleep_s = sleep_s
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/plain"})

    def _path(self, ghcn_id: str) -> Path:
        return self.cache_dir / f"{ghcn_id}.dly"

    def fetch_raw(self, ghcn_id: str, use_cache: bool = True,
                  allow_network: bool = True) -> str:
        path = self._path(ghcn_id)
        if use_cache and path.exists():
            age_h = (time.time() - path.stat().st_mtime) / 3600.0
            if (not allow_network) or age_h < self.stale_hours:
                return path.read_text(encoding="ascii", errors="replace")
        if not allow_network:
            raise FileNotFoundError(f"cache GHCN absent : {path}")
        last: Optional[BaseException] = None
        url = f"{GHCN_DLY_BASE}/{ghcn_id}.dly"
        for attempt in range(3):
            try:
                time.sleep(self.sleep_s)
                resp = self.session.get(url, timeout=90)
                if resp.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue
                resp.raise_for_status()
                text = resp.text
                path.write_text(text, encoding="ascii")
                return text
            except (requests.RequestException, OSError) as e:
                last = e
                time.sleep(1 + attempt)
        raise RuntimeError(f"GHCN-Daily fetch failed for {ghcn_id}: {last}")

    def fetch_station(self, icao: str, use_cache: bool = True,
                      allow_network: bool = True) -> list[GhcnDay]:
        meta = ICAO_TO_GHCN.get(icao.upper())
        if meta is None:
            raise KeyError(f"pas d'ID GHCN pour {icao}")
        text = self.fetch_raw(meta["ghcn_id"], use_cache=use_cache,
                              allow_network=allow_network)
        return parse_dly(text, icao.upper(), meta["ghcn_id"])


def coverage_from_days(days: list[GhcnDay], variable: str) -> dict:
    """Couverture réelle : première / dernière date observée, jours manquants.

    `missing_days` = jours calendaires entre first et last sans valeur
    exploitable. On n'extrapole pas avant first ni après last.
    """
    vals: list[tuple[date, int]] = []
    for d in days:
        v = d.high_f if variable == "temp_max" else d.low_f
        if v is not None:
            vals.append((d.valid, v))
    if not vals:
        return {
            "n_days": 0, "first": None, "last": None,
            "span_days": 0, "missing_days": None,
            "first_year": None, "last_year": None,
            "n_years_with_data": 0, "n_complete_years": 0,
        }
    first, last = vals[0][0], vals[-1][0]
    have = {d for d, _ in vals}
    span = (last - first).days + 1
    missing = span - len(have)
    by_year: dict[int, int] = {}
    for d, _ in vals:
        by_year[d.year] = by_year.get(d.year, 0) + 1
    complete = sum(1 for y, n in by_year.items() if n >= 300)
    return {
        "n_days": len(have),
        "first": first.isoformat(),
        "last": last.isoformat(),
        "span_days": span,
        "missing_days": missing,
        "first_year": first.year,
        "last_year": last.year,
        "n_years_with_data": len(by_year),
        "n_complete_years": complete,
    }
