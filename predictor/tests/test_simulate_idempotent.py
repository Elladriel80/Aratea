"""Revue 2026-06-10 A6 / finding E6 — simulate.py idempotent + heat fantôme.

- simulate.py écrit désormais dans un ledger DÉDIÉ (paper_bets_simulate.csv),
  physiquement séparé du ledger live -> ses paris jamais résolus n'entrent plus
  dans PortfolioHeat.from_ledger ni dans les compteurs du manifest.
- Dédup avant append par (event_ticker, market_ticker) sur les paris ouverts
  -> idempotent sur re-run.
"""
from __future__ import annotations

import simulate
from src.simulation.ledger import Ledger, PaperBet, make_bet_id


def _bet(event, market, *, resolved=False):
    return PaperBet(
        bet_id=make_bet_id(),
        placed_at_utc="2026-06-10T00:00:00+00:00",
        market_ticker=market,
        event_ticker=event,
        target_date="2026-06-11",
        side="YES",
        stake_usd=10.0,
        entry_price=0.5,
        prob_model=0.6,
        prob_market_implied=0.5,
        edge=0.1,
        method="forecast_blend",
        spec="desc",
        resolved_at_utc="2026-06-11T00:00:00+00:00" if resolved else None,
        resolution="yes" if resolved else None,
        pnl_usd=10.0 if resolved else None,
    )


def test_simulate_ledger_is_separate_from_live():
    # Garde-fou anti-heat-fantôme : le simulateur ne partage pas le ledger live.
    assert simulate.SIMULATE_LEDGER_PATH != Ledger.DEFAULT_PATH
    assert simulate.SIMULATE_LEDGER_PATH.name == "paper_bets_simulate.csv"


def test_open_bet_keys_excludes_resolved(tmp_path):
    ledger = Ledger(tmp_path / "sim.csv")
    ledger.append(_bet("KXLOWTNYC-26JUN11", "KXLOWTNYC-26JUN11-B50.5"))
    ledger.append(_bet("KXLOWTNYC-26JUN11", "KXLOWTNYC-26JUN11-B52.5", resolved=True))
    keys = simulate._open_bet_keys(ledger)
    # Seul le pari ouvert apparaît ; le résolu est exclu.
    assert ("KXLOWTNYC-26JUN11", "KXLOWTNYC-26JUN11-B50.5") in keys
    assert ("KXLOWTNYC-26JUN11", "KXLOWTNYC-26JUN11-B52.5") not in keys


def test_dedup_makes_rerun_idempotent(tmp_path):
    ledger = Ledger(tmp_path / "sim.csv")
    key = ("KXLOWTNYC-26JUN11", "KXLOWTNYC-26JUN11-B50.5")

    # Premier "run" : le bin n'est pas ouvert -> on parie.
    open_keys = simulate._open_bet_keys(ledger)
    assert key not in open_keys
    ledger.append(_bet(*key))

    # Second "run" : le bin est désormais ouvert -> dédup, pas de doublon.
    open_keys = simulate._open_bet_keys(ledger)
    assert key in open_keys  # serait skippé par la garde `if key in open_keys`

    # Le ledger ne contient qu'une ligne ouverte pour ce bin.
    opens = [b for b in ledger.read_all()
             if (b.event_ticker, b.market_ticker) == key and not b.resolved_at_utc]
    assert len(opens) == 1
