"""eval_single_curve_skill.py — Une seule courbe (piste A5).

FR : Le champion en ligne fabrique déjà une gaussienne (moyenne des
vendeurs + correction ville), découpe P(bin) par la CDF, PUIS mélange
chaque bin avec une fréquence climatologique (pas une courbe). Convention
live : pas de renormalisation inter-bins.

On mesure, hors ligne, sur les mêmes fichiers déjà là :

  A  champion rejoué = mélange horizon (courbe gaussienne + fréquence
     par bin). C'est ce que `EnsemblePredictor` renvoie aujourd'hui.
  H1 courbe_gauss = la même N(mu + biais, sigma résiduel), sans mélange
     par bin. Hypothèse : une seule courbe, plus de fuite climat par case.
  H2 courbe_melange = mélange équipondéré de N(v_i + biais, sigma
     résiduel) sur les vendeurs déjà capturés. Hypothèse : une densité
     à plusieurs bosses, puis découpe. Ce n'est PAS les 31 versions GEFS
     (A3, déjà mesuré).
  mid = kalshi_mid quand un prix existe.

Split temporel A1 (TRAIN < 2026-08-03). Sign-test par date. J0 et J-1
séparés. Le champion en ligne n'est pas touché.

EN : Offline A/B of the live champion (Gaussian + per-bin climato blend)
vs a single continuous curve then bin cut. Two labelled curves: station
Gaussian without blend (H1), equal mixture of vendor Gaussians (H2).
kalshi_mid on the side. Does not switch the live champion.

Usage:
    python scripts/eval_single_curve_skill.py
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

from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, CliDay  # noqa: E402
from src.truth.skill import SIGMA_FLOOR_F, ForecastPoint, StationBias  # noqa: E402
from src.truth.synthetic_bins import (  # noqa: E402
    Bin, brier, horizon_blend, kalshi_style_bins,
    prob_in_bin_gaussian, prob_in_bin_mixture,
)

A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)
MIN_PAIRS = 20


def load_cli(path: Path) -> dict[tuple[str, date], dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {(r["station"], date.fromisoformat(r["valid"])): r for r in rows}


def truth_value(row: dict | None, variable: str):
    if not row:
        return None
    v = row.get("high" if variable == "temp_max" else "low")
    return None if v is None else float(v)


def load_points(path: Path, wanted: set[str] | None) -> list[ForecastPoint]:
    out: list[ForecastPoint] = []
    if not path.exists():
        return out
    for r in json.loads(path.read_text(encoding="utf-8")):
        if wanted is not None and r["station"] not in wanted:
            continue
        out.append(ForecastPoint(
            station=r["station"], variable=r["variable"],
            target=date.fromisoformat(r["target"]), lead=int(r["lead"]),
            per_model={m: float(v) for m, v in r["per_model"].items()},
        ))
    return out


def _curve_pair(vals: list[float], bias: float, sigma: float, b: Bin) -> tuple[float, float]:
    shifted = [v + bias for v in vals]
    mu = statistics.fmean(shifted)
    return (
        prob_in_bin_gaussian(mu, sigma, b),
        prob_in_bin_mixture(shifted, sigma, b),
    )


def score_skill(
    hold: list[ForecastPoint],
    truth: dict,
    bias: StationBias,
) -> list[dict]:
    """HOLDOUT A1, bins synthétiques. Pas de marché, pas de mélange climato.

    Ici A (correction ville) et H1 (courbe gauss) sont la même densité.
    Seul H2 (mélange des vendeurs) peut différer.
    """
    rows = []
    for p in hold:
        obs = truth_value(truth.get((p.station, p.target)), p.variable)
        if obs is None:
            continue
        st = bias.apply(p)
        if st is None:
            continue
        mu_st, sig_st = st
        bias_f = mu_st - p.mean
        for b in kalshi_style_bins(p.mean, n_central=6):
            if not b.is_central:
                continue
            p_h1, p_h2 = _curve_pair(list(p.per_model.values()), bias_f, sig_st, b)
            rows.append({
                "station": p.station, "variable": p.variable,
                "target": p.target, "lead": p.lead,
                "central": True, "y": b.contains(obs),
                "p_champion": p_h1,   # hors marché : déjà une seule courbe
                "p_h1": p_h1,
                "p_h2": p_h2,
                "p_mid": None,
                "bin": b.label(),
            })
    return rows


def load_market_records(pred_dir: Path, leads: set[int] | None) -> list[dict]:
    """Première capture par (ticker, lead). Cases centrales et queues."""
    seen: dict[tuple[str, int], dict] = {}
    for f in sorted(glob.glob(str(pred_dir / "forward_*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in d.get("records", []):
            ens = (r.get("predictions") or {}).get("ensemble") or {}
            inp = ens.get("inputs") or {}
            pm = inp.get("per_model_value") or {}
            if len(pm) < 2:
                continue
            if r.get("yes_bid") is None or r.get("yes_ask") is None:
                continue
            if r["yes_ask"] <= 0 or r["yes_ask"] < r["yes_bid"]:
                continue
            target = date.fromisoformat(r["target_date"])
            snap = datetime.strptime(r["snapshot_at"], "%Y%m%dT%H%M%SZ").replace(
                tzinfo=timezone.utc)
            lead = (target - snap.date()).days
            if lead < 0 or (leads is not None and lead not in leads):
                continue
            key = (r["ticker"], lead)
            if key in seen:
                continue
            seen[key] = {
                **r,
                "_target": target,
                "_snap": snap.date(),
                "_lead": lead,
                "_pm": {m: float(v) for m, v in pm.items()},
                "_p_climato": inp.get("p_climato"),
                "_p_live": ens.get("prob_yes"),
                "_event": r.get("event_ticker") or r.get("series_ticker") or r["ticker"],
            }
    return list(seen.values())


def score_market(
    records: list[dict],
    truth: dict,
    points: list[ForecastPoint],
) -> tuple[list[dict], dict]:
    """Biais ville point-in-time (cibles < date de capture), comme A1 marché."""
    import eval_station_bias_market as mkt

    # PointInTimeBias attend forecast_points au format dict avec _target/_mean.
    raw_pts = []
    for p in points:
        raw_pts.append({
            "station": p.station, "variable": p.variable, "lead": p.lead,
            "_target": p.target, "_mean": p.mean,
        })
    bias = mkt.PointInTimeBias(raw_pts, truth)

    rows, skips = [], defaultdict(int)
    for r in records:
        icao = CITY_TO_ICAO.get(r["location_key"])
        if not icao:
            skips["no_station"] += 1
            continue
        obs = truth_value(truth.get((icao, r["_target"])), r["variable"])
        if obs is None:
            skips["no_cli_truth"] += 1
            continue
        lo = r.get("lower")
        hi = r.get("upper")
        b = Bin(
            None if lo is None else int(lo),
            None if hi is None else int(hi),
        )
        vals = list(r["_pm"].values())
        mu = statistics.fmean(vals)
        bs = bias.get(icao, r["variable"], r["_lead"], r["_snap"])
        if bs is None:
            skips["no_bias_yet"] += 1
            continue
        bias_f, sig_st, _n = bs
        p_h1, p_h2 = _curve_pair(vals, bias_f, sig_st, b)
        p_climato = r.get("_p_climato")
        if not isinstance(p_climato, (int, float)):
            skips["no_climato"] += 1
            p_champion = p_h1
            has_climato = False
        else:
            p_champion = horizon_blend(p_h1, float(p_climato), r["_lead"])
            has_climato = True
        p_live = r.get("_p_live")
        p_live = float(p_live) if isinstance(p_live, (int, float)) else None
        rows.append({
            "station": icao, "variable": r["variable"],
            "target": r["_target"], "lead": r["_lead"],
            "event": r["_event"], "ticker": r["ticker"],
            "central": b.is_central,
            "y": b.contains(obs),
            "p_champion": p_champion,
            "p_h1": p_h1,
            "p_h2": p_h2,
            "p_mid": float(r["yes_mid"]),
            "p_live": p_live,
            "has_climato": has_climato,
            "bin": b.label(),
        })
    return rows, dict(skips)


def _common(rows: list[dict], keys: tuple[str, ...]) -> list[dict]:
    return [r for r in rows if all(r.get(k) is not None for k in keys)]


def summarize(rows: list[dict], keyf, keys: tuple[str, ...]) -> dict:
    g: dict = defaultdict(list)
    for r in rows:
        g[keyf(r)].append(r)
    out = {}
    for k, rs in sorted(g.items(), key=lambda kv: str(kv[0])):
        use = _common(rs, keys)
        if not use:
            continue
        rec = {
            "n_bins": len(use),
            "n_dates": len({r["target"] for r in use}),
            "base_rate": statistics.fmean(float(r["y"]) for r in use),
        }
        for name in keys:
            rec[f"brier_{name}"] = statistics.fmean(
                brier(float(r[name]), r["y"]) for r in use)
        out[k] = rec
    return out


def sign_test(rows: list[dict], a: str, b: str) -> dict:
    by: dict = defaultdict(list)
    for r in rows:
        if r.get(a) is None or r.get(b) is None:
            continue
        by[r["target"]].append(r)
    w = l = 0
    for rs in by.values():
        ba = statistics.fmean(brier(float(r[a]), r["y"]) for r in rs)
        bb = statistics.fmean(brier(float(r[b]), r["y"]) for r in rs)
        w += ba < bb
        l += ba > bb
    n = w + l
    p = (sum(math.comb(n, i) for i in range(w, n + 1)) / 2 ** n) if n else None
    return {"a": a, "b": b, "dates": n, "a_wins": w, "p_one_sided": p}


def consistency(rows: list[dict]) -> dict:
    """Somme des P sur les cases listées d'un même événement (ville-jour-lead)."""
    by: dict = defaultdict(list)
    for r in rows:
        by[(r["event"], r["lead"], r["target"])].append(r)
    sums = {"p_champion": [], "p_h1": [], "p_h2": [], "p_mid": []}
    both_tails = 0
    n_events = 0
    for rs in by.values():
        n_events += 1
        has_lo = any(not r["central"] and r["bin"].endswith("or below") for r in rs)
        has_hi = any(not r["central"] and r["bin"].endswith("or above") for r in rs)
        if has_lo and has_hi:
            both_tails += 1
        for name in sums:
            vals = [float(r[name]) for r in rs if r.get(name) is not None]
            if vals:
                sums[name].append(sum(vals))

    def pack(xs: list[float]) -> dict:
        if not xs:
            return {"n": 0}
        return {
            "n": len(xs),
            "mean_sum": statistics.fmean(xs),
            "min_sum": min(xs),
            "max_sum": max(xs),
            "n_abs_err_gt_0_05": sum(1 for x in xs if abs(x - 1.0) > 0.05),
            "n_abs_err_gt_0_20": sum(1 for x in xs if abs(x - 1.0) > 0.20),
        }

    return {
        "n_events": n_events,
        "n_events_both_tails": both_tails,
        **{name: pack(xs) for name, xs in sums.items()},
    }


