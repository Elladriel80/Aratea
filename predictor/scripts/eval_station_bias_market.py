"""eval_station_bias_market.py — la correction station face au marché, hors ligne.

FR : Rejoue les captures live `data/predictions/forward_*.json` (bins centraux
avec cotation deux côtés) en recalculant P(bin) de deux façons à partir des
valeurs par modèle stockées :
  raw      moyenne des modèles, sigma inter-modèles plancher 1 °F (politique
           de production depuis PR #160, appliquée uniformément même aux
           captures antérieures pour comparer à égalité) ;
  station  moyenne + biais station, sigma résiduel, appris STRICTEMENT
           point-in-time sur `data/truth/skill/forecast_points.json` × vérité
           CLI : seules les dates cibles antérieures à la capture servent.
L'issue de chaque bin vient de la vérité CLI (`data/truth/cli_daily.json`),
qui est la règle de résolution Kalshi. Aucun réseau.

Question tranchée : la correction station réduit-elle l'écart à `kalshi_mid`
sur les vrais bins et les vrais prix ?

EN : Replays live captures, recomputes P(bin) as raw (production policy) and
station-corrected (bias + residual sigma fitted strictly point-in-time on
forecast_points × CLI truth), settles each bin from CLI truth, and compares
both to kalshi_mid. Offline.

Usage:
    python scripts/eval_station_bias_market.py
    python scripts/eval_station_bias_market.py --min-date 2026-08-03 --leads 0,1
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR  # noqa: E402
from src.truth.synthetic_bins import Bin, brier, prob_in_bin_gaussian  # noqa: E402

SIGMA_FLOOR = 1.0
MIN_PAIRS = 20


def load_truth() -> dict[tuple[str, date], dict]:
    rows = json.loads((TRUTH_DIR / "cli_daily.json").read_text(encoding="utf-8"))
    return {(r["station"], date.fromisoformat(r["valid"])): r for r in rows}


def truth_value(t: dict, variable: str):
    v = t.get("high" if variable == "temp_max" else "low")
    return None if v is None else float(v)


def load_points() -> list[dict]:
    pts = json.loads((TRUTH_DIR / "skill" / "forecast_points.json").read_text(encoding="utf-8"))
    for p in pts:
        p["_target"] = date.fromisoformat(p["target"])
        p["_mean"] = statistics.fmean(p["per_model"].values())
    return pts


class PointInTimeBias:
    """Biais et sigma par (station, variable, lead) appris sur les paires
    (prévision, vérité CLI) dont la date cible est antérieure à `as_of`."""

    def __init__(self, points: list[dict], truth: dict):
        self.pairs: dict[tuple, list[tuple[date, float]]] = defaultdict(list)
        for p in points:
            t = truth.get((p["station"], p["_target"]))
            if not t:
                continue
            obs = truth_value(t, p["variable"])
            if obs is None:
                continue
            self.pairs[(p["station"], p["variable"], p["lead"])].append((p["_target"], obs - p["_mean"]))
        for k in self.pairs:
            self.pairs[k].sort()
        self._cache: dict = {}

    def get(self, station: str, variable: str, lead: int, as_of: date):
        lead = min(7, max(1, lead))
        key = (station, variable, lead, as_of)
        if key in self._cache:
            return self._cache[key]
        resid = [r for d, r in self.pairs.get((station, variable, lead), []) if d < as_of]
        out = None
        if len(resid) >= MIN_PAIRS:
            out = (statistics.fmean(resid), max(SIGMA_FLOOR, statistics.pstdev(resid)), len(resid))
        self._cache[key] = out
        return out


def load_records(min_date: date | None, leads: set[int] | None) -> list[dict]:
    seen: dict[tuple[str, int], dict] = {}
    for f in sorted(glob.glob(str(ROOT / "data" / "predictions" / "forward_*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in d.get("records", []):
            if r.get("lower") is None or r.get("upper") is None:
                continue                                       # bins centraux seulement
            if r.get("yes_bid") is None or r.get("yes_ask") is None or r["yes_ask"] <= 0 or r["yes_ask"] < r["yes_bid"]:
                continue
            ens = (r.get("predictions") or {}).get("ensemble") or {}
            pm = (ens.get("inputs") or {}).get("per_model_value") or {}
            if len(pm) < 2:
                continue
            target = date.fromisoformat(r["target_date"])
            if min_date and target < min_date:
                continue
            snap = datetime.strptime(r["snapshot_at"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).date()
            lead = (target - snap).days
            if lead < 0 or (leads is not None and lead not in leads):
                continue
            key = (r["ticker"], lead)
            if key in seen:
                continue                                       # première capture par (ticker, lead)
            seen[key] = {**r, "_target": target, "_snap": snap, "_lead": lead, "_pm": pm}
    return list(seen.values())


def fmt(x):
    return "n/a" if x is None else f"{x:.4f}"


def summarize(rows: list[dict], keyf) -> dict:
    g: dict = defaultdict(list)
    for r in rows:
        g[keyf(r)].append(r)
    out = {}
    for k, rs in sorted(g.items(), key=lambda kv: str(kv[0])):
        out[k] = {
            "n_bins": len(rs), "n_dates": len({r["_target"] for r in rs}),
            "base_rate": statistics.fmean(r["y"] for r in rs),
            "brier_raw": statistics.fmean(brier(r["p_raw"], r["y"]) for r in rs),
            "brier_station": statistics.fmean(brier(r["p_station"], r["y"]) for r in rs),
            "brier_market": statistics.fmean(brier(r["p_mkt"], r["y"]) for r in rs),
        }
    return out


def sign_test(rows, a, b):
    by: dict = defaultdict(list)
    for r in rows:
        by[r["_target"]].append(r)
    w = l = 0
    for rs in by.values():
        ba = statistics.fmean(brier(r[a], r["y"]) for r in rs)
        bb = statistics.fmean(brier(r[b], r["y"]) for r in rs)
        w += ba < bb
        l += ba > bb
    n = w + l
    p = sum(math.comb(n, i) for i in range(w, n + 1)) / 2 ** n if n else None
    return {"a": a, "b": b, "dates": n, "a_wins": w, "p_one_sided": p}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-date", default="", help="ne garder que les cibles ≥ cette date")
    ap.add_argument("--leads", default="", help="ex. 0,1 (défaut : tous)")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "skill"))
    args = ap.parse_args()
    min_date = date.fromisoformat(args.min_date) if args.min_date else None
    leads = {int(x) for x in args.leads.split(",")} if args.leads else None

    truth = load_truth()
    bias = PointInTimeBias(load_points(), truth)
    records = load_records(min_date, leads)

    rows, skips = [], defaultdict(int)
    for r in records:
        icao = CITY_TO_ICAO.get(r["location_key"])
        t = truth.get((icao, r["_target"])) if icao else None
        obs = truth_value(t, r["variable"]) if t else None
        if obs is None:
            skips["no_cli_truth"] += 1
            continue
        b = Bin(int(r["lower"]), int(r["upper"]))
        y = 1 if b.contains(obs) else 0
        vals = list(r["_pm"].values())
        mu, sig = statistics.fmean(vals), max(SIGMA_FLOOR, statistics.pstdev(vals))
        p_raw = prob_in_bin_gaussian(mu, sig, b)
        bs = bias.get(icao, r["variable"], r["_lead"], r["_snap"])
        if bs is None:
            skips["no_bias_yet"] += 1
            continue
        p_station = prob_in_bin_gaussian(mu + bs[0], bs[1], b)
        em = (r.get("predictions") or {}).get("ensemble_members") or {}
        p_members = em.get("prob_yes") if isinstance(em.get("prob_yes"), (int, float)) else None
        rows.append({**r, "y": y, "p_raw": p_raw, "p_station": p_station, "p_mkt": r["yes_mid"],
                     "p_members": p_members, "_month": r["_target"].strftime("%Y-%m"), "_icao": icao})

    if not rows:
        print(f"Aucune ligne évaluable. Skips : {dict(skips)}")
        return 1

    overall = summarize(rows, lambda r: "all")
    by_lead = summarize(rows, lambda r: r["_lead"])
    by_month = summarize(rows, lambda r: r["_month"])
    by_station = summarize(rows, lambda r: f"{r['_icao']}/{r['variable']}")
    # Challenger ensemble_members (capturé depuis le 2026-09-09) : comparé sur
    # ses seules lignes, aux trois autres politiques.
    mrows = [r for r in rows if r.get("p_members") is not None]
    members_summ = {}
    if mrows:
        for k, v in summarize(mrows, lambda r: r["_lead"]).items():
            v["brier_members"] = statistics.fmean(brier(r["p_members"], r["y"]) for r in mrows if r["_lead"] == k)
            members_summ[k] = v
        members_tests = {"members_vs_station": sign_test(mrows, "p_members", "p_station"),
                         "members_vs_market": sign_test(mrows, "p_members", "p_mkt")}
    tests = {
        "station_vs_raw": sign_test(rows, "p_station", "p_raw"),
        "raw_vs_market": sign_test(rows, "p_raw", "p_mkt"),
        "station_vs_market": sign_test(rows, "p_station", "p_mkt"),
    }

    def table(title, summ, key):
        L = [f"### {title}", "", f"| {key} | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |",
             "|---|---|---|---|---|---|---|---|"]
        for k, v in summ.items():
            L.append(f"| {k} | {v['n_bins']} | {v['n_dates']} | {v['base_rate']:.3f} | {v['brier_raw']:.4f} | "
                     f"{v['brier_station']:.4f} | {v['brier_market']:.4f} | {v['brier_station'] - v['brier_market']:+.4f} |")
        return L + [""]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ["# Correction station vs marché Kalshi / Station bias vs Kalshi market", "",
             f"Généré / generated : {now}. Captures live `forward_*.json`, bins centraux cotés deux côtés, "
             f"première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time "
             f"(cibles < date de capture, ≥ {MIN_PAIRS} paires). Skips : {dict(skips)}.", "",
             "FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais "
             "station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.",
             "EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; "
             "kalshi_mid = market mid at capture. Negative last column = beats the market.", ""]
    lines += table("Global / overall", overall, "groupe")
    lines += table("Par lead / by lead (jours entre capture et cible)", by_lead, "lead")
    lines += table("Par mois de cible / by target month", by_month, "mois")
    lines += table("Par station / by station", by_station, "station/variable")
    if members_summ:
        lines += ["### Challenger ensemble_members (lignes où il est capturé)", "",
                  "| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |", "|---|---|---|---|---|---|---|"]
        for k, v in members_summ.items():
            lines.append(f"| {k} | {v['n_bins']} | {v['n_dates']} | {v['brier_raw']:.4f} | {v['brier_station']:.4f} | "
                         f"{v['brier_members']:.4f} | {v['brier_market']:.4f} |")
        lines.append("")
        tests.update(members_tests)
    lines += ["### Sign tests par date", "", "| comparaison | dates | victoires a | p unilatéral |", "|---|---|---|---|"]
    for k, t in tests.items():
        lines.append(f"| {k} ({t['a']} < {t['b']}) | {t['dates']} | {t['a_wins']} | {fmt(t['p_one_sided'])} |")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "market_backtest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "market_backtest.json").write_text(json.dumps({
        "schema": "station_bias_market_backtest/1", "generated_at": now,
        "params": {"min_date": args.min_date or None, "leads": sorted(leads) if leads else None},
        "n_rows": len(rows), "skips": dict(skips), "overall": overall, "by_lead": by_lead,
        "by_month": by_month, "by_station": by_station, "sign_tests": tests,
        "ensemble_members_by_lead": members_summ}, indent=2), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
