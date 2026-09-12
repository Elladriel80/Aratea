"""Lecture IEM / NWS : rien n'est inventé. Hors réseau."""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

from src.truth.asos import (
    icao_from_iem, iem_station_id, observed_extreme_so_far, parse_iem_csv,
    parse_nws_feature,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "asos_knyc.csv"


def test_icao_roundtrip():
    assert icao_from_iem("NYC") == "KNYC"
    assert icao_from_iem("KNYC") == "KNYC"
    assert iem_station_id("KNYC") == "NYC"


def test_parse_iem_skips_missing_temperature():
    rows = parse_iem_csv(FIXTURE.read_text(encoding="utf-8"), station_hint="KNYC")
    assert rows
    assert all(r.station == "KNYC" for r in rows)
    assert all(r.source == "iem" for r in rows)
    # La ligne 2026-08-04 00:51 a tmpf=M : jetée, pas inventée.
    valids = [r.valid for r in rows]
    assert datetime(2026, 8, 4, 0, 51, tzinfo=timezone.utc) not in valids
    assert datetime(2026, 8, 4, 1, 51, tzinfo=timezone.utc) in valids
    assert abs(rows[0].tmp_f - 77.0) < 1e-9


def test_observed_extreme_respects_as_of_and_lst():
    rows = parse_iem_csv(FIXTURE.read_text(encoding="utf-8"), station_hint="KNYC")
    as_of = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)
    got = observed_extreme_so_far(rows, "America/New_York", date(2026, 8, 3), as_of, "max")
    assert got is not None
    # 00:51 UTC le 3 août = 19:51 LST le 2 (heure standard). Hors jour.
    # Lectures du 3 LST jusqu'à 17:51 UTC : max 76. Le 18:51 est après 18:00.
    assert got["extreme_f"] == 76.0
    assert got["n_obs"] >= 4
    assert got["last"] == datetime(2026, 8, 3, 17, 51, tzinfo=timezone.utc)


def test_observed_extreme_missing_if_too_few_or_too_stale():
    rows = parse_iem_csv(FIXTURE.read_text(encoding="utf-8"), station_hint="KNYC")
    early = datetime(2026, 8, 3, 6, 10, tzinfo=timezone.utc)
    assert observed_extreme_so_far(
        rows, "America/New_York", date(2026, 8, 3), early, "max", min_obs=4,
    ) is None
    late = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)
    assert observed_extreme_so_far(
        rows, "America/New_York", date(2026, 8, 3), late, "max",
        max_stale_hours=0.1,
    ) is None


def test_parse_nws_skips_null_temperature():
    good = {
        "properties": {
            "timestamp": "2026-09-12T13:51:00+00:00",
            "temperature": {"value": 22.8, "unitCode": "wmoUnit:degC"},
        }
    }
    bad = {
        "properties": {
            "timestamp": "2026-09-12T13:51:00+00:00",
            "temperature": {"value": None, "unitCode": "wmoUnit:degC"},
        }
    }
    o = parse_nws_feature(good, "KNYC")
    assert o is not None
    assert abs(o.tmp_f - (22.8 * 9 / 5 + 32)) < 1e-6
    assert o.source == "nws"
    assert parse_nws_feature(bad, "KNYC") is None
    assert parse_nws_feature({"properties": {}}, "KNYC") is None
