"""Agrège les résultats backtest climato pour KXHIGHTSFO et calcule BSS.

À lancer APRÈS :
  python predictor/scripts/backtest.py --series KXHIGHTSFO --limit 200

Lit runs_backtest/<dates>/<seq>/report.json filtrés sur series=KXHIGHTSFO,
calcule :
  - N (taille effective)
  - Brier moyen modèle (climato)
  - Brier baseline "constante" = base rate observé (= mean outcome)
  - BSS = 1 - Brier_modele / Brier_baseline
  - Top-1 accuracy (winning bin coverage)

Usage:
  python predictor/scripts/_aggregate_sfo_high.py
  python predictor/scripts/_aggregate_sfo_high.py --series KXHIGHTSFO
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict
from statistics import mean

ROOT = Path(__file__).resolve().parent.parent
RUNS_BT = ROOT / "runs_backtest"


def collect(series_filter: str):
    # Dédup par market_ticker : un replay (re-lancement du backtest) ré-émet le
    # même ticker dans un nouveau report.json. Sans dédup, chaque marché serait
    # compté plusieurs fois et gonflerait N/Brier/BSS (revue 2026-06-10 A1, gate
    # Phase B `edge_confirmed`). On garde le replay le plus récent (ts_replay_utc
    # max, comparable lexicographiquement car format %Y-%m-%dT%H:%M:%SZ).
    by_ticker: dict[str, dict] = {}
    if not RUNS_BT.exists():
        print(f"!! {RUNS_BT} n'existe pas — lance d'abord le backtest.")
        return []
    for day_dir in sorted(RUNS_BT.iterdir()):
        if not day_dir.is_dir():
            continue
        for run_dir in sorted(day_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            rep = run_dir / "report.json"
            if not rep.exists():
                continue
            try:
                data = json.loads(rep.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"!! {rep}: parse error {e}")
                continue
            ev = data.get("event", {})
            if ev.get("series") != series_filter:
                continue
            mkts = data.get("markets") or []
            if not mkts:
                continue
            m = mkts[0]
            res = m.get("resolution", {})
            preds = m.get("predictions_by_model") or {}
            # Le modèle climato est nommé "climatology"
            p = preds.get("climatology")
            if p is None:
                # fallback : premier modèle dispo
                if preds:
                    p = next(iter(preds.values()))
            if p is None:
                continue
            outcome = res.get("outcome_int")
            if outcome is None:
                continue
            ticker = m.get("ticker")
            ts_replay = data.get("ts_replay_utc") or ""
            row = {
                "as_of": data.get("as_of_date"),
                "target": data.get("target_date"),
                "ticker": ticker,
                "p_model": float(p),
                "outcome": int(outcome),
                "event_ticker": ev.get("ticker"),
                "ts_replay": ts_replay,
            }
            # Clé de dédup = ticker ; si absent (ne devrait pas arriver), clé
            # unique par chemin pour ne pas fusionner des marchés distincts.
            key = ticker if ticker else f"__norow_{len(by_ticker)}__"
            prev = by_ticker.get(key)
            if prev is None or ts_replay >= prev["ts_replay"]:
                by_ticker[key] = row
    return list(by_ticker.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="KXHIGHTSFO")
    ap.add_argument("--json", action="store_true",
                    help="Émet uniquement un blob JSON sur stdout (mode CI/cron).")
    ap.add_argument("--bss-gate", type=float, default=0.05,
                    help="Seuil BSS de l'edge gate (défaut 0.05, white paper §7.7).")
    ap.add_argument("--n-gate", type=int, default=200,
                    help="Seuil N de robustesse (défaut 200).")
    args = ap.parse_args()

    rows = collect(args.series)
    if not rows:
        if args.json:
            print(json.dumps({
                "series": args.series, "N": 0, "verdict": "NO_DATA",
                "bss": None, "edge_confirmed": False,
            }))
        else:
            print(f"!! Aucune ligne pour series={args.series}.")
        return 1

    N = len(rows)
    base_rate = mean(r["outcome"] for r in rows)
    brier_model = mean((r["p_model"] - r["outcome"]) ** 2 for r in rows)
    brier_baseline_const = mean((base_rate - r["outcome"]) ** 2 for r in rows)
    bss = (1.0 - brier_model / brier_baseline_const) if brier_baseline_const > 0 else None

    # Top-1 par event (le winning bin a outcome=1 ; on regarde si le modèle
    # met la plus grande p sur la bonne ligne, événement par événement)
    by_event = defaultdict(list)
    for r in rows:
        by_event[r["event_ticker"]].append(r)
    n_events = len(by_event)
    n_top1 = 0
    n_events_with_winner = 0
    for ev, lst in by_event.items():
        has_winner = any(r["outcome"] == 1 for r in lst)
        if not has_winner:
            continue
        n_events_with_winner += 1
        best = max(lst, key=lambda r: r["p_model"])
        if best["outcome"] == 1:
            n_top1 += 1
    top1_acc = (n_top1 / n_events_with_winner) if n_events_with_winner else None

    if not args.json:
        print("=" * 60)
        print(f"Backtest climatologie — series={args.series}")
        print("=" * 60)
        print(f"N (markets-jours)         : {N}")
        print(f"Events distincts          : {n_events}")
        print(f"Events avec winner        : {n_events_with_winner}")
        print(f"Base rate observé (1)     : {base_rate:.4f}")
        print(f"Brier modèle (climato)    : {brier_model:.4f}")
        print(f"Brier baseline constante  : {brier_baseline_const:.4f}")
        if bss is not None:
            sign = "+" if bss >= 0 else ""
            print(f"BSS                       : {sign}{bss:.4f}   {'<-- POSITIF' if bss > 0 else ''}")
        if top1_acc is not None:
            print(f"Top-1 accuracy par event  : {top1_acc:.3f}  ({n_top1}/{n_events_with_winner})")
        print()
        print(f"Échantillon (5 premières lignes) :")
        for r in rows[:5]:
            print(f"  {r['as_of']} -> {r['target']}  p={r['p_model']:.3f}  y={r['outcome']}  {r['ticker']}")

    # Verdict
    if bss is None:
        verdict = "INDETERMINATE"
        verdict_msg = "Verdict : indéterminable (baseline=0)."
        edge_confirmed = False
    elif bss > args.bss_gate and N >= args.n_gate:
        verdict = "EDGE_CONFIRMED"
        verdict_msg = f"Verdict : ✅ EDGE CONFIRMÉ (BSS={bss:+.3f} sur N={N} >= {args.n_gate})."
        edge_confirmed = True
    elif bss > args.bss_gate and N < args.n_gate:
        verdict = "POSITIVE_UNDERSIZED"
        verdict_msg = f"Verdict : 🟡 Signal positif (BSS={bss:+.3f}) mais N={N} < {args.n_gate} — étendre la fenêtre."
        edge_confirmed = False
    elif 0 < bss <= args.bss_gate:
        verdict = "BSS_MARGINAL"
        verdict_msg = f"Verdict : 🟠 BSS marginal (+{bss:.3f}) — pas exploitable seul."
        edge_confirmed = False
    else:
        verdict = "NO_EDGE"
        verdict_msg = f"Verdict : ❌ BSS non positif ({bss:+.3f}) — pas d'edge sur cette série."
        edge_confirmed = False

    if args.json:
        # Mode CI/cron : JSON unique sur stdout, exit 0 ssi edge confirmé.
        print(json.dumps({
            "series": args.series,
            "N": N,
            "n_events": n_events,
            "n_events_with_winner": n_events_with_winner,
            "base_rate": round(base_rate, 4),
            "brier_model": round(brier_model, 4),
            "brier_baseline_const": round(brier_baseline_const, 4),
            "bss": round(bss, 4) if bss is not None else None,
            "top1_acc": round(top1_acc, 3) if top1_acc is not None else None,
            "verdict": verdict,
            "edge_confirmed": edge_confirmed,
            "n_gate": args.n_gate,
            "bss_gate": args.bss_gate,
        }))
    else:
        print()
        print(verdict_msg)

    # Exit 0 ssi edge confirmé : facilite l'enrobage cron/CI ("si exit 0 alors poster Discord").
    return 0 if edge_confirmed else 2


if __name__ == "__main__":
    sys.exit(main() or 0)
