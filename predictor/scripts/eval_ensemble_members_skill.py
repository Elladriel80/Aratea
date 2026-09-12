"""eval_ensemble_members_skill.py — vrais membres contre la vérité CLI (piste A3).

FR : Open-Meteo ne garde les membres que ~3 jours. Pour le même holdout
que A1/A2 (cibles ≥ 2026-08-03), on prend les 31 membres GEFS de
l'archive NOAA, on construit P(bin) = part des membres dans chaque
contrat de 2 °, après la correction ville de A1 si elle existe, et on
compare au mélange actuel, à NBM (A2) et au prix du marché.

Le champion en ligne n'est pas touché. On mesure seulement.

EN : Score GEFS 31-member P(bin) vs CLI on the A1/A2 holdout. Open-Meteo
members cover only ~3 days and are not used as the main score.

Usage:
    python scripts/eval_ensemble_members_skill.py
    python scripts/eval_ensemble_members_skill.py --skip-fetch
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

import eval_nbm_skill as nbm_eval  # noqa: E402
from src.forecast.gefs_s3 import GefsS3Client, fetch_range  # noqa: E402
from src.forecast.nbm_client import NbmTextClient  # noqa: E402
from src.forecast.nbm_prob import prob_in_bin_nbm  # noqa: E402
from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, kalshi_stations  # noqa: E402
from src.truth.skill import SIGMA_FLOOR_F, climatology_gaussian  # noqa: E402
from src.truth.station_bias_table import StationBiasTable  # noqa: E402
from src.truth.synthetic_bins import (  # noqa: E402
    Bin, brier, kalshi_style_bins, prob_in_bin_gaussian, prob_in_bin_members,
)
from src.weather.ensemble_api import DEFAULT_MEMBER_MODELS, EnsembleMembersClient  # noqa: E402

A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)
MIN_MEMBERS = 10


def group_members(rows: list[GefsDaily]) -> dict[tuple, list[float]]:
    """(station, variable, target, lead) → valeurs membres °F."""
    out: dict[tuple, list[float]] = defaultdict(list)
    for r in rows:
        out[(r.station, r.variable, r.target, r.lead)].append(r.value_f)
    return out


def score_vs_ensemble(
    members: dict[tuple, list[float]],
    nbm_forecasts: list,
    cli: dict,
    truth_lists: dict,
    points: list[dict],
    split: date,
    leads: set[int],
    bias_table: StationBiasTable,
) -> list[dict]:
    """Mêmes contrats que le mélange (centrées sur la moyenne des 5 modèles)."""
    nbm_idx = nbm_eval.index_forecasts(nbm_forecasts) if nbm_forecasts else {}
    rows = []
    for p in points:
        if p["_target"] < split or p["lead"] not in leads:
            continue
        t = cli.get((p["station"], p["_target"]))
        obs = nbm_eval.truth_value(t, p["variable"]) if t else None
        if obs is None:
            continue
        vals = members.get((p["station"], p["variable"], p["_target"], p["lead"]))
        if not vals or len(vals) < MIN_MEMBERS:
            continue
        mu = p["_mean"]
        sig = max(SIGMA_FLOOR_F, statistics.pstdev(list(p["per_model"].values()))
                  if len(p["per_model"]) >= 2 else SIGMA_FLOOR_F)
        sb = bias_table.entries.get((p["station"], p["variable"], p["lead"]))
        shifted = [x + sb[0] for x in vals] if sb else None
        st = None
        if sb:
            st = (mu + sb[0], max(SIGMA_FLOOR_F, sb[1]))
        cl = climatology_gaussian(truth_lists.get(p["station"], []), p["variable"], p["_target"])
        fc = nbm_eval.pick_nbm(nbm_idx, p["station"], p["variable"], p["_target"], p["lead"]) if nbm_idx else None
        for b in kalshi_style_bins(mu, n_central=6):
            if not b.is_central:
                continue
            p_nbm = prob_in_bin_nbm(fc, b) if fc is not None else None
            rows.append({
                "station": p["station"], "variable": p["variable"],
                "target": p["_target"], "lead": p["lead"],
                "outcome": b.contains(obs),
                "p_members": prob_in_bin_members(vals, b),
                "p_members_bias": prob_in_bin_members(shifted, b) if shifted else None,
                "p_raw": prob_in_bin_gaussian(mu, sig, b),
                "p_station": prob_in_bin_gaussian(st[0], st[1], b) if st else None,
                "p_climo": prob_in_bin_gaussian(cl[0], cl[1], b) if cl else None,
                "p_nbm": p_nbm, "p_market": None, "bin": b.label(),
                "n_members": len(vals),
            })
    return rows


def score_market(
    members: dict[tuple, list[float]],
    nbm_forecasts: list,
    cli: dict,
    leads: set[int],
    min_date: date,
) -> tuple[list[dict], dict]:
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
        t = cli.get((icao, r["_target"]))
        obs = nbm_eval.truth_value(t, r["variable"]) if t else None
        if obs is None:
            skips["no_cli_truth"] += 1
            continue
        vals = members.get((icao, r["variable"], r["_target"], r["_lead"]))
        if not vals or len(vals) < MIN_MEMBERS:
            skips["no_members"] += 1
            continue
        b = Bin(int(r["lower"]), int(r["upper"]))
        p_mem = prob_in_bin_members(vals, b)
        p_nbm = None
        if nbm_tgt:
            fc = nbm_eval.pick_nbm_before(nbm_tgt, icao, r["variable"], r["_target"], r["_snap"])
            if fc is not None:
                p_nbm = prob_in_bin_nbm(fc, b)
        raw_vals = list(r["_pm"].values()) if r["_pm"] else []
        p_raw = None
        if len(raw_vals) >= 2:
            p_raw = prob_in_bin_gaussian(
                statistics.fmean(raw_vals),
                max(SIGMA_FLOOR_F, statistics.pstdev(raw_vals)), b)
        rows.append({
            "station": icao, "variable": r["variable"], "target": r["_target"],
            "lead": r["_lead"], "outcome": b.contains(obs),
            "p_members": p_mem, "p_members_bias": None,
            "p_raw": p_raw, "p_station": None, "p_climo": None,
            "p_nbm": p_nbm, "p_market": float(r["yes_mid"]), "bin": b.label(),
            "n_members": len(vals),
        })
    return rows, dict(skips)


def probe_open_meteo(stations: dict, models: list[str]) -> dict:
    """Couverture réelle des membres Open-Meteo (pas le score principal)."""
    client = EnsembleMembersClient(models=models, sleep_s=0.15)
    coverage = {}
    failures = dict(client.failures)
    for icao, meta in list(stations.items())[:1]:  # une station suffit à dater la fenêtre
        try:
            by = client.fetch(meta["lat"], meta["lon"], days=1, past_days=40)
        except Exception as e:  # noqa: BLE001
            return {"error": str(e), "failures": dict(client.failures)}
        days = client.member_value_days(by)
        coverage[icao] = {m: d for m, d in days.items()}
        failures.update(client.failures)
        n_members = {m: len(s) for m, s in by.items()}
        return {
            "probe_station": icao,
            "n_members": n_members,
            "value_days": coverage[icao],
            "failures": failures,
            "comment": (
                "Open-Meteo ne remplit les membres que sur ~3 jours passés. "
                "Ce n'est pas le holdout A1/A2."
            ),
        }
    return {"error": "aucune station", "failures": failures}


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
    ap.add_argument("--start-issue", default="2026-07-27")
    ap.add_argument("--end-issue", default="2026-09-06")
    ap.add_argument("--leads", default="1,2,3,4,5,6,7")
    ap.add_argument("--split-date", default=A1_SPLIT.isoformat())
    ap.add_argument("--stations", default="")
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--skip-open-meteo", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "ensemble"))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    station_meta = {k: v for k, v in stations.items() if k in set(wanted)}
    leads = sorted({int(x) for x in args.leads.split(",")})
    lead_set = set(leads)
    split = date.fromisoformat(args.split_date)
    start = date.fromisoformat(args.start_issue)
    end = date.fromisoformat(args.end_issue)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cli_path = TRUTH_DIR / "cli_daily.json"
    if not cli_path.exists():
        print(f"Vérité CLI absente : {cli_path}. Lancer d'abord build_station_truth.py.")
        return 2
    cli = nbm_eval.load_cli(cli_path)
    truth_lists = nbm_eval.cli_lists(cli)

    client = GefsS3Client()
    failures = []
    if args.skip_fetch:
        gefs_rows = [r for r in client.load_extracted() if r.station in set(wanted)]
        print(f"Relu {client.extracted_path} ({len(gefs_rows)} lignes membre)", flush=True)
        if not gefs_rows:
            print("Aucun membre GEFS en cache. Relancer sans --skip-fetch.")
            return 1
    else:
        print(f"Téléchargement GEFS S3 {start} → {end} 00z leads {leads} ...", flush=True)
        try:
            result = fetch_range(
                client, start, end, leads, stations=station_meta, workers=args.workers,
            )
        except RuntimeError as e:
            print(f"GEFS : {e}")
            return 1
        gefs_rows = [r for r in result.forecasts if r.station in set(wanted)]
        failures = [
            {"source": f.source, "url": f.url, "issued": f.issued,
             "member": f.member, "fhr": f.fhr, "error": f.error}
            for f in result.failures
        ]
        print(f"   {len(gefs_rows)} extrêmes, {result.n_files_ok} fichiers OK, "
              f"{len(result.failures)} échecs", flush=True)
        if gefs_rows:
            client.persist_extracted(gefs_rows)

    members = group_members(gefs_rows)
    found_st = sorted({r.station for r in gefs_rows})
    missing_st = sorted(set(wanted) - set(found_st))
    print(f"Stations GEFS : {len(found_st)}/{len(wanted)}"
          + (f" manquantes : {missing_st}" if missing_st else ""), flush=True)

    om_probe = None
    if not args.skip_open_meteo:
        print("Sonde Open-Meteo Ensemble API (fenêtre récente seulement) ...", flush=True)
        try:
            om_probe = probe_open_meteo(station_meta, DEFAULT_MEMBER_MODELS + ["google_weathernext2_ensemble"])
            print(f"   Open-Meteo : {om_probe}", flush=True)
        except Exception as e:  # noqa: BLE001
            om_probe = {"error": str(e)}
            print(f"   Open-Meteo a échoué : {e}", flush=True)

    points: list[dict] = []
    fp_path = TRUTH_DIR / "skill" / "forecast_points.json"
    if fp_path.exists():
        for p in json.loads(fp_path.read_text(encoding="utf-8")):
            if p["station"] not in set(wanted):
                continue
            p["_target"] = date.fromisoformat(p["target"])
            p["_mean"] = statistics.fmean(p["per_model"].values())
            points.append(p)

    nbm_forecasts = []
    nbm_note = None
    try:
        nbm_forecasts = [f for f in NbmTextClient().load_extracted() if f.station in set(wanted)]
        nbm_note = f"{len(nbm_forecasts)} prévisions NBM déjà là (A2)."
    except Exception as e:  # noqa: BLE001
        nbm_note = f"NBM absent ou illisible : {e}"

    bias_table = StationBiasTable()
    versus = score_vs_ensemble(
        members, nbm_forecasts, cli, truth_lists, points, split, lead_set, bias_table,
    )
    market, market_skips = score_market(members, nbm_forecasts, cli, lead_set, start)

    fields_vs = ("p_members", "p_members_bias", "p_raw", "p_station", "p_nbm", "p_climo")
    fields_mk = ("p_members", "p_raw", "p_nbm", "p_market")

    vs_all = nbm_eval.summarize(versus, lambda r: "all", fields_vs)
    vs_lead = nbm_eval.summarize(versus, lambda r: r["lead"], fields_vs)
    vs_var = nbm_eval.summarize(versus, lambda r: r["variable"], fields_vs)
    vs_st = nbm_eval.summarize(versus, lambda r: f"{r['station']}/{r['variable']}", fields_vs)
    mk_all = nbm_eval.summarize(market, lambda r: "all", fields_mk)
    mk_lead = nbm_eval.summarize(market, lambda r: r["lead"], fields_mk)

    tests = {}
    if versus:
        tests["members_vs_raw"] = nbm_eval.sign_test_rows(versus, "p_members", "p_raw")
        tests["members_vs_station"] = nbm_eval.sign_test_rows(versus, "p_members", "p_station")
        tests["members_bias_vs_station"] = nbm_eval.sign_test_rows(versus, "p_members_bias", "p_station")
        tests["members_vs_nbm"] = nbm_eval.sign_test_rows(versus, "p_members", "p_nbm")
        tests["members_bias_vs_nbm"] = nbm_eval.sign_test_rows(versus, "p_members_bias", "p_nbm")
    if market:
        tests["members_vs_market"] = nbm_eval.sign_test_rows(market, "p_members", "p_market")
        tests["members_vs_raw_market_rows"] = nbm_eval.sign_test_rows(market, "p_members", "p_raw")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Vrais membres contre le chiffre officiel",
        "",
        f"Généré : {now}. Émissions GEFS 00z {start} → {end}. "
        f"Cibles holdout ≥ {split}, leads {leads}.",
        "",
        "P(bin) = part des 31 versions du modèle américain (GEFS) dans chaque "
        "contrat de 2 °. La vérité est le chiffre officiel de la station "
        "(même fichier que A1). La correction ville est la table A1, apprise "
        "avant le 3 août, pas sur les jours de test.",
        "",
        "Open-Meteo ne garde les membres que 3 jours. L'archive européenne "
        "n'a plus août. On a donc utilisé l'archive publique NOAA pour GEFS. "
        "Aucun chiffre manquant n'a été inventé.",
        "",
    ]
    if om_probe:
        if om_probe.get("error"):
            lines += [f"Sonde Open-Meteo : échec ({om_probe['error']}).", ""]
        else:
            days = om_probe.get("value_days") or {}
            filled = {m: (v[0], v[-1], len(v)) for m, v in days.items() if v}
            lines += [
                f"Sonde Open-Meteo (station {om_probe.get('probe_station')}) : "
                f"membres remplis seulement {filled}. "
                "Ce n'est pas le holdout. On ne mélange pas ces 3 jours au test principal.",
                "",
            ]
            if om_probe.get("failures"):
                lines += [f"Modèles Open-Meteo en échec : {om_probe['failures']}.", ""]
    if failures:
        lines += [
            f"Téléchargements GEFS en échec : {len(failures)}. "
            "Ces heures sont absentes, pas remplacées. Détail dans ensemble_skill.json.",
            "",
        ]
    if missing_st:
        lines += [f"Stations sans aucun membre GEFS : {', '.join(missing_st)}.", ""]
    if nbm_note:
        lines += [nbm_note, ""]

    lines += [
        "Comparaison principale : les mêmes contrats que notre mélange actuel "
        "(centrées sur la moyenne des 5 modèles, comme A1 et A2). "
        "Plus le score d'erreur est petit, mieux c'est.",
        "",
    ]
    lines += _table(
        "Même contrats que l'ensemble (HOLDOUT)",
        vs_all, "groupe",
        [("Brier membres", "brier_members"),
         ("Brier membres + correction ville", "brier_members_bias"),
         ("Brier mélange", "brier_raw"),
         ("Brier mélange + correction ville", "brier_station"),
         ("Brier NBM", "brier_nbm")],
    )
    lines += _table(
        "Par horizon (jours d'avance)",
        vs_lead, "lead",
        [("Brier membres", "brier_members"),
         ("Brier membres + correction ville", "brier_members_bias"),
         ("Brier mélange", "brier_raw"),
         ("Brier mélange + correction ville", "brier_station"),
         ("Brier NBM", "brier_nbm")],
    )
    lines += _table(
        "Par max / min",
        vs_var, "variable",
        [("Brier membres", "brier_members"),
         ("Brier membres + correction ville", "brier_members_bias"),
         ("Brier mélange", "brier_raw"),
         ("Brier NBM", "brier_nbm")],
    )
    lines += _table(
        "Par station",
        vs_st, "station",
        [("Brier membres", "brier_members"),
         ("Brier membres + correction ville", "brier_members_bias"),
         ("Brier mélange", "brier_raw"),
         ("Brier NBM", "brier_nbm")],
    )
    if mk_all:
        lines += [
            "Prix de marché (kalshi_mid) quand une capture existait, "
            "membres GEFS émis avant la date cible, vérité CLI.",
            f"Lignes écartées : {market_skips}.",
            "",
        ]
        lines += _table(
            "Contre le prix de marché",
            mk_all, "groupe",
            [("Brier membres", "brier_members"), ("Brier mélange", "brier_raw"),
             ("Brier NBM", "brier_nbm"), ("Brier marché", "brier_market")],
        )
        lines += _table(
            "Marché par horizon",
            mk_lead, "lead",
            [("Brier membres", "brier_members"), ("Brier mélange", "brier_raw"),
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
    (out_dir / "ensemble_skill.md").write_text(report, encoding="utf-8")
    payload = {
        "schema": "ensemble_members_skill/1",
        "generated_at": now,
        "params": {
            "start_issue": start.isoformat(), "end_issue": end.isoformat(),
            "leads": leads, "split_date": split.isoformat(),
            "stations": wanted, "source": "noaa-gefs-pds 00z 31 members",
        },
        "coverage": {
            "n_member_rows": len(gefs_rows),
            "n_groups": len(members),
            "stations_found": found_st,
            "stations_missing": missing_st,
            "target_dates_holdout": sorted({r["target"].isoformat() for r in versus}),
            "n_members_hist": sorted({r["n_members"] for r in versus}) if versus else [],
        },
        "failures": failures[:200],
        "n_failures": len(failures),
        "open_meteo_probe": om_probe,
        "nbm_note": nbm_note,
        "n_rows_vs_ensemble": len(versus),
        "n_rows_market": len(market),
        "market_skips": market_skips,
        "vs_ensemble": {"all": vs_all, "by_lead": vs_lead, "by_variable": vs_var, "by_station": vs_st},
        "market": {"all": mk_all, "by_lead": mk_lead},
        "sign_tests": tests,
    }
    (out_dir / "ensemble_skill.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    print(report)
    if not versus:
        print("Aucune ligne scorée : vérifier GEFS et la vérité CLI.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
