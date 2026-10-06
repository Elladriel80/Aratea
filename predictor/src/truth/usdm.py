"""US Drought Monitor weekly statistics (NDMC / USDA Climate Hubs).

FR : Vérité officielle pour la cible catalogue « Sécheresse US ».
On ne invente pas de classe. On ne redessine pas le Midwest ni le
Sud-Ouest : on lit les séries déjà nommées Midwest et Southwest dans
le service REST USDM (hubs USDA), plus le CONUS, plus les États que
les pages USDA des hubs listent.

EN : Official weekly USDM statistics. Catalogue names stay
« Sécheresse US » and « US Drought Monitor ». Region membership is
the USDA Climate Hub list published on the hub pages, not a homemade
map.

REST : https://usdmdataservices.unl.edu/api/
Doc  : https://droughtmonitor.unl.edu/DmData/DataDownload/WebServiceInfo.aspx
Classes published on every map : None, D0, D1, D2, D3, D4.
statisticsType=1 cumulative (D0 includes D1–D4). Type 2 categorical.
"""
from __future__ import annotations

import json
import re
import time
from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urlencode

import requests

from src.config import DATA_DIR, USER_AGENT

USDM_API = "https://usdmdataservices.unl.edu/api"
USDM_CACHE = DATA_DIR / "truth" / "usdm_cache"
USDM_OUT = DATA_DIR / "truth" / "usdm"

# First published USDM map (official archive).
USDM_ARCHIVE_START = date(2000, 1, 4)

# Classes as published. Do not add a homemade class.
CLASSES = ("none", "d0", "d1", "d2", "d3", "d4")
CLASS_LABELS_EN = {
    "none": "None",
    "d0": "D0 Abnormally Dry",
    "d1": "D1 Moderate Drought",
    "d2": "D2 Severe Drought",
    "d3": "D3 Extreme Drought",
    "d4": "D4 Exceptional Drought",
}
CUMULATIVE_KEYS = {
    "d0": ("d0", "d1", "d2", "d3", "d4"),
    "d1": ("d1", "d2", "d3", "d4"),
    "d2": ("d2", "d3", "d4"),
    "d3": ("d3", "d4"),
    "d4": ("d4",),
}

# USDM REST Climate Hub AOIs discovered 2026-09-12 (name field in JSON).
# 3 = "Midwest", 10 = "Southwest". Other hubs exist; we do not rename them.
CLIMATE_HUB_AOI = {"Midwest": 3, "Southwest": 10}

# Mainland states listed on the official USDA hub pages (fetched 2026-09-12).
# Midwest : https://www.climatehubs.usda.gov/hubs/midwest
# Southwest : https://www.climatehubs.usda.gov/hubs/southwest/about
# Hawaii and the Pacific Islands are in the Southwest Hub text; they are
# not added to the mainland state table. The hub time series is used as
# published, without subtracting anyone.
MIDWEST_STATES = {
    "IL": "17", "IN": "18", "IA": "19", "MI": "26",
    "MN": "27", "MO": "29", "OH": "39", "WI": "55",
}
SOUTHWEST_MAINLAND_STATES = {
    "AZ": "04", "CA": "06", "NV": "32", "NM": "35", "UT": "49",
}

# 30 % D2+ is already written in predictor/PHASE_B_SCAFFOLDING.md §3.2.
# Used only as a counting threshold, not as a priced product.
D2PLUS_AREA_THRESHOLD = 30.0

_SAFE_RE = re.compile(r"[^A-Za-z0-9._-]")

SEASON_MONTHS = {
    "DJF": (12, 1, 2),
    "MAM": (3, 4, 5),
    "JJA": (6, 7, 8),
    "SON": (9, 10, 11),
}


def parse_usdm_stamp(value: str) -> date:
    """'2024-01-02T00:00:00' or '2024-01-02' → date. No invented day."""
    if not value:
        raise ValueError("empty USDM stamp")
    return date.fromisoformat(value[:10])


def met_season(d: date) -> tuple[str, int]:
    """Meteorological season and its year (DJF year = January year)."""
    if d.month == 12:
        return "DJF", d.year + 1
    if d.month in (1, 2):
        return "DJF", d.year
    if d.month in (3, 4, 5):
        return "MAM", d.year
    if d.month in (6, 7, 8):
        return "JJA", d.year
    return "SON", d.year


def tuesdays_in_month(year: int, month: int) -> list[date]:
    last_day = monthrange(year, month)[1]
    out = []
    for day in range(1, last_day + 1):
        d = date(year, month, day)
        if d.weekday() == 1:
            out.append(d)
    return out


def month_is_complete(year: int, month: int, have: set[date]) -> bool:
    needed = tuesdays_in_month(year, month)
    return bool(needed) and all(d in have for d in needed)


def expected_weekly_tuesdays(first: date, last: date) -> list[date]:
    """USDM maps are weekly Tuesdays from the first published map."""
    if first.weekday() != 1:
        raise ValueError(f"USDM first map is not a Tuesday: {first}")
    out = []
    d = first
    while d <= last:
        out.append(d)
        d += timedelta(days=7)
    return out


