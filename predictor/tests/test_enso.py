"""Tests hors réseau : parse RONI, seuils CPC, épisodes, script."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from src.truth.enso import (
    COLD_LT,
    MIN_CONSECUTIVE_SEASONS,
    PHASE_EL_NINO,
    PHASE_LA_NINA,
    PHASE_NEUTRE,
    WARM_GT,
    find_gaps,
    inventory,
    mark_official_episodes,
    parse_roni_ascii,
    value_phase,
)

FIXTURE = """SEAS YR ANOM
DJF 2000 -0.50
JFM 2000 -0.51
FMA 2000 -0.60
MAM 2000 -0.70
AMJ 2000 -0.80
MJJ 2000 -0.90
JJA 2000 0.00
JAS 2000 0.50
ASO 2000 0.51
SON 2000 0.60
OND 2000 0.70
NDJ 2000 0.80
DJF 2001 0.40
"""


def test_published_thresholds_are_cpc_quotes():
    assert WARM_GT == 0.5
    assert COLD_LT == -0.5
    assert MIN_CONSECUTIVE_SEASONS == 5


def test_exact_half_degree_is_neutre():
    assert value_phase(0.50) == PHASE_NEUTRE
    assert value_phase(-0.50) == PHASE_NEUTRE
    assert value_phase(0.51) == PHASE_EL_NINO
    assert value_phase(-0.51) == PHASE_LA_NINA


def test_parse_and_official_five_season_rule():
    rows = parse_roni_ascii(FIXTURE)
    assert len(rows) == 13
    assert rows[0].value_phase == PHASE_NEUTRE          # -0.50
    assert rows[1].value_phase == PHASE_LA_NINA         # -0.51
    assert rows[7].value_phase == PHASE_NEUTRE          # +0.50
    marked, episodes = mark_official_episodes(rows)
    assert len(episodes) == 1
    assert episodes[0].phase == PHASE_LA_NINA
    assert episodes[0].n_seasons == 5
    assert episodes[0].start_label == "JFM 2000"
    assert episodes[0].end_label == "MJJ 2000"
    warm = [r for r in marked if r.value_phase == PHASE_EL_NINO]
    assert len(warm) == 4
    assert all(not r.in_official_episode for r in warm)


def test_four_consecutive_is_not_an_episode():
    text = "SEAS YR ANOM\n"
    seasons = ["DJF", "JFM", "FMA", "MAM"]
    for s in seasons:
        text += f"{s} 1999 0.60\n"
    text += "AMJ 1999 0.10\n"
    rows = parse_roni_ascii(text)
    _, episodes = mark_official_episodes(rows)
    assert episodes == []
    inv = inventory(rows)
    assert inv["seasons_by_value"]["el_nino"] == 4
    assert inv["seasons_by_official_episode"]["el_nino"] == 0
    assert inv["short_runs_below_5"]["el_nino"][0]["n_seasons"] == 4


def test_gap_in_the_middle_is_reported():
    text = "SEAS YR ANOM\nDJF 1950 0.00\nFMA 1950 0.10\n"
    rows = parse_roni_ascii(text)
    gaps = find_gaps(rows)
    assert gaps == [{
        "kind": "hole",
        "season": "JFM",
        "year": 1950,
        "label": "JFM 1950",
    }]


def test_inventory_year_mix_and_open_year():
    rows = parse_roni_ascii(FIXTURE)
    inv = inventory(rows)
    assert inv["coverage"]["n_holes"] == 0
    assert inv["coverage"]["first"] == "DJF 2000"
    assert inv["coverage"]["last"] == "DJF 2001"
    assert inv["years_by_value"]["years_with_both"] == [2000]
    assert inv["years_by_value"]["years_incomplete"] == [2001]
    assert inv["coverage"]["trailing_open_year"][0]["n_missing"] == 11
    assert inv["n_la_nina_episodes"] == 1
    assert inv["n_el_nino_episodes"] == 0


def test_unknown_season_is_not_invented():
    with pytest.raises(ValueError, match="saison CPC inconnue"):
        parse_roni_ascii("SEAS YR ANOM\nXYZ 1950 0.10\n")


def test_committed_snapshot_matches_inventory():
    root = Path(__file__).resolve().parent.parent / "data" / "truth" / "enso"
    ascii_path = root / "RONI.ascii.txt"
    json_path = root / "enso_inventory.json"
    if not ascii_path.exists() or not json_path.exists():
        pytest.skip("snapshot officiel pas encore écrit")
    inv = inventory(parse_roni_ascii(ascii_path.read_text(encoding="utf-8")))
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["catalogue_name"] == "Régime ENSO"
    assert saved["champion_switched"] is False
    assert saved["kalshi_temperature_scored"] is False
    assert inv["coverage"]["n_holes"] == 0
    assert inv["coverage"]["first"] == "DJF 1950"
    assert inv["seasons_by_value"] == saved["seasons_by_value"]
    assert inv["n_el_nino_episodes"] == saved["n_el_nino_episodes"]
    assert inv["n_la_nina_episodes"] == saved["n_la_nina_episodes"]
    assert (
        inv["seasons_by_value"]["el_nino"]
        + inv["seasons_by_value"]["la_nina"]
        + inv["seasons_by_value"]["neutre"]
        == inv["coverage"]["n_seasons"]
    )


def test_eval_script_skip_fetch(tmp_path: Path, monkeypatch):
    raw = tmp_path / "RONI.ascii.txt"
    raw.write_text(FIXTURE, encoding="utf-8")
    scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import eval_enso
    monkeypatch.setattr(
        "sys.argv",
        ["eval_enso.py", "--skip-fetch", "--out-dir", str(tmp_path)],
    )
    assert eval_enso.main() == 0
    report = (tmp_path / "enso_report.md").read_text(encoding="utf-8")
    payload = json.loads((tmp_path / "enso_inventory.json").read_text(encoding="utf-8"))
    assert payload["champion_switched"] is False
    assert payload["kalshi_temperature_scored"] is False
    assert payload["seasonal_forecast_scored"] is False
    assert payload["catalogue_name"] == "Régime ENSO"
    assert "El Niño (RONI > 0.5)" in report
    assert payload["seasons_by_value"]["la_nina"] == 5
