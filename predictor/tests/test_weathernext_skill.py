"""WeatherNext : sondes, J0 vs J-1, aucun score inventé."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from src.truth.synthetic_bins import Bin, prob_in_bin_members
from src.weather.ensemble_api import MemberSeries
from src.weather.weathernext import (
    lead_name, member_daily_values, member_fill_summary, gcp_env_status,
)

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import eval_weathernext_skill as ev  # noqa: E402


def test_member_fill_summary_counts_only_real_values():
    hourly = {
        "time": ["2026-09-09T00:00", "2026-09-09T01:00", "2026-09-10T00:00"],
        "temperature_2m": [70.0, None, None],
        "temperature_2m_member01": [71.0, 72.0, None],
    }
    s = member_fill_summary(hourly, "temperature_2m")
    assert s["n_member_keys"] == 2
    assert s["n_filled_cells"] == 3
    assert s["filled_days"] == ["2026-09-09"]
    assert s["days"]["2026-09-10"]["hours_any_member"] == 0
    assert s["days"]["2026-09-09"]["members_with_any"] == 2


def test_member_fill_summary_empty_is_zero_not_invented():
    hourly = {
        "time": ["2026-08-03T00:00", "2026-08-03T01:00"],
        "temperature_2m": [None, None],
        "temperature_2m_member01": [None, None],
    }
    s = member_fill_summary(hourly, "temperature_2m")
    assert s["n_filled_cells"] == 0
    assert s["filled_days"] == []
    assert s["first_filled"] is None


def test_lead_name_keeps_j0_and_j1_apart():
    assert lead_name(0) == "J0"
    assert lead_name(1) == "J-1"
    assert lead_name(2) == "lead_2"


def _series(center: float, tz_start_hour_utc: int = 5) -> list[MemberSeries]:
    """24 h from 05z (00:00 EST) with a peak at local afternoon."""
    start = datetime(2026, 9, 10, tz_start_hour_utc, tzinfo=timezone.utc)
    times = [(start + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(24)]
    out = []
    for k, shift in enumerate((-2.0, 0.0, 2.0, 1.0)):
        vals = [center - 8.0] * 24
        vals[14] = center + shift
        out.append(MemberSeries("google_weathernext2_ensemble", k, times, vals))
    return out


def test_member_daily_values_omit_incomplete_members():
    members = _series(80.0)
    members[0].values = [None] * 24
    vals = member_daily_values(members, "America/New_York", date(2026, 9, 10), "max")
    assert len(vals) == 3
    assert min(vals) >= 78.0


def test_score_vs_cli_j0_does_not_use_j1_members():
    cli = {("KATL", date(2026, 9, 10)): {"high": 81, "low": 68}}
    extremes = {
        ("KATL", "temp_max", date(2026, 9, 10), 0): [79.0, 80.0, 81.0] * 4,
        ("KATL", "temp_max", date(2026, 9, 10), 1): [90.0] * 12,
    }
    j0 = ev.score_vs_cli(extremes, cli, lead=0)
    j1 = ev.score_vs_cli(extremes, cli, lead=1)
    assert j0 and all(r["lead"] == 0 and r["horizon"] == "J0" for r in j0)
    assert j1 and all(r["lead"] == 1 and r["horizon"] == "J-1" for r in j1)
    # J0 center ~80 ; J-1 center 90. Different P(bin) : no mix.
    p_j0 = {r["bin"]: r["p_wn"] for r in j0}
    p_j1 = {r["bin"]: r["p_wn"] for r in j1}
    assert p_j0 != p_j1


def test_score_vs_cli_skips_when_members_or_truth_missing():
    cli = {("KATL", date(2026, 9, 10)): {"high": 81, "low": 68}}
    empty = ev.score_vs_cli({("KATL", "temp_max", date(2026, 9, 10), 0): [80.0] * 3}, cli, 0)
    assert empty == []
    no_truth = ev.score_vs_cli(
        {("KATL", "temp_max", date(2026, 9, 11), 0): [80.0] * 12}, cli, 0
    )
    assert no_truth == []


def test_prob_in_bin_members_empty_is_zero():
    assert prob_in_bin_members([], Bin(80, 81)) == 0.0


def test_verdict_blocked_even_if_wn2_has_a_few_days():
    assert ev.verdict_text({"blocked": True}, j0_dates=3, j1_dates=0) == (
        "pas encore mesurable (bloquée)"
    )
    assert ev.verdict_text({"blocked": False}, j0_dates=3, j1_dates=0) == (
        "pas encore mesurable (bloquée)"
    )


def test_gcp_env_status_does_not_leak_secret_values(monkeypatch):
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/secret/path.json")
    st = gcp_env_status()
    assert st["GOOGLE_APPLICATION_CREDENTIALS_set"] is True
    assert "/secret/path.json" not in str(st)
