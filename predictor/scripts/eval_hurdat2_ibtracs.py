"""eval_hurdat2_ibtracs.py — vérité HURDAT2 / IBTrACS (Atlantique).

FR : Compte le best-track officiel NHC (HURDAT2 Atlantique) puis le
fichier NA IBTrACS v04r01. Pas de prévision NHC. Pas de score. Le
champion Kalshi n'est pas touché. Aucun chiffre inventé.

Usage:
    python scripts/eval_hurdat2_ibtracs.py
    python scripts/eval_hurdat2_ibtracs.py --skip-fetch
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.truth.hurdat2 import (  # noqa: E402
    ACE_HYPERACTIVE, HURDAT2_DIR, HURDAT2_FORMAT_PDF, HURDAT2_OUT,
    HURDAT2_PAGE, NAMED_STORMS_THRESHOLD, SSHWS_URL, Hurdat2Client,
    coverage_table as hurdat_coverage, season_rows,
)
from src.truth.ibtracs import (  # noqa: E402
    IBTRACS_COLUMNS_PDF, IBTRACS_NA_URL, IBTRACS_PRODUCT, IbtracsClient,
    countable, coverage_table as ibtracs_coverage,
)

CATALOGUE_TRUTH = "HURDAT2 / IBTrACS"
TARGETS = ("Ouragan formation", "Ouragan intensité", "Ouragan landfall")


def overlap_atcf(hurdat_storms, ibtracs_storms) -> dict[str, Any]:
    """Compare published ATCF IDs. Missing IDs stay missing."""
    h_ids = {s.storm_id for s in hurdat_storms}
    i_kept = countable(ibtracs_storms)
    i_ids = {s.usa_atcf_id for s in i_kept if s.usa_atcf_id}
    both = sorted(h_ids.intersection(i_ids))
    only_h = sorted(h_ids - i_ids)
    only_i = sorted(i_ids - h_ids)
    i_blank = sum(1 for s in i_kept if not s.usa_atcf_id)
    return {
        "n_hurdat2_ids": len(h_ids),
        "n_ibtracs_with_atcf_id": len(i_ids),
        "n_ibtracs_blank_atcf_id": i_blank,
        "n_same_atcf_id": len(both),
        "n_hurdat2_id_not_in_ibtracs": len(only_h),
        "n_ibtracs_atcf_id_not_in_hurdat2": len(only_i),
        "note": (
            "Comparaison sur USA_ATCF_ID / identifiant HURDAT2 tels quels. "
            "Un ID vide n'est pas inventé."
        ),
    }


def verdicts(h_ok: bool, i_ok: bool) -> dict[str, str]:
    """Catalogue statuses. Names are not renamed. No forecast scored."""
    truth = "testée, ça aide" if (h_ok and i_ok) else "bloquée"
    return {
        CATALOGUE_TRUTH: truth,
        "Ouragan formation": "cible Tier 1 (pas encore testée)",
        "Ouragan intensité": "cible Tier 1 (pas encore testée)",
        "Ouragan landfall": "cible Tier 1 (pas encore testée)",
        "NHC a-decks / b-decks": "pas encore testée",
        "Marché ouragan Kalshi": "pas encore testée",
        "SEAS5": "pas encore testée",
        "C3S multi-modèle": "pas encore testée",
        "Régime ENSO": "pas encore testée",
        "Sécheresse Méditerranée": "cible Tier 1 (pas encore testée)",
        "Sécheresse Inde": "cible Tier 1 (pas encore testée)",
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    h = payload["hurdat2"]["coverage"]
    i = payload["ibtracs"]["coverage"]
    ov = payload["overlap_atcf"]
    lines = [
        f"# {CATALOGUE_TRUTH} : comptes mesurés",
        "",
        f"Vérité catalogue : {CATALOGUE_TRUTH}.",
        "Cibles : Ouragan formation / intensité / landfall.",
        "Aucune prévision NHC notée. Champion Kalshi inchangé.",
        "Aucun chiffre inventé.",
        "",
        "## HURDAT2 Atlantique (NHC)",
        "",
        f"Fichier : `{payload['hurdat2']['source']['filename']}`.",
        f"URL : {payload['hurdat2']['source']['url']}.",
        f"SHA256 : `{payload['hurdat2']['sha256']}`.",
        "",
        "| Mesure | Valeur |",
        "|---|---:|",
        f"| Systèmes | {h['n_systems']} |",
        f"| Première année | {h['first_year']} |",
        f"| Dernière année | {h['last_year']} |",
        f"| Années avec au moins 1 système | {h['n_years_with_a_system']} |",
        f"| Années manquantes dans l'intervalle | {h['n_missing_years_in_span']} |",
        f"| Atteint TS / SS / HU (nommés) | {h['n_named']} |",
        f"| Atteint HU | {h['n_hurricanes_HU']} |",
        f"| Majeur (vent ≥ 96 kt) | {h['n_major_sshws']} |",
        f"| Au moins un drapeau L | {h['n_with_L']} |",
        f"| Points L | {h['n_L_points']} |",
        f"| Landfall L en statut HU | {h['n_hu_landfall_L']} |",
        f"| Landfall L majeur (vent ≥ 96 kt) | {h['n_major_landfall_L']} |",
        f"| Vent max manquant | {h['n_peak_wind_missing']} |",
        f"| Erreurs de parse | {h['n_parse_gaps']} |",
        f"| Saisons named ≥ {NAMED_STORMS_THRESHOLD} | {h['n_seasons_named_ge_18']} |",
        f"| Saisons ACE ≥ {int(ACE_HYPERACTIVE)} | {h['n_seasons_ace_ge_159']} |",
        f"| Saisons avec landfall HU (L) | {h['n_seasons_any_hu_landfall_L']} |",
        f"| Saisons avec landfall majeur (L) | {h['n_seasons_any_major_landfall_L']} |",
        "",
        "Pic d'intensité (échelle officielle NHC, nœuds) :",
        "",
        "| Pic | Systèmes |",
        "|---|---:|",
    ]
    for label, n in h["peak_sshws_counts"].items():
        lines.append(f"| {label} | {n} |")
    lines += [
        "",
        h["landfall_L_gap"],
        "",
        "## IBTrACS Atlantique nord (NCEI v04r01)",
        "",
        f"Fichier : `{payload['ibtracs']['filename']}`.",
        f"URL : {payload['ibtracs']['url']}.",
        f"SHA256 : `{payload['ibtracs']['sha256']}`.",
        "",
        "| Mesure | Valeur |",
        "|---|---:|",
        f"| Systèmes dans le fichier | {i['n_systems_in_file']} |",
        f"| Systèmes comptés (hors spur) | {i['n_systems_counted']} |",
        f"| Spur exclus | {i['n_spur_only_excluded']} |",
        f"| Dont provisoires | {i['n_provisional_among_counted']} |",
        f"| Première saison | {i['first_season']} |",
        f"| Dernière saison | {i['last_season']} |",
        f"| Saisons manquantes dans l'intervalle | {i['n_missing_seasons_in_span']} |",
        f"| Nommés (USA_STATUS TS/SS/HU/HR) | {i['n_named_usa_status']} |",
        f"| Ouragan (USA_STATUS HU/HR) | {i['n_hurricanes_usa_status']} |",
        f"| USA_SSHS ≥ 1 | {i['n_cat1_plus_usa_sshs']} |",
        f"| Majeur (USA_SSHS ≥ 3 ou vent ≥ 96 kt) | {i['n_major_usa_sshs_or_wind']} |",
        f"| LANDFALL = 0 | {i['n_with_landfall_zero']} |",
        f"| Points LANDFALL = 0 | {i['n_landfall_zero_points']} |",
        f"| USA_RECORD L | {i['n_with_usa_record_L']} |",
        f"| Points USA_RECORD L | {i['n_usa_record_L_points']} |",
        f"| Erreurs de parse | {i['n_parse_gaps']} |",
        "",
        "Pic USA_SSHS (échelle publiée NCEI) :",
        "",
        "| Pic | Systèmes |",
        "|---|---:|",
    ]
    for label, n in i["peak_usa_sshs_counts"].items():
        lines.append(f"| {label} | {n} |")
    lines += [
        "",
        i["landfall_note"],
        "",
        "## Recouvrement des identifiants ATCF",
        "",
        f"Même ID : {ov['n_same_atcf_id']}. "
        f"HURDAT2 sans ID IBTrACS : {ov['n_hurdat2_id_not_in_ibtracs']}. "
        f"IBTrACS avec ID hors HURDAT2 : {ov['n_ibtracs_atcf_id_not_in_hurdat2']}. "
        f"IBTrACS sans USA_ATCF_ID : {ov['n_ibtracs_blank_atcf_id']}.",
        "",
        "## Verdicts (noms du catalogue, non renommés)",
        "",
    ]
    for name, status in payload["verdicts"].items():
        lines.append(f"- {name} : {status}")
    lines += [
        "",
        "Pas de score NHC a-decks / b-decks dans ce run.",
        "Pas de BSS inventé pour la sécheresse US.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skip-fetch", action="store_true")
    p.add_argument("--out-dir", default=str(HURDAT2_OUT))
    p.add_argument("--hurdat-cache", default="")
    p.add_argument("--ibtracs-cache", default="")
    args = p.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    h_kwargs: dict[str, Any] = {}
    i_kwargs: dict[str, Any] = {}
    if args.hurdat_cache:
        h_kwargs["cache_dir"] = Path(args.hurdat_cache)
    if args.ibtracs_cache:
        i_kwargs["cache_dir"] = Path(args.ibtracs_cache)

    print(f"{CATALOGUE_TRUTH}", flush=True)
    print("HURDAT2 Atlantique ...", flush=True)
    h_raw = Hurdat2Client(**h_kwargs).fetch_atlantic(allow_network=not args.skip_fetch)
    h_storms = h_raw["storms"]
    h_cov = hurdat_coverage(h_storms, h_raw["gaps"])
    h_seasons = season_rows(h_storms)

    print("IBTrACS NA ...", flush=True)
    i_raw = IbtracsClient(**i_kwargs).fetch_na(allow_network=not args.skip_fetch)
    i_storms = i_raw["storms"]
    i_cov = ibtracs_coverage(i_storms, i_raw["gaps"])
    ov = overlap_atcf(h_storms, i_storms)

    h_ok = h_cov.get("n_systems", 0) > 0 and h_cov.get("n_parse_gaps", 1) == 0
    i_ok = i_cov.get("n_systems_counted", 0) > 0 and i_cov.get("n_parse_gaps", 1) == 0

    payload = {
        "catalogue_truth": CATALOGUE_TRUTH,
        "targets": list(TARGETS),
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "champion_switched": False,
        "real_money": False,
        "forecast_scored": False,
        "nhc_decks_started": False,
        "hurdat2": {
            "page": HURDAT2_PAGE,
            "directory": HURDAT2_DIR,
            "format_pdf": HURDAT2_FORMAT_PDF,
            "sshws_url": SSHWS_URL,
            "source": h_raw["source"],
            "sha256": h_raw["sha256"],
            "n_bytes": h_raw["n_bytes"],
            "coverage": h_cov,
            "seasons": h_seasons,
        },
        "ibtracs": {
            "url": IBTRACS_NA_URL,
            "filename": i_raw["filename"],
            "version": i_raw["version"],
            "columns_pdf": IBTRACS_COLUMNS_PDF,
            "product_url": IBTRACS_PRODUCT,
            "sha256": i_raw["sha256"],
            "n_bytes": i_raw["n_bytes"],
            "coverage": i_cov,
        },
        "overlap_atcf": ov,
        "verdicts": verdicts(h_ok, i_ok),
        "next_forecast_step": (
            "Quand la vérité est comptée : archives NHC a-decks / b-decks "
            "(prévisions vs best-track), sans les commencer ici."
        ),
    }
    (out_dir / "hurdat2_ibtracs_counts.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    (out_dir / "hurdat2_seasons.json").write_text(
        json.dumps(h_seasons, indent=2), encoding="utf-8"
    )
    write_report(out_dir / "hurdat2_ibtracs_report.md", payload)
    print(json.dumps({
        "hurdat2_systems": h_cov.get("n_systems"),
        "hurdat2_years": [h_cov.get("first_year"), h_cov.get("last_year")],
        "hurdat2_HU": h_cov.get("n_hurricanes_HU"),
        "hurdat2_L": h_cov.get("n_with_L"),
        "hurdat2_gaps": h_cov.get("n_parse_gaps"),
        "ibtracs_counted": i_cov.get("n_systems_counted"),
        "ibtracs_seasons": [i_cov.get("first_season"), i_cov.get("last_season")],
        "ibtracs_gaps": i_cov.get("n_parse_gaps"),
        "verdicts": payload["verdicts"],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