def _fmt(x):
    return "n/a" if x is None else f"{x:.4f}"


def _table(title: str, summ: dict, key: str, cols: list[tuple[str, str]]) -> list[str]:
    head = [c[0] for c in cols]
    lines = [f"### {title}", "",
             f"| {key} | n contrats | n dates | " + " | ".join(head) + " |",
             "|" + "|".join(["---"] * (3 + len(cols))) + "|"]
    for k, r in summ.items():
        cells = [str(k), str(r["n_bins"]), str(r["n_dates"])]
        for _, field in cols:
            cells.append(_fmt(r.get(field)))
        lines.append("| " + " | ".join(cells) + " |")
    return lines + [""]


def _sign_lines(tests: dict) -> list[str]:
    lines = ["### Sign-test par date (Brier plus petit = gagne)", "",
             "| comparaison | dates | jours gagnés par a | p unilatéral |",
             "|---|---|---|---|"]
    for name, t in tests.items():
        lines.append(
            f"| {name} ({t['a']} < {t['b']}) | {t['dates']} | {t['a_wins']} | {_fmt(t['p_one_sided'])} |"
        )
    return lines + [""]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split-date", default=A1_SPLIT.isoformat())
    ap.add_argument("--end", default=A1_END.isoformat())
    ap.add_argument("--skill-leads", default="1,2,3,4,5,6,7")
    ap.add_argument("--market-leads", default="0,1")
    ap.add_argument("--stations", default="")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "curve"))
    ap.add_argument("--pred-dir", default=str(ROOT / "data" / "predictions"))
    args = ap.parse_args()

    split = date.fromisoformat(args.split_date)
    end = date.fromisoformat(args.end)
    skill_leads = {int(x) for x in args.skill_leads.split(",") if x}
    market_leads = {int(x) for x in args.market_leads.split(",") if x}
    wanted = {s.strip() for s in args.stations.split(",") if s.strip()} or None

    truth = load_cli(TRUTH_DIR / "cli_daily.json")
    points = load_points(TRUTH_DIR / "skill" / "forecast_points.json", wanted)
    train = [p for p in points if p.target < split]
    hold = [p for p in points if split <= p.target <= end and p.lead in skill_leads]
    truth_cli = {}
    for (st, d), r in truth.items():
        truth_cli[(st, d)] = CliDay(
            station=st, valid=d, high_f=r.get("high"), low_f=r.get("low"),
            high_time=r.get("high_time"), low_time=r.get("low_time"),
            precip_in=r.get("precip"), precip_trace=bool(r.get("precip_trace")),
            snow_in=r.get("snow"), snow_trace=bool(r.get("snow_trace")),
            product=None,
        )
    bias = StationBias().fit(train, truth_cli)

    skill_rows = score_skill(hold, truth, bias)
    skill_keys = ("p_champion", "p_h1", "p_h2")
    skill_all = summarize(skill_rows, lambda r: "all", skill_keys)
    skill_lead = summarize(skill_rows, lambda r: r["lead"], skill_keys)
    skill_var = summarize(skill_rows, lambda r: r["variable"], skill_keys)
    skill_tests = {
        "h2_vs_h1": sign_test(skill_rows, "p_h2", "p_h1"),
        "h1_vs_champion": sign_test(skill_rows, "p_h1", "p_champion"),
    }

    records = load_market_records(Path(args.pred_dir), market_leads)
    mkt_rows, skips = score_market(records, truth, points)
    central = [r for r in mkt_rows if r["central"]]
    mkt_keys = ("p_champion", "p_h1", "p_h2", "p_mid")
    mkt_all = summarize(central, lambda r: "all", mkt_keys)
    mkt_lead = summarize(central, lambda r: r["lead"], mkt_keys)
    mkt_var = summarize(central, lambda r: r["variable"], mkt_keys)
    cons_all = consistency(mkt_rows)
    cons_lead = {lead: consistency([r for r in mkt_rows if r["lead"] == lead])
                 for lead in sorted({r["lead"] for r in mkt_rows})}

    def tests_for(rs: list[dict]) -> dict:
        return {
            "h1_vs_champion": sign_test(rs, "p_h1", "p_champion"),
            "h2_vs_champion": sign_test(rs, "p_h2", "p_champion"),
            "h2_vs_h1": sign_test(rs, "p_h2", "p_h1"),
            "h1_vs_mid": sign_test(rs, "p_h1", "p_mid"),
            "h2_vs_mid": sign_test(rs, "p_h2", "p_mid"),
            "champion_vs_mid": sign_test(rs, "p_champion", "p_mid"),
        }

    mkt_tests = tests_for(central)
    mkt_tests_by_lead = {str(lead): tests_for([r for r in central if r["lead"] == lead])
                         for lead in sorted({r["lead"] for r in central})}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cols_skill = [
        ("Brier champion (= H1 hors marché)", "brier_p_champion"),
        ("Brier H1 gauss", "brier_p_h1"),
        ("Brier H2 mélange", "brier_p_h2"),
    ]
    cols_mkt = [
        ("Brier champion", "brier_p_champion"),
        ("Brier H1 gauss", "brier_p_h1"),
        ("Brier H2 mélange", "brier_p_h2"),
        ("Brier kalshi_mid", "brier_p_mid"),
    ]
    lines = [
        "# Une seule courbe (piste A5) / Single predictive curve",
        "",
        f"Généré / generated : {now}.",
        f"Split TRAIN < {split.isoformat()}, HOLDOUT skill {split.isoformat()} → {end.isoformat()}.",
        "H1 = N(mu + biais ville, sigma résiduel), une gaussienne, découpe des cases.",
        "H2 = mélange équipondéré des vendeurs déjà capturés, même biais, même sigma, puis découpe.",
        "Champion rejoué = H1 mélangé à la fréquence climat par bin (formule live, tau = 8 j).",
        "Hors marché le mélange climat n'existe pas : champion = H1.",
        "Vérité : rapport officiel CLI. Aucun chiffre inventé. Champion en ligne inchangé.",
        f"Skips marché : {skips}.",
        "",
    ]
    lines += _table("Skill hors marché (HOLDOUT A1, bins synthétiques centraux)", skill_all, "groupe", cols_skill)
    lines += _table("Skill par lead", skill_lead, "lead", cols_skill)
    lines += _table("Skill par variable", skill_var, "variable", cols_skill)
    lines += _sign_lines(skill_tests)
    lines += _table("Marché, cases centrales cotées (J0 et J-1)", mkt_all, "groupe", cols_mkt)
    lines += _table("Marché par lead (0 = jour même, 1 = veille)", mkt_lead, "lead", cols_mkt)
    lines += _table("Marché par variable", mkt_var, "variable", cols_mkt)
    lines += _sign_lines(mkt_tests)
    lines += ["### Sign-test marché par lead", ""]
    for lead, tests in mkt_tests_by_lead.items():
        lines += [f"Lead {lead}", ""]
        lines += _sign_lines(tests)

    def cons_block(title: str, c: dict) -> list[str]:
        L = [f"### {title}", "",
             f"Événements (ville-jour-lead) : {c['n_events']}. "
             f"Avec les deux queues listées : {c['n_events_both_tails']}.",
             "",
             "| série | n | somme moyenne | min | max | |somme−1| > 0,05 | |somme−1| > 0,20 |",
             "|---|---|---|---|---|---|---|"]
        labels = {
            "p_champion": "champion rejoué",
            "p_h1": "H1 gauss",
            "p_h2": "H2 mélange",
            "p_mid": "kalshi_mid",
        }
        for name, label in labels.items():
            s = c.get(name) or {}
            if not s.get("n"):
                L.append(f"| {label} | 0 | n/a | n/a | n/a | n/a | n/a |")
                continue
            L.append(
                f"| {label} | {s['n']} | {s['mean_sum']:.4f} | {s['min_sum']:.4f} | "
                f"{s['max_sum']:.4f} | {s['n_abs_err_gt_0_05']} | {s['n_abs_err_gt_0_20']} |"
            )
        return L + [""]

    lines += cons_block("Cohérence (somme des P sur les cases listées du même événement)", cons_all)
    for lead, c in cons_lead.items():
        lines += cons_block(f"Cohérence lead {lead}", c)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "curve_skill.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload = {
        "schema": "single_curve_a5/1",
        "generated_at": now,
        "hypotheses": {
            "A_champion": (
                "horizon_blend(H1, p_climato_stored, lead); "
                "on skill holdout this equals H1 (no climato blend)"
            ),
            "H1_courbe_gauss": "N(mu + station_bias, residual_sigma) then CDF bin cut",
            "H2_courbe_melange": (
                "equal mixture of N(vendor_i + station_bias, residual_sigma) then CDF bin cut"
            ),
            "mid": "kalshi yes_mid at first capture of (ticker, lead)",
        },
        "params": {
            "split_date": split.isoformat(),
            "end": end.isoformat(),
            "skill_leads": sorted(skill_leads),
            "market_leads": sorted(market_leads),
            "sigma_floor": SIGMA_FLOOR_F,
            "min_train_pairs": MIN_PAIRS,
        },
        "investigation": {
            "champion_core": "single_gaussian_cdf_cut",
            "champion_then": "per_bin_climato_frequency_blend",
            "renormalize": False,
        },
        "skill": {
            "n_rows": len(skill_rows),
            "overall": skill_all,
            "by_lead": {str(k): v for k, v in skill_lead.items()},
            "by_variable": skill_var,
            "sign_tests": skill_tests,
        },
        "market": {
            "n_rows_all": len(mkt_rows),
            "n_rows_central": len(central),
            "skips": skips,
            "overall": mkt_all,
            "by_lead": {str(k): v for k, v in mkt_lead.items()},
            "by_variable": mkt_var,
            "sign_tests": mkt_tests,
            "sign_tests_by_lead": mkt_tests_by_lead,
            "consistency": cons_all,
            "consistency_by_lead": {str(k): v for k, v in cons_lead.items()},
        },
    }
    (out_dir / "curve_skill.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
