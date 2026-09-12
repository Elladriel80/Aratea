"""HRRR du matin même : run 12Z seulement, hors réseau."""
from __future__ import annotations

from datetime import date, datetime, timezone

from src.weather.hrrr_hourly import remaining_extreme
from src.weather.hrrr_morning import SOURCE, available_at, issued_12z


def test_issued_and_available_are_same_day_morning():
    d = date(2026, 8, 3)
    assert issued_12z(d) == datetime(2026, 8, 3, 12, tzinfo=timezone.utc)
    assert available_at(d) == datetime(2026, 8, 3, 13, tzinfo=timezone.utc)


def test_remaining_after_12z_stays_on_lst_day_and_labels_morning_source():
    times = [
        "2026-08-03T12:00", "2026-08-03T13:00", "2026-08-03T18:00",
        "2026-08-03T21:00", "2026-08-04T04:00", "2026-08-04T06:00",
    ]
    values = [70.0, 71.0, 80.0, 84.0, 72.0, 60.0]
    as_of = issued_12z(date(2026, 8, 3))
    got = remaining_extreme(
        times, values, "America/New_York", date(2026, 8, 3), as_of, "max",
        source=SOURCE,
    )
    assert got is not None
    # 12:00 pile est exclu. 06:00 UTC le 4 = 01:00 LST le 4 : hors jour.
    assert got["extreme_f"] == 84.0
    assert got["n_hours"] == 4
    assert got["source"] == "hrrr_morning_12z"


def test_remaining_does_not_invent_missing_hours():
    times = ["2026-08-03T15:00", "2026-08-03T16:00"]
    values = [None, None]
    assert remaining_extreme(
        times, values, "America/New_York", date(2026, 8, 3),
        issued_12z(date(2026, 8, 3)), "max", source=SOURCE,
    ) is None


def test_default_source_stays_yesterday_for_c1():
    times = ["2026-08-03T15:00"]
    values = [70.0]
    got = remaining_extreme(
        times, values, "America/New_York", date(2026, 8, 3),
        issued_12z(date(2026, 8, 3)), "max",
    )
    assert got is not None
    assert got["source"] == "hrrr_previous_day1"
