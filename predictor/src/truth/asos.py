"""Observations station (IEM ASOS / METAR, api.weather.gov).

FR : Le thermomètre de la station, heure par heure. IEM archive l'historique
METAR/ASOS. api.weather.gov ne garde que les tout derniers jours (souvent
~7). On n'invente aucune température manquante : une heure absente reste
absente.

EN : Station thermometer readings. IEM has the archive. api.weather.gov
only keeps recent observations. Missing values stay missing.
"""
from __future__ import annotations

import csv
import io
import json
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

import requests

from src.config import DATA_DIR, USER_AGENT
from src.truth.iem_cli import kalshi_stations
from src.truth.lst_window import lst_date, standard_utc_offset

IEM_ASOS = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
NWS_BASE = "https://api.weather.gov"
ASOS_DIR = DATA_DIR / "asos"
CACHE_DIR = ASOS_DIR / "cache"
EXTRACTED_PATH = ASOS_DIR / "extracted.json"

# IEM renvoie souvent le code à 3 lettres (NYC). Nos stations Kalshi sont K + 3.
def icao_from_iem(code: str) -> str:
    c = (code or "").strip().upper()
    if len(c) == 3:
        return "K" + c
    return c


def iem_station_id(icao: str) -> str:
    icao = icao.upper()
    if icao.startswith("K") and len(icao) == 4:
        return icao[1:]
    return icao


@dataclass(frozen=True)
class StationObs:
    """Une lecture de température à la station. Jamais inventée."""
    station: str                 # ICAO, ex KNYC
    valid: datetime              # UTC
    tmp_f: float
    source: str                  # "iem" | "nws"

    def to_compact(self) -> dict:
        return {
            "station": self.station,
            "valid": self.valid.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tmp_f": round(self.tmp_f, 2),
            "source": self.source,
        }


def from_compact(r: dict) -> StationObs:
    return StationObs(
        station=str(r["station"]).upper(),
        valid=datetime.fromisoformat(str(r["valid"]).replace("Z", "+00:00")).astimezone(timezone.utc),
        tmp_f=float(r["tmp_f"]),
        source=str(r.get("source") or "iem"),
    )


def _parse_tmpf(raw: str) -> Optional[float]:
    if raw is None:
        return None
    s = str(raw).strip()
    if s == "" or s.upper() == "M":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _parse_valid(raw: str) -> Optional[datetime]:
    if not raw:
        return None
    s = str(raw).strip()
    if s.endswith("Z"):
        s = s[:-1]
    if "+" in s[10:]:
        s = s.split("+")[0]
    s = s.replace("T", " ")
    for fmt, n in (("%Y-%m-%d %H:%M:%S", 19), ("%Y-%m-%d %H:%M", 16)):
        try:
            return datetime.strptime(s[:n], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def parse_iem_csv(text: str, station_hint: Optional[str] = None) -> list[StationObs]:
    """Parse le CSV IEM. Les lignes sans température lisible sont jetées."""
    out: list[StationObs] = []
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return out
    for row in reader:
        tmp = _parse_tmpf(row.get("tmpf") or row.get("tmp_f") or row.get("tmpf_f"))
        valid = _parse_valid(row.get("valid") or row.get("valid_utc"))
        if tmp is None or valid is None:
            continue
        st = icao_from_iem(row.get("station") or station_hint or "")
        if station_hint:
            st = station_hint.upper()
        if not st:
            continue
        out.append(StationObs(station=st, valid=valid, tmp_f=tmp, source="iem"))
    return out


def parse_nws_feature(feat: dict, station_hint: str) -> Optional[StationObs]:
    """Une observation api.weather.gov. None si la température manque."""
    props = feat.get("properties") if isinstance(feat, dict) else None
    if not isinstance(props, dict):
        return None
    temp = props.get("temperature") or {}
    val = temp.get("value") if isinstance(temp, dict) else None
    if val is None:
        return None
    try:
        c = float(val)
    except (TypeError, ValueError):
        return None
    raw_ts = props.get("timestamp")
    valid = _parse_valid(str(raw_ts) if raw_ts else "")
    if valid is None:
        return None
    return StationObs(
        station=station_hint.upper(),
        valid=valid,
        tmp_f=c * 9.0 / 5.0 + 32.0,
        source="nws",
    )


def observed_extreme_so_far(
    obs: Iterable[StationObs],
    tz_name: str,
    target: date,
    as_of: datetime,
    kind: str,
    min_obs: int = 4,
    max_stale_hours: float = 3.0,
) -> Optional[dict]:
    """Max ou min déjà mesuré du jour LST, strictement à ou avant `as_of`.

    Renvoie None si trop peu de lectures, ou si la dernière est trop vieille.
    Aucune valeur n'est inventée.
    """
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)
    picked: list[StationObs] = []
    for o in obs:
        if o.valid > as_of:
            continue
        if lst_date(o.valid, tz_name) != target:
            continue
        picked.append(o)
    if len(picked) < min_obs:
        return None
    picked.sort(key=lambda o: o.valid)
    last = picked[-1]
    stale_h = (as_of - last.valid).total_seconds() / 3600.0
    if stale_h > max_stale_hours:
        return None
    vals = [o.tmp_f for o in picked]
    extreme = max(vals) if kind == "max" else min(vals)
    off = standard_utc_offset(tz_name, as_of)
    lst_midnight = datetime(target.year, target.month, target.day, tzinfo=timezone.utc) - off
    hours_open = max(0.0, (as_of - lst_midnight).total_seconds() / 3600.0)
    return {
        "extreme_f": extreme,
        "n_obs": len(picked),
        "first": picked[0].valid,
        "last": last.valid,
        "stale_hours": stale_h,
        "hours_open": hours_open,
        "coverage": len(picked) / max(1.0, hours_open),
    }


