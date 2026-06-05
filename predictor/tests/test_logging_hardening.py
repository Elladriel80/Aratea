"""Tests for the report logging hardening (2026-06-05).

`_predict_all_models` used to store only {"method": "ensemble"} for the
champion, discarding the component probabilities the EnsemblePredictor had
already computed. `_ensemble_components` persists those scalars so the learned
feature vector can be rebuilt offline from report.json. These tests pin that
contract and guarantee the change stays additive (no None noise, no crash on
empty inputs).
"""
from __future__ import annotations

from live_run import _ensemble_components


def _full_inputs():
    return {
        "per_model_value": {"ecmwf": 71.2, "gfs": 70.4, "jma": 72.0},
        "weights": {"ecmwf": 1.0, "gfs": 1.0, "jma": 1.0},
        "mu": 71.2,
        "sigma_inter_models": 0.65,
        "sigma_climato": 4.1,
        "sigma_total": 2.1,
        "p_forecast": 0.41,
        "p_climato": 0.33,
        "blend_weight_forecast": 0.78,
        "days_ahead": 2,
        "n_models_active": 3,
        "climato_value_min": 60.0,
        "climato_value_max": 80.0,
    }


def test_components_are_persisted():
    out = _ensemble_components(0.39, _full_inputs())
    assert out["method"] == "ensemble"
    assert out["p_ensemble"] == 0.39
    assert out["p_climato"] == 0.33
    assert out["p_forecast"] == 0.41
    assert out["days_ahead"] == 2
    assert out["sigma_inter_models"] == 0.65
    assert out["per_model_value"] == {"ecmwf": 71.2, "gfs": 70.4, "jma": 72.0}


def test_reconstructable_consensus_inputs_present():
    # p_consensus = mean(p_climatology, p_forecast_blend, p_ensemble). The
    # report must carry enough to approximate it offline: p_climato, a
    # forecast-side prob, and p_ensemble.
    out = _ensemble_components(0.39, _full_inputs())
    for k in ("p_ensemble", "p_climato", "p_forecast"):
        assert k in out and out[k] is not None


def test_no_none_noise_and_no_crash_on_empty():
    assert _ensemble_components(None, None) == {"method": "ensemble", "p_ensemble": None}
    assert _ensemble_components(0.5, {}) == {"method": "ensemble", "p_ensemble": 0.5}


def test_none_valued_keys_are_dropped():
    out = _ensemble_components(0.5, {"p_climato": None, "days_ahead": 3})
    assert "p_climato" not in out          # None is filtered
    assert out["days_ahead"] == 3          # present value kept


def test_empty_per_model_value_omitted():
    out = _ensemble_components(0.5, {"per_model_value": {}})
    assert "per_model_value" not in out
