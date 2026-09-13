"""Bout-en-bout hors ligne de scripts/eval_hrrr_morning_skill.py."""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
import eval_hrrr_morning_skill as ens
from src.weather.hrrr_morning import HrrrMorningClient, SOURCE


def test_eval_hrrr_morning_skill_offline(tmp_path, monkeypatch):
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

    extracted = []
    d = date(2026, 6, 1)
    while d <= date(2026, 9, 7):
        times, values = [], []
        for hour in range(12, 30):
            day = d if hour < 24 else d + timedelta(days=1)
            hh = hour if hour < 24 else hour - 24
            times.append(f"{day.isoformat()}T{hh:02d}:00")
            values.append(74.0 if d < date(2026, 8, 3) else 78.0)
        extracted.append({
            "station": "KNYC",
            "issued_date": d.isoformat(),
            "issued": f"{d.isoformat()}T12:00:00Z",
            "times": times,
            "values": values,
        })
        d += timedelta(days=1)
    hrrr_extracted = tmp_path / "hrrr_morning_extracted.json"
    hrrr_extracted.write_text(json.dumps(extracted), encoding="utf-8")

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
    monkeypatch.setattr(ens.nowcast_eval, "ROOT", tmp_path)
    monkeypatch.setattr(ens.nowcast_eval, "TRUTH_DIR", truth_dir)

    hrrr_client = HrrrMorningClient(
        cache_dir=tmp_path / "hcache", extracted_path=hrrr_extracted,
    )
    monkeypatch.setattr(ens, "HrrrMorningClient", lambda: hrrr_client)

    out_dir = tmp_path / "out"
    argv = [
        "eval_hrrr_morning_skill.py", "--skip-fetch",
        "--stations", "KNYC",
        "--start", "2026-06-01", "--end", "2026-09-07",
        "--split-date", "2026-08-03",
        "--out-dir", str(out_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert ens.main() == 0

    run = json.loads((out_dir / "hrrr_morning_skill.json").read_text(encoding="utf-8"))
    assert run["n_rows"] > 0
    assert run["n_dates"] >= 10
    assert run["promote"] is False
    assert run["champion_unchanged"] is True
    assert run["source"] == SOURCE
    assert run["verdict"] in ("testée ça aide", "testée ça n'aide pas", "bloquée")
    hold = run["all"]["all"]
    assert "brier_hrrr" in hold
    assert "brier_station" in hold
    assert "brier_market" in hold
    report = (out_dir / "hrrr_morning_skill.md").read_text(encoding="utf-8")
    assert "HRRR du matin même" in report
    assert "Le modèle en ligne n'est pas changé" in report
    assert "Pas de pari avec de l'argent réel" in report
    assert "previous_day1" not in report or "pas la veille" in report.lower() or "Ce n'est pas la veille" in report


def test_score_market_skips_price_before_run_is_public():
    rows, skips = ens.score_market(
        [{
            "location_key": "NYC", "variable": "temp_max",
            "_target": date(2026, 8, 3),
            "_snap": datetime(2026, 8, 3, 12, 30, tzinfo=timezone.utc),
            "_pm": {"a": 70.0, "b": 72.0},
            "lower": 76, "upper": 77, "yes_mid": 0.3,
        }],
        {("KNYC", date(2026, 8, 3)): {
            "times": ["2026-08-03T15:00"], "values": [80.0],
        }},
        {("KNYC", date(2026, 8, 3)): {"high": 80, "low": 60}},
        {"KNYC": {"tz": "America/New_York"}},
        {("KNYC", "temp_max"): 1.5},
        type("B", (), {"get": lambda *a, **k: (0.0, 1.0, 20)})(),
    )
    assert rows == []
    assert skips.get("prix_avant_le_run_du_matin") == 1


def test_score_market_does_not_invent_missing_run():
    rows, skips = ens.score_market(
        [{
            "location_key": "NYC", "variable": "temp_max",
            "_target": date(2026, 8, 3),
            "_snap": datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc),
            "_pm": {"a": 70.0, "b": 72.0},
            "lower": 76, "upper": 77, "yes_mid": 0.3,
        }],
        {},
        {("KNYC", date(2026, 8, 3)): {"high": 80, "low": 60}},
        {"KNYC": {"tz": "America/New_York"}},
        {},
        type("B", (), {"get": lambda *a, **k: (0.0, 1.0, 20)})(),
    )
    assert rows == []
    assert skips.get("pas_de_run_du_matin") == 1
