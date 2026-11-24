"""MED robustness for the 7 Oct 2026 C3S/CHIRPS edge. Offline.

The headline ECMWF-51 BSS (0.063, N=97) is re-sliced: bootstrap,
permutation, leads, thresholds, halves, and a true season-start forecast.
No CDS call. No secrets. No new data.

Dependency (not on main): this script imports the C3S scoring code from
PR 260, branch ``cursor/c3s-multimodel-ab-59e8``, commit 973a4ab.
Those modules are absent from main and this file does not vendor them:

- ``src.forecast.c3s_offline`` — ``load_c3s_csv``, ``aggregate_equal_weight``,
  ``filter_window``, ``ECMWF_51``
- ``src.score.c3s_ab`` — ``score_all``

Also uses, and these are on main:

- ``src.forecast.seas5_offline.collapse_shortest_lead``
- ``src.score.seas5_ab`` — ``_load_chirps_truth``, ``skill_block``

Paths are relative to ``predictor/`` unless overridden. There is no
fallback to a shared-box directory.

Usage (from ``predictor/``, on a tree that contains the PR 260 modules):

    python scripts/med_robustness.py
    python scripts/med_robustness.py \\
        --forecast-csv data/forecasts/c3s/c3s_tp_monthly.csv \\
        --out data/truth/c3s_ab/MED_ROBUSTNESS.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import DATA_DIR  # noqa: E402
from src.forecast.seas5_offline import collapse_shortest_lead  # noqa: E402
from src.score.seas5_ab import _load_chirps_truth, skill_block  # noqa: E402

# PR 260, branch cursor/c3s-multimodel-ab-59e8 @ 973a4ab. Not on main.
C3S_CODE = (
    "PR 260 branch cursor/c3s-multimodel-ab-59e8 @973a4ab "
    "(modules not on main)"
)
C3S_IMPORT_ERROR = (
    "med_robustness.py needs the C3S scoring modules from PR 260, "
    "branch cursor/c3s-multimodel-ab-59e8 (commit 973a4ab). "
    "They are not on main: src.forecast.c3s_offline "
    "(load_c3s_csv, aggregate_equal_weight, filter_window, ECMWF_51) "
    "and src.score.c3s_ab (score_all). Import failed: {exc}"
)

DEFAULT_CSV = ROOT / "data" / "forecasts" / "c3s" / "c3s_tp_monthly.csv"
DEFAULT_OUT = ROOT / "data" / "truth" / "c3s_ab" / "MED_ROBUSTNESS.json"

REGION = "med"
SEASON_FIRST = {"DJF": 12, "MAM": 3, "JJA": 6, "SON": 9}
NBOOT = 2000
NPERM = 2000

THRESH = [
    ("below_mean", None, "sous la moyenne (headline)"),
    ("below_q", 0.2, "tres sec: sous le 20e centile"),
    ("below_q", 1 / 3, "sec: tiers le plus sec"),
    ("below_q", 0.5, "sous la mediane"),
    ("above_q", 2 / 3, "humide: tiers le plus humide"),
    ("above_q", 0.8, "tres humide: au-dessus du 80e centile"),
]


def _display(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def _load_c3s():
    try:
        from src.forecast.c3s_offline import (  # type: ignore
            ECMWF_51,
            aggregate_equal_weight,
            filter_window,
            load_c3s_csv,
        )
        from src.score import c3s_ab  # type: ignore
    except ImportError as exc:
        raise SystemExit(C3S_IMPORT_ERROR.format(exc=exc)) from exc
    return ECMWF_51, aggregate_equal_weight, filter_window, load_c3s_csv, c3s_ab


def run(csv_path: Path, out_path: Path, data_dir: Path) -> dict:
    """Same slices as the 2026-11-24 measurement. Writes JSON and returns it."""
    ECMWF_51, aggregate_equal_weight, filter_window, load_c3s_csv, c3s_ab = (
        _load_c3s()
    )
    rng = np.random.default_rng(20261124)

    raw = load_c3s_csv(csv_path)
    raw = [r for r in raw if r["region"] == REGION]
    truth_rows, reason = _load_chirps_truth(data_dir)
    if reason is not None:
        raise SystemExit(reason)
    truth = {
        (r["season"], r["year"]): r["mean"]
        for r in truth_rows
        if r["region"] == REGION
    }

    def arm_rows(arm, rows):
        if arm == "ecmwf51":
            return [r for r in rows if (r["origin"], int(r["system"])) == ECMWF_51]
        return aggregate_equal_weight(rows)

    def seasons_from(monthly):
        b = {}
        for r in monthly:
            b.setdefault((r["season"], r["season_year"]), {})[r["valid_month"]] = (
                r["tp_mean_mm"]
            )
        return {k: statistics.fmean(v.values()) for k, v in b.items() if len(v) == 3}

    def fc_shortest(arm):
        rows = arm_rows(arm, filter_window(raw, None, 1, 7))
        rows = sorted(
            rows,
            key=lambda r: (
                r["valid_year"],
                r["valid_month"],
                r["lead_month"],
                r.get("init_year", 0),
                r.get("init_month", 0),
            ),
        )
        return seasons_from(collapse_shortest_lead(rows))

    def fc_fixed_lead(arm, lead):
        return seasons_from(arm_rows(arm, filter_window(raw, None, lead, lead)))

    def fc_seasonal_init(arm, k):
        """One init per season: init month = first season month - (k-1); leads k..k+2."""
        out_fc = {}
        rows = arm_rows(arm, raw)
        for season, month0 in SEASON_FIRST.items():
            init_month = ((month0 - (k - 1) - 1) % 12) + 1
            sel = [
                r
                for r in rows
                if int(r["init_month"]) == init_month
                and k <= int(r["lead_month"]) <= k + 2
                and r["season"] == season
            ]
            out_fc.update(
                {kk: v for kk, v in seasons_from(sel).items() if kk[0] == season}
            )
        return out_fc

    def loo_thresh(vals, i, kind, q):
        others = np.delete(np.asarray(vals), i)
        if kind == "below_mean":
            return others.mean()
        return np.quantile(others, q)

    def flag(v, thr, kind):
        return v < thr if kind.startswith("below") else v > thr

    def build(fc, kind, q):
        """(season, year, p, event). LOO thresholds, forecast and truth apart."""
        out_rows = []
        for season in SEASON_FIRST:
            fk = sorted([k for k in fc if k[0] == season], key=lambda k: k[1])
            tk = sorted([k for k in truth if k[0] == season], key=lambda k: k[1])
            fv = [fc[k] for k in fk]
            tv = [truth[k] for k in tk]
            fflag = {
                k: flag(fc[k], loo_thresh(fv, i, kind, q), kind)
                for i, k in enumerate(fk)
            }
            tflag = {
                k: flag(truth[k], loo_thresh(tv, i, kind, q), kind)
                for i, k in enumerate(tk)
            }
            for k in fk:
                if k in tflag:
                    out_rows.append(
                        (k[0], k[1], 1.0 if fflag[k] else 0.0, bool(tflag[k]))
                    )
        out_rows.sort(key=lambda x: (x[1], x[0]))
        return out_rows

    def bss_of(ev, p):
        if len(ev) < 2:
            return None
        blk = skill_block(list(ev), list(p))
        return blk["bss"]

    def bss_raw(ev, p):
        ev = np.asarray(ev, float)
        p = np.asarray(p, float)
        n = len(ev)
        if n < 2:
            return np.nan
        cl = (ev.sum() - ev) / (n - 1)
        bc = np.mean((cl - ev) ** 2)
        return np.nan if bc == 0 else 1 - np.mean((p - ev) ** 2) / bc

    def stats(rows, do_ci=True):
        if not rows:
            return {"n": 0}
        ev = np.array([r[3] for r in rows], float)
        p = np.array([r[2] for r in rows], float)
        yrs = np.array([r[1] for r in rows])
        seas = np.array([r[0] for r in rows])
        n = len(ev)
        b = bss_raw(ev, p)
        res = {
            "n": n,
            "base_rate": round(ev.mean(), 3),
            "bss": None if np.isnan(b) else round(b, 4),
        }
        yes = p == 1
        res["fc_yes_n"] = int(yes.sum())
        res["event_rate_when_fc_yes"] = round(ev[yes].mean(), 3) if yes.any() else None
        res["event_rate_when_fc_no"] = (
            round(ev[~yes].mean(), 3) if (~yes).any() else None
        )
        res["hit_rate_pct"] = round(100 * np.mean(p == ev), 1)
        pc = np.empty(n)
        for i in range(n):
            m = p == p[i]
            m[i] = False
            pc[i] = ev[m].mean() if m.any() else ev[np.arange(n) != i].mean()
        bc = bss_raw(ev, pc)
        res["bss_calibrated_cv"] = None if np.isnan(bc) else round(bc, 4)
        if not do_ci or n < 10:
            return res
        uy = np.unique(yrs)
        idx_by_y = {y: np.where(yrs == y)[0] for y in uy}
        boots = []
        for _ in range(NBOOT):
            pick = rng.choice(uy, len(uy), replace=True)
            ii = np.concatenate([idx_by_y[y] for y in pick])
            v = bss_raw(ev[ii], p[ii])
            if not np.isnan(v):
                boots.append(v)
        boots = np.array(boots)
        res["ci95"] = [
            round(float(np.quantile(boots, 0.025)), 4),
            round(float(np.quantile(boots, 0.975)), 4),
        ]
        res["p_boot_bss_le_0"] = round(float(np.mean(boots <= 0)), 3)
        res["p_luck_pass_gate_if_true_bss_0"] = round(
            float(np.mean((boots - boots.mean()) > 0.05)), 3
        )
        res["ci_excludes_0"] = bool(res["ci95"][0] > 0)
        loyo = [bss_raw(ev[yrs != y], p[yrs != y]) for y in uy]
        res["loyo_min_max"] = [
            round(float(np.nanmin(loyo)), 4),
            round(float(np.nanmax(loyo)), 4),
        ]
        perm = []
        for _ in range(NPERM):
            pp = p.copy()
            for s in np.unique(seas):
                m = np.where(seas == s)[0]
                pp[m] = p[rng.permutation(m)]
            perm.append(bss_raw(ev, pp))
        perm = np.array(perm)
        res["p_perm"] = round(float((np.sum(perm >= b) + 1) / (len(perm) + 1)), 3)
        res["p_null_pass_gate"] = round(float(np.mean(perm > 0.05)), 3)
        return res

    def sub(rows, pred):
        return [r for r in rows if pred(r)]

    out = {
        "meta": {
            "date": "2026-11-24",
            "region": "MED",
            "truth": "CHIRPS v2 monthly (repo data/truth/chirps)",
            "code": C3S_CODE,
            "forecast_csv": _display(csv_path),
            "forecast": (
                "ensemble-mean seasonal total; forecast prob is 0/1 "
                "(dry if below LOO climatology of forecast, same rule as PR 246/260)"
            ),
            "climato": "LOO base rate on the scored seasons (repo skill_block)",
            "bootstrap": f"{NBOOT} resamples of years",
            "permutation": f"{NPERM} shuffles of forecast years within season type",
            "gate": "N>=10 and BSS>0.05",
            "cds_called": False,
        },
        "slices": [],
    }

    rep = c3s_ab.score_all(forecast_csv=csv_path)
    out["reproduce"] = {
        "ecmwf51_bss_repo": rep["ecmwf51"]["ab"]["C"]["by_region"]["med"]["bss"],
        "mix_bss_repo": rep["ab"]["C"]["by_region"]["med"]["bss"],
    }
    for arm in ("ecmwf51", "mix"):
        rows = build(fc_shortest(arm), "below_mean", None)
        out["reproduce"][arm + "_bss_here"] = round(
            bss_raw([r[3] for r in rows], [r[2] for r in rows]), 4
        )
        out["reproduce"][arm + "_n_here"] = len(rows)
    print(out["reproduce"])

    def add(group, label, arm, rows, **extra):
        s = stats(rows)
        s.update({"group": group, "slice": label, "arm": arm})
        s.update(extra)
        s["passes_gate"] = bool(
            s.get("n", 0) >= 10 and s.get("bss") is not None and s["bss"] > 0.05
        )
        out["slices"].append(s)
        return s

    for arm in ("ecmwf51", "mix"):
        fcs = fc_shortest(arm)
        head = build(fcs, "below_mean", None)
        add("headline", "MED toutes saisons, delai court", arm, head)
        for season in SEASON_FIRST:
            add("saison", season, arm, sub(head, lambda r, season=season: r[0] == season))
        for lead in range(1, 7):
            add(
                "delai_mois",
                f"delai {lead} (chaque mois prevu {lead - 1} mois avant)",
                arm,
                build(fc_fixed_lead(arm, lead), "below_mean", None),
            )
        for k in (1, 2, 3, 4):
            rows = build(fc_seasonal_init(arm, k), "below_mean", None)
            add(
                "vraie_saison",
                f"une prevision par saison, lancee {k - 1} mois avant",
                arm,
                rows,
            )
            if k in (1, 2):
                for season in SEASON_FIRST:
                    add(
                        "vraie_saison_x_saison",
                        f"lancee {k - 1} mois avant, {season}",
                        arm,
                        sub(rows, lambda r, season=season: r[0] == season),
                    )
        for kind, q, lab in THRESH[1:]:
            add("seuil", lab, arm, build(fcs, kind, q))
        add("moitie", "1993-2004", arm, sub(head, lambda r: r[1] <= 2004))
        add("moitie", "2005-2017", arm, sub(head, lambda r: r[1] >= 2005))

    for arm in ("ecmwf51", "mix"):
        ss = [
            s
            for s in out["slices"]
            if s["arm"] == arm and s["group"] != "headline" and s.get("n", 0) >= 10
        ]
        out.setdefault("multiple_testing", {})[arm] = {
            "n_slices": len(ss),
            "n_pass_gate": sum(s["passes_gate"] for s in ss),
            "expected_pass_by_luck_if_true_bss_0": round(
                sum(s.get("p_luck_pass_gate_if_true_bss_0", 0) for s in ss), 1
            ),
            "expected_pass_vs_random_0_1_forecast": round(
                sum(s.get("p_null_pass_gate", 0) for s in ss), 1
            ),
            "n_ci95_above_0": sum(1 for s in ss if s.get("ci_excludes_0")),
            "expected_ci95_above_0_by_luck": round(0.025 * len(ss), 1),
            "ci95_above_0": [s["slice"] for s in ss if s.get("ci_excludes_0")],
            "passing": [s["slice"] for s in ss if s["passes_gate"]],
        }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for s in out["slices"]:
        print(
            f"{s['arm']:8} {s['group']:22} {s['slice'][:42]:42} "
            f"N={s['n']:3} BSS={s.get('bss')} CI={s.get('ci95')} "
            f"luck={s.get('p_luck_pass_gate_if_true_bss_0')} "
            f"pperm={s.get('p_perm')} cal={s.get('bss_calibrated_cv')} "
            f"yes={s.get('event_rate_when_fc_yes')} no={s.get('event_rate_when_fc_no')}"
        )
    print(json.dumps(out["multiple_testing"], indent=1, ensure_ascii=False))
    # bss_of is the repo skill_block path; kept so a reader can compare it to bss_raw.
    _ = bss_of
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=(
            "MED robustness of the 7 Oct 2026 C3S/CHIRPS edge. Offline. "
            "Needs the C3S modules from PR 260 "
            "(branch cursor/c3s-multimodel-ab-59e8); they are not on main."
        )
    )
    p.add_argument(
        "--forecast-csv",
        default=str(DEFAULT_CSV),
        help="C3S monthly CSV (default: predictor/data/forecasts/c3s/c3s_tp_monthly.csv)",
    )
    p.add_argument(
        "--out",
        default=str(DEFAULT_OUT),
        help="JSON output (default: predictor/data/truth/c3s_ab/MED_ROBUSTNESS.json)",
    )
    p.add_argument(
        "--data-dir",
        default=str(DATA_DIR),
        help="Predictor data dir that holds CHIRPS truth (default: predictor/data)",
    )
    args = p.parse_args(argv)
    csv_path = Path(args.forecast_csv)
    if not csv_path.is_file():
        raise SystemExit(
            f"CSV absent: {csv_path}. "
            "Pass --forecast-csv. This script does not call CDS and does not "
            "look on a shared box."
        )
    run(csv_path, Path(args.out), Path(args.data_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
