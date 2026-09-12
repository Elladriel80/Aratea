"""Bout-en-bout hors ligne de scripts/eval_nbm_skill.py.

Le bulletin KNYC réel sert de prévision. La vérité CLI et les points
ensemble sont fabriqués. Aucun réseau.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from src.forecast.nbm_text import parse_bulletin

import eval_nbm_skill as ens

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "nbm_knyc_nbp.txt"


def test_eval_nbm_skill_offline(tmp_path, monkeypatch):
    forecasts = parse_bulletin(FIXTURE.read_text(encoding="utf-8"), ["KNYC"])
    assert forecasts
    extracted = tmp_path / "extracted.json"
    extracted.write_text(json.dumps([f.to_compact() for f in forecasts]), encoding="utf-8")

    # Vérité : max du 2 septembre = 76 (le seuil 50 % NBM), assez d'historique climato.
    cli_rows = []
    for year in range(2018, 2027):
        d = date(year, 1, 1)
        while d.year == year:
            hi = 76 if (d.month, d.day) == (9, 2) and year == 2026 else 70 + (d.month % 5)
            cli_rows.append({"station": "KNYC", "valid": d.isoformat(), "high": hi, "low": hi - 12})
            d += timedelta(days=1)
    truth_dir = tmp_path / "truth"
    truth_dir.mkdir()
    (truth_dir / "cli_daily.json").write_text(json.dumps(cli_rows), encoding="utf-8")
    skill_dir = truth_dir / "skill"
    skill_dir.mkdir()
    skill_dir.joinpath("forecast_points.json").write_text(json.dumps([
        {"station": "KNYC", "variable": "temp_max", "target": "2026-09-02", "lead": 1,
         "per_model": {"gfs_global": 74.0, "ecmwf_ifs025": 76.0}},
        {"station": "KNYC", "variable": "temp_max", "target": "2026-08-20", "lead": 1,
         "per_model": {"gfs_global": 70.0, "ecmwf_ifs025": 72.0}},
    ]), encoding="utf-8")

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
                "gfs_global": 74.0, "ecmwf_ifs025": 76.0}}}},
        }],
    }), encoding="utf-8")

    monkeypatch.setattr(ens, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens, "ROOT", tmp_path)
    monkeypatch.setattr(ens, "A1_SPLIT", date(2026, 8, 3))

    client = ens.NbmTextClient(cache_dir=tmp_path / "cache", extracted_path=extracted)
    monkeypatch.setattr(ens, "NbmTextClient", lambda: client)

    out_dir = tmp_path / "out"
    argv = [
        "eval_nbm_skill.py", "--skip-fetch", "--stations", "KNYC",
        "--leads", "1", "--split-date", "2026-08-03",
        "--out-dir", str(out_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert ens.main() == 0

    run = json.loads((out_dir / "nbm_skill.json").read_text(encoding="utf-8"))
    assert run["n_rows_standalone"] > 0
    assert run["n_rows_vs_ensemble"] > 0
    assert run["coverage"]["stations_found"] == ["KNYC"]
    report = (out_dir / "nbm_skill.md").read_text(encoding="utf-8")
    assert "NBM station contre le chiffre officiel" in report
    assert "Le modèle en ligne n'est pas changé" in report
