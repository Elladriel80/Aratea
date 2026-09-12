"""Densités ville / végétation / eau autour des stations officielles.

FR : Pas des comptages OSM (v2, rejeté). Trois couches publiques
documentées, lues telles quelles :

  - Ville : habitants / km². WorldPop 2020, 30 secondes d'arc (~1 km),
    fichier de *comptage* par pixel. On convertit en densité avec la
    surface réelle du pixel (formule sphère, rayon 6371 km). On n'invente
    pas un nombre d'habitants.
  - Végétation : part des pixels WorldCover 2021 (10 m) classés arbre,
    buisson, herbe, culture, marais, mangrove. Unité : km² verts / km².
  - Eau : part des pixels WorldCover classés « eau permanente » (80).
    Unité : km² d'eau / km². L'océan est de l'eau.

EN : Real raster densities in a circle around the official station.
OSM feature counts are out of scope (v2 NO-GO).

Sources (no invented values):
  WorldPop count 2020 1 km (USA file, WGS84, 30 arc-sec):
    https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/2020/USA/usa_ppp_2020_1km_Aggregated.tif
    WorldPop & CIESIN (2018), https://dx.doi.org/10.5258/SOTON/WP00674
  ESA WorldCover 10 m 2021 v200 (CC BY 4.0):
    https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/
    Zanaga et al. (2022), https://doi.org/10.5281/zenodo.7254221
"""
from __future__ import annotations

import math
from typing import Iterable, Optional

import numpy as np

EARTH_R_KM = 6371.0
RADII_KM = (1, 2, 5, 10, 20)

# WorldCover 2021 legend (Zanaga et al. 2022). 0 = no data.
WC_TREE = 10
WC_SHRUB = 20
WC_GRASS = 30
WC_CROP = 40
WC_BUILT = 50
WC_BARE = 60
WC_SNOW = 70
WC_WATER = 80
WC_WETLAND = 90
WC_MANGROVE = 95
WC_MOSS = 100

# « Forêt / végétation » = couvert vert, pas seulement les arbres.
VEG_CLASSES = frozenset({
    WC_TREE, WC_SHRUB, WC_GRASS, WC_CROP, WC_WETLAND, WC_MANGROVE, WC_MOSS,
})
WATER_CLASSES = frozenset({WC_WATER})
TREE_CLASSES = frozenset({WC_TREE, WC_MANGROVE})

WORLDPOP_URL = (
    "https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/2020/USA/"
    "usa_ppp_2020_1km_Aggregated.tif"
)
WORLDPOP_NODATA = -99999.0
WORLDCOVER_TILE_TMPL = (
    "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/"
    "ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"
)
WORLDCOVER_TILE_DEG = 3

SOURCE_NOTES = {
    "population": (
        "WorldPop 2020, fichier usa_ppp_2020_1km_Aggregated.tif "
        "(habitants par pixel, 30 secondes d'arc, WGS84). "
        "Densité = somme des habitants dans le disque / surface du disque "
        "(π r²). Pixel sans donnée = 0 habitant. "
        "https://dx.doi.org/10.5258/SOTON/WP00674"
    ),
    "vegetation": (
        "ESA WorldCover 10 m 2021 v200, classes 10/20/30/40/90/95/100 "
        "(arbre, buisson, herbe, culture, marais, mangrove, mousse). "
        "Densité = pixels verts / pixels lus. "
        "https://doi.org/10.5281/zenodo.7254221"
    ),
    "water": (
        "ESA WorldCover 10 m 2021 v200, classe 80 (eau permanente), "
        "y compris mer et lacs. Densité = pixels eau / pixels lus. "
        "https://doi.org/10.5281/zenodo.7254221"
    ),
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2)
    return 2 * EARTH_R_KM * math.asin(math.sqrt(min(1.0, a)))


def cell_area_km2(lat_center: float, dlat_deg: float, dlon_deg: float) -> float:
    """Surface d'un pixel WGS84 (sphère 6371 km). Pas une invention : géométrie."""
    dlat = math.radians(abs(dlat_deg))
    dlon = math.radians(abs(dlon_deg))
    return EARTH_R_KM * EARTH_R_KM * dlat * dlon * math.cos(math.radians(lat_center))


def disk_area_km2(radius_km: float) -> float:
    return math.pi * radius_km * radius_km


def worldcover_tile_id(lat_sw: int, lon_sw: int) -> str:
    """Identifiant dalles WorldCover : coin sud-ouest, pas de 3°."""
    ns = "N" if lat_sw >= 0 else "S"
    ew = "E" if lon_sw >= 0 else "W"
    return f"{ns}{abs(lat_sw):02d}{ew}{abs(lon_sw):03d}"


