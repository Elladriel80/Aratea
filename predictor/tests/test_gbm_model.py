"""Tests for GBMLearnedModel (GBM hypothesis, 2026-06-20).

Pins the interface contract: fit/predict_proba/feature_importance work
correctly, probabilities stay in [0,1], and the model generalises
(test Brier < naive baseline 0.25 on synthetic data).
"""
from __future__ import annotations

import numpy as np
import pytest

from src.learning.model import GBMLearnedModel, brier_score


def _synthetic_dataset(n: int = 200, seed: int = 42):
    """Synthetic (X, y) with a non-linear signal: y=1 when x0>0.5 XOR x1>0.3."""
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(0, 1, n)
    x1 = rng.uniform(0, 1, n)
    noise = rng.uniform(-0.1, 0.1, n)
    # non-linear signal that LR would struggle with
    y = ((x0 > 0.5) ^ (x1 > 0.3)).astype(int)
    X = [{"x0": float(x0[i] + noise[i]), "x1": float(x1[i])} for i in range(n)]
    return X, y.tolist()


def test_gbm_fit_predict_shape():
    X, y = _synthetic_dataset(100)
    m = GBMLearnedModel(feature_names=["x0", "x1"])
    m.fit(X, y)
    p = m.predict_proba(X)
    assert p.shape == (100,)


def test_gbm_probabilities_in_unit_interval():
    X, y = _synthetic_dataset(100)
    m = GBMLearnedModel(feature_names=["x0", "x1"])
    m.fit(X, y)
    p = m.predict_proba(X)
    assert float(np.min(p)) >= 0.0
    assert float(np.max(p)) <= 1.0


def test_gbm_brier_below_naive_baseline():
    """Model must beat the uninformative baseline (predict 0.5 everywhere → Brier=0.25)."""
    X, y = _synthetic_dataset(300)
    train, test = X[:200], X[200:]
    ytrain, ytest = y[:200], y[200:]
    m = GBMLearnedModel(feature_names=["x0", "x1"])
    m.fit(train, ytrain)
    p = m.predict_proba(test)
    b = brier_score(ytest, p)
    assert b < 0.25, f"GBM Brier {b:.4f} should beat naive 0.25"


def test_gbm_feature_importance_sums_near_one():
    X, y = _synthetic_dataset(100)
    m = GBMLearnedModel(feature_names=["x0", "x1"])
    m.fit(X, y)
    importances = m.feature_importance()
    assert len(importances) == 2
    total = sum(v for _, v in importances)
    assert abs(total - 1.0) < 1e-6, f"importances sum={total}, expected ~1.0"


def test_gbm_feature_importance_names_match():
    X, y = _synthetic_dataset(100)
    m = GBMLearnedModel(feature_names=["x0", "x1"])
    m.fit(X, y)
    names = [n for n, _ in m.feature_importance()]
    assert names == ["x0", "x1"]


def test_gbm_interface_matches_lr():
    """GBMLearnedModel must expose the same fit/predict_proba/feature_importance API as LearnedModel."""
    from src.learning.model import LearnedModel

    X, y = _synthetic_dataset(100)
    for cls in (LearnedModel, GBMLearnedModel):
        m = cls(feature_names=["x0", "x1"])
        m.fit(X, y)
        p = m.predict_proba(X)
        imp = m.feature_importance()
        assert p.shape == (100,)
        assert isinstance(imp, list)
