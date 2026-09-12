"""eval_hrrr_morning_skill.py — HRRR du matin même (reste du jour, J0).

FR : Pour chaque jour, on prend le run HRRR de 12 h UTC (pas la veille).
On garde les heures encore dans le jour officiel LST après 12 h. On en
tire un max et un min, puis P(case de 2 °F). On note contre le chiffre
officiel de la station, contre le mélange déjà corrigé ville par ville,
et contre le prix du jour même quand il existe.

Le champion en ligne n'est pas touché. Pas de pari avec de l'argent réel.
On ne relance pas le thermomètre du jour (C1) ni la prévision de la veille.

EN : Same-day 12Z HRRR remaining-day max/min → P(bin). Scores vs CLI,
city-corrected champion, and kalshi_mid. Does not switch the live
champion. Keeps J0 separate from yesterday's HRRR and from C1.

Usage:
    python scripts/eval_hrrr_morning_skill.py
    python scripts/eval_hrrr_morning_skill.py --skip-fetch
"""
from __future__ import annotations

import argparse
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
import eval_nowcast_skill as nowcast_eval  # noqa: E402
import eval_station_bias_market as mkt  # noqa: E402
from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, kalshi_stations  # noqa: E402
from src.truth.synthetic_bins import (  # noqa: E402
    Bin, kalshi_style_bins, prob_in_bin_gaussian,
)
from src.weather.hrrr_hourly import remaining_extreme  # noqa: E402
from src.weather.hrrr_morning import (  # noqa: E402
    AVAILABLE_AFTER_UTC, HRRR_NOTE, SOURCE, HrrrMorningClient,
    available_at, issued_12z,
)

A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)
MIN_MARKET_DAYS = 30
SIGMA_FLOOR = 1.0
DEFAULT_SIGMA = 1.5


def train_sigma(
    hrrr_by: dict,
    cli: dict,
    stations: dict,
    split: date,
) -> dict[tuple[str, str], float]:
    """Écart officiel − extrême HRRR 12Z (reste du jour), jours avant `split`."""
    resid: dict[tuple[str, str], list[float]] = defaultdict(list)
    for (icao, d), series in hrrr_by.items():
        if d >= split:
            continue
        meta = stations.get(icao)
        if not meta:
            continue
        t = cli.get((icao, d))
        if not t:
            continue
        as_of = issued_12z(d)
        for variable, kind in (("temp_max", "max"), ("temp_min", "min")):
            official = nbm_eval.truth_value(t, variable)
            if official is None:
                continue
            rem = remaining_extreme(
                series["times"], series["values"], meta["tz"], d, as_of, kind,
                source=SOURCE,
            )
            if rem is None:
                continue
            resid[(icao, variable)].append(official - rem["extreme_f"])
    out = {}
    for k, vals in resid.items():
        if len(vals) >= 20:
            out[k] = max(0.5, statistics.pstdev(vals) if len(vals) > 1 else DEFAULT_SIGMA)
    return out


def score_standalone(
    hrrr_by: dict,
    cli: dict,
    stations: dict,
    sig: dict,
    start: date,
    end: date,
) -> list[dict]:
    """Cases synthétiques autour de l'extrême du matin, contre le CLI."""
    rows = []
    for (icao, d), series in hrrr_by.items():
        if d < start or d > end:
            continue
        meta = stations.get(icao)
        if not meta:
            continue
        t = cli.get((icao, d))
        as_of = issued_12z(d)
        for variable, kind in (("temp_max", "max"), ("temp_min", "min")):
            official = nbm_eval.truth_value(t, variable) if t else None
            if official is None:
                continue
            rem = remaining_extreme(
                series["times"], series["values"], meta["tz"], d, as_of, kind,
                source=SOURCE,
            )
            if rem is None:
                continue
            mu = rem["extreme_f"]
            sigma = max(SIGMA_FLOOR, sig.get((icao, variable), DEFAULT_SIGMA))
            for b in kalshi_style_bins(mu, n_central=6):
                if not b.is_central:
                    continue
                rows.append({
                    "station": icao, "variable": variable, "target": d,
                    "lead": 0, "issued": as_of, "outcome": b.contains(official),
                    "p_hrrr": prob_in_bin_gaussian(mu, sigma, b),
                    "p_station": None, "p_raw": None, "p_market": None,
                    "bin": b.label(), "n_hours": rem["n_hours"],
                    "pred": mu, "official": official,
                })
    return rows


