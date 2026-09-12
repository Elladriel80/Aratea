"""eval_stacking_skill.py — combiner avec le prix (piste B3).

FR : Le prix kalshi_mid est le point de départ. On apprend un seul
nombre sur les jours avant le 3 août : quelle part de l'écart
(modèle − prix) garder. On note ensuite les jours de test où un
vrai prix et un modèle existent, mêmes contrats que A2/B1 (la veille).

Le modèle maison est le mélange déjà corrigé ville par ville (le
meilleur essai à ce jour). NBM est noté sur les mêmes lignes s'il
est là. Les prix viennent des captures live (yes_mid), jamais
inventés. Le carnet papier est lu pour vérifier que ces prix
existent aussi, pas pour en fabriquer.

Le champion en ligne n'est pas touché. On mesure seulement.

EN : Residual stack of city-corrected mix on real kalshi_mid. Same
A1 split and same day-before market rows as A2/B1. Does not switch
the live champion.

Usage:
    python scripts/eval_stacking_skill.py
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

import eval_emos_skill as emos_eval  # noqa: E402
import eval_nbm_skill as nbm_eval  # noqa: E402
from src.config import LEDGER_DIR  # noqa: E402
from src.forecast.nbm_client import NbmTextClient  # noqa: E402
from src.truth.iem_cli import TRUTH_DIR, kalshi_stations  # noqa: E402
from src.truth.skill import StationBias  # noqa: E402
from src.truth.stacking import (  # noqa: E402
    MIN_TRAIN_STACK, apply_stack, brier_mean, disagreement_count, ece, mae,
    residual_weight,
)

A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)
MIN_MARKET_DAYS = 30


def load_ledger_summary(path: Path) -> dict:
    """Lit le carnet papier. Aucun prix manquant n'est inventé."""
    empty = {
        "path": str(path),
        "n_rows": 0,
        "n_resolved": 0,
        "n_with_price": 0,
        "n_dates": 0,
        "date_min": None,
        "date_max": None,
        "present": path.exists(),
    }
    if not path.exists():
        return empty
    n_rows = n_resolved = n_price = 0
    dates: set[str] = set()
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            n_rows += 1
            if row.get("resolution") in ("yes", "no"):
                n_resolved += 1
            price = row.get("prob_market_implied") or row.get("entry_price")
            if price not in (None, ""):
                n_price += 1
            d = row.get("target_date")
            if d:
                dates.add(d)
    return {
        "path": str(path),
        "n_rows": n_rows,
        "n_resolved": n_resolved,
        "n_with_price": n_price,
        "n_dates": len(dates),
        "date_min": min(dates) if dates else None,
        "date_max": max(dates) if dates else None,
        "present": True,
    }


def _ys(rows: list[dict]) -> list[float]:
    return [1.0 if r["outcome"] else 0.0 for r in rows]


def _ready(rows: list[dict], *fields: str) -> list[dict]:
    return [r for r in rows if all(r.get(f) is not None for f in fields)]


def attach_stack(rows: list[dict], weight: float) -> None:
    for r in rows:
        if r.get("p_station") is None or r.get("p_market") is None:
            r["p_stack"] = None
            continue
        r["p_stack"] = apply_stack(r["p_market"], r["p_station"], weight)


