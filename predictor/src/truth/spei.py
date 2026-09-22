"""CSIC SPEI global drought index (catalogue name « SPEI »).

FR : Vérité catalogue « SPEI ». On ne invente pas de case, pas de
classe, pas de BSS. Sans fichier de grille, on ne compte pas les
cellules. Les régions sont celles du catalogue Phase 2.

EN : Catalogue name stays « SPEI ». Usable cell counts come only from
a published SPEI grid. A missing file is a blocker, not an inventory.

Preferred file : SPEIbase spei06.nc (6-month scale, same horizon as
Phase B SPI-6). CSIC page : https://spei.csic.es/database.html
v2.9 record : https://digital.csic.es/handle/10261/332007
GEE catalogue (metadata, not pixels) :
https://developers.google.com/earth-engine/datasets/catalog/CSIC_SPEI_2_11
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import numpy as np
import requests

from src.config import DATA_DIR, USER_AGENT

CATALOGUE_TRUTH = "SPEI"
TARGET_MED = "Sécheresse Méditerranée"
TARGET_US = "Sécheresse US"
TARGET_INDE = "Sécheresse Inde"

SPEI_CACHE = DATA_DIR / "truth" / "spei_cache"
SPEI_OUT = DATA_DIR / "truth" / "spei"

# Official / catalogue pages. Do not invent a mirror.
SPEI_CSIC_PAGE = "https://spei.csic.es/database.html"
SPEI_CSIC_V29_VIEWER = "https://spei.csic.es/spei_database_2_9/"
SPEI_CSIC_V29_SPEI06 = "https://spei.csic.es/spei_database_2_9/spei06.nc"
SPEI_CSIC_V210_VIEWER = "https://spei.csic.es/spei_database_2_10/"
DIGITAL_CSIC_V29 = "https://digital.csic.es/handle/10261/332007"
DIGITAL_CSIC_V210 = "https://digital.csic.es/handle/10261/364137"
DIGITAL_CSIC_V29_DOI = "https://doi.org/10.20350/digitalCSIC/15470"
DIGITAL_CSIC_V210_DOI = "https://doi.org/10.20350/digitalCSIC/16497"
GEE_STAC_211 = (
    "https://storage.googleapis.com/earthengine-stac/catalog/CSIC/CSIC_SPEI_2_11.json"
)
GEE_HTML_211 = (
    "https://developers.google.com/earth-engine/datasets/catalog/CSIC_SPEI_2_11"
)
GEE_API_211 = (
    "https://earthengine.googleapis.com/v1/projects/earthengine-legacy"
    "/imageCollections/CSIC/SPEI/2_11"
)
VICENTE_2010 = "https://doi.org/10.1175/2009JCLI2909.1"
WMO_SPI_GUIDE = "https://library.wmo.int/idurl/4/39629"

# IPCC AR6 WGI reference region MED (Iturbide et al. 2020). Vertices
# copied from the published CSV (lon|lat), not redrawn.
# MED is labelled Land-Ocean in that CSV.
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

# USDA Climate Hub mainland states, same published lists as PR 240.
# Midwest : https://www.climatehubs.usda.gov/hubs/midwest
# Southwest : https://www.climatehubs.usda.gov/hubs/southwest/about
# Natural Earth 50m admin-1 names (public domain), matched as published.
NE_ADMIN1_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_50m_admin_1_states_provinces.geojson"
)
MIDWEST_NE_NAMES = (
    "Illinois", "Indiana", "Iowa", "Michigan",
    "Minnesota", "Missouri", "Ohio", "Wisconsin",
)
SOUTHWEST_NE_NAMES = (
    "Arizona", "California", "Nevada", "New Mexico", "Utah",
)
# Catalogue Phase 2 : Maharashtra et Karnataka (pas toute l'Inde).
INDE_NE_NAMES = ("Maharashtra", "Karnataka")

# CSIC / GEE published SPEI display range (STAC summaries, estimated_range=false).
CSIC_GEE_SPEI_MIN = -2.33
CSIC_GEE_SPEI_MAX = 2.33

# WMO-No. 1090 SPI classes. SPEI is the same kind of standardized
# number (Vicente-Serrano 2010). Count only, not a priced product.
WMO_SPI_CLASSES: tuple[tuple[str, Optional[float], Optional[float]], ...] = (
    ("extremely_dry", None, -2.0),
    ("severely_dry", -2.0, -1.5),
    ("moderately_dry", -1.5, -1.0),
    ("near_normal", -1.0, 1.0),
    ("moderately_wet", 1.0, 1.5),
    ("severely_wet", 1.5, 2.0),
    ("extremely_wet", 2.0, None),
)

# Already written in predictor/PHASE_B_SCAFFOLDING.md §3.1 (SPI-6 ≤ -1.5).
# Count only.
PHASE_B_DRY_THRESHOLD = -1.5
DEFAULT_TIMESCALE = 6

PROBE_URLS = (
    SPEI_CSIC_PAGE,
    SPEI_CSIC_V29_VIEWER,
    SPEI_CSIC_V29_SPEI06,
    SPEI_CSIC_V210_VIEWER,
    DIGITAL_CSIC_V29,
    DIGITAL_CSIC_V210,
    DIGITAL_CSIC_V29_DOI,
    GEE_STAC_211,
    GEE_HTML_211,
    GEE_API_211,
    IPCC_REGIONS_CSV,
    NE_ADMIN1_URL,
)


def wmo_class(value: float) -> str:
    """Map a published SPEI/SPI value to the WMO-No. 1090 table.

    Extremely dry : SPEI ≤ -2.0. Severely dry : -2.0 < SPEI ≤ -1.5.
    Moderately dry : -1.5 < SPEI ≤ -1.0. A value belongs to one class.
    """
    if value <= -2.0:
        return "extremely_dry"
    if value <= -1.5:
        return "severely_dry"
    if value <= -1.0:
        return "moderately_dry"
    if value < 1.0:
        return "near_normal"
    if value < 1.5:
        return "moderately_wet"
    if value < 2.0:
        return "severely_wet"
    return "extremely_wet"


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
    """Keep published Natural Earth polygons whose name matches exactly.

    Unmatched names stay listed. Nothing is drawn by hand.
    """
    wanted = {n.casefold(): n for n in names}
    found: dict[str, list[list[tuple[float, float]]]] = {n: [] for n in names}
    extras: list[str] = []
    for feat in geojson.get("features") or []:
        props = feat.get("properties") or {}
        name = _feature_name(props)
        admin = _feature_admin(props)
        if name.casefold() not in wanted:
            continue
        if admin_contains and not any(tok.casefold() in admin.casefold() for tok in admin_contains):
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


@dataclass
class SpeiGrid:
    """One published SPEI cube. NaN = missing, never filled."""
    lats: np.ndarray
    lons: np.ndarray
    times: list[date]
    values: np.ndarray
    timescale_months: int
    source: dict[str, Any] = field(default_factory=dict)

    @property
    def n_times(self) -> int:
        return len(self.times)

    @property
    def n_lat(self) -> int:
        return int(self.lats.size)

    @property
    def n_lon(self) -> int:
        return int(self.lons.size)


def lon_in_180(lon: float) -> float:
    """SPEIbase / CRU longitudes may be 0..360. Keep the published number
    for storage; convert only when testing a (-180, 180) polygon.
    """
    if lon > 180.0:
        return lon - 360.0
    return lon


def _ring_bbox(ring: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    return min(xs), max(xs), min(ys), max(ys)


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


def coverage_for_mask(grid: SpeiGrid, mask: np.ndarray, label: str) -> dict[str, Any]:
    """Usable cells = finite SPEI on the published mask. Empty stays empty."""
    n_mask = int(mask.sum())
    if n_mask == 0 or grid.n_times == 0:
        return {
            "region": label,
            "n_cells_in_published_cut": n_mask,
            "n_times": grid.n_times,
            "usable_measured": False,
            "note": "Aucune cellule dans le découpage publié, ou aucune date.",
        }
    slab = grid.values[:, mask]
    finite = np.isfinite(slab)
    n_usable_any = int(np.any(finite, axis=0).sum())
    months_all_valid = [grid.times[t].isoformat()[:7] for t in range(grid.n_times) if bool(np.all(finite[t]))]
    months_any_valid = [grid.times[t].isoformat()[:7] for t in range(grid.n_times) if bool(np.any(finite[t]))]
    years = sorted({t.year for t in grid.times})
    years_with_a_value: list[int] = []
    years_missing_in_span: list[int] = []
    if years:
        by_year: dict[int, list[int]] = {}
        for t_i, t in enumerate(grid.times):
            by_year.setdefault(t.year, []).append(t_i)
        for y in range(years[0], years[-1] + 1):
            idxs = by_year.get(y, [])
            if idxs and any(bool(np.any(finite[i])) for i in idxs):
                years_with_a_value.append(y)
            else:
                years_missing_in_span.append(y)
    class_counts = {name: 0 for name, _, _ in WMO_SPI_CLASSES}
    n_finite = 0
    n_le_phase_b = 0
    n_outside_gee_range = 0
    if n_usable_any:
        flat = slab[finite]
        n_finite = int(flat.size)
        class_counts = {
            "extremely_dry": int(np.sum(flat <= -2.0)),
            "severely_dry": int(np.sum((flat > -2.0) & (flat <= -1.5))),
            "moderately_dry": int(np.sum((flat > -1.5) & (flat <= -1.0))),
            "near_normal": int(np.sum((flat > -1.0) & (flat < 1.0))),
            "moderately_wet": int(np.sum((flat >= 1.0) & (flat < 1.5))),
            "severely_wet": int(np.sum((flat >= 1.5) & (flat < 2.0))),
            "extremely_wet": int(np.sum(flat >= 2.0)),
        }
        n_le_phase_b = int(np.sum(flat <= PHASE_B_DRY_THRESHOLD))
        n_outside_gee_range = int(
            np.sum((flat < CSIC_GEE_SPEI_MIN) | (flat > CSIC_GEE_SPEI_MAX))
        )
    first_t = grid.times[0].isoformat() if grid.times else None
    last_t = grid.times[-1].isoformat() if grid.times else None
    first_valid = months_any_valid[0] if months_any_valid else None
    last_valid = months_any_valid[-1] if months_any_valid else None
    return {
        "region": label,
        "n_cells_in_published_cut": n_mask,
        "n_cells_usable_any_month": n_usable_any,
        "n_cells_never_valid": n_mask - n_usable_any,
        "n_times": grid.n_times,
        "first_month": first_t,
        "last_month": last_t,
        "first_month_with_a_value": first_valid,
        "last_month_with_a_value": last_valid,
        "n_months_with_any_valid": len(months_any_valid),
        "n_months_without_any_valid": grid.n_times - len(months_any_valid),
        "n_months_all_cells_valid": len(months_all_valid),
        "n_calendar_years_in_file": len(years),
        "n_calendar_years_with_a_value": len(years_with_a_value),
        "missing_years_in_span": years_missing_in_span,
        "n_missing_years_in_span": len(years_missing_in_span),
        "n_finite_cell_months": n_finite,
        "n_cell_months_spei_le_minus_1_5": n_le_phase_b,
        "n_cell_months_outside_gee_pm_2_33": n_outside_gee_range,
        "wmo_class_cell_months": class_counts,
        "usable_measured": True,
        "timescale_months": grid.timescale_months,
        "thresholds": {
            "phase_b_spi6_le": PHASE_B_DRY_THRESHOLD,
            "phase_b_source": "PHASE_B_SCAFFOLDING.md §3.1 (count only)",
            "wmo_spi_source": WMO_SPI_GUIDE,
            "csic_gee_range": [CSIC_GEE_SPEI_MIN, CSIC_GEE_SPEI_MAX],
            "csic_gee_source": GEE_STAC_211,
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
        "wmo_class_cell_months": None,
        "reason": reason,
    }


class SpeiClient:
    """Probe public SPEI URLs. Download pixels only when the file is real."""

    def __init__(self, cache_dir: Path = SPEI_CACHE, timeout: int = 20):
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
            r = self.session.get(url, timeout=self.timeout, stream=True, allow_redirects=True)
            chunk = next(r.iter_content(8192), b"")
            rest_len = 0
            # Do not pull a 367 MB NetCDF into RAM during a probe.
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
            if "netcdf" in ctype or url.endswith(".nc"):
                row["n_bytes"] = int(r.headers.get("Content-Length") or len(chunk))
            else:
                extra = b"".join(r.iter_content(64_000))
                rest_len = len(extra)
                chunk = chunk + extra
                row["n_bytes"] = len(chunk)
            row["http_status"] = r.status_code
            row["content_type"] = ctype or None
            row["final_url"] = str(r.url)
            text_head = chunk[:800].decode("utf-8", errors="replace")
            if (
                "Making sure you're not a bot" in text_head
                or "anubis" in text_head.lower()
                or "Protected by" in text_head
            ):
                row["note"] = "Anubis (page anti-robot DIGITAL.CSIC)"
            elif "Web Page Blocked" in text_head or "has been blocked" in text_head:
                row["note"] = "filtre réseau : page bloquée"
            elif r.status_code == 200 and (
                "application/json" in ctype
                or "text/" in ctype
                or "geo+json" in ctype
                or url.endswith(".csv")
                or url.endswith(".json")
                or url.endswith(".geojson")
            ):
                row["ok"] = True
                row["note"] = "réponse lue"
            elif r.status_code == 200 and ("netcdf" in ctype or url.endswith(".nc")):
                row["ok"] = True
                row["note"] = "en-tête NetCDF lu (fichier non téléchargé ici)"
            else:
                row["note"] = f"HTTP {r.status_code}"
            row["n_bytes"] = row["n_bytes"] if row["n_bytes"] is not None else rest_len
        except requests.Timeout:
            row["note"] = f"timeout {self.timeout}s, 0 octet"
        except requests.RequestException as exc:
            row["note"] = f"erreur réseau : {type(exc).__name__}"
        row["elapsed_s"] = round(time.time() - started, 3)
        return row

    def probe_all(self, urls: tuple[str, ...] = PROBE_URLS) -> list[dict[str, Any]]:
        return [self.probe(u) for u in urls]

    def fetch_json(self, url: str) -> dict[str, Any]:
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict):
            raise ValueError(f"JSON object expected from {url}")
        return data

    def fetch_text(self, url: str) -> str:
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.text

    def cached_spei06(self) -> Optional[Path]:
        if not self.cache_dir.exists():
            return None
        files = sorted(self.cache_dir.glob("spei06*.nc"))
        return files[-1] if files else None

    def bitstream_urls(self, html: str, page_url: str) -> list[str]:
        """Collect published bitstream links. No guessed file numbers."""
        import re
        from urllib.parse import urljoin
        found: list[str] = []
        for href in re.findall(r'href="([^"]+)"', html):
            if "bitstream" not in href.lower() and "spei06" not in href.lower():
                continue
            if href.startswith("/"):
                href = urljoin(page_url, href)
            if href.startswith("http"):
                found.append(href)
        # Prefer explicit spei06.nc names; keep order stable.
        spei06 = [u for u in found if "spei06" in u.lower()]
        return spei06 or found

    def download_spei06(self, url: str) -> Path:
        """Stream a named spei06.nc. Partial files are deleted, not invented."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        dest = self.cache_dir / "spei06.nc"
        tmp = self.cache_dir / "spei06.nc.part"
        with self.session.get(url, timeout=120, stream=True) as r:
            r.raise_for_status()
            ctype = (r.headers.get("Content-Type") or "").lower()
            first = next(r.iter_content(4096), b"")
            if first.lstrip().startswith(b"<") or "html" in ctype:
                raise ValueError(f"SPEI download is HTML, not NetCDF: {url}")
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
            raise ValueError(f"SPEI download too small ({n} bytes): {url}")
        tmp.replace(dest)
        return dest


