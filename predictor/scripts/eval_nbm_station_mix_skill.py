"""eval_nbm_station_mix_skill.py — mélanger NBM et la correction ville (hors ligne).

FR : Sur les contrats où NBM et le mélange déjà corrigé ville par ville
existent tous les deux, on combine les deux chances. Deux mélanges
honnêtes, sans regarder le futur :

  moyenne   la moitié de chaque chance (poids fixe 0,5 / 0,5)
  ajusté    un seul nombre appris avant le 3 août 2026, comme B3 :
            P = correction ville + w · (NBM − correction ville)
            w = 0 garde la correction ville. w = 1 garde NBM.

Mêmes fenêtres que A2 : 36 jours de skill (3 août au 7 septembre 2026)
contre le chiffre officiel de la station ; la veille contre le prix
quand un milieu Kalshi existe (fenêtre A2 de 61 jours si on peut
la reconstruire).

Le champion en ligne n'est pas touché. On mesure seulement.

EN : Honest mix of NBM and the city-corrected blend. Fixed 50/50 and
one TRAIN-only weight. Same A2 windows. Does not switch the live champion.

Usage:
    python scripts/eval_nbm_station_mix_skill.py
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

import eval_emos_skill as emos_eval  # noqa: E402
import eval_nbm_skill as nbm_eval  # noqa: E402
import eval_station_bias_market as pit  # noqa: E402
from src.forecast.nbm_client import NbmTextClient  # noqa: E402
from src.forecast.nbm_prob import prob_in_bin_nbm  # noqa: E402
from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, kalshi_stations  # noqa: E402
from src.truth.skill import SIGMA_FLOOR_F, ForecastPoint, StationBias  # noqa: E402
from src.truth.stacking import (  # noqa: E402
    MIN_TRAIN_STACK, apply_stack, clip_prob, residual_weight,
)
from src.truth.synthetic_bins import Bin, kalshi_style_bins, prob_in_bin_gaussian  # noqa: E402

A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)
A2_MARKET_START = date(2026, 5, 25)
MIN_MARKET_DAYS = 30


def mix_average(p_nbm: float, p_station: float) -> float:
    return clip_prob(0.5 * float(p_nbm) + 0.5 * float(p_station))


def attach_mixes(rows: list[dict], weight: float | None) -> None:
    for r in rows:
        if r.get("p_nbm") is None or r.get("p_station") is None:
            r["p_avg"] = None
            r["p_fit"] = None
            continue
        r["p_avg"] = mix_average(r["p_nbm"], r["p_station"])
        r["p_fit"] = (
            apply_stack(r["p_station"], r["p_nbm"], weight)
            if weight is not None else None
        )


def _ready(rows: list[dict], *fields: str) -> list[dict]:
    return [r for r in rows if all(r.get(f) is not None for f in fields)]


def _ys(rows: list[dict]) -> list[float]:
    return [1.0 if r["outcome"] else 0.0 for r in rows]


def score_ensemble_bins(
    forecasts: list,
    cli: dict,
    points: list[ForecastPoint],
    bias: StationBias,
    leads: set[int],
    start: date,
    end: date,
) -> list[dict]:
    """Mêmes bins que A2 (centrées sur la moyenne des modèles).

    Une ligne n'existe que si NBM a une chance pour ce contrat.
    La correction ville peut manquer (pas assez de jours d'apprentissage).
    """
    idx = nbm_eval.index_forecasts(forecasts) if forecasts else {}
    rows = []
    for p in points:
        if p.target < start or p.target > end or p.lead not in leads:
            continue
        t = cli.get((p.station, p.target))
        obs = nbm_eval.truth_value(t, p.variable) if t else None
        if obs is None:
            continue
        fc = nbm_eval.pick_nbm(idx, p.station, p.variable, p.target, p.lead) if idx else None
        if fc is None:
            continue
        mu, sig = p.mean, max(SIGMA_FLOOR_F, p.spread)
        st = bias.apply(p)
        for b in kalshi_style_bins(mu, n_central=6):
            if not b.is_central:
                continue
            p_nbm = prob_in_bin_nbm(fc, b)
            if p_nbm is None:
                continue
            rows.append({
                "station": p.station, "variable": p.variable,
                "target": p.target, "lead": p.lead,
                "outcome": b.contains(obs),
                "p_nbm": p_nbm,
                "p_raw": prob_in_bin_gaussian(mu, sig, b),
                "p_station": (
                    prob_in_bin_gaussian(st[0], st[1], b) if st else None
                ),
                "p_market": None, "bin": b.label(),
            })
    return rows


def score_market_mix(
    forecasts: list,
    cli: dict,
    bias_frozen: StationBias,
    pit_bias: pit.PointInTimeBias,
    leads: set[int],
    min_date: date,
) -> tuple[list[dict], dict]:
    """Même lecture des captures que A2, plus les deux corrections ville.

    p_station : correction figée apprise avant le split (fuite si la
    cible est dans l'apprentissage). p_station_causal : seulement les
    jours déjà passés à l'heure de la capture. Aucun prix n'est inventé.
    """
    nbm_tgt = nbm_eval.index_by_target(forecasts) if forecasts else {}
    seen: dict[tuple, dict] = {}
    skips: dict[str, int] = defaultdict(int)
    for f in sorted((ROOT / "data" / "predictions").glob("forward_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
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
            snap = datetime.strptime(
                r["snapshot_at"], "%Y%m%dT%H%M%SZ"
            ).replace(tzinfo=timezone.utc)
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
        t = cli.get((icao, r["_target"]))
        obs = nbm_eval.truth_value(t, r["variable"]) if t else None
        if obs is None:
            skips["no_cli_truth"] += 1
            continue
        fc = nbm_eval.pick_nbm_before(
            nbm_tgt, icao, r["variable"], r["_target"], r["_snap"]
        ) if nbm_tgt else None
        if fc is None:
            skips["no_nbm"] += 1
            continue
        b = Bin(int(r["lower"]), int(r["upper"]))
        p_nbm = prob_in_bin_nbm(fc, b)
        if p_nbm is None:
            skips["no_nbm_prob"] += 1
            continue
        raw_vals = list(r["_pm"].values()) if r["_pm"] else []
        p_raw = None
        mu = None
        if len(raw_vals) >= 2:
            mu = statistics.fmean(raw_vals)
            sig = max(SIGMA_FLOOR_F, statistics.pstdev(raw_vals))
            p_raw = prob_in_bin_gaussian(mu, sig, b)
        p_station = p_station_causal = None
        if mu is not None:
            fake = ForecastPoint(
                icao, r["variable"], r["_target"], max(1, r["_lead"]),
                {f"m{i}": v for i, v in enumerate(raw_vals)},
            )
            st = bias_frozen.apply(fake)
            if st:
                p_station = prob_in_bin_gaussian(st[0], st[1], b)
            causal = pit_bias.get(icao, r["variable"], r["_lead"], r["_snap"].date())
            if causal:
                p_station_causal = prob_in_bin_gaussian(mu + causal[0], causal[1], b)
        rows.append({
            "station": icao, "variable": r["variable"],
            "target": r["_target"], "lead": r["_lead"],
            "outcome": b.contains(obs),
            "p_nbm": p_nbm, "p_raw": p_raw,
            "p_station": p_station,
            "p_station_causal": p_station_causal,
            "p_market": float(r["yes_mid"]),
            "bin": b.label(),
        })
    return rows, dict(skips)


def _fmt(x):
    return "n/a" if x is None else f"{x:.4f}"


def _table(title: str, summ: dict, key: str, cols: list[tuple[str, str]]) -> list[str]:
    head = [c[0] for c in cols]
    lines = [
        f"### {title}", "",
        f"| {key} | n bins | n dates | " + " | ".join(head) + " |",
        "|" + "|".join(["---"] * (3 + len(cols))) + "|",
    ]
    for k, r in summ.items():
        cells = [str(k), str(r["n_bins"]), str(r["n_dates"])]
        for _, field in cols:
            cells.append(_fmt(r.get(field)))
        lines.append("| " + " | ".join(cells) + " |")
    return lines + [""]


def _brier_of(summ: dict, field: str):
    block = summ.get("all") or {}
    return block.get(field)


def decide_promote(
    n_dates: int,
    b_mix,
    b_station,
    b_market,
    mix_name: str,
) -> tuple[bool, str]:
    """La règle est écrite. Cette étape ne promeut jamais."""
    if n_dates < MIN_MARKET_DAYS:
        return False, (
            f"Pas de promotion : {n_dates} jours de marché avec le mélange "
            f"({mix_name}), il en faut {MIN_MARKET_DAYS}."
        )
    if b_mix is None:
        return False, "Pas de promotion : pas de score pour le mélange."
    beats_mkt = b_market is not None and b_mix < b_market
    beats_st = b_station is not None and b_mix < b_station
    if beats_mkt and beats_st:
        return False, (
            f"Le mélange ({mix_name}) bat le marché et la correction ville "
            f"sur {n_dates} jours. Cette étape ne promeut pas : à relire."
        )
    if beats_mkt:
        return False, (
            f"Le mélange ({mix_name}) bat le marché sur {n_dates} jours, "
            "mais pas la correction ville. On ne promeut pas."
        )
    if beats_st:
        return False, (
            f"Le mélange ({mix_name}) bat la correction ville sur {n_dates} "
            "jours, mais pas le marché. On ne promeut pas."
        )
    return False, (
        f"Assez de jours ({n_dates}), mais le mélange ({mix_name}) "
        "ne bat ni le marché ni la correction ville."
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--split-date", default=A1_SPLIT.isoformat())
    ap.add_argument("--end", default=A1_END.isoformat())
    ap.add_argument("--leads", default="1,2,3,4,5,6,7")
    ap.add_argument("--stations", default="")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "nbm_mix"))
    args = ap.parse_args()

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
    truth_by = emos_eval.truth_by_from_cli(cli)

    points = [
        p for p in emos_eval.load_points(TRUTH_DIR / "skill" / "forecast_points.json", wanted_set)
        if p.lead in leads and p.target <= end
    ]
    if not points:
        print("Aucun point prévision. Vérifier forecast_points.json.")
        return 1

    train_pts = [p for p in points if p.target < split]
    hold_pts = [p for p in points if p.target >= split]
    print(
        f"Points : TRAIN {len(train_pts)} ({len({p.target for p in train_pts})} dates), "
        f"HOLDOUT {len(hold_pts)} ({len({p.target for p in hold_pts})} dates)",
        flush=True,
    )
    bias = StationBias().fit(train_pts, truth_by)

    nbm_forecasts = []
    nbm_note = None
    try:
        nbm_forecasts = [f for f in NbmTextClient().load_extracted() if f.station in wanted_set]
        nbm_note = f"{len(nbm_forecasts)} prévisions NBM déjà là (A2)."
    except Exception as e:  # noqa: BLE001
        nbm_note = f"NBM absent ou illisible : {e}"
    if not nbm_forecasts:
        print("Aucune prévision NBM en cache. Lancer d'abord eval_nbm_skill.py.")
        return 1

    train_rows = score_ensemble_bins(
        nbm_forecasts, cli, train_pts, bias, leads, date(2026, 5, 12), split - timedelta(days=1),
    )
    hold_rows = score_ensemble_bins(
        nbm_forecasts, cli, hold_pts, bias, leads, split, end,
    )
    hold_both = _ready(hold_rows, "p_nbm", "p_station")
    train_both = _ready(train_rows, "p_nbm", "p_station")

    weight = residual_weight(
        [r["p_nbm"] for r in train_both],
        [r["p_station"] for r in train_both],
        _ys(train_both),
    )
    attach_mixes(train_both, weight)
    attach_mixes(hold_both, weight)

    fields_vs = ("p_avg", "p_fit", "p_station", "p_nbm", "p_raw")
    vs_all = nbm_eval.summarize(hold_both, lambda r: "all", fields_vs)
    vs_lead = nbm_eval.summarize(hold_both, lambda r: r["lead"], fields_vs)
    vs_var = nbm_eval.summarize(hold_both, lambda r: r["variable"], fields_vs)
    vs_train = nbm_eval.summarize(train_both, lambda r: "all", fields_vs)

    tests = {}
    if hold_both:
        tests["avg_vs_station"] = nbm_eval.sign_test_rows(hold_both, "p_avg", "p_station")
        tests["avg_vs_nbm"] = nbm_eval.sign_test_rows(hold_both, "p_avg", "p_nbm")
        tests["avg_vs_raw"] = nbm_eval.sign_test_rows(hold_both, "p_avg", "p_raw")
        tests["nbm_vs_station"] = nbm_eval.sign_test_rows(hold_both, "p_nbm", "p_station")
        tests["station_vs_raw"] = nbm_eval.sign_test_rows(hold_both, "p_station", "p_raw")
        if weight is not None:
            tests["fit_vs_station"] = nbm_eval.sign_test_rows(hold_both, "p_fit", "p_station")
            tests["fit_vs_nbm"] = nbm_eval.sign_test_rows(hold_both, "p_fit", "p_nbm")
            tests["fit_vs_avg"] = nbm_eval.sign_test_rows(hold_both, "p_fit", "p_avg")

    # Marché : même règle de capture que A2, plus les corrections ville.
    pit_points = []
    fp_path = TRUTH_DIR / "skill" / "forecast_points.json"
    if fp_path.exists():
        raw_pts = json.loads(fp_path.read_text(encoding="utf-8"))
        for p in raw_pts:
            if p["station"] not in wanted_set:
                continue
            p = dict(p)
            p["_target"] = date.fromisoformat(p["target"])
            p["_mean"] = statistics.fmean(p["per_model"].values())
            pit_points.append(p)
    pit_bias = pit.PointInTimeBias(pit_points, cli)

    market, market_skips = score_market_mix(
        nbm_forecasts, cli, bias, pit_bias, {1}, A2_MARKET_START,
    )
    market_a2 = _ready(market, "p_nbm", "p_market")
    market_causal = []
    for r in market:
        if r.get("p_nbm") is None or r.get("p_station_causal") is None or r.get("p_market") is None:
            continue
        cr = dict(r)
        cr["p_station"] = r["p_station_causal"]
        market_causal.append(cr)
    attach_mixes(market_causal, None)  # moyenne seulement : le poids ajusté vient du futur

    market_hold = []
    for r in market:
        if r["target"] < split:
            continue
        if r.get("p_nbm") is None or r.get("p_station") is None or r.get("p_market") is None:
            continue
        market_hold.append(r)
    attach_mixes(market_hold, weight)

    fields_mk = ("p_avg", "p_fit", "p_station", "p_nbm", "p_raw", "p_market")
    fields_a2 = ("p_nbm", "p_raw", "p_market")
    mk_a2 = nbm_eval.summarize(market_a2, lambda r: "all", fields_a2)
    mk_causal = nbm_eval.summarize(market_causal, lambda r: "all", fields_mk)
    mk_hold = nbm_eval.summarize(market_hold, lambda r: "all", fields_mk) if market_hold else {}

    if market_causal:
        tests["avg_vs_market_a2"] = nbm_eval.sign_test_rows(market_causal, "p_avg", "p_market")
        tests["avg_vs_station_a2"] = nbm_eval.sign_test_rows(market_causal, "p_avg", "p_station")
        tests["avg_vs_nbm_a2"] = nbm_eval.sign_test_rows(market_causal, "p_avg", "p_nbm")
        tests["nbm_vs_market_a2"] = nbm_eval.sign_test_rows(market_causal, "p_nbm", "p_market")
        tests["station_vs_market_a2"] = nbm_eval.sign_test_rows(market_causal, "p_station", "p_market")
    if market_a2:
        tests["nbm_vs_market_a2_all"] = nbm_eval.sign_test_rows(market_a2, "p_nbm", "p_market")
    if market_hold:
        tests["avg_vs_market_hold"] = nbm_eval.sign_test_rows(market_hold, "p_avg", "p_market")
        tests["station_vs_market_hold"] = nbm_eval.sign_test_rows(market_hold, "p_station", "p_market")
        if weight is not None:
            tests["fit_vs_market_hold"] = nbm_eval.sign_test_rows(market_hold, "p_fit", "p_market")
            tests["fit_vs_station_hold"] = nbm_eval.sign_test_rows(market_hold, "p_fit", "p_station")

    n_a2_dates = len({r["target"] for r in market_a2})
    n_causal_dates = len({r["target"] for r in market_causal})
    n_hold_mkt_dates = len({r["target"] for r in market_hold})

    b_avg_causal = _brier_of(mk_causal, "brier_avg")
    b_st_causal = _brier_of(mk_causal, "brier_station")
    b_mkt_causal = _brier_of(mk_causal, "brier_market")
    promote, promote_reason = decide_promote(
        n_causal_dates, b_avg_causal, b_st_causal, b_mkt_causal, "moyenne",
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Mélanger NBM et la correction ville",
        "",
        f"Généré : {now}. Split TRAIN < {split}, HOLDOUT ≥ {split} jusqu'au {end}. "
        f"Leads {sorted(leads)}.",
        "",
        "On ne garde que les contrats où NBM et la correction ville existent "
        "tous les deux. Aucun chiffre manquant n'a été inventé. "
        "La vérité est le chiffre officiel de la station (même fichier que A1).",
        "",
        f"Nombre appris w = {_fmt(weight)}. "
        "w = 0 voudrait dire : garder la correction ville. "
        "w = 1 voudrait dire : garder NBM. "
        "La moyenne simple est 0,5 / 0,5, sans apprentissage.",
        "",
        f"Lignes d'apprentissage (NBM + correction ville) : {len(train_both)} "
        f"({len({r['target'] for r in train_both})} jours). "
        f"Lignes de test skill : {len(hold_both)} "
        f"({len({r['target'] for r in hold_both})} jours). "
        f"Lignes skill avec NBM mais sans correction ville : "
        f"{len(hold_rows) - len(hold_both)}.",
        "",
    ]
    if nbm_note:
        lines += [nbm_note, ""]
    if weight is None:
        lines += [
            f"Pas assez de lignes d'apprentissage avec les deux sources "
            f"({len(train_both)} < {MIN_TRAIN_STACK}) : le mélange ajusté "
            "n'est pas calculé. La moyenne simple reste.",
            "",
        ]

    lines += [
        "Comparaison principale : les mêmes contrats que A2, 36 jours, "
        "seulement là où les deux sources existent. "
        "Plus le score d'erreur est petit, mieux c'est.",
        "",
    ]
    if vs_all:
        lines += _table(
            "Même contrats que l'ensemble (HOLDOUT, NBM + correction ville)",
            vs_all, "groupe",
            [("Brier moyenne", "brier_avg"),
             ("Brier ajusté", "brier_fit"),
             ("Brier correction ville", "brier_station"),
             ("Brier NBM", "brier_nbm"),
             ("Brier mélange brut", "brier_raw")],
        )
    if vs_train:
        lines += _table(
            "Apprentissage (même règle, avant le split)",
            vs_train, "groupe",
            [("Brier moyenne", "brier_avg"),
             ("Brier ajusté", "brier_fit"),
             ("Brier correction ville", "brier_station"),
             ("Brier NBM", "brier_nbm")],
        )
    if vs_lead:
        lines += _table(
            "Par horizon (jours d'avance)",
            vs_lead, "lead",
            [("Brier moyenne", "brier_avg"),
             ("Brier ajusté", "brier_fit"),
             ("Brier correction ville", "brier_station"),
             ("Brier NBM", "brier_nbm")],
        )
    if vs_var:
        lines += _table(
            "Par max / min",
            vs_var, "variable",
            [("Brier moyenne", "brier_avg"),
             ("Brier ajusté", "brier_fit"),
             ("Brier correction ville", "brier_station"),
             ("Brier NBM", "brier_nbm")],
        )

    lines += [
        "Prix de marché (kalshi_mid), la veille seulement. "
        "La fenêtre A2 compte les jours avec un prix et un bulletin NBM. "
        "Le mélange n'est noté que si la correction ville existe aussi, "
        "sans regarder le futur : on apprend le biais seulement sur les "
        "jours déjà passés à l'heure de la capture.",
        f"Lignes écartées à la lecture des captures : {market_skips}.",
        f"Fenêtre A2 reconstruite : {len(market_a2)} contrats, {n_a2_dates} jours.",
        f"Dont avec correction ville honnête : {len(market_causal)} contrats, "
        f"{n_causal_dates} jours.",
        f"HOLDOUT seulement (correction figée + poids appris) : "
        f"{len(market_hold)} contrats, {n_hold_mkt_dates} jours.",
        "",
    ]
    if mk_a2:
        lines += _table(
            "Contre le prix, fenêtre A2 (NBM + prix, comme A2)",
            mk_a2, "groupe",
            [("Brier NBM", "brier_nbm"),
             ("Brier mélange brut", "brier_raw"),
             ("Brier marché", "brier_market")],
        )
    if mk_causal:
        lines += _table(
            "Contre le prix, jours avec NBM + correction ville honnête",
            mk_causal, "groupe",
            [("Brier moyenne", "brier_avg"),
             ("Brier correction ville", "brier_station"),
             ("Brier NBM", "brier_nbm"),
             ("Brier mélange brut", "brier_raw"),
             ("Brier marché", "brier_market")],
        )
    if mk_hold:
        lines += _table(
            "Contre le prix, HOLDOUT seulement (poids appris, correction figée)",
            mk_hold, "groupe",
            [("Brier moyenne", "brier_avg"),
             ("Brier ajusté", "brier_fit"),
             ("Brier correction ville", "brier_station"),
             ("Brier NBM", "brier_nbm"),
             ("Brier marché", "brier_market")],
        )

    lines += [
        "### Victoires jour par jour", "",
        "| comparaison | jours | victoires du premier | chance que ce soit le hasard |",
        "|---|---|---|---|",
    ]
    for name, t in tests.items():
        lines.append(
            f"| {name} | {t['dates']} | {t['a_wins']} | {_fmt(t['p_one_sided'])} |"
        )
    lines += [
        "",
        f"Décision : on ne change pas le modèle en ligne. {promote_reason}",
        "",
        "Le modèle en ligne n'est pas changé. Le site public n'est pas changé. "
        "Pas de pari avec de l'argent réel.",
        "",
    ]

    report = "\n".join(lines) + "\n"
    (out_dir / "nbm_mix_skill.md").write_text(report, encoding="utf-8")
    payload = {
        "schema": "nbm_station_mix_skill/1",
        "generated_at": now,
        "params": {
            "split_date": split.isoformat(),
            "end": end.isoformat(),
            "leads": sorted(leads),
            "stations": wanted,
            "min_train_stack": MIN_TRAIN_STACK,
            "min_market_days": MIN_MARKET_DAYS,
            "mix_average": "0.5 * nbm + 0.5 * station_bias",
            "mix_fit": "station + w * (nbm - station), w from TRAIN < split",
            "market_station": (
                "point-in-time bias (targets < capture date) on the A2-style "
                "window; frozen TRAIN bias only on HOLDOUT market rows"
            ),
        },
        "weight": weight,
        "nbm_note": nbm_note,
        "n_rows_train": len(train_both),
        "n_rows_holdout": len(hold_both),
        "n_rows_holdout_nbm_only": len(hold_rows) - len(hold_both),
        "n_dates_train": len({r["target"].isoformat() for r in train_both}),
        "n_dates_holdout": len({r["target"].isoformat() for r in hold_both}),
        "n_rows_market_a2": len(market_a2),
        "n_dates_market_a2": n_a2_dates,
        "n_rows_market_causal": len(market_causal),
        "n_dates_market_causal": n_causal_dates,
        "n_rows_market_holdout": len(market_hold),
        "n_dates_market_holdout": n_hold_mkt_dates,
        "train_dates": sorted({r["target"].isoformat() for r in train_both}),
        "holdout_dates": sorted({r["target"].isoformat() for r in hold_both}),
        "market_a2_dates": sorted({r["target"].isoformat() for r in market_a2}),
        "market_causal_dates": sorted({r["target"].isoformat() for r in market_causal}),
        "market_holdout_dates": sorted({r["target"].isoformat() for r in market_hold}),
        "market_skips": market_skips,
        "vs_ensemble": {
            "all": vs_all, "by_lead": vs_lead, "by_variable": vs_var, "train": vs_train,
        },
        "market": {
            "a2_nbm_price": mk_a2,
            "causal_mix": mk_causal,
            "holdout_frozen": mk_hold,
        },
        "sign_tests": tests,
        "promote": promote,
        "promote_reason": promote_reason,
        "live_champion_changed": False,
    }
    (out_dir / "nbm_mix_skill.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    print(report)
    if not hold_both:
        print("Aucune ligne de test avec NBM et la correction ville.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
