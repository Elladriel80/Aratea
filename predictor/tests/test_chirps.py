"""Tests hors réseau : polygones CHIRPS, comptes, script."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from src.truth.chirps import (
    CATALOGUE_TRUTH, FAQ_FILL, FAQ_RESOLUTION_DEG, FAQ_UNITS, IPCC_MED_VERTICES,
    PUBLISHED_DROUGHT_THRESHOLDS, TARGET_INDE, TARGET_MED, ChirpsSlab,
    coverage_for_mask, empty_region_row, extract_named_states,
    gee_catalog_excerpt, iri_time_to_date, mask_from_rings, month_label,
    parse_ipcc_med_vertices, parse_ucsb_tif_index, parse_ucsb_year_index,
    point_in_ring, regions_from_sources,
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
    ],
}

TIF_HTML = """
<a href="chirps-v2.0.1981.01.tif.gz">chirps-v2.0.1981.01.tif.gz</a>
<a href="chirps-v2.0.1981.02.tif.gz">chirps-v2.0.1981.02.tif.gz</a>
<a href="chirps-v2.0.1981.04.tif.gz">chirps-v2.0.1981.04.tif.gz</a>
"""

YEAR_HTML = """
<a href="chirps-v2.0.1981.monthly.nc">chirps-v2.0.1981.monthly.nc</a>
<a href="chirps-v2.0.1983.monthly.nc">chirps-v2.0.1983.monthly.nc</a>
"""


def _slab() -> ChirpsSlab:
    lats = np.array([14.25, 18.25, 34.25, 42.25])
    lons = np.array([0.25, 76.25, 200.0])
    times = [date(1981, 1, 1), date(1981, 2, 1), date(1982, 1, 1)]
    values = np.array([
        [
            [np.nan, 12.0, np.nan],
            [0.0, 80.0, np.nan],
            [5.0, np.nan, np.nan],
            [3.0, np.nan, np.nan],
        ],
        [
            [np.nan, 0.0, np.nan],
            [1.0, 10.0, np.nan],
            [np.nan, np.nan, np.nan],
            [2.0, np.nan, np.nan],
        ],
        [
            [np.nan, 4.0, np.nan],
            [0.0, 9.0, np.nan],
            [8.0, np.nan, np.nan],
            [1.0, np.nan, np.nan],
        ],
    ], dtype=float)
    return ChirpsSlab(
        lats=lats, lons=lons, times=times, values=values,
        source={"filename": "mini.nc"},
    )


def test_catalogue_name_is_not_renamed():
    assert CATALOGUE_TRUTH == "CHIRPS pluie"
    assert TARGET_MED == "Sécheresse Méditerranée"
    assert TARGET_INDE == "Sécheresse Inde"
    assert FAQ_FILL == -9999.0
    assert FAQ_RESOLUTION_DEG == 0.05
    assert FAQ_UNITS == "mm/month"
    assert PUBLISHED_DROUGHT_THRESHOLDS == ()


def test_iri_time_jan_1981_is_252_5():
    assert iri_time_to_date(252.5) == date(1981, 1, 1)
    assert iri_time_to_date(253.5) == date(1981, 2, 1)
    assert iri_time_to_date(799.5) == date(2026, 8, 1)
    assert month_label(2026, 8) == "Aug 2026"


def test_ipcc_med_vertices_are_read_not_redrawn():
    verts = parse_ipcc_med_vertices(MINI_IPCC)
    assert verts == [(-10.0, 30.0), (-10.0, 45.0), (40.0, 45.0), (40.0, 30.0)]
    assert point_in_ring(0.0, 40.0, verts) is True
    assert point_in_ring(-20.0, 40.0, verts) is False
    with pytest.raises(ValueError):
        parse_ipcc_med_vertices("no,med,here\n")


def test_natural_earth_keeps_only_named_indian_states():
    got = extract_named_states(MINI_NE, ("Maharashtra", "Karnataka"), ("India",))
    assert got["missing_names"] == []
    assert got["n_rings"] == 2
    us = extract_named_states(MINI_NE, ("Iowa", "Ohio"), ("United States",))
    assert us["missing_names"] == ["Ohio"]


def test_coverage_does_not_fill_nan_or_invent_thresholds():
    slab = _slab()
    mask = mask_from_rings(slab.lats, slab.lons, [list(IPCC_MED_VERTICES)])
    assert bool(mask[2, 0]) is True
    assert bool(mask[0, 0]) is False
    cov = coverage_for_mask(slab, mask, TARGET_MED)
    assert cov["usable_measured"] is True
    assert cov["n_cells_in_published_cut"] == int(mask.sum())
    assert cov["n_cells_usable_any_month"] <= cov["n_cells_in_published_cut"]
    assert cov["n_missing_years_in_span"] == 0
    assert cov["n_finite_cell_months"] == int(np.isfinite(slab.values[:, mask]).sum())
    assert cov["first_month_with_a_value"] == "1981-01"
    assert "drought_classes_in_monthly_file_docs" in cov["thresholds"]
    assert cov["thresholds"]["drought_classes_in_monthly_file_docs"] == []


def test_empty_row_has_none_not_zero():
    row = empty_region_row(TARGET_INDE, "pas de fichier")
    assert row["usable_measured"] is False
    assert row["n_cells_usable_any_month"] is None
    assert row["n_finite_cell_months"] is None


def test_tif_index_reports_the_missing_month_it_read():
    got = parse_ucsb_tif_index(TIF_HTML)
    assert got["n_files"] == 3
    assert got["first_month"] == "1981-01"
    assert got["last_month"] == "1981-04"
    assert got["missing_months_in_span"] == ["1981-03"]
    assert got["n_missing_months_in_span"] == 1


def test_year_index_reports_the_missing_year_it_read():
    got = parse_ucsb_year_index(YEAR_HTML)
    assert got["years"] == [1981, 1983]
    assert got["missing_years_in_span"] == [1982]


def test_gee_excerpt_keeps_only_read_fields():
    raw = {
        "id": "UCSB-CHG/CHIRPS/PENTAD",
        "title": "CHIRPS",
        "version": "2.0",
        "license": "proprietary",
        "extent": {
            "temporal": {"interval": [["1981-01-01T00:00:00Z", "2026-07-26T00:00:00Z"]]},
            "spatial": {"bbox": [[-180, -50, 180, 50]]},
        },
        "summaries": {
            "precipitation": {
                "minimum": 0, "maximum": 1072.43, "gee:estimated_range": True,
            },
            "gsd": [5566],
        },
        "extra": "ignored",
    }
    got = gee_catalog_excerpt(raw)
    assert got["id"] == "UCSB-CHG/CHIRPS/PENTAD"
    assert got["pixels_included"] is False
    assert "extra" not in got


def test_count_regions_without_india_polygons_stays_empty():
    regions = regions_from_sources(None, None)
    assert regions[TARGET_MED]["rings"]
    assert regions[TARGET_INDE]["rings"] == []
    from src.truth.chirps import count_regions
    got = count_regions(_slab(), {TARGET_INDE: {"rings": []}})
    assert got[TARGET_INDE]["usable_measured"] is False
    assert got[TARGET_INDE]["n_cells_usable_any_month"] is None


def test_eval_script_offline(tmp_path, monkeypatch):
    import scripts.eval_chirps as ev

    out = tmp_path / "out"
    monkeypatch.setattr("sys.argv", [
        "eval_chirps.py", "--skip-fetch",
        "--cache-dir", str(tmp_path / "cache"),
        "--out-dir", str(out),
    ])
    assert ev.main() == 0
    counts = json.loads((out / "chirps_counts.json").read_text(encoding="utf-8"))
    assert counts["catalogue_truth"] == CATALOGUE_TRUTH
    assert counts["champion_switched"] is False
    assert counts["forecast_scored"] is False
    assert counts["seas5_started"] is False
    assert counts["c3s_started"] is False
    assert counts["bss_invented"] is False
    assert counts["thresholds_invented"] is False
    assert counts["verdicts"][CATALOGUE_TRUTH] == "bloquée"
    assert counts["verdicts"][TARGET_MED] == "cible Tier 1 (pas encore testée)"
    assert counts["verdicts"][TARGET_INDE] == "cible Tier 1 (pas encore testée)"
    assert counts["regions"][TARGET_MED]["n_cells_usable_any_month"] is None
    report = (out / "chirps_report.md").read_text(encoding="utf-8")
    assert "Aucun chiffre inventé" in report
    assert "Pas de BSS inventé" in report
    assert "Pas de seuil inventé" in report
