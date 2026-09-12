"""eval_nowcast_skill.py — thermomètre du jour (piste C1).

FR : Pour les contrats max/min du jour même, on lit la température déjà
mesurée à la station, plus un risque simple pour les heures encore
ouvertes (HRRR de la veille si elle est là, sinon une largeur selon
les heures restantes). On note contre le chiffre officiel de la
station, et contre le prix du marché quand un prix same-day existe.

On n'invente aucune lecture. Si l'historique manque à l'heure utile,
on le dit et on mesure seulement ce qu'on a.

Le robot actuel ne parie pas sur aujourd'hui (il vise demain). On ne
change pas ça. Le champion en ligne n'est pas touché.

EN : Same-day nowcast from real station observations + remaining-day
risk. Scores vs CLI truth and kalshi_mid. Does not switch the live
champion or the public site.

Usage:
    python scripts/eval_nowcast_skill.py
    python scripts/eval_nowcast_skill.py --skip-fetch
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

import eval_nbm_skill as nbm_eval  # noqa: E402
import eval_station_bias_market as mkt  # noqa: E402
from src.truth.asos import (  # noqa: E402
    IemAsosClient, NwsObservationClient, index_obs, observed_extreme_so_far,
)
from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, kalshi_stations  # noqa: E402
from src.truth.nowcast import (  # noqa: E402
    EmpiricalRemaining, hours_left, kind_for_variable, prob_bin_nowcast,
    remaining_params,
)
from src.truth.synthetic_bins import Bin, brier, prob_in_bin_gaussian  # noqa: E402
from src.weather.hrrr_hourly import (  # noqa: E402
    HRRR_NOTE, HrrrHourlyClient, remaining_extreme,
)

A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)
MIN_MARKET_DAYS = 30
SIGMA_FLOOR = 1.0
EMPIRICAL_HOURS = (17, 18, 19, 20)


def load_j0_records(min_date: date | None, max_date: date | None) -> list[dict]:
    """Captures live lead 0, bins centraux cotés deux côtés. Premier (ticker)."""
    seen: dict[str, dict] = {}
    pred_dir = ROOT / "data" / "predictions"
    for f in sorted(pred_dir.glob("forward_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for r in d.get("records", []):
            if r.get("variable") not in ("temp_max", "temp_min"):
                continue
            if r.get("lower") is None or r.get("upper") is None:
                continue
            if r.get("yes_bid") is None or r.get("yes_ask") is None:
                continue
            if r["yes_ask"] <= 0 or r["yes_ask"] < r["yes_bid"]:
                continue
            ens = (r.get("predictions") or {}).get("ensemble") or {}
            pm = (ens.get("inputs") or {}).get("per_model_value") or {}
            if len(pm) < 2:
                continue
            target = date.fromisoformat(r["target_date"])
            if min_date and target < min_date:
                continue
            if max_date and target > max_date:
                continue
            snap = datetime.strptime(r["snapshot_at"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            if (target - snap.date()).days != 0:
                continue
            if r["ticker"] in seen:
                continue
            seen[r["ticker"]] = {**r, "_target": target, "_snap": snap, "_pm": pm}
    return list(seen.values())


def build_empirical(
    obs_by: dict,
    cli: dict,
    stations: dict,
    split: date,
) -> EmpiricalRemaining:
    """Apprend la hausse/baisse restante sur les jours avant `split`."""
    emp = EmpiricalRemaining()
    for icao, meta in stations.items():
        rows = obs_by.get(icao, [])
        if not rows:
            continue
        tz = meta["tz"]
        d = min((o.valid.date() for o in rows), default=None)
        if d is None:
            continue
        last = max(o.valid.date() for o in rows)
        while d < split and d <= last:
            t = cli.get((icao, d))
            if t:
                for hour in EMPIRICAL_HOURS:
                    as_of = datetime(d.year, d.month, d.day, hour, 0, tzinfo=timezone.utc)
                    for variable, kind in (("temp_max", "max"), ("temp_min", "min")):
                        official = nbm_eval.truth_value(t, variable)
                        if official is None:
                            continue
                        got = observed_extreme_so_far(rows, tz, d, as_of, kind)
                        if got is None:
                            continue
                        emp.add(icao, variable, hour, got["extreme_f"], official)
            d = d + timedelta(days=1)
    return emp


def hrrr_residual_sigma(
    obs_by: dict,
    hrrr_by: dict,
    cli: dict,
    stations: dict,
    split: date,
) -> dict[tuple[str, str], float]:
    """Écart officiel − max(obs, HRRR reste) sur TRAIN, par station/variable."""
    resid: dict[tuple[str, str], list[float]] = defaultdict(list)
    for icao, meta in stations.items():
        series = hrrr_by.get(icao)
        rows = obs_by.get(icao, [])
        if not series or not rows:
            continue
        tz = meta["tz"]
        d = min((o.valid.date() for o in rows), default=None)
        if d is None:
            continue
        last = max(o.valid.date() for o in rows)
        while d < split and d <= last:
            t = cli.get((icao, d))
            if t:
                for hour in EMPIRICAL_HOURS:
                    as_of = datetime(d.year, d.month, d.day, hour, 0, tzinfo=timezone.utc)
                    for variable, kind in (("temp_max", "max"), ("temp_min", "min")):
                        official = nbm_eval.truth_value(t, variable)
                        if official is None:
                            continue
                        got = observed_extreme_so_far(rows, tz, d, as_of, kind)
                        if got is None:
                            continue
                        rem = remaining_extreme(
                            series["times"], series["values"], tz, d, as_of, kind,
                        )
                        if rem is None:
                            continue
                        if kind == "max":
                            pred = max(got["extreme_f"], rem["extreme_f"])
                        else:
                            pred = min(got["extreme_f"], rem["extreme_f"])
                        resid[(icao, variable)].append(official - pred)
            d = d + timedelta(days=1)
    out = {}
    for k, vals in resid.items():
        if len(vals) >= 20:
            out[k] = max(0.5, statistics.pstdev(vals) if len(vals) > 1 else 1.5)
    return out


def score_records(
    records: list[dict],
    obs_by: dict,
    hrrr_by: dict,
    cli: dict,
    stations: dict,
    emp: EmpiricalRemaining,
    hrrr_sig: dict,
    bias: mkt.PointInTimeBias,
) -> tuple[list[dict], dict]:
    skips: dict[str, int] = defaultdict(int)
    rows = []
    for r in records:
        icao = CITY_TO_ICAO.get(r["location_key"])
        if not icao:
            skips["pas_de_station"] += 1
            continue
        meta = stations.get(icao)
        if not meta:
            skips["pas_de_station"] += 1
            continue
        t = cli.get((icao, r["_target"]))
        official = nbm_eval.truth_value(t, r["variable"]) if t else None
        if official is None:
            skips["pas_de_chiffre_officiel"] += 1
            continue
        kind = kind_for_variable(r["variable"])
        tz = meta["tz"]
        as_of = r["_snap"]
        got = observed_extreme_so_far(obs_by.get(icao, []), tz, r["_target"], as_of, kind)
        if got is None:
            skips["pas_assez_de_lectures"] += 1
            continue
        series = hrrr_by.get(icao)
        hrrr = None
        if series:
            hrrr = remaining_extreme(
                series["times"], series["values"], tz, r["_target"], as_of, kind,
            )
        left = hours_left(r["_target"], tz, as_of)
        emp_pair = emp.get(icao, r["variable"], as_of.hour)
        mu, sig, src = remaining_params(
            got["extreme_f"], left, hrrr, emp_pair,
            hrrr_sigma=hrrr_sig.get((icao, r["variable"])),
        )
        mu_fb, sig_fb, src_fb = remaining_params(
            got["extreme_f"], left, None, emp_pair,
        )
        b = Bin(int(r["lower"]), int(r["upper"]))
        y = b.contains(official)
        p_now = prob_bin_nowcast(got["extreme_f"], mu, sig, b, kind)
        p_fb = prob_bin_nowcast(got["extreme_f"], mu_fb, sig_fb, b, kind)
        vals = list(r["_pm"].values())
        mu_raw = statistics.fmean(vals)
        sig_raw = max(SIGMA_FLOOR, statistics.pstdev(vals))
        p_raw = prob_in_bin_gaussian(mu_raw, sig_raw, b)
        bs = bias.get(icao, r["variable"], 0, as_of.date())
        if bs is None:
            skips["pas_encore_de_correction_ville"] += 1
            continue
        p_station = prob_in_bin_gaussian(mu_raw + bs[0], bs[1], b)
        rows.append({
            "station": icao, "variable": r["variable"], "target": r["_target"],
            "lead": 0, "issued": as_of, "outcome": y,
            "p_nowcast": p_now, "p_fallback": p_fb, "p_raw": p_raw,
            "p_station": p_station, "p_market": float(r["yes_mid"]),
            "bin": b.label(), "nowcast_source": src, "fallback_source": src_fb,
            "obs_so_far": got["extreme_f"], "n_obs": got["n_obs"],
            "hours_left": left, "official": official,
        })
    return rows, dict(skips)


def _table(title: str, summ: dict, key: str, cols: list[tuple[str, str]]) -> list[str]:
    head = [c[0] for c in cols]
    lines = [f"### {title}", "",
             f"| {key} | n bins | n dates | " + " | ".join(head) + " |",
             "|" + "|".join(["---"] * (3 + len(cols))) + "|"]
    for k, r in summ.items():
        cells = [str(k), str(r["n_bins"]), str(r["n_dates"])]
        for _, field in cols:
            cells.append(nbm_eval._fmt(r.get(field)))
        lines.append("| " + " | ".join(cells) + " |")
    return lines + [""]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", default="2026-05-01")
    ap.add_argument("--end", default="2026-09-11")
    ap.add_argument("--split-date", default=A1_SPLIT.isoformat())
    ap.add_argument("--stations", default="")
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--skip-nws-probe", action="store_true")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "nowcast"))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    stations = {k: v for k, v in stations.items() if k in set(wanted)}
    split = date.fromisoformat(args.split_date)
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cli_path = TRUTH_DIR / "cli_daily.json"
    if not cli_path.exists():
        print(f"Vérité officielle absente : {cli_path}. Lancer d'abord build_station_truth.py.")
        return 2
    cli = nbm_eval.load_cli(cli_path)

    asos = IemAsosClient()
    hrrr_client = HrrrHourlyClient()
    fetch_errors: list[dict] = []
    nws_note = None

    if args.skip_fetch:
        obs_rows = [o for o in asos.load_extracted() if o.station in set(wanted)]
        hrrr_by = {k: v for k, v in hrrr_client.load_extracted().items() if k in set(wanted)}
        print(f"Relu {asos.extracted_path} ({len(obs_rows)} lectures)", flush=True)
        print(f"Relu {hrrr_client.extracted_path} ({len(hrrr_by)} stations HRRR)", flush=True)
        if not obs_rows:
            print("Aucune lecture station en cache. Relancer sans --skip-fetch.")
            return 1
    else:
        obs_rows = []
        y, m = start.year, start.month
        while date(y, m, 1) <= end:
            print(f"[IEM] {y}-{m:02d} ({len(wanted)} stations) ...", flush=True)
            try:
                rows, month_fails = asos.fetch_month_many(wanted, y, m)
            except Exception as e:  # noqa: BLE001
                fetch_errors.append({"source": "iem", "month": f"{y}-{m:02d}", "error": str(e)})
                print(f"   échec IEM : {e}", flush=True)
                rows, month_fails = [], [str(e)]
            print(f"   {len(rows)} lectures"
                  + (f", manques : {month_fails}" if month_fails else ""),
                  flush=True)
            obs_rows.extend(rows)
            for msg in month_fails:
                fetch_errors.append({"source": "iem", "error": msg})
            if m == 12:
                y, m = y + 1, 1
            else:
                m += 1
        # Garde seulement la fenêtre demandée.
        obs_rows = [o for o in obs_rows if start <= o.valid.date() <= end + timedelta(days=1)]
        if obs_rows:
            asos.persist_extracted(obs_rows)
        hrrr_by = {}
        for icao, meta in stations.items():
            print(f"[{icao}] HRRR veille {start} → {end} ...", flush=True)
            try:
                hrrr_by[icao] = hrrr_client.fetch_range(
                    icao, meta["lat"], meta["lon"], start, end,
                )
                n_ok = sum(1 for v in hrrr_by[icao]["values"] if v is not None)
                print(f"   {n_ok} heures avec une valeur", flush=True)
            except Exception as e:  # noqa: BLE001
                fetch_errors.append({"source": "hrrr", "station": icao, "error": str(e)})
                print(f"   échec HRRR : {e}", flush=True)
        if hrrr_by:
            hrrr_client.persist_extracted(hrrr_by)
        if not args.skip_nws_probe and wanted:
            print(f"Sonde api.weather.gov ({wanted[0]}) ...", flush=True)
            nws_note = NwsObservationClient().probe_span(wanted[0])
            print(f"   {nws_note}", flush=True)

    obs_by = index_obs(obs_rows)
    found = sorted(obs_by)
    missing = sorted(set(wanted) - set(found))
    print(f"Stations avec lectures : {len(found)}/{len(wanted)}"
          + (f" manquantes : {missing}" if missing else ""), flush=True)

    emp = build_empirical(obs_by, cli, stations, split)
    hrrr_sig = hrrr_residual_sigma(obs_by, hrrr_by, cli, stations, split)
    print(f"Hausse restante apprise : {sum(len(v) for v in emp.pairs.values())} paires TRAIN",
          flush=True)

    fp_path = TRUTH_DIR / "skill" / "forecast_points.json"
    if not fp_path.exists():
        print(f"Points de prévision absents : {fp_path}.")
        return 2
    bias = mkt.PointInTimeBias(mkt.load_points(), cli)
    records = load_j0_records(start, end)
    print(f"Captures same-day cotées : {len(records)}", flush=True)

    rows, skips = score_records(records, obs_by, hrrr_by, cli, stations, emp, hrrr_sig, bias)
    hold = [r for r in rows if r["target"] >= split]
    print(f"Lignes notées : {len(rows)} (dont test {len(hold)}). Skips : {skips}", flush=True)

    fields = ("p_nowcast", "p_fallback", "p_station", "p_raw", "p_market")
    all_sum = nbm_eval.summarize(rows, lambda r: "all", fields) if rows else {}
    hold_sum = nbm_eval.summarize(hold, lambda r: "all", fields) if hold else {}
    by_var = nbm_eval.summarize(rows, lambda r: r["variable"], fields) if rows else {}
    by_src = nbm_eval.summarize(rows, lambda r: r["nowcast_source"], fields) if rows else {}
    by_st = nbm_eval.summarize(rows, lambda r: f"{r['station']}/{r['variable']}", fields) if rows else {}

    tests = {}
    if rows:
        tests["nowcast_vs_station"] = nbm_eval.sign_test_rows(rows, "p_nowcast", "p_station")
        tests["nowcast_vs_market"] = nbm_eval.sign_test_rows(rows, "p_nowcast", "p_market")
        tests["fallback_vs_station"] = nbm_eval.sign_test_rows(rows, "p_fallback", "p_station")
        tests["fallback_vs_market"] = nbm_eval.sign_test_rows(rows, "p_fallback", "p_market")
        tests["station_vs_market"] = nbm_eval.sign_test_rows(rows, "p_station", "p_market")
    if hold:
        tests["nowcast_vs_station_hold"] = nbm_eval.sign_test_rows(hold, "p_nowcast", "p_station")
        tests["nowcast_vs_market_hold"] = nbm_eval.sign_test_rows(hold, "p_nowcast", "p_market")

    n_dates = len({r["target"] for r in rows}) if rows else 0
    n_hold_dates = len({r["target"] for r in hold}) if hold else 0
    mkt_test = tests.get("nowcast_vs_market") or {}
    promote = bool(
        n_dates >= MIN_MARKET_DAYS
        and mkt_test.get("p_one_sided") is not None
        and mkt_test["p_one_sided"] < 0.05
        and mkt_test.get("a_wins", 0) > mkt_test.get("dates", 0) / 2
        and all_sum.get("all", {}).get("brier_nowcast") is not None
        and all_sum["all"]["brier_nowcast"] < all_sum["all"].get("brier_market", 99)
        and all_sum["all"]["brier_nowcast"] < all_sum["all"].get("brier_station", 99)
    )

    src_counts = defaultdict(int)
    for r in rows:
        src_counts[r["nowcast_source"]] += 1

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Thermomètre du jour contre le chiffre officiel et le marché",
        "",
        f"Généré : {now}. Captures du jour même (lead 0), bins cotés deux côtés. "
        f"Vérité : chiffre officiel de la station (même fichier que A1). "
        f"Apprentissage de la hausse restante : jours avant {split}. "
        f"Aucune lecture manquante n'a été inventée.",
        "",
        HRRR_NOTE,
        "",
        "api.weather.gov ne garde que les jours récents. L'été 2026 vient de "
        "l'archive IEM (lectures horaires). "
        + (f"Sonde NWS : {nws_note}." if nws_note else "Sonde NWS non relancée."),
        "",
        f"Stations avec lectures : {len(found)}/{len(wanted)}"
        + (f". Il manque : {', '.join(missing)}. On ne les a pas inventées." if missing else "."),
        f"Lectures IEM : {len(obs_rows)}. Stations HRRR : {len(hrrr_by)}.",
        f"Captures same-day lues : {len(records)}. Lignes notées : {len(rows)} "
        f"({n_dates} jours). Jours de test (≥ {split}) : {n_hold_dates}.",
        f"Skips : {skips}.",
        f"Source du reste de journée : {dict(src_counts)}.",
        f"Échecs de téléchargement : {len(fetch_errors)}.",
        "",
        "Le robot de paper-trading ne vise que demain "
        "(`daily_auto.py`, date = aujourd'hui + 1). On n'a pas changé ça.",
        "",
        "Plus le score d'erreur est petit, mieux c'est.",
        "",
    ]
    cols = [
        ("Brier thermomètre + reste", "brier_nowcast"),
        ("Brier reste simple", "brier_fallback"),
        ("Brier correction ville", "brier_station"),
        ("Brier mélange", "brier_raw"),
        ("Brier prix", "brier_market"),
    ]
    if all_sum:
        lines += _table("Tous les jours same-day avec un prix", all_sum, "groupe", cols)
    if hold_sum:
        lines += _table(f"Jours de test (≥ {split})", hold_sum, "groupe", cols)
    if by_var:
        lines += _table("Par max / min", by_var, "variable", cols)
    if by_src:
        lines += _table("Par source du reste de journée", by_src, "source", cols)
    if by_st:
        lines += _table("Par station", by_st, "station/variable", cols)

    def _test_line(name: str, t: dict) -> str:
        if not t:
            return f"- {name} : pas assez de jours"
        p = t.get("p_one_sided")
        ptxt = "n/a" if p is None else f"{p:.4f}"
        return (f"- {name} : {t.get('a_wins', 0)} jours sur {t.get('dates', 0)} "
                f"(p = {ptxt})")

    lines += ["### Combien de jours on gagne", ""]
    for key, label in (
        ("nowcast_vs_station", "thermomètre contre correction ville"),
        ("nowcast_vs_market", "thermomètre contre le prix"),
        ("fallback_vs_station", "reste simple contre correction ville"),
        ("fallback_vs_market", "reste simple contre le prix"),
        ("station_vs_market", "correction ville contre le prix"),
        ("nowcast_vs_station_hold", "thermomètre contre correction ville (test)"),
        ("nowcast_vs_market_hold", "thermomètre contre le prix (test)"),
    ):
        lines.append(_test_line(label, tests.get(key) or {}))
    lines += [
        "",
        f"Règle : 30 jours minimum pour parler du marché. Jours avec prix et "
        f"thermomètre : {n_dates}. Promotion : {'oui' if promote else 'non'}.",
        "",
        "Le modèle en ligne n'est pas changé. Pas de pari avec de l'argent réel.",
        "",
    ]

    report = out_dir / "nowcast_skill.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {
        "generated": now,
        "split": split.isoformat(),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "n_obs": len(obs_rows),
        "n_stations_obs": len(found),
        "missing_stations": missing,
        "n_hrrr_stations": len(hrrr_by),
        "n_records": len(records),
        "n_rows": len(rows),
        "n_dates": n_dates,
        "n_holdout_rows": len(hold),
        "n_holdout_dates": n_hold_dates,
        "skips": skips,
        "fetch_errors": fetch_errors,
        "nws": nws_note,
        "hrrr_note": HRRR_NOTE,
        "source_counts": dict(src_counts),
        "all": all_sum,
        "holdout": hold_sum,
        "by_variable": by_var,
        "by_source": by_src,
        "by_station": by_st,
        "tests": tests,
        "promote": promote,
        "min_market_days": MIN_MARKET_DAYS,
        "bot_skips_same_day": True,
    }
    (out_dir / "nowcast_skill.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Écrit {report}", flush=True)
    print(f"Écrit {out_dir / 'nowcast_skill.json'}", flush=True)
    if not rows:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
