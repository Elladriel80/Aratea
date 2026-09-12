"""Tests hors réseau : Kalshi ouragan, HURDAT2, a-decks / b-decks."""
from __future__ import annotations

import json

import pytest

from src.truth.hurdat2_atl import (
    MAJOR_MIN_KT, PR241_HU, PR241_MAJOR, coverage_counts, climato_exceedance,
    discover_atlantic_filename, parse_hurdat2, season_rows, sshws_from_knots,
)
from src.truth.kalshi_hurricane import (
    CATALOGUE_MARKET, is_hurricane_series, parse_threshold, playability,
    price_vs_climato,
)
from src.truth.nhc_decks import (
    CATALOGUE_DECKS, extract_techs_from_gzip, list_year_files, parse_adeck_text,
    parse_atcf_lat, parse_atcf_lon, score_decks,
)

MINI_HURDAT2 = """AL092021,            IDA,      4,
20210826, 1800,  , TS, 17.4N,  79.5W,  35, 1006, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
20210827, 1800, L, HU, 21.5N,  82.6W,  70,  987, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
20210829, 1655, L, HU, 29.1N,  90.2W, 130,  931, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
20210829, 1800,  , HU, 29.2N,  90.4W, 125,  932, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
AL182021,            WADE,      2,
20211001, 0000,  , TS, 25.0N,  60.0W,  40, 1004, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
20211001, 0600,  , TS, 25.5N,  61.0W,  45, 1002, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
"""

MINI_ADECK = """AL, 09, 2021082618, 03, OFCL,  24, 215N,  826W,  80,  980, HU
AL, 09, 2021082618, 03, OCD5,  24, 210N,  820W,  50,  990, TS
AL, 09, 2021082618, 03, AVNO,  24, 200N,  810W,  40, 1000, TS
AL, 09, 2021082718, 03, OFCL,  12, 250N,  850W,  90,  970, HU
AL, 09, 2021082718, 03, OCD5,  12, 240N,  840W,  60,  980, HU
"""

MINI_BDECK = """AL, 09, 2021082618,   , BEST,   0, 174N,  795W,  35, 1006, TS
AL, 09, 2021082718,   , BEST,   0, 215N,  826W,  70,  987, HU
"""


def test_catalogue_names_are_stable():
    assert CATALOGUE_MARKET == "Marché ouragan Kalshi"
    assert CATALOGUE_DECKS == "NHC a-decks / b-decks"
    assert PR241_HU == 978
    assert PR241_MAJOR == 342
    assert MAJOR_MIN_KT == 96


def test_series_filter_keeps_weather_drops_false_friends():
    assert is_hurricane_series("KXHURCTOT", "Number of hurricanes", "Climate and Weather")
    assert is_hurricane_series("KXHURCAT", "Hurricane category", "Climate and Weather")
    assert not is_hurricane_series("KXNCAAFAPCHURN", "College Football AP Poll Churn", "Sports")
    assert not is_hurricane_series("KXTOPALBUMBYERICCHURCH", "Eric Church #1 Album", "Entertainment")
    assert not is_hurricane_series("KXLOWTCHI", "Chicago low temp", "Climate and Weather")


def test_parse_threshold_from_kalshi_rules():
    assert parse_threshold("records more than 6 hurricanes of hurricane category 1", "Above 6") == 6
    assert parse_threshold("", "Above 0") == 0
    assert parse_threshold("no number here", "Category 5 or above") is None


def test_playability_zero_settled_seasons_is_thin():
    inv = [{
        "series_ticker": "KXHURCTOT",
        "n_events": 5,
        "n_markets": 9,
        "n_markets_volume_gt0": 9,
        "n_quoted_two_sided": 4,
        "n_settled_yes_no": 0,
        "n_settled_with_mid": 0,
        "event_years_from_title": [2022, 2023, 2024, 2025, 2026],
        "markets": [
            {
                "result": None,
                "mid": 0.08,
                "event_ticker": "KXHURCTOT-26DEC01",
                "rules_primary": "more than 4 hurricanes ... 2026",
            }
        ],
    }]
    play = playability(inv)
    assert play["n_seasons_settled_with_public_mid_and_hurdat2"] == 0
    assert play["too_thin_to_score"] is True
    assert play["playable_to_score"] is False