def disagreement_block(rows: list[dict], threshold: float) -> dict:
    ready = _ready(rows, "p_station", "p_market")
    n_real, n_tot = disagreement_count(
        [r["p_station"] for r in ready],
        [r["p_market"] for r in ready],
        threshold,
    )
    real_rows = [r for r in ready if abs(r["p_station"] - r["p_market"]) > threshold]
    ys = _ys(real_rows)
    out = {
        "threshold": threshold,
        "n_rows": n_tot,
        "n_real": n_real,
        "share_real": (n_real / n_tot) if n_tot else None,
        "n_dates_real": len({r["target"] for r in real_rows}),
        "brier_station_real": brier_mean([r["p_station"] for r in real_rows], ys),
        "brier_market_real": brier_mean([r["p_market"] for r in real_rows], ys),
        "brier_stack_real": brier_mean(
            [r["p_stack"] for r in real_rows if r.get("p_stack") is not None],
            _ys([r for r in real_rows if r.get("p_stack") is not None]),
        ),
        "brier_nbm_real": brier_mean(
            [r["p_nbm"] for r in real_rows if r.get("p_nbm") is not None],
            _ys([r for r in real_rows if r.get("p_nbm") is not None]),
        ),
    }
    return out


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
    ap.add_argument("--stations", default="")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "stacking"))
    ap.add_argument("--ledger", default=str(LEDGER_DIR / "paper_bets.csv"))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    wanted_set = set(wanted)
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

    points = [p for p in emos_eval.load_points(TRUTH_DIR / "skill" / "forecast_points.json", wanted_set)
              if p.target <= end]
    if not points:
        print("Aucun point prévision. Vérifier forecast_points.json.")
        return 1

    train_pts = [p for p in points if p.target < split]
    print(f"Points TRAIN pour la correction ville : {len(train_pts)} "
          f"({len({p.target for p in train_pts})} dates)", flush=True)
    bias = StationBias().fit(train_pts, truth_by)

    nbm_forecasts = []
    nbm_note = None
    try:
        nbm_forecasts = [f for f in NbmTextClient().load_extracted() if f.station in wanted_set]
        nbm_note = f"{len(nbm_forecasts)} prévisions NBM déjà là (A2)."
    except Exception as e:  # noqa: BLE001
        nbm_note = f"NBM absent ou illisible : {e}"

    # Dummy EMOS : score_market n'applique EMOS que si target >= split
    # et emos.apply répond. On passe un EMOS vide : p_emos reste None,
    # p_station et p_market restent les champs utiles.
    from src.truth.emos import Emos
    empty_emos = Emos()

    market, market_skips = emos_eval.score_market(
        points, truth_by, bias, empty_emos, nbm_forecasts, {1}, date(2026, 5, 25), split,
    )
    train = _ready(market, "p_station", "p_market")
    train = [r for r in train if r["target"] < split]
    hold = _ready(market, "p_station", "p_market")
    hold = [r for r in hold if r["target"] >= split]
    hold_nbm = _ready(hold, "p_nbm")

    weight = residual_weight(
        [r["p_station"] for r in train],
        [r["p_market"] for r in train],
        _ys(train),
    )
    if weight is None:
        print(f"Pas assez de lignes d'apprentissage ({len(train)} < {MIN_TRAIN_STACK}) "
              "avec un prix et un modèle.")
        return 1
    attach_stack(train, weight)
    attach_stack(hold, weight)

    fields = ("p_stack", "p_station", "p_market", "p_nbm", "p_raw")
    mk_train = nbm_eval.summarize(train, lambda r: "all", fields)
    mk_hold = nbm_eval.summarize(hold, lambda r: "all", fields)
    mk_hold_var = nbm_eval.summarize(hold, lambda r: r["variable"], fields)
    mk_hold_nbm = nbm_eval.summarize(hold_nbm, lambda r: "all", fields) if hold_nbm else {}

    tests = {}
    if hold:
        tests["stack_vs_market"] = nbm_eval.sign_test_rows(hold, "p_stack", "p_market")
        tests["stack_vs_station"] = nbm_eval.sign_test_rows(hold, "p_stack", "p_station")
        tests["station_vs_market"] = nbm_eval.sign_test_rows(hold, "p_station", "p_market")
    if hold_nbm:
        tests["stack_vs_nbm"] = nbm_eval.sign_test_rows(hold_nbm, "p_stack", "p_nbm")
        tests["nbm_vs_market"] = nbm_eval.sign_test_rows(hold_nbm, "p_nbm", "p_market")

    ece_station_train = ece([r["p_station"] for r in train], _ys(train))
    ece_market_train = ece([r["p_market"] for r in train], _ys(train))
    threshold = ece_station_train
    if threshold is None:
        print("Impossible de mesurer l'erreur de calibration : TRAIN vide.")
        return 1

    disc_train = disagreement_block(train, threshold)
    disc_hold = disagreement_block(hold, threshold)
    ledger = load_ledger_summary(Path(args.ledger))

    n_hold_dates = len({r["target"] for r in hold})
    promote = False
    promote_reason = (
        f"Pas de promotion : {n_hold_dates} jours de test avec un prix, "
        f"il en faut {MIN_MARKET_DAYS}."
    )
    if n_hold_dates >= MIN_MARKET_DAYS and hold:
        b_stack = brier_mean([r["p_stack"] for r in hold], _ys(hold))
        b_mkt = brier_mean([r["p_market"] for r in hold], _ys(hold))
        b_st = brier_mean([r["p_station"] for r in hold], _ys(hold))
        if b_stack is not None and b_mkt is not None and b_stack < b_mkt:
            promote_reason = (
                "Le mélange avec le prix bat le prix seul sur assez de jours. "
                "À relire avant toute bascule."
            )
        elif b_stack is not None and b_st is not None and b_stack < b_st:
            promote_reason = (
                "Le mélange avec le prix bat la correction ville sur assez de jours. "
                "À relire avant toute bascule."
            )
        else:
            promote_reason = (
                "Assez de jours, mais le mélange avec le prix ne bat ni le marché "
                "ni la correction ville."
            )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Combiner avec le prix du marché",
        "",
        f"Généré : {now}. Apprentissage des poids < {split}. "
        f"Test ≥ {split}, la veille seulement, mêmes contrats que B1 "
        "quand un prix existe.",
        "",
        "On part du prix réel (kalshi_mid des captures, jamais inventé). "
        "On apprend un seul nombre : quelle part de l'écart entre le "
        "mélange déjà corrigé ville par ville et ce prix garder. "
        "La vérité est le chiffre officiel de la station (même fichier que A1).",
        "",
        f"Nombre appris w = {_fmt(weight)}. "
        "w = 0 voudrait dire : garder le prix. w = 1 voudrait dire : "
        "garder le mélange corrigé.",
        "",
        f"Lignes d'apprentissage (prix + modèle) : {len(train)} "
        f"({len({r['target'] for r in train})} jours). "
        f"Lignes de test : {len(hold)} ({n_hold_dates} jours). "
        f"Dont avec NBM : {len(hold_nbm)}.",
        "",
        f"Carnet papier : {ledger['n_rows']} lignes, "
        f"{ledger['n_with_price']} avec un prix, "
        f"{ledger['n_dates']} jours "
        f"({ledger['date_min']} → {ledger['date_max']}). "
        "Ces prix ne remplacent pas ceux des captures : ce n'est pas "
        "le même instant. On les lit pour confirmer que des prix réels "
        "existent. Le module d'apprentissage utilise déjà yes_mid "
        "des mêmes captures.",
        "",
        f"Erreur de calibration du mélange corrigé (apprentissage) : "
        f"{_fmt(ece_station_train)}. "
        f"Celle du prix : {_fmt(ece_market_train)}. "
        f"Écart moyen au vrai résultat, mélange corrigé : "
        f"{_fmt(mae([r['p_station'] for r in train], _ys(train)))}. "
        "Un désaccord n'est traité comme réel que s'il est plus grand "
        "que l'erreur de calibration du mélange.",
        "",
        f"Désaccords réels à l'apprentissage : {disc_train['n_real']} / "
        f"{disc_train['n_rows']} "
        f"({_fmt(disc_train['share_real'])}).",
        f"Désaccords réels au test : {disc_hold['n_real']} / "
        f"{disc_hold['n_rows']} "
        f"({_fmt(disc_hold['share_real'])}), "
        f"{disc_hold['n_dates_real']} jours.",
        "",
    ]
    if nbm_note:
        lines += [nbm_note, ""]
    shown_skips = {k: v for k, v in market_skips.items() if k != "emos_pre_split"}
    if shown_skips:
        lines += [f"Lignes écartées à la lecture des captures : {shown_skips}.", ""]

    lines += [
        "Comparaison principale : les mêmes contrats que A2/B1, "
        "la veille, seulement quand un prix et un modèle existent. "
        "Plus le score d'erreur est petit, mieux c'est.",
        "",
    ]
    if mk_hold:
        lines += _table(
            "Test, la veille (prix + mélange corrigé)",
            mk_hold, "groupe",
            [("Brier mélange+prix", "brier_stack"),
             ("Brier correction ville", "brier_station"),
             ("Brier marché", "brier_market"),
             ("Brier NBM", "brier_nbm"),
             ("Brier mélange brut", "brier_raw")],
        )
    if mk_train:
        lines += _table(
            "Apprentissage (même règle, avant le split)",
            mk_train, "groupe",
            [("Brier mélange+prix", "brier_stack"),
             ("Brier correction ville", "brier_station"),
             ("Brier marché", "brier_market"),
             ("Brier NBM", "brier_nbm")],
        )
    if mk_hold_var:
        lines += _table(
            "Test par max / min",
            mk_hold_var, "variable",
            [("Brier mélange+prix", "brier_stack"),
             ("Brier correction ville", "brier_station"),
             ("Brier marché", "brier_market"),
             ("Brier NBM", "brier_nbm")],
        )
    if mk_hold_nbm:
        lines += _table(
            "Test, seulement les lignes avec NBM",
            mk_hold_nbm, "groupe",
            [("Brier mélange+prix", "brier_stack"),
             ("Brier correction ville", "brier_station"),
             ("Brier marché", "brier_market"),
             ("Brier NBM", "brier_nbm")],
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
    (out_dir / "stacking_skill.md").write_text(report, encoding="utf-8")
    payload = {
        "schema": "market_residual_stack/1",
        "generated_at": now,
        "params": {
            "split_date": split.isoformat(),
            "end": end.isoformat(),
            "leads": [1],
            "stations": wanted,
            "min_train_stack": MIN_TRAIN_STACK,
            "min_market_days": MIN_MARKET_DAYS,
            "model": "city-corrected mix (station bias, TRAIN < split)",
            "prior": "kalshi_mid yes_mid from forward captures",
            "fit": "OLS residual, no intercept: y-market ~ w*(model-market)",
        },
        "weight": weight,
        "n_rows_market": len(market),
        "n_rows_train": len(train),
        "n_rows_holdout": len(hold),
        "n_rows_holdout_nbm": len(hold_nbm),
        "n_dates_train": len({r["target"].isoformat() for r in train}),
        "n_dates_holdout": n_hold_dates,
        "train_dates": sorted({r["target"].isoformat() for r in train}),
        "holdout_dates": sorted({r["target"].isoformat() for r in hold}),
        "market_skips": market_skips,
        "nbm_note": nbm_note,
        "ledger": ledger,
        "calibration_train": {
            "ece_station": ece_station_train,
            "ece_market": ece_market_train,
            "mae_station": mae([r["p_station"] for r in train], _ys(train)),
            "mae_market": mae([r["p_market"] for r in train], _ys(train)),
        },
        "disagreement": {"train": disc_train, "holdout": disc_hold},
        "market": {"train": mk_train, "holdout": mk_hold,
                   "holdout_by_variable": mk_hold_var, "holdout_nbm": mk_hold_nbm},
        "sign_tests": tests,
        "promote": promote,
        "promote_reason": promote_reason,
        "learning_reuse": {
            "yes_mid": "src/learning/dataset.py keeps the earliest capture with yes_mid",
            "not_used": "old LogisticRegression feature sets (they fight the market)",
        },
    }
    (out_dir / "stacking_skill.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    print(report)
    if not hold:
        print("Aucune ligne de test avec un prix et un modèle.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
