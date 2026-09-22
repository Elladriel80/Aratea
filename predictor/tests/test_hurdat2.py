"""Tests hors réseau : parse HURDAT2 / IBTrACS, catégories, ACE, script."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.truth.hurdat2 import (
    ACE_HYPERACTIVE, MAJOR_MIN_KT, NAMED_STORMS_THRESHOLD, ace_contribution,
    coverage_table, discover_atlantic_filename, parse_hurdat2, parse_lat,
    parse_lon, season_rows, sshws_from_knots,
)
from src.truth.ibtracs import (
    is_spur_type, parse_ibtracs_na, coverage_table as ib_coverage,
)

# Official Ida landfall line from the NHC format PDF (20210829, 1655, L, HU, 130 kt).
MINI_HURDAT2 = """AL092021,            IDA,      4,
20210826, 1800,  , TS, 17.4N,  79.5W,  35, 1006, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
20210827, 1800, L, HU, 21.5N,  82.6W,  70,  987, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
20210829, 1655, L, HU, 29.1N,  90.2W, 130,  931, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
20210829, 1800,  , HU, 29.2N,  90.4W, 125,  932, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
AL182021,            WADE,      2,
20211001, 0000,  , TS, 25.0N,  60.0W,  40, 1004, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
20211001, 0600,  , TS, 25.5N,  61.0W,  45, 1002, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999, -999
"""

MINI_IBTRACS = """SID,SEASON,NUMBER,BASIN,SUBBASIN,NAME,ISO_TIME,NATURE,LAT,LON,WMO_WIND,WMO_PRES,WMO_AGENCY,TRACK_TYPE,DIST2LAND,LANDFALL,IFLAG,USA_AGENCY,USA_ATCF_ID,USA_LAT,USA_LON,USA_RECORD,USA_STATUS,USA_WIND,USA_PRES,USA_SSHS
,Year,,,,,,,,degrees_north,degrees_east,kts,mb,, ,km,km,,, ,degrees_north,degrees_east,, ,kts,mb,1
2021233N15301,2021,18,NA,CS,IDA,2021-08-26 18:00:00,TS,17.4,-79.5,35,1006,hurdat,MAIN,400,200,O,hurdat,AL092021,17.4,-79.5, ,TS,35,1006,0
2021233N15301,2021,18,NA,CS,IDA,2021-08-29 16:55:00,TS,29.1,-90.2,130,931,hurdat,MAIN,0,0,O,hurdat,AL092021,29.1,-90.2,L,HU,130,931,4
2021999N99999,2021,99,NA,NA,SPURLET,2021-09-01 00:00:00,DS,10.0,-40.0,,, ,spur,1000,900,O,, ,,,, ,XX,,, -5
"""


def test_sshws_table_is_the_official_nhc_knot_table():
    assert sshws_from_knots(33) == "TD"
    assert sshws_from_knots(34) == "TS"
    assert sshws_from_knots(63) == "TS"
    assert sshws_from_knots(64) == "1"
    assert sshws_from_knots(82) == "1"
    assert sshws_from_knots(83) == "2"
    assert sshws_from_knots(95) == "2"
    assert sshws_from_knots(96) == "3"
    assert sshws_from_knots(112) == "3"
    assert sshws_from_knots(113) == "4"
    assert sshws_from_knots(136) == "4"
    assert sshws_from_knots(137) == "5"
    assert sshws_from_knots(-99) is None
    assert sshws_from_knots(None) is None
    assert MAJOR_MIN_KT == 96
    assert ACE_HYPERACTIVE == 159.0
    assert NAMED_STORMS_THRESHOLD == 18


def test_ace_skips_asynoptic_missing_and_non_named():
    assert ace_contribution(130, "1655", "HU") == 0.0
    assert ace_contribution(130, "1800", "HU") == pytest.approx(1.69)
    assert ace_contribution(30, "1800", "TD") == 0.0
    assert ace_contribution(None, "1800", "HU") == 0.0
    assert ace_contribution(40, "1200", "EX") == 0.0


def test_parse_lat_lon_uses_published_hemispheres():
    assert parse_lat("29.1N") == pytest.approx(29.1)
    assert parse_lat("10.0S") == pytest.approx(-10.0)
    assert parse_lon("90.2W") == pytest.approx(-90.2)
    assert parse_lon("10.0E") == pytest.approx(10.0)
    with pytest.raises(ValueError):
        parse_lat("29.1")


def test_parse_hurdat2_ida_landfalls_and_peak():
    storms, gaps = parse_hurdat2(MINI_HURDAT2)
    assert gaps == []
    assert [s.storm_id for s in storms] == ["AL092021", "AL182021"]
    ida = storms[0]
    assert ida.name == "IDA"
    assert ida.year == 2021
    assert ida.reached_hu is True
    assert ida.reached_major is True
    assert ida.peak_wind_kt == 130
    assert ida.peak_sshws == "4"
    assert ida.n_landfalls == 2
    assert ida.hu_landfall is True
    assert ida.major_landfall is True
    # ACE: synoptic hours only. The 1655 / 130 kt landfall is asynoptic.
    assert ida.ace == pytest.approx((35 * 35 + 70 * 70 + 125 * 125) / 10_000)
    wade = storms[1]
    assert wade.reached_hu is False
    assert wade.n_landfalls == 0
    assert wade.peak_sshws == "TS"


def test_unknown_status_is_a_gap_not_invented():
    text = MINI_HURDAT2.replace("20211001, 0600,  , TS,", "20211001, 0600,  , ZZ,")
    storms, gaps = parse_hurdat2(text)
    assert storms[1].storm_id == "AL182021"
    assert any("unknown HURDAT2 status" in g for g in gaps)
    assert storms[1].n_declared == 2
    assert len(storms[1].points) == 1


def test_coverage_and_season_rows_are_counts():
    storms, gaps = parse_hurdat2(MINI_HURDAT2)
    cov = coverage_table(storms, gaps)
    assert cov["n_systems"] == 2
    assert cov["first_year"] == 2021
    assert cov["last_year"] == 2021
    assert cov["n_hurricanes_HU"] == 1
    assert cov["n_with_L"] == 1
    assert cov["n_hu_landfall_L"] == 1
    assert cov["n_major_landfall_L"] == 1
    assert cov["n_parse_gaps"] == 0
    assert cov["peak_sshws_counts"]["4"] == 1
    assert cov["peak_sshws_counts"]["TS"] == 1
    rows = season_rows(storms)
    assert len(rows) == 1
    assert rows[0]["n_named"] == 2
    assert rows[0]["n_hurricanes"] == 1
    assert rows[0]["event_named_ge_18"] is False
    assert rows[0]["event_any_hu_landfall_L"] is True


def test_discover_picks_the_newest_atlantic_file():
    html = """
    <a href="hurdat2-1851-2024-040425.txt">old</a>
    <a href="hurdat2-nepac-1949-2025-02272026.txt">pacific</a>
    <a href="hurdat2-1851-2025-02272026.txt">new</a>
    <a href="hurdat2-format-atlantic.pdf">doc</a>
    """
    info = discover_atlantic_filename(html)
    assert info is not None
    assert info["filename"] == "hurdat2-1851-2025-02272026.txt"
    assert info["end_year"] == "2025"


def test_spur_types_seen_in_the_na_file_are_excluded():
    assert is_spur_type("spur") is True
    assert is_spur_type("spur-other") is True
    assert is_spur_type("spur-merge") is True
    assert is_spur_type("main") is False
    assert is_spur_type("PROVISIONAL") is False


def test_ibtracs_drops_spur_and_reads_published_landfall():
    storms, gaps = parse_ibtracs_na(MINI_IBTRACS)
    assert gaps == []
    assert len(storms) == 2
    ida = next(s for s in storms if s.sid == "2021233N15301")
    spur = next(s for s in storms if s.sid == "2021999N99999")
    assert ida.usa_atcf_id == "AL092021"
    assert ida.reached_hu_status is True
    assert ida.peak_usa_sshs == 4
    assert ida.n_landfall_zero == 1
    assert ida.n_usa_record_L == 1
    assert spur.is_spur_only is True
    cov = ib_coverage(storms, gaps)
    assert cov["n_systems_in_file"] == 2
    assert cov["n_systems_counted"] == 1
    assert cov["n_spur_only_excluded"] == 1
    assert cov["n_with_landfall_zero"] == 1
    assert cov["n_with_usa_record_L"] == 1


def test_eval_script_offline(tmp_path, monkeypatch):
    import scripts.eval_hurdat2_ibtracs as ev

    h_cache = tmp_path / "h"
    i_cache = tmp_path / "i"
    h_cache.mkdir()
    i_cache.mkdir()
    (h_cache / "hurdat2-1851-2021-01012022.txt").write_text(MINI_HURDAT2, encoding="utf-8")
    (i_cache / "ibtracs.NA.list.v04r01.csv").write_text(MINI_IBTRACS, encoding="utf-8")
    out = tmp_path / "out"
    monkeypatch.setattr("sys.argv", [
        "eval_hurdat2_ibtracs.py", "--skip-fetch",
        "--hurdat-cache", str(h_cache),
        "--ibtracs-cache", str(i_cache),
        "--out-dir", str(out),
    ])
    assert ev.main() == 0
    counts = json.loads((out / "hurdat2_ibtracs_counts.json").read_text(encoding="utf-8"))
    assert counts["catalogue_truth"] == "HURDAT2 / IBTrACS"
    assert counts["champion_switched"] is False
    assert counts["forecast_scored"] is False
    assert counts["nhc_decks_started"] is False
    assert counts["hurdat2"]["coverage"]["n_systems"] == 2
    assert counts["ibtracs"]["coverage"]["n_systems_counted"] == 1
    assert counts["overlap_atcf"]["n_same_atcf_id"] == 1
    assert counts["verdicts"]["HURDAT2 / IBTrACS"] == "testée, ça aide"
    assert counts["verdicts"]["Ouragan formation"] == "cible Tier 1 (pas encore testée)"
    assert counts["verdicts"]["NHC a-decks / b-decks"] == "pas encore testée"
    assert "Sécheresse Méditerranée" in counts["verdicts"]
    report = (out / "hurdat2_ibtracs_report.md").read_text(encoding="utf-8")
    assert "HURDAT2 / IBTrACS" in report
    assert "Pas de BSS inventé" in report
