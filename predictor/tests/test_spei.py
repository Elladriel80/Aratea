"""Tests hors réseau : classes SPEI, polygones, comptes, script."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from src.truth.spei import (
    CATALOGUE_TRUTH, IPCC_MED_VERTICES, PHASE_B_DRY_THRESHOLD, TARGET_INDE,
    TARGET_MED, TARGET_US, SpeiClient, SpeiGrid, count_regions,
    coverage_for_mask, empty_region_row, extract_named_states,
    gee_catalog_excerpt, mask_from_rings, parse_ipcc_med_vertices,
    point_in_ring, regions_from_sources, wmo_class,
)

MINI_IPCC = """Continent,Surface,Name,Acronym,V1,V2,V3,V4
EUROPE-AFRICA,Land-Ocean,Mediterranean,MED,-10.0|30.0,-10.0|45.0,40.0|45.0,40.0|30.0
ASIA,Land,S.Asia,SAS,60.0|23.5,60.0|30.0,75.0|30.0,75.0|23.5
"""

MINI_NE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "name": "Maharashtra",
                "name_en": "Maharashtra",
                "admin": "India",
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[72.0, 16.0], [80.0, 16.0], [80.0, 22.0], [72.0, 22.0], [72.0, 16.0]]],
            },
        },
        {
            "type": "Feature",
            "properties": {
                "name": "Karnataka",
                "name_en": "Karnataka",
                "admin": "India",
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[74.0, 12.0], [78.0, 12.0], [78.0, 16.0], [74.0, 16.0], [74.0, 12.0]]],
            },
        },
        {
            "type": "Feature",
            "properties": {
                "name": "Iowa",
                "name_en": "Iowa",
                "admin": "United States of America",
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-96.0, 40.0], [-90.0, 40.0], [-90.0, 44.0], [-96.0, 44.0], [-96.0, 40.0]]],
            },
        },
        {
            "type": "Feature",
            "properties": {
                "name": "Arizona",
                "name_en": "Arizona",
                "admin": "United States of America",
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-115.0, 31.0], [-109.0, 31.0], [-109.0, 37.0], [-115.0, 37.0], [-115.0, 31.0]]],
            },
        },
    ],
}


def _grid() -> SpeiGrid:
    lats = np.array([14.25, 18.25, 34.25, 42.25])
    lons = np.array([-112.25, -93.25, 0.25, 76.25])
    times = [date(2000, 6, 1), date(2000, 7, 1), date(2001, 6, 1)]
    values = np.array([
        [
            [np.nan, -1.6, 0.2, -2.1],
            [0.1, np.nan, -0.4, -1.2],
            [-2.4, -0.2, -1.7, 0.3],
            [0.5, 0.4, 1.1, np.nan],
        ],
        [
            [np.nan, -0.5, 0.1, -1.6],
            [0.0, np.nan, -0.1, -0.8],
            [-1.1, 0.2, -2.0, 0.4],
            [0.2, 0.3, 0.9, np.nan],
        ],
        [
            [np.nan, -2.2, -0.3, -2.5],
            [-0.2, np.nan, 0.0, -1.8],
            [-1.6, -0.1, -1.4, 0.1],
            [0.1, 0.0, 0.4, np.nan],
        ],
    ], dtype=float)
    return SpeiGrid(
        lats=lats, lons=lons, times=times, values=values,
        timescale_months=6, source={"filename": "mini.nc"},
    )


def test_wmo_table_edges_are_the_published_spi_edges():
    assert wmo_class(-2.0) == "extremely_dry"
    assert wmo_class(-2.1) == "extremely_dry"
    assert wmo_class(-1.99) == "severely_dry"
    assert wmo_class(-1.5) == "severely_dry"
    assert wmo_class(-1.49) == "moderately_dry"
    assert wmo_class(-1.0) == "moderately_dry"
    assert wmo_class(-0.99) == "near_normal"
    assert wmo_class(0.0) == "near_normal"
    assert wmo_class(1.0) == "moderately_wet"
    assert wmo_class(1.5) == "severely_wet"
    assert wmo_class(2.0) == "extremely_wet"
    assert PHASE_B_DRY_THRESHOLD == -1.5


def test_ipcc_med_vertices_are_read_not_redrawn():
    verts = parse_ipcc_med_vertices(MINI_IPCC)
    assert verts == [(-10.0, 30.0), (-10.0, 45.0), (40.0, 45.0), (40.0, 30.0)]
    assert point_in_ring(0.0, 40.0, verts) is True
    assert point_in_ring(-20.0, 40.0, verts) is False
    with pytest.raises(ValueError):
        parse_ipcc_med_vertices("no,med,here\n")


def test_natural_earth_keeps_only_named_states():
    got = extract_named_states(MINI_NE, ("Maharashtra", "Karnataka"), ("India",))
    assert got["missing_names"] == []
    assert got["n_rings"] == 2
    # A US state with the same list is not added.
    us = extract_named_states(MINI_NE, ("Iowa", "Ohio"), ("United States",))
    assert us["missing_names"] == ["Ohio"]
    assert len(us["rings_by_name"]["Iowa"]) == 1


def test_coverage_does_not_fill_nan():
    grid = _grid()
    # Mediterranean published box covers lon 0.25, lat 34.25 and 42.25.
    mask = mask_from_rings(grid.lats, grid.lons, [list(IPCC_MED_VERTICES)])
    assert bool(mask[2, 2]) is True
    cov = coverage_for_mask(grid, mask, TARGET_MED)
    assert cov["usable_measured"] is True
    assert cov["n_cells_in_published_cut"] == int(mask.sum())
    assert cov["n_cells_usable_any_month"] <= cov["n_cells_in_published_cut"]
    # Year 2000 and 2001 both have a finite value in the cut.
    assert cov["n_missing_years_in_span"] == 0
    assert cov["n_finite_cell_months"] == int(np.isfinite(grid.values[:, mask]).sum())
    assert cov["first_month_with_a_value"] == "2000-06"
    assert cov["n_months_without_any_valid"] == 0


def test_empty_row_has_none_not_zero():
    row = empty_region_row(TARGET_INDE, "pas de fichier")
    assert row["usable_measured"] is False
    assert row["n_cells_usable_any_month"] is None
    assert row["wmo_class_cell_months"] is None


def test_gee_excerpt_keeps_only_read_fields():
    raw = {
        "id": "CSIC/SPEI/2_11",
        "title": "SPEIbase",
        "version": "2.11",
        "license": "CC-BY-4.0",
        "extent": {
            "temporal": {"interval": [["1901-01-01T00:00:00Z", "2025-01-01T00:00:00Z"]]},
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
        },
        "summaries": {
            "SPEI_06_month": {
                "minimum": -2.33, "maximum": 2.33, "gee:estimated_range": False,
            },
            "gsd": [55660],
            "eo:bands": [1, 2],
        },
        "extra": "ignored",
    }
    got = gee_catalog_excerpt(raw)
    assert got["id"] == "CSIC/SPEI/2_11"
    assert got["spei06_min"] == -2.33
    assert got["pixels_included"] is False
    assert "extra" not in got


def test_count_regions_without_polygons_stays_empty():
    grid = _grid()
    regions = regions_from_sources(None, None)
    # Built-in IPCC MED vertices still exist (published constants).
    assert regions[TARGET_MED]["rings"]
    got = count_regions(grid, {TARGET_US: {"rings": []}})
    assert got[TARGET_US]["usable_measured"] is False
    assert got[TARGET_US]["n_cells_usable_any_month"] is None


def test_bitstream_urls_keep_only_published_hrefs():
    html = """
    <a href="/bitstream/10261/332007/11/spei06.nc">spei06.nc</a>
    <a href="https://digital.csic.es/bitstream/10261/332007/53/file-list.txt">list</a>
    <a href="/foo/bar">other</a>
    """
    urls = SpeiClient().bitstream_urls(html, "https://digital.csic.es/handle/10261/332007")
    assert urls == ["https://digital.csic.es/bitstream/10261/332007/11/spei06.nc"]


def test_eval_script_offline(tmp_path, monkeypatch):
    import scripts.eval_spei as ev

    out = tmp_path / "out"
    monkeypatch.setattr("sys.argv", [
        "eval_spei.py", "--skip-fetch",
        "--cache-dir", str(tmp_path / "cache"),
        "--out-dir", str(out),
    ])
    assert ev.main() == 0
    counts = json.loads((out / "spei_counts.json").read_text(encoding="utf-8"))
    assert counts["catalogue_truth"] == CATALOGUE_TRUTH
    assert counts["champion_switched"] is False
    assert counts["forecast_scored"] is False
    assert counts["seas5_started"] is False
    assert counts["c3s_started"] is False
    assert counts["bss_invented"] is False
    assert counts["verdicts"][CATALOGUE_TRUTH] == "bloquée"
    assert counts["verdicts"][TARGET_MED] == "cible Tier 1 (pas encore testée)"
    assert counts["verdicts"][TARGET_INDE] == "cible Tier 1 (pas encore testée)"
    assert counts["regions"][TARGET_MED]["n_cells_usable_any_month"] is None
    report = (out / "spei_report.md").read_text(encoding="utf-8")
    assert "Aucun chiffre inventé" in report
    assert "Pas de BSS inventé" in report
