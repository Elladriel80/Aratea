"""eval_enso.py — compte officiel Régime ENSO (CPC RONI).

FR : Télécharge la série officielle NOAA / CPC. Compte les saisons
El Niño / La Niña / neutre avec les seuils publiés. Pas de score de
prévision. Pas de notation Kalshi température. Pas SEAS5 / C3S.

EN : Official CPC RONI inventory only.

Usage:
    python scripts/eval_enso.py
    python scripts/eval_enso.py --skip-fetch
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.config import USER_AGENT  # noqa: E402
from src.truth.enso import (  # noqa: E402
    COLD_LT,
    MIN_CONSECUTIVE_SEASONS,
    PHASE_EL_NINO,
    PHASE_LA_NINA,
    RONI_ASCII_URL,
    SEASON_MONTHS,
    WARM_GT,
    inventory,
    parse_roni_ascii,
)
from src.truth.iem_cli import TRUTH_DIR  # noqa: E402

PHASE_FR = {
    PHASE_EL_NINO: "El Niño",
    PHASE_LA_NINA: "La Niña",
    "neutre": "neutre",
}


def fetch_roni(url: str, timeout: int = 30) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain"})
    with urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return raw.decode("utf-8", errors="replace")


def _fr_anom(x: float) -> str:
    return f"{x:+.2f}".replace(".", ",")


def write_md(path: Path, inv: dict, generated_at: str) -> None:
    src = inv["source"]
    cov = inv["coverage"]
    val = inv["seasons_by_value"]
    epc = inv["seasons_by_official_episode"]
    yv = inv["years_by_value"]
    lines = [
        "# Régime ENSO : compte officiel CPC RONI",
        "",
        f"Généré : {generated_at}.",
        "Série officielle NOAA / NCEP CPC depuis le 1er février 2026 : "
        "Relative Oceanic Niño Index (RONI).",
        "Pas de score de prévision. Pas de notation Kalshi température.",
        "",
        "## Source et seuils publiés (pas inventés)",
        "",
        f"- Fichier : `{src['ascii']}`",
        f"- Page : `{src['page']}`",
        f"- Annonce officielle (1er février 2026) : `{src['pns']}`",
        f"- Seuil El Niño (page CPC) : {src['thresholds_quoted']['warm_el_nino']}",
        f"- Seuil La Niña (page CPC) : {src['thresholds_quoted']['cold_la_nina']}",
        f"- Neutre ici : {src['thresholds_quoted']['neutre']}",
        f"- Épisode colorié (page CPC) : {src['thresholds_quoted']['official_episode']}",
        "- On compte le fichier ASCII (deux décimales). La page web arrondit à une décimale. "
        "On ne mélange pas les deux.",
        "- L'ancien ONI reste en ligne pour l'histoire. Il n'est pas compté ici.",
        "- CPC classe des saisons de 3 mois qui se chevauchent, pas une année civile.",
        "",
        "## Couverture",
        "",
        f"- Première saison : {cov['first']}",
        f"- Dernière saison : {cov['last']}",
        f"- Années civiles dans le fichier : {cov['n_calendar_years']} "
        f"({cov['first_year']} à {cov['last_year']})",
        f"- Saisons présentes : {cov['n_seasons']}",
        f"- Saisons attendues dans cet intervalle : {cov['n_expected_seasons_in_span']}",
        f"- Trous au milieu : {cov['n_holes']}",
        f"- Doublons : {cov['n_duplicates']}",
        "",
    ]
    if cov["gaps"]:
        lines += ["Trous ou doublons :", ""]
        for g in cov["gaps"]:
            lines.append(f"- {g}")
        lines.append("")
    else:
        lines += ["Aucun trou, aucun doublon dans l'intervalle du fichier.", ""]
    if cov["trailing_open_year"]:
        t = cov["trailing_open_year"][0]
        lines += [
            "Année pas finie (ce n'est pas un trou au milieu) :",
            "",
            f"- {t['year']} : {t['n_present']} saisons présentes "
            f"(dernière {t['last_present']}), {t['n_missing']} encore absentes "
            f"({', '.join(t['missing_seasons'])}).",
            "- CPC : les toutes dernières valeurs RONI sont une estimation "
            "(elles peuvent bouger jusqu'à deux mois).",
            "",
        ]
    lines += [
        "## Saisons (valeur du seuil ±0,5 °C)",
        "",
        "Une saison = 3 mois qui se chevauchent (DJF, JFM, …).",
        "",
        "| Phase | Saisons |",
        "|---|---:|",
        f"| El Niño (RONI > {WARM_GT}) | {val['el_nino']} |",
        f"| La Niña (RONI < {COLD_LT}) | {val['la_nina']} |",
        f"| Neutre | {val['neutre']} |",
        f"| Total | {inv['coverage']['n_seasons']} |",
        "",
        "## Saisons dans un épisode officiel (5 saisons d'affilée)",
        "",
        "| Lecture | Saisons |",
        "|---|---:|",
        f"| Dans un El Niño colorié | {epc['el_nino']} |",
        f"| Dans une La Niña coloriée | {epc['la_nina']} |",
        f"| Hors épisode (neutre ou run trop court) | {epc['hors_episode']} |",
        "",
        f"Épisodes El Niño : {inv['n_el_nino_episodes']}. "
        f"Épisodes La Niña : {inv['n_la_nina_episodes']}.",
        "",
        "## Années civiles (le fichier étiquette la saison, pas l'année)",
        "",
        "Une année peut avoir les deux. On ne force pas une seule case.",
        "",
        "| Lecture | Années |",
        "|---|---:|",
        f"| Au moins une saison El Niño | {yv['n_years_with_el_nino_season']} |",
        f"| Au moins une saison La Niña | {yv['n_years_with_la_nina_season']} |",
        f"| Les deux dans la même année | {yv['n_years_with_both']} |",
        f"| Seulement neutre | {yv['n_years_neutre_only']} |",
        f"| Année incomplète | {yv['n_years_incomplete']} |",
        "",
        "Années avec les deux : "
        + (", ".join(str(y) for y in yv["years_with_both"]) or "aucune")
        + ".",
        "",
        "Années seulement neutre : "
        + (", ".join(str(y) for y in yv["years_neutre_only"]) or "aucune")
        + ".",
        "",
        "## Épisodes officiels (5 saisons ou plus)",
        "",
        "| # | Phase | Début | Fin | Saisons | Pic RONI | Ouvert à la fin |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for e in inv["episodes"]:
        lines.append(
            f"| {e['episode_id']} | {PHASE_FR[e['phase']]} | {e['start_label']} | "
            f"{e['end_label']} | {e['n_seasons']} | {_fr_anom(e['peak_anom'])} | "
            f"{'oui' if e['open_at_end'] else 'non'} |"
        )
    lines += [
        "",
        f"Runs au-dessus du seuil mais trop courts pour un épisode "
        f"(moins de {MIN_CONSECUTIVE_SEASONS} saisons) :",
        "",
    ]
    shorts = inv["short_runs_below_5"]["el_nino"] + inv["short_runs_below_5"]["la_nina"]
    if shorts:
        lines += [
            "| Phase | Début | Fin | Saisons |",
            "|---|---|---|---:|",
        ]
        for s in shorts:
            lines.append(
                f"| {PHASE_FR[s['phase']]} | {s['start_label']} | "
                f"{s['end_label']} | {s['n_seasons']} |"
            )
        lines.append("")
    else:
        lines += ["Aucun.", ""]
    lines += [
        "## Table année par année",
        "",
        "| Année | Saisons dans le fichier | El Niño | La Niña | Neutre | Mélange |",
        "|---|---:|---:|---:|---:|---|",
    ]
    mix_fr = {
        "el_nino": "El Niño",
        "la_nina": "La Niña",
        "el_nino_et_la_nina": "les deux",
        "neutre": "neutre",
    }
    for y in inv["years"]:
        lines.append(
            f"| {y['year']} | {y['n_seasons_in_file']} | {y['n_el_nino_seasons']} | "
            f"{y['n_la_nina_seasons']} | {y['n_neutre_seasons']} | "
            f"{mix_fr[y['value_mix']]} |"
        )
    lines += [
        "",
        "## Mois de chaque saison CPC",
        "",
        "| Saison | Mois |",
        "|---|---|",
    ]
    for seas, months in SEASON_MONTHS.items():
        lines.append(f"| {seas} | {' '.join(months)} |")
    lines += [
        "",
        "DJF d'une année Y contient décembre de l'année Y-1. "
        "NDJ d'une année Y contient janvier de l'année Y+1. "
        "C'est la convention CPC, pas une année inventée.",
        "",
        "Champion Kalshi inchangé. Pas de trading réel. Pas SEAS5. Pas C3S.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--url", default=RONI_ASCII_URL)
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "enso"))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "RONI.ascii.txt"

    if args.skip_fetch:
        if not raw_path.exists():
            raise SystemExit(f"manque {raw_path} ; relancer sans --skip-fetch")
        text = raw_path.read_text(encoding="utf-8")
        fetched = False
    else:
        print(f"Télécharge {args.url}", flush=True)
        text = fetch_roni(args.url)
        raw_path.write_text(text, encoding="utf-8")
        fetched = True

    rows = parse_roni_ascii(text)
    inv = inventory(rows)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "schema": "regime_enso_roni/1",
        "generated_at": generated_at,
        "fetched": fetched,
        "catalogue_name": "Régime ENSO",
        "verdict": "testée, ça aide",
        "verdict_note": (
            "Inventaire officiel mesuré. Utile mutuelle / Phase 2. "
            "Pas pour Kalshi J+1. Pas de score de prévision."
        ),
        "champion_switched": False,
        "kalshi_temperature_scored": False,
        "seasonal_forecast_scored": False,
        **{k: v for k, v in inv.items() if k != "seasons"},
        "n_seasons_listed_in_ascii": inv["coverage"]["n_seasons"],
    }
    (out_dir / "enso_inventory.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    write_md(out_dir / "enso_report.md", inv, generated_at)
    cov = inv["coverage"]
    val = inv["seasons_by_value"]
    print(
        f"Saisons {cov['first']} → {cov['last']} : {cov['n_seasons']} "
        f"(El Niño {val['el_nino']}, La Niña {val['la_nina']}, "
        f"neutre {val['neutre']}), trous={cov['n_holes']}"
    )
    print(f"Écrit : {out_dir / 'enso_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
