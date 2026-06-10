"""Revue 2026-06-10 A1 — dédup backtest par ticker.

Couvre les trois chemins qui gonflaient la gate Phase B en cas de re-run :
- `_aggregate_sfo_high.collect` : dédup par market_ticker (replay le + récent).
- `backtest._append_backtest_ledger_row` : upsert par market_ticker.
- `build_dashboard_manifest._backtest_ledger_summary` : N sur tickers uniques.

Critère de la revue : « agréger deux fois le même run → N inchangé ».
"""
from __future__ import annotations

import csv
import json

import _aggregate_sfo_high as agg
import backtest
import build_dashboard_manifest as manifest


def _write_report(runs_bt, day, seq, ticker, *, ts_replay, p_model, outcome,
                  series="KXHIGHTSFO", event="KXHIGHTSFO-26JUN06"):
    run_dir = runs_bt / day / seq
    run_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "ts_replay_utc": ts_replay,
        "as_of_date": day,
        "target_date": day,
        "event": {"series": series, "ticker": event},
        "markets": [
            {
                "ticker": ticker,
                "predictions_by_model": {"climatology": p_model},
                "resolution": {"outcome_int": outcome},
            }
        ],
    }
    (run_dir / "report.json").write_text(json.dumps(report), encoding="utf-8")


def test_collect_dedups_by_ticker_keeping_latest_replay(tmp_path, monkeypatch):
    runs_bt = tmp_path / "runs_backtest"
    # Run initial : 2 tickers distincts.
    _write_report(runs_bt, "2026-06-06", "0001", "KXHIGHTSFO-26JUN06-T75",
                  ts_replay="2026-06-06T07:00:00Z", p_model=0.30, outcome=0)
    _write_report(runs_bt, "2026-06-06", "0002", "KXHIGHTSFO-26JUN06-T80",
                  ts_replay="2026-06-06T07:00:00Z", p_model=0.60, outcome=1)
    monkeypatch.setattr(agg, "RUNS_BT", runs_bt)

    rows = agg.collect("KXHIGHTSFO")
    assert len(rows) == 2
    n_before = len(rows)

    # Replay du MÊME run (mêmes tickers), ts plus récent, p_model différents.
    _write_report(runs_bt, "2026-06-06", "0003", "KXHIGHTSFO-26JUN06-T75",
                  ts_replay="2026-06-06T09:00:00Z", p_model=0.35, outcome=0)
    _write_report(runs_bt, "2026-06-06", "0004", "KXHIGHTSFO-26JUN06-T80",
                  ts_replay="2026-06-06T09:00:00Z", p_model=0.65, outcome=1)

    rows2 = agg.collect("KXHIGHTSFO")
    # N inchangé malgré le double comptage potentiel.
    assert len(rows2) == n_before == 2
    # Le replay le plus récent est conservé.
    by_ticker = {r["ticker"]: r for r in rows2}
    assert by_ticker["KXHIGHTSFO-26JUN06-T75"]["p_model"] == 0.35
    assert by_ticker["KXHIGHTSFO-26JUN06-T80"]["p_model"] == 0.65


def test_append_ledger_row_upserts_by_ticker(tmp_path, monkeypatch):
    ledger = tmp_path / "paper_bets_backtest.csv"
    monkeypatch.setattr(backtest, "LEDGER_BACKTEST_PATH", ledger)

    base = {
        "backtest_id": "backtest_20260606_0001",
        "market_ticker": "KXHIGHTSFO-26JUN06-T75",
        "mode": "replay_climatology",
        "prob_model": 0.30,
        "outcome": 0,
    }
    backtest._append_backtest_ledger_row(dict(base))
    # Replay : même ticker, prob différente.
    backtest._append_backtest_ledger_row({**base, "prob_model": 0.35,
                                          "backtest_id": "backtest_20260606_0009"})
    # Un autre ticker.
    backtest._append_backtest_ledger_row({**base,
                                          "market_ticker": "KXHIGHTSFO-26JUN06-T80",
                                          "prob_model": 0.60})

    with ledger.open(encoding="utf-8", newline="") as f:
        data_rows = list(csv.DictReader(f))
    # 2 tickers uniques, pas 3 lignes.
    assert len(data_rows) == 2
    by_ticker = {r["market_ticker"]: r for r in data_rows}
    # La ligne conservée pour T75 est le replay le plus récent.
    assert by_ticker["KXHIGHTSFO-26JUN06-T75"]["prob_model"] == "0.35"
    assert by_ticker["KXHIGHTSFO-26JUN06-T75"]["backtest_id"] == "backtest_20260606_0009"


def test_ledger_summary_counts_unique_tickers(tmp_path, monkeypatch):
    ledger = tmp_path / "paper_bets_backtest.csv"
    fieldnames = backtest._ledger_fieldnames()
    rows = [
        {"market_ticker": "T-A", "mode": "replay_climatology"},
        {"market_ticker": "T-A", "mode": "replay_climatology"},  # doublon
        {"market_ticker": "T-B", "mode": "replay_climatology"},
        {"market_ticker": "T-C", "mode": "replay_naive_ensemble"},
    ]
    with ledger.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    monkeypatch.setattr(manifest, "PAPER_BETS_BACKTEST_CSV", ledger)

    summary = manifest._backtest_ledger_summary()
    # 3 tickers uniques au total (T-A compté une fois), 2 strict, 1 naive.
    assert summary["n_total"] == 3
    assert summary["n_strict_point_in_time"] == 2
    assert summary["n_naive_excluded"] == 1
    # by_mode reste un comptage de lignes brut (informationnel).
    assert summary["by_mode"]["replay_climatology"] == 3