def test_price_vs_climato_uses_measured_season_rates():
    rows = [
        {"year": 2000, "n_hurricanes": 8, "n_major": 3},
        {"year": 2001, "n_hurricanes": 4, "n_major": 0},
        {"year": 2002, "n_hurricanes": 4, "n_major": 1},
        {"year": 2003, "n_hurricanes": 7, "n_major": 3},
    ]
    inv = [{
        "series_ticker": "KXHURCTOT",
        "markets": [{
            "ticker": "KXHURCTOT-26DEC01-T4",
            "event_ticker": "KXHURCTOT-26DEC01",
            "subtitle": "Above 4",
            "threshold_more_than": 4,
            "yes_bid": 0.07,
            "yes_ask": 0.08,
            "last_price": 0.08,
            "mid": 0.075,
            "volume": 10.0,
            "rules_primary": "more than 4 hurricanes",
        }],
    }]
    out = price_vs_climato(inv, rows, rows)
    assert len(out) == 1
    # 8 and 7 are > 4 ; 4 is not. 2/4 = 0.5
    assert out[0]["climato_through_dec1"]["n_exceed"] == 2
    assert out[0]["climato_through_dec1"]["p"] == 0.5
    assert out[0]["mid_minus_climato_dec1"] == pytest.approx(-0.425)


def test_hurdat2_mini_counts_and_sshws():
    storms, gaps = parse_hurdat2(MINI_HURDAT2)
    assert gaps == []
    assert sshws_from_knots(130) == "4"
    cov = coverage_counts(storms, gaps)
    assert cov["n_systems"] == 2
    assert cov["n_hurricanes_HU"] == 1
    assert cov["n_hu_landfall_L"] == 1
    assert cov["matches_pr241"] is False
    rows = season_rows(storms, through_md=(12, 1))
    assert rows[0]["n_hurricanes"] == 1
    ex = climato_exceedance(rows, "n_hurricanes", 0)
    assert ex["n_exceed"] == 1 and ex["p"] == 1.0


def test_discover_atlantic_file():
    html = """
    <a href="hurdat2-1851-2024-040425.txt">old</a>
    <a href="hurdat2-1851-2025-02272026.txt">new</a>
    """
    info = discover_atlantic_filename(html)
    assert info["filename"] == "hurdat2-1851-2025-02272026.txt"


def test_atcf_lat_lon_and_adeck_filter():
    assert parse_atcf_lat("215N") == pytest.approx(21.5)
    assert parse_atcf_lon("826W") == pytest.approx(-82.6)
    lines = parse_adeck_text(MINI_ADECK)
    assert {ln.tech for ln in lines} == {"OFCL", "OCD5"}
    assert all(ln.storm_id == "AL092021" for ln in lines)


def test_list_year_files_skips_invest_and_pacific():
    html = """
    <a href="aal092021.dat.gz">ok</a>
    <a href="aal902021.dat.gz">invest</a>
    <a href="aep092021.dat.gz">pacific</a>
    <a href="bal092021.dat.gz">b</a>
    """
    a = list_year_files(html, "a")
    b = list_year_files(html, "b")
    assert [x[1] for x in a] == ["aal092021.dat.gz"]
    assert [x[1] for x in b] == ["bal092021.dat.gz"]


def test_intensity_ofcl_vs_ocd5_exact_time_only():
    storms, _ = parse_hurdat2(MINI_HURDAT2)
    adecks = {"AL092021": parse_adeck_text(MINI_ADECK)}
    bdecks = {"AL092021": parse_adeck_text(MINI_BDECK, techs=("BEST",))}
    scored = score_decks(adecks, bdecks, storms)
    # Only 20210826 18Z + 24h = 20210827 18Z matches a HURDAT2 point (70 kt HU L).
    assert scored["intensity"]["n"] == 1
    row_lead = scored["intensity"]["by_lead"]["24"]
    assert row_lead["n"] == 1
    assert row_lead["ofcl_mae_kt"] == 10  # 80 vs 70
    assert row_lead["ocd5_mae_kt"] == 20  # 50 vs 70
    assert row_lead["ofcl_beats_ocd5"] is True
    assert scored["first_hu_timing"]["genesis_scored"] is False
    assert scored["landfall"]["binary_landfall_scored"] is False
    # L at 20210827 1800 matches OFCL valid time, tau 24
    assert scored["landfall"]["n_ofcl_at_exact_L_time"] == 1


def test_extract_techs_from_gzip_roundtrip():
    import gzip
    raw = gzip.compress(MINI_ADECK.encode("utf-8"))
    text = extract_techs_from_gzip(raw, ("OFCL", "OCD5"))
    assert "AVNO" not in text
    assert "OFCL" in text and "OCD5" in text


