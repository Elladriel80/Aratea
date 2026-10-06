"""Tests hors réseau : parse USDM, saisons, agrégation, Brier/BSS."""
from __future__ import annotations

import json
from datetime import date

import pytest

from src.forecast.nmme import _looks_like_hindcast
from src.forecast.open_meteo_seasonal import monthly_rows
from src.truth.usdm import (
    CLASSES, D2PLUS_AREA_THRESHOLD, MIDWEST_STATES, SOUTHWEST_MAINLAND_STATES,
    USDM_ARCHIVE_START, UsdmWeek, brier_skill_score, combine_area_weeks,
    coverage_table, expected_weekly_tuesdays, leave_one_out_climato, met_season,
    month_is_complete, parse_usdm_stamp, parse_week, season_means,
)


def _row(day: str, **vals):
    base = dict(none=10.0, d0=20.0, d1=30.0, d2=25.0, d3=10.0, d4=5.0)
    base.update(vals)
    return {
        "mapDate": f"{day}T00:00:00",
        "validStart": f"{day}T00:00:00",
        "validEnd": f"{day}T23:59:59",
        "statisticFormatID": 2,
        "name": "Midwest",
        **base,
    }


def test_published_classes_are_exactly_d0_to_d4_and_none():
    assert CLASSES == ("none", "d0", "d1", "d2", "d3", "d4")
    assert D2PLUS_AREA_THRESHOLD == 30.0
    assert USDM_ARCHIVE_START == date(2000, 1, 4)
    assert USDM_ARCHIVE_START.weekday() == 1


def test_usda_hub_state_lists_are_the_published_mainland_sets():
    assert set(MIDWEST_STATES) == {"IL", "IN", "IA", "MI", "MN", "MO", "OH", "WI"}
    assert set(SOUTHWEST_MAINLAND_STATES) == {"AZ", "CA", "NV", "NM", "UT"}
    assert "KY" not in MIDWEST_STATES
    assert "CO" not in SOUTHWEST_MAINLAND_STATES
    assert "HI" not in SOUTHWEST_MAINLAND_STATES


def test_parse_week_rejects_a_missing_class():
    raw = _row("2024-01-02")
    del raw["d3"]
    with pytest.raises(ValueError, match="missing classes"):
        parse_week(raw, "Midwest", "percent")


def test_parse_and_d2_plus():
    w = parse_week(_row("2024-01-02"), "Midwest", "percent")
    assert w.map_date == date(2024, 1, 2)
    assert w.d2_plus() == 40.0
    assert w.statistic_format == 2
    assert parse_usdm_stamp("2024-01-02T00:00:00") == date(2024, 1, 2)


def test_met_season_djf_belongs_to_january_year():
    assert met_season(date(2023, 12, 26)) == ("DJF", 2024)
    assert met_season(date(2024, 1, 2)) == ("DJF", 2024)
    assert met_season(date(2024, 6, 4)) == ("JJA", 2024)
    assert met_season(date(2024, 9, 3)) == ("SON", 2024)


def test_month_is_complete_needs_every_tuesday():
    have = {date(2026, 9, 1), date(2026, 9, 8)}
    assert month_is_complete(2026, 9, have) is False
    have = {date(2026, 9, 1), date(2026, 9, 8), date(2026, 9, 15),
            date(2026, 9, 22), date(2026, 9, 29)}
    assert month_is_complete(2026, 9, have) is True


def test_expected_tuesdays_and_missing_week():
    first, last = date(2024, 1, 2), date(2024, 1, 16)
    exp = expected_weekly_tuesdays(first, last)
    assert exp == [date(2024, 1, 2), date(2024, 1, 9), date(2024, 1, 16)]
    weeks = [
        parse_week(_row("2024-01-02", d2=0, d3=0, d4=0), "X", "percent"),
        parse_week(_row("2024-01-16", d2=40, d3=0, d4=0), "X", "percent"),
    ]
    cov = coverage_table(weeks)
    assert cov["n_weeks"] == 2
    assert cov["expected_weeks"] == 3
    assert cov["missing_weeks"] == 1
    assert cov["missing_map_dates"] == ["2024-01-09"]
    assert cov["d2_plus"]["weeks_gt_0"] == 1
    assert cov["d2_plus"]["weeks_ge_30"] == 1


def test_combine_area_weeks_rebuilds_percent_from_published_areas():
    a = parse_week(_row("2024-01-02", none=50, d0=50, d1=0, d2=0, d3=0, d4=0), "Midwest", "area")
    b = parse_week(_row("2024-01-02", none=0, d0=0, d1=0, d2=100, d3=0, d4=0), "Southwest", "area")
    comb = combine_area_weeks([[a], [b]], "Midwest_plus_Southwest")
    assert len(comb) == 1
    assert comb[0].unit == "percent"
    assert comb[0].values["none"] == pytest.approx(25.0)
    assert comb[0].values["d2"] == pytest.approx(50.0)
    assert comb[0].d2_plus() == pytest.approx(50.0)


