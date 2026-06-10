"""Revue 2026-06-10 A3 / E3 — normalisation unifiée des probabilités.

Avant : trois conventions incompatibles (backtest renormalisait sur bins
centraux, simulate sur tous les bins, daily_auto brut). Désormais une seule
fonction partagée `normalize_event_probs`, convention live (inconditionnelle).

Critère de la revue : mêmes probas d'entrée -> mêmes probas de sortie dans les
trois chemins.
"""
from __future__ import annotations

from src.predictors.normalize import normalize_event_probs


PROBS = [0.20, 0.60, 0.90]  # somme = 1.70 (volontairement != 1)


def test_unconditional_identity_no_renormalization():
    out = normalize_event_probs(PROBS)
    assert out == PROBS
    # Surtout PAS de renormalisation : la somme reste != 1.
    assert abs(sum(out) - 1.0) > 1e-9


def test_returns_floats_in_order():
    out = normalize_event_probs((1, 0, 0.5))  # accepte un itérable d'ints
    assert out == [1.0, 0.0, 0.5]
    assert all(isinstance(x, float) for x in out)


def test_three_paths_agree_on_same_input():
    """Reproduit le mapping de chaque site d'appel et vérifie l'égalité.

    backtest : liste de dicts ; simulate : liste de tuples (objets .prob_yes) ;
    daily_auto : dict par ticker. Les trois doivent produire les mêmes P(YES).
    """
    # backtest-like
    bt_records = [{"prob_yes": p} for p in PROBS]
    normed = normalize_event_probs([r["prob_yes"] for r in bt_records])
    for r, p in zip(bt_records, normed):
        r["prob_yes"] = p
    bt_out = [r["prob_yes"] for r in bt_records]

    # simulate-like
    class _Pred:
        def __init__(self, p):
            self.prob_yes = p
    sim_preds = [(None, None, _Pred(p)) for p in PROBS]
    normed = normalize_event_probs([p.prob_yes for _, _, p in sim_preds])
    for (_, _, p), val in zip(sim_preds, normed):
        p.prob_yes = val
    sim_out = [p.prob_yes for _, _, p in sim_preds]

    # daily_auto-like
    by_ticker = {f"T{i}": p for i, p in enumerate(PROBS)}
    tickers = list(by_ticker.keys())
    normed = normalize_event_probs([by_ticker[t] for t in tickers])
    by_ticker = dict(zip(tickers, normed))
    da_out = [by_ticker[t] for t in tickers]

    assert bt_out == sim_out == da_out == PROBS