def score_market(
    records: list[dict],
    hrrr_by: dict,
    cli: dict,
    stations: dict,
    sig: dict,
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
        if r["_snap"] < available_at(r["_target"]):
            skips["prix_avant_le_run_du_matin"] += 1
            continue
        t = cli.get((icao, r["_target"]))
        official = nbm_eval.truth_value(t, r["variable"]) if t else None
        if official is None:
            skips["pas_de_chiffre_officiel"] += 1
            continue
        series = hrrr_by.get((icao, r["_target"]))
        if not series:
            skips["pas_de_run_du_matin"] += 1
            continue
        kind = "max" if r["variable"] == "temp_max" else "min"
        rem = remaining_extreme(
            series["times"], series["values"], meta["tz"], r["_target"],
            issued_12z(r["_target"]), kind, source=SOURCE,
        )
        if rem is None:
            skips["pas_assez_d_heures"] += 1
            continue
        vals = list(r["_pm"].values())
        mu_raw = statistics.fmean(vals)
        sig_raw = max(SIGMA_FLOOR, statistics.pstdev(vals))
        b = Bin(int(r["lower"]), int(r["upper"]))
        y = b.contains(official)
        p_raw = prob_in_bin_gaussian(mu_raw, sig_raw, b)
        bs = bias.get(icao, r["variable"], 0, r["_snap"].date())
        if bs is None:
            skips["pas_encore_de_correction_ville"] += 1
            continue
        p_station = prob_in_bin_gaussian(mu_raw + bs[0], bs[1], b)
        sigma = max(SIGMA_FLOOR, sig.get((icao, r["variable"]), DEFAULT_SIGMA))
        p_hrrr = prob_in_bin_gaussian(rem["extreme_f"], sigma, b)
        rows.append({
            "station": icao, "variable": r["variable"], "target": r["_target"],
            "lead": 0, "issued": issued_12z(r["_target"]), "outcome": y,
            "p_hrrr": p_hrrr, "p_raw": p_raw, "p_station": p_station,
            "p_market": float(r["yes_mid"]), "bin": b.label(),
            "n_hours": rem["n_hours"], "pred": rem["extreme_f"],
            "official": official, "source": SOURCE,
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
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "hrrr_morning"))
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

    client = HrrrMorningClient()
    fetch_errors: list[dict] = []
    if args.skip_fetch:
        hrrr_by = {k: v for k, v in client.load_extracted().items() if k[0] in set(wanted)}
        print(f"Relu {client.extracted_path} ({len(hrrr_by)} runs HRRR matin)", flush=True)
        if not hrrr_by:
            print("Aucun run du matin en cache. Relancer sans --skip-fetch.")
            return 1
    else:
        hrrr_by, fetch_errors = client.fetch_range(start, end, stations=stations)
        if any((s.get("times") for s in hrrr_by.values())):
            client.persist_extracted(hrrr_by)
        if not any(s.get("times") for s in hrrr_by.values()):
            print("Aucun run du matin récupéré. Rien n'a été inventé.")
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            payload = {
                "generated": now, "verdict": "bloquée",
                "hrrr_note": HRRR_NOTE, "fetch_errors": fetch_errors,
                "n_rows": 0, "n_dates": 0, "promote": False,
            }
            (out_dir / "hrrr_morning_skill.json").write_text(
                json.dumps(payload, indent=2, default=str), encoding="utf-8")
            (out_dir / "hrrr_morning_skill.md").write_text(
                "# HRRR du matin même\n\nBloquée. Aucun chiffre inventé.\n"
                f"Échecs : {fetch_errors}\n",
                encoding="utf-8")
            return 1

    sig = train_sigma(hrrr_by, cli, stations, split)
    print(f"Sigma appris (avant {split}) : {len(sig)} paires station/variable", flush=True)

    standalone = score_standalone(hrrr_by, cli, stations, sig, start, end)
    hold_st = [r for r in standalone if split <= r["target"] <= A1_END]
    print(f"Lignes hors marché : {len(standalone)} (holdout A1 {len(hold_st)})", flush=True)

    fp_path = TRUTH_DIR / "skill" / "forecast_points.json"
    if not fp_path.exists():
        print(f"Points de prévision absents : {fp_path}.")
        return 2
    bias = mkt.PointInTimeBias(mkt.load_points(), cli)
    records = nowcast_eval.load_j0_records(start, end)
    print(f"Captures same-day cotées : {len(records)}", flush=True)

    market, skips = score_market(records, hrrr_by, cli, stations, sig, bias)
    hold_m = [r for r in market if r["target"] >= split]
    print(f"Lignes marché : {len(market)} (test {len(hold_m)}). Skips : {skips}", flush=True)

    fields_st = ("p_hrrr",)
    fields_m = ("p_hrrr", "p_station", "p_raw", "p_market")
    st_all = nbm_eval.summarize(standalone, lambda r: "all", fields_st) if standalone else {}
    st_hold = nbm_eval.summarize(hold_st, lambda r: "all", fields_st) if hold_st else {}
    st_var = nbm_eval.summarize(standalone, lambda r: r["variable"], fields_st) if standalone else {}
    mk_all = nbm_eval.summarize(market, lambda r: "all", fields_m) if market else {}
    mk_hold = nbm_eval.summarize(hold_m, lambda r: "all", fields_m) if hold_m else {}
    mk_var = nbm_eval.summarize(market, lambda r: r["variable"], fields_m) if market else {}
    mk_st = nbm_eval.summarize(market, lambda r: f"{r['station']}/{r['variable']}", fields_m) if market else {}

    tests = {}
    if market:
        tests["hrrr_vs_station"] = nbm_eval.sign_test_rows(market, "p_hrrr", "p_station")
        tests["hrrr_vs_market"] = nbm_eval.sign_test_rows(market, "p_hrrr", "p_market")
        tests["station_vs_market"] = nbm_eval.sign_test_rows(market, "p_station", "p_market")
    if hold_m:
        tests["hrrr_vs_station_hold"] = nbm_eval.sign_test_rows(hold_m, "p_hrrr", "p_station")
        tests["hrrr_vs_market_hold"] = nbm_eval.sign_test_rows(hold_m, "p_hrrr", "p_market")

    n_dates = len({r["target"] for r in market}) if market else 0
    n_hold_dates = len({r["target"] for r in hold_m}) if hold_m else 0
    mkt_test = tests.get("hrrr_vs_market") or {}
    promote = bool(
        n_dates >= MIN_MARKET_DAYS
        and mkt_test.get("p_one_sided") is not None
        and mkt_test["p_one_sided"] < 0.05
        and mkt_test.get("a_wins", 0) > mkt_test.get("dates", 0) / 2
        and mk_all.get("all", {}).get("brier_hrrr") is not None
        and mk_all["all"]["brier_hrrr"] < mk_all["all"].get("brier_market", 99)
        and mk_all["all"]["brier_hrrr"] < mk_all["all"].get("brier_station", 99)
    )
    if not market and not standalone:
        verdict = "bloquée"
    elif promote:
        verdict = "testée ça aide"
    else:
        verdict = "testée ça n'aide pas"

    n_hrrr_st = len({icao for (icao, _d), s in hrrr_by.items()
                     if any(v is not None for v in s.get("values") or [])})
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# HRRR du matin même contre le chiffre officiel et le marché",
        "",
        f"Généré : {now}. Run 12 h UTC du jour même, heures encore dans le "
        f"jour LST après 12 h. Vérité : chiffre officiel de la station "
        f"(même fichier que A1). Sigma appris avant {split}. "
        f"Prix notés seulement s'ils sont pris à {AVAILABLE_AFTER_UTC} h UTC "
        f"ou plus tard (le run est alors public). "
        f"Aucune heure manquante n'a été inventée.",
        "",
        HRRR_NOTE,
        "",
        "Ce fichier ne mélange pas la prévision de la veille. "
        "Il ne relance pas le thermomètre du jour.",
        "",
        f"Stations avec un run du matin : {n_hrrr_st}/{len(wanted)}.",
        f"Lignes hors marché : {len(standalone)}. "
        f"Holdout A1 ({split} → {A1_END}) : {len(hold_st)}.",
        f"Captures same-day lues : {len(records)}. Lignes marché : {len(market)} "
        f"({n_dates} jours). Jours de test (≥ {split}) : {n_hold_dates}.",
        f"Skips : {skips}.",
        f"Échecs de téléchargement : {len(fetch_errors)}.",
        f"Verdict : {verdict}. Promotion : {'oui' if promote else 'non'}.",
        "",
        "Le robot de paper-trading ne vise que demain. On n'a pas changé ça.",
        "",
        "Plus le score d'erreur est petit, mieux c'est.",
        "",
    ]
    cols_st = [("Brier HRRR matin", "brier_hrrr")]
    cols_m = [
        ("Brier HRRR matin", "brier_hrrr"),
        ("Brier correction ville", "brier_station"),
        ("Brier mélange", "brier_raw"),
        ("Brier prix", "brier_market"),
    ]
    if st_all:
        lines += _table("Hors marché, cases synthétiques autour du max/min du matin", st_all, "groupe", cols_st)
    if st_hold:
        lines += _table(f"Hors marché, holdout A1 ({split} → {A1_END})", st_hold, "groupe", cols_st)
    if st_var:
        lines += _table("Hors marché, par max / min", st_var, "variable", cols_st)
    if mk_all:
        lines += _table("Jour même avec un prix (après 13 h UTC)", mk_all, "groupe", cols_m)
    if mk_hold:
        lines += _table(f"Jour même, test (≥ {split})", mk_hold, "groupe", cols_m)
    if mk_var:
        lines += _table("Jour même, par max / min", mk_var, "variable", cols_m)
    if mk_st:
        lines += _table("Jour même, par station", mk_st, "station/variable", cols_m)

    def _test_line(name: str, t: dict) -> str:
        if not t:
            return f"- {name} : pas assez de jours"
        p = t.get("p_one_sided")
        ptxt = "n/a" if p is None else f"{p:.4f}"
        return (f"- {name} : {t.get('a_wins', 0)} jours sur {t.get('dates', 0)} "
                f"(p = {ptxt})")

    lines += ["### Combien de jours on gagne", ""]
    for key, label in (
        ("hrrr_vs_station", "HRRR matin contre correction ville"),
        ("hrrr_vs_market", "HRRR matin contre le prix"),
        ("station_vs_market", "correction ville contre le prix"),
        ("hrrr_vs_station_hold", "HRRR matin contre correction ville (test)"),
        ("hrrr_vs_market_hold", "HRRR matin contre le prix (test)"),
    ):
        lines.append(_test_line(label, tests.get(key) or {}))
    lines += [
        "",
        f"Règle : 30 jours minimum pour parler du marché. Jours avec prix et "
        f"HRRR du matin : {n_dates}. Promotion : {'oui' if promote else 'non'}.",
        "",
        "Le modèle en ligne n'est pas changé. Pas de pari avec de l'argent réel.",
        "",
    ]

    report = out_dir / "hrrr_morning_skill.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {
        "generated": now,
        "name": "HRRR du matin même",
        "source": SOURCE,
        "verdict": verdict,
        "split": split.isoformat(),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "n_hrrr_stations": n_hrrr_st,
        "n_records": len(records),
        "n_standalone": len(standalone),
        "n_standalone_holdout": len(hold_st),
        "n_rows": len(market),
        "n_dates": n_dates,
        "n_holdout_rows": len(hold_m),
        "n_holdout_dates": n_hold_dates,
        "skips": skips,
        "fetch_errors": fetch_errors,
        "hrrr_note": HRRR_NOTE,
        "available_after_utc": AVAILABLE_AFTER_UTC,
        "standalone": st_all,
        "standalone_holdout": st_hold,
        "standalone_by_variable": st_var,
        "all": mk_all,
        "holdout": mk_hold,
        "by_variable": mk_var,
        "by_station": mk_st,
        "tests": tests,
        "promote": promote,
        "min_market_days": MIN_MARKET_DAYS,
        "bot_skips_same_day": True,
        "champion_unchanged": True,
    }
    (out_dir / "hrrr_morning_skill.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"Écrit {report}", flush=True)
    print(f"Écrit {out_dir / 'hrrr_morning_skill.json'}", flush=True)
    print(f"Verdict : {verdict}. Promotion : {promote}.", flush=True)
    if not market and not standalone:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