class IemAsosClient:
    """Archive horaire IEM. Cache CSV par station et par mois."""

    def __init__(
        self,
        cache_dir: Path = CACHE_DIR,
        extracted_path: Path = EXTRACTED_PATH,
        sleep_s: float = 0.35,
        timeout_s: float = 90.0,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_path = Path(extracted_path)
        self.extracted_path.parent.mkdir(parents=True, exist_ok=True)
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "text/plain, text/csv, */*"})

    def _cache_path(self, icao: str, year: int, month: int) -> Path:
        return self.cache_dir / f"iem_{icao}_{year}{month:02d}.csv"

    def fetch_month(self, icao: str, year: int, month: int, use_cache: bool = True) -> list[StationObs]:
        icao = icao.upper()
        path = self._cache_path(icao, year, month)
        if use_cache and path.exists() and path.stat().st_size > 20:
            return parse_iem_csv(path.read_text(encoding="utf-8", errors="replace"), station_hint=icao)
        start = date(year, month, 1)
        if month == 12:
            end = date(year, 12, 31)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)
        params = {
            "station": iem_station_id(icao),
            "data": "tmpf",
            "year1": start.year, "month1": start.month, "day1": start.day,
            "year2": end.year, "month2": end.month, "day2": end.day,
            "tz": "UTC",
            "format": "onlycomma",
            "latlon": "no",
            "elev": "no",
            "missing": "M",
            "trace": "T",
            "direct": "no",
            "report_type": "3",
        }
        time.sleep(self.sleep_s)
        resp = self.session.get(IEM_ASOS, params=params, timeout=self.timeout_s)
        resp.raise_for_status()
        text = resp.text
        path.write_text(text, encoding="utf-8")
        return parse_iem_csv(text, station_hint=icao)

    def fetch_range(self, icao: str, start: date, end: date, use_cache: bool = True) -> list[StationObs]:
        rows: list[StationObs] = []
        y, m = start.year, start.month
        while date(y, m, 1) <= end:
            rows.extend(self.fetch_month(icao, y, m, use_cache=use_cache))
            if m == 12:
                y, m = y + 1, 1
            else:
                m += 1
        return [o for o in rows if start <= o.valid.date() <= end + timedelta(days=1)]

    def persist_extracted(self, rows: list[StationObs]) -> Path:
        compact = [o.to_compact() for o in rows]
        compact.sort(key=lambda r: (r["station"], r["valid"]))
        self.extracted_path.write_text(json.dumps(compact), encoding="utf-8")
        return self.extracted_path

    def load_extracted(self) -> list[StationObs]:
        if not self.extracted_path.exists():
            return []
        data = json.loads(self.extracted_path.read_text(encoding="utf-8"))
        return [from_compact(r) for r in data]


class NwsObservationClient:
    """Observations récentes api.weather.gov. Pas d'archive été 2026."""

    def __init__(self, sleep_s: float = 1.0, timeout_s: float = 30.0):
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/geo+json, application/json",
        })

    def fetch_recent(self, icao: str, limit: int = 500) -> list[StationObs]:
        icao = icao.upper()
        time.sleep(self.sleep_s)
        url = f"{NWS_BASE}/stations/{icao}/observations"
        resp = self.session.get(url, params={"limit": limit}, timeout=self.timeout_s)
        resp.raise_for_status()
        feats = (resp.json() or {}).get("features") or []
        out: list[StationObs] = []
        for feat in feats:
            o = parse_nws_feature(feat, icao)
            if o is not None:
                out.append(o)
        out.sort(key=lambda o: o.valid)
        return out

    def probe_span(self, icao: str) -> dict:
        """Dit jusqu'où l'API remonte. N'invente rien si elle est vide."""
        try:
            rows = self.fetch_recent(icao, limit=500)
        except requests.RequestException as e:
            return {"station": icao, "n": 0, "error": str(e)}
        if not rows:
            return {"station": icao, "n": 0, "oldest": None, "newest": None,
                    "comment": "aucune observation renvoyée"}
        return {
            "station": icao,
            "n": len(rows),
            "oldest": rows[0].valid.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "newest": rows[-1].valid.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "comment": "api.weather.gov ne garde que les jours récents, pas l'été 2026.",
        }


def index_obs(rows: Iterable[StationObs]) -> dict[str, list[StationObs]]:
    by: dict[str, list[StationObs]] = {}
    for o in rows:
        by.setdefault(o.station, []).append(o)
    for st in by:
        by[st].sort(key=lambda o: o.valid)
    return by


def default_stations() -> list[str]:
    return list(kalshi_stations())
