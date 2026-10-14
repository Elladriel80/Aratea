"""eval_c3s_ab.py : trois A/B C3S multi-modèle vs climato, hors ligne.

FR : Note le mélange C3S contre la climato, sur USDM / SPEI-6 / CHIRPS,
seulement si le PM a déposé un CSV. ECMWF-51 est noté seul pour voir
si le mélange le bat. Jamais CDS. Jamais de clé. Jamais de score
inventé. Un centre absent reste un trou. Le champion Kalshi n'est
pas touché.

Usage:
    python scripts/eval_c3s_ab.py
    python scripts/eval_c3s_ab.py --forecast-csv /chemin/c3s_tp_monthly.csv
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

if "cdsapi" in sys.modules:  # pragma: no cover
    raise RuntimeError("cdsapi ne doit pas être importé")

from src.forecast.c3s_offline import (  # noqa: E402
    C3S_DIR, C3S_OUT, FORECAST_NAME, LOCAL_FORECAST_CSV, SHARED_FORECAST_CSV,
)
from src.forecast.seas5_offline import DOWNLOAD_ENVELOPES  # noqa: E402
from src.score.c3s_ab import (  # noqa: E402
    BSS_GATE, MIN_SEASONS_FOR_GATE, score_all,
)
from src.score.seas5_ab import AB_SPECS  # noqa: E402


def _rel(path: Optional[Path]) -> Optional[str]:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _fmt(value: Any) -> str:
    if value is None:
        return "n/d"
    return str(value)


def _strip_seasons(block: dict[str, Any]) -> None:
    for row in (block.get("by_region") or {}).values():
        row.pop("seasons", None)


def _notes(payload: dict[str, Any]) -> list[str]:
    notes = []
    status = payload["forecast"]
    if not status.get("present"):
        notes.append("CSV C3S absent. Mesure bloquée. Aucun BSS inventé.")
    else:
        missing = (status.get("inventory") or {}).get("missing_centres") or []
        if missing:
            labels = ", ".join(item["label"] for item in missing)
            notes.append(
                f"Centres absents (trous non comblés) : {labels}."
            )
    notes.append(
        "Headline C = CHIRPS MED seulement. India à part. Pas de C poolé."
    )
    notes.append(
        "SPEI-6 publié (PR 246) : Brier climato 0 au seuil ≤ -1,5 "
        "après moyenne spatiale. Pas de BSS SPEI inventé."
    )
    notes.append(
        "ECMWF-51 n'est recalculé que si ses lignes sont dans le CSV C3S. "
        "La mesure PR 246 n'est pas recopiée dans les BSS de ce run."
    )
    notes.append("Champion Kalshi inchangé. Pas d'appel CDS.")
    return notes


def write_report(path: Path, payload: dict[str, Any]) -> None:
    status = payload["forecast"]
    lines = [
        f"# {FORECAST_NAME} : A/B hors ligne",
        "",
        f"Prévision : {FORECAST_NAME}.",
        "Trois A/B séparés contre la climato. Aucun chiffre inventé.",
        "Champion Kalshi inchangé. CDS non appelé.",
        "Moyenne équipondérée par centre. Un trou n'est pas comblé.",
        "",
        "## Entrée",
        "",
        f"CSV PM (prioritaire) : `{SHARED_FORECAST_CSV}`.",
        f"Copie locale : `{LOCAL_FORECAST_CSV}`.",
        f"CSV lu : {status.get('csv_path') or 'absent'}.",
        "Fenêtre hindcast attendue en premier : 1993-2016.",
        (
            "Cellules du mélange : "
            f"{(status.get('inventory') or {}).get('n_cells', 0)}. "
            "Dont un centre manque : "
            f"{(status.get('inventory') or {}).get('n_cells_with_hole', 0)}."
        ),
    ]
    if status.get("reason"):
        lines += ["", status["reason"]]
    lines += [
        "",
        f"Gate : {MIN_SEASONS_FOR_GATE} saisons et BSS > {BSS_GATE}.",
        "",
        "## Centres",
        "",
        "| Centre | Système | Lignes | Statut |",
        "|---|---:|---:|---|",
    ]
    inventory = status.get("inventory") or {}
    expected = inventory.get("expected_centres") or status.get("expected_centres") or []
    for item in expected:
        n_rows = item.get("n_rows", 0)
        state = "présent" if item.get("present") else "trou"
        lines.append(
            f"| {item.get('label', item.get('origin'))} | {item.get('system')} | "
            f"{n_rows} | {state} |"
        )
    lines += [
        "",
        "## Les trois A/B du mélange (par région, jamais poolé)",
        "",
        "Headline C = MED seulement. On ne mélange pas MED et India.",
        "",
        "| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    _append_ab_rows(lines, payload["ab"])
    lines += [
        "",
        "## ECMWF-51 seul (SEAS5, lignes de ce CSV seulement)",
        "",
        "Si le centre manque, la ligne reste bloquée. On ne remplit pas.",
        "",
        "| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    _append_ab_rows(lines, payload["ecmwf51"]["ab"])
    comp = payload["comparison"]
    beats = comp.get("mix_beats_ecmwf51")
    if beats is True:
        beats_txt = "le mélange bat ECMWF-51"
    elif beats is False:
        beats_txt = "le mélange ne bat pas ECMWF-51"
    else:
        beats_txt = "comparaison bloquée (BSS manquant)"
    lines += [
        "",
        "## Comparaison headline (CHIRPS MED seulement)",
        "",
        f"N mélange : {comp.get('multi_n', 0)}. "
        f"BSS mélange : {_fmt(comp.get('multi_bss'))}.",
        f"N ECMWF-51 : {comp.get('ecmwf51_n', 0)}. "
        f"BSS ECMWF-51 : {_fmt(comp.get('ecmwf51_bss'))}.",
        f"Verdict : {beats_txt}.",
        "India n'entre pas dans cette ligne.",
        "",
        "## Baseline SEAS5 déjà mesurée (PR 246, pas un score de ce run)",
        "",
        "Ces chiffres viennent du commit aa8d61f. Ils ne sont pas recalculés.",
        "Le BSS SPEI reste n/d. On ne pool pas MED et India.",
        "",
        "| A/B | Région | N | BSS | Verdict |",
        "|---|---|---:|---:|---|",
    ]
    published = payload["published_seas5_baseline"]
    for key, spec in (
        ("A", {"midwest": "Midwest", "southwest": "Southwest"}),
        ("B", {"med": "MED", "india": "India", "us": "US"}),
        ("C", {"med": "MED (headline)", "india": "India"}),
    ):
        for region, label in spec.items():
            row = published[key][region]
            lines.append(
                f"| {key} | {label} | {row['n']} | {_fmt(row['bss'])} | "
                f"{row['verdict']} |"
            )
    lines += ["", "## Notes", ""]
    for note in _notes(payload):
        lines.append(f"- {note}")
    lines += [
        "",
        "## Boîtes de téléchargement PM (pas le masque de score)",
        "",
        "Le score utilise les polygones déjà publiés (PR 240 / 243 / 244).",
        "",
        "| Région | N | W | S | E | Masque de score |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for slug, spec in DOWNLOAD_ENVELOPES.items():
        n, w, s, e = spec["cds_area"]
        lines.append(
            f"| {spec['label']} (`{slug}`) | {n} | {w} | {s} | {e} | {spec['mask']} |"
        )
    lines += ["", "## Verdicts", ""]
    for name, status_v in payload["verdicts"].items():
        lines.append(f"- {name} : {status_v}")
    lines += [
        "",
        "La ligne SEAS5 du catalogue est la mesure PR 246, pas un recalcul.",
        "US Drought Monitor, SPEI et CHIRPS pluie sont les statuts déjà publiés des vérités.",
        "Le résultat de ce run est le tableau des trois A/B.",
        "",
        "Pas de clé API dans ce dépôt.",
        "Pas d'appel cdsapi.",
        "Pas de bascule du champion Kalshi.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _append_ab_rows(lines: list[str], ab: dict[str, Any]) -> None:
    for key in ("A", "B", "C"):
        block = ab[key]
        spec = AB_SPECS[key]
        headline = spec.get("headline_region")
        for region, label in spec["region_labels"].items():
            row = (block.get("by_region") or {}).get(region) or {}
            name = f"{label} (headline)" if headline == region else label
            lines.append(
                f"| {key} {spec['truth_name']} | {name} | "
                f"{row.get('n', 0)} | "
                f"{_fmt(row.get('brier_forecast'))} | "
                f"{_fmt(row.get('brier_climato'))} | "
                f"{_fmt(row.get('bss'))} | {row.get('verdict', 'bloquée')} |"
            )


def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    def arm(ab: dict[str, Any]) -> dict[str, Any]:
        return {
            k: {
                "verdict": ab[k]["verdict"],
                "n": ab[k]["n_seasons_scored"],
                "bss": ab[k]["bss"],
                "blocker": ab[k].get("blocker"),
            }
            for k in ("A", "B", "C")
        }

    comp = payload["comparison"]
    inventory = (payload["forecast"].get("inventory") or {})
    return {
        "forecast_name": payload["forecast_name"],
        "forecast_present": payload["forecast"]["present"],
        "cds_called": payload["cds_called"],
        "champion_switched": payload["champion_switched"],
        "bss_invented": payload["bss_invented"],
        "pooled": payload["pooled"],
        "filled_from_seas5": payload["filled_from_seas5"],
        "missing_centres": [
            item["label"] for item in inventory.get("missing_centres") or []
        ],
        "ab": arm(payload["ab"]),
        "ecmwf51": arm(payload["ecmwf51"]["ab"]),
        "comparison_chirps_med": {
            "multi_n": comp["multi_n"],
            "multi_bss": comp["multi_bss"],
            "ecmwf51_n": comp["ecmwf51_n"],
            "ecmwf51_bss": comp["ecmwf51_bss"],
            "mix_beats_ecmwf51": comp["mix_beats_ecmwf51"],
        },
        "verdicts": payload["verdicts"],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--forecast-csv", default="")
    p.add_argument("--forecast-dir", default=str(C3S_DIR))
    p.add_argument("--data-dir", default=str(ROOT / "data"))
    p.add_argument("--out-dir", default=str(C3S_OUT))
    p.add_argument("--init-month", type=int, default=0,
                   help="Mois d'init 1-12. 0 = tous.")
    p.add_argument("--min-lead", type=int, default=1)
    p.add_argument("--max-lead", type=int, default=7)
    p.add_argument("--no-shared", action="store_true")
    args = p.parse_args()

    forecast_dir = Path(args.forecast_dir)
    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    init_month = args.init_month if args.init_month else None
    explicit = Path(args.forecast_csv) if args.forecast_csv else None

    print(FORECAST_NAME, "hors ligne", flush=True)
    payload = score_all(
        data_dir=data_dir,
        forecast_dir=forecast_dir,
        forecast_csv=explicit,
        init_month=init_month,
        min_lead=args.min_lead,
        max_lead=args.max_lead,
        include_shared=not args.no_shared,
    )
    payload["as_of"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload["paths"] = {
        "forecast_dir": _rel(forecast_dir),
        "data_dir": _rel(data_dir),
        "out_dir": _rel(out_dir),
    }
    fc = payload.get("forecast") or {}
    if fc.get("directory"):
        fc["directory"] = _rel(Path(fc["directory"])) or fc["directory"]
    if fc.get("csv_path"):
        fc["csv_path"] = _rel(Path(fc["csv_path"])) or fc["csv_path"]
    if fc.get("searched"):
        fc["searched"] = [_rel(Path(item)) or str(item) for item in fc["searched"]]
    payload["forecast"] = fc
    for arm in (payload["ab"], payload["ecmwf51"]["ab"]):
        for key in ("A", "B", "C"):
            block = arm[key]
            _strip_seasons(block)
            if block.get("forecast_path"):
                block["forecast_path"] = _rel(Path(block["forecast_path"]))
            if block.get("truth_path"):
                block["truth_path"] = _rel(Path(block["truth_path"]))

    (out_dir / "c3s_ab_report.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    write_report(out_dir / "c3s_ab_report.md", payload)
    print(json.dumps(_summary(payload), indent=2, ensure_ascii=False), flush=True)
    if "cdsapi" in sys.modules:
        raise RuntimeError("cdsapi a été importé pendant le run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
