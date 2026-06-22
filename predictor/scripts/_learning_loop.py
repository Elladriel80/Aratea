"""_learning_loop.py — champion/challenger iteration loop on historical data.

Exploratory script (underscore prefix — keeps production code immutable).

Idea: chain one-modification-at-a-time improvements and keep only the
ones that demonstrably generalize, without overfitting the backtest.

Workflow:
  1. Build the resolved-events dataset ONCE (same builder as
     train_learned.py), or load it from a JSON cache (--dataset-cache).
  2. Three-way chronological split by target_date (group-snapped, no
     event-day straddles a boundary):
         TRAIN (default 60%) -> fit candidate models
         VALID (default 20%) -> accept/reject each candidate
         HOLDOUT (default 20%, most recent) -> FROZEN. Evaluated exactly
         once, at the very end, to check the accepted chain generalizes.
  3. Candidate queue — ONE modification per candidate:
         {"op": "add_feature",  "feature": "..."}
         {"op": "drop_feature", "feature": "..."}
         {"op": "set_C",        "value": 0.3}     # L2 regularization weight
     Default queue is generated automatically; override with --candidates.
  4. Acceptance gate for each candidate (vs current incumbent config):
       (a) VALID Brier strictly lower,
       (b) one-sided Wilcoxon signed-rank test on per-DATE mean Brier
           deltas (rows from the same event-day are correlated, so we
           test by distinct date, not by row), p <= alpha (default 0.10),
       (c) VALID spans >= --min-distinct-dates distinct target_dates.
     Accepted -> becomes the incumbent. Every trial is logged either way.
  5. Final: refit initial config and final config on TRAIN+VALID, score
     both ONCE on HOLDOUT, alongside the kalshi_mid benchmark.
  6. Writes runs_learning/loop_<ts>/{loop.json, REPORT.md}.

This script NEVER touches CHAMPION.json — live promotion stays governed
by the existing champion/challenger rule on resolved trades.

Usage:
    python predictor/scripts/_learning_loop.py
    python predictor/scripts/_learning_loop.py --save-dataset-cache ds.json
    python predictor/scripts/_learning_loop.py --dataset-cache ds.json
    python predictor/scripts/_learning_loop.py --candidates my_queue.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.learning.features import FEATURE_SETS  # noqa: E402
from src.learning.model import GBMLearnedModel, LearnedModel, brier_score  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402

# Reuse the group-snapped chronological splitter from the main trainer —
# single source of truth for "no event-day straddles the boundary".
from train_learned import chronological_split  # noqa: E402

RUNS_DIR = ROOT / "runs_learning"

DEFAULT_BASE_SET = "v3"
DEFAULT_C = 1.0
MIN_DISTINCT_DATES = 3  # same spirit as PROMOTABLE_MIN_CARDINALITY

# Features that have no historical coverage — including them in the
# dataset union would silently drop (almost) every row.
FORWARD_ONLY_FEATURES = {"p_nws_ndfd"}

# Features that cannot be pre-computed at backfill time; they are derived
# from the training fold only (fold-aware) and injected at train time.
# They are excluded from the missing-features check and from the default
# candidate queue (to avoid asking for them from a cache that lacks them).
FOLD_AWARE_FEATURES = {
    "series_bias_fa",
    "p_consensus_x_series_bias_fa",
    "days_ahead_x_series_bias_fa",
    "forecast_revision",
}


# ---------------------------------------------------------------- catalogue

def feature_catalogue() -> dict:
    """name -> extractor fn, union of every registered feature set."""
    cat: dict = {}
    for spec in FEATURE_SETS.values():
        for name, fn in spec:
            cat.setdefault(name, fn)
    return cat


def default_candidates(base_features: list[str]) -> list[dict]:
    """One-modification-at-a-time queue from the base config.

    Order matters: cheap reweighting first (C sweep), then the ablation
    flagged in FEATURES.md (drop days_ahead), then one-by-one feature
    additions (excluding forward-only and fold-aware features).
    """
    queue: list[dict] = [
        {"op": "set_C", "value": 0.3},
        {"op": "set_C", "value": 3.0},
        {"op": "set_C", "value": 0.1},
    ]
    if "days_ahead" in base_features:
        queue.append({"op": "drop_feature", "feature": "days_ahead"})
    # If the base uses p_consensus, do NOT re-add its collinear
    # components by default (v2 NO-GO: compensating-coefficient artefact).
    # They stay testable through a custom --candidates file.
    skip = set(FORWARD_ONLY_FEATURES) | FOLD_AWARE_FEATURES
    if "p_consensus" in base_features:
        skip |= {"p_climatology", "p_forecast_blend", "p_ensemble"}
    for name in sorted(feature_catalogue()):
        if name in base_features or name in skip:
            continue
        queue.append({"op": "add_feature", "feature": name})
    return queue


# -------------------------------------------------------- fold-aware helpers

def _compute_series_bias_fa(X, y, meta):
    """Compute mean(p_consensus - outcome) per series_ticker from the given fold.

    Used to derive series_bias_fa at train time without data leakage into
    VALID/HOLDOUT.  p_consensus must already be present in X.
    """
    from collections import defaultdict
    s: dict = defaultdict(float)
    c: dict = defaultdict(int)
    for xi, yi, mi in zip(X, y, meta):
        st = mi.get("series_ticker")
        pc = xi.get("p_consensus")
        if st and pc is not None:
            s[st] += pc - yi
            c[st] += 1
    return {st: s[st] / c[st] for st in s}


def _inject_series_bias_fa(X, meta, bias, fallback=0.0):
    """Add series_bias_fa to every feature dict in X in place.

    Unknown series (not seen in the fold that produced `bias`) get `fallback`
    (default 0.0 = neutral prior, no systematic bias assumed).
    """
    for xi, mi in zip(X, meta):
        st = mi.get("series_ticker")
        xi["series_bias_fa"] = bias.get(st, fallback)


# ------------------------------------------------------------------ dataset

def build_or_load_dataset(union_features: list[str],
                          cache_path: str | None,
                          save_cache: str | None):
    if cache_path:
        data = json.loads(Path(cache_path).read_text(encoding="utf-8"))
        X, y, meta = data["X"], data["y"], data["meta"]
        # Fold-aware features are not stored in the cache; they are injected
        # after the chronological split (see main()).  Only check the others.
        missing = [f for f in union_features
                   if f not in FOLD_AWARE_FEATURES and X and f not in X[0]]
        if missing:
            raise SystemExit(
                f"dataset cache lacks features {missing}; rebuild without "
                f"--dataset-cache or trim the candidate queue.")
        return X, y, meta
    from src.learning.dataset import build
    cat = feature_catalogue()
    spec = [(n, cat[n]) for n in union_features if n not in FOLD_AWARE_FEATURES]
    X, y, meta = build(spec)
    if save_cache:
        Path(save_cache).write_text(
            json.dumps({"X": X, "y": y, "meta": meta}), encoding="utf-8")
        print(f">> dataset cached to {save_cache}")
    return X, y, meta


# ------------------------------------------------------------------- models

def fit_config(Xtr, ytr, config: dict, model_type: str = "lr") -> LearnedModel:
    feats = config["features"]
    if model_type == "gbm":
        m = GBMLearnedModel(feature_names=list(feats))
    else:
        m = LearnedModel(feature_names=list(feats))
        m.clf = LogisticRegression(penalty="l2", C=config["C"], solver="lbfgs",
                                   max_iter=2000, random_state=42)
    m.fit([{k: r[k] for k in feats} for r in Xtr], ytr)
    return m


def eval_config(model: LearnedModel, X, y) -> tuple[float, np.ndarray]:
    feats = model.feature_names
    p = model.predict_proba([{k: r[k] for k in feats} for r in X])
    return brier_score(y, p), p


# -------------------------------------------------------------- significance

def per_date_paired_test(meta, y, p_inc, p_cha) -> dict:
    """One-sided Wilcoxon signed-rank test on per-date mean Brier deltas.

    Rows sharing a target_date see the same weather — they are one
    observation, not many. So: average the per-row Brier within each
    distinct date, then test whether the challenger's per-date Brier is
    systematically lower than the incumbent's. Wilcoxon (rather than a
    pure sign test) keeps the MAGNITUDE of each date's improvement,
    which matters a lot while the number of distinct dates is small —
    a sign test needs 9/10 wins to reach p<=0.10, discarding real
    signal carried by a few strongly-improved dates.

    Falls back to the sign test if scipy is unavailable.
    """
    by_date: dict[str, list[int]] = {}
    for i, m in enumerate(meta):
        by_date.setdefault(m.get("target_date") or "?", []).append(i)
    y = np.asarray(y, dtype=float)
    deltas: list[float] = []  # incumbent - challenger; >0 = challenger better
    for idx in by_date.values():
        ii = np.array(idx)
        b_inc = float(np.mean((p_inc[ii] - y[ii]) ** 2))
        b_cha = float(np.mean((p_cha[ii] - y[ii]) ** 2))
        if b_cha != b_inc:  # drop exact ties (Wilcoxon convention)
            deltas.append(b_inc - b_cha)
    n = len(deltas)
    wins = sum(1 for d in deltas if d > 0)
    if n == 0:
        return {"n_dates_compared": 0, "wins": 0, "p_value": 1.0,
                "method": "none"}
    try:
        from scipy.stats import wilcoxon
        stat = wilcoxon(deltas, alternative="greater",
                        method="exact" if n <= 25 else "auto")
        return {"n_dates_compared": n, "wins": wins,
                "p_value": float(stat.pvalue), "method": "wilcoxon"}
    except ImportError:
        p_val = sum(math.comb(n, k) for k in range(wins, n + 1)) / 2 ** n
        return {"n_dates_compared": n, "wins": wins, "p_value": float(p_val),
                "method": "sign_test"}


# --------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-feature-set", default=DEFAULT_BASE_SET,
                    choices=sorted(FEATURE_SETS.keys()))
    ap.add_argument("--train-frac", type=float, default=0.6)
    ap.add_argument("--valid-frac", type=float, default=0.2)
    ap.add_argument("--alpha", type=float, default=0.10,
                    help="sign-test acceptance threshold")
    ap.add_argument("--min-distinct-dates", type=int,
                    default=MIN_DISTINCT_DATES)
    ap.add_argument("--candidates", default=None,
                    help="JSON file: list of {op,...} candidate dicts")
    ap.add_argument("--dataset-cache", default=None,
                    help="load dataset from this JSON instead of rebuilding")
    ap.add_argument("--save-dataset-cache", default=None)
    ap.add_argument("--no-write-run", action="store_true")
    ap.add_argument("--model-type", default="lr", choices=["lr", "gbm"],
                    help="lr = LogisticRegression L2 (default); gbm = GradientBoosting depth-2")
    args = ap.parse_args()

    base_features = [n for n, _ in FEATURE_SETS[args.base_feature_set]]
    model_type = args.model_type
    if args.candidates:
        queue = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    else:
        queue = default_candidates(base_features)
        if model_type == "gbm":
            # GBM has no C hyperparameter; skip set_C candidates
            queue = [c for c in queue if c.get("op") != "set_C"]

    # Union of every feature any config may need → identical rows for all
    # configs (comparability beats sample size here).
    union = sorted({*base_features,
                    *(c["feature"] for c in queue if "feature" in c)}
                   - FORWARD_ONLY_FEATURES)
    print(f">> base config: {args.base_feature_set} = {base_features}, "
          f"C={DEFAULT_C} (ignored for gbm)")
    print(f">> model type: {model_type}")
    print(f">> candidate queue: {len(queue)} modification(s)")
    print(f">> dataset union features: {union}")

    X, y, meta = build_or_load_dataset(union, args.dataset_cache,
                                       args.save_dataset_cache)
    print(f">> rows: {len(X)}  "
          f"distinct target_dates: {len({m.get('target_date') for m in meta})}")
    if len(X) < 30:
        print("!! dataset too small for a 3-way split. abort.")
        return 1

    # ---- 3-way chronological split (reuses the group-snapped splitter) --
    inner_frac = args.train_frac + args.valid_frac
    Xin, yin, min_, Xho, yho, mho = chronological_split(
        X, y, meta, inner_frac, split_key="target_date")
    Xtr, ytr, mtr, Xva, yva, mva = chronological_split(
        Xin, yin, min_, args.train_frac / inner_frac,
        split_key="target_date")

    def dr(mm):
        vals = sorted(v for v in (m.get("target_date") for m in mm) if v)
        return (f"{vals[0]}..{vals[-1]} ({len(set(vals))} dates)"
                if vals else "(none)")

    print(f">> TRAIN   n={len(Xtr):>4}  {dr(mtr)}")
    print(f">> VALID   n={len(Xva):>4}  {dr(mva)}")
    print(f">> HOLDOUT n={len(Xho):>4}  {dr(mho)}  [frozen until the end]")

    # ---- fold-aware feature injection -----------------------------------
    # series_bias_fa (and any other FOLD_AWARE_FEATURES in the base set) must
    # be estimated from TRAIN labels only so that VALID/HOLDOUT rows receive
    # the TRAIN-derived bias — no leakage.  After the main loop, the final
    # holdout evaluation re-injects using TRAIN+VALID bias (more data, same
    # spirit as refitting the model on the full inner set).
    fa_inject = [f for f in base_features if f in FOLD_AWARE_FEATURES]
    fa_needed = fa_inject and (not X or "series_bias_fa" not in X[0])
    if fa_needed:
        if "series_bias_fa" in fa_inject:
            bias_train = _compute_series_bias_fa(Xtr, ytr, mtr)
            _inject_series_bias_fa(Xtr, mtr, bias_train)
            _inject_series_bias_fa(Xva, mva, bias_train)
            _inject_series_bias_fa(Xho, mho, bias_train)
            print(f">> fold-aware series_bias_fa injected from TRAIN "
                  f"({len(bias_train)} series, "
                  f"mean bias {sum(bias_train.values())/len(bias_train):.4f}): "
                  f"{dict(bias_train)}")

    n_valid_dates = len({m.get("target_date") for m in mva})
    if n_valid_dates < args.min_distinct_dates:
        print(f"!! VALID spans only {n_valid_dates} distinct dates "
              f"(< {args.min_distinct_dates}). Any acceptance would be "
              "noise. abort.")
        return 1

    # ---- incumbent = base config --------------------------------------
    incumbent = {"features": list(base_features), "C": DEFAULT_C}
    inc_model = fit_config(Xtr, ytr, incumbent, model_type)
    inc_brier, inc_p = eval_config(inc_model, Xva, yva)
    initial_config = json.loads(json.dumps(incumbent))
    print(f"\n>> incumbent VALID Brier: {inc_brier:.4f}")

    mid_va = np.array([m["yes_mid"] for m in mva], dtype=float)
    print(f">> kalshi_mid VALID Brier: {brier_score(yva, mid_va):.4f}")

    # ---- the loop -------------------------------------------------------
    ledger: list[dict] = []
    for i, cand in enumerate(queue, 1):
        cfg = json.loads(json.dumps(incumbent))
        op = cand.get("op")
        if op == "add_feature":
            if cand["feature"] in cfg["features"]:
                continue
            cfg["features"] = cfg["features"] + [cand["feature"]]
        elif op == "drop_feature":
            if cand["feature"] not in cfg["features"] \
               or len(cfg["features"]) <= 1:
                continue
            cfg["features"] = [f for f in cfg["features"]
                               if f != cand["feature"]]
        elif op == "set_C":
            if cand["value"] == cfg["C"]:
                continue
            cfg["C"] = float(cand["value"])
        else:
            print(f"   [skip] unknown op {op!r}")
            continue

        model = fit_config(Xtr, ytr, cfg, model_type)
        b, p = eval_config(model, Xva, yva)
        test = per_date_paired_test(mva, yva, inc_p, p)
        accepted = (b < inc_brier
                    and test["p_value"] <= args.alpha
                    and test["n_dates_compared"] >= args.min_distinct_dates)

        entry = {"trial": i, "candidate": cand, "config": cfg,
                 "brier_valid": b, "brier_valid_incumbent": inc_brier,
                 "sign_test": test, "accepted": accepted}
        ledger.append(entry)
        tag = "ACCEPT" if accepted else "reject"
        print(f"   [{i:>2}/{len(queue)}] {op}({cand.get('feature', cand.get('value'))}) "
              f"Brier {b:.4f} vs {inc_brier:.4f}  "
              f"sign-test p={test['p_value']:.3f} "
              f"({test['wins']}/{test['n_dates_compared']} dates)  -> {tag}")
        if accepted:
            incumbent, inc_brier, inc_p = cfg, b, p

    n_accepted = sum(e["accepted"] for e in ledger)
    print(f"\n>> loop done: {len(ledger)} trials, {n_accepted} accepted")
    print(f">> final config: {incumbent}")

    # ---- single-shot holdout verification -------------------------------
    # Refit on TRAIN+VALID (all data the loop was allowed to see), score
    # once on the frozen, most-recent slice. This answers the only
    # question that matters: did the accepted chain improve the FUTURE?
    XtrVa, ytrVa = Xin, yin
    # For fold-aware features: re-estimate bias from TRAIN+VALID (larger
    # sample than TRAIN alone) and re-inject before the final evaluation.
    if fa_needed and "series_bias_fa" in fa_inject:
        bias_trva = _compute_series_bias_fa(XtrVa, ytrVa, min_)
        _inject_series_bias_fa(XtrVa, min_, bias_trva)
        _inject_series_bias_fa(Xho, mho, bias_trva)
        print(f">> fold-aware series_bias_fa re-injected from TRAIN+VALID "
              f"({len(bias_trva)} series) for final holdout evaluation")
    b_init_ho, _ = eval_config(fit_config(XtrVa, ytrVa, initial_config, model_type),
                               Xho, yho)
    b_final_ho, _ = eval_config(fit_config(XtrVa, ytrVa, incumbent, model_type),
                                Xho, yho)
    mid_ho = np.array([m["yes_mid"] for m in mho], dtype=float)
    b_mid_ho = brier_score(yho, mid_ho)

    print("\n>> HOLDOUT (single evaluation, frozen most-recent slice):")
    print(f"   initial config Brier : {b_init_ho:.4f}")
    print(f"   final   config Brier : {b_final_ho:.4f}")
    print(f"   kalshi_mid     Brier : {b_mid_ho:.4f}")
    generalized = b_final_ho < b_init_ho
    print(">> chain GENERALIZED to holdout." if generalized else
          ">> chain did NOT generalize — accepted gains were "
          "validation-specific. Do not promote; gather more dates.")

    # ---- persist ---------------------------------------------------------
    if not args.no_write_run:
        ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        out = RUNS_DIR / f"loop_{ts}"
        out.mkdir(parents=True, exist_ok=True)
        record = {
            "schema": "learning_loop/1",
            "timestamp_utc": ts,
            "base_feature_set": args.base_feature_set,
            "model_type": model_type,
            "initial_config": initial_config,
            "final_config": incumbent,
            "params": {"train_frac": args.train_frac,
                       "valid_frac": args.valid_frac,
                       "alpha": args.alpha,
                       "min_distinct_dates": args.min_distinct_dates},
            "split": {"n_train": len(Xtr), "n_valid": len(Xva),
                      "n_holdout": len(Xho),
                      "train_dates": dr(mtr), "valid_dates": dr(mva),
                      "holdout_dates": dr(mho)},
            "n_trials": len(ledger), "n_accepted": n_accepted,
            "ledger": ledger,
            "holdout": {"brier_initial": b_init_ho,
                        "brier_final": b_final_ho,
                        "brier_kalshi_mid": b_mid_ho,
                        "generalized": generalized},
            "multiple_testing_note": (
                f"{len(ledger)} candidates were tested against the same "
                "validation slice; the holdout verdict above is the only "
                "unbiased number in this file."),
        }
        (out / "loop.json").write_text(json.dumps(record, indent=2),
                                       encoding="utf-8")
        lines = [
            f"# Learning loop {ts}",
            "",
            f"- Base: `{args.base_feature_set}` -> final `{incumbent}`",
            f"- Trials: {len(ledger)}, accepted: {n_accepted}",
            f"- VALID: {dr(mva)} / HOLDOUT: {dr(mho)}",
            "",
            "| # | candidate | Brier valid | vs incumbent | p | verdict |",
            "|---|---|---|---|---|---|",
        ]
        for e in ledger:
            c = e["candidate"]
            lines.append(
                f"| {e['trial']} | {c['op']}"
                f"({c.get('feature', c.get('value'))}) "
                f"| {e['brier_valid']:.4f} "
                f"| {e['brier_valid_incumbent']:.4f} "
                f"| {e['sign_test']['p_value']:.3f} "
                f"| {'ACCEPT' if e['accepted'] else 'reject'} |")
        lines += [
            "",
            "## Holdout (single shot)",
            "",
            f"- initial: {b_init_ho:.4f} / final: {b_final_ho:.4f} "
            f"/ kalshi_mid: {b_mid_ho:.4f}",
            f"- **{'GENERALIZED' if generalized else 'DID NOT GENERALIZE'}**",
            "",
            "_This run never edits CHAMPION.json; live promotion follows "
            "the existing champion/challenger rule._",
        ]
        (out / "REPORT.md").write_text("\n".join(lines) + "\n",
                                       encoding="utf-8")
        print(f"\n>> wrote {out / 'loop.json'} and REPORT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# end