def gee_catalog_excerpt(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep only fields we actually read from the GEE STAC document."""
    extent = raw.get("extent") or {}
    summaries = raw.get("summaries") or {}
    spei06 = summaries.get("SPEI_06_month") or {}
    return {
        "id": raw.get("id"),
        "title": raw.get("title"),
        "version": raw.get("version"),
        "deprecated": raw.get("deprecated"),
        "license": raw.get("license"),
        "temporal_interval": (extent.get("temporal") or {}).get("interval"),
        "spatial_bbox": (extent.get("spatial") or {}).get("bbox"),
        "cadence": raw.get("gee:interval"),
        "gsd_m": summaries.get("gsd"),
        "spei06_min": spei06.get("minimum"),
        "spei06_max": spei06.get("maximum"),
        "spei06_range_is_estimated": spei06.get("gee:estimated_range"),
        "n_bands": len(summaries.get("eo:bands") or []),
        "citation": raw.get("sci:citation"),
        "doi": raw.get("sci:doi"),
        "source": GEE_STAC_211,
        "pixels_included": False,
    }


def read_spei_netcdf(path: Path, timescale_months: int = DEFAULT_TIMESCALE) -> SpeiGrid:
    """Read a SPEIbase-style NetCDF. Missing values stay missing."""
    try:
        import netCDF4  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "netCDF4 is required to read a SPEI .nc file. "
            "The inventory does not invent cells without the reader."
        ) from exc
    ds = netCDF4.Dataset(str(path))
    try:
        lat_name = next(n for n in ("lat", "latitude", "y") if n in ds.variables)
        lon_name = next(n for n in ("lon", "longitude", "x") if n in ds.variables)
        time_name = next(n for n in ("time",) if n in ds.variables)
        var_name = next(
            n for n in ("spei", "SPEI", f"SPEI_{timescale_months:02d}_month")
            if n in ds.variables
        )
        lats = np.asarray(ds.variables[lat_name][:], dtype=float)
        lons = np.asarray(ds.variables[lon_name][:], dtype=float)
        tvar = ds.variables[time_name]
        try:
            times_raw = netCDF4.num2date(tvar[:], tvar.units, getattr(tvar, "calendar", "standard"))
        except Exception:
            times_raw = tvar[:]
        times: list[date] = []
        gaps: list[str] = []
        for i, t in enumerate(times_raw):
            try:
                times.append(date(int(t.year), int(t.month), int(getattr(t, "day", 1) or 1)))
            except Exception:
                gaps.append(f"time[{i}] unreadable")
        arr = np.asarray(ds.variables[var_name][:], dtype=float)
        fill = getattr(ds.variables[var_name], "_FillValue", None)
        if fill is not None:
            arr = np.where(arr == float(fill), np.nan, arr)
        arr = np.where(np.abs(arr) > 1.0e20, np.nan, arr)
        if arr.ndim != 3:
            raise ValueError(f"SPEI variable {var_name} is not 3-D: {arr.shape}")
        # Normalize to (time, lat, lon)
        if arr.shape[0] != len(times) and arr.shape[-1] == len(times):
            arr = np.moveaxis(arr, -1, 0)
        if arr.shape[1] != lats.size and arr.shape[2] == lats.size:
            arr = np.swapaxes(arr, 1, 2)
        return SpeiGrid(
            lats=lats,
            lons=lons,
            times=times,
            values=arr,
            timescale_months=timescale_months,
            source={
                "path": str(path),
                "filename": path.name,
                "variable": var_name,
                "n_bytes": path.stat().st_size,
                "time_gaps": gaps,
                "title": getattr(ds, "title", None),
                "version": getattr(ds, "version", None),
            },
        )
    finally:
        ds.close()


def inventory_from_netcdf(
    path: Path,
    regions: dict[str, Any],
    timescale_months: int = DEFAULT_TIMESCALE,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Count regions by reading only the bbox slice. Full cube stays on disk."""
    try:
        import netCDF4  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "netCDF4 is required to read a SPEI .nc file. "
            "The inventory does not invent cells without the reader."
        ) from exc
    ds = netCDF4.Dataset(str(path))
    try:
        lats = np.asarray(ds.variables["lat"][:], dtype=float)
        lons = np.asarray(ds.variables["lon"][:], dtype=float)
        tvar = ds.variables["time"]
        times_raw = netCDF4.num2date(
            tvar[:], tvar.units, getattr(tvar, "calendar", "standard")
        )
        times: list[date] = []
        time_gaps: list[str] = []
        for i, t in enumerate(times_raw):
            try:
                times.append(date(int(t.year), int(t.month), int(getattr(t, "day", 1) or 1)))
            except Exception:
                time_gaps.append(f"time[{i}] unreadable")
        attrs = {a: str(ds.getncattr(a)) for a in ds.ncattrs()}
        header = {
            "path": str(path),
            "filename": path.name,
            "n_bytes": path.stat().st_size,
            "shape": [int(x) for x in ds.variables["spei"].shape],
            "n_lat": int(lats.size),
            "n_lon": int(lons.size),
            "n_times": len(times),
            "first_month": times[0].isoformat() if times else None,
            "last_month": times[-1].isoformat() if times else None,
            "time_gaps": time_gaps,
            "fill_value": float(getattr(ds.variables["spei"], "_FillValue", 1e30)),
            "title": attrs.get("title"),
            "version": attrs.get("version"),
            "summary": attrs.get("summary"),
            "date_created": attrs.get("date"),
            "institution": attrs.get("institution"),
            "source": attrs.get("source"),
            "attrs": attrs,
        }
        out: dict[str, Any] = {}
        for label, spec in regions.items():
            rings = spec.get("rings") or []
            if not rings:
                out[label] = empty_region_row(
                    label,
                    "Découpage publié sans polygone lisible. Pas de compte inventé.",
                )
                continue
            mask = mask_from_rings(lats, lons, rings)
            ii, jj = np.where(mask)
            if ii.size == 0:
                dummy = SpeiGrid(
                    lats=lats[:1], lons=lons[:1], times=times,
                    values=np.full((len(times), 1, 1), np.nan),
                    timescale_months=timescale_months,
                    source=header,
                )
                out[label] = coverage_for_mask(
                    dummy, np.zeros((1, 1), dtype=bool), label
                )
                out[label]["n_cells_in_published_cut"] = 0
                continue
            i0, i1 = int(ii.min()), int(ii.max()) + 1
            j0, j1 = int(jj.min()), int(jj.max()) + 1
            slab = np.asarray(ds.variables["spei"][:, i0:i1, j0:j1], dtype=np.float32)
            slab = np.where(np.abs(slab) >= 1.0e20, np.nan, slab)
            local = mask[i0:i1, j0:j1]
            grid = SpeiGrid(
                lats=lats[i0:i1],
                lons=lons[j0:j1],
                times=times,
                values=slab,
                timescale_months=timescale_months,
                source=header,
            )
            out[label] = coverage_for_mask(grid, local, label)
        return out, header
    finally:
        ds.close()


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
    midwest = extract_named_states(ne_geojson or {}, MIDWEST_NE_NAMES, ("United States", "USA"))
    southwest = extract_named_states(ne_geojson or {}, SOUTHWEST_NE_NAMES, ("United States", "USA"))
    inde = extract_named_states(ne_geojson or {}, INDE_NE_NAMES, ("India",))
    us_rings: list[list[tuple[float, float]]] = []
    for name in MIDWEST_NE_NAMES + SOUTHWEST_NE_NAMES:
        us_rings.extend(midwest["rings_by_name"].get(name, []))
        us_rings.extend(southwest["rings_by_name"].get(name, []))
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
        TARGET_US: {
            "cut": "USDA Climate Hub Midwest + Southwest (listes PR 240)",
            "catalogue_target": TARGET_US,
            "midwest": midwest,
            "southwest": southwest,
            "rings": us_rings,
            "source_hubs": {
                "midwest": "https://www.climatehubs.usda.gov/hubs/midwest",
                "southwest": "https://www.climatehubs.usda.gov/hubs/southwest/about",
            },
            "source_polygons": NE_ADMIN1_URL,
        },
        TARGET_INDE: {
            "cut": "Maharashtra + Karnataka (catalogue Phase 2)",
            "catalogue_target": TARGET_INDE,
            "states": inde,
            "rings": inde_rings,
            "source_polygons": NE_ADMIN1_URL,
        },
    }


def count_regions(grid: SpeiGrid, regions: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for label, spec in regions.items():
        rings = spec.get("rings") or []
        if not rings:
            out[label] = empty_region_row(
                label,
                "Découpage publié sans polygone lisible. Pas de compte inventé.",
            )
            continue
        mask = mask_from_rings(grid.lats, grid.lons, rings)
        out[label] = coverage_for_mask(grid, mask, label)
    return out
