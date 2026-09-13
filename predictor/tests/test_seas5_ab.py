"""Tests hors réseau : SEAS5 Phase 2 A/B, mode bloqué, gates, pas de CDS."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.forecast.seas5_offline import (
    DOWNLOAD_ENVELOPES, FORECAST_NAME, FORECAST_REQUIRED, PM_REGION_LABELS,
    REGION_ALIASES, SHARED_FORECAST_CSV, canonical_region,
    collapse_shortest_lead, find_forecast_csv, forecast_status, load_forecast_csv,
    load_pairs_csv, met_season, valid_year_month,
)
from src.score.seas5_ab import (
    BSS_GATE, MIN_SEASONS_FOR_GATE, brier_skill_score, leave_one_out_climato,
    region_verdict, score_all, skill_block,
)


def _write_csv(path: Path, header: str, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def test_name_is_seas5_and_gates_are_the_published_ones():
    assert FORECAST_NAME == "SEAS5"
    assert BSS_GATE == 0.05
    assert MIN_SEASONS_FOR_GATE == 10
    assert FORECAST_REQUIRED == (
        "region", "year", "init_month", "lead_month", "tp_mean_mm"
    )


def test_download_envelopes_match_pm_boxes():
    assert DOWNLOAD_ENVELOPES["med"]["cds_area"] == [45.0, -10.0, 30.0, 40.0]
    assert DOWNLOAD_ENVELOPES["midwest"]["cds_area"] == [49.5, -97.5, 36.0, -80.5]
    assert DOWNLOAD_ENVELOPES["southwest"]["cds_area"] == [42.0, -124.5, 31.3, -103.0]
    assert DOWNLOAD_ENVELOPES["india"]["cds_area"] == [22.1, 72.5, 11.5, 81.0]


def test_region_aliases_and_valid_month():
    assert PM_REGION_LABELS == {
        "MED": "med", "Midwest": "midwest", "Southwest": "southwest", "India": "india",
    }
    assert canonical_region("MED") == "med"
    assert canonical_region("Midwest") == "midwest"
    assert canonical_region("Southwest") == "southwest"
    assert canonical_region("India") == "india"
    assert canonical_region("Méditerranée") == "med"
    assert canonical_region("Inde") == "india"
    assert canonical_region("Maharashtra+Karnataka") == "india"
    assert SHARED_FORECAST_CSV.name == "seas5_tp_monthly.csv"
    assert valid_year_month(2020, 11, 1) == (2020, 11)
    assert valid_year_month(2020, 11, 3) == (2021, 1)
    assert met_season(2020, 12) == ("DJF", 2021)
    assert met_season(2021, 1) == ("DJF", 2021)
    with pytest.raises(ValueError, match="inconnue"):
        canonical_region("sahel")
    assert "cdsapi" not in REGION_ALIASES


def test_loo_climato_and_bss_are_not_invented():
    assert leave_one_out_climato([True]) == []
    assert leave_one_out_climato([True, False, False]) == pytest.approx([0.0, 0.5, 0.5])
    assert brier_skill_score(0.1, 0.2) == pytest.approx(0.5)
    assert brier_skill_score(0.1, 0.0) is None
    empty = skill_block([], [])
    assert empty["n"] == 0 and empty["bss"] is None
    assert region_verdict(4, 0.9) == "bloquée"
    assert region_verdict(10, None) == "bloquée"
    assert region_verdict(10, 0.05) == "testée, ça n'aide pas"
    assert region_verdict(10, 0.051) == "testée, ça aide"


def test_collapse_keeps_shortest_lead():
    rows = [
        {"region": "med", "valid_year": 2001, "valid_month": 6,
         "lead_month": 4, "tp_mean_mm": 10.0},
        {"region": "med", "valid_year": 2001, "valid_month": 6,
         "lead_month": 1, "tp_mean_mm": 12.0},
    ]
    out = collapse_shortest_lead(rows)
    assert len(out) == 1
    assert out[0]["lead_month"] == 1
    assert out[0]["tp_mean_mm"] == 12.0


def test_dry_mode_when_forecast_missing(tmp_path):
    data = tmp_path / "data"
    fc = data / "forecasts" / "seas5"
    fc.mkdir(parents=True)
    payload = score_all(data_dir=data, forecast_dir=fc, include_shared=False)
    assert payload["cds_called"] is False
    assert payload["champion_switched"] is False
    assert payload["bss_invented"] is False
    assert payload["forecast"]["present"] is False
    assert "Pas de score inventé" in payload["forecast"]["reason"]
    assert "seas5_tp_monthly.csv" in payload["forecast"]["reason"]
    assert payload["ab"]["A"]["bss"] is None
    for key in ("A", "B", "C"):
        block = payload["ab"][key]
        assert block["verdict"] == "bloquée"
        assert block["bss"] is None
        assert block["n_seasons_scored"] == 0
        assert block["brier_forecast"] is None
    assert payload["verdicts"][FORECAST_NAME] == "bloquée"
    assert payload["verdicts"]["Sécheresse US"] == "bloquée"


def test_raw_netcdf_without_csv_is_blocked(tmp_path):
    fc = tmp_path / "seas5"
    fc.mkdir()
    (fc / "seas5_slice.nc").write_bytes(b"not-a-real-netcdf")
    status = forecast_status(fc, include_shared=False)
    assert status["present"] is False
    assert "seas5_slice.nc" in status["reason"]
    assert "Pas d'appel CDS" in status["reason"]
    payload = score_all(
        data_dir=tmp_path / "data", forecast_dir=fc, include_shared=False
    )
    assert payload["ab"]["A"]["bss"] is None
    assert payload["ab"]["A"]["verdict"] == "bloquée"


def test_header_only_forecast_csv_does_not_invent_scores(tmp_path):
    fc = tmp_path / "seas5"
    _write_csv(fc / "regional_monthly.csv", ",".join(FORECAST_REQUIRED), [])
    rows = load_forecast_csv(fc / "regional_monthly.csv")
    assert rows == []
    payload = score_all(
        data_dir=tmp_path / "data", forecast_dir=fc, include_shared=False
    )
    assert payload["ab"]["A"]["bss"] is None
    assert payload["ab"]["A"]["n_seasons_scored"] == 0
    assert payload["ab"]["A"]["verdict"] == "bloquée"


def _pairs_rows(n: int, perfect: bool, region: str = "midwest") -> list[str]:
    seasons = ("DJF", "MAM", "JJA", "SON")
    rows = []
    for i in range(n):
        event = 1 if i % 2 == 0 else 0
        p = event if perfect else 1 - event
        year = 2000 + i
        season = seasons[i % 4]
        rows.append(f"{region},{year},{season},{p},{event}")
    return rows


def test_pairs_n_below_ten_is_blocked_with_measured_n(tmp_path):
    data = tmp_path / "data"
    fc = data / "forecasts" / "seas5"
    header = "region,year,season,p_forecast_dry,event"
    _write_csv(fc / "pairs_usdm.csv", header, _pairs_rows(4, True, "midwest"))
    payload = score_all(data_dir=data, forecast_dir=fc, include_shared=False)
    mw = payload["ab"]["A"]["by_region"]["midwest"]
    assert mw["n"] == 4
    assert mw["verdict"] == "bloquée"
    assert payload["ab"]["A"]["verdict"] == "bloquée"
    assert payload["verdicts"][FORECAST_NAME] == "bloquée"


def test_pairs_n_ten_bss_above_gate_helps(tmp_path):
    data = tmp_path / "data"
    fc = data / "forecasts" / "seas5"
    header = "region,year,season,p_forecast_dry,event"
    _write_csv(fc / "pairs_usdm.csv", header, _pairs_rows(12, True, "midwest"))
    payload = score_all(data_dir=data, forecast_dir=fc, include_shared=False)
    mw = payload["ab"]["A"]["by_region"]["midwest"]
    assert mw["n"] == 12
    assert mw["bss"] is not None and mw["bss"] > BSS_GATE
    assert mw["verdict"] == "testée, ça aide"
    assert payload["ab"]["A"]["verdict"] == "testée, ça aide"
    assert payload["verdicts"][FORECAST_NAME] == "testée, ça aide"
    assert payload["champion_switched"] is False


def test_pairs_n_ten_bss_not_above_gate_does_not_help(tmp_path):
    data = tmp_path / "data"
    fc = data / "forecasts" / "seas5"
    header = "region,year,season,p_forecast_dry,event"
    _write_csv(fc / "pairs_usdm.csv", header, _pairs_rows(12, False, "southwest"))
    payload = score_all(data_dir=data, forecast_dir=fc, include_shared=False)
    sw = payload["ab"]["A"]["by_region"]["southwest"]
    assert sw["n"] == 12
    assert sw["bss"] is not None and sw["bss"] <= BSS_GATE
    assert sw["verdict"] == "testée, ça n'aide pas"
    assert payload["ab"]["A"]["verdict"] == "testée, ça n'aide pas"


def test_chirps_headline_is_med_not_pooled(tmp_path):
    data = tmp_path / "data"
    fc = data / "forecasts" / "seas5"
    header = "region,year,season,p_forecast_dry,event"
    rows = _pairs_rows(12, True, "med") + _pairs_rows(12, False, "india")
    _write_csv(fc / "pairs_chirps.csv", header, rows)
    payload = score_all(data_dir=data, forecast_dir=fc, include_shared=False)
    c = payload["ab"]["C"]
    assert c["headline_region"] == "med"
    assert c["pooled"] is False
    assert c["n_seasons_scored"] == 12
    assert c["by_region"]["med"]["n"] == 12
    assert c["by_region"]["india"]["n"] == 12
    assert c["by_region"]["med"]["verdict"] == "testée, ça aide"
    assert c["by_region"]["india"]["verdict"] == "testée, ça n'aide pas"
    assert c["verdict"] == "testée, ça aide"
    assert c["bss"] == c["by_region"]["med"]["bss"]
    assert payload["verdicts"][FORECAST_NAME] == "testée, ça aide (CHIRPS MED seulement)"
    assert payload["verdicts"]["Sécheresse Méditerranée"] == "testée, ça aide"
    assert payload["verdicts"]["Sécheresse Inde"] == "testée, ça n'aide pas"


def test_regional_monthly_plus_usdm_truth_scores(tmp_path):
    data = tmp_path / "data"
    fc = data / "forecasts" / "seas5"
    truth = data / "truth" / "usdm"
    fc_rows = []
    truth_rows = []
    # 12 JJA seasons, 2001-2012. Dry forecast (low rain) matches D2+ years.
    for year in range(2001, 2013):
        event = 1 if year % 2 == 0 else 0
        rain = 20.0 if event else 80.0
        for month, lead in ((6, 1), (7, 2), (8, 3)):
            fc_rows.append(f"midwest,{year},6,{lead},{rain}")
        truth_rows.append(f"midwest,{year},JJA,{10.0 + 30.0 * event},{event}")
    _write_csv(fc / "regional_monthly.csv", ",".join(FORECAST_REQUIRED), fc_rows)
    _write_csv(
        truth / "usdm_seasons.csv",
        "region,year,season,d2_plus_mean,event_d2_plus_ge_30",
        truth_rows,
    )
    rows = load_forecast_csv(fc / "regional_monthly.csv")
    assert len(rows) == 36
    payload = score_all(data_dir=data, forecast_dir=fc, include_shared=False)
    mw = payload["ab"]["A"]["by_region"]["midwest"]
    assert mw["n"] == 12
    assert mw["verdict"] == "testée, ça aide"
    assert payload["ab"]["B"]["verdict"] == "bloquée"
    assert payload["ab"]["C"]["verdict"] == "bloquée"
    assert payload["ab"]["B"]["bss"] is None


def test_shared_pm_csv_is_read_before_repo_copy(tmp_path, monkeypatch):
    import src.forecast.seas5_offline as off

    shared_dir = tmp_path / "cds-test" / "seas5-monthly"
    local = tmp_path / "forecasts" / "seas5"
    header = ",".join(FORECAST_REQUIRED)
    _write_csv(shared_dir / "seas5_tp_monthly.csv", header, ["MED,2001,6,1,11.5"])
    _write_csv(local / "regional_monthly.csv", header, ["Midwest,2001,6,1,99.0"])
    monkeypatch.setattr(off, "SHARED_FORECAST_DIR", shared_dir)
    monkeypatch.setattr(off, "SHARED_FORECAST_CSV", shared_dir / "seas5_tp_monthly.csv")
    path = find_forecast_csv(local, include_shared=True)
    assert path == shared_dir / "seas5_tp_monthly.csv"
    rows = load_forecast_csv(path)
    assert rows[0]["region"] == "med"
    assert rows[0]["tp_mean_mm"] == 11.5
    fallback = find_forecast_csv(local, include_shared=False)
    assert fallback == local / "regional_monthly.csv"
    assert load_forecast_csv(fallback)[0]["region"] == "midwest"


def test_eval_script_dry(tmp_path, monkeypatch):
    import scripts.eval_seas5_ab as ev

    out = tmp_path / "out"
    fc = tmp_path / "seas5"
    fc.mkdir()
    monkeypatch.setattr("sys.argv", [
        "eval_seas5_ab.py",
        "--forecast-dir", str(fc),
        "--data-dir", str(tmp_path / "data"),
        "--out-dir", str(out),
    ])
    assert ev.main() == 0
    counts = json.loads((out / "seas5_ab_report.json").read_text(encoding="utf-8"))
    report = (out / "seas5_ab_report.md").read_text(encoding="utf-8")
    assert counts["forecast_name"] == "SEAS5"
    assert counts["champion_switched"] is False
    assert counts["cds_called"] is False
    assert counts["bss_invented"] is False
    assert counts["ab"]["A"]["bss"] is None
    assert "Pas de score inventé" in report
    assert "CDS non appelé" in report
    assert "CDS_API_KEY" not in report
    assert "—" not in report


def test_source_files_never_call_cds():
    root = Path(__file__).resolve().parents[1]
    files = [
        root / "src" / "forecast" / "seas5_offline.py",
        root / "src" / "score" / "seas5_ab.py",
        root / "scripts" / "eval_seas5_ab.py",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "import cdsapi" not in text
        assert "from cdsapi" not in text
        assert "CDS_API_KEY" not in text
        assert "cds.climate.copernicus.eu" not in text


def test_load_pairs_rejects_bad_event(tmp_path):
    path = tmp_path / "pairs_usdm.csv"
    _write_csv(
        path,
        "region,year,season,p_forecast_dry,event",
        ["midwest,2001,JJA,1,maybe"],
    )
    with pytest.raises(ValueError, match="booléen"):
        load_pairs_csv(path)
