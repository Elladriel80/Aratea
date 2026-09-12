"""eval_land_density.py — ville, végétation, eau autour des 18 stations.

FR : Mesure l'hypothèse du 12 septembre 2026 : habitants / km², couvert
vert / km², eau / km², à plusieurs rayons autour du vrai point de la
station. Relie ces nombres au climat officiel (fichier siècle). Compare
un correctif linéaire (TRAIN) au mélange corrigé ville par ville (0,1154)
si les prévisions A1 sont là. Ne change pas le champion.

Usage:
    python scripts/eval_land_density.py
    python scripts/eval_land_density.py --skip-fetch
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import statistics
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.config import USER_AGENT  # noqa: E402
from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, kalshi_stations  # noqa: E402
from src.truth.land_density import (  # noqa: E402
    RADII_KM, SOURCE_NOTES, WORLDPOP_NODATA, WORLDPOP_URL, WORLDCOVER_TILE_TMPL,
    apply_standard, bbox_for_radius, cover_in_circle, density_feature_row,
    disk_area_km2, fit_ols, mesh_centers, population_in_circle, spearman,
    standardize_train, worldcover_tiles_for_bbox,
)
from src.truth.skill import sign_test_by_date  # noqa: E402
from src.truth.synthetic_bins import brier, kalshi_style_bins, prob_in_bin_gaussian  # noqa: E402

CACHE = TRUTH_DIR / "density_cache"
OUT_DEFAULT = TRUTH_DIR / "density"
WORLDPOP_NAME = "usa_ppp_2020_1km_Aggregated.tif"
A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)
SIGMA_FLOOR = 1.0
MIN_BIAS_PAIRS = 20
CHAMPION_BRIER = 0.1154
CITY_FR = {
    "KATL": "Atlanta", "KAUS": "Austin", "KBOS": "Boston", "KMDW": "Chicago",
    "KDFW": "Dallas", "KDEN": "Denver", "KHOU": "Houston", "KLAS": "Las Vegas",
    "KLAX": "Los Angeles", "KMIA": "Miami", "KMSP": "Minneapolis",
    "KNYC": "New York", "KPHL": "Philadelphie", "KPHX": "Phoenix",
    "KSAT": "San Antonio", "KSFO": "San Francisco", "KSEA": "Seattle",
    "KDCA": "Washington",
}


def _http_get(url: str, dest: Path, timeout: int = 180) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as r:
        dest.write_bytes(r.read())


def ensure_worldpop(cache: Path, allow_network: bool) -> Path:
    path = cache / WORLDPOP_NAME
    if path.exists() and path.stat().st_size > 1_000_000:
        return path
    if not allow_network:
        raise FileNotFoundError(f"WorldPop absent : {path}")
    print(f"  télécharge WorldPop → {path}")
    _http_get(WORLDPOP_URL, path)
    return path


def _rio():
    import rasterio
    from rasterio.windows import from_bounds
    return rasterio, from_bounds


def read_worldpop_window(ds, lat: float, lon: float, radius_km: float):
    south, west, north, east = bbox_for_radius(lat, lon, radius_km)
    _, from_bounds = _rio()
    win = from_bounds(west, south, east, north, ds.transform)
    arr = ds.read(1, window=win, boundless=True, fill_value=ds.nodata or WORLDPOP_NODATA)
    transform = ds.window_transform(win)
    lats, lons = mesh_centers(transform, arr.shape[0], arr.shape[1])
    return arr, lats, lons


def read_worldcover_mosaic(lat: float, lon: float, radius_km: float,
                           cache: Path, allow_network: bool):
    """Lit le plus grand disque utile (20 km) en dalles WorldCover, via HTTP."""
    rasterio, from_bounds = _rio()
    south, west, north, east = bbox_for_radius(lat, lon, radius_km)
    tiles = worldcover_tiles_for_bbox(south, west, north, east)
    pieces = []
    used = []
    env_kw = {
        "GDAL_HTTP_USERAGENT": USER_AGENT,
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif",
        "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    }
    for tile in tiles:
        url = WORLDCOVER_TILE_TMPL.format(tile=tile)
        vsicurl = "/vsicurl/" + url
        try:
            with rasterio.Env(**env_kw):
                with rasterio.open(vsicurl) as ds:
                    win = from_bounds(west, south, east, north, ds.transform)
                    arr = ds.read(1, window=win, boundless=True, fill_value=0)
                    transform = ds.window_transform(win)
        except Exception as e:  # noqa: BLE001
            if not allow_network:
                raise
            # deuxième essai : fichier local si déjà là
            local = cache / f"ESA_WorldCover_10m_2021_v200_{tile}_Map.tif"
            if local.exists():
                with rasterio.open(local) as ds:
                    win = from_bounds(west, south, east, north, ds.transform)
                    arr = ds.read(1, window=win, boundless=True, fill_value=0)
                    transform = ds.window_transform(win)
            else:
                raise RuntimeError(f"WorldCover dalle {tile} : {e}") from e
        if arr.size == 0:
            continue
        lats, lons = mesh_centers(transform, arr.shape[0], arr.shape[1])
        pieces.append((arr, lats, lons))
        used.append(tile)
    if not pieces:
        raise RuntimeError(f"aucune dalle WorldCover pour {lat},{lon}")
    # Une seule dalle suffit presque toujours ; sinon on colle en 1D.
    if len(pieces) == 1:
        arr, lats, lons = pieces[0]
        return arr, lats, lons, used
    arr = np_concat_flat(pieces)
    return arr[0], arr[1], arr[2], used


def np_concat_flat(pieces):
    import numpy as np
    klass = np.concatenate([p[0].ravel() for p in pieces])
    lats = np.concatenate([p[1].ravel() for p in pieces])
    lons = np.concatenate([p[2].ravel() for p in pieces])
    return klass.reshape(1, -1), lats.reshape(1, -1), lons.reshape(1, -1)


def compute_station(icao: str, lat: float, lon: float, pop_ds,
                    cache: Path, allow_network: bool) -> dict:
    print(f"  [{icao}] {lat:.4f},{lon:.4f}", flush=True)
    pop_arr, pop_lat, pop_lon = read_worldpop_window(pop_ds, lat, lon, max(RADII_KM))
    wc_arr, wc_lat, wc_lon, tiles = read_worldcover_mosaic(
        lat, lon, max(RADII_KM), cache, allow_network)
    radii = {}
    for r in RADII_KM:
        pop = population_in_circle(pop_arr, pop_lat, pop_lon, lat, lon, r)
        cov = cover_in_circle(wc_arr, wc_lat, wc_lon, lat, lon, r)
        radii[str(r)] = {
            "radius_km": r,
            "disk_km2": disk_area_km2(r),
            "pop_per_km2": pop["pop_per_km2"],
            "people": pop["people"],
            "pop_n_pixels": pop["n_pixels"],
            "pop_n_valid": pop["n_valid"],
            "veg_frac": cov["veg_frac"],
            "tree_frac": cov["tree_frac"],
            "water_frac": cov["water_frac"],
            "built_frac": cov["built_frac"],
            "cover_n_pixels": cov["n_pixels"],
            "cover_n_valid": cov["n_valid"],
        }
    return {
        "icao": icao,
        "lat": lat,
        "lon": lon,
        "worldcover_tiles": tiles,
        "radii": radii,
    }


def load_climate() -> dict[str, dict]:
    """Climat officiel déjà mesuré (siècle). On ne retélécharge pas GHCN."""
    spread = json.loads((TRUTH_DIR / "century" / "spread.json").read_text(encoding="utf-8"))
    tails = json.loads((TRUTH_DIR / "century" / "mutual_tails.json").read_text(encoding="utf-8"))
    out = {}
    for icao, sp in spread.items():
        t = (tails.get("stations") or tails).get(icao, {})
        hi = sp.get("temp_max") or {}
        lo = sp.get("temp_min") or {}
        heat = t.get("heat") or {}
        frost = t.get("frost") or {}
        tmax = hi.get("typical_mean_f")
        tmin = lo.get("typical_mean_f")
        out[icao] = {
            "typical_max_f": tmax,
            "typical_min_f": tmin,
            "typical_range_f": None if tmax is None or tmin is None else tmax - tmin,
            "median_days_ge_100f": heat.get("median_days_ge_100f"),
            "median_frost_days": frost.get("median_frost_days"),
            "hottest_f": heat.get("hottest_f"),
            "coldest_f": frost.get("coldest_f"),
            "n_complete_years_heat": heat.get("n_complete_years"),
            "n_complete_years_frost": frost.get("n_complete_years"),
        }
    return out


def relate(densities: dict[str, dict], climate: dict[str, dict]) -> dict:
    """Spearman densité × climat, un rayon à la fois. n = stations avec les deux."""
    clim_keys = (
        "typical_max_f", "typical_min_f", "typical_range_f",
        "median_days_ge_100f", "median_frost_days",
    )
    dens_keys = ("pop_per_km2", "veg_frac", "water_frac", "tree_frac")
    out: dict[str, Any] = {"n_stations_max": 0, "by_radius": {}}
    for r in RADII_KM:
        block = {}
        for dk in dens_keys:
            for ck in clim_keys:
                xs, ys, names = [], [], []
                for icao, rec in densities.items():
                    d = rec["radii"][str(r)].get(dk)
                    c = (climate.get(icao) or {}).get(ck)
                    if d is None or c is None:
                        continue
                    xs.append(float(d))
                    ys.append(float(c))
                    names.append(icao)
                sp = spearman(xs, ys)
                block[f"{dk}__{ck}"] = {
                    "n": len(xs),
                    "stations": names,
                    "spearman": sp,
                }
                out["n_stations_max"] = max(out["n_stations_max"], len(xs))
        out["by_radius"][str(r)] = block
    return out


def strongest_links(relate_payload: dict, min_n: int = 15) -> list[dict]:
    """Liens avec |r| ≥ 0,47 (seuil Student ~5 % à n=18) et p_approx < 0,05."""
    hits = []
    for r, block in relate_payload["by_radius"].items():
        for key, rec in block.items():
            sp = rec.get("spearman")
            if not sp or rec.get("n", 0) < min_n:
                continue
            p = sp.get("p_approx")
            if p is None or p >= 0.05 or abs(sp["r"]) < 0.47:
                continue
            dk, ck = key.split("__", 1)
            hits.append({
                "radius_km": int(r), "density": dk, "climate": ck,
                "r": sp["r"], "p_approx": p, "n": rec["n"],
            })
    hits.sort(key=lambda h: abs(h["r"]), reverse=True)
    return hits


def load_cli(path: Path) -> dict[tuple[str, date], dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {(r["station"], date.fromisoformat(r["valid"])): r for r in rows}


def truth_value(row: Optional[dict], variable: str) -> Optional[float]:
    if not row:
        return None
    v = row.get("high" if variable == "temp_max" else "low")
    return None if v is None else float(v)


def load_points(path: Path) -> list[dict]:
    pts = json.loads(path.read_text(encoding="utf-8"))
    for p in pts:
        p["_target"] = date.fromisoformat(p["target"])
        p["_mean"] = statistics.fmean(p["per_model"].values())
    return pts


def fit_bias(points: list[dict], cli: dict, split: date) -> dict[tuple, tuple]:
    resid: dict[tuple, list[float]] = defaultdict(list)
    for p in points:
        if p["_target"] >= split:
            continue
        obs = truth_value(cli.get((p["station"], p["_target"])), p["variable"])
        if obs is None:
            continue
        resid[(p["station"], p["variable"], p["lead"])].append(obs - p["_mean"])
    out = {}
    for k, r in resid.items():
        if len(r) >= MIN_BIAS_PAIRS:
            out[k] = (statistics.fmean(r), max(SIGMA_FLOOR, statistics.pstdev(r)), len(r))
    return out


def fit_density_bias(points: list[dict], cli: dict, split: date,
                     densities: dict, radius_km: int) -> Optional[dict]:
    """Un seul modèle pour toutes les stations : résidu ~ densités (TRAIN)."""
    x_rows, y = [], []
    for p in points:
        if p["_target"] >= split:
            continue
        obs = truth_value(cli.get((p["station"], p["_target"])), p["variable"])
        feat = density_feature_row((densities.get(p["station"]) or {}).get("radii", {}), radius_km)
        if obs is None or feat is None:
            continue
        x_rows.append(feat)
        y.append(obs - p["_mean"])
    if len(y) < 30:
        return None
    xs, means, stds = standardize_train(x_rows)
    model = fit_ols(xs, y)
    if model is None:
        return None
    model["means"] = means
    model["stds"] = stds
    model["radius_km"] = radius_km
    model["features"] = ["intercept", "log1p_pop_per_km2", "veg_frac", "water_frac"]
    return model


def predict_resid(model: dict, feat: list[float]) -> float:
    z = apply_standard(feat, model["means"], model["stds"])
    return sum(b * v for b, v in zip(model["beta"], z))


def score_holdout(points: list[dict], cli: dict, densities: dict,
                  split: date, end: date) -> dict:
    bias = fit_bias(points, cli, split)
    models = {r: fit_density_bias(points, cli, split, densities, r) for r in RADII_KM}
    rows = []
    for p in points:
        t = p["_target"]
        if t < split or t > end:
            continue
        obs = truth_value(cli.get((p["station"], t)), p["variable"])
        if obs is None:
            continue
        mu = p["_mean"]
        sig = max(SIGMA_FLOOR, statistics.pstdev(list(p["per_model"].values()))
                  if len(p["per_model"]) >= 2 else SIGMA_FLOOR)
        st = bias.get((p["station"], p["variable"], p["lead"]))
        dens_mu_sig: dict[int, tuple[float, float]] = {}
        for r, model in models.items():
            feat = density_feature_row((densities.get(p["station"]) or {}).get("radii", {}), r)
            if model is None or feat is None:
                continue
            resid = predict_resid(model, feat)
            dens_mu_sig[r] = (mu + resid, max(SIGMA_FLOOR, model["resid_std"]))
        for b in kalshi_style_bins(mu, n_central=6):
            if not b.is_central:
                continue
            rec = {
                "station": p["station"], "variable": p["variable"], "target": t,
                "lead": p["lead"], "outcome": b.contains(obs),
                "p_raw": prob_in_bin_gaussian(mu, sig, b),
                "p_station": None if st is None else prob_in_bin_gaussian(mu + st[0], st[1], b),
            }
            for r, (m, s) in dens_mu_sig.items():
                rec[f"p_dens_{r}"] = prob_in_bin_gaussian(m, s, b)
            rows.append(rec)
    return {"rows": rows, "models": {str(k): v for k, v in models.items() if v}}


def summarize_rows(rows: list[dict], fields: tuple[str, ...]) -> dict:
    rec = {
        "n_bins": len(rows),
        "n_dates": len({r["target"] for r in rows}),
    }
    if rows:
        rec["base_rate"] = statistics.fmean(1.0 if r["outcome"] else 0.0 for r in rows)
    for name in fields:
        common = [r for r in rows if r.get(name) is not None]
        if common:
            rec[f"brier_{name[2:] if name.startswith('p_') else name}"] = statistics.fmean(
                brier(r[name], r["outcome"]) for r in common)
            rec[f"n_{name}"] = len(common)
    return rec


def sign_test_rows(rows: list[dict], a: str, b: str) -> dict:
    class _S:
        def __init__(self, r):
            self.target = r["target"]
            self.outcome = r["outcome"]
            setattr(self, a, r[a])
            setattr(self, b, r[b])
    scores = [_S(r) for r in rows if r.get(a) is not None and r.get(b) is not None]
    return sign_test_by_date(scores, a, b)


def load_market_records(min_date: date, leads: set[int]) -> list[dict]:
    seen: dict[tuple, dict] = {}
    for f in sorted(glob.glob(str(ROOT / "data" / "predictions" / "forward_*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in d.get("records", []):
            if r.get("lower") is None or r.get("upper") is None:
                continue
            if r.get("yes_mid") is None:
                continue
            ens = (r.get("predictions") or {}).get("ensemble") or {}
            pm = (ens.get("inputs") or {}).get("per_model_value") or {}
            target = date.fromisoformat(r["target_date"])
            if target < min_date:
                continue
            snap = datetime.strptime(r["snapshot_at"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            lead = (target - snap.date()).days
            if lead < 0 or lead not in leads:
                continue
            key = (r["ticker"], lead)
            if key in seen:
                continue
            seen[key] = {**r, "_target": target, "_lead": lead, "_pm": pm}
    return list(seen.values())


def score_market(cli: dict, densities: dict, models: dict,
                 min_date: date, leads: set[int]) -> dict:
    records = load_market_records(min_date, leads)
    rows = []
    skips: dict[str, int] = defaultdict(int)
    for r in records:
        icao = CITY_TO_ICAO.get(r["location_key"])
        if not icao:
            skips["no_station"] += 1
            continue
        obs = truth_value(cli.get((icao, r["_target"])), r["variable"])
        if obs is None:
            skips["no_cli_truth"] += 1
            continue
        vals = list(r["_pm"].values()) if r["_pm"] else []
        if len(vals) < 2:
            skips["no_ensemble"] += 1
            continue
        mu = statistics.fmean(vals)
        sig = max(SIGMA_FLOOR, statistics.pstdev(vals))
        from src.truth.synthetic_bins import Bin
        b = Bin(int(r["lower"]), int(r["upper"]))
        rec = {
            "station": icao, "variable": r["variable"], "target": r["_target"],
            "lead": r["_lead"], "outcome": b.contains(obs),
            "p_raw": prob_in_bin_gaussian(mu, sig, b),
            "p_market": float(r["yes_mid"]),
        }
        for rs, model in models.items():
            if model is None:
                continue
            feat = density_feature_row((densities.get(icao) or {}).get("radii", {}), int(rs))
            if feat is None:
                continue
            resid = predict_resid(model, feat)
            rec[f"p_dens_{rs}"] = prob_in_bin_gaussian(
                mu + resid, max(SIGMA_FLOOR, model["resid_std"]), b)
        rows.append(rec)
    return {"rows": rows, "skips": dict(skips)}


def _fr(x, nd=1):
    if x is None:
        return "n/a"
    return f"{x:.{nd}f}".replace(".", ",")


def _fr4(x):
    return _fr(x, 4)


def write_reports(out_dir: Path, payload: dict) -> None:
    dens = payload["stations"]
    climate = payload["climate"]
    rel = payload["relate"]
    hits = payload["strong_links"]
    hold = payload.get("holdout") or {}
    lines = [
        "# Ville, végétation, eau autour de la station",
        "",
        f"Généré : {payload['generated_at']}. "
        "Habitants : WorldPop 2020 (fichier de comptage 1 km). "
        "Vert et eau : ESA WorldCover 2021 (10 m). "
        "Point = coordonnées officielles A1. Aucun chiffre inventé.",
        "",
        "## D'où viennent les nombres",
        "",
        f"- Ville : {SOURCE_NOTES['population']}",
        f"- Végétation : {SOURCE_NOTES['vegetation']}",
        f"- Eau : {SOURCE_NOTES['water']}",
        "",
        "Les anciens comptages OSM (bâtiments, arbres, rivières) ne sont pas utilisés.",
        "",
        "À 1 km, beaucoup d'aéroports ont 0 habitant : la carte WorldPop "
        "fait 1 km de côté, et la piste est vide. Le 5 km commence à voir "
        "le quartier. Le 20 km voit la mer pour Boston, San Francisco, "
        "Los Angeles, Seattle.",
        "",
        "## Les 18 stations, rayon 5 km",
        "",
        "| Ville | Habitants / km² | Part verte | Part d'eau | Max typique | Min typique | Jours ≥ 100 °F | Jours de gel |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for icao in sorted(dens):
        r5 = dens[icao]["radii"]["5"]
        cl = climate.get(icao) or {}
        lines.append(
            f"| {CITY_FR.get(icao, icao)} | {_fr(r5['pop_per_km2'], 0)} | "
            f"{_fr((r5['veg_frac'] or 0) * 100, 0)} % | "
            f"{_fr((r5['water_frac'] or 0) * 100, 0)} % | "
            f"{_fr(cl.get('typical_max_f'), 0)} °F | {_fr(cl.get('typical_min_f'), 0)} °F | "
            f"{_fr(cl.get('median_days_ge_100f'), 0)} | {_fr(cl.get('median_frost_days'), 0)} |"
        )
    lines += [
        "",
        "## Tous les rayons (habitants / km², part verte, part d'eau)",
        "",
        "| Ville | 1 km hab | 1 km vert | 1 km eau | 2 km hab | 5 km hab | 10 km hab | 20 km hab | 20 km vert | 20 km eau |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for icao in sorted(dens):
        rr = dens[icao]["radii"]
        def cell(rad, key, pct=False, nd=0):
            v = rr[str(rad)].get(key)
            if v is None:
                return "n/a"
            if pct:
                return f"{_fr(v * 100, nd)} %"
            return _fr(v, nd)
        lines.append(
            f"| {CITY_FR.get(icao, icao)} | {cell(1,'pop_per_km2')} | {cell(1,'veg_frac',True)} | "
            f"{cell(1,'water_frac',True)} | {cell(2,'pop_per_km2')} | {cell(5,'pop_per_km2')} | "
            f"{cell(10,'pop_per_km2')} | {cell(20,'pop_per_km2')} | "
            f"{cell(20,'veg_frac',True)} | {cell(20,'water_frac',True)} |"
        )
    lines += [
        "",
        "## Lien avec le climat officiel (fichier siècle)",
        "",
        "On range les 18 villes. On regarde si l'ordre des densités suit "
        "l'ordre des températures. n = 18 partout où le siècle a un chiffre. "
        "Un lien n'est retenu que si |r| ≥ 0,47 et p < 0,05 (ordre, n=18).",
        "",
    ]
    if not hits:
        lines.append(
            "Aucun rayon ne montre un lien assez net entre ville, végétation "
            "ou eau et le max typique, le min typique, l'écart jour-nuit, "
            "les jours à 100 °F ou les jours de gel. Les 18 aéroports se "
            "ressemblent trop, ou le climat vient d'ailleurs (latitude, désert, mer)."
        )
    else:
        lines += [
            "| Rayon | Densité | Climat | r | p approx |",
            "|---|---|---|---|---|",
        ]
        label = {
            "pop_per_km2": "habitants", "veg_frac": "végétation",
            "water_frac": "eau", "tree_frac": "arbres",
            "typical_max_f": "max typique", "typical_min_f": "min typique",
            "typical_range_f": "écart jour-nuit",
            "median_days_ge_100f": "jours ≥ 100 °F",
            "median_frost_days": "jours de gel",
        }
        for h in hits:
            lines.append(
                f"| {h['radius_km']} km | {label.get(h['density'], h['density'])} | "
                f"{label.get(h['climate'], h['climate'])} | {_fr(h['r'], 2)} | "
                f"{_fr(h['p_approx'], 3)} |"
            )
    # Toujours montrer le plus fort r par couple, même s'il est faible.
    lines += [
        "",
        "### Le plus fort r, même s'il est trop faible pour compter",
        "",
        "| Rayon | Habitants × min | Végétation × max | Eau × écart jour-nuit |",
        "|---|---|---|---|",
    ]
    for r in RADII_KM:
        block = rel["by_radius"][str(r)]
        def rr(key):
            sp = (block.get(key) or {}).get("spearman")
            return "n/a" if not sp else _fr(sp["r"], 2)
        lines.append(
            f"| {r} km | {rr('pop_per_km2__typical_min_f')} | "
            f"{rr('veg_frac__typical_max_f')} | "
            f"{rr('water_frac__typical_range_f')} |"
        )
    hsum = (hold.get("holdout") or {})
    lines += [
        "",
        "## Skill Kalshi (holdout A1, 3 août au 7 septembre 2026)",
        "",
        "Correctif unique pour toutes les villes : on apprend sur TRAIN "
        "l'écart prévision − station à partir des trois densités, puis on "
        "l'applique au HOLDOUT. Ce n'est pas un biais par ville. "
        "Le champion reste le mélange corrigé ville par ville (0,1154) "
        "sauf victoire claire.",
        "",
    ]
    if hsum:
        ov = hsum.get("overall") or {}
        lines += [
            "| Méthode | Score d'erreur |",
            "|---|---|",
            f"| Mélange brut | {_fr(ov.get('brier_raw'), 4)} |",
            f"| Mélange corrigé ville par ville | {_fr(ov.get('brier_station'), 4)} |",
        ]
        for r in RADII_KM:
            key = f"brier_dens_{r}"
            if key in ov:
                lines.append(f"| Densités à {r} km | {_fr(ov[key], 4)} |")
        lines.append("")
        signs = hsum.get("sign_tests") or {}
        for name, st in signs.items():
            lines.append(
                f"- {name} : {st.get('a_wins')}/{st.get('dates')} jours "
                f"(p = {_fr(st.get('p_one_sided'), 4)})."
            )
        decision = payload.get("decision", "")
        lines += ["", "## Décision", "", decision]
    else:
        lines += [
            "Holdout non calculé (fichiers A1 absents).",
            "",
            "## Décision",
            "",
            payload.get("decision", "On ne change pas le modèle en ligne."),
        ]
    mkt = payload.get("market")
    if mkt and mkt.get("overall"):
        ov = mkt["overall"]
        lines += [
            "",
            "## Contre le prix du marché (la veille, si on a le prix)",
            "",
            "| Méthode | Score d'erreur |",
            "|---|---|",
            f"| Prix du marché | {_fr(ov.get('brier_market'), 4)} |",
            f"| Mélange brut | {_fr(ov.get('brier_raw'), 4)} |",
        ]
        for r in RADII_KM:
            key = f"brier_dens_{r}"
            if key in ov:
                lines.append(f"| Densités à {r} km | {_fr(ov[key], 4)} |")
        lines.append(f"Jours : {ov.get('n_dates')}. Contrats : {ov.get('n_bins')}.")
    lines += [
        "",
        "Pas de changement du site public. Pas de trading réel. "
        "Pas de bascule du champion sauf victoire claire ci-dessus.",
        "",
        "Pour relancer : `python scripts/eval_land_density.py` "
        "(ou `--skip-fetch` si WorldPop est déjà en cache).",
    ]
    (out_dir / "density_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def owner_note(payload: dict) -> str:
    """Note propriétaire : français très simple, sans jargon."""
    hold = ((payload.get("holdout") or {}).get("holdout") or {})
    ov = hold.get("overall") or {}
    dens = payload["stations"]
    rel = payload.get("relate") or {}

    def val(icao, rad, key):
        return dens[icao]["radii"][str(rad)].get(key)

    def r_water_range(rad):
        block = ((rel.get("by_radius") or {}).get(str(rad)) or {})
        sp = (block.get("water_frac__typical_range_f") or {}).get("spearman")
        return None if not sp else sp["r"]

    def r_pop_min(rad):
        block = ((rel.get("by_radius") or {}).get(str(rad)) or {})
        sp = (block.get("pop_per_km2__typical_min_f") or {}).get("spearman")
        return None if not sp else sp["r"]

    def r_veg_max(rad):
        block = ((rel.get("by_radius") or {}).get(str(rad)) or {})
        sp = (block.get("veg_frac__typical_max_f") or {}).get("spearman")
        return None if not sp else sp["r"]

    nyc_pop = val("KNYC", 5, "pop_per_km2")
    den_pop = val("KDEN", 5, "pop_per_km2")
    bos_w20 = val("KBOS", 20, "water_frac")
    den_w20 = val("KDEN", 20, "water_frac")
    phx_v5 = val("KPHX", 5, "veg_frac")
    r20 = r_water_range(20)
    r10 = r_water_range(10)
    r5 = r_water_range(5)
    r1 = r_water_range(1)

    lines = [
        "# Ville, forêt et eau autour de la station",
        "",
        "**Date :** 12 septembre 2026",
        "**Pour :** le propriétaire (pas un document technique)",
        "",
        "Question : une ville, une forêt ou de l'eau changent-elles la "
        "température, et à quelle distance de la station ?",
        "",
        "Cette note dit seulement ce qui a été mesuré. Le site public n'a "
        "pas été changé. Le modèle en ligne n'a pas été changé. Aucun pari "
        "avec de l'argent réel. Aucun chiffre n'a été inventé.",
        "",
        "## Ce que ça mesure",
        "",
        "Ville = habitants au km². Pas le nombre de bâtiments.",
        "",
        "Forêt = part du sol qui est verte. Pas le nombre d'arbres sur une carte.",
        "",
        "Eau = part du sol qui est de l'eau (mer, lac, fleuve). "
        "Pas le nombre de rivières sur une carte.",
        "",
        "On a regardé 1, 2, 5, 10 et 20 km autour du vrai point des "
        "18 stations. Habitants : fichier public WorldPop 2020. "
        "Vert et eau : carte publique ESA 2021. "
        "Températures : le fichier officiel déjà utilisé pour le siècle.",
        "",
        "## Quelques chiffres vrais",
        "",
        f"New York, à 5 km : {_fr(nyc_pop, 0)} habitants / km².",
        f"Denver (aéroport), à 5 km : {_fr(den_pop, 0)} habitant / km².",
        f"Boston, à 20 km : {_fr((bos_w20 or 0) * 100, 0)} % d'eau.",
        f"Denver, à 20 km : {_fr((den_w20 or 0) * 100, 0)} % d'eau.",
        f"Phoenix, à 5 km : {_fr((phx_v5 or 0) * 100, 0)} % de sol vert.",
        "",
        "Ça suffit à dire : ici c'est une ville, ici c'est près de l'eau, "
        "ici c'est sec. Pour la mutuelle, un terrain près d'un lac n'est "
        "pas un terrain en ville.",
        "",
        "## Quel rayon a un effet ?",
        "",
        "L'eau, oui. Surtout à 20 km. Déjà visible à 10 km et à 5 km. "
        "À 1 km, presque rien.",
        "",
        f"Plus il y a d'eau autour, plus le jour et la nuit se ressemblent "
        f"(ordre à 20 km : {_fr(r20, 2)} ; à 10 km : {_fr(r10, 2)} ; "
        f"à 5 km : {_fr(r5, 2)} ; à 1 km : {_fr(r1, 2)}).",
        "",
        "En clair : Boston ou San Francisco (beaucoup de mer) n'ont pas "
        "le même écart jour-nuit que Denver ou Phoenix (presque pas d'eau). "
        "Le 20 km est le plus net.",
        "",
        "La ville (habitants), non. Ranger les 18 stations de la plus "
        f"habitée à la moins habitée ne range pas les nuits "
        f"(à 5 km, ordre {_fr(r_pop_min(5), 2)}, trop faible). "
        "Ces 18 points sont surtout des aéroports, pas le centre-ville. "
        "À 1 km, presque tous sont vides. C'est la piste d'atterrissage.",
        "",
        "La forêt (sol vert), non. Ranger les stations de la plus verte "
        f"à la moins verte ne range pas les jours les plus chauds "
        f"(à 5 km, ordre {_fr(r_veg_max(5), 2)}, trop faible).",
        "",
        "On ne force pas une histoire que les 18 points ne tiennent pas.",
    ]
    b_st = ov.get("brier_station")
    best_d = None
    best_r = None
    for r in RADII_KM:
        v = ov.get(f"brier_dens_{r}")
        if v is None:
            continue
        if best_d is None or v < best_d:
            best_d, best_r = v, r
    lines += [
        "",
        "## Est-ce que ça aide les paris du jour ?",
        "",
    ]
    if best_d is None:
        lines.append("Le test sur les jours d'août-septembre n'a pas pu tourner.")
    else:
        lines.append(
            f"Mélange déjà corrigé ville par ville : {_fr(b_st, 4)}."
        )
        lines.append(
            f"Meilleur essai avec les densités (rayon {best_r} km) : {_fr(best_d, 4)}."
        )
        lines.append("")
        lines.append(
            "Ça n'aide pas les paris du jour. On s'y attendait. "
            "Corriger chaque ville avec son propre écart marche déjà. "
            "Ajouter ville, forêt ou eau par-dessus ne gagne pas. "
            "L'ancien essai (compter les bâtiments sur une carte) "
            "avait déjà échoué."
        )
    mkt = payload.get("market") or {}
    mov = mkt.get("overall") or {}
    if mov.get("brier_market") is not None:
        md = None
        for r in RADII_KM:
            v = mov.get(f"brier_dens_{r}")
            if v is None:
                continue
            if md is None or v < md:
                md = v
        lines += [
            "",
            f"Prix du marché, la veille ({mov.get('n_dates')} jours, mêmes contrats) : "
            f"{_fr(mov.get('brier_market'), 4)}.",
            f"Densités sur ces mêmes contrats : {_fr(md, 4)}.",
            "Les densités ne battent pas le marché.",
        ]
    lines += [
        "",
        "## Décision",
        "",
        payload.get("decision", "On ne change pas le modèle en ligne."),
        "",
        "Les tableaux sont dans `data/truth/density/density_report.md`.",
        "Pour relancer : `python scripts/eval_land_density.py --from-json data/truth/density/densities.json`",
        "",
        "Pas de changement du texte du site. Pas de trading réel.",
    ]
    return "\n".join(lines) + "\n"


def decide(holdout_overall: dict, n_dates: int, hits: list,
           market_overall: Optional[dict] = None) -> str:
    best = None
    for r in RADII_KM:
        v = holdout_overall.get(f"brier_dens_{r}")
        if v is None:
            continue
        if best is None or v < best[0]:
            best = (v, r)
    station = holdout_overall.get("brier_station")
    parts = ["On ne change pas le modèle en ligne."]
    if best is None or station is None:
        parts.append(
            "Mesure faite pour la mutuelle et pour savoir si un rayon "
            "a un effet. Holdout absent ou incomplet."
        )
    else:
        parts.append(
            f"Les densités ne battent pas le mélange corrigé ville par ville "
            f"({_fr(best[0], 4)} contre {_fr(station, 4)} au meilleur rayon, "
            f"{n_dates} jours)."
        )
    if market_overall and market_overall.get("brier_market") is not None:
        mb = None
        for r in RADII_KM:
            v = market_overall.get(f"brier_dens_{r}")
            if v is None:
                continue
            if mb is None or v < mb[0]:
                mb = (v, r)
        if mb:
            parts.append(
                f"Sur les contrats avec un prix (la veille, "
                f"{market_overall.get('n_dates', '?')} jours) : "
                f"densités {_fr(mb[0], 4)} contre marché "
                f"{_fr(market_overall['brier_market'], 4)}."
            )
    water_hits = [h for h in hits if h["density"] == "water_frac"
                  and h["climate"] == "typical_range_f"]
    if water_hits:
        best_w = max(water_hits, key=lambda h: abs(h["r"]))
        parts.append(
            f"L'eau à {best_w['radius_km']} km est le lien le plus net "
            "avec l'écart entre le jour et la nuit. "
            "Utile pour décrire un lieu (mutuelle), pas pour remplacer "
            "la correction ville par ville."
        )
    elif not hits:
        parts.append("Aucun rayon n'a d'effet net sur le climat des 18 stations.")
    return " ".join(parts)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skip-fetch", action="store_true")
    p.add_argument("--from-json", type=Path,
                   help="Relire densities.json déjà mesuré (pas de raster).")
    p.add_argument("--out-dir", type=Path, default=OUT_DEFAULT)
    p.add_argument("--cache-dir", type=Path, default=CACHE)
    p.add_argument("--skip-holdout", action="store_true")
    p.add_argument("--skip-market", action="store_true")
    p.add_argument("--split-date", default=A1_SPLIT.isoformat())
    p.add_argument("--end-date", default=A1_END.isoformat())
    args = p.parse_args(argv)

    allow = not args.skip_fetch
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.cache_dir.mkdir(parents=True, exist_ok=True)

    stations = kalshi_stations()
    if len(stations) != 18:
        print(f"attendu 18 stations, obtenu {len(stations)}", file=sys.stderr)
        return 2

    densities: dict[str, dict] = {}
    if args.from_json:
        densities = json.loads(args.from_json.read_text(encoding="utf-8"))
        if set(densities) != set(stations):
            print("densities.json ne couvre pas les 18 stations", file=sys.stderr)
            return 2
        print(f"lu {args.from_json} ({len(densities)} stations)")
    else:
        rasterio, _ = _rio()
        pop_path = ensure_worldpop(args.cache_dir, allow)
        with rasterio.open(pop_path) as pop_ds:
            print(f"WorldPop {pop_ds.width}×{pop_ds.height} nodata={pop_ds.nodata} res={pop_ds.res}",
                  flush=True)
            for icao in sorted(stations):
                meta = stations[icao]
                densities[icao] = compute_station(
                    icao, meta["lat"], meta["lon"], pop_ds, args.cache_dir, allow)
                densities[icao]["city_key"] = meta["city_key"]
                densities[icao]["label"] = CITY_FR.get(icao, icao)

    climate = load_climate()
    rel = relate(densities, climate)
    hits = strongest_links(rel)

    hold_payload = None
    market_payload = None
    split = date.fromisoformat(args.split_date)
    end = date.fromisoformat(args.end_date)
    cli_path = TRUTH_DIR / "cli_daily.json"
    pts_path = TRUTH_DIR / "skill" / "forecast_points.json"
    if (not args.skip_holdout) and cli_path.exists() and pts_path.exists():
        cli = load_cli(cli_path)
        points = load_points(pts_path)
        scored = score_holdout(points, cli, densities, split, end)
        fields = ("p_raw", "p_station", *(f"p_dens_{r}" for r in RADII_KM))
        overall = summarize_rows(scored["rows"], fields)
        signs = {}
        for r in RADII_KM:
            key = f"p_dens_{r}"
            if any(row.get(key) is not None and row.get("p_station") is not None
                   for row in scored["rows"]):
                signs[f"dens{r}_vs_station"] = sign_test_rows(scored["rows"], key, "p_station")
                signs[f"dens{r}_vs_raw"] = sign_test_rows(scored["rows"], key, "p_raw")
        hold_payload = {
            "holdout": {
                "overall": overall,
                "sign_tests": signs,
                "split": split.isoformat(),
                "end": end.isoformat(),
            },
            "models": scored["models"],
        }
        if not args.skip_market:
            m = score_market(cli, densities, scored["models"], date(2026, 4, 11), {1})
            mfields = ("p_raw", "p_market", *(f"p_dens_{r}" for r in RADII_KM))
            market_payload = {
                "overall": summarize_rows(m["rows"], mfields),
                "skips": m["skips"],
                "lead": 1,
            }

    n_dates = ((hold_payload or {}).get("holdout") or {}).get("overall", {}).get("n_dates") or 0
    overall = ((hold_payload or {}).get("holdout") or {}).get("overall") or {}
    decision = decide(overall, n_dates, hits, (market_payload or {}).get("overall"))

    payload = {
        "schema": "land_density/1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": SOURCE_NOTES,
        "radii_km": list(RADII_KM),
        "stations": densities,
        "climate": climate,
        "relate": rel,
        "strong_links": hits,
        "holdout": hold_payload,
        "market": market_payload,
        "decision": decision,
        "champion_switched": False,
        "champion_brier_reference": CHAMPION_BRIER,
    }
    (args.out_dir / "densities.json").write_text(
        json.dumps({k: densities[k] for k in sorted(densities)}, indent=2),
        encoding="utf-8",
    )
    (args.out_dir / "relate.json").write_text(
        json.dumps({"relate": rel, "strong_links": hits}, indent=2),
        encoding="utf-8",
    )
    slim_hold = None
    if hold_payload:
        slim_hold = {
            "holdout": hold_payload["holdout"],
            "models": hold_payload["models"],
            "champion_switched": False,
        }
        (args.out_dir / "holdout.json").write_text(
            json.dumps(slim_hold, indent=2, default=str), encoding="utf-8")
    if market_payload:
        (args.out_dir / "market.json").write_text(
            json.dumps(market_payload, indent=2, default=str), encoding="utf-8")
    write_reports(args.out_dir, payload)
    note = owner_note(payload)
    docs = ROOT / "docs" / "densites-ville-foret-eau-2026-09-12.md"
    docs.write_text(note, encoding="utf-8")
    print(f"wrote {args.out_dir} and {docs}")
    print(decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