@dataclass(frozen=True)
class UsdmWeek:
    """One published weekly row."""
    series: str
    map_date: date
    valid_start: date
    valid_end: date
    statistic_format: int          # 1 cumulative, 2 categorical
    values: dict[str, float]       # none, d0, d1, d2, d3, d4
    unit: str                      # "percent" | "area"
    name: Optional[str] = None

    def d2_plus(self) -> float:
        return self.values["d2"] + self.values["d3"] + self.values["d4"]

    def to_json(self) -> dict[str, Any]:
        row = {
            "series": self.series,
            "map_date": self.map_date.isoformat(),
            "valid_start": self.valid_start.isoformat(),
            "valid_end": self.valid_end.isoformat(),
            "statistic_format": self.statistic_format,
            "unit": self.unit,
            **{k: self.values[k] for k in CLASSES},
        }
        if self.name:
            row["name"] = self.name
        return row


def parse_week(raw: dict, series: str, unit: str) -> UsdmWeek:
    missing = [k for k in CLASSES if k not in raw or raw[k] is None]
    if missing:
        raise ValueError(f"USDM row missing classes {missing}: {raw}")
    values = {k: float(raw[k]) for k in CLASSES}
    return UsdmWeek(
        series=series,
        map_date=parse_usdm_stamp(raw["mapDate"]),
        valid_start=parse_usdm_stamp(raw["validStart"]),
        valid_end=parse_usdm_stamp(raw["validEnd"]),
        statistic_format=int(raw["statisticFormatID"]),
        values=values,
        unit=unit,
        name=raw.get("name") or raw.get("areaOfInterest") or raw.get("stateAbbreviation"),
    )


class UsdmClient:
    """Thin REST client with a disk cache. Nothing is invented on a miss."""

    def __init__(self, cache_dir: Path = USDM_CACHE, timeout: int = 90,
                 pause_s: float = 0.15):
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.pause_s = pause_s
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        })

    def _cache_path(self, key: str) -> Path:
        safe = _SAFE_RE.sub("_", key)
        return self.cache_dir / f"{safe}.json"

    def get_json(self, url: str, cache_key: str, allow_network: bool) -> list[dict]:
        path = self._cache_path(cache_key)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        if not allow_network:
            raise FileNotFoundError(f"USDM cache missing: {path}")
        time.sleep(self.pause_s)
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            raise ValueError(f"USDM expected a JSON list, got {type(data)}: {data!r}"[:300])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return data

    def fetch_percent(
        self,
        area: str,
        aoi: str,
        start: date,
        end: date,
        statistics_type: int,
        series: str,
        allow_network: bool = True,
    ) -> list[UsdmWeek]:
        q = urlencode({
            "aoi": aoi,
            "startdate": f"{start.month}/{start.day}/{start.year}",
            "enddate": f"{end.month}/{end.day}/{end.year}",
            "statisticsType": statistics_type,
        })
        url = f"{USDM_API}/{area}/GetDroughtSeverityStatisticsByAreaPercent?{q}"
        key = f"{area}_{aoi}_pct_t{statistics_type}_{start.isoformat()}_{end.isoformat()}"
        raw = self.get_json(url, key, allow_network)
        weeks = [parse_week(row, series, "percent") for row in raw]
        return sorted(weeks, key=lambda w: w.map_date)

    def fetch_area(
        self,
        area: str,
        aoi: str,
        start: date,
        end: date,
        statistics_type: int,
        series: str,
        allow_network: bool = True,
    ) -> list[UsdmWeek]:
        q = urlencode({
            "aoi": aoi,
            "startdate": f"{start.month}/{start.day}/{start.year}",
            "enddate": f"{end.month}/{end.day}/{end.year}",
            "statisticsType": statistics_type,
        })
        url = f"{USDM_API}/{area}/GetDroughtSeverityStatisticsByArea?{q}"
        key = f"{area}_{aoi}_area_t{statistics_type}_{start.isoformat()}_{end.isoformat()}"
        raw = self.get_json(url, key, allow_network)
        weeks = [parse_week(row, series, "area") for row in raw]
        return sorted(weeks, key=lambda w: w.map_date)


def combine_area_weeks(parts: Iterable[list[UsdmWeek]], series: str) -> list[UsdmWeek]:
    """Sum published areas that share a map date. Percents are rebuilt."""
    by_date: dict[date, list[UsdmWeek]] = {}
    for weeks in parts:
        for w in weeks:
            if w.unit != "area":
                raise ValueError("combine_area_weeks needs area rows, not percent")
            by_date.setdefault(w.map_date, []).append(w)
    out: list[UsdmWeek] = []
    for d, rows in sorted(by_date.items()):
        fmt = {r.statistic_format for r in rows}
        if len(fmt) != 1:
            raise ValueError(f"mixed statistic formats on {d}")
        totals = {k: sum(r.values[k] for r in rows) for k in CLASSES}
        land = sum(totals.values())
        if land <= 0:
            raise ValueError(f"zero land area on {d}")
        percents = {k: 100.0 * totals[k] / land for k in CLASSES}
        out.append(UsdmWeek(
            series=series,
            map_date=d,
            valid_start=rows[0].valid_start,
            valid_end=rows[0].valid_end,
            statistic_format=rows[0].statistic_format,
            values=percents,
            unit="percent",
            name=series,
        ))
    return out


