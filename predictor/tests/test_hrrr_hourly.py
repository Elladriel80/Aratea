"""Reste de journée HRRR : heures après la capture seulement. Hors réseau."""
from __future__ import annotations

from datetime import date, datetime, timezone

from src.weather.hrrr_hourly import remaining_extreme


def test_remaining_extreme_skips_hours_at_or_before_as_of():
    times = [
        "2026-08-03T17:00", "2026-08-03T18:00", "2026-08-03T19:00",
        "2026-08-03T21:00", "2026-08-04T04:00", "2026-08-04T06:00",
    ]
    values = [70.0, 71.0, 80.0, 84.0, 72.0, 60.0]
    as_of = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)
    got = remaining_extreme(times, values, "America/New_York", date(2026, 8, 3), as_of, "max")
    assert got is not None
    # 18:00 pile est exclu. 06:00 UTC le 4 = 01:00 LST le 4 : hors jour.
    # 04:00 UTC le 4 = 23:00 LST le 3 : encore le jour.
    assert got["extreme_f"] == 84.0
    assert got["n_hours"] == 3
    assert got["source"] == "hrrr_previous_day1"


def test_remaining_extreme_none_if_all_hours_missing():
    times = ["2026-08-03T19:00", "2026-08-03T20:00"]
    values = [None, None]
    as_of = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)
    assert remaining_extreme(
        times, values, "America/New_York", date(2026, 8, 3), as_of, "max",
    ) is None