def test_eval_script_offline(tmp_path, monkeypatch):
    import scripts.eval_marche_ouragan_kalshi as ev

    h_cache = tmp_path / "h"
    d_cache = tmp_path / "d"
    h_cache.mkdir()
    (h_cache / "hurdat2-1851-2021-01012022.txt").write_text(MINI_HURDAT2, encoding="utf-8")
    listing = d_cache / "listings"
    listing.mkdir(parents=True)
    (listing / "2021.html").write_text(
        '<a href="aal092021.dat.gz">a</a><a href="bal092021.dat.gz">b</a>',
        encoding="utf-8",
    )
    extracted = d_cache / "extracted"
    extracted.mkdir()
    (extracted / "aal092021.dat.gz.txt").write_text(MINI_ADECK, encoding="utf-8")
    (extracted / "bal092021.dat.gz.txt").write_text(MINI_BDECK, encoding="utf-8")

    inv = [{
        "series_ticker": "KXHURCTOT",
        "title": "Number of hurricanes",
        "category": "Climate and Weather",
        "frequency": "annual",
        "contract_url": "https://assets.kalshi.com/regulatory/product-certifications/LTHUR.pdf",
        "settlement_sources": [{"name": "NOAA", "url": "https://www.nhc.noaa.gov/"}],
        "n_events": 1,
        "n_markets": 1,
        "event_tickers": ["KXHURCTOT-26DEC01"],
        "event_titles": ["How many Atlantic hurricanes will there be in 2026?"],
        "event_years_from_close": ["2026"],
        "event_years_from_title": [2026],
        "market_status": {"active": 1},
        "volume_sum": 10.0,
        "n_markets_volume_gt0": 1,
        "n_quoted_two_sided": 1,
        "n_settled_yes_no": 0,
        "n_settled_with_mid": 0,
        "markets": [{
            "ticker": "KXHURCTOT-26DEC01-T4",
            "event_ticker": "KXHURCTOT-26DEC01",
            "status": "active",
            "result": None,
            "subtitle": "Above 4",
            "yes_bid": 0.07,
            "yes_ask": 0.08,
            "last_price": 0.08,
            "mid": 0.075,
            "volume": 10.0,
            "two_sided": True,
            "rules_primary": "If the NOAA's National Hurricane Center records more than 4 hurricanes of hurricane category 1 or above between January 1, 2026 and December 01, 2026, then the market resolves to Yes.",
            "threshold_more_than": 4,
            "close_time": "2026-12-02T04:59:00+00:00",
            "expiration_time": None,
        }],
    }]
    inv_path = tmp_path / "inv.json"
    inv_path.write_text(json.dumps(inv), encoding="utf-8")
    out = tmp_path / "out"
    deck_out = tmp_path / "decks"
    monkeypatch.setattr("sys.argv", [
        "eval_marche_ouragan_kalshi.py", "--skip-fetch",
        "--hurdat-cache", str(h_cache),
        "--deck-cache", str(d_cache),
        "--inventory-json", str(inv_path),
        "--out-dir", str(out),
        "--deck-out-dir", str(deck_out),
        "--deck-first-year", "2021",
        "--deck-last-year", "2021",
    ])
    assert ev.main() == 0
    counts = json.loads((out / "kalshi_hurricane_inventory.json").read_text(encoding="utf-8"))
    assert counts["catalogue"] == "Marché ouragan Kalshi"
    assert counts["champion_switched"] is False
    assert counts["real_money"] is False
    assert counts["playability"]["n_seasons_settled_with_public_mid_and_hurdat2"] == 0
    assert counts["verdicts"]["Marché ouragan Kalshi"] == "bloquée"
    assert counts["verdicts"]["Ouragan formation"] == "bloquée"
    assert counts["verdicts"]["Ouragan landfall"] == "bloquée"
    assert counts["verdicts"]["Sécheresse Méditerranée"] == "cible Tier 1 (pas encore testée)"
    assert counts["verdicts"]["NHC a-decks / b-decks"] == "testée, ça aide"
    assert counts["verdicts"]["Ouragan intensité"] == "testée, ça aide"
    report = (out / "kalshi_hurricane_report.md").read_text(encoding="utf-8")
    assert "Marché ouragan Kalshi" in report
    assert "—" not in report
    deck_report = (deck_out / "nhc_decks_report.md").read_text(encoding="utf-8")
    assert "NHC a-decks / b-decks" in deck_report
    assert "—" not in deck_report
