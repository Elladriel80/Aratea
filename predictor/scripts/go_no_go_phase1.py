#!/usr/bin/env python3
"""Phase 1 go/no-go evaluator — mechanical verdict for predictor/runs/CONVENTION.md §6.

Reads every resolved live run under ``predictor/runs/*/report.json`` and produces
the Brier comparison the §6 criterion is written against:

  - meta-ensemble (champion ``vendor_ensemble``)
  - the tracked individual models (``learned_v2``, ``kalshi_mid_baseline``)
  - ``climatology`` — NOT logged in the schema-v2 scoring block, so it is
    *recomputed* here from the same bin/date with ``ClimatologyPredictor``.
    The config (years_back=30, window_days=3 = the predictor defaults) is
    validated against the climatology Brier logged in the early runs
    (e.g. run 002: logged brier_climatology=0.0237, recompute=0.0237).

Every number printed traces back to a ``report.json`` scoring block or to the
deterministic climatology recompute below. No value is hand-entered.

Usage:
    python predictor/scripts/go_no_go_phase1.py
"""
from __future__ import annotations

import glob
import json
import math
import os
import statistics as st
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.predictors.base import ContractSpec  # noqa: E402
from src.predictors.climatology import ClimatologyPredictor  # noqa: E402
from src.predictors.parsers import SERIES_MAP, parse_kalshi_date  # noqa: E402

# Validated climatology config (matches the brier_climatology logged in run 002).
CLIM_YEARS_BACK = 30
CLIM_WINDOW_DAYS = 3


def target_spec(ticker: str) -> Optional[ContractSpec]:
    """Reconstruct the ContractSpec of a run's target market from its ticker.

    All Phase-1 resolved targets are 1 degF ``B`` bins (e.g. ``...-B51.5`` =
    51..52 degF), so the bin bounds are encoded in the ticker — no subtitle
    needed. Returns None for any non-B / unmappable ticker.
    """
    parts = ticker.split("-")
    if len(parts) < 3 or parts[0] not in SERIES_MAP or not parts[2].startswith("B"):
        return None
    variable, city = SERIES_MAP[parts[0]]
    d = parse_kalshi_date(parts[1])
    if d is None:
        return None
    center = float(parts[2][1:])
    return ContractSpec(
        market_ticker=ticker,
        event_ticker="-".join(parts[:2]),
        variable=variable,
        location_key=city,
        target_date=d,
        lower=center - 0.5,
        upper=center + 0.5,
        raw_subtitle="",
    )


def sign_test(better: list, worse: list) -> tuple:
    """1-sided binomial sign test that ``better`` has lower Brier than ``worse``.

    Returns (wins, losses, p_value) where p = P(X >= wins | Binom(wins+losses, .5)).
    """
    wins = sum(1 for a, b in zip(better, worse) if a is not None and b is not None and a < b)
    losses = sum(1 for a, b in zip(better, worse) if a is not None and b is not None and a > b)
    n = wins + losses
    p = sum(math.comb(n, k) for k in range(wins, n + 1)) * 0.5 ** n if n else float("nan")
    return wins, losses, p


def main() -> int:
    runs_dir = os.path.join(os.path.dirname(__file__), "..", "runs")
    clim = ClimatologyPredictor(years_back=CLIM_YEARS_BACK, window_days=CLIM_WINDOW_DAYS)

    ens, learned, kalshi, climato = [], [], [], []
    skipped = []
    for f in sorted(glob.glob(os.path.join(runs_dir, "*", "report.json"))):
        d = json.load(open(f, encoding="utf-8"))
        sc = d.get("scoring") or {}
        bm = sc.get("by_model") or {}
        outcome = sc.get("outcome")
        if not (isinstance(bm.get("vendor_ensemble"), dict) and outcome in ("yes", "no")):
            continue
        y = 1.0 if outcome == "yes" else 0.0
        ticker = (d.get("event") or {}).get("target_market_ticker") \
            or (d.get("markets") or [{}])[0].get("ticker")
        spec = target_spec(ticker) if ticker else None
        if spec is None:
            skipped.append((d.get("run_id"), ticker))
            continue
        p_clim = clim.predict(spec).prob_yes
        ens.append(bm["vendor_ensemble"]["brier"])
        learned.append((bm.get("learned_v2") or {}).get("brier"))
        kalshi.append((bm.get("kalshi_mid_baseline") or {}).get("brier"))
        climato.append((p_clim - y) ** 2)

    n = len(ens)
    mean = lambda xs: st.mean([x for x in xs if x is not None])
    median = lambda xs: st.median([x for x in xs if x is not None])

    print(f"N resolved live runs = {n}  (skipped: {len(skipped)})")
    print(f"{'model':<24}{'mean Brier':>12}{'median':>10}")
    for name, xs in [("vendor_ensemble", ens), ("learned_v2", learned),
                     ("kalshi_mid_baseline", kalshi),
                     (f"climatology({CLIM_YEARS_BACK}/{CLIM_WINDOW_DAYS})", climato)]:
        print(f"{name:<24}{mean(xs):>12.4f}{median(xs):>10.4f}")

    print("\nHead-to-head sign tests (ensemble strictly lower Brier = win):")
    for label, comp in [("learned_v2", learned), ("kalshi_mid", kalshi), ("climatology", climato)]:
        w, l, p = sign_test(ens, comp)
        print(f"  ensemble vs {label:<12} wins={w:>3} losses={l:>3}  1-sided p={p:.4f}")

    me, ml, mk, mc = mean(ens), mean(learned), mean(kalshi), mean(climato)
    best_individual = min(ml, mk)
    cond_a = me < best_individual
    cond_b = me < mc
    print("\n§6 conditions (mean Brier):")
    print(f"  A  ensemble < best individual model ({best_individual:.4f}): {cond_a}")
    print(f"  B  ensemble < climatology ({mc:.4f}): {cond_b}")
    print(f"\nMECHANICAL VERDICT: {'GO' if (cond_a and cond_b) else 'NO-GO'}")
    print("(see predictor/docs/go-no-go-phase1-2026-06-03.md for the significance caveats)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
