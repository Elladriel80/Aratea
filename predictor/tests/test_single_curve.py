"""Piste A5 : une densité continue, puis découpe des bins."""
from __future__ import annotations

import math

from src.truth.synthetic_bins import (
    Bin, horizon_blend, kalshi_style_bins,
    prob_in_bin_gaussian, prob_in_bin_mixture,
)


def test_mixture_over_full_ladder_sums_to_one():
    bins = kalshi_style_bins(76.0, n_central=6)
    vals = [72.0, 76.0, 81.0]
    total = sum(prob_in_bin_mixture(vals, 2.0, b) for b in bins)
    assert abs(total - 1.0) < 1e-9


def test_mixture_empty_is_zero():
    assert prob_in_bin_mixture([], 2.0, Bin(76, 77)) == 0.0


def test_mixture_differs_from_single_gaussian_when_vendors_disagree():
    b = Bin(76, 77)
    vals = [70.0, 76.0, 84.0]
    gauss = prob_in_bin_gaussian(sum(vals) / 3.0, 2.5, b)
    mix = prob_in_bin_mixture(vals, 2.5, b)
    assert abs(mix - gauss) > 1e-6


def test_horizon_blend_is_pure_curve_on_same_day():
    assert horizon_blend(0.20, 0.80, 0) == 0.20
    j1 = horizon_blend(0.20, 0.80, 1)
    assert 0.20 < j1 < 0.80
    expected = math.exp(-1.0 / 8.0) * 0.20 + (1.0 - math.exp(-1.0 / 8.0)) * 0.80
    assert abs(j1 - expected) < 1e-12


def test_champion_formula_matches_horizon_blend():
    """Le champion live est une courbe, puis un mélange par bin (ensemble.py)."""
    p_forecast, p_climato, days = 0.31, 0.12, 3
    w = math.exp(-days / 8.0)
    live = w * p_forecast + (1 - w) * p_climato
    assert abs(live - horizon_blend(p_forecast, p_climato, days)) < 1e-12
