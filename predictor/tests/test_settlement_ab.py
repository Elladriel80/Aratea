"""Fenêtre d'hiver et Degré entier : A/B hors réseau, rien d'inventé."""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from src.truth.asos import StationObs
from src.truth.settlement_ab import (
    aggregate_station_days,
    aggregate_windows,
    cli_time_is_disputed,
    even_bin,
    in_disputed_hour,
    nearest_half,
    nws_int,
    parse_cli_clock,
    rounding_from_values,
    summarize_cli_times,
    summarize_rounding,
    summarize_window,
    wall_date,
)
from src.truth.lst_window import lst_date


def _obs(station: str, utc: datetime, tmp_f: float) -> StationObs:
    return StationObs(station=station, valid=utc, tmp_f=tmp_f, source="iem")


def _hourly(station: str, start: datetime, values: list[float]) -> list[StationObs]:
    return [
        _obs(station, start + timedelta(hours=i), v) for i, v in enumerate(values)
    ]


def test_parse_cli_clock_common_iem_formats():
    assert parse_cli_clock("420 PM") == (16, 20)
    assert parse_cli_clock("1159 PM") == (23, 59)
    assert parse_cli_clock("1258 AM") == (0, 58)
    assert parse_cli_clock("1200 AM") == (0, 0)
    assert parse_cli_clock("12 AM") == (0, 0)
    assert parse_cli_clock("12 PM") == (12, 0)
    assert parse_cli_clock("126 AM") == (1, 26)
    assert parse_cli_clock("101 AM") == (1, 1)
    assert parse_cli_clock("MM") is None
    assert parse_cli_clock(None) is None
    assert parse_cli_clock("") is None


def test_lst_vs_wall_on_documented_dst_midnight():
    # 00:30 EDT le 9 mai = 04:30 UTC = 23:30 EST le 8 → CLI du 8, murale du 9.
    utc = datetime(2026, 5, 9, 4, 30, tzinfo=timezone.utc)
    assert lst_date(utc, "America/New_York") == date(2026, 5, 8)
    assert wall_date(utc, "America/New_York") == date(2026, 5, 9)
    assert in_disputed_hour(utc, "America/New_York") is True
    assert in_disputed_hour(datetime(2026, 5, 9, 5, 30, tzinfo=timezone.utc),
                            "America/New_York") is False


def test_phoenix_has_no_disputed_hour():
    utc = datetime(2026, 7, 1, 7, 30, tzinfo=timezone.utc)  # 00:30 MST
    assert lst_date(utc, "America/Phoenix") == wall_date(utc, "America/Phoenix")
    assert in_disputed_hour(utc, "America/Phoenix") is False


def test_daily_max_moves_when_spike_is_in_disputed_hour():
    # 48 h à partir du 8 mai 00:00 UTC. Pic 90 °F à 04:00 UTC le 9 mai.
    start = datetime(2026, 5, 8, 0, tzinfo=timezone.utc)
    vals = [60.0] * 48
    vals[28] = 90.0
    rows = aggregate_windows(_hourly("KNYC", start, vals), "America/New_York", min_obs=18)
    by = {r.valid: r for r in rows}
    d8, d9 = by[date(2026, 5, 8)], by[date(2026, 5, 9)]
    assert d8.max_lst == 90.0 and d8.max_wall == 60.0
    assert d8.max_value_differs and d8.max_int_differs and d8.max_bin_differs
    assert d9.max_lst == 60.0 and d9.max_wall == 90.0


def test_winter_window_is_identical():
    start = datetime(2026, 1, 15, 0, tzinfo=timezone.utc)
    vals = [30.0] * 48
    vals[10] = 45.0
    rows = aggregate_windows(_hourly("KNYC", start, vals), "America/New_York", min_obs=18)
    assert rows
    assert all(not r.max_value_differs and not r.min_value_differs for r in rows)
    assert all(not r.dst_that_day for r in rows)


def test_partial_day_is_dropped_not_invented():
    start = datetime(2026, 5, 8, 5, tzinfo=timezone.utc)
    rows = aggregate_windows(_hourly("KNYC", start, [70.0] * 10), "America/New_York")
    assert rows == []


