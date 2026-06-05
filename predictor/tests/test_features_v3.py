"""Tests for the V3 feature set (corrected Phase 1 set, 2026-06-05).

V3 fixes the v2 NO-GO diagnosis with two changes:

  1. The three near-collinear probability features (p_climatology,
     p_forecast_blend, p_ensemble) collapse into a single `p_consensus`
     equal to their arithmetic mean.
  2. The six static geographic features are dropped.

These tests pin the contract so a future refactor can't silently bring
back the collinear block or the geographic noise.
"""
from __future__ import annotations

import math

from src.learning.features import (
    FEATURE_SETS,
    FEATURES_V2,
    FEATURES_V3,
    extract,
    f_p_consensus,
)


def _rec(p_clim, p_blend, p_ens):
    """Minimal forward-capture record carrying the three probability views."""
    return {
        "predictions": {
            "climatology": {"prob_yes": p_clim},
            "forecast_blend": {"prob_yes": p_blend},
            "ensemble": {
                "prob_yes": p_ens,
                "inputs": {"individual_probs": {"ecmwf": 0.4, "gfs": 0.6}},
            },
        },
        "target_date": "2026-06-10",
        "snapshot_at": "20260605T120000Z",
    }


def test_p_consensus_is_mean_of_three_probabilities():
    rec = _rec(0.2, 0.5, 0.8)
    assert math.isclose(f_p_consensus(rec), (0.2 + 0.5 + 0.8) / 3.0)


def test_p_consensus_none_if_any_probability_missing():
    # Drop the row instead of imputing — mirrors the v0/v2 contract.
    rec = _rec(0.2, None, 0.8)
    rec["predictions"]["forecast_blend"] = {}
    assert f_p_consensus(rec) is None


def test_v3_feature_names_and_order():
    names = [n for n, _ in FEATURES_V3]
    assert names == ["p_consensus", "forecast_spread", "days_ahead"]


def test_v3_drops_collinear_probabilities_and_geographic_features():
    names = {n for n, _ in FEATURES_V3}
    # the three collinear probability views must not appear individually
    for collinear in ("p_climatology", "p_forecast_blend", "p_ensemble"):
        assert collinear not in names
    # none of the six static geographic features survive
    geo = {
        "urban_density_5km",
        "water_pct_10km",
        "forest_pct_5km",
        "elevation_m",
        "distance_to_coast_km",
        "latitude",
    }
    assert names.isdisjoint(geo)
    # v3 is strictly smaller than v2
    assert len(FEATURES_V3) < len(FEATURES_V2)


def test_v3_is_selectable_via_feature_sets():
    assert "v3" in FEATURE_SETS
    assert FEATURE_SETS["v3"] is FEATURES_V3


def test_extract_v3_produces_expected_keys():
    rec = _rec(0.2, 0.5, 0.8)
    feats = extract(rec, FEATURES_V3)
    assert feats is not None
    assert set(feats) == {"p_consensus", "forecast_spread", "days_ahead"}
    assert math.isclose(feats["p_consensus"], 0.5)
