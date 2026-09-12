"""Bout-en-bout hors ligne de scripts/eval_stacking_skill.py."""
from __future__ import annotations

import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import eval_stacking_skill as ens
from src.forecast.nbm_text import parse_bulletin

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "nbm_knyc_nbp.txt"


def test_eval_stacking_skill_offline(tmp_path, monkeypatch):
    cli_rows = []
    points = []
    for year in range(2018, 2027):
        d = date(year, 1, 1)
        while d.year == year:
            if year == 2026 and date(2026, 6, 1) <= d <= date(2026, 9, 7):
                hi = 76 if d >= date(2026, 8, 3) else 72 + (d.day % 3)
            else:
                hi = 70 + (d.month % 5)
            cli_rows.append({"station": "KNYC", "valid": d.isoformat(),
                             "high": hi, "low": hi - 12})
            d += timedelta(days=1)

    d = date(2026, 6, 1)
    while d <= date(2026, 9, 7):
        points.append({
            "station": "KNYC", "variable": "temp_max", "target": d.isoformat(),
            "lead": 1,
            "per_model": {"gfs_global": 70.0, "ecmwf_ifs025": 72.0},
        })
        d += timedelta(days=1)

    truth_dir = tmp_path / "truth"
    truth_dir.mkdir()
    (truth_dir / "cli_daily.json").write_text(json.dumps(cli_rows), encoding="utf-8")
    skill_dir = truth_dir / "skill"
    skill_dir.mkdir()
    skill_dir.joinpath("forecast_points.json").write_text(
        json.dumps(points), encoding="utf-8")

    forecasts = parse_bulletin(FIXTURE.read_text(encoding="utf-8"), ["KNYC"])
    nbm_extracted = tmp_path / "nbm_extracted.json"
    nbm_extracted.write_text(json.dumps([f.to_compact() for f in forecasts]), encoding="utf-8")

    records = []
    d = date(2026, 6, 10)
    while d <= date(2026, 9, 4):
        records.append({
            "ticker": f"KXHIGHTNYC-26{d.strftime('%b%d').upper()}-B72.5",
            "target_date": d.isoformat(),
            "snapshot_at": (d - timedelta(days=1)).strftime("%Y%m%dT180000Z"),
            "location_key": "NYC",
            "variable": "temp_max",
            "lower": 72, "upper": 73,
            "yes_bid": 0.30, "yes_ask": 0.40, "yes_mid": 0.35,
            "predictions": {"ensemble": {"inputs": {"per_model_value": {
                "gfs_global": 70.0, "ecmwf_ifs025": 72.0}}}},
        })
        d += timedelta(days=1)

    pred_dir = tmp_path / "data" / "predictions"
    pred_dir.mkdir(parents=True)
    pred_dir.joinpath("forward_fake.json").write_text(
        json.dumps({"records": records}), encoding="utf-8")

    ledger = tmp_path / "paper_bets.csv"
    with ledger.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "bet_id", "placed_at_utc", "market_ticker", "event_ticker",
            "target_date", "side", "stake_usd", "entry_price", "prob_model",
            "prob_market_implied", "edge", "method", "spec", "resolved_at_utc",
            "resolution", "pnl_usd", "algo_signal",
        ])
        w.writeheader()
        w.writerow({
            "bet_id": "t1", "placed_at_utc": "2026-06-10T18:00:00Z",
            "market_ticker": records[0]["ticker"], "event_ticker": "KXHIGHTNYC",
            "target_date": records[0]["target_date"], "side": "YES",
            "stake_usd": 1, "entry_price": 0.35, "prob_model": 0.2,
            "prob_market_implied": 0.35, "edge": -0.15, "method": "ensemble",
            "spec": "test", "resolved_at_utc": "2026-06-11T12:00:00Z",
            "resolution": "no", "pnl_usd": -1, "algo_signal": "no_bet",
        })

    monkeypatch.setattr(ens, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens, "ROOT", tmp_path)
    monkeypatch.setattr(ens.emos_eval, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens.emos_eval, "ROOT", tmp_path)
    monkeypatch.setattr(ens.nbm_eval, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens.nbm_eval, "ROOT", tmp_path)

    from src.forecast.nbm_client import NbmTextClient
    nbm_client = NbmTextClient(cache_dir=tmp_path / "ncache", extracted_path=nbm_extracted)
    monkeypatch.setattr(ens, "NbmTextClient", lambda: nbm_client)

    out_dir = tmp_path / "out"
    argv = [
        "eval_stacking_skill.py", "--stations", "KNYC",
        "--split-date", "2026-08-03", "--end", "2026-09-07",
        "--out-dir", str(out_dir), "--ledger", str(ledger),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert ens.main() == 0

    run = json.loads((out_dir / "stacking_skill.json").read_text(encoding="utf-8"))
    assert run["n_rows_train"] >= 50
    assert run["n_rows_holdout"] > 0
    assert run["weight"] is not None
    assert run["promote"] is False
    assert "ece_station" in run["calibration_train"]
    assert run["ledger"]["n_with_price"] == 1
    hold = run["market"]["holdout"]["all"]
    assert "brier_stack" in hold
    assert "brier_market" in hold
    assert "brier_station" in hold
    report = (out_dir / "stacking_skill.md").read_text(encoding="utf-8")
    assert "Combiner avec le prix du marché" in report
    assert "Le modèle en ligne n'est pas changé" in report
    assert "Pas de pari avec de l'argent réel" in report


def test_ledger_summary_missing_file(tmp_path):
    got = ens.load_ledger_summary(tmp_path / "absent.csv")
    assert got["present"] is False
    assert got["n_rows"] == 0
