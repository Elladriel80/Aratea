"""Tests du paquet src/truth : parsing CLI, fenêtre LST, bins synthétiques,
biais station. Aucun accès réseau : fixtures synthétiques uniquement."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone

import pytest

from src.truth.iem_cli import IEMCliClient, CliDay, kalshi_stations, parse_cli_record, station_for_series
from src.truth.lst_window import daily_extreme_lst, lst_date, standard_utc_offset
from src.truth.skill import (
    ForecastPoint, StationBias, build_forecast_points, climatology_gaussian,
    score_points, sign_test_by_date, summarize,
)
from src.truth.synthetic_bins import Bin, kalshi_style_bins, prob_in_bin_gaussian
from src.weather.previous_runs import HourlyLeadSeries, PreviousRunsClient


# ------------------------------------------------------------------ IEM CLI

def test_parse_cli_record_handles_missing_and_trace():
    rec = {"valid": "2026-05-08", "station": "KNYC", "high": 78, "low": "M",
           "high_time": "3:05 PM", "precip": "T", "snow": None, "product": "CLINYC"}
    d = parse_cli_record(rec)
    assert d.valid == date(2026, 5, 8)
    assert d.high_f == 78 and d.low_f is None
    assert d.precip_in == 0.0 and d.precip_trace is True
    assert d.snow_in is None
    assert d.value_for("temp_max") == 78.0 and d.value_for("temp_min") is None


def test_parse_cli_record_rejects_unreadable_date():
    assert parse_cli_record({"valid": "garbage", "station": "KNYC"}) is None


def test_client_keeps_last_report_per_day_and_caches(tmp_path, monkeypatch):
    payload = {"results": [
        {"valid": "2026-05-08", "station": "KNYC", "high": 77, "low": 60, "product": "CLINYC_prelim"},
        {"valid": "2026-05-08", "station": "KNYC", "high": 78, "low": 60, "product": "CLINYC_final"},
        {"valid": "2026-05-09", "station": "KNYC", "high": 70, "low": 55},
    ]}
    client = IEMCliClient(cache_dir=tmp_path, sleep_s=0)
    calls = {"n": 0}

    def fake_fetch(station, year):
        calls["n"] += 1
        return payload

    monkeypatch.setattr(client, "_fetch_year_raw", fake_fetch)
    days = client.fetch_year("knyc", 2026)
    assert [d.high_f for d in days] == [78, 70]          # dernier produit gagne
    assert days[0].product == "CLINYC_final"
    # deuxième appel : cache (année courante fraîche)
    client.fetch_year("KNYC", 2026)
    assert calls["n"] == 1
    assert (tmp_path / "cli_KNYC_2026.json").exists()


def test_station_mapping_covers_all_kalshi_cities():
    st = kalshi_stations()
    assert len(st) == 18
    assert st["KNYC"]["tz"] == "America/New_York"
    assert st["KPHX"]["tz"] == "America/Phoenix"
    assert station_for_series("KXLOWTNYC") == "KNYC"
    assert station_for_series("KXHIGHTSFO") == "KSFO"
    assert station_for_series("KXHIGHTDC") == "KDCA"
    assert station_for_series("KXHIGHTSEA-26JUN03") == "KSEA"


# --------------------------------------------------------------- LST window

def test_standard_offset_ignores_dst():
    summer = datetime(2026, 7, 1, 12, tzinfo=timezone.utc)
    winter = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    assert standard_utc_offset("America/New_York", summer) == timedelta(hours=-5)
    assert standard_utc_offset("America/New_York", winter) == timedelta(hours=-5)
    assert standard_utc_offset("America/Phoenix", summer) == timedelta(hours=-7)


def test_lst_date_midnight_dst_belongs_to_previous_climatological_day():
    # 00:30 EDT le 9 mai = 04:30 UTC = 23:30 EST le 8 mai → journée CLI du 8.
    assert lst_date(datetime(2026, 5, 9, 4, 30, tzinfo=timezone.utc), "America/New_York") == date(2026, 5, 8)
    # 01:30 EDT le 9 mai = 05:30 UTC = 00:30 EST → journée CLI du 9.
    assert lst_date(datetime(2026, 5, 9, 5, 30, tzinfo=timezone.utc), "America/New_York") == date(2026, 5, 9)


def _hourly(start_utc: datetime, values):
    times = [(start_utc + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(len(values))]
    return times, values


def test_daily_extreme_uses_lst_window_not_local_daylight_window():
    # 48 h à partir du 8 mai 00:00 UTC ; pic de 90 °F à 04:00 UTC le 9 mai
    # (= 00:00 EDT le 9, mais 23:00 EST le 8) → doit compter pour le 8.
    start = datetime(2026, 5, 8, 0, tzinfo=timezone.utc)
    vals = [60.0] * 48
    vals[28] = 90.0                  # 8 mai 00:00 UTC + 28 h = 9 mai 04:00 UTC
    times, values = _hourly(start, vals)
    assert daily_extreme_lst(times, values, "America/New_York", date(2026, 5, 8), "max") == 90.0
    assert daily_extreme_lst(times, values, "America/New_York", date(2026, 5, 9), "max", min_hours=10) == 60.0


def test_daily_extreme_refuses_partial_day():
    start = datetime(2026, 5, 8, 5, tzinfo=timezone.utc)   # 00:00 EST
    times, values = _hourly(start, [70.0] * 10)
    assert daily_extreme_lst(times, values, "America/New_York", date(2026, 5, 8), "max") is None


# ---------------------------------------------------------- synthetic bins

def test_kalshi_style_bins_shape_and_partition():
    bins = kalshi_style_bins(76.3, n_central=6)
    assert len(bins) == 8
    central = [b for b in bins if b.is_central]
    assert central[0] == Bin(70, 71) and central[-1] == Bin(80, 81)
    assert bins[0] == Bin(None, 69) and bins[-1] == Bin(82, None)
    # partition : chaque entier tombe dans exactement un bin
    for v in range(50, 100):
        assert sum(1 for b in bins if b.contains(v)) == 1
    assert bins[4].label() == "76° to 77°"


def test_gaussian_bin_probabilities_sum_to_one_and_respect_rounding():
    bins = kalshi_style_bins(76.0)
    total = sum(prob_in_bin_gaussian(76.0, 2.5, b) for b in bins)
    assert abs(total - 1.0) < 1e-9
    # sigma nul : masse entière sur le bin qui contient mu arrondi
    assert prob_in_bin_gaussian(76.4, 0.0, Bin(76, 77)) == 1.0
    assert prob_in_bin_gaussian(76.4, 0.0, Bin(78, 79)) == 0.0
    # un mu à 77.6 (arrondi 78) doit donner plus au bin 78-79 qu'au bin 76-77
    assert prob_in_bin_gaussian(77.6, 0.5, Bin(78, 79)) > prob_in_bin_gaussian(77.6, 0.5, Bin(76, 77))


# ----------------------------------------------------------- previous runs

def test_previous_runs_merge_multi_model_and_single_model_keys():
    c = PreviousRunsClient.__new__(PreviousRunsClient)
    c.models, c.leads = ["gfs_global", "ecmwf_ifs025"], [1, 2]
    out = {m: {n: HourlyLeadSeries(m, n) for n in c.leads} for m in c.models}
    data = {"hourly": {"time": ["2026-05-08T00:00", "2026-05-08T01:00"],
                       "temperature_2m_previous_day1_gfs_global": [70.0, 71.0],
                       "temperature_2m_previous_day2_gfs_global": [69.0, None],
                       "temperature_2m_previous_day1_ecmwf_ifs025": [72.0, 73.0]}}
    c._merge(data, "temperature_2m", out)
    assert out["gfs_global"][1].values == [70.0, 71.0]
    assert out["gfs_global"][2].n_valid == 1
    assert out["ecmwf_ifs025"][2].values == []
    cov = PreviousRunsClient.coverage(out)
    assert cov["gfs_global"][1]["n_days"] == 1 and cov["ecmwf_ifs025"][2]["n_days"] == 0

    single = PreviousRunsClient.__new__(PreviousRunsClient)
    single.models, single.leads = ["gfs_global"], [1]
    out1 = {"gfs_global": {1: HourlyLeadSeries("gfs_global", 1)}}
    single._merge({"hourly": {"time": ["t"], "temperature_2m_previous_day1": [65.0]}}, "temperature_2m", out1)
    assert out1["gfs_global"][1].values == [65.0]


def test_previous_runs_rejects_bad_leads():
    with pytest.raises(ValueError):
        PreviousRunsClient(leads=[0, 8])


# ------------------------------------------------------------------ skill

def _truth(station, start: date, n: int, high_fn):
    return [CliDay(station, start + timedelta(days=i), int(high_fn(i)), 50, None, None,
                   0.0, False, 0.0, False, None) for i in range(n)]


def test_station_bias_learns_offset_and_improves_brier():
    station, var = "KTST", "temp_max"
    start = date(2026, 3, 1)
    n = 120
    # vérité : 80 °F + variation ; les modèles sous-estiment de 3 °F systématiquement
    truth = _truth(station, start, n, lambda i: 80 + (i % 7) - 3)
    truth_by = {(d.station, d.valid): d for d in truth}
    points = [ForecastPoint(station, var, d.valid, 1,
                            {"m1": d.high_f - 3.0 + 0.4, "m2": d.high_f - 3.0 - 0.4})
              for d in truth]
    split = start + timedelta(days=84)
    train = [p for p in points if p.target < split]
    hold = [p for p in points if p.target >= split]
    bias = StationBias().fit(train, truth_by)
    b, s, cnt = bias.params[(station, var, 1)]
    assert abs(b - 3.0) < 1e-6 and cnt == 84 and s == 1.0      # plancher 1 °F
    scores = score_points(hold, truth_by, {station: truth}, bias)
    assert scores and all(sc.p_climo is None for sc in scores)   # pas d'années passées → pas de climato
    # summarize exige climato définie → vide ; on compare à la main
    import statistics
    raw = statistics.fmean((sc.p_raw - sc.outcome) ** 2 for sc in scores)
    st = statistics.fmean((sc.p_station - sc.outcome) ** 2 for sc in scores)
    assert st < raw
    t = sign_test_by_date(scores, "p_station", "p_raw")
    assert t["a_wins"] == t["dates"] and t["p_one_sided"] < 0.01


def test_station_bias_requires_min_pairs():
    station, var = "KTST", "temp_max"
    truth = _truth(station, date(2026, 3, 1), 5, lambda i: 80)
    truth_by = {(d.station, d.valid): d for d in truth}
    pts = [ForecastPoint(station, var, d.valid, 1, {"m1": 77.0, "m2": 78.0}) for d in truth]
    assert StationBias().fit(pts, truth_by).params == {}


def test_climatology_is_point_in_time_and_uses_previous_years_only():
    station = "KTST"
    truth = []
    for y in (2023, 2024, 2025):
        truth += _truth(station, date(y, 5, 1), 31, lambda i, y=y: 70 + (y - 2023) * 2)
    truth += _truth(station, date(2026, 5, 1), 31, lambda i: 99)     # année cible, doit être ignorée
    mu, sigma = climatology_gaussian(truth, "temp_max", date(2026, 5, 15), window_days=7, years_back=8)
    assert abs(mu - 72.0) < 1e-9 and sigma >= 1.0
    assert climatology_gaussian(truth, "temp_max", date(2023, 5, 15)) is None   # aucune année avant


def test_build_forecast_points_requires_two_models():
    start = datetime(2026, 5, 8, 5, tzinfo=timezone.utc)
    times, vals = _hourly(start, [70.0] * 24)
    s1 = HourlyLeadSeries("m1", 1, times, vals)
    series = {"m1": {1: s1}}
    assert build_forecast_points("KNYC", "temp_max", "America/New_York", series, [date(2026, 5, 8)]) == []
    series["m2"] = {1: HourlyLeadSeries("m2", 1, times, [72.0] * 24)}
    pts = build_forecast_points("KNYC", "temp_max", "America/New_York", series, [date(2026, 5, 8)])
    assert len(pts) == 1 and pts[0].mean == 71.0 and pts[0].spread == 1.0


def test_summarize_groups_and_reports_deltas():
    from src.truth.skill import BinScore
    rows = [BinScore("K", "temp_max", date(2026, 5, 8), 1, "b", True, 0.5, 0.9, 0.2),
            BinScore("K", "temp_max", date(2026, 5, 9), 1, "b", False, 0.5, 0.1, 0.8)]
    s = summarize(rows, lambda r: r.lead)
    assert s[1]["n_bins"] == 2 and s[1]["n_dates"] == 2
    assert s[1]["brier_station"] < s[1]["brier_raw"] < s[1]["brier_climo"]


def test_kalshi_resolution_stations_match_market_rules():
    """Revue 2026-09-09 : les règles Kalshi nomment Chicago Midway, Houston Hobby
    et Dallas-Fort Worth (aucun CLI n'existe pour Love Field). Verrouille la
    correction pour que personne ne remette O'Hare / Intercontinental."""
    from src.kalshi.resolution import NWS_STATIONS, SERIES_TO_STATION
    from src.weather.open_meteo import CITIES
    from src.truth.iem_cli import CITY_TO_ICAO
    assert SERIES_TO_STATION["KXLOWTCHI"] == "CLIMDW" and SERIES_TO_STATION["KXHIGHTCHI"] == "CLIMDW"
    assert SERIES_TO_STATION["KXLOWTHOU"] == "CLIHOU" and SERIES_TO_STATION["KXHIGHTHOU"] == "CLIHOU"
    assert SERIES_TO_STATION["KXHIGHTDAL"] == "CLIDFW"
    assert SERIES_TO_STATION["KXHIGHTDC"] == "CLIDCA"
    assert SERIES_TO_STATION["KXHIGHTSEA"] == "CLISEA"
    assert CITY_TO_ICAO["CHICAGO"] == "KMDW" and CITY_TO_ICAO["HOUSTON"] == "KHOU" and CITY_TO_ICAO["DALLAS"] == "KDFW"
    # les coordonnées de prévision sont celles de la station de résolution
    for city, icao in (("CHICAGO", "KMDW"), ("HOUSTON", "KHOU"), ("DALLAS", "KDFW")):
        st = next(s for s in NWS_STATIONS.values() if s.icao == icao)
        assert abs(CITIES[city]["lat"] - st.lat) < 0.01 and abs(CITIES[city]["lon"] - st.lon) < 0.01
