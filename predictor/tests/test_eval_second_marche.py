"""Mesure Second marché : parseurs, jointure exacte, script hors réseau."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import eval_second_marche as ens
from src.truth.second_marche import (
    CITY_MAPS, attach_blends, bin_key, event_target_date, fit_gap_weight,
    outcome_from_cli, parse_pm_bin, pm_site_icao, price_at_or_before,
    same_bin, slice_metrics, snapshot_unix, yes_token_id,
)


def test_parse_pm_bin_titles():
    assert parse_pm_bin("81°F or below") == (None, 81)
    assert parse_pm_bin("100°F or higher") == (100, None)
    assert parse_pm_bin("90-91°F") == (90, 91)
    assert parse_pm_bin("Will the highest temperature in Atlanta be between 82-83°F on September 11?") == (82, 83)
    assert parse_pm_bin("") is None


def test_site_and_token_and_date():
    assert pm_site_icao("https://www.weather.gov/wrh/timeseries?site=klga") == "KLGA"
    assert pm_site_icao("no site here") is None
    assert yes_token_id({"clobTokenIds": json.dumps(["aaa", "bbb"])}) == "aaa"
    assert event_target_date({"eventDate": "2026-09-11"}) == date(2026, 9, 11)
    ts = snapshot_unix("20260910T202833Z")
    assert ts is not None
    from datetime import datetime, timezone
    assert ts == int(datetime(2026, 9, 10, 20, 28, 33, tzinfo=timezone.utc).timestamp())


def test_exact_bin_match_rejects_shifted_ladder():
    # Kalshi Atlanta 11 sept. : 89-90. Polymarket : 88-89 et 90-91.
    assert same_bin(89, 90, 89, 90)
    assert not same_bin(89, 90, 88, 89)
    assert not same_bin(89, 90, 90, 91)
    assert bin_key(89.0, 90.0) == (89, 90)


def test_price_at_or_before_does_not_invent():
    hist = [{"t": 100, "p": 0.20}, {"t": 200, "p": 0.40}, {"t": 300, "p": 0.80}]
    assert price_at_or_before(hist, 200) == (0.40, 200)
    assert price_at_or_before(hist, 199) == (0.20, 100)
    assert price_at_or_before(hist, 50) is None
    assert price_at_or_before([], 200) is None
    assert price_at_or_before([{"t": 100, "p": 1.5}], 200) is None


def test_cli_outcome_inclusive_bin():
    assert outcome_from_cli(90.0, 89, 90) is True
    assert outcome_from_cli(88.0, 89, 90) is False
    assert outcome_from_cli(88.0, None, 88) is True


def test_city_maps_are_explicit():
    slugs = {c.slug for c in CITY_MAPS}
    assert "atlanta" in slugs and "dallas" in slugs
    atl = next(c for c in CITY_MAPS if c.slug == "atlanta")
    dal = next(c for c in CITY_MAPS if c.slug == "dallas")
    assert atl.same_station_note is True
    assert dal.same_station_note is False
    assert dal.kalshi_icao == "KDFW" and dal.pm_icao_note == "KDAL"


def test_eval_second_marche_offline(tmp_path, monkeypatch):
    cli_rows = []
    d = date(2026, 6, 1)
    while d <= date(2026, 9, 7):
        cli_rows.append({"station": "KATL", "valid": d.isoformat(), "high": 90})
        d += timedelta(days=1)
    truth = tmp_path / "cli_daily.json"
    truth.write_text(json.dumps(cli_rows), encoding="utf-8")

    records = []
    d = date(2026, 6, 10)
    while d <= date(2026, 9, 4):
        records.append({
            "ticker": f"KXHIGHTATL-26{d.strftime('%b%d').upper()}-B89.5",
            "target_date": d.isoformat(),
            "snapshot_at": (d - timedelta(days=1)).strftime("%Y%m%dT180000Z"),
            "location_key": "ATLANTA",
            "variable": "temp_max",
            "lower": 89, "upper": 90,
            "yes_bid": 0.30, "yes_ask": 0.40, "yes_mid": 0.35,
            "subtitle": "89° to 90°",
        })
        d += timedelta(days=1)
    pred_dir = tmp_path / "predictions"
    pred_dir.mkdir()
    pred_dir.joinpath("forward_fake.json").write_text(
        json.dumps({"records": records}), encoding="utf-8")

    events = []
    d = date(2026, 6, 10)
    while d <= date(2026, 9, 4):
        events.append({
            "slug": f"highest-temperature-in-atlanta-on-{d.isoformat()}",
            "title": f"Highest temperature in Atlanta on {d.isoformat()}?",
            "city_slug": "atlanta",
            "target": d.isoformat(),
            "pm_icao": "KATL",
            "n_markets": 1,
            "markets": [{
                "title": "89-90°F",
                "lower": 89, "upper": 90,
                "yes_token": f"tok-{d.isoformat()}",
            }],
            "closed": True,
        })
        d += timedelta(days=1)
    extract = tmp_path / "extracted_events.json"
    extract.write_text(json.dumps(events), encoding="utf-8")

    def fake_hist(token: str, allow_network: bool):
        # Case 89-90 vraie (max=90). Polymarket 0,80 ; Kalshi 0,35.
        return [{"t": 1, "p": 0.80}]

    monkeypatch.setattr(ens, "fetch_history", fake_hist)
    monkeypatch.setattr(ens, "discover_open_high_cities", lambda allow_network: {
        "n_events": 1, "n_cities_sept12": 1,
        "cities_sept12": ["Atlanta"], "source": "fixture",
    })
    monkeypatch.setattr(ens, "TRUTH_DIR", tmp_path)
    monkeypatch.setattr(ens, "CACHE_DIR", tmp_path / "cache")

    out = tmp_path / "out"
    argv = [
        "eval_second_marche.py", "--skip-fetch",
        "--pred-dir", str(pred_dir),
        "--truth", str(truth),
        "--out-dir", str(out),
        "--extract", str(extract),
        "--joined", str(out / "joined_rows.json"),
    ]
    monkeypatch.setattr("sys.argv", argv)
    assert ens.main() == 0

    report = json.loads((out / "second_marche_skill.json").read_text(encoding="utf-8"))
    prim = report["primary"]
    assert prim["n_bins"] > 50
    assert prim["n_dates"] >= 30
    assert prim["brier_pm"] is not None
    assert prim["brier_kalshi"] is not None
    assert prim["brier_pm"] < prim["brier_kalshi"]
    md = (out / "second_marche_skill.md").read_text(encoding="utf-8")
    assert "Second marché" in md
    assert "—" not in md and "–" not in md


def test_blend_and_metrics_helpers():
    rows = [
        {"kalshi_key": "ATLANTA", "target": "2026-08-01", "p_kalshi": 0.2,
         "p_pm": 0.8, "outcome": True, "lead": 1},
        {"kalshi_key": "ATLANTA", "target": "2026-08-02", "p_kalshi": 0.8,
         "p_pm": 0.2, "outcome": False, "lead": 1},
    ]
    w = fit_gap_weight(rows * 30)
    attach_blends(rows, w)
    assert rows[0]["p_avg"] == 0.5
    m = slice_metrics(rows)
    assert m["n_bins"] == 2
    assert abs(m["mean_abs_gap"] - 0.6) < 1e-12
