"""Tests for V3fb interaction features (B38, 2026-06-21).

V3fb extends v3fa with two fold-aware interaction terms:
  - p_consensus_x_series_bias_fa : p_consensus × series_bias_fa
  - days_ahead_x_series_bias_fa  : days_ahead  × series_bias_fa

Both require series_bias_fa to be pre-annotated in the record (same as v3fa).
"""
from __future__ import annotations

from src.learning.features import (
    FEATURE_SETS,
    FEATURES_V3FB,
    f_p_consensus_x_series_bias_fa,
    f_days_ahead_x_series_bias_fa,
    extract,
)


def _rec_v3fb(p_clim=0.4, p_blend=0.5, p_ens=0.6,
              days_ahead=1, bias_fa=-0.090):
    """Minimal record with pre-computed series_bias_fa."""
    return {
        "predictions": {
            "climatology": {"prob_yes": p_clim},
            "forecast_blend": {
                "prob_yes": p_blend,
                "inputs": {"days_ahead": days_ahead},
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


def test_p_consensus_x_series_bias_fa_value():
    rec = _rec_v3fb(p_clim=0.4, p_blend=0.5, p_ens=0.6, bias_fa=-0.090)
    pc = (0.4 + 0.5 + 0.6) / 3  # = 0.5
    expected = pc * (-0.090)
    result = f_p_consensus_x_series_bias_fa(rec)
    assert result is not None
    assert abs(result - expected) < 1e-9


def test_p_consensus_x_series_bias_fa_none_if_bias_absent():
    rec = _rec_v3fb()
    del rec["series_bias_fa"]
    assert f_p_consensus_x_series_bias_fa(rec) is None


def test_p_consensus_x_series_bias_fa_zero_bias():
    rec = _rec_v3fb(bias_fa=0.0)
    assert f_p_consensus_x_series_bias_fa(rec) == 0.0


def test_days_ahead_x_series_bias_fa_value():
    rec = _rec_v3fb(days_ahead=3, bias_fa=-0.090)
    result = f_days_ahead_x_series_bias_fa(rec)
    assert result is not None
    assert abs(result - (3 * -0.090)) < 1e-9


def test_days_ahead_x_series_bias_fa_none_if_bias_absent():
    rec = _rec_v3fb(days_ahead=2)
    del rec["series_bias_fa"]
    assert f_days_ahead_x_series_bias_fa(rec) is None


def test_v3fb_feature_names_and_order():
    names = [n for n, _ in FEATURES_V3FB]
    assert names == [
        "p_consensus",
        "forecast_spread",
        "days_ahead",
        "series_bias_fa",
        "p_consensus_x_series_bias_fa",
        "days_ahead_x_series_bias_fa",
    ]


def test_v3fb_registered_in_feature_sets():
    assert "v3fb" in FEATURE_SETS
    assert FEATURE_SETS["v3fb"] is FEATURES_V3FB


def test_extract_v3fb_produces_all_keys():
    rec = _rec_v3fb(bias_fa=-0.081, days_ahead=2)
    feats = extract(rec, FEATURES_V3FB)
    assert feats is not None
    expected_keys = {
        "p_consensus", "forecast_spread", "days_ahead", "series_bias_fa",
        "p_consensus_x_series_bias_fa", "days_ahead_x_series_bias_fa",
    }
    assert set(feats) == expected_keys
    pc = (0.4 + 0.5 + 0.6) / 3
    assert abs(feats["p_consensus_x_series_bias_fa"] - pc * (-0.081)) < 1e-9
    assert abs(feats["days_ahead_x_series_bias_fa"] - 2 * (-0.081)) < 1e-9


def test_extract_v3fb_drops_row_if_bias_absent():
    rec = _rec_v3fb()
    del rec["series_bias_fa"]
    assert extract(rec, FEATURES_V3FB) is None
