"""eval_nbm_skill.py — NBM station contre la vérité CLI (piste A2).

FR : Télécharge les bulletins NBP (seuils 10/25/50/75/90 du max et du min
déjà corrigés par station), construit P(bin) par interpolation, et compare
à la vérité officielle CLI. Même holdout que A1 (cibles ≥ 2026-08-03) et,
quand un prix existe, à kalshi_mid.

Le champion en ligne n'est pas touché ici. On mesure seulement.

EN : Fetch NBM NBP percentiles, interpolate P(bin), score vs CLI truth
and vs kalshi_mid. Does not switch the live champion.

Usage:
    python scripts/eval_nbm_skill.py
    python scripts/eval_nbm_skill.py --skip-fetch
    python scripts/eval_nbm_skill.py --start-issue 2026-07-27 --end-issue 2026-09-06
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.forecast.nbm_client import NbmTextClient, try_iem_afos_latest  # noqa: E402
from src.forecast.nbm_prob import prob_in_bin_nbm  # noqa: E402
from src.forecast.nbm_text import NbmDaily  # noqa: E402
from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, kalshi_stations  # noqa: E402
from src.truth.skill import climatology_gaussian, sign_test_by_date  # noqa: E402
from src.truth.synthetic_bins import Bin, brier, kalshi_style_bins, prob_in_bin_gaussian  # noqa: E402

SIGMA_FLOOR = 1.0
A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)


def load_cli(path: Path) -> dict[tuple[str, date], dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {(r["station"], date.fromisoformat(r["valid"])): r for r in rows}


def cli_lists(cli: dict) -> dict[str, list]:
    from src.truth.iem_cli import CliDay
    by: dict[str, list] = defaultdict(list)
    for (st, d), r in cli.items():
        by[st].append(CliDay(
            station=st, valid=d, high_f=r.get("high"), low_f=r.get("low"),
            high_time=r.get("high_time"), low_time=r.get("low_time"),
            precip_in=r.get("precip"), precip_trace=bool(r.get("precip_trace")),
            snow_in=r.get("snow"), snow_trace=bool(r.get("snow_trace")),
            product=None,
        ))
    return by


def truth_value(row: dict, variable: str) -> Optional[float]:
    v = row.get("high" if variable == "temp_max" else "low")
    return None if v is None else float(v)


def pick_nbm(index: dict, station: str, variable: str, target: date, lead: int,
             before: Optional[datetime] = None) -> Optional[NbmDaily]:
    """Une prévision NBM pour (station, variable, cible, lead), émise avant `before`."""
    cands = index.get((station, variable, target, lead), [])
    if before is not None:
        cands = [f for f in cands if f.issued <= before]
    if not cands:
        return None
    cands.sort(key=lambda f: f.issued)
    return cands[-1]          # plus proche de l'instant demandé, sans fuite


def pick_nbm_before(index_tgt: dict, station: str, variable: str, target: date,
                    before: datetime) -> Optional[NbmDaily]:
    """Dernière émission NBM pour cette cible, strictement avant `before`.

    On ne force pas le même « lead » que le marché : une capture à 12 UTC
    ne peut pas voir le bulletin de 13 UTC du même jour.
    """
    cands = [f for f in index_tgt.get((station, variable, target), []) if f.issued <= before]
    if not cands:
        return None
    return max(cands, key=lambda f: f.issued)


def index_forecasts(rows: list[NbmDaily]) -> dict:
    out: dict = defaultdict(list)
    for f in rows:
        out[(f.station, f.variable, f.target, f.lead)].append(f)
    return out


def index_by_target(rows: list[NbmDaily]) -> dict:
    out: dict = defaultdict(list)
    for f in rows:
        out[(f.station, f.variable, f.target)].append(f)
    return out


def score_standalone(forecasts: list[NbmDaily], cli: dict, truth_lists: dict,
                     split: date, leads: set[int]) -> list[dict]:
    """Bins centrés sur le seuil 50 % NBM, scorés contre CLI + climato CLI."""
    rows = []
    for f in forecasts:
        if f.lead not in leads:
            continue
        if f.target < split:
            continue
        t = cli.get((f.station, f.target))
        obs = truth_value(t, f.variable) if t else None
        if obs is None or f.center_f() is None:
            continue
        p_nbm_ok = False
        cl = climatology_gaussian(truth_lists.get(f.station, []), f.variable, f.target)
        for b in kalshi_style_bins(f.center_f(), n_central=6):
            if not b.is_central:
                continue
            p_nbm = prob_in_bin_nbm(f, b)
            if p_nbm is None:
                continue
            p_nbm_ok = True
            p_climo = prob_in_bin_gaussian(cl[0], cl[1], b) if cl else None
            rows.append({
                "station": f.station, "variable": f.variable, "target": f.target,
                "lead": f.lead, "issued": f.issued, "outcome": b.contains(obs),
                "p_nbm": p_nbm, "p_climo": p_climo, "p_raw": None, "p_station": None,
                "p_market": None, "bin": b.label(),
            })
        if not p_nbm_ok:
            continue
    return rows


def score_vs_ensemble(forecasts: list[NbmDaily], cli: dict, truth_lists: dict,
                      points: list[dict], split: date, leads: set[int]) -> list[dict]:
    """Mêmes bins que l'ensemble (centrées sur la moyenne des modèles)."""
    idx = index_forecasts(forecasts)
    bias_by: dict[tuple, list[float]] = defaultdict(list)
    for p in points:
        if p["_target"] >= split:
            continue
        t = cli.get((p["station"], p["_target"]))
        obs = truth_value(t, p["variable"]) if t else None
        if obs is None:
            continue
        bias_by[(p["station"], p["variable"], p["lead"])].append(obs - p["_mean"])

    rows = []
    for p in points:
        if p["_target"] < split or p["lead"] not in leads:
            continue
        t = cli.get((p["station"], p["_target"]))
        obs = truth_value(t, p["variable"]) if t else None
        if obs is None:
            continue
        fc = pick_nbm(idx, p["station"], p["variable"], p["_target"], p["lead"])
        if fc is None:
            continue
        mu = p["_mean"]
        sig = max(SIGMA_FLOOR, statistics.pstdev(list(p["per_model"].values()))
                  if len(p["per_model"]) >= 2 else SIGMA_FLOOR)
        resid = bias_by.get((p["station"], p["variable"], p["lead"]), [])
        st = None
        if len(resid) >= 20:
            st = (mu + statistics.fmean(resid),
                  max(SIGMA_FLOOR, statistics.pstdev(resid) if len(resid) > 1 else SIGMA_FLOOR))
        cl = climatology_gaussian(truth_lists.get(p["station"], []), p["variable"], p["_target"])
        for b in kalshi_style_bins(mu, n_central=6):
            if not b.is_central:
                continue
            p_nbm = prob_in_bin_nbm(fc, b)
            if p_nbm is None:
                continue
            rows.append({
                "station": p["station"], "variable": p["variable"], "target": p["_target"],
                "lead": p["lead"], "issued": fc.issued, "outcome": b.contains(obs),
                "p_nbm": p_nbm,
                "p_raw": prob_in_bin_gaussian(mu, sig, b),
                "p_station": prob_in_bin_gaussian(st[0], st[1], b) if st else None,
                "p_climo": prob_in_bin_gaussian(cl[0], cl[1], b) if cl else None,
                "p_market": None, "bin": b.label(),
            })
    return rows


