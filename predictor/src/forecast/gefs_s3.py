"""Membres GEFS historiques depuis l'archive publique NOAA S3.

FR : Open-Meteo ne garde les membres que ~3 jours. L'archive
`noaa-gefs-pds` a les 31 membres (contrôle + 30) pour l'été 2026.
On prend TMAX et TMIN sur 6 h dans le fichier surface 0,25°, on
extrait les 18 stations, on jette la grille. Un fichier manquant
est un échec, pas un chiffre inventé.

EN : Historical GEFS 31-member daily extremes at Kalshi stations
from NOAA's public S3 archive, because Open-Meteo drops members
after ~3 days.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

import requests

from src.config import DATA_DIR, USER_AGENT
from src.forecast.grib_point import (
    find_idx_row, kelvin_to_f, parse_idx, points_from_message,
)
from src.truth.iem_cli import kalshi_stations
from src.truth.lst_window import standard_utc_offset

S3_BASE = "https://noaa-gefs-pds.s3.amazonaws.com"
GEFS_DIR = DATA_DIR / "gefs"
CACHE_DIR = GEFS_DIR / "cache"
EXTRACTED_PATH = GEFS_DIR / "extracted.json"

# Contrôle + 30 perturbés = 31, comme l'Ensemble API gfs025.
MEMBER_IDS = ["gec00"] + [f"gep{n:02d}" for n in range(1, 31)]


@dataclass
class FetchFailure:
    source: str
    url: str
    issued: str
    member: str
    fhr: int
    error: str


@dataclass
class GefsDaily:
    """Extrême journalier LST d'un membre GEFS."""
    station: str
    variable: str
    target: date
    lead: int
    issued: datetime
    member: int
    value_f: float
    n_windows: int

    def to_compact(self) -> dict:
        return {
            "station": self.station, "variable": self.variable,
            "target": self.target.isoformat(), "lead": self.lead,
            "issued": self.issued.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "member": self.member, "value_f": round(self.value_f, 2),
            "n_windows": self.n_windows,
        }


def from_compact(r: dict) -> GefsDaily:
    return GefsDaily(
        station=r["station"], variable=r["variable"],
        target=date.fromisoformat(r["target"]), lead=int(r["lead"]),
        issued=datetime.fromisoformat(r["issued"].replace("Z", "+00:00")),
        member=int(r["member"]), value_f=float(r["value_f"]),
        n_windows=int(r.get("n_windows") or 0),
    )


def member_number(member_id: str) -> int:
    if member_id == "gec00":
        return 0
    return int(member_id.replace("gep", ""))


def s3_key(issued: datetime, member_id: str, fhr: int) -> str:
    ymd = issued.strftime("%Y%m%d")
    hh = issued.strftime("%H")
    return (f"gefs.{ymd}/{hh}/atmos/pgrb2sp25/"
            f"{member_id}.t{hh}z.pgrb2s.0p25.f{fhr:03d}")


def window_overlaps_lst(issue: datetime, fhr: int, tz_name: str,
                        target: date, width_h: int = 6) -> bool:
    """La fenêtre [issue+fhr−6 h, issue+fhr] touche-t-elle le jour LST ?"""
    end = issue + timedelta(hours=fhr)
    start = end - timedelta(hours=width_h)
    off = standard_utc_offset(tz_name, issue)
    d0 = (start + off).date()
    d1 = ((end - timedelta(microseconds=1)) + off).date()
    return d0 <= target <= d1


def needed_fhrs(leads: Iterable[int]) -> list[int]:
    """Heures de prévision 6 h qui couvrent les jours cibles US (LST)."""
    fhrs: set[int] = set()
    for lead in leads:
        # Jour LST à lead L : environ fhr L*24 à L*24+30 (côte ouest UTC−8).
        start = max(6, lead * 24)
        end = lead * 24 + 36
        f = start - (start % 6)
        if f < start:
            f += 6
        while f <= end:
            fhrs.add(f)
            f += 6
    return sorted(fhrs)