def tile_sw_corner(lat: float, lon: float, step: int = WORLDCOVER_TILE_DEG) -> tuple[int, int]:
    lat0 = int(math.floor(lat / step) * step)
    lon0 = int(math.floor(lon / step) * step)
    return lat0, lon0


def worldcover_tiles_for_bbox(south: float, west: float, north: float, east: float,
                              step: int = WORLDCOVER_TILE_DEG) -> list[str]:
    """Toutes les dalles 3° qui touchent la boîte. Longitudes dans (−180, 180)."""
    tiles: list[str] = []
    lat = int(math.floor(south / step) * step)
    while lat < north:
        lon = int(math.floor(west / step) * step)
        while lon < east:
            tiles.append(worldcover_tile_id(lat, lon))
            lon += step
        lat += step
    return tiles


def bbox_for_radius(lat: float, lon: float, radius_km: float,
                    pad_km: float = 1.0) -> tuple[float, float, float, float]:
    """(south, west, north, east) en degrés, marge pour ne pas couper le disque."""
    r = radius_km + pad_km
    dlat = r / 111.32
    clon = max(0.2, math.cos(math.radians(lat)))
    dlon = r / (111.32 * clon)
    return lat - dlat, lon - dlon, lat + dlat, lon + dlon


def circle_mask(lat0: float, lon0: float, lats: np.ndarray, lons: np.ndarray,
                radius_km: float) -> np.ndarray:
    """Masque booléen : centre de pixel à ≤ radius_km de (lat0, lon0)."""
    if lats.size == 0:
        return np.zeros(lats.shape, dtype=bool)
    phi1 = np.radians(lat0)
    phi2 = np.radians(lats)
    dphi = np.radians(lats - lat0)
    dl = np.radians(lons - lon0)
    a = (np.sin(dphi / 2) ** 2
         + np.cos(phi1) * np.cos(phi2) * np.sin(dl / 2) ** 2)
    dist = 2 * EARTH_R_KM * np.arcsin(np.minimum(1.0, np.sqrt(a)))
    return dist <= radius_km


def mesh_centers(transform, height: int, width: int) -> tuple[np.ndarray, np.ndarray]:
    """Centres de pixels (lat, lon) pour un GeoTransform rasterio/affine."""
    # x = transform.c + (col + 0.5) * transform.a + (row + 0.5) * transform.b
    # y = transform.f + (col + 0.5) * transform.d + (row + 0.5) * transform.e
    rows = np.arange(height)
    cols = np.arange(width)
    cc, rr = np.meshgrid(cols, rows)
    xs = transform.c + (cc + 0.5) * transform.a + (rr + 0.5) * transform.b
    ys = transform.f + (cc + 0.5) * transform.d + (rr + 0.5) * transform.e
    return ys, xs  # lat, lon for north-up WGS84


def population_in_circle(
    count: np.ndarray,
    lats: np.ndarray,
    lons: np.ndarray,
    lat0: float,
    lon0: float,
    radius_km: float,
    nodata: float = WORLDPOP_NODATA,
) -> dict:
    """Habitants et densité dans le disque. count = habitants par pixel."""
    mask = circle_mask(lat0, lon0, lats, lons, radius_km)
    n_pix = int(mask.sum())
    if n_pix == 0:
        return {
            "n_pixels": 0, "n_valid": 0, "people": None,
            "pop_per_km2": None, "disk_km2": disk_area_km2(radius_km),
        }
    vals = count[mask]
    valid = np.isfinite(vals) & (vals != nodata) & (vals >= 0)
    people = float(vals[valid].sum()) if valid.any() else 0.0
    disk = disk_area_km2(radius_km)
    return {
        "n_pixels": n_pix,
        "n_valid": int(valid.sum()),
        "people": people,
        "pop_per_km2": people / disk,
        "disk_km2": disk,
    }


def cover_in_circle(
    klass: np.ndarray,
    lats: np.ndarray,
    lons: np.ndarray,
    lat0: float,
    lon0: float,
    radius_km: float,
) -> dict:
    """Parts WorldCover dans le disque. Pixel 0 = pas de donnée, exclu."""
    mask = circle_mask(lat0, lon0, lats, lons, radius_km)
    n_pix = int(mask.sum())
    if n_pix == 0:
        return {
            "n_pixels": 0, "n_valid": 0,
            "veg_frac": None, "tree_frac": None, "water_frac": None,
            "built_frac": None, "disk_km2": disk_area_km2(radius_km),
        }
    vals = klass[mask]
    valid = vals != 0
    n_valid = int(valid.sum())
    if n_valid == 0:
        return {
            "n_pixels": n_pix, "n_valid": 0,
            "veg_frac": None, "tree_frac": None, "water_frac": None,
            "built_frac": None, "disk_km2": disk_area_km2(radius_km),
        }
    v = vals[valid]
    return {
        "n_pixels": n_pix,
        "n_valid": n_valid,
        "veg_frac": float(np.isin(v, list(VEG_CLASSES)).mean()),
        "tree_frac": float(np.isin(v, list(TREE_CLASSES)).mean()),
        "water_frac": float(np.isin(v, list(WATER_CLASSES)).mean()),
        "built_frac": float((v == WC_BUILT).mean()),
        "disk_km2": disk_area_km2(radius_km),
    }


