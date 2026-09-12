"""Tests hors réseau : disque, dalles, rang, script."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from src.truth.iem_cli import kalshi_stations
from src.truth.land_density import (
    RADII_KM, VEG_CLASSES, WATER_CLASSES, WORLDPOP_NODATA,
    apply_standard, bbox_for_radius, cell_area_km2, circle_mask,
    cover_in_circle, density_feature_row, disk_area_km2, fit_ols,
    haversine_km, population_in_circle, ranks, spearman,
    standardize_train, tile_sw_corner, worldcover_tile_id,
    worldcover_tiles_for_bbox,
)


def test_eighteen_official_stations():
    st = kalshi_stations()
    assert set(st) == {
        "KATL", "KAUS", "KBOS", "KMDW", "KDFW", "KDEN", "KHOU", "KLAS",
        "KLAX", "KMIA", "KMSP", "KNYC", "KPHL", "KPHX", "KSAT", "KSFO",
        "KSEA", "KDCA",
    }
    nyc = st["KNYC"]
    assert abs(nyc["lat"] - 40.7794) < 1e-6
    assert abs(nyc["lon"] - (-73.9692)) < 1e-6


def test_worldcover_tile_id_sw_corner():
    assert worldcover_tile_id(*tile_sw_corner(40.7794, -73.9692)) == "N39W075"
    assert worldcover_tile_id(*tile_sw_corner(25.7959, -80.2870)) == "N24W081"
    assert worldcover_tile_id(*tile_sw_corner(39.8561, -104.6737)) == "N39W105"
    assert worldcover_tile_id(*tile_sw_corner(47.4444, -122.3139)) == "N45W123"
    # pile sur une frontière : le coin sud-ouest est la dalle qui contient le point
    assert worldcover_tile_id(*tile_sw_corner(39.0, -75.0)) == "N39W075"


def test_tiles_for_bbox_picks_neighbors():
    # 20 km autour de DFW (32.90, -97.04) peut toucher N30 et N33
    south, west, north, east = bbox_for_radius(32.8998, -97.0403, 20)
    tiles = worldcover_tiles_for_bbox(south, west, north, east)
    assert "N30W099" in tiles
    assert len(tiles) >= 1


def test_cell_area_and_disk():
    # 30" × 30" à l'équateur ≈ 0,857 km² (111.32² × (1/120)²)
    a0 = cell_area_km2(0.0, 1.0 / 120.0, 1.0 / 120.0)
    assert 0.84 < a0 < 0.88
    a40 = cell_area_km2(40.0, 1.0 / 120.0, 1.0 / 120.0)
    assert a40 < a0
    assert abs(disk_area_km2(1) - np.pi) < 1e-9


def test_circle_mask_counts_center_only():
    lats = np.array([[40.0, 40.0], [40.05, 40.05]])
    lons = np.array([[-74.0, -73.9], [-74.0, -73.9]])
    m = circle_mask(40.0, -74.0, lats, lons, 1.0)
    assert m[0, 0]
    assert int(m.sum()) == 1


def test_population_density_is_people_over_disk():
    count = np.array([[100.0, WORLDPOP_NODATA], [0.0, 50.0]])
    lats = np.array([[0.0, 0.0], [0.01, 0.01]])
    lons = np.array([[0.0, 0.02], [0.0, 0.02]])
    # rayon assez grand pour les 4 pixels ; nodata ignoré
    out = population_in_circle(count, lats, lons, 0.0, 0.0, 5.0)
    assert out["people"] == 150.0
    assert out["n_valid"] == 3
    assert abs(out["pop_per_km2"] - 150.0 / disk_area_km2(5.0)) < 1e-9


def test_cover_fractions_ignore_nodata_zero():
    klass = np.array([[10, 80, 0], [50, 30, 10]])
    lats = np.zeros((2, 3))
    lons = np.zeros((2, 3))
    out = cover_in_circle(klass, lats, lons, 0.0, 0.0, 100.0)
    assert out["n_valid"] == 5
    assert out["water_frac"] == pytest.approx(1 / 5)
    assert out["veg_frac"] == pytest.approx(3 / 5)   # 10, 30, 10
    assert out["tree_frac"] == pytest.approx(2 / 5)
    assert out["built_frac"] == pytest.approx(1 / 5)
    assert 10 in VEG_CLASSES and 80 in WATER_CLASSES


def test_spearman_perfect_and_none():
    sp = spearman([1, 2, 3, 4, 5], [10, 20, 30, 40, 50])
    assert sp is not None and abs(sp["r"] - 1.0) < 1e-12
    assert spearman([1, 2], [3, 4]) is None
    # rangs ex aequo
    assert ranks([3, 1, 1, 2]) == [4.0, 1.5, 1.5, 3.0]


def test_ols_and_standardize_roundtrip():
    # y = 2 + 3 x
    rows = [[1.0, float(x)] for x in range(10)]
    y = [2.0 + 3.0 * x for x in range(10)]
    xs, means, stds = standardize_train(rows)
    model = fit_ols(xs, y)
    assert model is not None
    # x=4 → z = (4-mean)/std
    feat = apply_standard([1.0, 4.0], means, stds)
    pred = sum(b * v for b, v in zip(model["beta"], feat))
    assert abs(pred - 14.0) < 1e-6


def test_density_feature_row_needs_all_three():
    dens = {"5": {"pop_per_km2": 100.0, "veg_frac": 0.2, "water_frac": 0.1}}
    row = density_feature_row(dens, 5)
    assert row is not None and row[0] == 1.0
    assert density_feature_row({"5": {"pop_per_km2": 1.0, "veg_frac": None, "water_frac": 0}}, 5) is None


def test_haversine_nyc_to_itself_and_about_one_degree():
    assert haversine_km(40.78, -73.97, 40.78, -73.97) == 0.0
    # 1° de latitude ≈ 111 km
    d = haversine_km(40.0, -74.0, 41.0, -74.0)
    assert 110 < d < 112


def test_eval_script_offline(tmp_path, monkeypatch):
    import eval_land_density as eld

    stations = kalshi_stations()
    fake = {}
    for icao, meta in stations.items():
        radii = {}
        for r in RADII_KM:
            radii[str(r)] = {
                "radius_km": r, "disk_km2": disk_area_km2(r),
                "pop_per_km2": 1000.0 if icao == "KNYC" else 50.0,
                "people": 1000.0, "pop_n_pixels": 4, "pop_n_valid": 4,
                "veg_frac": 0.4, "tree_frac": 0.2,
                "water_frac": 0.3 if icao == "KMIA" else 0.01,
                "built_frac": 0.2, "cover_n_pixels": 100, "cover_n_valid": 100,
            }
        fake[icao] = {
            "icao": icao, "lat": meta["lat"], "lon": meta["lon"],
            "worldcover_tiles": ["N00E000"], "radii": radii,
            "city_key": meta["city_key"], "label": icao,
        }

    class _DS:
        width = 10
        height = 10
        nodata = -99999.0
        res = (0.008, 0.008)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(eld, "ensure_worldpop", lambda cache, allow: tmp_path / "wp.tif")
    monkeypatch.setattr(eld, "_rio", lambda: (type("R", (), {"open": staticmethod(lambda p: _DS())}), None))
    monkeypatch.setattr(
        eld, "compute_station",
        lambda icao, lat, lon, pop_ds, cache, allow: fake[icao],
    )
    century = tmp_path / "century"
    century.mkdir()
    spread = {
        icao: {
            "temp_max": {"typical_mean_f": 70.0 + i},
            "temp_min": {"typical_mean_f": 50.0 + i * 0.5},
        }
        for i, icao in enumerate(sorted(stations))
    }
    tails = {"stations": {
        icao: {
            "heat": {"median_days_ge_100f": float(i), "hottest_f": 100, "n_complete_years": 40},
            "frost": {"median_frost_days": 10.0, "coldest_f": 0, "n_complete_years": 40},
        }
        for i, icao in enumerate(sorted(stations))
    }}
    century.joinpath("spread.json").write_text(json.dumps(spread), encoding="utf-8")
    century.joinpath("mutual_tails.json").write_text(json.dumps(tails), encoding="utf-8")

    skill = tmp_path / "skill"
    skill.mkdir()
    cli = []
    pts = []
    for i, d in enumerate((date(2026, 8, 3), date(2026, 8, 4), date(2026, 8, 5))):
        cli.append({"station": "KNYC", "valid": d.isoformat(), "high": 82, "low": 65})
        pts.append({
            "station": "KNYC", "variable": "temp_max", "target": d.isoformat(),
            "lead": 1, "per_model": {"m1": 78.0, "m2": 80.0},
        })
    (tmp_path / "cli_daily.json").write_text(json.dumps(cli), encoding="utf-8")
    skill.joinpath("forecast_points.json").write_text(json.dumps(pts), encoding="utf-8")

    out = tmp_path / "density"
    docs = tmp_path / "docs"
    docs.mkdir()
    monkeypatch.setattr(eld, "TRUTH_DIR", tmp_path)
    monkeypatch.setattr(eld, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", [
        "eval_land_density.py", "--skip-fetch", "--skip-market",
        "--out-dir", str(out), "--cache-dir", str(tmp_path / "cache"),
        "--split-date", "2026-08-03", "--end-date", "2026-08-05",
    ])
    assert eld.main() == 0
    dens = json.loads((out / "densities.json").read_text(encoding="utf-8"))
    assert set(dens) == set(stations)
    assert dens["KNYC"]["radii"]["5"]["pop_per_km2"] == 1000.0
    report = (out / "density_report.md").read_text(encoding="utf-8")
    assert "New York" in report and "On ne change pas" in report
    note = (docs / "densites-ville-foret-eau-2026-09-12.md").read_text(encoding="utf-8")
    assert "propriétaire" in note
    hold = json.loads((out / "holdout.json").read_text(encoding="utf-8"))
    assert hold["champion_switched"] is False
