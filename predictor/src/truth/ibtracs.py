"""IBTrACS North Atlantic CSV (NCEI / NOAA), v04r01.

FR : Même nom de catalogue « HURDAT2 / IBTrACS ». On lit le fichier NA
officiel. On ne compte pas les tracks « spur » (consigne NCEI). On ne
invente pas de côte, pas de catégorie.

EN : Official IBTrACS v04r01 North Atlantic list. LANDFALL=0 and
USA_RECORD L are counted as published. USA_SSHS uses the published
scale. Spur tracks are excluded when counting storms, as the NCEI
column documentation says they should not likely be counted.

CSV   : https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NA.list.v04r01.csv
Columns: https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/doc/IBTrACS_v04r01_column_documentation.pdf
Product: https://www.ncei.noaa.gov/products/international-best-track-archive
"""
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

import requests

from src.config import DATA_DIR, USER_AGENT
from src.truth.hurdat2 import MAJOR_MIN_KT, is_major, sshws_from_knots

IBTRACS_VERSION = "v04r01"
IBTRACS_CSV_DIR = (
    "https://www.ncei.noaa.gov/data/"
    "international-best-track-archive-for-climate-stewardship-ibtracs/"
    f"{IBTRACS_VERSION}/access/csv/"
)
IBTRACS_NA_FILENAME = f"ibtracs.NA.list.{IBTRACS_VERSION}.csv"
IBTRACS_NA_URL = IBTRACS_CSV_DIR + IBTRACS_NA_FILENAME
IBTRACS_COLUMNS_PDF = (
    "https://www.ncei.noaa.gov/data/"
    "international-best-track-archive-for-climate-stewardship-ibtracs/"
    f"{IBTRACS_VERSION}/doc/IBTrACS_v04r01_column_documentation.pdf"
)
IBTRACS_PRODUCT = (
    "https://www.ncei.noaa.gov/products/international-best-track-archive"
)
IBTRACS_CACHE = DATA_DIR / "truth" / "ibtracs_cache"

# Official USA_SSHS scale (NCEI column PDF). Do not add a homemade class.
USA_SSHS_LABELS = {
    -5: "unknown",
    -4: "post_tropical",
    -3: "misc_disturbance",
    -2: "subtropical",
    -1: "tropical_depression",
    0: "tropical_storm",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
}

# Official TRACK_TYPE values that NCEI says should not likely be counted.
# The v04r01 NA file also uses "spur-other" and "spur-merge" (measured).
SPUR_TYPE_PREFIXES = ("spur",)
PROVISIONAL_PREFIXES = ("provisional", "us-provisional")


def is_spur_type(track_type: str) -> bool:
    return track_type.lower().startswith(SPUR_TYPE_PREFIXES)


def is_provisional_type(track_type: str) -> bool:
    return track_type.lower().startswith(PROVISIONAL_PREFIXES)

NEEDED_COLS = (
    "SID", "SEASON", "NUMBER", "BASIN", "NAME", "ISO_TIME", "NATURE",
    "TRACK_TYPE", "DIST2LAND", "LANDFALL", "USA_ATCF_ID", "USA_RECORD",
    "USA_STATUS", "USA_WIND", "USA_SSHS",
)


