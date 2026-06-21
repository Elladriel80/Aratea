"""Tests for the V3fa feature set (fold-aware series bias, B35, 2026-06-21).

V3fa replaces the full-dataset series_bias_prior (V3b) with a fold-aware
variant estimated from TRAIN dates only, eliminating leakage into VALID/HOLDOUT.

The feature is pre-computed into the dataset record under the key
'series_bias_fa'; f_series_bias_fa just reads it from the dict.
"""
from __future__ import annotations

from src.learning.features import (
    FEATURE_SETS,
    FEATURES_V3FA,
    f_series_bias_fa,
    extract,
    f_p_consensus,
    f_forecast_spread,
)


def _rec_v3fa(p_clim=0.4, p_blend=0.5, p_ens=0.6, bias_fa=-0.09):
    """Minimal record with pre-computed series_bias_fa."""
    return {
        "predictions": {
            "climatology": {"prob_yes": p_clim},
            "forecast_blend": {
                "prob_yes": p_blend,
                "inputs": {"days_ahead": 1},
            },
            "ensemble": {
                "prob_yes": p_ens,
                "inputs": {"individual_probs": {"ecmwf": 0.4, "gfs": 0.6}},
            },
        },
        "target_date": "2026-06-10",
        "snapshot_at": "20260609T120000Z",
        "series_bias_fa": bias_fa,
    }


def test_f_series_bias_fa_reads_precomputed_value():
    rec = _rec_v3fa(bias_fa=-0.087)
    assert abs(f_series_bias_fa(rec) - (-0.087)) < 1e-9


def test_f_series_bias_fa_returns_none_if_absent():
    rec = _rec_v3fa()
    del rec["series_bias_fa"]
    assert f_series_bias_fa(rec) is None


def test_v3fa_feature_names_and_order():
    names = [n for n, _ in FEATURES_V3FA]
    assert names == ["p_consensus", "forecast_spread", "days_ahead", "series_bias_fa"]


def test_v3fa_registered_in_feature_sets():
    assert "v3fa" in FEATURE_SETS
    assert FEATURE_SETS["v3fa"] is FEATURES_V3FA


def test_extract_v3fa_produces_expected_keys():
    rec = _rec_v3fa(bias_fa=-0.090)
    feats = extract(rec, FEATURES_V3FA)
    assert feats is not None
    assert set(feats) == {"p_consensus", "forecast_spread", "days_ahead", "series_bias_fa"}
    assert abs(feats["series_bias_fa"] - (-0.090)) < 1e-9


def test_extract_v3fa_drops_row_if_bias_fa_missing():
    rec = _rec_v3fa()
    del rec["series_bias_fa"]
    assert extract(rec, FEATURES_V3FA) is None
