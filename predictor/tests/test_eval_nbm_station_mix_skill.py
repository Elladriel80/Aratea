"""Bout-en-bout hors ligne de scripts/eval_nbm_station_mix_skill.py."""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import eval_nbm_station_mix_skill as ens
from src.forecast.nbm_text import parse_bulletin
from src.truth.stacking import clip_prob

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "nbm_knyc_nbp.txt"


def _clone_nbm(base_rows: list[dict], target: date, lead: int = 1) -> list[dict]:
    issued = (target - timedelta(days=lead)).strftime("%Y-%m-%dT13:00:00Z")
    out = []
    for row in base_rows:
        r = dict(row)
        r["target"] = target.isoformat()
        r["issued"] = issued
        r["lead"] = lead
        out.append(r)
    return out


def test_mix_average_is_midpoint():
    assert abs(ens.mix_average(0.2, 0.8) - 0.5) < 1e-12
    assert ens.mix_average(-1.0, 0.0) == clip_prob(0.0)


def test_eval_nbm_station_mix_skill_offline(tmp_path, monkeypatch):
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
        json.dumps(points), encoding="utf-8"
    )

    forecasts = parse_bulletin(FIXTURE.read_text(encoding="utf-8"), ["KNYC"])
    base = [f.to_compact() for f in forecasts if f.variable == "temp_max"]
    cloned = []
    d = date(2026, 6, 10)
    while d <= date(2026, 9, 7):
        cloned.extend(_clone_nbm(base, d, lead=1))
        d += timedelta(days=1)
    nbm_extracted = tmp_path / "nbm_extracted.json"
    nbm_extracted.write_text(json.dumps(cloned), encoding="utf-8")

    records = []
    d = date(2026, 6, 20)
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
        json.dumps({"records": records}), encoding="utf-8"
    )

    monkeypatch.setattr(ens, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens, "ROOT", tmp_path)
    monkeypatch.setattr(ens.emos_eval, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens.emos_eval, "ROOT", tmp_path)
    monkeypatch.setattr(ens.nbm_eval, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens.nbm_eval, "ROOT", tmp_path)
    monkeypatch.setattr(ens.pit, "TRUTH_DIR", truth_dir)
    monkeypatch.setattr(ens.pit, "ROOT", tmp_path)

    from src.forecast.nbm_client import NbmTextClient
    nbm_client = NbmTextClient(cache_dir=tmp_path / "ncache", extracted_path=nbm_extracted)
    monkeypatch.setattr(ens, "NbmTextClient", lambda: nbm_client)

    out_dir = tmp_path / "out"
    argv = [
        "eval_nbm_station_mix_skill.py", "--stations", "KNYC", "--leads", "1",
        "--split-date", "2026-08-03", "--end", "2026-09-07",
        "--out-dir", str(out_dir),
    ]
    monkeypatch.setattr(sys, "argv", argv)
    assert ens.main() == 0

    run = json.loads((out_dir / "nbm_mix_skill.json").read_text(encoding="utf-8"))
    assert run["n_rows_holdout"] > 0
    assert run["n_rows_train"] >= 50
    assert run["weight"] is not None
    assert run["promote"] is False
    assert run["live_champion_changed"] is False
    overall = run["vs_ensemble"]["all"]["all"]
    assert "brier_avg" in overall
    assert "brier_station" in overall
    assert "brier_nbm" in overall
    assert "brier_raw" in overall
    assert "brier_fit" in overall
    assert run["n_dates_market_a2"] > 0
    report = (out_dir / "nbm_mix_skill.md").read_text(encoding="utf-8")
    assert "Mélanger NBM et la correction ville" in report
    assert "Le modèle en ligne n'est pas changé" in report
    assert "Pas de pari avec de l'argent réel" in report


def test_decide_promote_never_true():
    ok, reason = ens.decide_promote(40, 0.10, 0.12, 0.13, "moyenne")
    assert ok is False
    assert "ne promeut pas" in reason
    ok, reason = ens.decide_promote(13, 0.10, 0.12, 0.13, "moyenne")
    assert ok is False
    assert "13 jours" in reason
