"""eval_seas5_ab.py : trois A/B SEAS5 vs climato, hors ligne.

FR : Note SEAS5 contre la climato, sur USDM / SPEI-6 / CHIRPS, seulement
si le PM a déposé un CSV. Jamais CDS. Jamais de clé. Jamais de score
inventé. Le champion Kalshi n'est pas touché.

Usage:
    python scripts/eval_seas5_ab.py
    python scripts/eval_seas5_ab.py --forecast-dir /chemin/seas5
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

if "cdsapi" in sys.modules:  # pragma: no cover
    raise RuntimeError("cdsapi ne doit pas être importé")

from src.forecast.seas5_offline import (  # noqa: E402
    DOWNLOAD_ENVELOPES, FORECAST_NAME, FORECAST_REQUIRED, PM_REGION_LABELS,
    SEAS5_DIR, SEAS5_OUT, SHARED_FORECAST_CSV,
)
from src.score.seas5_ab import (  # noqa: E402
    AB_SPECS, BSS_GATE, MIN_SEASONS_FOR_GATE, score_all,
)


def _rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    status = payload["forecast"]
    lines = [
        f"# {FORECAST_NAME} : A/B hors ligne",
        "",
        f"Prévision : {FORECAST_NAME}.",
        "Trois A/B séparés contre la climato. Aucun chiffre inventé.",
        "Champion Kalshi inchangé. CDS non appelé.",
        "",
        "## Entrée",
        "",
        f"CSV PM (prioritaire) : `{SHARED_FORECAST_CSV}`.",
        f"Dossier local : `{status.get('directory')}`.",
        f"CSV régional : {status.get('csv_path') or 'absent'}.",
        f"Labels PM : {', '.join(PM_REGION_LABELS)}.",
        f"Fichiers bruts : {status.get('raw_files') or 'aucun'}.",
    ]
    if status.get("reason"):
        lines += ["", status["reason"]]
    lines += [
        "",
        f"Gate : {MIN_SEASONS_FOR_GATE} saisons et BSS > {BSS_GATE}.",
        "",
        "## Les trois A/B (par région, jamais poolé)",
        "",
        "Headline C = MED seulement. On ne mélange pas MED et India.",
        "",
        "| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for key in ("A", "B", "C"):
        block = payload["ab"][key]
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
    seen_notes: list[str] = []
    for key in ("A", "B", "C"):
        note = payload["ab"][key].get("blocker")
        if note and note not in seen_notes:
            seen_notes.append(note)
    if seen_notes:
        lines += ["", "Notes :", ""]
        for note in seen_notes:
            lines.append(f"- {note}")
    lines += ["", "## Par région (N mesuré seulement)", ""]
    for key in ("A", "B", "C"):
        block = payload["ab"][key]
        spec = AB_SPECS[key]
        lines += [f"### {key}. {spec['title']}", ""]
        for region, label in spec["region_labels"].items():
            row = (block.get("by_region") or {}).get(region) or {}
            lines.append(
                f"- {label} (`{region}`) : n={row.get('n', 0)} "
                f"BSS {_fmt(row.get('bss'))} : {row.get('verdict', 'bloquée')}"
            )
        lines.append("")
    lines += [
        "## Boîtes de téléchargement PM (pas le masque de score)",
        "",
        "Le score utilise les polygones déjà publiés (PR 240 / 243 / 244).",
        "Ces rectangles CDS [N, W, S, E] servent seulement au téléchargement.",
        "",
        "| Région | N | W | S | E | Masque de score |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for slug, spec in DOWNLOAD_ENVELOPES.items():
        n, w, s, e = spec["cds_area"]
        lines.append(
            f"| {spec['label']} (`{slug}`) | {n} | {w} | {s} | {e} | {spec['mask']} |"
        )
    lines += [
        "",
        "## Verdicts (noms du catalogue, non renommés)",
        "",
    ]
    for name, status_v in payload["verdicts"].items():
        lines.append(f"- {name} : {status_v}")
    lines += [
        "",
        "Pas de clé API dans ce dépôt.",
        "Pas d'appel cdsapi.",
        "Pas de bascule du champion Kalshi.",
        "",
        "Schéma CSV : " + ",".join(FORECAST_REQUIRED) + ".",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return "n/d"
    return str(value)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--forecast-dir", default=str(SEAS5_DIR))
    p.add_argument("--data-dir", default=str(ROOT / "data"))
    p.add_argument("--out-dir", default=str(SEAS5_OUT))
    p.add_argument("--init-month", type=int, default=0,
                   help="Mois d'init 1-12. 0 = tous.")
    p.add_argument("--min-lead", type=int, default=1)
    p.add_argument("--max-lead", type=int, default=7)
    args = p.parse_args()

    forecast_dir = Path(args.forecast_dir)
    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    init_month = args.init_month if args.init_month else None

    print(FORECAST_NAME, "hors ligne", flush=True)
    payload = score_all(
        data_dir=data_dir,
        forecast_dir=forecast_dir,
        init_month=init_month,
        min_lead=args.min_lead,
        max_lead=args.max_lead,
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
        fc["searched"] = [_rel(Path(p)) or str(p) for p in fc["searched"]]
    pairs = fc.get("pairs") or {}
    fc["pairs"] = {
        k: (_rel(Path(v)) if v else None) for k, v in pairs.items()
    }
    payload["forecast"] = fc
    for key in ("A", "B", "C"):
        block = payload["ab"][key]
        if block.get("forecast_path"):
            block["forecast_path"] = _rel(Path(block["forecast_path"]))
        if block.get("truth_path"):
            block["truth_path"] = _rel(Path(block["truth_path"]))

    (out_dir / "seas5_ab_report.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    write_report(out_dir / "seas5_ab_report.md", payload)

    summary = {
        "forecast_present": payload["forecast"]["present"],
        "cds_called": payload["cds_called"],
        "champion_switched": payload["champion_switched"],
        "bss_invented": payload["bss_invented"],
        "ab": {
            k: {
                "verdict": payload["ab"][k]["verdict"],
                "n": payload["ab"][k]["n_seasons_scored"],
                "bss": payload["ab"][k]["bss"],
                "blocker": payload["ab"][k].get("blocker"),
            }
            for k in ("A", "B", "C")
        },
        "verdicts": payload["verdicts"],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
    if "cdsapi" in sys.modules:
        raise RuntimeError("cdsapi a été importé pendant le run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