def score_market(forecasts: list[NbmDaily], cli: dict, leads: set[int],
                 min_date: date) -> tuple[list[dict], dict]:
    idx_tgt = index_by_target(forecasts)
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
        t = cli.get((icao, r["_target"]))
        obs = truth_value(t, r["variable"]) if t else None
        if obs is None:
            skips["no_cli_truth"] += 1
            continue
        fc = pick_nbm_before(idx_tgt, icao, r["variable"], r["_target"], r["_snap"])
        if fc is None:
            skips["no_nbm"] += 1
            continue
        b = Bin(int(r["lower"]), int(r["upper"]))
        p_nbm = prob_in_bin_nbm(fc, b)
        if p_nbm is None:
            skips["no_nbm_prob"] += 1
            continue
        vals = list(r["_pm"].values()) if r["_pm"] else []
        p_raw = None
        if len(vals) >= 2:
            p_raw = prob_in_bin_gaussian(
                statistics.fmean(vals),
                max(SIGMA_FLOOR, statistics.pstdev(vals)), b)
        rows.append({
            "station": icao, "variable": r["variable"], "target": r["_target"],
            "lead": r["_lead"], "issued": fc.issued, "outcome": b.contains(obs),
            "p_nbm": p_nbm, "p_raw": p_raw, "p_station": None, "p_climo": None,
            "p_market": float(r["yes_mid"]), "bin": b.label(),
        })
    return rows, dict(skips)


