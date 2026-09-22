"""HURDAT2 Atlantique, pour comparer un marché ou un a-deck à la vérité.

FR : Même fichier officiel NHC que la note PR 241 (HURDAT2 / IBTrACS).
On ne renomme pas le catalogue. On n'invente pas de statut ni de côte.
La saison 2026 n'est pas dans le fichier publié (arrêt 2025).

EN : Official NHC Atlantic HURDAT2. Catalogue name stays
« HURDAT2 / IBTrACS ». Used here only to match Kalshi / NHC decks.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urljoin

import requests

from src.config import DATA_DIR, USER_AGENT

HURDAT2_DIR = "https://www.nhc.noaa.gov/data/hurdat/"
HURDAT2_FORMAT_PDF = (
    "https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atl-1851-2021.pdf"
)
SSHWS_URL = "https://www.nhc.noaa.gov/aboutsshws.php"
HURDAT2_CACHE = DATA_DIR / "truth" / "hurdat2_cache"

# PR 241 measured totals on hurdat2-1851-2025-02272026.txt. Cited, not invented.
PR241_HU = 978
PR241_MAJOR = 342
PR241_HU_LANDFALL_L = 376
PR241_YEARS = (1851, 2025)
PR241_SYSTEMS = 2004

HURDAT2_STATUSES = ("TD", "TS", "HU", "EX", "SD", "SS", "LO", "WV", "DB")
NAMED_STATUSES = ("TS", "SS", "HU")
SYNOPTIC_HHMM = ("0000", "0600", "1200", "1800")
SSHWS_KNOTS = (
    ("TD", 0, 33),
    ("TS", 34, 63),
    ("1", 64, 82),
    ("2", 83, 95),
    ("3", 96, 112),
    ("4", 113, 136),
    ("5", 137, 999),
)
MAJOR_MIN_KT = 96
MISSING_WIND = -99
MISSING_PRES = -999
HEADER_RE = re.compile(r"^[A-Z]{2}\d{6}$")
ATL_FILE_RE = re.compile(
    r'href="(hurdat2-1851-(\d{4})-(\d+)\.txt)"', re.IGNORECASE
)


def sshws_from_knots(wind_kt: Optional[int]) -> Optional[str]:
    if wind_kt is None or wind_kt == MISSING_WIND or wind_kt < 0:
        return None
    for label, lo, hi in SSHWS_KNOTS:
        if lo <= wind_kt <= hi:
            return label
    return None


def is_major(wind_kt: Optional[int]) -> bool:
    return wind_kt is not None and wind_kt != MISSING_WIND and wind_kt >= MAJOR_MIN_KT


def parse_lat(token: str) -> float:
    token = token.strip()
    if not token:
        raise ValueError("empty latitude")
    hemi = token[-1].upper()
    value = float(token[:-1])
    if hemi == "S":
        return -value
    if hemi == "N":
        return value
    raise ValueError(f"latitude missing N/S: {token!r}")


def parse_lon(token: str) -> float:
    token = token.strip()
    if not token:
        raise ValueError("empty longitude")
    hemi = token[-1].upper()
    value = float(token[:-1])
    if hemi == "W":
        return -value
    if hemi == "E":
        return value
    raise ValueError(f"longitude missing E/W: {token!r}")


def parse_int_field(token: str, missing: int) -> Optional[int]:
    token = token.strip()
    if token == "":
        return None
    value = int(token)
    if value == missing:
        return None
    return value


@dataclass
class HurdatPoint:
    yyyymmdd: str
    hhmm: str
    record_id: str
    status: str
    lat: float
    lon: float
    wind_kt: Optional[int]
    pres_mb: Optional[int]

    @property
    def when(self) -> date:
        return date(int(self.yyyymmdd[:4]), int(self.yyyymmdd[4:6]), int(self.yyyymmdd[6:8]))

    @property
    def dt(self) -> datetime:
        return datetime(
            int(self.yyyymmdd[:4]), int(self.yyyymmdd[4:6]), int(self.yyyymmdd[6:8]),
            int(self.hhmm[:2]), int(self.hhmm[2:4]),
        )

    @property
    def is_landfall(self) -> bool:
        return self.record_id == "L"


@dataclass
class HurdatStorm:
    storm_id: str
    name: str
    n_declared: int
    points: list[HurdatPoint] = field(default_factory=list)

    @property
    def year(self) -> int:
        return int(self.storm_id[-4:])

    @property
    def statuses(self) -> set[str]:
        return {p.status for p in self.points}

    @property
    def peak_wind_kt(self) -> Optional[int]:
        winds = [p.wind_kt for p in self.points if p.wind_kt is not None]
        return max(winds) if winds else None

    @property
    def reached_hu(self) -> bool:
        return "HU" in self.statuses

    @property
    def reached_named(self) -> bool:
        return bool(self.statuses.intersection(NAMED_STATUSES))

    @property
    def reached_major(self) -> bool:
        return is_major(self.peak_wind_kt)

    @property
    def landfall_points(self) -> list[HurdatPoint]:
        return [p for p in self.points if p.is_landfall]

    @property
    def hu_landfall(self) -> bool:
        return any(p.status == "HU" for p in self.landfall_points)

    @property
    def major_landfall(self) -> bool:
        return any(is_major(p.wind_kt) for p in self.landfall_points)

    def first_status_dt(self, status: str) -> Optional[datetime]:
        for p in self.points:
            if p.status == status:
                return p.dt
        return None

    def point_at(self, when: datetime) -> Optional[HurdatPoint]:
        """Exact synoptic / published time only. No interpolation."""
        for p in self.points:
            if p.dt == when:
                return p
        return None


def parse_header(line: str) -> tuple[str, str, int]:
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 3 or not HEADER_RE.match(parts[0]):
        raise ValueError(f"not a HURDAT2 header: {line!r}")
    return parts[0], parts[1], int(parts[2])


def parse_point(line: str) -> HurdatPoint:
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 8:
        raise ValueError(f"HURDAT2 point too short: {line!r}")
    yyyymmdd = parts[0]
    if len(yyyymmdd) != 8 or not yyyymmdd.isdigit():
        raise ValueError(f"bad HURDAT2 date: {line!r}")
    status = parts[3]
    if status not in HURDAT2_STATUSES:
        raise ValueError(f"unknown HURDAT2 status {status!r}: {line!r}")
    return HurdatPoint(
        yyyymmdd=yyyymmdd,
        hhmm=parts[1],
        record_id=parts[2],
        status=status,
        lat=parse_lat(parts[4]),
        lon=parse_lon(parts[5]),
        wind_kt=parse_int_field(parts[6], MISSING_WIND),
        pres_mb=parse_int_field(parts[7], MISSING_PRES),
    )


def parse_hurdat2(text: str) -> tuple[list[HurdatStorm], list[str]]:
    storms: list[HurdatStorm] = []
    gaps: list[str] = []
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i].strip()
        if not raw:
            i += 1
            continue
        try:
            storm_id, name, n_decl = parse_header(raw)
        except ValueError as exc:
            gaps.append(f"line {i + 1}: {exc}")
            i += 1
            continue
        points: list[HurdatPoint] = []
        i += 1
        taken = 0
        while i < n and taken < n_decl:
            body = lines[i].strip()
            i += 1
            if not body:
                continue
            try:
                points.append(parse_point(body))
            except ValueError as exc:
                gaps.append(f"{storm_id} line {i}: {exc}")
            taken += 1
        if len(points) != n_decl:
            gaps.append(f"{storm_id}: declared {n_decl} points, parsed {len(points)}")
        storms.append(HurdatStorm(storm_id, name, n_decl, points))
    return storms, gaps


def discover_atlantic_filename(html: str) -> Optional[dict[str, str]]:
    found: list[tuple[int, int, str]] = []
    for match in ATL_FILE_RE.finditer(html):
        name, end_year, stamp = match.group(1), int(match.group(2)), int(match.group(3))
        found.append((end_year, stamp, name))
    if not found:
        return None
    end_year, stamp, name = max(found)
    return {
        "filename": name,
        "end_year": str(end_year),
        "issue_stamp": f"{stamp:08d}",
        "url": urljoin(HURDAT2_DIR, name),
    }


class Hurdat2Client:
    def __init__(self, cache_dir: Path = HURDAT2_CACHE, timeout: int = 90):
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def _get_text(self, url: str) -> str:
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.text

    def discover(self, allow_network: bool = True) -> dict[str, str]:
        listing_path = self.cache_dir / "hurdat_directory.html"
        if listing_path.exists():
            html = listing_path.read_text(encoding="utf-8", errors="replace")
        elif allow_network:
            html = self._get_text(HURDAT2_DIR)
            listing_path.parent.mkdir(parents=True, exist_ok=True)
            listing_path.write_text(html, encoding="utf-8")
        else:
            raise FileNotFoundError(f"HURDAT2 directory cache missing: {listing_path}")
        info = discover_atlantic_filename(html)
        if info is None:
            raise ValueError("no hurdat2-1851-YYYY-*.txt in NHC directory listing")
        return info

    def _cached_atlantic(self) -> Optional[Path]:
        files = sorted(self.cache_dir.glob("hurdat2-1851-*.txt"))
        return files[-1] if files else None

    def fetch_atlantic(self, allow_network: bool = True) -> dict[str, Any]:
        try:
            info = self.discover(allow_network=allow_network)
            path = self.cache_dir / info["filename"]
        except (FileNotFoundError, ValueError):
            cached = self._cached_atlantic()
            if cached is None:
                raise
            info = {
                "filename": cached.name,
                "url": urljoin(HURDAT2_DIR, cached.name),
                "end_year": "from_cache",
                "issue_stamp": "from_cache",
            }
            path = cached
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
        elif allow_network:
            text = self._get_text(info["url"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        else:
            raise FileNotFoundError(f"HURDAT2 cache missing: {path}")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        storms, gaps = parse_hurdat2(text)
        return {
            "source": info,
            "path": str(path),
            "sha256": digest,
            "n_bytes": len(text.encode("utf-8")),
            "storms": storms,
            "gaps": gaps,
        }


def season_rows(storms: Iterable[HurdatStorm], through_md: Optional[tuple[int, int]] = None) -> list[dict[str, Any]]:
    """One row per HURDAT2 year. through_md=(12, 1) = Kalshi window to 1 Dec."""
    by_year: dict[int, list[HurdatStorm]] = {}
    for s in storms:
        by_year.setdefault(s.year, []).append(s)
    rows = []
    for year in sorted(by_year):
        group = by_year[year]
        if through_md is not None:
            cutoff = date(year, through_md[0], through_md[1])

            def hu_in_window(storm: HurdatStorm) -> bool:
                return any(p.status == "HU" and p.when <= cutoff for p in storm.points)

            def major_in_window(storm: HurdatStorm) -> bool:
                return any(
                    is_major(p.wind_kt) and p.when <= cutoff for p in storm.points
                )
        else:
            def hu_in_window(storm: HurdatStorm) -> bool:
                return storm.reached_hu

            def major_in_window(storm: HurdatStorm) -> bool:
                return storm.reached_major

        hu = [s for s in group if hu_in_window(s)]
        major = [s for s in group if major_in_window(s)]
        named = [s for s in group if s.reached_named]
        rows.append({
            "year": year,
            "n_systems": len(group),
            "n_named": len(named),
            "n_hurricanes": len(hu),
            "n_major": len(major),
            "n_hu_landfall_L": sum(1 for s in group if s.hu_landfall),
            "n_major_landfall_L": sum(1 for s in group if s.major_landfall),
        })
    return rows


def climato_exceedance(rows: list[dict[str, Any]], field: str, threshold: int) -> dict[str, Any]:
    """P(count > threshold) on measured season rows. Empty stays empty."""
    if not rows:
        return {"n_seasons": 0, "n_exceed": 0, "p": None, "threshold": threshold, "field": field}
    n_ex = sum(1 for r in rows if r[field] > threshold)
    return {
        "n_seasons": len(rows),
        "n_exceed": n_ex,
        "p": n_ex / len(rows),
        "threshold": threshold,
        "field": field,
        "first_year": rows[0]["year"],
        "last_year": rows[-1]["year"],
        "mean": sum(r[field] for r in rows) / len(rows),
    }


def coverage_counts(storms: list[HurdatStorm], gaps: list[str]) -> dict[str, Any]:
    if not storms:
        return {"n_systems": 0, "n_parse_gaps": len(gaps)}
    years = [s.year for s in storms]
    return {
        "n_systems": len(storms),
        "first_year": min(years),
        "last_year": max(years),
        "n_hurricanes_HU": sum(1 for s in storms if s.reached_hu),
        "n_major_sshws": sum(1 for s in storms if s.reached_major),
        "n_hu_landfall_L": sum(1 for s in storms if s.hu_landfall),
        "n_parse_gaps": len(gaps),
        "matches_pr241": (
            len(storms) == PR241_SYSTEMS
            and sum(1 for s in storms if s.reached_hu) == PR241_HU
            and sum(1 for s in storms if s.reached_major) == PR241_MAJOR
            and sum(1 for s in storms if s.hu_landfall) == PR241_HU_LANDFALL_L
            and min(years) == PR241_YEARS[0]
            and max(years) == PR241_YEARS[1]
        ),
    }


def storms_by_id(storms: Iterable[HurdatStorm]) -> dict[str, HurdatStorm]:
    return {s.storm_id: s for s in storms}
