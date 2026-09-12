"""Bout-en-bout hors ligne de scripts/eval_nowcast_skill.py."""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import eval_nowcast_skill as ens
from src.truth.asos import IemAsosClient, StationObs
from src.weather.hrrr_hourly import HrrrHourlyClient

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "asos_knyc.csv"


def test_eval_nowcast_skill_offline(tmp_path, monkeypatch):
    cli_rows = []
    points = []
    d = date(2026, 6, 1)
    while d <= date(2026, 9, 7):
        hi = 76 if d >= date(2026, 8, 3) else 72
        cli_rows.append({"station": "KNYC", "valid": d.isoformat(),
                         "high": hi, "low": hi - 12})
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

    obs = []
    d = date(2026, 6, 1)
    while d <= date(2026, 9, 7):
        for hour in range(5, 24):
            obs.append(StationObs(
                station="KNYC",
                valid=datetime(d.year, d.month, d.day, hour, 51, tzinfo=timezone.utc),
                tmp_f=70.0 + (hour / 10.0) + (4.0 if d >= date(2026, 8, 3) else 0.0),
                source="iem",
            ))
        d += timedelta(days=1)
    asos_extracted = tmp_path / "asos_extracted.json"
    asos_extracted.write_text(json.dumps([o.to_compact() for o in obs]), encoding="utf-8")

    times, values = [], []
    d = date(2026, 6, 1)
    while d <= date(2026, 9, 7):
        for hour in range(24):
            times.append(f"{d.isoformat()}T{hour:02d}:00")
            values.append(74.0 if d < date(2026, 8, 3) else 78.0)
        d += timedelta(days=1)
    hrrr_extracted = tmp_path / "hrrr_extracted.json"
    hrrr_extracted.write_text(json.dumps([{
        "station": "KNYC", "times": times, "values": values,
    }]), encoding="utf-8")

    records = []
    d = date(2026, 6, 10)
    while d <= date(2026, 9, 4):
        records.append({
            "ticker": f"KXHIGHTNYC-26{d.strftime('%b%d').upper()}-B76.5",
            "target_date": d.isoformat(),
            "snapshot_at": d.strftime("%Y%m%dT180000Z"),
            "location_key": "NYC",
            "variable": "temp_max",
            "lower": 76, "upper": 77,
            "yes_bid": 0.30, "yes_ask": 0.40, "yes_mid": 0.35,
            "predictions": {"ensemble": {"inputs": {"per_model_value": {
                "gfs_global": 70.0, "ecmwf_ifs025": 72.0}}}},
        })
        d += timedelta(days=1)
    pred_dir = tmp_path / "data" / "predictions"
    pred_dir.mkdir(parents=True)
    pred_dir.joinpath("forward_fake.json").write_text(
        json.dumps({"records": records}), encoding="utf-8")

    monkeypatch.setattr(ens, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens, "ROOT", tmp_path)
    monkeypatch.setattr(ens.nbm_eval, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens.nbm_eval, "ROOT", tmp_path)
    monkeypatch.setattr(ens.mkt, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens.mkt, "ROOT", tmp_path)

    asos_client = IemAsosClient(cache_dir=tmp_path / "acache", extracted_path=asos_extracted)
    hrrr_client = HrrrHourlyClient(cache_dir=tmp_path / "hcache", extracted_path=hrrr_extracted)
    monkeypatch.setattr(ens, "IemAsosClient", lambda: asos_client)
    monkeypatch.setattr(ens, "HrrrHourlyClient", lambda: hrrr_client)

    out_dir = tmp_path / "out"
    argv = [
        "eval_nowcast_skill.py", "--skip-fetch", "--skip-nws-probe",
        "--stations", "KNYC",
        "--start", "2026-06-01", "--end", "2026-09-07",
        "--split-date", "2026-08-03",
        "--out-dir", str(out_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert ens.main() == 0

    run = json.loads((out_dir / "nowcast_skill.json").read_text(encoding="utf-8"))
    assert run["n_rows"] > 0
    assert run["n_dates"] >= 10
    assert run["promote"] is False
    assert run["bot_skips_same_day"] is True
    assert "pas_assez_de_lectures" in run["skips"] or run["n_rows"] > 0
    hold = run["all"]["all"]
    assert "brier_nowcast" in hold
    assert "brier_station" in hold
    assert "brier_market" in hold
    report = (out_dir / "nowcast_skill.md").read_text(encoding="utf-8")
    assert "Thermomètre du jour" in report
    assert "Le modèle en ligne n'est pas changé" in report
    assert "Pas de pari avec de l'argent réel" in report
    assert "ne vise que demain" in report


def test_missing_obs_are_not_invented():
    rows = ens.score_records(
        [{
            "location_key": "NYC", "variable": "temp_max",
            "_target": date(2026, 8, 3),
            "_snap": datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc),
            "_pm": {"a": 70.0, "b": 72.0},
            "lower": 76, "upper": 77, "yes_mid": 0.3,
        }],
        {}, {}, {}, {"KNYC": {"tz": "America/New_York"}},
        ens.EmpiricalRemaining(), {},
        type("B", (), {"get": lambda *a, **k: (0.0, 1.0, 20)})(),
    )
    scored, skips = rows
    assert scored == []
    assert skips.get("pas_assez_de_lectures") == 1 or skips.get("pas_de_chiffre_officiel") == 1
