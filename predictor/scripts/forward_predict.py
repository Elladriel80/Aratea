"""Capture quotidienne des predictions des trois predictors sur le panel Kalshi du jour.

A lancer chaque jour idealement vers 14:00 UTC (apres mise a jour des forecasts AM
et avant le close des markets J+1). Stocke les predictions horodatees pour pouvoir
les scorer plus tard contre les resolutions NWS.

Usage:
    python scripts/forward_predict.py
    python scripts/forward_predict.py --predictors climatology,ensemble
    python scripts/forward_predict.py --series KXHIGHAUS,KXLOWTSEA
    python scripts/forward_predict.py --time-budget-seconds 1560

Sortie : data/predictions/forward_<TIMESTAMP>.json

Resilience timeout (fix 2026-06-17) : ecriture INCREMENTALE du JSON (flush
periodique) + BUDGET TEMPS logiciel optionnel. Au-dela du budget, arret propre
avec ecriture de tout le carburant deja calcule (champ "partial": true) au lieu
de tout perdre quand le subprocess parent (daily_run.py) tue le process au
timeout dur. C'est ce qui a gele le dashboard du 9 au 16 juin 2026 :
forward_predict n'ecrivait son JSON qu'a la toute fin -> SIGKILL = 100 % perdu.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.config import MARKETS_DIR, DATA_DIR  # noqa: E402
from src.kalshi.models import Event  # noqa: E402
from src.predictors.parsers import parse_market  # noqa: E402
from src.predictors.climatology import ClimatologyPredictor  # noqa: E402
from src.predictors.forecast_blend import ForecastBlendPredictor  # noqa: E402
from src.predictors.ensemble import EnsemblePredictor  # noqa: E402
from src.weather import OpenMeteoClient  # noqa: E402


PREDICTOR_FACTORIES = {
    "climatology": lambda w: ClimatologyPredictor(w),
    "forecast_blend": lambda w: ForecastBlendPredictor(w),
    "ensemble": lambda w: EnsemblePredictor(w),
}


def _slim_inputs(inputs: dict) -> dict:
    """Retire les inputs trop verbeux pour ne pas bloater le JSON."""
    drop_keys = {"climato_years_used"}
    return {k: v for k, v in inputs.items() if k not in drop_keys}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictors", default="climatology,forecast_blend,ensemble",
                        help="Liste de predictors (virgule-separee)")
    parser.add_argument("--series", default="",
                        help="Filtre par prefixes serie (vide = tous les snapshots dispo)")
    parser.add_argument("--time-budget-seconds", type=int,
                        default=int(os.environ.get("FORWARD_TIME_BUDGET_S", "0")),
                        help="Budget temps logiciel : au-dela, arret propre avec "
                             "ecriture du carburant deja calcule (0 = illimite, defaut "
                             "manuel). En CI, daily_run.py passe une valeur < au kill "
                             "dur du subprocess pour ne JAMAIS perdre le carburant.")
    parser.add_argument("--checkpoint-every", type=int, default=5,
                        help="Flush du JSON sur disque tous les N snapshots traites "
                             "(filet anti-SIGKILL : on ne perd au pire que les "
                             "snapshots depuis le dernier flush).")
    args = parser.parse_args()

    predictor_names = [p.strip() for p in args.predictors.split(",") if p.strip()]
    unknown = [p for p in predictor_names if p not in PREDICTOR_FACTORIES]
    if unknown:
        print(f"Predictors inconnus : {unknown}")
        return 1

    series_filter = [s.strip() for s in args.series.split(",") if s.strip()]

    weather = OpenMeteoClient()
    predictors = {name: PREDICTOR_FACTORIES[name](weather) for name in predictor_names}

    snapshots = sorted(p for p in MARKETS_DIR.glob("*.json") if not p.name.startswith("_"))
    if series_filter:
        snapshots = [p for p in snapshots
                     if any(p.name.startswith(s) for s in series_filter)]

    if not snapshots:
        print("Pas de snapshots dans data/markets/. Lance scripts/fetch_markets.py d'abord.")
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    budget_s = max(0, args.time_budget_seconds)
    print(f"Forward-prediction snapshot @ {timestamp}")
    print(f"  predictors : {predictor_names}")
    print(f"  events     : {len(snapshots)}")
    print(f"  budget     : {budget_s}s" if budget_s else "  budget     : illimite")
    print()

    out_dir = DATA_DIR / "predictions"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"forward_{timestamp}.json"

    def flush(records, partial, done, total):
        # Ecriture ATOMIQUE (.tmp + os.replace) : a tout instant le fichier sur
        # disque est un JSON valide avec tout ce qui a deja ete calcule.
        tmp = out_path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps({
                "snapshot_at": timestamp,
                "predictors": predictor_names,
                "n_records": len(records),
                "partial": partial,
                "snapshots_done": done,
                "snapshots_total": total,
                "records": records,
            }, indent=2, default=str),
            encoding="utf-8",
        )
        os.replace(tmp, out_path)

    start = time.monotonic()
    total = len(snapshots)
    records = []
    partial = False
    done = 0
    for path in snapshots:
        # Garde-fou budget : arret PROPRE entre deux snapshots, avant le kill dur.
        if budget_s and (time.monotonic() - start) > budget_s:
            partial = True
            print(f"\n[BUDGET] Limite de {budget_s}s atteinte apres {done}/{total} "
                  f"snapshots -- arret propre, on ecrit le carburant deja produit.")
            break
        ev = Event.from_api(json.loads(path.read_text(encoding="utf-8")))
        for m in ev.markets:
            spec = parse_market(m)
            if spec is None:
                continue
            row = {
                "ticker": m.ticker,
                "event_ticker": ev.event_ticker,
                "series_ticker": ev.series_ticker,
                "subtitle": m.subtitle,
                "target_date": spec.target_date.isoformat(),
                "variable": spec.variable,
                "location_key": spec.location_key,
                "lower": spec.lower,
                "upper": spec.upper,
                "yes_bid": m.yes_bid,
                "yes_ask": m.yes_ask,
                "yes_mid": m.implied_prob_yes,
                "snapshot_at": timestamp,
                "predictions": {},
            }
            for name, predictor in predictors.items():
                try:
                    pred = predictor.predict(spec)
                    row["predictions"][name] = {
                        "prob_yes": pred.prob_yes,
                        "method": pred.method,
                        "inputs": _slim_inputs(pred.inputs),
                    }
                except Exception as e:
                    row["predictions"][name] = {"error": f"{type(e).__name__}: {e}"}
            records.append(row)
            mid_str = f"{m.implied_prob_yes:.2f}" if m.implied_prob_yes is not None else "-"
            preds_str = "  ".join(
                f"{n}={row['predictions'][n].get('prob_yes', '-'):.2f}"
                if isinstance(row["predictions"][n].get("prob_yes"), (int, float))
                else f"{n}=err"
                for n in predictor_names
            )
            print(f"  {m.ticker:<35} mid={mid_str:>5} {preds_str}")

        done += 1
        # Filet anti-SIGKILL : flush periodique.
        if args.checkpoint_every and done % args.checkpoint_every == 0:
            flush(records, True, done, total)

    flush(records, partial, done, total)

    rel = out_path.relative_to(DATA_DIR.parent)
    if partial:
        print(f"\n-> Predictions PARTIELLES stockees dans {rel} "
              f"({len(records)} records, {done}/{total} snapshots).")
        # Rend l'echec partiel VISIBLE dans l'UI Actions (fini le faux "success").
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print(f"::warning title=forward_predict partiel::"
                  f"{done}/{total} snapshots avant le budget temps ({budget_s}s). "
                  f"Carburant ecrit, mais incomplet.")
    else:
        print(f"\n-> Predictions stockees dans {rel} ({len(records)} records).")
    print("  Une fois les markets resolus, lance score_forward.py pour les evaluer.")
    # Arret sur budget = SUCCES (carburant valide ecrit) -> on retourne 0.
    return 0


if __name__ == "__main__":
    sys.exit(main())
