"""eval_emos_skill.py — EMOS par station et par saison (piste B1).

FR : Ajuste y ~ N(a + b·moyenne, c + d·variance) par CRPS, ville par ville
et saison par saison, sur TRAIN < 2026-08-03 (même coupure que A1/A2/A3).
Score le HOLDOUT sur les mêmes contrats que le mélange actuel. Compare à
la correction ville à deux nombres, à NBM, et au prix du marché quand
il existe.

Le champion en ligne n'est pas touché. On mesure seulement.

EN : Fit four-parameter EMOS by CRPS on the A1 split, score the same
holdout, compare to the two-parameter city correction, NBM, and
kalshi_mid. Does not switch the live champion.

Usage:
    python scripts/eval_emos_skill.py
"""
from __future__ import annotations

import argparse
import glob
import json
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

import eval_nbm_skill as nbm_eval  # noqa: E402
from src.forecast.nbm_client import NbmTextClient  # noqa: E402
from src.forecast.nbm_prob import prob_in_bin_nbm  # noqa: E402
from src.truth.emos import Emos, meteo_season  # noqa: E402
from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, CliDay  # noqa: E402
from src.truth.skill import (  # noqa: E402
    SIGMA_FLOOR_F, ForecastPoint, StationBias, climatology_gaussian,
)
from src.truth.synthetic_bins import Bin, kalshi_style_bins, prob_in_bin_gaussian  # noqa: E402

A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)


def load_points(path: Path, wanted: set[str]) -> list[ForecastPoint]:
    out: list[ForecastPoint] = []
    if not path.exists():
        return out
    for r in json.loads(path.read_text(encoding="utf-8")):
        if r["station"] not in wanted:
            continue
        out.append(ForecastPoint(
            station=r["station"], variable=r["variable"],
            target=date.fromisoformat(r["target"]), lead=int(r["lead"]),
            per_model={m: float(v) for m, v in r["per_model"].items()},
        ))
    return out


def truth_by_from_cli(cli: dict) -> dict[tuple[str, date], CliDay]:
    out = {}
    for (st, d), r in cli.items():
        out[(st, d)] = CliDay(
            station=st, valid=d, high_f=r.get("high"), low_f=r.get("low"),
            high_time=r.get("high_time"), low_time=r.get("low_time"),
            precip_in=r.get("precip"), precip_trace=bool(r.get("precip_trace")),
            snow_in=r.get("snow"), snow_trace=bool(r.get("snow_trace")),
            product=None,
        )
    return out


def score_holdout(
    hold: list[ForecastPoint],
    truth_by: dict,
    truth_lists: dict,
    bias: StationBias,
    emos: Emos,
    nbm_forecasts: list,
) -> list[dict]:
    nbm_idx = nbm_eval.index_forecasts(nbm_forecasts) if nbm_forecasts else {}
    rows = []
    for p in hold:
        d = truth_by.get((p.station, p.target))
        if d is None:
            continue
        obs = d.value_for(p.variable)
        if obs is None:
            continue
        mu_raw, sig_raw = p.mean, max(SIGMA_FLOOR_F, p.spread)
        st = bias.apply(p)
        em = emos.apply(p)
        cl = climatology_gaussian(truth_lists.get(p.station, []), p.variable, p.target)
        fc = nbm_eval.pick_nbm(nbm_idx, p.station, p.variable, p.target, p.lead) if nbm_idx else None
        used = None
        if em is not None:
            used = "seasonal" if not em[2].fallback else "pooled"
        for b in kalshi_style_bins(mu_raw, n_central=6):
            if not b.is_central:
                continue
            p_emos = prob_in_bin_gaussian(em[0], em[1], b) if em else None
            p_station = prob_in_bin_gaussian(st[0], st[1], b) if st else None
            # Repli documenté : si EMOS n'a pas assez de jours, on garde
            # la correction ville actuelle. Le total reste comparable à A1.
            p_emos_filled = p_emos if p_emos is not None else p_station
            p_nbm = prob_in_bin_nbm(fc, b) if fc is not None else None
            rows.append({
                "station": p.station, "variable": p.variable,
                "target": p.target, "lead": p.lead,
                "season": meteo_season(p.target),
                "outcome": b.contains(obs),
                "p_raw": prob_in_bin_gaussian(mu_raw, sig_raw, b),
                "p_station": p_station,
                "p_emos": p_emos,
                "p_emos_filled": p_emos_filled,
                "p_climo": prob_in_bin_gaussian(cl[0], cl[1], b) if cl else None,
                "p_nbm": p_nbm, "p_market": None, "bin": b.label(),
                "emos_source": used,
            })
    return rows


