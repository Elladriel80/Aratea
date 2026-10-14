"""Tests hors réseau : C3S multi-modèle, trous, gates PR 246, pas de CDS."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.forecast.c3s_offline import (
    C3S_DIR,
    C3S_REQUIRED,
    EXPECTED_CENTRES,
    FORECAST_FILENAME,
    FORECAST_NAME,
    LOCAL_FORECAST_CSV,
    SHARED_FORECAST_CSV,
    aggregate_equal_weight,
    find_c3s_csv,
    forecast_status,
    load_c3s_csv,
)
from src.score.c3s_ab import (
    BSS_GATE,
    MIN_SEASONS_FOR_GATE,
    PUBLISHED_SEAS5_BASELINE,
    compare_to_ecmwf51,
    score_all,
)


def _write_csv(path: Path, header: str, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def _header() -> str:
    return ",".join(C3S_REQUIRED)


def _cell(
    origin: str,
    system: int,
    region: str,
    year: int,
    lead: int,
    tp: float,
    n_members: int = 10,
    init_month: int = 5,
) -> str:
    return (
        f"{origin},{system},{region},{year},{init_month},{lead},"
        f"{tp},{n_members},12"
    )


def test_name_gates_and_expected_centres():
    assert FORECAST_NAME == "C3S multi-modèle"
    assert BSS_GATE == 0.05
    assert MIN_SEASONS_FOR_GATE == 10
    assert EXPECTED_CENTRES == (
        ("meteo_france", 8),
        ("dwd", 21),
        ("cmcc", 35),
        ("ncep", 2),
        ("ecmwf", 51),
    )
    assert SHARED_FORECAST_CSV == Path(
        "/workspace/cds-test/c3s-monthly/c3s_tp_monthly.csv"
    )
    assert LOCAL_FORECAST_CSV == C3S_DIR / FORECAST_FILENAME
    assert PUBLISHED_SEAS5_BASELINE["computed"] is False
    assert PUBLISHED_SEAS5_BASELINE["C"]["med"]["bss"] == 0.0552
    assert PUBLISHED_SEAS5_BASELINE["C"]["india"]["bss"] == -0.0707
    assert PUBLISHED_SEAS5_BASELINE["B"]["med"]["bss"] is None
    assert PUBLISHED_SEAS5_BASELINE["B"]["india"]["bss"] is None
    assert PUBLISHED_SEAS5_BASELINE["pooled"] is False


def test_example_file_is_not_a_forecast():
    example = C3S_DIR / "c3s_tp_monthly.csv.example"
    text = example.read_text(encoding="utf-8").strip()
    assert text == _header()
    assert find_c3s_csv(include_shared=False) is None


def test_equal_weight_ignores_members_and_does_not_fill_holes(tmp_path):
    rows = [
        _cell("ecmwf", 51, "MED", 2001, 2, 0, n_members=100),
        _cell("meteo_france", 8, "MED", 2001, 2, 90, n_members=1),
        _cell("ukmo", 602, "MED", 2001, 2, 1000, n_members=50),
    ]
    path = tmp_path / "c3s_tp_monthly.csv"
    _write_csv(path, _header(), rows)
    loaded = load_c3s_csv(path)
    assert any(not row["expected"] for row in loaded)
    means = aggregate_equal_weight(loaded)
    assert len(means) == 1
    assert means[0]["tp_mean_mm"] == pytest.approx(45.0)
    assert means[0]["n_centres"] == 2
    missing = {(c["origin"], c["system"]) for c in means[0]["missing_centres"]}
    assert missing == {("dwd", 21), ("cmcc", 35), ("ncep", 2)}
    assert means[0]["weighting"] == "equal_centre"


def test_three_centres_mean_is_not_padded(tmp_path):
    rows = [
        _cell("meteo_france", 8, "MED", 2001, 2, 10),
        _cell("dwd", 21, "MED", 2001, 2, 20),
        _cell("cmcc", 35, "MED", 2001, 2, 30),
    ]
    path = tmp_path / "c3s_tp_monthly.csv"
    _write_csv(path, _header(), rows)
    means = aggregate_equal_weight(load_c3s_csv(path))
    assert means[0]["tp_mean_mm"] == pytest.approx(20.0)
    assert means[0]["n_centres"] == 3


def test_seas5_label_counts_as_ecmwf_51(tmp_path):
    path = tmp_path / "c3s_tp_monthly.csv"
    _write_csv(path, _header(), [_cell("SEAS5", 51, "India", 1993, 1, 12.5)])
    rows = load_c3s_csv(path)
    assert rows[0]["origin"] == "ecmwf"
    assert rows[0]["system"] == 51
    assert rows[0]["expected"] is True
    assert rows[0]["region"] == "india"


def test_duplicate_centre_cell_is_rejected(tmp_path):
    path = tmp_path / "c3s_tp_monthly.csv"
    _write_csv(path, _header(), [
        _cell("dwd", 21, "MED", 2001, 2, 10),
        _cell("dwd", 21, "MED", 2001, 2, 12),
    ])
    with pytest.raises(ValueError, match="doublon"):
        load_c3s_csv(path)


def test_unknown_region_is_rejected(tmp_path):
    path = tmp_path / "c3s_tp_monthly.csv"
    _write_csv(path, _header(), [_cell("dwd", 21, "Sahel", 2001, 2, 10)])
    with pytest.raises(ValueError, match="région C3S inconnue"):
        load_c3s_csv(path)


def test_shared_csv_is_read_before_repo_copy(tmp_path, monkeypatch):
    import src.forecast.c3s_offline as off

    shared = tmp_path / "cds-test" / "c3s-monthly" / "c3s_tp_monthly.csv"
    local = tmp_path / "forecasts" / "c3s" / "c3s_tp_monthly.csv"
    _write_csv(shared, _header(), [_cell("ecmwf", 51, "MED", 2001, 2, 11)])
    _write_csv(local, _header(), [_cell("dwd", 21, "MED", 2001, 2, 99)])
    monkeypatch.setattr(off, "SHARED_FORECAST_CSV", shared)
    found = find_c3s_csv(local.parent, include_shared=True)
    assert found == shared
    fallback = find_c3s_csv(local.parent, include_shared=False)
    assert fallback == local


def test_raw_netcdf_without_csv_is_blocked(tmp_path):
    folder = tmp_path / "c3s"
    folder.mkdir()
    (folder / "c3s_slice.nc").write_bytes(b"not-a-real-netcdf")
    status = forecast_status(folder, include_shared=False)
    assert status["present"] is False
    assert "c3s_slice.nc" in status["reason"]
    assert "Pas d'appel CDS" in status["reason"]
    assert status["filled_from_seas5"] is False


def test_dry_run_blocked_when_csv_absent(tmp_path):
    if SHARED_FORECAST_CSV.is_file() or LOCAL_FORECAST_CSV.is_file():
        pytest.skip("CSV C3S présent : le cas bloqué ne s'applique pas")
    payload = score_all(
        data_dir=tmp_path / "data",
        forecast_dir=tmp_path / "empty",
        include_shared=True,
    )
    assert payload["cds_called"] is False
    assert payload["champion_switched"] is False
    assert payload["bss_invented"] is False
    assert payload["pooled"] is False
    assert payload["filled_from_seas5"] is False
    assert payload["forecast"]["present"] is False
    assert "Mesure bloquée" in payload["forecast"]["reason"]
    assert "Pas de score inventé" in payload["forecast"]["reason"]
    assert payload["published_seas5_baseline"]["computed"] is False
    for key in ("A", "B", "C"):
        block = payload["ab"][key]
        assert block["verdict"] == "bloquée"
        assert block["bss"] is None
        assert block["n_seasons_scored"] == 0
        assert block["brier_forecast"] is None
        assert payload["ecmwf51"]["ab"][key]["bss"] is None
    assert payload["ab"]["C"]["bss"] != 0.0552
    assert payload["comparison"]["mix_beats_ecmwf51"] is None
    assert payload["comparison"]["uses_published_baseline"] is False
    assert payload["comparison"]["pooled"] is False
    assert payload["verdicts"][FORECAST_NAME] == "bloquée"
    missing = {
        (item["origin"], item["system"])
        for item in payload["forecast"]["inventory"]["missing_centres"]
    }
    assert missing == set(EXPECTED_CENTRES)


def test_header_only_does_not_invent_scores(tmp_path):
    folder = tmp_path / "c3s"
    _write_csv(folder / "c3s_tp_monthly.csv", _header(), [])
    payload = score_all(
        data_dir=tmp_path / "data",
        forecast_dir=folder,
        include_shared=False,
    )
    assert payload["ab"]["C"]["verdict"] == "bloquée"
    assert payload["ab"]["C"]["bss"] is None
    assert payload["ab"]["B"]["bss"] is None


def test_comparison_uses_recomputed_bss_not_the_published_one():
    multi = {
        "A": {"verdict": "bloquée", "by_region": {}},
        "B": {"verdict": "bloquée", "by_region": {}},
        "C": {"verdict": "testée, ça aide", "by_region": {
            "med": {"n": 12, "bss": 0.06, "verdict": "testée, ça aide"},
            "india": {"n": 12, "bss": 0.9, "verdict": "testée, ça aide"},
        }},
    }
    ecmwf = {
        "A": {"verdict": "bloquée", "by_region": {}},
        "B": {"verdict": "bloquée", "by_region": {}},
        "C": {"verdict": "testée, ça aide", "by_region": {
            "med": {"n": 12, "bss": 0.2, "verdict": "testée, ça aide"},
            "india": {"n": 12, "bss": -1.0, "verdict": "testée, ça n'aide pas"},
        }},
    }
    comp = compare_to_ecmwf51(multi, ecmwf)
    assert comp["region"] == "med"
    assert comp["pooled"] is False
    assert comp["mix_beats_ecmwf51"] is False
    assert comp["by_ab"]["C"]["india"]["mix_beats_ecmwf51"] is True
    assert comp["uses_published_baseline"] is False


def _skill_csv(years: range, centres: tuple[str, ...] = (
    "ecmwf", "meteo_france", "dwd", "cmcc", "ncep",
)) -> list[str]:
    systems = {
        "ecmwf": 51,
        "meteo_france": 8,
        "dwd": 21,
        "cmcc": 35,
        "ncep": 2,
    }
    rows = []
    for year in years:
        even = year % 2 == 0
        for region in ("MED", "India", "Midwest"):
            for lead in (2, 3, 4):
                for origin in centres:
                    if origin == "ecmwf":
                        tp = 100.0 if even else 0.0
                        members = 51
                    else:
                        tp = 0.0 if even else 100.0
                        members = 1
                    rows.append(_cell(
                        origin, systems[origin], region, year, lead, tp, members,
                    ))
    return rows


def _write_truth(data: Path, years: range, spei_event: int = 0) -> None:
    chirps = []
    usdm = []
    spei = []
    for year in years:
        even = year % 2 == 0
        med_event = 1 if even else 0
        india_event = 0 if even else 1
        chirps.append(f"med,{year},JJA,{40 + med_event},{med_event}")
        chirps.append(f"india,{year},JJA,{40 + india_event},{india_event}")
        usdm.append(f"midwest,{year},JJA,{20 + 20 * med_event},{med_event}")
        spei.append(f"med,{year},JJA,0.2,{spei_event}")
        spei.append(f"india,{year},JJA,0.2,{spei_event}")
    _write_csv(
        data / "truth" / "chirps" / "chirps_seasons.csv",
        "region,year,season,tp_mean_mm,event_below_climato",
        chirps,
    )
    _write_csv(
        data / "truth" / "usdm" / "usdm_seasons.csv",
        "region,year,season,d2_plus_mean,event_d2_plus_ge_30",
        usdm,
    )
    _write_csv(
        data / "truth" / "spei" / "spei6_seasons.csv",
        "region,year,season,spei6_mean,event_spei6_le_minus_1_5",
        spei,
    )


def test_tiny_fixture_scores_three_separate_abs(tmp_path):
    data = tmp_path / "data"
    folder = data / "forecasts" / "c3s"
    years = range(2001, 2013)
    _write_csv(folder / "c3s_tp_monthly.csv", _header(), _skill_csv(years))
    _write_truth(data, years, spei_event=0)
    payload = score_all(data_dir=data, forecast_dir=folder, include_shared=False)
    med = payload["ab"]["C"]["by_region"]["med"]
    india = payload["ab"]["C"]["by_region"]["india"]
    assert payload["pooled"] is False
    assert payload["ab"]["C"]["headline_region"] == "med"
    assert payload["ab"]["C"]["n_seasons_scored"] == 12
    assert med["n"] == 12
    assert india["n"] == 12
    assert med["n"] + india["n"] != payload["ab"]["C"]["n_seasons_scored"]
    assert med["verdict"] == "testée, ça aide"
    assert med["bss"] is not None and med["bss"] > BSS_GATE
    assert india["verdict"] == "testée, ça n'aide pas"
    assert payload["ab"]["C"]["verdict"] == "testée, ça aide"
    assert payload["ab"]["C"]["bss"] == med["bss"]
    assert payload["verdicts"][FORECAST_NAME] == "testée, ça aide (CHIRPS MED seulement)"
    assert payload["verdicts"]["Sécheresse Inde"] == "testée, ça n'aide pas"
    assert payload["champion_switched"] is False
    ecmwf_med = payload["ecmwf51"]["ab"]["C"]["by_region"]["med"]
    assert ecmwf_med["n"] == 12
    assert ecmwf_med["verdict"] == "testée, ça n'aide pas"
    assert payload["comparison"]["mix_beats_ecmwf51"] is True
    assert payload["comparison"]["region"] == "med"
    assert payload["comparison"]["by_ab"]["C"]["india"]["mix_beats_ecmwf51"] is False
    spei = payload["ab"]["B"]["by_region"]["med"]
    assert spei["n"] == 12
    assert spei["brier_climato"] == 0.0
    assert spei["bss"] is None
    assert spei["verdict"] == "bloquée"
    assert payload["ab"]["B"]["verdict"] == "bloquée"
    assert payload["ab"]["B"]["bss"] is None
    assert payload["forecast"]["inventory"]["missing_centres"] == []
    assert payload["filled_from_seas5"] is False


def test_four_seasons_stay_blocked_with_measured_n(tmp_path):
    data = tmp_path / "data"
    folder = data / "forecasts" / "c3s"
    years = range(2001, 2005)
    _write_csv(folder / "c3s_tp_monthly.csv", _header(), _skill_csv(years))
    _write_truth(data, years)
    payload = score_all(data_dir=data, forecast_dir=folder, include_shared=False)
    med = payload["ab"]["C"]["by_region"]["med"]
    assert med["n"] == 4
    assert med["verdict"] == "bloquée"
    assert med["gate_n_ge_10"] is False
    assert payload["ab"]["C"]["verdict"] == "bloquée"
    assert payload["verdicts"][FORECAST_NAME] == "bloquée"


def test_missing_ecmwf_is_a_hole_and_seas5_csv_is_not_read(tmp_path, monkeypatch):
    import src.forecast.seas5_offline as seas5

    def _boom(*_args, **_kwargs):
        raise AssertionError("le CSV SEAS5 ne doit pas être lu")

    monkeypatch.setattr(seas5, "find_forecast_csv", _boom)
    monkeypatch.setattr(seas5, "load_forecast_csv", _boom)
    data = tmp_path / "data"
    folder = data / "forecasts" / "c3s"
    years = range(2001, 2013)
    centres = ("meteo_france", "dwd", "cmcc", "ncep")
    _write_csv(
        folder / "c3s_tp_monthly.csv", _header(), _skill_csv(years, centres),
    )
    _write_truth(data, years)
    payload = score_all(data_dir=data, forecast_dir=folder, include_shared=False)
    missing = payload["forecast"]["inventory"]["missing_centres"]
    assert missing == [{
        "origin": "ecmwf",
        "system": 51,
        "label": "ECMWF système 51 (SEAS5)",
    }]
    assert payload["ecmwf51"]["filled_from_seas5_csv"] is False
    assert payload["ecmwf51"]["ab"]["C"]["bss"] is None
    assert payload["ecmwf51"]["ab"]["C"]["verdict"] == "bloquée"
    assert "non comblé" in payload["ecmwf51"]["ab"]["C"]["blocker"]
    assert payload["comparison"]["mix_beats_ecmwf51"] is None
    assert payload["ab"]["C"]["bss"] != PUBLISHED_SEAS5_BASELINE["C"]["med"]["bss"]
    med = payload["ab"]["C"]["by_region"]["med"]
    assert med["n"] == 12
    assert all(c["origin"] != "ecmwf" for c in (
        payload["forecast"]["inventory"]["expected_centres"]
    ) if c["present"])


def test_eval_script_dry_run_prints_bloquee(tmp_path, monkeypatch, capsys):
    if SHARED_FORECAST_CSV.is_file() or LOCAL_FORECAST_CSV.is_file():
        pytest.skip("CSV C3S présent : le cas bloqué ne s'applique pas")
    import scripts.eval_c3s_ab as ev

    out = tmp_path / "out"
    monkeypatch.setattr("sys.argv", [
        "eval_c3s_ab.py",
        "--data-dir", str(tmp_path / "data"),
        "--out-dir", str(out),
        "--forecast-dir", str(C3S_DIR),
    ])
    assert ev.main() == 0
    printed = capsys.readouterr().out
    report = (out / "c3s_ab_report.md").read_text(encoding="utf-8")
    payload = json.loads((out / "c3s_ab_report.json").read_text(encoding="utf-8"))
    assert "bloquée" in printed
    assert payload["forecast_name"] == "C3S multi-modèle"
    assert payload["champion_switched"] is False
    assert payload["cds_called"] is False
    assert payload["bss_invented"] is False
    assert payload["pooled"] is False
    assert payload["ab"]["C"]["bss"] is None
    assert payload["ab"]["B"]["bss"] is None
    assert payload["published_seas5_baseline"]["B"]["med"]["bss"] is None
    assert payload["published_seas5_baseline"]["computed"] is False
    assert "Pas de score inventé" in report
    assert "CDS non appelé" in report
    assert "MED seulement" in report
    assert "—" not in report
    assert "CDS_API_KEY" not in report


def test_eval_script_fixture(tmp_path, monkeypatch):
    import scripts.eval_c3s_ab as ev

    data = tmp_path / "data"
    folder = data / "forecasts" / "c3s"
    years = range(2001, 2013)
    csv_path = folder / "c3s_tp_monthly.csv"
    _write_csv(csv_path, _header(), _skill_csv(years))
    _write_truth(data, years)
    out = tmp_path / "out"
    monkeypatch.setattr("sys.argv", [
        "eval_c3s_ab.py",
        "--forecast-csv", str(csv_path),
        "--data-dir", str(data),
        "--out-dir", str(out),
        "--no-shared",
    ])
    assert ev.main() == 0
    payload = json.loads((out / "c3s_ab_report.json").read_text(encoding="utf-8"))
    assert payload["ab"]["C"]["verdict"] == "testée, ça aide"
    assert payload["ab"]["C"]["by_region"]["india"]["verdict"] == "testée, ça n'aide pas"
    assert payload["comparison"]["mix_beats_ecmwf51"] is True
    assert payload["ab"]["B"]["bss"] is None
    assert payload["champion_switched"] is False


def test_source_files_never_call_cds():
    root = Path(__file__).resolve().parents[1]
    files = [
        root / "src" / "forecast" / "c3s_offline.py",
        root / "src" / "score" / "c3s_ab.py",
        root / "scripts" / "eval_c3s_ab.py",
        root / "docs" / "c3s-multimodele-ab-2026-10-04.md",
        root / "data" / "forecasts" / "c3s" / "README.md",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "import cdsapi" not in text
        assert "from cdsapi" not in text
        assert "CDS_API_KEY" not in text
        assert "cds.climate.copernicus.eu" not in text
        assert "\u2014" not in text
        assert "\u2013" not in text
