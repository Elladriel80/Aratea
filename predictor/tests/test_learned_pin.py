"""Revue 2026-06-10 A2 — LearnedPredictor honore le pin de CHAMPION.json.

Constat E1 : `LearnedPredictor` chargeait runs_learning/<dernier>/run.json,
qui peut être un run récent non-promotable — les Brier shadow étiquetés
"learned_v2" mesuraient alors un autre modèle. Le run doit être épinglé via
le `trained_at` de CHAMPION.json, sinon erreur explicite (pas de fallback).
"""
from __future__ import annotations

import json

import pytest

from src.predictors import learned as learned_mod
from src.predictors.learned import (
    LearnedPredictor,
    _resolve_run_json_from_registry,
)


PIN = "20260101T000000Z"      # run épinglé (le "bon")
LATEST = "20260606T070428Z"   # run plus récent, non-promotable (le piège)


def _write_run(runs_root, ts, feature_set="v2"):
    d = runs_root / ts
    d.mkdir(parents=True, exist_ok=True)
    run = {
        "schema_version": 2,
        "timestamp_utc": ts,
        "feature_set_used": feature_set,
        "feature_names": ["f1"],
        "intercept": 0.0,
        "feature_importances": {"f1": 0.5},
        "feature_means": {"f1": 0.0},
        "feature_stds": {"f1": 1.0},
    }
    (d / "run.json").write_text(json.dumps(run), encoding="utf-8")


def _write_registry(runs_root, pinned_trained_at):
    registry = {
        "current_champion": "vendor_ensemble",
        "models": [
            {"name": "vendor_ensemble", "method": "ensemble",
             "trained_at": None, "feature_set": None},
            {"name": "learned_v2", "method": "learned_v2",
             "trained_at": pinned_trained_at, "feature_set": "v2"},
        ],
    }
    (runs_root / "CHAMPION.json").write_text(json.dumps(registry), encoding="utf-8")


def _make_runs(tmp_path):
    runs_root = tmp_path / "runs_learning"
    _write_run(runs_root, PIN)
    _write_run(runs_root, LATEST, feature_set="v2")  # plus récent (sorted() -> dernier)
    _write_registry(runs_root, PIN)
    return runs_root


def test_resolver_picks_pinned_not_latest(tmp_path):
    runs_root = _make_runs(tmp_path)
    path = _resolve_run_json_from_registry(runs_root, trained_at=None)
    assert path == runs_root / PIN / "run.json"
    assert PIN in str(path) and LATEST not in str(path)


def test_predictor_loads_pinned_run(tmp_path):
    runs_root = _make_runs(tmp_path)
    # Sub-prédicteurs / weather injectés en factices : on ne fait pas predict(),
    # on vérifie juste quel run.json est chargé à l'init (pas de réseau).
    dummy = object()
    learned = LearnedPredictor(
        weather_client=dummy,
        runs_root=runs_root,
        sub_climato=dummy,
        sub_forecast_blend=dummy,
        sub_ensemble=dummy,
    )
    assert learned.trained_at == PIN
    assert learned.run_json_path == runs_root / PIN / "run.json"


def test_explicit_trained_at_overrides(tmp_path):
    runs_root = _make_runs(tmp_path)
    dummy = object()
    learned = LearnedPredictor(
        weather_client=dummy,
        runs_root=runs_root,
        trained_at=LATEST,
        sub_climato=dummy,
        sub_forecast_blend=dummy,
        sub_ensemble=dummy,
    )
    assert learned.trained_at == LATEST


def test_no_pin_raises_instead_of_loading_latest(tmp_path):
    # Registre sans entrée learned avec trained_at -> doit lever, PAS charger LATEST.
    runs_root = tmp_path / "runs_learning"
    _write_run(runs_root, PIN)
    _write_run(runs_root, LATEST)
    registry = {"current_champion": "vendor_ensemble",
                "models": [{"name": "vendor_ensemble", "method": "ensemble",
                            "trained_at": None, "feature_set": None}]}
    (runs_root / "CHAMPION.json").write_text(json.dumps(registry), encoding="utf-8")
    with pytest.raises(ValueError):
        _resolve_run_json_from_registry(runs_root, trained_at=None)


def test_pin_to_missing_run_raises(tmp_path):
    runs_root = tmp_path / "runs_learning"
    _write_run(runs_root, LATEST)
    _write_registry(runs_root, PIN)  # pin vers PIN, qui n'existe pas sur disque
    with pytest.raises(FileNotFoundError):
        _resolve_run_json_from_registry(runs_root, trained_at=None)
