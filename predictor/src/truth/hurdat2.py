"""HURDAT2 Atlantic best-track (NHC / NOAA).

FR : Vérité officielle pour le nom de catalogue « HURDAT2 / IBTrACS ».
Atlantique seulement (Golfe du Mexique et mer des Caraïbes compris).
On ne invente pas de classe, pas de côte américaine, pas de saison 2026.

EN : Official NHC Atlantic HURDAT2. Catalogue name stays
« HURDAT2 / IBTrACS ». Status codes and the L landfall flag are used
as published. Saffir-Simpson categories come from the NHC knot table,
not from a homemade scale.

NHC file page : https://www.nhc.noaa.gov/data/
Directory     : https://www.nhc.noaa.gov/data/hurdat/
Format PDF    : https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atl-1851-2021.pdf
SSHWS knots   : https://www.nhc.noaa.gov/aboutsshws.php
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urljoin

import requests

from src.config import DATA_DIR, USER_AGENT

HURDAT2_PAGE = "https://www.nhc.noaa.gov/data/"
HURDAT2_DIR = "https://www.nhc.noaa.gov/data/hurdat/"
HURDAT2_FORMAT_PDF = (
    "https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atl-1851-2021.pdf"
)
SSHWS_URL = "https://www.nhc.noaa.gov/aboutsshws.php"
HURDAT2_CACHE = DATA_DIR / "truth" / "hurdat2_cache"
HURDAT2_OUT = DATA_DIR / "truth" / "hurdat2"

# Official HURDAT2 status codes (format PDF). Do not add a homemade status.
HURDAT2_STATUSES = ("TD", "TS", "HU", "EX", "SD", "SS", "LO", "WV", "DB")
TROPICAL_OR_SUBTROPICAL = ("TD", "TS", "HU", "SD", "SS")
# NHC "named storm" = tropical storm, subtropical storm, or hurricane.
NAMED_STATUSES = ("TS", "SS", "HU")
SYNOPTIC_HHMM = ("0000", "0600", "1200", "1800")

# Official Saffir-Simpson Hurricane Wind Scale, knots (NHC page).
# TD / TS are not SSHWS categories; they are listed so wind is never invented.
SSHWS_KNOTS = (
    ("TD", 0, 33),
    ("TS", 34, 63),
    ("1", 64, 82),
    ("2", 83, 95),
    ("3", 96, 112),
    ("4", 113, 136),
    ("5", 137, 999),
)
MAJOR_MIN_KT = 96  # official: Category 3 and higher = major hurricane
MISSING_WIND = -99
MISSING_PRES = -999

# Official NHC Atlantic hurricane season window (calendar, not a product).
SEASON_START_MD = (6, 1)
SEASON_END_MD = (11, 30)

# ACE threshold already written in predictor/PHASE_B_SCAFFOLDING.md §3.4a.
# Used only as a counting threshold, not as a priced product.
ACE_HYPERACTIVE = 159.0
# Named-storm threshold already written in §3.4c.
NAMED_STORMS_THRESHOLD = 18

HEADER_RE = re.compile(r"^[A-Z]{2}\d{6}$")
ATL_FILE_RE = re.compile(
    r'href="(hurdat2-1851-(\d{4})-(\d+)\.txt)"', re.IGNORECASE
)


def sshws_from_knots(wind_kt: Optional[int]) -> Optional[str]:
    """Map a published 1-min wind to the official SSHWS / NHC status table."""
    if wind_kt is None or wind_kt == MISSING_WIND:
        return None
    if wind_kt < 0:
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


def in_official_season(d: date) -> bool:
    md = (d.month, d.day)
    return SEASON_START_MD <= md <= SEASON_END_MD


def ace_contribution(wind_kt: Optional[int], hhmm: str, status: str) -> float:
    """Official ACE increment: v²/10⁴ at synoptic times, named-storm intensity.

    NHC glossary: sum of the square of maximum wind (10⁴ kt²) every 6 hours
    while the system is a named storm. Missing wind is skipped, not invented.
    """
    if hhmm not in SYNOPTIC_HHMM:
        return 0.0
    if status not in NAMED_STATUSES:
        return 0.0
    if wind_kt is None or wind_kt < 34:
        return 0.0
    return (wind_kt * wind_kt) / 10_000.0


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
    def is_landfall(self) -> bool:
        return self.record_id == "L"

    def to_json(self) -> dict[str, Any]:
        return {
            "date": self.when.isoformat(),
            "hhmm": self.hhmm,
            "record_id": self.record_id,
            "status": self.status,
            "lat": self.lat,
            "lon": self.lon,
            "wind_kt": self.wind_kt,
            "pres_mb": self.pres_mb,
            "sshws": sshws_from_knots(self.wind_kt),
        }


@dataclass
class HurdatStorm:
    storm_id: str
    name: str
    n_declared: int
    points: list[HurdatPoint] = field(default_factory=list)

    @property
    def basin(self) -> str:
        return self.storm_id[:2]

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
    def peak_sshws(self) -> Optional[str]:
        return sshws_from_knots(self.peak_wind_kt)

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
    def n_landfalls(self) -> int:
        return len(self.landfall_points)

    @property
    def hu_landfall(self) -> bool:
        return any(p.status == "HU" for p in self.landfall_points)

    @property
    def major_landfall(self) -> bool:
        return any(is_major(p.wind_kt) for p in self.landfall_points)

    @property
    def ace(self) -> float:
        return sum(ace_contribution(p.wind_kt, p.hhmm, p.status) for p in self.points)

    @property
    def first_date(self) -> Optional[date]:
        return self.points[0].when if self.points else None

    @property
    def last_date(self) -> Optional[date]:
        return self.points[-1].when if self.points else None

    def to_json(self) -> dict[str, Any]:
        return {
            "storm_id": self.storm_id,
            "name": self.name,
            "year": self.year,
            "n_declared": self.n_declared,
            "n_points": len(self.points),
            "first_date": self.first_date.isoformat() if self.first_date else None,
            "last_date": self.last_date.isoformat() if self.last_date else None,
            "statuses": sorted(self.statuses),
            "reached_named": self.reached_named,
            "reached_hu": self.reached_hu,
            "reached_major": self.reached_major,
            "peak_wind_kt": self.peak_wind_kt,
            "peak_sshws": self.peak_sshws,
            "n_landfalls_L": self.n_landfalls,
            "hu_landfall_L": self.hu_landfall,
            "major_landfall_L": self.major_landfall,
            "ace": round(self.ace, 4),
            "in_official_season": bool(
                self.first_date and in_official_season(self.first_date)
            ),
        }


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
    """Parse a full HURDAT2 Atlantic file. Gaps are listed, never filled."""
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
            gaps.append(
                f"{storm_id}: declared {n_decl} points, parsed {len(points)}"
            )
        storms.append(HurdatStorm(storm_id, name, n_decl, points))
    return storms, gaps


def discover_atlantic_filename(html: str) -> Optional[dict[str, str]]:
    """Pick the newest hurdat2-1851-YYYY-*.txt from the NHC directory listing."""
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
    """Download the current Atlantic HURDAT2 file. Nothing invented on a miss."""

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


def season_rows(storms: Iterable[HurdatStorm]) -> list[dict[str, Any]]:
    """One measured row per HURDAT2 year."""
    by_year: dict[int, list[HurdatStorm]] = {}
    for s in storms:
        by_year.setdefault(s.year, []).append(s)
    rows = []
    for year in sorted(by_year):
        group = by_year[year]
        named = [s for s in group if s.reached_named]
        hu = [s for s in group if s.reached_hu]
        major = [s for s in group if s.reached_major]
        land = [s for s in group if s.n_landfalls]
        hu_land = [s for s in group if s.hu_landfall]
        major_land = [s for s in group if s.major_landfall]
        ace = sum(s.ace for s in group)
        rows.append({
            "year": year,
            "n_systems": len(group),
            "n_named": len(named),
            "n_hurricanes": len(hu),
            "n_major": len(major),
            "n_with_L": len(land),
            "n_hu_landfall_L": len(hu_land),
            "n_major_landfall_L": len(major_land),
            "n_L_points": sum(s.n_landfalls for s in group),
            "ace": round(ace, 4),
            "event_named_ge_18": len(named) >= NAMED_STORMS_THRESHOLD,
            "event_ace_ge_159": ace >= ACE_HYPERACTIVE,
            "event_any_hu_landfall_L": bool(hu_land),
            "event_any_major_landfall_L": bool(major_land),
        })
    return rows


def coverage_table(storms: list[HurdatStorm], gaps: list[str]) -> dict[str, Any]:
    """Measured storm / year / intensity / landfall counts. Empty stays empty."""
    if not storms:
        return {"n_systems": 0, "gaps": gaps}
    years = [s.year for s in storms]
    first_year, last_year = min(years), max(years)
    expected_years = list(range(first_year, last_year + 1))
    have_years = set(years)
    missing_years = [y for y in expected_years if y not in have_years]
    peak_cats = {label: 0 for label, _, _ in SSHWS_KNOTS}
    n_peak_unknown = 0
    for s in storms:
        cat = s.peak_sshws
        if cat is None:
            n_peak_unknown += 1
        else:
            peak_cats[cat] += 1
    seasons = season_rows(storms)
    winds = [s.peak_wind_kt for s in storms if s.peak_wind_kt is not None]
    return {
        "basin": "AL",
        "n_systems": len(storms),
        "first_year": first_year,
        "last_year": last_year,
        "n_years_with_a_system": len(have_years),
        "n_years_span": last_year - first_year + 1,
        "missing_years_in_span": missing_years,
        "n_missing_years_in_span": len(missing_years),
        "n_named": sum(1 for s in storms if s.reached_named),
        "n_hurricanes_HU": sum(1 for s in storms if s.reached_hu),
        "n_major_sshws": sum(1 for s in storms if s.reached_major),
        "n_with_L": sum(1 for s in storms if s.n_landfalls),
        "n_L_points": sum(s.n_landfalls for s in storms),
        "n_hu_landfall_L": sum(1 for s in storms if s.hu_landfall),
        "n_major_landfall_L": sum(1 for s in storms if s.major_landfall),
        "n_peak_wind_missing": n_peak_unknown,
        "peak_sshws_counts": peak_cats,
        "peak_wind_kt_max": max(winds) if winds else None,
        "n_seasons": len(seasons),
        "n_seasons_named_ge_18": sum(1 for r in seasons if r["event_named_ge_18"]),
        "n_seasons_ace_ge_159": sum(1 for r in seasons if r["event_ace_ge_159"]),
        "n_seasons_any_hu_landfall_L": sum(
            1 for r in seasons if r["event_any_hu_landfall_L"]
        ),
        "n_seasons_any_major_landfall_L": sum(
            1 for r in seasons if r["event_any_major_landfall_L"]
        ),
        "ace_all_storms": round(sum(s.ace for s in storms), 4),
        "parse_gaps": gaps,
        "n_parse_gaps": len(gaps),
        "landfall_L_gap": (
            "Le drapeau L de HURDAT2 marque le centre qui croise une côte. "
            "Le PDF de format NHC dit que les landfalls des États-Unis "
            "continentaux sont marqués 1851-1970 et depuis 1991 ; les "
            "landfalls hors États-Unis seulement 1951-1970 et depuis 1991. "
            "On ne redessine pas la côte. On ne sépare pas US / ailleurs."
        ),
        "sshws_source": SSHWS_URL,
        "format_source": HURDAT2_FORMAT_PDF,
        "thresholds_count_only": {
            "ace_ge": ACE_HYPERACTIVE,
            "named_ge": NAMED_STORMS_THRESHOLD,
            "source": "PHASE_B_SCAFFOLDING.md §3.4 (count only)",
        },
    }
