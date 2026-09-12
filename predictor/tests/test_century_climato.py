"""Tests hors réseau : parse GHCN, couverture, tendance, fade, script."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from src.truth.century import (
    empirical_prob, fade_trigger, index_by_date, linear_slope, mutual_station_tails,
    trend_report, values_for_window, year_to_year_swing,
)
from src.truth.ghcn_daily import (
    ICAO_TO_GHCN, GhcnDay, coverage_from_days, parse_dly, tenths_c_to_f,
    tenths_mm_to_inches,
)
from src.truth.iem_cli import kalshi_stations
from src.truth.synthetic_bins import Bin


def test_icao_map_covers_the_eighteen_kalshi_stations():
    st = kalshi_stations()
    assert set(ICAO_TO_GHCN) == set(st)
    assert ICAO_TO_GHCN["KNYC"]["ghcn_id"] == "USW00094728"
    assert ICAO_TO_GHCN["KMDW"]["ghcn_id"] == "USW00014819"
    assert ICAO_TO_GHCN["KDEN"]["ghcn_id"] == "USW00003017"
    assert ICAO_TO_GHCN["KAUS"]["ghcn_id"] == "USW00013904"


def test_tenths_c_to_f_matches_nws_half_up():
    assert tenths_c_to_f(0) == 32          # 0.0 °C
    assert tenths_c_to_f(100) == 50        # 10.0 °C
    assert tenths_c_to_f(272) == 81        # 27.2 °C → 80.96 → 81
    assert tenths_c_to_f(-50) == 23        # -5.0 °C
    # 24.15 °C = 75.47 °F → 75 ; 24.20 °C = 75.56 °F → 76
    assert tenths_c_to_f(241) == 75
    assert tenths_c_to_f(242) == 76


def _dly_line(gid: str, year: int, month: int, elem: str, values: list[tuple[int, str]]) -> str:
    """Construit une ligne .dly. values = 31 × (val, qflag)."""
    assert len(values) == 31
    body = "".join(f"{val:5d} {q} " for val, q in values)
    return f"{gid}{year:04d}{month:02d}{elem}{body}"


def test_parse_dly_skips_missing_flagged_and_impossible_days():
    gid = "USW00094728"
    # janvier : jour 1 = 100 (10.0 °C), jour 2 manquant, jour 3 QFLAG=I, reste -9999
    jan = [(100, " "), (-9999, " "), (110, "I")] + [(-9999, " ")] * 28
    # février 2021 (non bissextile) : 29-31 doivent être ignorés même si remplis
    feb = [(0, " ")] * 28 + [(50, " "), (50, " "), (50, " ")]
    text = "\n".join([
        _dly_line(gid, 2021, 1, "TMAX", jan),
        _dly_line(gid, 2021, 1, "TMIN", [(0, " ")] * 31),
        _dly_line(gid, 2021, 2, "TMAX", feb),
        _dly_line(gid, 2021, 2, "PRCP", [(10, " ")] * 31),   # ignoré
    ])
    days = parse_dly(text, "KNYC", gid)
    highs = {d.valid: d.high_f for d in days if d.high_f is not None}
    assert highs[date(2021, 1, 1)] == 50
    assert date(2021, 1, 2) not in highs
    assert date(2021, 1, 3) not in highs          # QFLAG
    assert all(not (d.month == 2 and d.day == 29) for d in highs)
    assert date(2021, 2, 1) in highs
    assert all(d.station == "KNYC" for d in days)


def test_coverage_counts_only_observed_span():
    days = [
        GhcnDay("K", "U", date(2000, 1, 1), 40, 20),
        GhcnDay("K", "U", date(2000, 1, 3), 42, None),   # 2 janv. manquant
        GhcnDay("K", "U", date(2000, 1, 4), None, 21),    # max manquant
    ]
    c = coverage_from_days(days, "temp_max")
    assert c["first"] == "2000-01-01" and c["last"] == "2000-01-03"
    assert c["n_days"] == 2 and c["span_days"] == 3 and c["missing_days"] == 1
    assert c["first_year"] == 2000 and c["n_years_with_data"] == 1
    empty = coverage_from_days([], "temp_max")
    assert empty["n_days"] == 0 and empty["first"] is None and empty["missing_days"] is None


def test_window_is_point_in_time():
    days = []
    for y in (2023, 2024, 2025, 2026):
        days.append(GhcnDay("K", "U", date(y, 8, 3), 70 + (y - 2023), 50))
    by = index_by_date(days)
    vals = values_for_window(by, "temp_max", date(2026, 8, 3), 0, 2026)
    assert vals == [70, 71, 72]          # 2026 exclu
    assert values_for_window(by, "temp_max", date(2023, 8, 3), 0, 2023) == []
    assert values_for_window(by, "temp_max", date(2026, 8, 3), 0, 2026, years_back=2) == [71, 72]


def test_empirical_prob_and_fade_rule():
    # 20 fois 76, 5 fois 80 → bin 76-77 ≈ 20/25
    vals = [76] * 20 + [80] * 5
    p = empirical_prob(vals, Bin(76, 77))
    assert p is not None and 0.75 < p < 0.85
    assert empirical_prob([76] * 5, Bin(76, 77)) is None   # trop peu
    assert fade_trigger(0.80, 0.30) is True
    assert fade_trigger(0.80, 0.50) is False
    assert fade_trigger(0.50, 0.20) is False
    assert fade_trigger(0.80, None) is False


def test_trend_slope_and_short_record():
    # y = 50 + 0.1 * (year - 1980) → +1 °F / décennie
    pairs = [(1980 + i, 50.0 + 0.1 * i) for i in range(40)]
    sl = linear_slope(pairs)
    assert sl is not None
    assert abs(sl["slope_f_per_decade"] - 1.0) < 1e-9
    assert sl["n_years"] == 40
    assert linear_slope(pairs[:5]) is None
    days = [GhcnDay("K", "U", date(2020, 1, 1) + timedelta(days=i), 70, 50)
            for i in range(20)]
    tr = trend_report(days, "temp_max")
    assert tr["n_complete_years"] == 0 and tr["slope"] is None


def test_precip_parse_and_mutual_tails():
    assert abs(tenths_mm_to_inches(254) - 1.0) < 1e-9
    gid = "USW00000000"
    # janvier 2020 : 31 jours, 3 jours ≥ 100 °F, 2 gel, pluie 0.1 in le jour 1
    tmax = [(400, " ")] * 3 + [(200, " ")] * 28          # 104 °F puis 68 °F
    tmin = [(-50, " ")] * 2 + [(100, " ")] * 29          # 23 °F puis 50 °F
    prcp = [(254, " ")] + [(0, " ")] * 30
    text = "\n".join([
        _dly_line(gid, 2020, 1, "TMAX", tmax),
        _dly_line(gid, 2020, 1, "TMIN", tmin),
        _dly_line(gid, 2020, 1, "PRCP", prcp),
    ])
    days = parse_dly(text, "KTST", gid)
    assert days[0].precip_in is not None and abs(days[0].precip_in - 1.0) < 1e-9
    # pas assez d'année complète (31 < 300) → queues vides
    empty = mutual_station_tails(days)
    assert empty["heat"]["n_complete_years"] == 0

    long_days = []
    for i in range(310):
        d = date(2020, 1, 1) + timedelta(days=i)
        if d.year != 2020:
            break
        hi = 104 if i < 5 else 80
        lo = 20 if i < 10 else 50
        long_days.append(GhcnDay("KTST", gid, d, hi, lo, 0.0 if i > 0 else 1.0))
    tails = mutual_station_tails(long_days)
    assert tails["heat"]["n_complete_years"] == 1
    assert tails["heat"]["hottest_f"] == 104
    assert tails["heat"]["median_days_ge_100f"] == 5
    assert tails["frost"]["coldest_f"] == 20
    assert tails["frost"]["median_frost_days"] == 10
    assert abs(tails["rain"]["median_year_inches"] - 1.0) < 1e-9

    series = [(2000, 70.0, 365), (2001, 72.0, 365), (2002, 71.0, 365),
              (2004, 80.0, 365)]   # 2003 manquant : pas de saut 2002→2004
    sw = year_to_year_swing(series)
    assert sw is not None and sw["n_consecutive_jumps"] == 2
    assert abs(sw["median_abs_jump_f"] - 1.5) < 1e-9


def test_eval_script_offline(tmp_path, monkeypatch):
    import eval_century_climato as ecc

    def fake_days(icao: str, use_cache: bool = True):
        out = []
        for y in range(1990, 2027):
            for m, day, hi in ((8, 3, 80 + (y % 5)), (8, 4, 81), (8, 5, 79)):
                try:
                    d = date(y, m, day)
                except ValueError:
                    continue
                out.append(GhcnDay(icao, "USW00000000", d, hi, hi - 15))
            # année assez complète pour la tendance
            start = date(y, 1, 1)
            for i in range(360):
                dt = start + timedelta(days=i)
                if dt.year != y:
                    break
                if dt.month == 8 and dt.day in (3, 4, 5):
                    continue
                out.append(GhcnDay(icao, "USW00000000", dt, 70, 55))
        return out

    monkeypatch.setattr(
        ecc.GhcnDailyClient, "fetch_station",
        lambda self, icao, use_cache=True, allow_network=True: fake_days(icao),
    )
    monkeypatch.setattr(ecc, "TRUTH_DIR", tmp_path)
    cli = []
    pts = []
    for i, d in enumerate((date(2026, 8, 3), date(2026, 8, 4), date(2026, 8, 5))):
        cli.append({"station": "KNYC", "valid": d.isoformat(), "high": 82, "low": 65})
        pts.append({
            "station": "KNYC", "variable": "temp_max", "target": d.isoformat(),
            "lead": 1, "per_model": {"m1": 78.0, "m2": 80.0},
        })
    (tmp_path / "cli_daily.json").write_text(json.dumps(cli), encoding="utf-8")
    (tmp_path / "skill").mkdir()
    (tmp_path / "skill" / "forecast_points.json").write_text(json.dumps(pts), encoding="utf-8")

    out = tmp_path / "century"
    monkeypatch.setattr("sys.argv", [
        "eval_century_climato.py", "--stations", "KNYC",
        "--skip-iem-probe", "--split-date", "2026-08-03",
        "--end-date", "2026-08-05", "--out-dir", str(out),
        "--market-min-date", "2099-01-01",
    ])
    assert ecc.main() == 0
    cov = json.loads((out / "coverage.json").read_text(encoding="utf-8"))
    assert cov["KNYC"]["temp_max"]["first_year"] == 1990
    assert cov["KNYC"]["temp_max"]["n_days"] > 300
    skill = json.loads((out / "skill.json").read_text(encoding="utf-8"))
    assert skill["a1_holdout"]["n_dates"] == 3
    assert skill["champion_switched"] is False if "champion_switched" in skill else True
    report = (out / "century_report.md").read_text(encoding="utf-8")
    assert "New York" in report and "On ne change pas" in report
