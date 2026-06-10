"""Revue 2026-06-10 A7 / finding M2 — marchés void exclus du scoring.

Avant : `outcome = 1 if result == "yes" else 0` -> un result "void"/"" était
compté comme NO (outcome=0), faussant Brier/P&L. Désormais un result ∉
{yes,no} marque le marché `void` et l'exclut du scoring (ni yes ni no).
"""
from __future__ import annotations

import json

import pytest

import finalize_run


OUR_TICKER = "KXLOWTNYC-26JUN11-B50.5"
BET_ID = "BID-void-1"


class _FakeEvent:
    def __init__(self, raw):
        self.raw = raw


def _fake_client_factory(result):
    class _FakeClient:
        def get_event(self, event_ticker):
            return _FakeEvent({"markets": [
                {"ticker": OUR_TICKER, "status": "settled", "result": result},
            ]})

        def snapshot_event(self, ev):
            return None
    return _FakeClient


def _v2_report():
    return {
        "schema_version": 2,
        "run_id": "999",
        "champion_at_time_of_run": "vendor_ensemble",
        "event": {
            "ticker": "KXLOWTNYC-26JUN11",
            "title": "NYC Low Temp 2026-06-11",
            "target_market_ticker": OUR_TICKER,
        },
        "models": [
            {"name": "vendor_ensemble", "role": "champion", "method": "ensemble",
             "p_yes": 0.6},
        ],
        "markets": [
            {
                "platform": "kalshi",
                "ticker": OUR_TICKER,
                "snapshot_pre": {"yes_mid": 0.5},
                "champion_position": {
                    "side": "YES", "n_contracts": 10, "entry_price": 0.5,
                    "ledger_bet_id": BET_ID,
                },
                "challenger_shadow_positions": [],
            }
        ],
    }


def _setup_ledger(root):
    ledger = root / "data" / "ledger" / "paper_bets.csv"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    header = ("bet_id,placed_at_utc,market_ticker,event_ticker,target_date,side,"
              "stake_usd,entry_price,prob_model,prob_market_implied,edge,method,"
              "spec,resolved_at_utc,resolution,pnl_usd\n")
    row = (f"{BET_ID},2026-06-10T00:00:00Z,{OUR_TICKER},KXLOWTNYC-26JUN11,"
           f"2026-06-11,YES,5.0,0.5,0.6,0.5,0.1,ensemble,desc,,,\n")
    ledger.write_text(header + row, encoding="utf-8")
    return ledger


@pytest.mark.parametrize("result", ["void", "", "VOID", "cancelled"])
def test_v2_void_result_excluded_from_scoring(tmp_path, monkeypatch, result):
    run_dir = tmp_path / "runs" / "999"
    run_dir.mkdir(parents=True)
    report = _v2_report()
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    monkeypatch.setattr(finalize_run, "ROOT", tmp_path)
    monkeypatch.setattr(finalize_run, "KalshiClient", _fake_client_factory(result))
    ledger = _setup_ledger(tmp_path)

    rc = finalize_run._finalize_v2(report, report_path, run_dir, dry_run=False)
    assert rc == 0  # finalisé comme void, pas une erreur

    written = json.loads(report_path.read_text(encoding="utf-8"))
    # Marché marqué void, surtout PAS "no".
    assert written["markets"][0]["resolution"]["outcome"] == "void"
    assert written["scoring"]["outcome"] == "void"
    assert written["scoring"]["n_datapoints"] == 0
    # Pas de Brier calculé (le marché est exclu du scoring).
    assert written["scoring"].get("by_model") in ({}, None)

    # Ligne ledger marquée resolved-void, P&L 0 (mise remboursée) -> pas de
    # heat fantôme, pas comptée comme perte.
    import csv
    rows = list(csv.DictReader(ledger.open(encoding="utf-8")))
    bet = next(r for r in rows if r["bet_id"] == BET_ID)
    assert bet["resolution"] == "void"
    assert bet["pnl_usd"] == "0.00"
    assert bet["resolved_at_utc"] != ""


def test_v2_yes_result_still_scored_as_outcome_1(tmp_path, monkeypatch):
    # Garde-fou de non-régression : un vrai "yes" doit toujours scorer (≠ void).
    run_dir = tmp_path / "runs" / "999"
    run_dir.mkdir(parents=True)
    report = _v2_report()
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    monkeypatch.setattr(finalize_run, "ROOT", tmp_path)
    monkeypatch.setattr(finalize_run, "KalshiClient", _fake_client_factory("yes"))
    _setup_ledger(tmp_path)

    rc = finalize_run._finalize_v2(report, report_path, run_dir, dry_run=False)
    assert rc == 0
    written = json.loads(report_path.read_text(encoding="utf-8"))
    assert written["scoring"]["outcome"] == "yes"
    assert written["scoring"]["n_datapoints"] == 1
    assert written["markets"][0]["resolution"]["outcome"] == "yes"