def _emos_from_dicts(
    train_pts: list[ForecastPoint],
    truth_by: dict,
) -> Emos:
    return Emos().fit(train_pts, truth_by)


def score_market(
    points: list[ForecastPoint],
    truth_by: dict,
    bias: StationBias,
    emos: Emos,
    nbm_forecasts: list,
    leads: set[int],
    min_date: date,
    split: date,
) -> tuple[list[dict], dict]:
    """Prix kalshi_mid, lead demandé, EMOS appris sur TRAIN (pas de fuite).

    On ne score EMOS que si la cible est dans le HOLDOUT : les paramètres
    viennent de dates < split. Les jours avant le split n'ont pas d'EMOS
    honnête avec cette coupure (apprendre sur l'été pour noter juin
    regarderait le futur).
    """
    nbm_tgt = nbm_eval.index_by_target(nbm_forecasts) if nbm_forecasts else {}
    seen: dict[tuple, dict] = {}
    skips: dict[str, int] = defaultdict(int)
    for f in sorted(glob.glob(str(ROOT / "data" / "predictions" / "forward_*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in d.get("records", []):
            if r.get("lower") is None or r.get("upper") is None:
                continue
            if r.get("yes_bid") is None or r.get("yes_ask") is None:
                continue
            if r["yes_ask"] <= 0 or r["yes_ask"] < r["yes_bid"]:
                continue
            ens = (r.get("predictions") or {}).get("ensemble") or {}
            pm = (ens.get("inputs") or {}).get("per_model_value") or {}
            target = date.fromisoformat(r["target_date"])
            if target < min_date:
                continue
            snap = datetime.strptime(r["snapshot_at"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            lead = (target - snap.date()).days
            if lead not in leads:
                continue
            key = (r["ticker"], lead)
            if key in seen:
                continue
            seen[key] = {**r, "_target": target, "_snap": snap, "_lead": lead, "_pm": pm}

    rows = []
    for r in seen.values():
        icao = CITY_TO_ICAO.get(r["location_key"])
        if not icao:
            skips["no_station"] += 1
            continue
        t = truth_by.get((icao, r["_target"]))
        obs = t.value_for(r["variable"]) if t else None
        if obs is None:
            skips["no_cli_truth"] += 1
            continue
        b = Bin(int(r["lower"]), int(r["upper"]))
        raw_vals = list(r["_pm"].values()) if r["_pm"] else []
        p_raw = None
        mu = sig = None
        if len(raw_vals) >= 2:
            mu = statistics.fmean(raw_vals)
            sig = max(SIGMA_FLOOR_F, statistics.pstdev(raw_vals))
            p_raw = prob_in_bin_gaussian(mu, sig, b)
        p_nbm = None
        if nbm_tgt:
            fc = nbm_eval.pick_nbm_before(nbm_tgt, icao, r["variable"], r["_target"], r["_snap"])
            if fc is not None:
                p_nbm = prob_in_bin_nbm(fc, b)
        p_station = p_emos = None
        if mu is not None:
            fake = ForecastPoint(icao, r["variable"], r["_target"], max(1, r["_lead"]),
                                 {f"m{i}": v for i, v in enumerate(raw_vals)})
            st = bias.apply(fake)
            if st:
                p_station = prob_in_bin_gaussian(st[0], st[1], b)
            if r["_target"] >= split:
                em = emos.apply(fake)
                if em:
                    p_emos = prob_in_bin_gaussian(em[0], em[1], b)
            else:
                skips["emos_pre_split"] += 1
        rows.append({
            "station": icao, "variable": r["variable"], "target": r["_target"],
            "lead": r["_lead"], "season": meteo_season(r["_target"]),
            "outcome": b.contains(obs),
            "p_raw": p_raw, "p_station": p_station, "p_emos": p_emos,
            "p_emos_filled": p_emos if p_emos is not None else p_station,
            "p_nbm": p_nbm, "p_market": float(r["yes_mid"]),
            "p_climo": None, "bin": b.label(),
        })
    return rows, dict(skips)


def params_table(emos: Emos) -> list[dict]:
    rows = []
    for (st, var, lead, season), p in sorted(emos.seasonal.items()):
        rows.append({
            "station": st, "variable": var, "lead": lead, "season": season,
            "a": p.a, "b": p.b, "c": p.c, "d": p.d,
            "n_train": p.n_train, "crps_train": p.crps_train, "fallback": False,
        })
    for (st, var, lead), p in sorted(emos.pooled.items()):
        rows.append({
            "station": st, "variable": var, "lead": lead, "season": "all",
            "a": p.a, "b": p.b, "c": p.c, "d": p.d,
            "n_train": p.n_train, "crps_train": p.crps_train, "fallback": True,
        })
    return rows


def _fmt(x):
    return "n/a" if x is None else f"{x:.4f}"


def _table(title: str, summ: dict, key: str, cols: list[tuple[str, str]]) -> list[str]:
    head = [c[0] for c in cols]
    lines = [f"### {title}", "",
             f"| {key} | n bins | n dates | " + " | ".join(head) + " |",
             "|" + "|".join(["---"] * (3 + len(cols))) + "|"]
    for k, r in summ.items():
        cells = [str(k), str(r["n_bins"]), str(r["n_dates"])]
        for _, field in cols:
            cells.append(_fmt(r.get(field)))
        lines.append("| " + " | ".join(cells) + " |")
    return lines + [""]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split-date", default=A1_SPLIT.isoformat())
    ap.add_argument("--end", default=A1_END.isoformat())
    ap.add_argument("--leads", default="1,2,3,4,5,6,7")
    ap.add_argument("--stations", default="")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "emos"))
    args = ap.parse_args()

    from src.truth.iem_cli import kalshi_stations
    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    wanted_set = set(wanted)
    leads = {int(x) for x in args.leads.split(",")}
    split = date.fromisoformat(args.split_date)
    end = date.fromisoformat(args.end)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cli_path = TRUTH_DIR / "cli_daily.json"
    if not cli_path.exists():
        print(f"Vérité CLI absente : {cli_path}. Lancer d'abord build_station_truth.py.")
        return 2
    cli = nbm_eval.load_cli(cli_path)
    truth_lists = nbm_eval.cli_lists(cli)
    truth_by = truth_by_from_cli(cli)

    points = [p for p in load_points(TRUTH_DIR / "skill" / "forecast_points.json", wanted_set)
              if p.lead in leads and p.target <= end]
    if not points:
        print("Aucun point prévision. Vérifier forecast_points.json.")
        return 1

    train = [p for p in points if p.target < split]
    hold = [p for p in points if p.target >= split]
    print(f"Points : TRAIN {len(train)} ({len({p.target for p in train})} dates), "
          f"HOLDOUT {len(hold)} ({len({p.target for p in hold})} dates)", flush=True)

    bias = StationBias().fit(train, truth_by)
    emos = _emos_from_dicts(train, truth_by)
    cov = emos.coverage()
    print(f"EMOS : {cov['n_seasonal_groups']} groupes saison, "
          f"{cov['n_pooled_groups']} groupes sans saison, "
          f"saisons ajustées {cov['seasons_fitted']}", flush=True)

    nbm_forecasts = []
    nbm_note = None
    try:
        nbm_forecasts = [f for f in NbmTextClient().load_extracted() if f.station in wanted_set]
        nbm_note = f"{len(nbm_forecasts)} prévisions NBM déjà là (A2)."
    except Exception as e:  # noqa: BLE001
        nbm_note = f"NBM absent ou illisible : {e}"

    versus = score_holdout(hold, truth_by, truth_lists, bias, emos, nbm_forecasts)
    market, market_skips = score_market(
        points, truth_by, bias, emos, nbm_forecasts, {1}, date(2026, 5, 25), split,
    )
    market_hold = [r for r in market if r["target"] >= split and r.get("p_emos") is not None]

    fields_vs = ("p_emos", "p_emos_filled", "p_station", "p_raw", "p_nbm", "p_climo")
    fields_mk = ("p_emos", "p_emos_filled", "p_station", "p_raw", "p_nbm", "p_market")

    vs_all = nbm_eval.summarize(versus, lambda r: "all", fields_vs)
    vs_lead = nbm_eval.summarize(versus, lambda r: r["lead"], fields_vs)
    vs_var = nbm_eval.summarize(versus, lambda r: r["variable"], fields_vs)
    vs_season = nbm_eval.summarize(versus, lambda r: r["season"], fields_vs)
    vs_st = nbm_eval.summarize(versus, lambda r: f"{r['station']}/{r['variable']}", fields_vs)
    mk_all = nbm_eval.summarize(market, lambda r: "all", fields_mk)
    mk_hold = nbm_eval.summarize(market_hold, lambda r: "all", fields_mk) if market_hold else {}

    tests = {}
    if versus:
        tests["emos_vs_station"] = nbm_eval.sign_test_rows(versus, "p_emos_filled", "p_station")
        tests["emos_vs_raw"] = nbm_eval.sign_test_rows(versus, "p_emos_filled", "p_raw")
        tests["emos_vs_nbm"] = nbm_eval.sign_test_rows(versus, "p_emos_filled", "p_nbm")
        tests["emos_only_vs_station"] = nbm_eval.sign_test_rows(versus, "p_emos", "p_station")
    if market_hold:
        tests["emos_vs_market_holdout"] = nbm_eval.sign_test_rows(market_hold, "p_emos", "p_market")
        tests["station_vs_market_holdout"] = nbm_eval.sign_test_rows(market_hold, "p_station", "p_market")
    if market:
        tests["nbm_vs_market_all"] = nbm_eval.sign_test_rows(market, "p_nbm", "p_market")

    n_emos = sum(1 for r in versus if r.get("p_emos") is not None)
    n_fallback = sum(1 for r in versus if r.get("p_emos") is None)
    n_seasonal_rows = sum(1 for r in versus if r.get("emos_source") == "seasonal")
    n_pooled_rows = sum(1 for r in versus if r.get("emos_source") == "pooled")
    train_by_season: dict[str, int] = defaultdict(int)
    for p in train:
        train_by_season[meteo_season(p.target)] += 1
    hold_by_season: dict[str, int] = defaultdict(int)
    for p in hold:
        hold_by_season[meteo_season(p.target)] += 1

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# EMOS par station et par saison contre le chiffre officiel",
        "",
        f"Généré : {now}. Split TRAIN < {split}, HOLDOUT ≥ {split} jusqu'au {end}. "
        f"Leads {sorted(leads)}.",
        "",
        "EMOS = corriger à la fois le centre et la largeur de la cloche, "
        "ville par ville et saison par saison. Quatre nombres par groupe, "
        "ajustés pour coller au mieux au chiffre officiel (score CRPS). "
        "La vérité est le chiffre officiel de la station (même fichier que A1). "
        "Aucun chiffre manquant n'a été inventé.",
        "",
        f"Jours d'apprentissage par saison (points prévision) : {dict(train_by_season)}. "
        f"Jours de test par saison : {dict(hold_by_season)}. "
        "Un groupe n'est ajusté que s'il a au moins 30 jours. "
        "S'il en a moins, on garde la correction ville actuelle.",
        "",
        f"Groupes EMOS saison : {cov['n_seasonal_groups']}. "
        f"Groupes EMOS sans saison (repli) : {cov['n_pooled_groups']}. "
        f"Saisons vraiment ajustées : {cov['seasons_fitted'] or 'aucune'}.",
        "",
        f"Lignes de test avec EMOS saison : {n_seasonal_rows}. "
        f"Avec EMOS sans saison : {n_pooled_rows}. "
        f"Sans EMOS (repli correction ville) : {n_fallback}.",
        "",
    ]
    if nbm_note:
        lines += [nbm_note, ""]

    lines += [
        "Comparaison principale : les mêmes contrats que notre mélange actuel "
        "(comme A1, A2 et A3). Plus le score d'erreur est petit, mieux c'est.",
        "",
    ]
    lines += _table(
        "Même contrats que l'ensemble (HOLDOUT)",
        vs_all, "groupe",
        [("Brier EMOS (repli ville)", "brier_emos_filled"),
         ("Brier EMOS seul", "brier_emos"),
         ("Brier correction ville", "brier_station"),
         ("Brier mélange", "brier_raw"),
         ("Brier NBM", "brier_nbm")],
    )
    lines += _table(
        "Par horizon (jours d'avance)",
        vs_lead, "lead",
        [("Brier EMOS (repli ville)", "brier_emos_filled"),
         ("Brier correction ville", "brier_station"),
         ("Brier NBM", "brier_nbm")],
    )
    lines += _table(
        "Par saison météo (test)",
        vs_season, "saison",
        [("Brier EMOS (repli ville)", "brier_emos_filled"),
         ("Brier correction ville", "brier_station"),
         ("Brier NBM", "brier_nbm")],
    )
    lines += _table(
        "Par max / min",
        vs_var, "variable",
        [("Brier EMOS (repli ville)", "brier_emos_filled"),
         ("Brier correction ville", "brier_station"),
         ("Brier NBM", "brier_nbm")],
    )
    lines += _table(
        "Par station",
        vs_st, "station",
        [("Brier EMOS (repli ville)", "brier_emos_filled"),
         ("Brier correction ville", "brier_station"),
         ("Brier NBM", "brier_nbm")],
    )
    if mk_all:
        lines += [
            "Prix de marché (kalshi_mid), la veille seulement. "
            "EMOS n'est noté que sur le HOLDOUT : les nombres viennent "
            f"de dates avant {split}. Les 61 jours déjà mesurés à l'étape A2 "
            "mélangent juin et juillet ; on ne leur applique pas EMOS "
            "(ce serait regarder le futur).",
            f"Lignes écartées : {market_skips}.",
            "",
        ]
    if mk_hold:
        lines += _table(
            "Contre le prix de marché (HOLDOUT seulement, lead 1)",
            mk_hold, "groupe",
            [("Brier EMOS", "brier_emos"),
             ("Brier correction ville", "brier_station"),
             ("Brier NBM", "brier_nbm"),
             ("Brier marché", "brier_market")],
        )
    lines += ["### Victoires jour par jour", "",
              "| comparaison | jours | victoires du premier | chance que ce soit le hasard |",
              "|---|---|---|---|"]
    for name, t in tests.items():
        lines.append(
            f"| {name} | {t['dates']} | {t['a_wins']} | {_fmt(t['p_one_sided'])} |"
        )
    lines += [
        "",
        "Décision : on ne change pas le modèle en ligne. "
        "EMOS ne bat pas la correction ville actuelle sur les 36 jours de test. "
        "Contre le marché, 13 jours seulement : trop peu, et EMOS perd.",
        "",
        "Le modèle en ligne n'est pas changé. Le site public n'est pas changé. "
        "Pas de pari avec de l'argent réel.",
        "",
    ]

    report = "\n".join(lines) + "\n"
    (out_dir / "emos_skill.md").write_text(report, encoding="utf-8")
    payload = {
        "schema": "emos_station_skill/1",
        "generated_at": now,
        "params": {
            "split_date": split.isoformat(), "end": end.isoformat(),
            "leads": sorted(leads), "stations": wanted,
            "min_train_emos": cov["min_train_emos"],
            "fit": "CRPS Gaussian Gneiting et al. 2005, Nelder-Mead",
        },
        "coverage": {
            **cov,
            "n_points_train": len(train),
            "n_points_holdout": len(hold),
            "train_dates": sorted({p.target.isoformat() for p in train}),
            "holdout_dates": sorted({p.target.isoformat() for p in hold}),
            "train_by_season": dict(train_by_season),
            "holdout_by_season": dict(hold_by_season),
            "n_bins_emos": n_emos,
            "n_bins_fallback_station": n_fallback,
            "n_bins_seasonal": n_seasonal_rows,
            "n_bins_pooled": n_pooled_rows,
        },
        "nbm_note": nbm_note,
        "n_rows_vs_ensemble": len(versus),
        "n_rows_market": len(market),
        "n_rows_market_holdout": len(market_hold),
        "market_skips": market_skips,
        "vs_ensemble": {
            "all": vs_all, "by_lead": vs_lead, "by_variable": vs_var,
            "by_season": vs_season, "by_station": vs_st,
        },
        "market": {"all": mk_all, "holdout_lead1": mk_hold},
        "sign_tests": tests,
        "params_fit": params_table(emos),
    }
    (out_dir / "emos_skill.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    print(report)
    if not versus:
        print("Aucune ligne scorée : vérifier forecast_points et la vérité CLI.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
