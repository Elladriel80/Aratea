"""backtest_champion_vs_market.py — recover the Phase-1 go/no-go signal from
the resolved paper runs.

Why this exists
---------------
The learned-model training set (data/predictions/forward_*.json) stopped
growing on 2026-05-11 because the daily CI ran only daily_auto.py (paper
capture) and not the learning capture (forward_predict + score_forward).
That gap is fixed forward in .github/workflows/daily-trading.yml.

The *feature-level* history (climatology / forecast_blend / vendor spread)
cannot be reconstructed — forecasts are forward-only and Open-Meteo keeps
no archive of past forecast runs. BUT every resolved paper run faithfully
stored, at capture time, the champion's actual P(YES) (vendor_ensemble),
the Kalshi mid, and the later settlement. That is a clean, no-look-ahead
sample we CAN evaluate: it answers the only question the Phase-1 go/no-go
cares about — does the champion beat the market?

This script reads predictor/runs/*/report.json, keeps the resolved ones,
de-duplicates by settled market, and scores vendor_ensemble vs
kalshi_mid on Brier over the full multi-date sample.

Usage:
    python predictor/scripts/backtest_champion_vs_market.py
    python predictor/scripts/backtest_champion_vs_market.py --out path.json
    python predictor/scripts/backtest_champion_vs_market.py --keep last
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "runs"

_MONTHS = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}


def target_date_from_ticker(ticker: str) -> str | None:
    """KXLOWTMIA-26JUN03-B77.5 -> 2026-06-03."""
    m = re.search(r"-(\d{2})([A-Z]{3})(\d{2})", ticker or "")
    if not m:
        return None
    yy, mon, dd = m.group(1), m.group(2), m.group(3)
    if mon not in _MONTHS:
        return None
    return f"20{yy}-{_MONTHS[mon]:02d}-{int(dd):02d}"


def _p_yes(by_model: dict, name: str) -> float | None:
    rec = by_model.get(name)
    if not isinstance(rec, dict):
        return None
    p = rec.get("p_yes")
    return float(p) if p is not None else None


def brier(p: float, y: int) -> float:
    return (p - y) ** 2


def binom_sign_test_p(wins: int, n: int) -> float:
    """One-sided P(X >= wins) under Binomial(n, 0.5). Tie-free comparisons only."""
    if n == 0:
        return 1.0
    # sum_{k=wins}^{n} C(n,k) * 0.5^n
    total = 0.0
    for k in range(wins, n + 1):
        total += math.comb(n, k)
    return total * (0.5 ** n)


def collect(keep: str = "first") -> list[dict]:
    """One row per unique settled market ticker.

    keep='first' keeps the earliest captured run for a market (the prediction
    made furthest from settlement — the honest forecasting test); keep='last'
    keeps the most recent.
    """
    rows: dict[str, dict] = {}
    for f in sorted(glob.glob(str(RUNS_DIR / "*" / "report.json"))):
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("type") not in (None, "live"):
            continue
        scoring = d.get("scoring") or {}
        outcome = scoring.get("outcome")
        if outcome not in ("yes", "no"):
            continue
        by_model = scoring.get("by_model") or {}
        p_champ = _p_yes(by_model, "vendor_ensemble")
        p_mid = _p_yes(by_model, "kalshi_mid_baseline")
        if p_champ is None or p_mid is None:
            continue
        event = d.get("event") or {}
        ticker = event.get("target_market_ticker") or event.get("ticker") or d.get("run_id")
        td = target_date_from_ticker(event.get("ticker") or ticker or "")
        ts = d.get("ts_utc") or ""
        row = {
            "run_id": d.get("run_id"),
            "ticker": ticker,
            "target_date": td,
            "ts_utc": ts,
            "y": 1 if outcome == "yes" else 0,
            "p_champion": p_champ,
            "p_kalshi_mid": p_mid,
        }
        key = ticker
        if key not in rows:
            rows[key] = row
        else:
            prev = rows[key]
            if keep == "last" and ts > (prev["ts_utc"] or ""):
                rows[key] = row
            elif keep == "first" and ts < (prev["ts_utc"] or ""):
                rows[key] = row
    return list(rows.values())


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {"n": 0}
    base_rate = sum(r["y"] for r in rows) / n
    b_champ = sum(brier(r["p_champion"], r["y"]) for r in rows) / n
    b_mid = sum(brier(r["p_kalshi_mid"], r["y"]) for r in rows) / n
    b_clim = sum(brier(base_rate, r["y"]) for r in rows) / n  # constant base-rate baseline

    # Per-event: did the champion's Brier beat the market's? (ties excluded from sign test)
    champ_better = sum(1 for r in rows
                       if brier(r["p_champion"], r["y"]) < brier(r["p_kalshi_mid"], r["y"]))
    ties = sum(1 for r in rows
               if brier(r["p_champion"], r["y"]) == brier(r["p_kalshi_mid"], r["y"]))
    decided = n - ties
    sign_p = binom_sign_test_p(champ_better, decided)

    dates = sorted({r["target_date"] for r in rows if r["target_date"]})

    # Per-date Brier breakdown
    by_date: dict[str, dict] = {}
    for d in dates:
        sub = [r for r in rows if r["target_date"] == d]
        by_date[d] = {
            "n": len(sub),
            "brier_champion": round(sum(brier(r["p_champion"], r["y"]) for r in sub) / len(sub), 4),
            "brier_kalshi_mid": round(sum(brier(r["p_kalshi_mid"], r["y"]) for r in sub) / len(sub), 4),
        }

    return {
        "n": n,
        "n_distinct_target_dates": len(dates),
        "target_date_range": [dates[0], dates[-1]] if dates else None,
        "base_rate_yes": round(base_rate, 4),
        "brier_champion": round(b_champ, 4),
        "brier_kalshi_mid": round(b_mid, 4),
        "brier_base_rate_baseline": round(b_clim, 4),
        "champion_minus_market": round(b_champ - b_mid, 4),
        "bss_champion_vs_base_rate": round(1 - b_champ / b_clim, 4) if b_clim > 0 else None,
        "champion_beats_market_events": champ_better,
        "ties": ties,
        "decided_comparisons": decided,
        "sign_test_p_one_sided": round(sign_p, 4),
        "verdict": ("champion beats market" if b_champ < b_mid else "champion does NOT beat market"),
        "by_date": by_date,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", choices=["first", "last"], default="first",
                    help="which capture to keep per market when a market was captured multiple times")
    ap.add_argument("--out", default=None, help="path to write the JSON report")
    args = ap.parse_args()

    rows = collect(keep=args.keep)
    summ = summarize(rows)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = Path(args.out) if args.out else (ROOT / "runs_backtest" / f"champion_vs_market_{stamp}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "generated_at": stamp,
        "source": "predictor/runs/*/report.json (resolved, de-duplicated by market)",
        "keep_policy": args.keep,
        "summary": summ,
        "rows": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # Human-readable summary
    print("=" * 72)
    print("CHAMPION (vendor_ensemble) vs MARKET (kalshi_mid) — resolved paper runs")
    print("=" * 72)
    if summ["n"] == 0:
        print("No resolved runs found.")
        return 0
    print(f"N events (unique markets)   : {summ['n']}")
    print(f"distinct target_dates       : {summ['n_distinct_target_dates']}  "
          f"({summ['target_date_range'][0]} … {summ['target_date_range'][1]})")
    print(f"base rate P(yes)            : {summ['base_rate_yes']}")
    print("-" * 72)
    print(f"Brier champion              : {summ['brier_champion']}")
    print(f"Brier kalshi_mid (market)   : {summ['brier_kalshi_mid']}")
    print(f"Brier base-rate baseline    : {summ['brier_base_rate_baseline']}")
    print(f"champion − market           : {summ['champion_minus_market']:+}  "
          f"({'champion better' if summ['champion_minus_market'] < 0 else 'market better'})")
    print(f"BSS champion vs base rate   : {summ['bss_champion_vs_base_rate']}")
    print("-" * 72)
    print(f"events champion beats market: {summ['champion_beats_market_events']} / {summ['decided_comparisons']} "
          f"(ties: {summ['ties']})")
    print(f"sign-test p (one-sided)     : {summ['sign_test_p_one_sided']}")
    print("-" * 72)
    print(f">> VERDICT: {summ['verdict'].upper()}")
    print(f">> wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