def _cell(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def _opt_int(raw: str) -> Optional[int]:
    if raw == "" or raw in {"-999", "-99", "-9999"}:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def _opt_float(raw: str) -> Optional[float]:
    if raw == "" or raw in {"-999", "-99", "-9999"}:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


@dataclass
class IbtracsPoint:
    iso_time: str
    nature: str
    track_type: str
    landfall_km: Optional[float]
    dist2land_km: Optional[float]
    usa_record: str
    usa_status: str
    usa_wind: Optional[int]
    usa_sshs: Optional[int]

    @property
    def landfall_flag_zero(self) -> bool:
        return self.landfall_km == 0.0

    @property
    def usa_record_L(self) -> bool:
        return self.usa_record == "L"


@dataclass
class IbtracsStorm:
    sid: str
    season: int
    name: str
    basin: str
    usa_atcf_id: str
    points: list[IbtracsPoint] = field(default_factory=list)

    @property
    def track_types(self) -> set[str]:
        return {p.track_type for p in self.points if p.track_type}

    @property
    def is_spur_only(self) -> bool:
        types = self.track_types
        return bool(types) and all(is_spur_type(t) for t in types)

    @property
    def is_provisional(self) -> bool:
        return any(is_provisional_type(t) for t in self.track_types)

    @property
    def peak_usa_wind(self) -> Optional[int]:
        winds = [p.usa_wind for p in self.points if p.usa_wind is not None]
        return max(winds) if winds else None

    @property
    def peak_usa_sshs(self) -> Optional[int]:
        vals = [p.usa_sshs for p in self.points if p.usa_sshs is not None]
        return max(vals) if vals else None

    @property
    def reached_hu_status(self) -> bool:
        return any(p.usa_status in {"HU", "HR"} for p in self.points)

    @property
    def reached_named_status(self) -> bool:
        return any(p.usa_status in {"TS", "SS", "HU", "HR"} for p in self.points)

    @property
    def reached_cat1_plus(self) -> bool:
        peak = self.peak_usa_sshs
        return peak is not None and peak >= 1

    @property
    def reached_major(self) -> bool:
        peak = self.peak_usa_sshs
        if peak is not None and peak >= 3:
            return True
        return is_major(self.peak_usa_wind)

    @property
    def n_landfall_zero(self) -> int:
        return sum(1 for p in self.points if p.landfall_flag_zero)

    @property
    def n_usa_record_L(self) -> int:
        return sum(1 for p in self.points if p.usa_record_L)

    def to_json(self) -> dict[str, Any]:
        return {
            "sid": self.sid,
            "season": self.season,
            "name": self.name,
            "basin": self.basin,
            "usa_atcf_id": self.usa_atcf_id,
            "n_points": len(self.points),
            "track_types": sorted(self.track_types),
            "is_spur_only": self.is_spur_only,
            "is_provisional": self.is_provisional,
            "reached_named_status": self.reached_named_status,
            "reached_hu_status": self.reached_hu_status,
            "reached_cat1_plus": self.reached_cat1_plus,
            "reached_major": self.reached_major,
            "peak_usa_wind": self.peak_usa_wind,
            "peak_usa_sshs": self.peak_usa_sshs,
            "peak_sshws_from_usa_wind": sshws_from_knots(self.peak_usa_wind),
            "n_landfall_zero": self.n_landfall_zero,
            "n_usa_record_L": self.n_usa_record_L,
        }


def parse_ibtracs_na(text: str) -> tuple[list[IbtracsStorm], list[str]]:
    """Parse the official NA CSV. Row 2 is units and is skipped."""
    gaps: list[str] = []
    reader = csv.reader(text.splitlines())
    try:
        header = next(reader)
        units = next(reader)  # noqa: F841 — published units row, not data
    except StopIteration:
        return [], ["IBTrACS CSV too short (missing header or units row)"]
    header = [h.strip() for h in header]
    missing_cols = [c for c in NEEDED_COLS if c not in header]
    if missing_cols:
        return [], [f"IBTrACS CSV missing columns: {missing_cols}"]
    by_sid: dict[str, IbtracsStorm] = {}
    for lineno, raw in enumerate(reader, start=3):
        if not raw or all(not c.strip() for c in raw):
            continue
        if len(raw) < len(header):
            raw = raw + [""] * (len(header) - len(raw))
        row = dict(zip(header, raw))
        sid = _cell(row, "SID")
        season_raw = _cell(row, "SEASON")
        if not sid or not season_raw:
            gaps.append(f"line {lineno}: empty SID or SEASON")
            continue
        season = _opt_int(season_raw)
        if season is None:
            gaps.append(f"line {lineno}: bad SEASON {season_raw!r}")
            continue
        storm = by_sid.get(sid)
        if storm is None:
            storm = IbtracsStorm(
                sid=sid,
                season=season,
                name=_cell(row, "NAME"),
                basin=_cell(row, "BASIN") or "NA",
                usa_atcf_id=_cell(row, "USA_ATCF_ID"),
            )
            by_sid[sid] = storm
        storm.points.append(IbtracsPoint(
            iso_time=_cell(row, "ISO_TIME"),
            nature=_cell(row, "NATURE"),
            track_type=_cell(row, "TRACK_TYPE"),
            landfall_km=_opt_float(_cell(row, "LANDFALL")),
            dist2land_km=_opt_float(_cell(row, "DIST2LAND")),
            usa_record=_cell(row, "USA_RECORD"),
            usa_status=_cell(row, "USA_STATUS"),
            usa_wind=_opt_int(_cell(row, "USA_WIND")),
            usa_sshs=_opt_int(_cell(row, "USA_SSHS")),
        ))
        if not storm.usa_atcf_id:
            storm.usa_atcf_id = _cell(row, "USA_ATCF_ID")
    storms = list(by_sid.values())
    return storms, gaps


class IbtracsClient:
    """Download the NA IBTrACS CSV. Nothing invented on a miss."""

    def __init__(self, cache_dir: Path = IBTRACS_CACHE, timeout: int = 180):
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def fetch_na(self, allow_network: bool = True) -> dict[str, Any]:
        path = self.cache_dir / IBTRACS_NA_FILENAME
        if path.exists():
            raw = path.read_bytes()
        elif allow_network:
            r = self.session.get(IBTRACS_NA_URL, timeout=self.timeout)
            r.raise_for_status()
            raw = r.content
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        else:
            raise FileNotFoundError(f"IBTrACS cache missing: {path}")
        text = raw.decode("utf-8", errors="replace")
        storms, gaps = parse_ibtracs_na(text)
        return {
            "url": IBTRACS_NA_URL,
            "filename": IBTRACS_NA_FILENAME,
            "version": IBTRACS_VERSION,
            "path": str(path),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "n_bytes": len(raw),
            "storms": storms,
            "gaps": gaps,
        }


def countable(storms: Iterable[IbtracsStorm]) -> list[IbtracsStorm]:
    """Drop spur-only tracks (NCEI: should not likely be counted)."""
    return [s for s in storms if not s.is_spur_only]


def coverage_table(storms: list[IbtracsStorm], gaps: list[str]) -> dict[str, Any]:
    kept = countable(storms)
    if not kept:
        return {
            "n_systems_in_file": len(storms),
            "n_systems_counted": 0,
            "n_spur_only_excluded": len(storms),
            "gaps": gaps,
        }
    years = [s.season for s in kept]
    first_year, last_year = min(years), max(years)
    have = set(years)
    missing = [y for y in range(first_year, last_year + 1) if y not in have]
    sshs_peak = {k: 0 for k in USA_SSHS_LABELS}
    n_sshs_missing = 0
    for s in kept:
        peak = s.peak_usa_sshs
        if peak is None or peak not in sshs_peak:
            n_sshs_missing += 1
        else:
            sshs_peak[peak] += 1
    by_type: dict[str, int] = {}
    for s in kept:
        key = ",".join(sorted(s.track_types)) or "(empty)"
        by_type[key] = by_type.get(key, 0) + 1
    n_provisional = sum(1 for s in kept if s.is_provisional)
    return {
        "basin_file": "NA",
        "version": IBTRACS_VERSION,
        "n_systems_in_file": len(storms),
        "n_systems_counted": len(kept),
        "n_spur_only_excluded": len(storms) - len(kept),
        "n_provisional_among_counted": n_provisional,
        "first_season": first_year,
        "last_season": last_year,
        "n_seasons_with_a_system": len(have),
        "n_seasons_span": last_year - first_year + 1,
        "missing_seasons_in_span": missing,
        "n_missing_seasons_in_span": len(missing),
        "n_named_usa_status": sum(1 for s in kept if s.reached_named_status),
        "n_hurricanes_usa_status": sum(1 for s in kept if s.reached_hu_status),
        "n_cat1_plus_usa_sshs": sum(1 for s in kept if s.reached_cat1_plus),
        "n_major_usa_sshs_or_wind": sum(1 for s in kept if s.reached_major),
        "n_with_landfall_zero": sum(1 for s in kept if s.n_landfall_zero),
        "n_landfall_zero_points": sum(s.n_landfall_zero for s in kept),
        "n_with_usa_record_L": sum(1 for s in kept if s.n_usa_record_L),
        "n_usa_record_L_points": sum(s.n_usa_record_L for s in kept),
        "n_peak_usa_sshs_missing": n_sshs_missing,
        "peak_usa_sshs_counts": {
            USA_SSHS_LABELS[k]: v for k, v in sorted(sshs_peak.items())
        },
        "track_type_counts": by_type,
        "parse_gaps": gaps,
        "n_parse_gaps": len(gaps),
        "landfall_note": (
            "LANDFALL=0 : le centre croise une terre du masque NCEI "
            "(continents et îles > 1400 km²) dans les 3 heures. "
            "USA_RECORD L : même drapeau que HURDAT2. "
            "Ce n'est pas seulement les États-Unis."
        ),
        "columns_pdf": IBTRACS_COLUMNS_PDF,
        "product_url": IBTRACS_PRODUCT,
        "major_min_kt": MAJOR_MIN_KT,
    }
