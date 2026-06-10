"""Revue 2026-06-10 A4 / finding E2 — formule Kelly correcte.

Avant : f = edge/b = (p-px)·px/(1-px) = Kelly · px (sous-mise d'un facteur px).
Après : f* = (p - px)/(1 - px), symétrique côté NO.

Cas chiffré de la revue : p=0.6, px=0.5 -> f* = 0.2 (avant application de
kelly_fraction et des caps).
"""
from __future__ import annotations

from src.simulation.sizing import kelly_fractional_size


def _raw_fraction(prob_yes, px, side):
    """f* brute : kelly_fraction=1, bankroll=1, cap=1 -> renvoie la fraction."""
    return kelly_fractional_size(
        prob_yes=prob_yes,
        market_yes_price=px,
        side=side,
        kelly_fraction=1.0,
        bankroll=1.0,
        max_fraction_per_bet=1.0,
    )


def test_kelly_yes_numeric_case():
    # p=0.6, px=0.5 -> (0.6-0.5)/(1-0.5) = 0.2
    assert _raw_fraction(0.6, 0.5, "YES") == 0.2


def test_kelly_no_is_symmetric():
    # NO avec p_yes=0.4 (p_no=0.6), px=0.5 (px_no=0.5) -> 0.2 aussi.
    assert _raw_fraction(0.4, 0.5, "NO") == 0.2


def test_kelly_is_one_over_px_larger_than_old_formula():
    # La correction multiplie la mise par 1/px vs l'ancienne (p-px)*px/(1-px).
    p, px = 0.7, 0.4
    new = _raw_fraction(p, px, "YES")
    old = (p - px) * px / (1 - px)  # ancienne formule edge/b
    assert abs(new - old / px) < 1e-9
    assert abs(new - (p - px) / (1 - px)) < 1e-9


def test_kelly_fraction_and_bankroll_applied():
    # f* = 0.2, quart Kelly, bankroll 1000 -> 0.2 * 0.25 * 1000 = 50.0
    amount = kelly_fractional_size(
        prob_yes=0.6, market_yes_price=0.5, side="YES",
        kelly_fraction=0.25, bankroll=1000.0, max_fraction_per_bet=1.0,
    )
    assert amount == 50.0


def test_kelly_cap_still_binds():
    # Même mise correcte, le cap max_fraction_per_bet reste appliqué.
    amount = kelly_fractional_size(
        prob_yes=0.6, market_yes_price=0.5, side="YES",
        kelly_fraction=1.0, bankroll=1000.0, max_fraction_per_bet=0.05,
    )
    assert amount == 50.0  # 0.05 * 1000, cap binding (Kelly brut 0.2 > 0.05)


def test_non_profitable_bet_is_zero():
    # p < px côté YES -> edge négatif -> 0.
    assert _raw_fraction(0.4, 0.5, "YES") == 0.0
