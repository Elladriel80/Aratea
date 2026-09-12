"""Nowcast : thermomètre déjà vu + reste du jour. Hors réseau."""
from __future__ import annotations

from datetime import date, datetime, timezone

from src.truth.nowcast import (
    EmpiricalRemaining, FALLBACK_BASE_F, MIN_EMPIRICAL, ROUNDING_SIGMA,
    fallback_sigma, hours_left, kind_for_variable, prob_bin_nowcast,
    remaining_params,
)
from src.truth.synthetic_bins import Bin


def test_hours_left_new_york_afternoon():
    # 18 UTC = 13 h standard (UTC−5). Fin du jour LST = 05 UTC le lendemain.
    as_of = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)
    left = hours_left(date(2026, 8, 3), "America/New_York", as_of)
    assert 10.5 < left < 11.5


def test_hours_left_zero_after_lst_midnight():
    as_of = datetime(2026, 8, 4, 6, 0, tzinfo=timezone.utc)
    assert hours_left(date(2026, 8, 3), "America/New_York", as_of) == 0.0


def test_fallback_sigma_shrinks_and_never_invents_a_reading():
    assert fallback_sigma(0.0) == ROUNDING_SIGMA
    assert fallback_sigma(12.0) == FALLBACK_BASE_F
    assert fallback_sigma(6.0) == FALLBACK_BASE_F * 0.5
    assert fallback_sigma(24.0) == FALLBACK_BASE_F


def test_prob_max_already_above_bin_is_zero():
    b = Bin(76, 77)
    assert prob_bin_nowcast(80.0, 82.0, 1.5, b, "max") == 0.0


def test_prob_max_already_in_bin_falls_if_rest_goes_higher():
    b = Bin(76, 77)
    # déjà 76,5 : on reste dans le bin seulement si le reste ≤ 77,5
    p_safe = prob_bin_nowcast(76.5, 70.0, 0.4, b, "max")
    p_risk = prob_bin_nowcast(76.5, 84.0, 0.4, b, "max")
    assert p_safe > 0.9
    assert p_risk < 0.1


def test_prob_max_still_below_bin_needs_the_rest():
    b = Bin(80, 81)
    p = prob_bin_nowcast(70.0, 80.5, 0.3, b, "max")
    assert p > 0.8
    p_miss = prob_bin_nowcast(70.0, 72.0, 0.3, b, "max")
    assert p_miss < 0.05


def test_prob_min_already_below_bin_is_zero():
    b = Bin(60, 61)
    assert prob_bin_nowcast(55.0, 54.0, 1.0, b, "min") == 0.0


def test_prob_min_already_in_bin_falls_if_rest_goes_lower():
    b = Bin(60, 61)
    p_safe = prob_bin_nowcast(60.5, 70.0, 0.4, b, "min")
    p_risk = prob_bin_nowcast(60.5, 50.0, 0.4, b, "min")
    assert p_safe > 0.9
    assert p_risk < 0.1


def test_remaining_params_prefers_hrrr_then_empirical_then_width():
    hrrr = {"extreme_f": 82.0}
    emp = (2.0, 1.2)
    mu, sig, src = remaining_params(76.0, 8.0, hrrr, emp, hrrr_sigma=1.7)
    assert src == "hrrr_previous_day1" and mu == 82.0 and sig == 1.7
    mu, sig, src = remaining_params(76.0, 8.0, None, emp)
    assert src == "empirical_train" and mu == 78.0 and abs(sig - 1.2) < 1e-9
    mu, sig, src = remaining_params(76.0, 6.0, None, None)
    assert src == "hours_left_width" and mu == 76.0
    assert abs(sig - fallback_sigma(6.0)) < 1e-9
    mu, sig, src = remaining_params(76.0, 0.0, hrrr, emp)
    assert src == "day_closed" and mu == 76.0 and sig == ROUNDING_SIGMA


def test_empirical_remaining_needs_enough_days_and_does_not_invent():
    emp = EmpiricalRemaining()
    assert emp.get("KNYC", "temp_max", 18) is None
    for i in range(MIN_EMPIRICAL):
        emp.add("KNYC", "temp_max", 18, 70.0, 72.0)
    got = emp.get("KNYC", "temp_max", 18)
    assert got is not None
    assert abs(got[0] - 2.0) < 1e-9
    # une autre ville au même horaire peut prendre le pot commun
    pooled = emp.get("KLAX", "temp_max", 18)
    assert pooled is not None


def test_kind_for_variable():
    assert kind_for_variable("temp_max") == "max"
    assert kind_for_variable("temp_min") == "min"
