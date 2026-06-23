"""Analyse de puissance statistique pour le sign-test G2 (predictor vs Kalshi mid).

Le modèle v3fa+forest_pct_5km a atteint HOLDOUT Brier 0.1172 < marché 0.1173
sur 12 dates (loop_20260622T063316Z). La puissance statistique est insuffisante
avec 12 dates. Ce script calcule combien de dates HOLDOUT sont nécessaires.

Usage:
    python scripts/power_analysis.py
    python scripts/power_analysis.py --theta 0.60 0.65 0.70
    python scripts/power_analysis.py --current-wins 8 --current-n 12

Le « win rate » est la probabilité que le modèle batte le marché (Brier_model <
Brier_market) sur une date donnée. H0: theta = 0.5 (no edge). H1: theta > 0.5.
"""
from __future__ import annotations

import argparse
import sys
from typing import Sequence

try:
    from scipy import stats
    import numpy as np
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def _binom_pvalue(k: int, n: int) -> float:
    """P(X >= k | n, p=0.5) via exact binomial (one-tailed, H1: theta > 0.5)."""
    if HAS_SCIPY:
        return float(stats.binomtest(k, n, p=0.5, alternative="greater").pvalue)
    # Fallback: manual binomial CDF (no numpy/scipy)
    from math import comb, pow as mpow
    # P(X >= k) = sum_{i=k}^{n} C(n,i) * 0.5^n
    total = sum(comb(n, i) for i in range(k, n + 1))
    return total / (2 ** n)


def power_table(
    thetas: Sequence[float],
    n_range: Sequence[int],
    alpha: float = 0.05,
) -> None:
    """Print a table: for each (theta, n), show expected wins and p-value."""
    header = f"{'N':>5}"
    for theta in thetas:
        header += f"  theta={theta:.0%} (p-val)"
    print(header)
    print("-" * len(header))

    for n in n_range:
        row = f"{n:>5}"
        for theta in thetas:
            if HAS_SCIPY:
                expected_k = int(round(theta * n))
            else:
                expected_k = int(theta * n + 0.5)
            pval = _binom_pvalue(expected_k, n)
            marker = "*" if pval < alpha else " "
            row += f"  {expected_k:2d}/{n} p={pval:.4f}{marker} "
        print(row)

    print(f"\n* = p < {alpha:.2f} (significant, one-tailed sign-test)")


def min_n_for_significance(
    theta: float,
    alpha: float = 0.05,
    max_n: int = 200,
) -> int | None:
    """Return the minimum N such that expected wins give p < alpha."""
    for n in range(1, max_n + 1):
        if HAS_SCIPY:
            expected_k = int(round(theta * n))
        else:
            expected_k = int(theta * n + 0.5)
        pval = _binom_pvalue(expected_k, n)
        if pval < alpha:
            return n
    return None


def observed_pvalue(k: int, n: int) -> None:
    """Print the current p-value and context for observed k wins out of n."""
    pval = _binom_pvalue(k, n)
    print(f"\n{'=' * 50}")
    print(f"Observed: {k}/{n} wins (win rate = {k/n:.1%})")
    print(f"Sign-test (one-tailed, H1: theta > 0.5): p = {pval:.4f}")
    if pval < 0.05:
        print("-> SIGNIFICANT at alpha=0.05 OK")
    elif pval < 0.10:
        print("-> Borderline (p < 0.10) — more data recommended")
    else:
        print("-> Not yet significant -- more HOLDOUT dates needed")
    print(f"{'=' * 50}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--theta", type=float, nargs="+",
        default=[0.55, 0.60, 0.65, 0.70],
        help="Assumed true win rates to tabulate (default: 0.55 0.60 0.65 0.70)",
    )
    parser.add_argument(
        "--n-range", type=int, nargs=2, default=[12, 60],
        metavar=("MIN", "MAX"),
        help="Range of N (HOLDOUT dates) to tabulate (default: 12 60)",
    )
    parser.add_argument(
        "--alpha", type=float, default=0.05,
        help="Significance threshold (default: 0.05)",
    )
    parser.add_argument(
        "--current-wins", type=int, default=None,
        help="Observed wins on current HOLDOUT (for p-value printout)",
    )
    parser.add_argument(
        "--current-n", type=int, default=None,
        help="Total current HOLDOUT dates",
    )
    args = parser.parse_args()

    if not HAS_SCIPY:
        print("[warn] scipy not available; using manual exact binomial (slower for large N)")

    if args.current_wins is not None and args.current_n is not None:
        observed_pvalue(args.current_wins, args.current_n)

    n_min, n_max = args.n_range
    n_range = list(range(n_min, n_max + 1, max(1, (n_max - n_min) // 20)))
    if n_max not in n_range:
        n_range.append(n_max)

    print(f"\nPower table (alpha={args.alpha:.2f}, H1: model beats market on each date)\n")
    power_table(args.theta, n_range, alpha=args.alpha)

    print("\nMinimum N for significance:")
    for theta in args.theta:
        n_req = min_n_for_significance(theta, alpha=args.alpha)
        if n_req:
            print(f"  theta={theta:.0%} -> need at least {n_req} HOLDOUT dates")
        else:
            print(f"  theta={theta:.0%} -> not achievable within 200 dates")

    print(
        "\nContext (Aratea G2 -- 2026-06-22):\n"
        "  Current HOLDOUT: 12 dates, Brier 0.1172 < market 0.1173 (gap 0.0001)\n"
        "  VALID trial 8 (forest_pct_5km): 8/12 wins (theta_hat ~= 0.67)\n"
        "  Next step: expand Kalshi universe (B45/B39) to reach >= 20 HOLDOUT dates\n"
        "  Target: Brier < market on p < 0.05 (one-tailed sign-test)\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