def coverage_table(weeks: list[UsdmWeek]) -> dict[str, Any]:
    """Measured week / season / class counts. Empty input stays empty."""
    if not weeks:
        return {"n_weeks": 0}
    units = {w.unit for w in weeks}
    fmts = {w.statistic_format for w in weeks}
    if len(units) != 1 or len(fmts) != 1:
        raise ValueError("coverage_table needs one unit and one statistic format")
    first = weeks[0].map_date
    last = weeks[-1].map_date
    expected = expected_weekly_tuesdays(first, last)
    have = {w.map_date for w in weeks}
    missing = [d.isoformat() for d in expected if d not in have]
    by_season: dict[str, list[UsdmWeek]] = {}
    by_year: dict[int, list[UsdmWeek]] = {}
    for w in weeks:
        season, sy = met_season(w.map_date)
        by_season.setdefault(f"{season}-{sy}", []).append(w)
        by_year.setdefault(w.map_date.year, []).append(w)

    class_weeks = {}
    for k in CLASSES:
        n = sum(1 for w in weeks if w.values[k] > 0)
        class_weeks[k] = {
            "label": CLASS_LABELS_EN[k],
            "weeks_with_area": n,
            "share_of_weeks": n / len(weeks),
            "mean_value": sum(w.values[k] for w in weeks) / len(weeks),
            "max_value": max(w.values[k] for w in weeks),
        }

    d2p = [w.d2_plus() for w in weeks]
    seasons_complete = [k for k, rows in by_season.items() if len(rows) >= 12]
    years_complete = [y for y, rows in by_year.items() if len(rows) >= 52]

    season_type_counts = {"DJF": 0, "MAM": 0, "JJA": 0, "SON": 0}
    for key in seasons_complete:
        season_type_counts[key[:3]] += 1

    return {
        "series": weeks[0].series,
        "published_name": weeks[0].name,
        "unit": weeks[0].unit,
        "statistic_format": weeks[0].statistic_format,
        "n_weeks": len(weeks),
        "first_map": first.isoformat(),
        "last_map": last.isoformat(),
        "expected_weeks": len(expected),
        "missing_weeks": len(missing),
        "missing_map_dates": missing,
        "n_calendar_years_with_a_map": len(by_year),
        "n_calendar_years_52_plus_weeks": len(years_complete),
        "n_seasons_with_a_map": len(by_season),
        "n_seasons_12_plus_weeks": len(seasons_complete),
        "complete_seasons_by_type": season_type_counts,
        "classes": class_weeks,
        "d2_plus": {
            "mean": sum(d2p) / len(d2p),
            "max": max(d2p),
            "weeks_gt_0": sum(1 for x in d2p if x > 0),
            "weeks_ge_30": sum(1 for x in d2p if x >= D2PLUS_AREA_THRESHOLD),
            "threshold_30_source": "PHASE_B_SCAFFOLDING.md §3.2 (count only)",
        },
    }


def season_means(weeks: list[UsdmWeek]) -> list[dict[str, Any]]:
    """One row per meteorological season: mean categorical / area values."""
    buckets: dict[tuple[str, int], list[UsdmWeek]] = {}
    for w in weeks:
        buckets.setdefault(met_season(w.map_date), []).append(w)
    rows = []
    for (season, year), group in sorted(buckets.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        n = len(group)
        means = {k: sum(w.values[k] for w in group) / n for k in CLASSES}
        d2p = means["d2"] + means["d3"] + means["d4"]
        rows.append({
            "season": season,
            "year": year,
            "n_weeks": n,
            "complete": n >= 12,
            "first_map": group[0].map_date.isoformat(),
            "last_map": group[-1].map_date.isoformat(),
            **means,
            "d2_plus": d2p,
            "event_d2_plus_gt_0": d2p > 0,
            "event_d2_plus_ge_30": d2p >= D2PLUS_AREA_THRESHOLD,
        })
    return rows


def brier_score(p: float, outcome: bool) -> float:
    return (p - (1.0 if outcome else 0.0)) ** 2


def brier_skill_score(bs_forecast: float, bs_climato: float) -> Optional[float]:
    """BSS = 1 - BS_fc / BS_clim. None when climato BS is 0 (do not invent)."""
    if bs_climato == 0:
        return None
    return 1.0 - bs_forecast / bs_climato


def leave_one_out_climato(events: list[bool]) -> list[float]:
    """Climatology = frequency of the other seasons. Needs ≥ 2 rows."""
    n = len(events)
    if n < 2:
        return []
    total = sum(1.0 if e else 0.0 for e in events)
    return [(total - (1.0 if e else 0.0)) / (n - 1) for e in events]
