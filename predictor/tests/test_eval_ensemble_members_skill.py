"""Bout-en-bout hors ligne de scripts/eval_ensemble_members_skill.py."""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import eval_ensemble_members_skill as ens
from src.forecast.gefs_s3 import GefsDaily, GefsS3Client
from src.forecast.nbm_text import parse_bulletin

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "nbm_knyc_nbp.txt"


def test_eval_ensemble_members_offline(tmp_path, monkeypatch):
    from datetime import datetime, timezone
    issued = datetime(2026, 9, 1, 0, tzinfo=timezone.utc)
    target = date(2026, 9, 2)
    rows = []
    for m in range(31):
        rows.append(GefsDaily(
            station="KNYC", variable="temp_max", target=target, lead=1,
            issued=issued, member=m,
            value_f=74.0 + (2 if m < 10 else 0), n_windows=4,
        ))

    extracted = tmp_path / "extracted.json"
    extracted.write_text(json.dumps([r.to_compact() for r in rows]), encoding="utf-8")

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
    skill_dir.joinpath("station_bias.json").write_text(json.dumps([
        {"station": "KNYC", "variable": "temp_max", "lead": 1,
         "bias_f": 2.0, "sigma_f": 2.0, "n_train": 40},
    ]), encoding="utf-8")

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
                "gfs_global": 74.0, "ecmwf_ifs025": 76.0}}}},
        }],
    }), encoding="utf-8")

    monkeypatch.setattr(ens, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens, "ROOT", tmp_path)
    monkeypatch.setattr(ens.nbm_eval, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens.nbm_eval, "ROOT", tmp_path)
    monkeypatch.setenv("ARATEA_STATION_BIAS_PATH", str(skill_dir / "station_bias.json"))

    client = GefsS3Client(cache_dir=tmp_path / "gcache", extracted_path=extracted)
    monkeypatch.setattr(ens, "GefsS3Client", lambda: client)

    from src.forecast.nbm_client import NbmTextClient
    nbm_client = NbmTextClient(cache_dir=tmp_path / "ncache", extracted_path=nbm_extracted)
    monkeypatch.setattr(ens, "NbmTextClient", lambda: nbm_client)

    out_dir = tmp_path / "out"
    argv = [
        "eval_ensemble_members_skill.py", "--skip-fetch", "--skip-open-meteo",
        "--stations", "KNYC", "--leads", "1", "--split-date", "2026-08-03",
        "--out-dir", str(out_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert ens.main() == 0

    run = json.loads((out_dir / "ensemble_skill.json").read_text(encoding="utf-8"))
    assert run["n_rows_vs_ensemble"] > 0
    assert run["coverage"]["stations_found"] == ["KNYC"]
    report = (out_dir / "ensemble_skill.md").read_text(encoding="utf-8")
    assert "Vrais membres contre le chiffre officiel" in report
    assert "Le modèle en ligne n'est pas changé" in report
