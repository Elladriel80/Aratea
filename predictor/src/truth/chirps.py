"""CHIRPS v2 monthly rainfall (catalogue name « CHIRPS pluie »).

FR : Vérité catalogue « CHIRPS pluie ». On ne invente pas de case, pas
de seuil, pas de BSS. Sans grille ouverte, on ne compte pas les
cellules. Les régions sont celles du catalogue Phase 2 (Méditerranée
IPCC MED, Inde Maharashtra + Karnataka, comme SPEI PR 243).

EN : Catalogue name stays « CHIRPS pluie ». Cell counts come only from
an opened CHIRPS grid. A missing file is a blocker, not an inventory.

Preferred product : CHIRPS v2.0 global monthly, UCSB Climate Hazards,
0.05°, mm/month, land 50S-50N. Official tree :
https://data.chc.ucsb.edu/products/CHIRPS-2.0/
Monthly GeoTIFF index :
https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/
Yearly NetCDF :
https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/byYear/
Subset counted here : IRI Data Library of the same UCSB series
(public, no account) :
https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.monthly/.global/.precipitation/
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import numpy as np
import requests

from src.config import DATA_DIR, USER_AGENT

CATALOGUE_TRUTH = "CHIRPS pluie"
TARGET_MED = "Sécheresse Méditerranée"
TARGET_INDE = "Sécheresse Inde"

CHIRPS_CACHE = DATA_DIR / "truth" / "chirps_cache"
CHIRPS_OUT = DATA_DIR / "truth" / "chirps"

CHIRPS_HOME = "https://www.chc.ucsb.edu/data/chirps"
CHIRPS_V3_NOTE = "https://www.chc.ucsb.edu/data/chirps3"
CHIRPS_README = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/README-CHIRPS.txt"
CHIRPS_FAQ = "https://wiki.chc.ucsb.edu/CHIRPS_FAQ"
CHIRPS_DATA_ROOT = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/"
CHIRPS_TIFS = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/"
CHIRPS_NETCDF = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/"
CHIRPS_BYYEAR = (
    "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/byYear/"
)
CHIRPS_MONTHLY_NC = (
    "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/"
    "chirps-v2.0.monthly.nc"
)
CHIRPS_EWX = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly_EWX/"
CHIRPS_PRELIM_TIFS = (
    "https://data.chc.ucsb.edu/products/CHIRPS-2.0/prelim/global_monthly/tifs/"
)
IRI_PRECIP = (
    "https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/"
    ".monthly/.global/.precipitation/"
)
GEE_STAC_PENTAD = (
    "https://storage.googleapis.com/earthengine-stac/catalog/"
    "UCSB-CHG/UCSB-CHG_CHIRPS_PENTAD.json"
)
GEE_HTML_PENTAD = (
    "https://developers.google.com/earth-engine/datasets/catalog/"
    "UCSB-CHG_CHIRPS_PENTAD"
)
FUNK_2015 = "https://doi.org/10.1038/sdata.2015.66"
USGS_DS832 = "https://doi.org/10.3133/ds832"

# IPCC AR6 WGI MED (Iturbide et al. 2020). Same published CSV as SPEI PR 243.
IPCC_REGIONS_CSV = (
    "https://raw.githubusercontent.com/IPCC-WG1/Atlas/main/"
    "reference-regions/IPCC-WGI-reference-regions-v4_coordinates.csv"
)
IPCC_MED_VERTICES: tuple[tuple[float, float], ...] = (
    (-10.0, 30.0),
    (-10.0, 45.0),
    (40.0, 45.0),
    (40.0, 30.0),
)
NE_ADMIN1_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_50m_admin_1_states_provinces.geojson"
)
INDE_NE_NAMES = ("Maharashtra", "Karnataka")

# Published in the CHIRPS FAQ / ERDDAP copy of the same files. Not invented.
FAQ_RESOLUTION_DEG = 0.05
FAQ_LAT_MIN, FAQ_LAT_MAX = -50.0, 50.0
FAQ_FILL = -9999.0
FAQ_UNITS = "mm/month"
FAQ_GRID_NX, FAQ_GRID_NY = 7200, 2000

# No drought class is published in the monthly rainfall file docs.
# EWX has separate anomaly / zscore folders; those are not this product.
PUBLISHED_DROUGHT_THRESHOLDS: tuple[()] = ()

MONTH_ABBR = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)

PROBE_URLS = (
    CHIRPS_HOME,
    CHIRPS_README,
    CHIRPS_FAQ,
    CHIRPS_DATA_ROOT,
    CHIRPS_TIFS,
    CHIRPS_NETCDF,
    CHIRPS_BYYEAR,
    CHIRPS_MONTHLY_NC,
    CHIRPS_EWX,
    CHIRPS_PRELIM_TIFS,
    IRI_PRECIP,
    GEE_STAC_PENTAD,
    IPCC_REGIONS_CSV,
    NE_ADMIN1_URL,
    CHIRPS_V3_NOTE,
)


def iri_time_to_date(value: float) -> date:
    """IRI T is 'months since 1960-01-01' (mid-month, e.g. 252.5 = Jan 1981).

    Calendar attribute on the file says 360. Dates are recovered from the
    integer month count, not from a 360-day calendar.
    """
    months = int(np.floor(float(value)))
    year = 1960 + months // 12
    month = months % 12 + 1
    return date(year, month, 1)


def month_label(year: int, month: int) -> str:
    return f"{MONTH_ABBR[month - 1]} {year}"


def point_in_ring(lon: float, lat: float, ring: list[tuple[float, float]]) -> bool:
    """Even-odd rule. Vertices are (lon, lat) as published. No buffer."""
    if len(ring) < 3:
        return False
    inside = False
    x, y = lon, lat
    pts = ring
    if pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        intersect = ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / (y2 - y1 + 0.0) + x1
        )
        if intersect:
            inside = not inside
    return inside


def parse_ipcc_med_vertices(csv_text: str) -> list[tuple[float, float]]:
    """Read the published MED vertices. Missing MED is a gap, not invented."""
    for raw in csv_text.splitlines():
        parts = [p.strip() for p in raw.split(",")]
        if len(parts) < 5 or parts[3] != "MED":
            continue
        verts: list[tuple[float, float]] = []
        for token in parts[4:]:
            if not token or "|" not in token:
                continue
            lon_s, lat_s = token.split("|", 1)
            verts.append((float(lon_s), float(lat_s)))
        return verts
    raise ValueError("IPCC CSV has no MED row")


def _feature_name(props: dict[str, Any]) -> str:
    for key in ("name_en", "name", "gn_name", "woe_name"):
        value = props.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _feature_admin(props: dict[str, Any]) -> str:
    for key in ("admin", "adm0_a3", "gu_a3"):
        value = props.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _rings_from_geom(geom: dict[str, Any]) -> list[list[tuple[float, float]]]:
    gtype = geom.get("type")
    coords = geom.get("coordinates") or []
    rings: list[list[tuple[float, float]]] = []
    if gtype == "Polygon":
        if coords:
            rings.append([(float(x), float(y)) for x, y, *_ in coords[0]])
    elif gtype == "MultiPolygon":
        for poly in coords:
            if poly:
                rings.append([(float(x), float(y)) for x, y, *_ in poly[0]])
    return rings


def extract_named_states(
    geojson: dict[str, Any],
    names: tuple[str, ...],
    admin_contains: tuple[str, ...],
) -> dict[str, Any]:
    """Keep published Natural Earth polygons whose name matches exactly."""
    wanted = {n.casefold(): n for n in names}
    found: dict[str, list[list[tuple[float, float]]]] = {n: [] for n in names}
    extras: list[str] = []
    for feat in geojson.get("features") or []:
        props = feat.get("properties") or {}
        name = _feature_name(props)
        admin = _feature_admin(props)
        if name.casefold() not in wanted:
            continue
        if admin_contains and not any(
            tok.casefold() in admin.casefold() for tok in admin_contains
        ):
            extras.append(f"{name} admin={admin!r}")
            continue
        rings = _rings_from_geom(feat.get("geometry") or {})
        if rings:
            found[wanted[name.casefold()]].extend(rings)
    missing = [n for n in names if not found[n]]
    return {
        "names": list(names),
        "rings_by_name": found,
        "n_rings": sum(len(v) for v in found.values()),
        "missing_names": missing,
        "skipped_wrong_admin": extras,
        "source": NE_ADMIN1_URL,
    }


def _ring_bbox(ring: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return min(xs), max(xs), min(ys), max(ys)


def lon_in_180(lon: float) -> float:
    if lon > 180.0:
        return lon - 360.0
    return lon


def mask_from_rings(
    lats: np.ndarray,
    lons: np.ndarray,
    rings: list[list[tuple[float, float]]],
) -> np.ndarray:
    """True when the cell centre sits inside a published ring."""
    mask = np.zeros((lats.size, lons.size), dtype=bool)
    if not rings:
        return mask
    boxes = [_ring_bbox(ring) for ring in rings]
    lon180 = np.array([lon_in_180(float(x)) for x in lons], dtype=float)
    for i, lat in enumerate(lats):
        y = float(lat)
        for j, x in enumerate(lon180):
            for ring, (x0, x1, y0, y1) in zip(rings, boxes):
                if x < x0 or x > x1 or y < y0 or y > y1:
                    continue
                if point_in_ring(x, y, ring):
                    mask[i, j] = True
                    break
    return mask


def rings_bbox(
    rings: list[list[tuple[float, float]]], pad_deg: float = 0.1
) -> Optional[tuple[float, float, float, float]]:
    """Download window around published rings. Pad is not a new polygon."""
    if not rings:
        return None
    xs: list[float] = []
    ys: list[float] = []
    for ring in rings:
        xs.extend(p[0] for p in ring)
        ys.extend(p[1] for p in ring)
    return (
        min(xs) - pad_deg,
        max(xs) + pad_deg,
        min(ys) - pad_deg,
        max(ys) + pad_deg,
    )


def parse_ucsb_tif_index(html: str) -> dict[str, Any]:
    """Read published final monthly GeoTIFF names. No guessed months."""
    found = re.findall(r"chirps-v2\.0\.(\d{4})\.(\d{2})\.tif\.gz", html)
    months = sorted({(int(y), int(m)) for y, m in found})
    missing: list[str] = []
    if months:
        first = date(months[0][0], months[0][1], 1)
        last = date(months[-1][0], months[-1][1], 1)
        cur = first
        have = set(months)
        while cur <= last:
            key = (cur.year, cur.month)
            if key not in have:
                missing.append(f"{cur.year:04d}-{cur.month:02d}")
            if cur.month == 12:
                cur = date(cur.year + 1, 1, 1)
            else:
                cur = date(cur.year, cur.month + 1, 1)
    return {
        "source": CHIRPS_TIFS,
        "n_files": len(months),
        "first_month": f"{months[0][0]:04d}-{months[0][1]:02d}" if months else None,
        "last_month": f"{months[-1][0]:04d}-{months[-1][1]:02d}" if months else None,
        "months": [f"{y:04d}-{m:02d}" for y, m in months],
        "missing_months_in_span": missing,
        "n_missing_months_in_span": len(missing),
        "years": sorted({y for y, _ in months}),
        "product": "final monthly GeoTIFF (chirps-v2.0.YYYY.MM.tif.gz)",
    }


def parse_ucsb_year_index(html: str) -> dict[str, Any]:
    """Read published yearly monthly NetCDF names."""
    found = re.findall(r"chirps-v2\.0\.(\d{4})\.monthly\.nc", html)
    years = sorted({int(y) for y in found})
    missing: list[int] = []
    if years:
        missing = [y for y in range(years[0], years[-1] + 1) if y not in years]
    return {
        "source": CHIRPS_BYYEAR,
        "n_files": len(years),
        "first_year": years[0] if years else None,
        "last_year": years[-1] if years else None,
        "years": years,
        "missing_years_in_span": missing,
        "n_missing_years_in_span": len(missing),
        "product": "yearly monthly NetCDF (chirps-v2.0.YYYY.monthly.nc)",
    }


def parse_prelim_tif_index(html: str) -> dict[str, Any]:
    found = re.findall(r"chirps-v2\.0\.(\d{4})\.(\d{2})\.tif", html)
    months = sorted({(int(y), int(m)) for y, m in found})
    return {
        "source": CHIRPS_PRELIM_TIFS,
        "n_files": len(months),
        "first_month": f"{months[0][0]:04d}-{months[0][1]:02d}" if months else None,
        "last_month": f"{months[-1][0]:04d}-{months[-1][1]:02d}" if months else None,
        "product": "preliminary monthly GeoTIFF (not the counted final series)",
    }


@dataclass
class ChirpsSlab:
    """One opened CHIRPS cube (time, lat, lon). NaN = missing, never filled."""

    lats: np.ndarray
    lons: np.ndarray
    times: list[date]
    values: np.ndarray
    source: dict[str, Any] = field(default_factory=dict)
    units: str = FAQ_UNITS
    fill_value: float = FAQ_FILL

    @property
    def n_times(self) -> int:
        return len(self.times)


@dataclass
class RegionAccumulator:
    """Running cell counts. Empty stays empty. NaN is never replaced."""

    label: str
    mask: np.ndarray
    ever_valid: np.ndarray
    n_finite_cell_months: int = 0
    n_zero_cell_months: int = 0
    months_any: list[str] = field(default_factory=list)
    months_none: list[str] = field(default_factory=list)
    months_all: list[str] = field(default_factory=list)

    @classmethod
    def start(cls, label: str, mask: np.ndarray) -> "RegionAccumulator":
        return cls(
            label=label,
            mask=mask,
            ever_valid=np.zeros(mask.shape, dtype=bool),
        )

    def add(self, slab: np.ndarray, month: date) -> None:
        if slab.shape != self.mask.shape:
            raise ValueError(
                f"{self.label}: slab {slab.shape} != mask {self.mask.shape}"
            )
        cut = slab[self.mask]
        finite = np.isfinite(cut)
        iso = f"{month.year:04d}-{month.month:02d}"
        if finite.any():
            self.months_any.append(iso)
        else:
            self.months_none.append(iso)
        if finite.size and bool(np.all(finite)):
            self.months_all.append(iso)
        self.n_finite_cell_months += int(finite.sum())
        if finite.any():
            self.n_zero_cell_months += int(np.sum(finite & (cut == 0.0)))
        ever = self.ever_valid[self.mask]
        ever |= finite
        self.ever_valid[self.mask] = ever

    def finish(self) -> dict[str, Any]:
        n_mask = int(self.mask.sum())
        if n_mask == 0:
            return {
                "region": self.label,
                "n_cells_in_published_cut": 0,
                "usable_measured": False,
                "note": "Aucune cellule dans le découpage publié, ou aucune date.",
            }
        months = sorted(set(self.months_any) | set(self.months_none))
        years = sorted({int(m[:4]) for m in months}) if months else []
        years_with = sorted({int(m[:4]) for m in self.months_any})
        missing_years = (
            [y for y in range(years[0], years[-1] + 1) if y not in years_with]
            if years
            else []
        )
        return {
            "region": self.label,
            "n_cells_in_published_cut": n_mask,
            "n_cells_usable_any_month": int(self.ever_valid.sum()),
            "n_cells_never_valid": n_mask - int(self.ever_valid.sum()),
            "n_times": len(months),
            "first_month": months[0] if months else None,
            "last_month": months[-1] if months else None,
            "first_month_with_a_value": self.months_any[0] if self.months_any else None,
            "last_month_with_a_value": self.months_any[-1] if self.months_any else None,
            "n_months_with_any_valid": len(self.months_any),
            "n_months_without_any_valid": len(self.months_none),
            "n_months_all_cells_valid": len(self.months_all),
            "n_calendar_years_in_opened_files": len(years),
            "n_calendar_years_with_a_value": len(years_with),
            "missing_years_in_span": missing_years,
            "n_missing_years_in_span": len(missing_years),
            "n_finite_cell_months": self.n_finite_cell_months,
            "n_zero_rain_cell_months": self.n_zero_cell_months,
            "usable_measured": True,
            "units": FAQ_UNITS,
            "fill_value": FAQ_FILL,
            "thresholds": {
                "drought_classes_in_monthly_file_docs": list(
                    PUBLISHED_DROUGHT_THRESHOLDS
                ),
                "note": (
                    "Le fichier mensuel CHIRPS est en mm/mois. "
                    "Aucun seuil de sécheresse n'est publié dans le README, "
                    "la FAQ, ou l'en-tête. Les dossiers EWX anomaly/zscore "
                    "existent à part ; on ne les a pas transformés en classes."
                ),
            },
        }


def empty_region_row(label: str, reason: str) -> dict[str, Any]:
    """Honest empty inventory. Counts stay absent, not zero-as-if-measured."""
    return {
        "region": label,
        "usable_measured": False,
        "n_cells_usable_any_month": None,
        "n_cells_in_published_cut": None,
        "missing_years_in_span": None,
        "n_missing_years_in_span": None,
        "n_finite_cell_months": None,
        "reason": reason,
    }


def coverage_for_mask(slab: ChirpsSlab, mask: np.ndarray, label: str) -> dict[str, Any]:
    """One-shot coverage (tests). Same rules as the streaming accumulator."""
    acc = RegionAccumulator.start(label, mask)
    if slab.n_times == 0 or int(mask.sum()) == 0:
        return acc.finish() if int(mask.sum()) == 0 else empty_region_row(
            label, "Aucune date dans la dalle."
        )
    for i, t in enumerate(slab.times):
        acc.add(slab.values[i], t)
    return acc.finish()


def regions_from_sources(
    ipcc_csv: Optional[str],
    ne_geojson: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """Build published cuts. Missing source = missing rings, not invented."""
    med_verts = list(IPCC_MED_VERTICES)
    med_from_csv = False
    if ipcc_csv:
        try:
            med_verts = parse_ipcc_med_vertices(ipcc_csv)
            med_from_csv = True
        except ValueError:
            med_from_csv = False
    inde = extract_named_states(ne_geojson or {}, INDE_NE_NAMES, ("India",))
    inde_rings: list[list[tuple[float, float]]] = []
    for name in INDE_NE_NAMES:
        inde_rings.extend(inde["rings_by_name"].get(name, []))
    return {
        TARGET_MED: {
            "cut": "IPCC AR6 WGI MED (Iturbide 2020)",
            "catalogue_target": TARGET_MED,
            "vertices": med_verts,
            "rings": [med_verts],
            "vertices_from_live_csv": med_from_csv,
            "source": IPCC_REGIONS_CSV,
            "surface": "Land-Ocean (libellé publié)",
        },
        TARGET_INDE: {
            "cut": "Maharashtra + Karnataka (catalogue Phase 2, comme SPEI PR 243)",
            "catalogue_target": TARGET_INDE,
            "states": inde,
            "rings": inde_rings,
            "source_polygons": NE_ADMIN1_URL,
        },
    }


def count_regions(slab: ChirpsSlab, regions: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for label, spec in regions.items():
        rings = spec.get("rings") or []
        if not rings:
            out[label] = empty_region_row(
                label,
                "Découpage publié sans polygone lisible. Pas de compte inventé.",
            )
            continue
        mask = mask_from_rings(slab.lats, slab.lons, rings)
        out[label] = coverage_for_mask(slab, mask, label)
    return out


def _clean_precip(arr: np.ndarray, fill: float = FAQ_FILL) -> np.ndarray:
    out = np.asarray(arr, dtype=np.float32)
    out = np.where(out == np.float32(fill), np.nan, out)
    out = np.where(np.abs(out) >= 1.0e20, np.nan, out)
    return out


def read_iri_netcdf(path: Path) -> ChirpsSlab:
    """Read an IRI CHIRPS subset. Missing values stay missing."""
    try:
        import netCDF4  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "netCDF4 is required to read a CHIRPS .nc file. "
            "The inventory does not invent cells without the reader."
        ) from exc
    ds = netCDF4.Dataset(str(path))
    try:
        lat_name = next(n for n in ("Y", "lat", "latitude") if n in ds.variables)
        lon_name = next(n for n in ("X", "lon", "longitude") if n in ds.variables)
        time_name = next(n for n in ("T", "time") if n in ds.variables)
        var_name = next(
            n for n in ("precipitation", "precip", "pr") if n in ds.variables
        )
        lats = np.asarray(ds.variables[lat_name][:], dtype=float)
        lons = np.asarray(ds.variables[lon_name][:], dtype=float)
        tvar = ds.variables[time_name]
        raw_t = np.asarray(tvar[:], dtype=float)
        times: list[date] = []
        gaps: list[str] = []
        for i, t in enumerate(raw_t):
            try:
                times.append(iri_time_to_date(float(t)))
            except Exception:
                gaps.append(f"time[{i}] unreadable")
        arr = _clean_precip(
            ds.variables[var_name][:],
            fill=float(getattr(ds.variables[var_name], "missing_value", FAQ_FILL)),
        )
        if arr.ndim != 3:
            raise ValueError(f"{var_name} is not 3-D: {arr.shape}")
        units = str(getattr(ds.variables[var_name], "units", FAQ_UNITS))
        return ChirpsSlab(
            lats=lats,
            lons=lons,
            times=times,
            values=arr,
            units=units,
            fill_value=FAQ_FILL,
            source={
                "path": str(path),
                "filename": path.name,
                "variable": var_name,
                "n_bytes": path.stat().st_size,
                "time_gaps": gaps,
                "time_units": str(getattr(tvar, "units", "")),
                "time_calendar": str(getattr(tvar, "calendar", "")),
            },
        )
    finally:
        ds.close()


def read_ucsb_year_netcdf(
    path: Path,
    lat0: float,
    lat1: float,
    lon0: float,
    lon1: float,
) -> ChirpsSlab:
    """Read a published UCSB yearly monthly NetCDF, bbox only."""
    try:
        import netCDF4  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "netCDF4 is required to read a CHIRPS .nc file. "
            "The inventory does not invent cells without the reader."
        ) from exc
    ds = netCDF4.Dataset(str(path))
    try:
        lat_name = next(n for n in ("latitude", "lat", "Y") if n in ds.variables)
        lon_name = next(n for n in ("longitude", "lon", "X") if n in ds.variables)
        time_name = next(n for n in ("time", "T") if n in ds.variables)
        var_name = next(
            n for n in ("precip", "precipitation", "pr") if n in ds.variables
        )
        lats_all = np.asarray(ds.variables[lat_name][:], dtype=float)
        lons_all = np.asarray(ds.variables[lon_name][:], dtype=float)
        i = np.where((lats_all >= min(lat0, lat1)) & (lats_all <= max(lat0, lat1)))[0]
        j = np.where((lons_all >= min(lon0, lon1)) & (lons_all <= max(lon0, lon1)))[0]
        if i.size == 0 or j.size == 0:
            raise ValueError(f"{path.name}: bbox empty on this grid")
        i0, i1 = int(i.min()), int(i.max()) + 1
        j0, j1 = int(j.min()), int(j.max()) + 1
        lats = lats_all[i0:i1]
        lons = lons_all[j0:j1]
        tvar = ds.variables[time_name]
        try:
            raw = netCDF4.num2date(
                tvar[:], tvar.units, getattr(tvar, "calendar", "standard")
            )
            times = [
                date(int(t.year), int(t.month), 1) for t in raw
            ]
        except Exception:
            times = [iri_time_to_date(float(t)) for t in np.asarray(tvar[:])]
        arr = _clean_precip(
            ds.variables[var_name][:, i0:i1, j0:j1],
            fill=float(getattr(ds.variables[var_name], "_FillValue", FAQ_FILL)),
        )
        return ChirpsSlab(
            lats=lats,
            lons=lons,
            times=times,
            values=arr,
            units=str(getattr(ds.variables[var_name], "units", FAQ_UNITS)),
            fill_value=FAQ_FILL,
            source={
                "path": str(path),
                "filename": path.name,
                "variable": var_name,
                "n_bytes": path.stat().st_size,
                "title": str(getattr(ds, "title", "") or ""),
                "version": str(getattr(ds, "version", "") or ""),
            },
        )
    finally:
        ds.close()


class ChirpsClient:
    """Probe public CHIRPS URLs. Download pixels only when the file is real."""

    def __init__(self, cache_dir: Path = CHIRPS_CACHE, timeout: int = 30):
        self.cache_dir = cache_dir
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT, "Accept": "*/*"})

    def probe(self, url: str) -> dict[str, Any]:
        started = time.time()
        row: dict[str, Any] = {
            "url": url,
            "host": urlparse(url).netloc,
            "ok": False,
            "http_status": None,
            "content_type": None,
            "n_bytes": None,
            "elapsed_s": None,
            "note": "",
        }
        try:
            r = self.session.get(
                url, timeout=self.timeout, stream=True, allow_redirects=True
            )
            chunk = next(r.iter_content(8192), b"")
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
            clen = r.headers.get("Content-Length")
            if url.endswith(".nc") and clen and int(clen) > 1_000_000:
                row["n_bytes"] = int(clen)
                extra = b""
            else:
                extra = b"".join(r.iter_content(64_000))
                chunk = chunk + extra
                row["n_bytes"] = len(chunk)
            row["http_status"] = r.status_code
            row["content_type"] = ctype or None
            row["final_url"] = str(r.url)
            text_head = chunk[:800].decode("utf-8", errors="replace")
            if "dlauth" in text_head.lower() or "login" in text_head.lower() and "IRI" in text_head:
                row["note"] = "page IRI (pas les pixels)"
            elif r.status_code == 200 and (
                "netcdf" in ctype
                or url.endswith(".nc")
                or chunk.startswith(b"CDF")
                or chunk.startswith(b"\x89HDF")
            ):
                row["ok"] = True
                row["note"] = "NetCDF / HDF (en-tête, fichier non entièrement lu ici)"
            elif r.status_code == 200 and (
                "text/" in ctype
                or "json" in ctype
                or url.endswith(".csv")
                or url.endswith(".txt")
                or url.endswith("/")
            ):
                row["ok"] = True
                row["note"] = "réponse lue"
            else:
                row["note"] = f"HTTP {r.status_code}"
        except requests.Timeout:
            row["note"] = f"timeout {self.timeout}s, 0 octet"
        except requests.RequestException as exc:
            row["note"] = f"erreur réseau : {type(exc).__name__}"
        row["elapsed_s"] = round(time.time() - started, 3)
        return row

    def probe_all(self, urls: tuple[str, ...] = PROBE_URLS) -> list[dict[str, Any]]:
        return [self.probe(u) for u in urls]

    def fetch_text(self, url: str) -> str:
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.text

    def fetch_json(self, url: str) -> dict[str, Any]:
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict):
            raise ValueError(f"JSON object expected from {url}")
        return data

    def iri_url(
        self,
        lon0: float,
        lon1: float,
        lat0: float,
        lat1: float,
        t0: str,
        t1: str,
    ) -> str:
        return (
            f"{IRI_PRECIP}X/{lon0}/{lon1}/RANGE/Y/{lat0}/{lat1}/RANGE/"
            f"T/%28{t0}%29/%28{t1}%29/RANGE/data.nc"
        )

    def download_iri_year(
        self,
        key: str,
        lon0: float,
        lon1: float,
        lat0: float,
        lat1: float,
        year: int,
        last_month: int = 12,
    ) -> Path:
        """Stream one calendar year. Partial files are deleted, not invented."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        dest = self.cache_dir / f"iri_{key}_{year}.nc"
        if dest.exists() and dest.stat().st_size > 500:
            return dest
        url = self.iri_url(
            lon0, lon1, lat0, lat1,
            month_label(year, 1),
            month_label(year, last_month),
        )
        tmp = dest.with_suffix(".nc.part")
        with self.session.get(url, timeout=180, stream=True) as r:
            r.raise_for_status()
            first = next(r.iter_content(4096), b"")
            if first.lstrip().startswith(b"<") or first.startswith(b"Error"):
                raise ValueError(f"IRI returned text, not NetCDF: {url}")
            if not (first.startswith(b"CDF") or first.startswith(b"\x89HDF")):
                raise ValueError(f"IRI magic is not NetCDF: {url}")
            n = 0
            with tmp.open("wb") as fh:
                fh.write(first)
                n += len(first)
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        fh.write(chunk)
                        n += len(chunk)
        if n < 200:
            tmp.unlink(missing_ok=True)
            raise ValueError(f"IRI download too small ({n} bytes): {url}")
        tmp.replace(dest)
        return dest

    def download_ucsb_year(self, year: int) -> Path:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        dest = self.cache_dir / f"ucsb_{year}.monthly.nc"
        if dest.exists() and dest.stat().st_size > 1000:
            return dest
        url = f"{CHIRPS_BYYEAR}chirps-v2.0.{year}.monthly.nc"
        tmp = dest.with_suffix(".nc.part")
        with self.session.get(url, timeout=180, stream=True) as r:
            r.raise_for_status()
            first = next(r.iter_content(4096), b"")
            if first.lstrip().startswith(b"<"):
                raise ValueError(f"UCSB download is HTML: {url}")
            n = 0
            with tmp.open("wb") as fh:
                fh.write(first)
                n += len(first)
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        fh.write(chunk)
                        n += len(chunk)
        if n < 1000:
            tmp.unlink(missing_ok=True)
            raise ValueError(f"UCSB year too small ({n} bytes): {url}")
        tmp.replace(dest)
        return dest


def gee_catalog_excerpt(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep only fields we actually read from the GEE STAC document."""
    extent = raw.get("extent") or {}
    summaries = raw.get("summaries") or {}
    precip = summaries.get("precipitation") or {}
    return {
        "id": raw.get("id"),
        "title": raw.get("title"),
        "version": raw.get("version"),
        "license": raw.get("license"),
        "temporal_interval": (extent.get("temporal") or {}).get("interval"),
        "spatial_bbox": (extent.get("spatial") or {}).get("bbox"),
        "cadence": raw.get("gee:interval"),
        "gsd_m": summaries.get("gsd"),
        "precip_min": precip.get("minimum"),
        "precip_max": precip.get("maximum"),
        "precip_range_is_estimated": precip.get("gee:estimated_range"),
        "terms": raw.get("gee:terms_of_use"),
        "citation": raw.get("sci:citation"),
        "source": GEE_STAC_PENTAD,
        "pixels_included": False,
    }

