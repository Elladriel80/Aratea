"""Stacking résiduel : un nombre, le prix comme prior. Hors réseau."""
from __future__ import annotations

from src.truth.stacking import (
    MIN_TRAIN_STACK, apply_stack, brier_mean, clip_prob, disagreement_count,
    ece, mae, residual_weight,
)


def test_clip_prob_bounds():
    assert 0.0 < clip_prob(-1.0) < 0.01
    assert 0.99 < clip_prob(2.0) < 1.0
    assert abs(clip_prob(0.4) - 0.4) < 1e-12


def test_residual_weight_one_when_truth_follows_model():
    market = [0.2] * MIN_TRAIN_STACK
    model = [0.1] * (MIN_TRAIN_STACK // 2) + [0.9] * (MIN_TRAIN_STACK - MIN_TRAIN_STACK // 2)
    y = list(model)
    w = residual_weight(model, market, y)
    assert w is not None
    assert abs(w - 1.0) < 1e-9


def test_residual_weight_recovers_half_blend():
    market = [0.1 + 0.01 * i for i in range(MIN_TRAIN_STACK)]
    model = [m + 0.2 for m in market]
    # vérité = marché + 0.5 * (modèle − marché)
    y = [m + 0.5 * (s - m) for s, m in zip(model, market)]
    w = residual_weight(model, market, y)
    assert w is not None
    assert abs(w - 0.5) < 1e-9
    stacked = [apply_stack(m, s, w) for s, m in zip(model, market)]
    assert brier_mean(stacked, y) < 1e-12


def test_residual_weight_refuses_short_lists():
    assert residual_weight([0.2], [0.3], [1.0]) is None


def test_residual_weight_zero_when_model_equals_market():
    p = [0.3] * MIN_TRAIN_STACK
    y = [0.0] * MIN_TRAIN_STACK
    assert residual_weight(p, p, y) == 0.0


def test_apply_stack_endpoints():
    assert abs(apply_stack(0.4, 0.8, 0.0) - 0.4) < 1e-12
    assert abs(apply_stack(0.4, 0.8, 1.0) - 0.8) < 1e-12
    assert abs(apply_stack(0.4, 0.8, 0.5) - 0.6) < 1e-12


def test_ece_perfectly_calibrated_is_near_zero():
    # 50 fois 0.0 → y=0, 50 fois 1.0 → y=1
    half = MIN_TRAIN_STACK
    probs = [0.0] * half + [1.0] * half
    y = [0.0] * half + [1.0] * half
    assert ece(probs, y) is not None
    assert ece(probs, y) < 1e-12


def test_ece_constant_half_on_all_yes_is_one_half():
    probs = [0.5] * 20
    y = [1.0] * 20
    assert abs(ece(probs, y) - 0.5) < 1e-12


def test_disagreement_count_uses_threshold():
    model = [0.50, 0.70, 0.51]
    market = [0.50, 0.50, 0.50]
    n_real, n = disagreement_count(model, market, 0.05)
    assert n == 3 and n_real == 1


def test_mae_and_brier_on_known_values():
    assert abs(mae([0.0, 1.0], [1.0, 1.0]) - 0.5) < 1e-12
    assert abs(brier_mean([0.0, 1.0], [0.0, 1.0]) - 0.0) < 1e-12
    assert ece([], []) is None
    assert mae([], []) is None
