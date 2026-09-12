"""Bout-en-bout hors ligne de scripts/eval_candle_recovery.py."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import eval_candle_recovery as ev


def test_eval_candle_recovery_offline(tmp_path, monkeypatch):
    X = []
    y = []
    meta = []
    d = date(2026, 4, 14)
    for i in range(6):
        X.append({
            "p_ensemble": 0.2,
            "p_consensus": 0.25,
            "p_climatology": 0.2,
            "p_forecast_blend": 0.3,
            "forecast_spread": 0.1,
            "days_ahead": 1.0,
        })
        y.append(0)
        meta.append({
            "ticker": f"KXLOWTNYC-26APR{14 + i:02d}-B57.5",
            "event_ticker": f"KXLOWTNYC-26APR{14 + i:02d}",
            "target_date": (d + timedelta(days=i)).isoformat(),
            "capture_at": (d + timedelta(days=i - 1)).strftime("%Y%m%dT180000Z"),
            "yes_mid": 0.11,
            "days_ahead": 1,
            "series_ticker": "KXLOWTNYC",
        })
    backfill = tmp_path / "backfill.json"
    backfill.write_text(json.dumps({"X": X, "y": y, "meta": meta}),
                        encoding="utf-8")

    pred_dir = tmp_path / "predictions"
    pred_dir.mkdir()
    pred_dir.joinpath("forward_fake.json").write_text(json.dumps({
        "snapshot_at": "20260413T192000Z",
        "records": [{
            "ticker": "KXLOWTNYC-26APR14-B57.5",
            "target_date": "2026-04-14",
            "snapshot_at": "20260413T192000Z",
            "yes_mid": 0.12,
            "lower": 57, "upper": 58,
        }],
    }), encoding="utf-8")

    out_dir = tmp_path / "out"
    monkeypatch.setattr(ev, "PRED_DIR", pred_dir)
    monkeypatch.setattr(ev, "ROOT", tmp_path)

    rc = ev.main([
        "--backfill", str(backfill),
        "--out-dir", str(out_dir),
        "--offline-only",
    ])
    assert rc == 0
    summary = json.loads((out_dir / "candle_recovery.json").read_text(encoding="utf-8"))
    assert summary["inrepo_backfill"]["n_rows"] == 6
    assert summary["inrepo_backfill"]["n_dates"] == 6
    assert summary["score_inrepo_backfill"]["brier_kalshi_mid"] is not None
    assert summary["ab_same_universe"] is None
    assert summary["live_snapshots"]["n_exact_180000Z"] == 0
    assert summary["live_snapshots"]["n_with_yes_mid"] == 1
    assert summary["catalogue_variables_renamed"] is False
    assert summary["promotion_gates"]["champion_changed"] is False
    md = (out_dir / "candle_recovery.md").read_text(encoding="utf-8")
    assert "On ne change pas le champion" in md
    assert "—" not in md
