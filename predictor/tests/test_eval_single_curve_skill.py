"""Bout-en-bout hors ligne de scripts/eval_single_curve_skill.py."""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import eval_single_curve_skill as ev


def test_eval_single_curve_skill_offline(tmp_path, monkeypatch):
    cli_rows = []
    points = []
    for year in range(2018, 2027):
        d = date(year, 1, 1)
        while d.year == year:
            if year == 2026 and date(2026, 6, 1) <= d <= date(2026, 9, 7):
                hi = 76 if d >= date(2026, 8, 3) else 72 + (d.day % 3)
            else:
                hi = 70 + (d.month % 5)
            cli_rows.append({
                "station": "KNYC", "valid": d.isoformat(),
                "high": hi, "low": hi - 12,
            })
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

    records = []
    d = date(2026, 6, 20)
    while d <= date(2026, 9, 4):
        for lead, lo, hi, mid in (
            (1, 72, 73, 0.35),
            (0, 74, 75, 0.40),
            (1, None, 71, 0.05),
            (1, 80, None, 0.08),
        ):
            snap = d - timedelta(days=lead)
            records.append({
                "ticker": f"KXHIGHTNYC-{d.isoformat()}-L{lead}-{lo}-{hi}",
                "event_ticker": f"KXHIGHTNYC-{d.isoformat()}",
                "target_date": d.isoformat(),
                "snapshot_at": snap.strftime("%Y%m%dT180000Z"),
                "location_key": "NYC",
                "variable": "temp_max",
                "lower": lo, "upper": hi,
                "yes_bid": mid - 0.05, "yes_ask": mid + 0.05, "yes_mid": mid,
                "predictions": {
                    "ensemble": {
                        "prob_yes": 0.25,
                        "inputs": {
                            "per_model_value": {
                                "gfs_global": 70.0, "ecmwf_ifs025": 72.0,
                            },
                            "p_climato": 0.18,
                        },
                    }
                },
            })
        d += timedelta(days=1)

    pred_dir = tmp_path / "predictions"
    pred_dir.mkdir()
    pred_dir.joinpath("forward_fake.json").write_text(
        json.dumps({"records": records}), encoding="utf-8")

    monkeypatch.setattr(ev, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ev, "ROOT", tmp_path)

    out_dir = tmp_path / "out"
    argv = [
        "eval_single_curve_skill.py",
        "--stations", "KNYC",
        "--skill-leads", "1",
        "--market-leads", "0,1",
        "--split-date", "2026-08-03",
        "--end", "2026-09-07",
        "--out-dir", str(out_dir),
        "--pred-dir", str(pred_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert ev.main() == 0

    run = json.loads((out_dir / "curve_skill.json").read_text(encoding="utf-8"))
    assert run["schema"] == "single_curve_a5/1"
    assert run["investigation"]["renormalize"] is False
    assert run["investigation"]["champion_core"] == "single_gaussian_cdf_cut"
    skill = run["skill"]["overall"]["all"]
    assert skill["n_bins"] > 0 and skill["n_dates"] >= 30
    # Hors marché, champion = H1 (déjà une seule courbe).
    assert abs(skill["brier_p_champion"] - skill["brier_p_h1"]) < 1e-12
    market = run["market"]["overall"]["all"]
    assert market["n_bins"] > 0 and "brier_p_mid" in market
    assert "0" in run["market"]["by_lead"] and "1" in run["market"]["by_lead"]
    assert run["market"]["consistency"]["n_events"] > 0
    report = (out_dir / "curve_skill.md").read_text(encoding="utf-8")
    assert "Une seule courbe" in report
    assert "Champion en ligne inchangé" in report
    assert ev.horizon_blend(0.2, 0.8, 0) == 0.2