def ranks(xs: list[float]) -> list[float]:
    """Rangs moyens pour les ex aequo (Spearman)."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    out = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def pearson(xs: list[float], ys: list[float]) -> Optional[float]:
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0.0 or dy == 0.0:
        return None
    return num / (dx * dy)


def spearman(xs: list[float], ys: list[float]) -> Optional[dict]:
    """Corrélation de rang. p approximé par une loi de Student (n petit)."""
    if len(xs) != len(ys) or len(xs) < 5:
        return None
    r = pearson(ranks(xs), ranks(ys))
    if r is None:
        return None
    n = len(xs)
    if abs(r) >= 1.0:
        p = 0.0
    else:
        t = r * math.sqrt((n - 2) / (1.0 - r * r))
        # p bilatéral, approximation régulière incomplète via erfc sur z
        # Pour n=18 on reste descriptif : on publie r et t, pas une p inventée
        # plus précise que Student. p via Regularized incomplete beta.
        p = _student_p_two_sided(abs(t), n - 2)
    return {"n": n, "r": r, "t": None if abs(r) >= 1.0 else t, "p_approx": p}


def _student_p_two_sided(t: float, df: int) -> float:
    """P(|T| > t) pour Student(df). Beta régulière, pas une table inventée."""
    if df <= 0:
        return None  # type: ignore[return-value]
    x = df / (df + t * t)
    # I_x(df/2, 1/2) = P(T² > t²) = p two-sided
    return _reg_inc_beta(x, df / 2.0, 0.5)


def _reg_inc_beta(x: float, a: float, b: float) -> float:
    """I_x(a,b) via série (a,b > 0, 0≤x≤1). Suffisant pour n≈18."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    # Continued fraction (Numerical Recipes, public domain algorithm).
    ln_beta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1.0 - x) - ln_beta) / a
    # Lentz CF for incomplete beta
    tiny = 1e-30
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 200):
        m2 = 2 * m
        num = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + num * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + num / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        num = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + num * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + num / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-8:
            break
    return front * h


def fit_ols(x_rows: list[list[float]], y: list[float]) -> Optional[dict]:
    """Moindres carrés. Première colonne = 1 (constante). Rien d'inventé."""
    if len(y) < len(x_rows[0]) + 2 or len(x_rows) != len(y):
        return None
    x = np.asarray(x_rows, dtype=float)
    yy = np.asarray(y, dtype=float)
    try:
        beta, *_ = np.linalg.lstsq(x, yy, rcond=None)
    except np.linalg.LinAlgError:
        return None
    pred = x @ beta
    resid = yy - pred
    return {
        "beta": [float(b) for b in beta],
        "n": int(len(y)),
        "rmse": float(np.sqrt(np.mean(resid ** 2))),
        "resid_std": float(np.std(resid, ddof=0)),
    }


def standardize_train(rows: list[list[float]]) -> tuple[list[list[float]], list[float], list[float]]:
    """Centre-réduit les colonnes 1… (la constante reste 1). Stats TRAIN only."""
    arr = np.asarray(rows, dtype=float)
    means = [0.0]
    stds = [1.0]
    out = arr.copy()
    for j in range(1, arr.shape[1]):
        mu = float(arr[:, j].mean())
        sd = float(arr[:, j].std())
        if sd == 0.0:
            sd = 1.0
        out[:, j] = (arr[:, j] - mu) / sd
        means.append(mu)
        stds.append(sd)
    return out.tolist(), means, stds


def apply_standard(row: list[float], means: list[float], stds: list[float]) -> list[float]:
    return [(row[j] if j == 0 else (row[j] - means[j]) / stds[j])
            for j in range(len(row))]


def density_feature_row(dens: dict, radius_km: int) -> Optional[list[float]]:
    """[1, log1p(pop/km²), végétation, eau] à un rayon. None si un trou."""
    block = dens.get(str(radius_km)) or dens.get(radius_km)
    if not block:
        return None
    pop = block.get("pop_per_km2")
    veg = block.get("veg_frac")
    water = block.get("water_frac")
    if pop is None or veg is None or water is None:
        return None
    return [1.0, math.log1p(max(0.0, pop)), float(veg), float(water)]