class GefsS3Client:
    def __init__(
        self,
        cache_dir: Path = CACHE_DIR,
        extracted_path: Path = EXTRACTED_PATH,
        sleep_s: float = 0.0,
        timeout_s: float = 60.0,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_path = Path(extracted_path)
        self.extracted_path.parent.mkdir(parents=True, exist_ok=True)
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/octet-stream, text/plain, */*",
        })

    def _get(self, url: str, headers: Optional[dict] = None) -> requests.Response:
        if self.sleep_s:
            time.sleep(self.sleep_s)
        hdrs = dict(self.session.headers)
        if headers:
            hdrs.update(headers)
        resp = self.session.get(url, headers=hdrs, timeout=self.timeout_s)
        return resp

    def fetch_idx(self, issued: datetime, member_id: str, fhr: int) -> tuple[str, Optional[FetchFailure]]:
        key = s3_key(issued, member_id, fhr)
        url = f"{S3_BASE}/{key}.idx"
        cache = self.cache_dir / f"{key.replace('/', '_')}.idx"
        if cache.exists():
            return cache.read_text(encoding="utf-8", errors="replace"), None
        try:
            resp = self._get(url)
            if resp.status_code == 404:
                fail = FetchFailure("s3", url, issued.isoformat(), member_id, fhr,
                                    "index absent (404)")
                return "", fail
            resp.raise_for_status()
            text = resp.text
        except requests.RequestException as e:
            return "", FetchFailure("s3", url, issued.isoformat(), member_id, fhr, str(e))
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(text, encoding="utf-8")
        return text, None

    def fetch_message(self, issued: datetime, member_id: str, fhr: int,
                      start: int, end: Optional[int]) -> tuple[bytes, Optional[FetchFailure]]:
        key = s3_key(issued, member_id, fhr)
        url = f"{S3_BASE}/{key}"
        headers = {}
        if end is not None:
            headers["Range"] = f"bytes={start}-{end}"
        else:
            headers["Range"] = f"bytes={start}-"
        try:
            resp = self._get(url, headers=headers)
            if resp.status_code == 404:
                return b"", FetchFailure("s3", url, issued.isoformat(), member_id, fhr,
                                         "fichier absent (404)")
            resp.raise_for_status()
            return resp.content, None
        except requests.RequestException as e:
            return b"", FetchFailure("s3", url, issued.isoformat(), member_id, fhr, str(e))

    def extract_file(
        self,
        issued: datetime,
        member_id: str,
        fhr: int,
        coords: dict[str, tuple[float, float]],
        names: tuple[str, ...] = ("TMAX", "TMIN"),
    ) -> tuple[dict[str, dict[str, float]], Optional[FetchFailure]]:
        """{variable GRIB: {station: °F}} pour un fichier membre × échéance."""
        idx_text, fail = self.fetch_idx(issued, member_id, fhr)
        if fail:
            return {}, fail
        rows = parse_idx(idx_text)
        out: dict[str, dict[str, float]] = {}
        for name in names:
            row = find_idx_row(rows, name)
            if row is None:
                continue
            blob, fail = self.fetch_message(issued, member_id, fhr, row["start"], row["end"])
            if fail:
                return {}, fail
            try:
                kelvin = points_from_message(blob, coords)
            except Exception as e:  # noqa: BLE001
                return {}, FetchFailure(
                    "grib", f"{S3_BASE}/{s3_key(issued, member_id, fhr)}",
                    issued.isoformat(), member_id, fhr, f"decode: {e}",
                )
            out[name] = {st: kelvin_to_f(v) for st, v in kelvin.items()}
        if not out:
            return {}, FetchFailure(
                "s3", f"{S3_BASE}/{s3_key(issued, member_id, fhr)}.idx",
                issued.isoformat(), member_id, fhr, "pas de TMAX/TMIN dans l'index",
            )
        return out, None

    def persist_extracted(self, rows: list[GefsDaily]) -> Path:
        existing: dict[str, dict] = {}
        if self.extracted_path.exists():
            try:
                for r in json.loads(self.extracted_path.read_text(encoding="utf-8")):
                    existing[_row_key(r)] = r
            except (json.JSONDecodeError, TypeError, KeyError):
                existing = {}
        for f in rows:
            row = f.to_compact()
            existing[_row_key(row)] = row
        payload = sorted(existing.values(), key=lambda r: (
            r["station"], r["target"], r["variable"], r["lead"], r["member"]))
        self.extracted_path.write_text(
            json.dumps(payload, separators=(",", ":")), encoding="utf-8"
        )
        return self.extracted_path

    def load_extracted(self) -> list[GefsDaily]:
        if not self.extracted_path.exists():
            return []
        return [from_compact(r) for r in json.loads(self.extracted_path.read_text(encoding="utf-8"))]


def _row_key(r: dict) -> str:
    return "|".join([
        r["station"], r["variable"], r["target"], str(r["lead"]),
        r["issued"], str(r["member"]),
    ])


@dataclass
class WindowSample:
    issued: datetime
    fhr: int
    member: int
    station: str
    name: str          # TMAX | TMIN
    value_f: float


def aggregate_from_records(
    samples: list[WindowSample],
    stations: dict[str, dict],
    leads: Iterable[int],
    min_windows: int = 3,
) -> list[GefsDaily]:
    """Max des TMAX / min des TMIN sur les fenêtres qui touchent le jour LST."""
    leads = list(leads)
    buckets: dict[tuple, list[float]] = {}
    issued_of: dict[tuple, datetime] = {}
    for s in samples:
        tz = stations.get(s.station, {}).get("tz")
        if not tz:
            continue
        for lead in leads:
            target = (s.issued.date() + timedelta(days=lead))
            if not window_overlaps_lst(s.issued, s.fhr, tz, target):
                continue
            if s.name == "TMAX":
                variable = "temp_max"
            elif s.name == "TMIN":
                variable = "temp_min"
            else:
                continue
            key = (s.station, variable, target, lead, s.member)
            buckets.setdefault(key, []).append(s.value_f)
            issued_of[key] = s.issued

    out: list[GefsDaily] = []
    for key, vals in buckets.items():
        if len(vals) < min_windows:
            continue
        station, variable, target, lead, member = key
        value = max(vals) if variable == "temp_max" else min(vals)
        out.append(GefsDaily(
            station=station, variable=variable, target=target, lead=lead,
            issued=issued_of[key], member=member, value_f=value,
            n_windows=len(vals),
        ))
    return out


@dataclass
class FetchResult:
    forecasts: list[GefsDaily] = field(default_factory=list)
    failures: list[FetchFailure] = field(default_factory=list)
    n_files_ok: int = 0
    n_from_idx_cache: int = 0


def fetch_range(
    client: GefsS3Client,
    start_issue: date,
    end_issue: date,
    leads: list[int],
    cycle_hour: int = 0,
    stations: Optional[dict[str, dict]] = None,
    members: Optional[list[str]] = None,
    workers: int = 8,
) -> FetchResult:
    """Télécharge les membres GEFS 00z de `start_issue` à `end_issue`."""
    stations = stations or kalshi_stations()
    members = members or list(MEMBER_IDS)
    coords = {icao: (meta["lat"], meta["lon"]) for icao, meta in stations.items()}
    fhrs = needed_fhrs(leads)
    jobs = []
    d = start_issue
    while d <= end_issue:
        issued = datetime(d.year, d.month, d.day, cycle_hour, tzinfo=timezone.utc)
        for mid in members:
            for fhr in fhrs:
                jobs.append((issued, mid, fhr))
        d += timedelta(days=1)

    result = FetchResult()
    samples: list[WindowSample] = []

    def _one(job):
        issued, mid, fhr = job
        extracted, fail = client.extract_file(issued, mid, fhr, coords)
        return issued, mid, fhr, extracted, fail

    workers = max(1, min(workers, len(jobs) or 1))
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_one, job) for job in jobs]
        for fut in as_completed(futs):
            issued, mid, fhr, extracted, fail = fut.result()
            done += 1
            if done == 1 or done % 200 == 0 or done == len(jobs):
                print(f"   GEFS fichiers {done}/{len(jobs)}", flush=True)
            if fail:
                result.failures.append(fail)
                continue
            result.n_files_ok += 1
            mem = member_number(mid)
            for name, by_st in extracted.items():
                for st, val in by_st.items():
                    samples.append(WindowSample(issued, fhr, mem, st, name, val))

    result.forecasts = aggregate_from_records(samples, stations, leads)
    return result
