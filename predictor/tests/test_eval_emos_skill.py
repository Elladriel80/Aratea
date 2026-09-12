"""Bout-en-bout hors ligne de scripts/eval_emos_skill.py."""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import eval_emos_skill as ens
from src.forecast.nbm_text import parse_bulletin

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "nbm_knyc_nbp.txt"


def test_eval_emos_skill_offline(tmp_path, monkeypatch):
    cli_rows = []
    points = []
    # Assez de juin/juillet pour ajuster EMOS (lead 1, KNYC max).
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
        # Les modèles sous-estiment de ~2 °F, petit écart.
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

    pred_dir = tmp_path / "predictions"
    pred_dir.mkdir()
    pred_dir.joinpath("forward_fake.json").write_text(json.dumps({
        "records": [{
            "ticker": "KXHIGHTNYC-26SEP02-B76.5",
            "target_date": "2026-09-02",
            "snapshot_at": "20260901T180000Z",
            "location_key": "NYC",
            "variable": "temp_max",
            "lower": 76, "upper": 77,
            "yes_bid": 0.30, "yes_ask": 0.40, "yes_mid": 0.35,
            "predictions": {"ensemble": {"inputs": {"per_model_value": {
                "gfs_global": 70.0, "ecmwf_ifs025": 72.0}}}},
        }],
    }), encoding="utf-8")

    monkeypatch.setattr(ens, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens, "ROOT", tmp_path)
    monkeypatch.setattr(ens.nbm_eval, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens.nbm_eval, "ROOT", tmp_path)

    from src.forecast.nbm_client import NbmTextClient
    nbm_client = NbmTextClient(cache_dir=tmp_path / "ncache", extracted_path=nbm_extracted)
    monkeypatch.setattr(ens, "NbmTextClient", lambda: nbm_client)

    out_dir = tmp_path / "out"
    argv = [
        "eval_emos_skill.py", "--stations", "KNYC", "--leads", "1",
        "--split-date", "2026-08-03", "--end", "2026-09-07",
        "--out-dir", str(out_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert ens.main() == 0

    run = json.loads((out_dir / "emos_skill.json").read_text(encoding="utf-8"))
    assert run["n_rows_vs_ensemble"] > 0
    assert run["coverage"]["n_seasonal_groups"] >= 1
    overall = run["vs_ensemble"]["all"]["all"]
    assert "brier_emos_filled" in overall
    assert "brier_station" in overall
    report = (out_dir / "emos_skill.md").read_text(encoding="utf-8")
    assert "EMOS par station et par saison contre le chiffre officiel" in report
    assert "Le modèle en ligne n'est pas changé" in report