def test_rounding_integer_vs_half_and_bins():
    # 77.6 → entier NWS 78 (case 78-79) ; partie entière 77 (case 76-77).
    rows = rounding_from_values([
        ("KNYC", date(2026, 7, 1), "temp_max", 77.6, "fixture"),
        ("KNYC", date(2026, 7, 2), "temp_max", 76.0, "fixture"),
        ("KNYC", date(2026, 7, 3), "temp_min", 76.5, "fixture"),
    ])
    a, b, c = rows
    assert nws_int(77.6) == 78 and nearest_half(77.6) == 77.5
    assert a.int_vs_floor_differs and a.bin_vs_floor_differs
    assert a.bin_vs_half_floor_differs
    assert not b.int_vs_floor_differs and not b.bin_vs_floor_differs
    assert nws_int(76.5) == 77
    assert c.is_half_degree
    assert c.int_vs_banker_differs  # Python round(76.5) → 76
    assert even_bin(77) == (76, 77) and even_bin(78) == (78, 79)


def test_cli_disputed_only_during_dst():
    assert cli_time_is_disputed("1230 AM", date(2026, 7, 1), "America/New_York") is True
    assert cli_time_is_disputed("1230 AM", date(2026, 1, 15), "America/New_York") is False
    assert cli_time_is_disputed("330 PM", date(2026, 7, 1), "America/New_York") is False
    assert cli_time_is_disputed("1230 AM", date(2026, 7, 1), "America/Phoenix") is False
    assert cli_time_is_disputed("MM", date(2026, 7, 1), "America/New_York") is None


def test_summaries_count_zero_when_empty():
    w = summarize_window([])
    assert w["n_comparable_days"] == 0
    assert w["all"]["max_value_differs"] == 0
    r = summarize_rounding([])
    assert r["n"] == 0
    c = summarize_cli_times([])
    assert c["n_cli_days"] == 0 and c["high_disputed"] == 0


def test_aggregate_station_days_labels_station():
    start = datetime(2026, 7, 1, 0, tzinfo=timezone.utc)
    obs = _hourly("KPHX", start, [90.0] * 48)
    rows = aggregate_station_days(obs, min_obs=18)
    assert rows and all(r.station == "KPHX" for r in rows)
    assert all(not r.max_value_differs for r in rows)


def test_eval_script_offline(tmp_path, monkeypatch):
    import eval_settlement_window_rounding as ev

    # 3 jours NYC en DST, pic litigieux le 2e matin.
    obs = []
    t0 = datetime(2026, 7, 1, 0, tzinfo=timezone.utc)
    for i in range(72):
        tmp = 90.0 if i == 28 else 70.0  # 2 juillet 04:00 UTC
        obs.append(_obs("KNYC", t0 + timedelta(hours=i), tmp))
    asos_path = tmp_path / "extracted.json"
    asos_path.write_text(json.dumps([o.to_compact() for o in obs]), encoding="utf-8")
    cli_path = tmp_path / "cli_daily.json"
    cli_path.write_text(json.dumps([
        {"station": "KNYC", "valid": "2026-07-01", "high": 70, "low": 60,
         "high_time": "330 PM", "low_time": "600 AM"},
        {"station": "KNYC", "valid": "2026-07-01", "high": 90, "low": 60,
         "high_time": "1230 AM", "low_time": "MM"},
    ]), encoding="utf-8")
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", [
        "eval_settlement_window_rounding.py",
        "--skip-fetch", "--skip-ghcn",
        "--stations", "KNYC",
        "--asos-path", str(asos_path),
        "--cli-path", str(cli_path),
        "--out-dir", str(out),
        "--min-obs", "18",
    ])
    assert ev.main() == 0
    run = json.loads((out / "settlement_ab.json").read_text(encoding="utf-8"))
    assert run["champion_untouched"] is True
    s = run["fenetre_hiver"]["summary"]["all"]
    assert s["n_days"] >= 1
    assert s["max_value_differs"] >= 1
    assert run["degre_entier"]["asos_hourly"]["precision"]["n_readings"] == 72
    md = (out / "settlement_ab.md").read_text(encoding="utf-8")
    assert "Fenêtre d'hiver" in md
    assert "Degré entier" in md
    assert "—" not in md and "–" not in md