def test_season_means_need_twelve_weeks_to_be_complete():
    cur = date(2024, 6, 4)
    short = []
    for _ in range(11):
        short.append(parse_week(_row(cur.isoformat()), "X", "percent"))
        cur = date.fromordinal(cur.toordinal() + 7)
    rows = season_means(short)
    assert len(rows) == 1
    assert rows[0]["n_weeks"] == 11
    assert rows[0]["complete"] is False

    cur = date(2024, 6, 4)
    full = []
    for _ in range(13):
        full.append(parse_week(_row(cur.isoformat(), d2=30, d3=0, d4=0), "X", "percent"))
        cur = date.fromordinal(cur.toordinal() + 7)
    rows = season_means(full)
    assert rows[0]["complete"] is True
    assert rows[0]["event_d2_plus_ge_30"] is True


def test_loo_climato_and_bss_are_not_invented():
    assert leave_one_out_climato([True]) == []
    assert leave_one_out_climato([True, False, False]) == pytest.approx([0.0, 0.5, 0.5])
    assert brier_skill_score(0.1, 0.2) == pytest.approx(0.5)
    assert brier_skill_score(0.1, 0.0) is None


def test_nmme_html_page_is_not_a_hindcast_series():
    assert _looks_like_hindcast("text/html", b"<!DOCTYPE html><html>") is False
    assert _looks_like_hindcast("text/plain", b"1982 12 1.23\n1983 12 0.4") is True


def test_monthly_rows_skip_nothing_when_api_errors():
    assert monthly_rows({"error": True, "reason": "nope"}) == []
    rows = monthly_rows({
        "monthly": {
            "time": ["2026-06-01"],
            "precipitation_mean": [10.0],
            "precipitation_anomaly": [-2.0],
        }
    })
    assert rows == [{
        "month": "2026-06-01",
        "precipitation_mean": 10.0,
        "precipitation_anomaly": -2.0,
    }]


def test_eval_script_offline(tmp_path, monkeypatch):
    import scripts.eval_us_drought as ev

    def fake_fetch(client, start, end, allow_network):
        assert allow_network is False
        cur = date(2024, 1, 2)
        weeks = []
        for _ in range(13):
            weeks.append(parse_week(_row(cur.isoformat(), d2=5, d3=0, d4=0), "Midwest", "percent"))
            cur = date.fromordinal(cur.toordinal() + 7)
        area = [
            UsdmWeek(w.series, w.map_date, w.valid_start, w.valid_end, 2,
                     {k: 10.0 for k in CLASSES}, "area", w.name)
            for w in weeks
        ]
        return {
            "CONUS_cat": [UsdmWeek("CONUS", w.map_date, w.valid_start, w.valid_end, 2, w.values, "percent", "CONUS") for w in weeks],
            "CONUS_cum": [UsdmWeek("CONUS", w.map_date, w.valid_start, w.valid_end, 1, w.values, "percent", "CONUS") for w in weeks],
            "Midwest_cat": weeks,
            "Southwest_cat": [UsdmWeek("Southwest", w.map_date, w.valid_start, w.valid_end, 2, w.values, "percent", "Southwest") for w in weeks],
            "Midwest_area": area,
            "Southwest_area": area,
            "Midwest_plus_Southwest_cat": combine_area_weeks([area, area], "Midwest_plus_Southwest"),
        }

    monkeypatch.setattr(ev, "fetch_all", fake_fetch)
    monkeypatch.setattr(ev, "score_open_meteo", lambda series, allow_network: {
        "forecast_name": "Open-Meteo Seasonal",
        "blocker": "Open-Meteo Seasonal refuse start_date historique",
        "skill": {"n_months": 0, "bss": None, "gate_bss_gt_0_05": False, "gate_n_ge_10": False},
    })
    monkeypatch.setattr(ev, "probe_nmme", lambda: {
        "forecast_name": "NMME", "any_ok": True, "hindcast_usable": False,
        "blocker": "pas de série datée",
    })
    out = tmp_path / "usdm"
    monkeypatch.setattr("sys.argv", [
        "eval_us_drought.py", "--skip-fetch", "--end-date", "2024-04-02",
        "--out-dir", str(out),
    ])
    assert ev.main() == 0
    counts = json.loads((out / "usdm_counts.json").read_text(encoding="utf-8"))
    assert counts["catalogue_target"] == "Sécheresse US"
    assert counts["truth_name"] == "US Drought Monitor"
    assert counts["forecast_name_used"] == "Open-Meteo Seasonal"
    assert counts["champion_switched"] is False
    assert counts["coverage"]["Midwest_cat"]["n_weeks"] == 13
    assert "Sécheresse Méditerranée" in counts["verdicts"]
    assert counts["verdicts"]["Sécheresse Méditerranée"] == "cible Tier 1 (pas encore testée)"