def summarize(rows: list[dict], keyf, fields: tuple[str, ...]) -> dict:
    groups: dict = defaultdict(list)
    for r in rows:
        groups[keyf(r)].append(r)
    out = {}
    for k, rs in sorted(groups.items(), key=lambda kv: str(kv[0])):
        rec = {
            "n_bins": len(rs),
            "n_dates": len({r["target"] for r in rs}),
            "base_rate": statistics.fmean(1.0 if r["outcome"] else 0.0 for r in rs),
        }
        for name in fields:
            common = [r for r in rs if r.get(name) is not None]
            if common:
                rec[f"brier_{name[2:] if name.startswith('p_') else name}"] = statistics.fmean(
                    brier(r[name], r["outcome"]) for r in common)
                rec[f"n_{name}"] = len(common)
        out[k] = rec
    return out


def sign_test_rows(rows: list[dict], a: str, b: str) -> dict:
    class _S:
        def __init__(self, r):
            self.target = r["target"]
            self.outcome = r["outcome"]
            setattr(self, a, r[a])
            setattr(self, b, r[b])
    scores = [_S(r) for r in rows if r.get(a) is not None and r.get(b) is not None]
    return sign_test_by_date(scores, a, b)


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
    ap.add_argument("--start-issue", default="2026-05-25")
    ap.add_argument("--end-issue", default="2026-09-06")
    ap.add_argument("--cycles", default="13", help="heures UTC, ex. 13 ou 13,19")
    ap.add_argument("--leads", default="1,2,3,4,5,6,7")
    ap.add_argument("--split-date", default=A1_SPLIT.isoformat())
    ap.add_argument("--stations", default="")
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "nbm"))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    leads = {int(x) for x in args.leads.split(",")}
    cycles = [int(x) for x in args.cycles.split(",") if x.strip()]
    split = date.fromisoformat(args.split_date)
    start = date.fromisoformat(args.start_issue)
    end = date.fromisoformat(args.end_issue)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cli_path = TRUTH_DIR / "cli_daily.json"
    if not cli_path.exists():
        print(f"Vérité CLI absente : {cli_path}. Lancer d'abord build_station_truth.py.")
        return 2
    cli = load_cli(cli_path)
    truth_lists = cli_lists(cli)

    client = NbmTextClient()
    failures = []
    iem_note = None
    if args.skip_fetch:
        forecasts = [f for f in client.load_extracted() if f.station in set(wanted)]
        print(f"Relu {client.extracted_path} ({len(forecasts)} prévisions)", flush=True)
        if not forecasts:
            print("Aucune prévision NBM en cache. Relancer sans --skip-fetch.")
            return 1
    else:
        print(f"Téléchargement NBP S3 {start} → {end} cycles {cycles} ...", flush=True)
        result = client.fetch_range(start, end, cycles=cycles, product="NBP",
                                    stations=wanted, workers=args.workers)
        forecasts = result.forecasts
        failures = [
            {"source": f.source, "url": f.url, "issued": f.issued_date,
             "cycle": f.cycle, "product": f.product, "error": f.error}
            for f in result.failures
        ]
        print(f"   {len(forecasts)} prévisions, {len(result.failures)} échecs, "
              f"{result.from_cache} cycles déjà en cache", flush=True)
        if forecasts:
            client.persist_extracted(forecasts)
        # Un seul appel IEM pour dire si ce repli existe (il n'a pas l'historique).
        iem_rows, iem_err = try_iem_afos_latest(wanted[0])
        iem_note = {
            "station": wanted[0],
            "n_forecasts": len(iem_rows),
            "error": iem_err,
            "comment": "IEM AFOS ne garde que les derniers bulletins, pas août 2026.",
        }
        if iem_err:
            print(f"   Repli IEM AFOS : {iem_err}", flush=True)
        else:
            print(f"   Repli IEM AFOS : {len(iem_rows)} prévisions récentes pour {wanted[0]} "
                  "(pas d'archive holdout)", flush=True)

    found_st = sorted({f.station for f in forecasts})
    missing_st = sorted(set(wanted) - set(found_st))
    print(f"Stations NBM : {len(found_st)}/ {len(wanted)}"
          + (f" manquantes : {missing_st}" if missing_st else ""), flush=True)

    points: list[dict] = []
    fp_path = TRUTH_DIR / "skill" / "forecast_points.json"
    if fp_path.exists():
        for p in json.loads(fp_path.read_text(encoding="utf-8")):
            if p["station"] not in set(wanted):
                continue
            p["_target"] = date.fromisoformat(p["target"])
            p["_mean"] = statistics.fmean(p["per_model"].values())
            points.append(p)

    standalone = score_standalone(forecasts, cli, truth_lists, split, leads)
    versus = score_vs_ensemble(forecasts, cli, truth_lists, points, split, leads)
    market, market_skips = score_market(forecasts, cli, leads, start)

    fields_vs = ("p_nbm", "p_raw", "p_station", "p_climo")
    fields_st = ("p_nbm", "p_climo")
    fields_mk = ("p_nbm", "p_raw", "p_market")

    vs_all = summarize(versus, lambda r: "all", fields_vs)
    vs_lead = summarize(versus, lambda r: r["lead"], fields_vs)
    vs_var = summarize(versus, lambda r: r["variable"], fields_vs)
    vs_st = summarize(versus, lambda r: f"{r['station']}/{r['variable']}", fields_vs)
    st_all = summarize(standalone, lambda r: "all", fields_st)
    mk_all = summarize(market, lambda r: "all", fields_mk)
    mk_lead = summarize(market, lambda r: r["lead"], fields_mk)

    tests = {}
    if versus:
        tests["nbm_vs_raw"] = sign_test_rows(versus, "p_nbm", "p_raw")
        tests["nbm_vs_station"] = sign_test_rows(versus, "p_nbm", "p_station")
        tests["nbm_vs_climo"] = sign_test_rows(versus, "p_nbm", "p_climo")
    if standalone:
        tests["nbm_vs_climo_own_bins"] = sign_test_rows(standalone, "p_nbm", "p_climo")
    if market:
        tests["nbm_vs_market"] = sign_test_rows(market, "p_nbm", "p_market")
        tests["nbm_vs_raw_market_rows"] = sign_test_rows(market, "p_nbm", "p_raw")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# NBM station contre le chiffre officiel",
        "",
        f"Généré : {now}. Émissions NBP {start} → {end}, cycles {cycles} UTC. "
        f"Cibles holdout ≥ {split}, leads {sorted(leads)}.",
        "",
        "NBM = prévision déjà corrigée pour la station (seuils 10, 25, 50, 75 et 90 %). "
        "On relie ces seuils par des segments droits pour donner une chance à chaque contrat de 2 °. "
        "La vérité est le chiffre officiel de la station (même fichier que A1). "
        "Aucun chiffre manquant n'a été inventé.",
        "",
    ]
    if failures:
        lines += [
            f"Téléchargements en échec : {len(failures)}. Détail dans nbm_skill.json. "
            "Ces jours sont absents, pas remplacés.",
            "",
        ]
    if missing_st:
        lines += [f"Stations sans aucun bulletin NBM : {', '.join(missing_st)}.", ""]
    if iem_note and iem_note.get("error"):
        lines += [f"Repli IEM (bulletins récents seulement) : {iem_note['error']}.", ""]

    lines += [
        "Comparaison principale : les mêmes contrats que notre ensemble actuel "
        "(centrées sur la moyenne des modèles, comme A1). "
        "Plus le Brier est petit, mieux c'est.",
        "",
    ]
    lines += _table(
        "Même contrats que l'ensemble (HOLDOUT)",
        vs_all, "groupe",
        [("Brier NBM", "brier_nbm"), ("Brier ensemble", "brier_raw"),
         ("Brier ensemble + correction station", "brier_station"),
         ("Brier climatologie station", "brier_climo")],
    )
    lines += _table(
        "Par horizon (jours d'avance)",
        vs_lead, "lead",
        [("Brier NBM", "brier_nbm"), ("Brier ensemble", "brier_raw"),
         ("Brier ensemble + correction station", "brier_station"),
         ("Brier climatologie", "brier_climo")],
    )
    lines += _table(
        "Par max / min",
        vs_var, "variable",
        [("Brier NBM", "brier_nbm"), ("Brier ensemble", "brier_raw"),
         ("Brier ensemble + correction station", "brier_station")],
    )
    lines += _table(
        "Par station",
        vs_st, "station",
        [("Brier NBM", "brier_nbm"), ("Brier ensemble", "brier_raw"),
         ("Brier ensemble + correction station", "brier_station")],
    )
    if st_all:
        lines += [
            "Contrats centrés sur le chiffre NBM (50 %) : autre lecture, pas les mêmes contrats.",
            "",
        ]
        lines += _table(
            "Contrats autour du NBM (HOLDOUT)",
            st_all, "groupe",
            [("Brier NBM", "brier_nbm"), ("Brier climatologie station", "brier_climo")],
        )
    if mk_all:
        lines += [
            "Prix de marché (kalshi_mid) quand une capture existait, "
            "émission NBM avant la capture, vérité CLI.",
            f"Lignes écartées : {market_skips}.",
            "",
        ]
        lines += _table(
            "Contre le prix de marché",
            mk_all, "groupe",
            [("Brier NBM", "brier_nbm"), ("Brier ensemble", "brier_raw"),
             ("Brier marché", "brier_market")],
        )
        lines += _table(
            "Marché par horizon",
            mk_lead, "lead",
            [("Brier NBM", "brier_nbm"), ("Brier ensemble", "brier_raw"),
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
        "Le modèle en ligne n'est pas changé. Le site public n'est pas changé. "
        "Pas de pari avec de l'argent réel.",
        "",
    ]

    report = "\n".join(lines) + "\n"
    (out_dir / "nbm_skill.md").write_text(report, encoding="utf-8")
    payload = {
        "schema": "nbm_station_skill/1",
        "generated_at": now,
        "params": {
            "start_issue": start.isoformat(), "end_issue": end.isoformat(),
            "cycles": cycles, "leads": sorted(leads), "split_date": split.isoformat(),
            "stations": wanted,
        },
        "coverage": {
            "n_forecasts": len(forecasts),
            "stations_found": found_st,
            "stations_missing": missing_st,
            "issue_dates": sorted({f.issued.date().isoformat() for f in forecasts}),
            "target_dates_holdout": sorted({r["target"].isoformat() for r in versus}),
        },
        "failures": failures,
        "iem_afos": iem_note,
        "n_rows_vs_ensemble": len(versus),
        "n_rows_standalone": len(standalone),
        "n_rows_market": len(market),
        "market_skips": market_skips,
        "vs_ensemble": {"all": vs_all, "by_lead": vs_lead, "by_variable": vs_var, "by_station": vs_st},
        "standalone": {"all": st_all},
        "market": {"all": mk_all, "by_lead": mk_lead},
        "sign_tests": tests,
    }
    (out_dir / "nbm_skill.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(report)
    if not versus and not standalone:
        print("Aucune ligne scorée : vérifier le téléchargement et la vérité CLI.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
