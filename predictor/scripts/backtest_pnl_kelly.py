"""backtest_pnl_kelly.py — Simulation PnL & Kelly fractionnel sur runs résolus.

Lit tous les runs/*/report.json déjà résolus (outcome yes/no) pour lesquels
on dispose du champion (p_champion) ET du prix de marché (p_kalshi_mid), puis
simule des paris Kelly fractionnels et calcule le PnL cumulé.

Hypothèses:
  - Bankroll virtuelle fixe (bankroll_usd, défaut 1000 $).
  - Quart Kelly (kelly_fraction 0.25), cap 5 % par pari (max_fraction_per_bet).
  - Payoff Kalshi binaire:
      - BET YES à prix px : +stake*(1-px)/px si YES, -stake si NO.
      - BET NO  à prix (1-px) : +stake*px/(1-px) si NO, -stake si YES.
  - Pas de réinvestissement (bankroll restant constant à bankroll_usd).
  - Un pari par run (pas de corrélation inter-marchés ici).
  - On ne parie que si l'edge théorique produit stake > 0.

Usage:
    python scripts/backtest_pnl_kelly.py
    python scripts/backtest_pnl_kelly.py --bankroll 500 --kelly-fraction 0.1
    python scripts/backtest_pnl_kelly.py --out results/pnl_kelly.json
    python scripts/backtest_pnl_kelly.py --min-edge 0.02
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

RUNS_DIR = ROOT / "runs"

_MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

CHAMPION_KEYS = ("vendor_ensemble", "learned_v3", "ensemble")


def target_date_from_ticker(ticker: str) -> str | None:
    m = re.search(r"-(\d{2})([A-Z]{3})(\d{2})", ticker or "")
    if not m:
        return None
    yy, mon, dd = m.group(1), m.group(2), m.group(3)
    if mon not in _MONTHS:
        return None
    return f"20{yy}-{_MONTHS[mon]:02d}-{int(dd):02d}"


def load_resolved_rows() -> list[dict]:
    rows: dict[str, dict] = {}
    for f in sorted(RUNS_DIR.glob("*/report.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("type") not in (None, "live", "pipeline"):
            continue
        scoring = d.get("scoring") or {}
        outcome = scoring.get("outcome")
        if outcome not in ("yes", "no"):
            continue
        by_model = scoring.get("by_model") or {}
        p_champ: float | None = None
        for key in CHAMPION_KEYS:
            rec = by_model.get(key)
            if isinstance(rec, dict) and rec.get("p_yes") is not None:
                p_champ = float(rec["p_yes"])
                break
        mid_rec = by_model.get("kalshi_mid_baseline")
        if mid_rec is None or p_champ is None:
            continue
        p_mid = mid_rec.get("p_yes")
        if p_mid is None:
            continue
        event = d.get("event") or {}
        ticker = (
            event.get("target_market_ticker")
            or event.get("ticker")
            or d.get("run_id", "")
        )
        target_date = target_date_from_ticker(ticker)
        ts = d.get("ts_utc") or ""
        # De-dup par ticker : on garde la prédiction la plus ancienne (no look-ahead)
        if ticker not in rows or ts < rows[ticker]["ts_utc"]:
            rows[ticker] = {
                "run_id": d.get("run_id"),
                "ticker": ticker,
                "target_date": target_date,
                "ts_utc": ts,
                "y": 1 if outcome == "yes" else 0,
                "p_champion": p_champ,
                "p_kalshi_mid": float(p_mid),
            }
    return sorted(rows.values(), key=lambda r: (r.get("target_date") or "", r["ts_utc"]))


def simulate_bet(
    row: dict,
    *,
    bankroll: float,
    kelly_fraction: float,
    max_fraction_per_bet: float,
    min_edge: float,
) -> dict | None:
    p = row["p_champion"]
    px = max(1e-4, min(1 - 1e-4, row["p_kalshi_mid"]))
    y = row["y"]

    if p > px:
        side = "YES"
        edge = p - px
        f_k = max(0.0, edge / (1.0 - px))
    else:
        side = "NO"
        p_no = 1.0 - p
        px_no = 1.0 - px
        edge = p_no - px_no
        f_k = max(0.0, edge / (1.0 - px_no))

    if edge < min_edge:
        return None

    f = min(f_k * kelly_fraction, max_fraction_per_bet)
    stake = round(f * bankroll, 2)
    if stake <= 0.0:
        return None

    # Payoff Kalshi binaire
    if side == "YES":
        pnl = round(stake * (1.0 - px) / px, 4) if y == 1 else -stake
        won = y == 1
    else:
        pnl = round(stake * px / (1.0 - px), 4) if y == 0 else -stake
        won = y == 0

    return {
        "run_id": row["run_id"],
        "ticker": row["ticker"],
        "target_date": row["target_date"],
        "p_champion": round(p, 4),
        "p_kalshi_mid": round(px, 4),
        "edge": round(edge, 4),
        "side": side,
        "kelly_full": round(f_k, 4),
        "kelly_used": round(f, 4),
        "stake_usd": stake,
        "pnl_usd": pnl,
        "won": won,
        "y": y,
    }


def aggregate(bets: list[dict], bankroll: float) -> dict:
    n = len(bets)
    if n == 0:
        return {"n_bets": 0}
    total_pnl = sum(b["pnl_usd"] for b in bets)
    wins = sum(1 for b in bets if b["won"])
    total_staked = sum(b["stake_usd"] for b in bets)
    roi = (total_pnl / total_staked * 100) if total_staked > 0 else 0.0

    # Cumul par date
    cumul: dict[str, float] = {}
    running = 0.0
    for b in sorted(bets, key=lambda x: x.get("target_date") or ""):
        d = b["target_date"] or "unknown"
        running += b["pnl_usd"]
        cumul[d] = round(running, 2)

    # Sharpe simplifié (par pari)
    pnls = [b["pnl_usd"] for b in bets]
    mean = sum(pnls) / n
    std = math.sqrt(sum((x - mean) ** 2 for x in pnls) / n) if n > 1 else 0.0
    sharpe = mean / std if std > 0 else None

    # Répartition par côté
    yes_bets = [b for b in bets if b["side"] == "YES"]
    no_bets = [b for b in bets if b["side"] == "NO"]

    distinct_dates = len({b["target_date"] for b in bets if b["target_date"]})
    edges = [b["edge"] for b in bets]
    median_edge = sorted(edges)[n // 2]

    return {
        "n_bets": n,
        "n_distinct_target_dates": distinct_dates,
        "win_rate": round(wins / n, 4),
        "total_pnl_usd": round(total_pnl, 2),
        "total_staked_usd": round(total_staked, 2),
        "roi_pct": round(roi, 2),
        "roi_on_bankroll_pct": round(total_pnl / bankroll * 100, 2),
        "sharpe_per_bet": round(sharpe, 4) if sharpe is not None else None,
        "mean_edge": round(sum(edges) / n, 4),
        "median_edge": round(median_edge, 4),
        "by_side": {
            "YES": {"n": len(yes_bets), "pnl": round(sum(b["pnl_usd"] for b in yes_bets), 2), "wins": sum(1 for b in yes_bets if b["won"])},
            "NO": {"n": len(no_bets), "pnl": round(sum(b["pnl_usd"] for b in no_bets), 2), "wins": sum(1 for b in no_bets if b["won"])},
        },
        "cumulative_pnl_by_date": cumul,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Simulation PnL Kelly sur runs résolus")
    ap.add_argument("--bankroll", type=float, default=1000.0, help="Bankroll virtuelle en USD (défaut 1000)")
    ap.add_argument("--kelly-fraction", type=float, default=0.25, help="Fraction du Kelly (défaut 0.25 = quart)")
    ap.add_argument("--max-fraction-per-bet", type=float, default=0.05, help="Cap par pari (fraction de bankroll, défaut 0.05)")
    ap.add_argument("--min-edge", type=float, default=0.0, help="Edge minimum pour parier (défaut 0 = tout)")
    ap.add_argument("--out", type=str, default=None, help="Chemin JSON de sortie")
    args = ap.parse_args()

    rows = load_resolved_rows()
    print(f"Runs résolus avec champion+marché: {len(rows)}", file=sys.stderr)

    bets: list[dict] = []
    skipped = 0
    for row in rows:
        b = simulate_bet(
            row,
            bankroll=args.bankroll,
            kelly_fraction=args.kelly_fraction,
            max_fraction_per_bet=args.max_fraction_per_bet,
            min_edge=args.min_edge,
        )
        if b is None:
            skipped += 1
        else:
            bets.append(b)

    print(f"Paris simulés: {len(bets)}, skippés (edge nul): {skipped}", file=sys.stderr)

    stats = aggregate(bets, args.bankroll)

    result = {
        "params": {
            "bankroll_usd": args.bankroll,
            "kelly_fraction": args.kelly_fraction,
            "max_fraction_per_bet": args.max_fraction_per_bet,
            "min_edge": args.min_edge,
        },
        "summary": stats,
        "bets": bets,
    }

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Résultat écrit dans {args.out}", file=sys.stderr)
    else:
        # Afficher le résumé (pas les 267 paris)
        print(json.dumps({"params": result["params"], "summary": stats}, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
