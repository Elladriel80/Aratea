"""Jonction CLI × ledger / prévisions, hors réseau."""
from __future__ import annotations

from datetime import date

from src.truth.era5_compare import compare_era5_to_cli
from src.truth.iem_cli import CliDay
from src.truth.join_cli import (
    cli_value_for,
    forecast_vs_cli_by_station,
    index_cli_days,
    join_forecast_points,
    join_ledger_rows,
    summarize_joins,
)
from src.weather.open_meteo import DailyObservation


def test_index_and_value():
    idx = index_cli_days([
        {"station": "KNYC", "valid": "2026-05-11", "high": 72, "low": 54},
        {"station": "kphx", "valid": "2026-05-11T00:00:00", "high": None, "low": 70},
    ])
    assert cli_value_for(idx[("KNYC", "2026-05-11")], "temp_max") == 72
    assert cli_value_for(idx[("KPHX", "2026-05-11")], "temp_min") == 70
    assert cli_value_for(idx[("KPHX", "2026-05-11")], "temp_max") is None


def test_join_ledger_reasons():
    cli = index_cli_days([
        {"station": "KNYC", "valid": "2026-05-11", "high": 72, "low": 54},
        {"station": "KNYC", "valid": "2026-05-12", "high": None, "low": None},
    ])
    rows = join_ledger_rows([
        {"event_ticker": "KXLOWTNYC-26MAY11", "target_date": "2026-05-11",
         "resolution": "no", "method": "ensemble"},
        {"event_ticker": "KXLOWTNYC-26MAY12", "target_date": "2026-05-12"},
        {"event_ticker": "KXLOWTNYC-26MAY13", "target_date": "2026-05-13"},
        {"event_ticker": "KXUNKNOWN-26MAY11", "target_date": "2026-05-11"},
        {"event_ticker": "KXHIGHTDC-26JUN03", "target_date": "2026-06-03"},
    ], cli, "paper")
    assert rows[0]["joined"] is True and rows[0]["cli_value"] == 54 and rows[0]["station"] == "KNYC"
    assert rows[1]["reason"] == "cli_sans_valeur"
    assert rows[2]["reason"] == "pas_de_jour_cli"
    assert rows[3]["reason"] == "serie_inconnue"
    assert rows[4]["station"] == "KDCA" and rows[4]["reason"] == "pas_de_jour_cli"


def test_join_forecasts_skips_old_stations():
    cli = index_cli_days([
        {"station": "KMDW", "valid": "2026-05-12", "high": 70, "low": 50},
        {"station": "KORD", "valid": "2026-05-12", "high": 71, "low": 51},
    ])
    rows = join_forecast_points([
        {"station": "KMDW", "variable": "temp_max", "target": "2026-05-12", "lead": 1,
         "per_model": {"gfs_global": 68.0, "ecmwf_ifs025": 70.0}},
        {"station": "KORD", "variable": "temp_max", "target": "2026-05-12", "lead": 1,
         "per_model": {"gfs_global": 69.0}},
        {"station": "KMDW", "variable": "temp_max", "target": "2026-05-13", "lead": 1,
         "per_model": {"gfs_global": 71.0}},
    ], cli, current_stations={"KMDW"})
    assert rows[0]["joined"] is True and rows[0]["forecast_mean_f"] == 69.0 and rows[0]["error_f"] == -1.0
    assert rows[1]["joined"] is False and rows[1]["reason"] == "ancienne_station"
    assert rows[2]["reason"] == "pas_de_jour_cli"
    summary = summarize_joins([], rows)
    assert summary["forecasts"]["n_joined"] == 1
    assert summary["forecasts"]["not_joined_reasons"]["ancienne_station"] == 1
    fc = forecast_vs_cli_by_station(rows)
    assert fc["KMDW:temp_max"]["n"] == 1
    assert fc["KMDW:temp_max"]["bias_forecast_minus_cli_f"] == -1.0


class _FakeOM:
    def __init__(self, by_span: dict):
        self.by_span = by_span
        self.calls = []

    def historical_observations(self, lat, lon, start, end, timezone="auto"):
        self.calls.append((start, end))
        key = (start, end)
        if key in self.by_span:
            val = self.by_span[key]
            if isinstance(val, Exception):
                raise val
            return val
        raise RuntimeError("unexpected span")


def _obs(d: date, hi: float, lo: float) -> DailyObservation:
    return DailyObservation(d, hi, lo, None, None, {})


def _cli(d: date, hi: int, lo: int) -> CliDay:
    return CliDay("KLAX", d, hi, lo, None, None, None, False, None, False, None)


def test_era5_compare_stats_and_empty_error():
    meta = {"lat": 1.0, "lon": 2.0, "tz": "America/Los_Angeles"}
    truth = [_cli(date(2026, 7, 1), 80, 60), _cli(date(2026, 7, 2), 82, 61)]
    om = _FakeOM({
        (date(2026, 7, 1), date(2026, 7, 2)): [
            _obs(date(2026, 7, 1), 78.4, 59.0),
            _obs(date(2026, 7, 2), 84.0, 63.2),
        ]
    })
    out = compare_era5_to_cli(om, meta, truth, date(2026, 7, 1), date(2026, 7, 2))
    assert out["high:all"]["n"] == 2
    assert out["high:all"]["bias_era5_minus_cli_f"] == 0.2  # (78.4-80 + 84-82) / 2
    assert out["high:all"]["exact_share"] == 0.0

    empty = _FakeOM({(date(2026, 7, 1), date(2026, 7, 2)): []})
    err = compare_era5_to_cli(empty, meta, truth, date(2026, 7, 1), date(2026, 7, 2))
    assert "error" in err


def test_era5_retries_when_long_series_too_short():
    meta = {"lat": 1.0, "lon": 2.0, "tz": "UTC"}
    truth = [_cli(date(2024, 6, 1), 80, 60), _cli(date(2025, 6, 1), 82, 61)]
    om = _FakeOM({
        (date(2024, 1, 1), date(2025, 12, 31)): [_obs(date(2025, 6, 1), 81.0, 60.0)],
        (date(2024, 1, 1), date(2024, 12, 31)): [_obs(date(2024, 6, 1), 79.0, 59.0)],
        (date(2025, 1, 1), date(2025, 12, 31)): [_obs(date(2025, 6, 1), 81.0, 60.0)],
    })
    out = compare_era5_to_cli(om, meta, truth, date(2024, 1, 1), date(2025, 12, 31))
    assert out["high:all"]["n"] == 2
    assert om.calls[0] == (date(2024, 1, 1), date(2025, 12, 31))
    assert len(om.calls) == 3


def test_era5_year_chunk_fallback():
    meta = {"lat": 1.0, "lon": 2.0, "tz": "UTC"}
    truth = [_cli(date(2025, 12, 31), 50, 30), _cli(date(2026, 1, 1), 40, 20)]
    om = _FakeOM({
        (date(2025, 12, 31), date(2026, 1, 1)): RuntimeError("timeout"),
        (date(2025, 12, 31), date(2025, 12, 31)): [_obs(date(2025, 12, 31), 52.0, 31.0)],
        (date(2026, 1, 1), date(2026, 1, 1)): [_obs(date(2026, 1, 1), 39.0, 19.0)],
    })
    out = compare_era5_to_cli(om, meta, truth, date(2025, 12, 31), date(2026, 1, 1))
    assert out["high:all"]["n"] == 2
    assert out["high:all"]["bias_era5_minus_cli_f"] == 0.5
