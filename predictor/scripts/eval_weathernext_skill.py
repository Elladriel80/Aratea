"""eval_weathernext_skill.py — WeatherNext 3 (et 2 si 3 bloquée) contre le CLI.

FR : On cherche d'abord WeatherNext 3 (Google, août 2026). S'il est
bloqué, on mesure la version la plus proche vraiment disponible
(WeatherNext 2 via Open-Meteo), clairement étiquetée. J0 et J-1 restent
séparés. Aucun chiffre manquant n'est inventé. Le champion en ligne
n'est pas touché. Pas de pari avec de l'argent réel.

EN : Measure WeatherNext 3 if reachable; otherwise score Open-Meteo
WeatherNext 2 and say so. J0 and J-1 stay separate. Champion unchanged.

Usage:
    python scripts/eval_weathernext_skill.py
    python scripts/eval_weathernext_skill.py --skip-fetch
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

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

import eval_nbm_skill as nbm_eval  # noqa: E402
from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, kalshi_stations  # noqa: E402
from src.truth.skill import SIGMA_FLOOR_F  # noqa: E402
from src.truth.synthetic_bins import (  # noqa: E402
    Bin, kalshi_style_bins, prob_in_bin_gaussian, prob_in_bin_members,
)
from src.weather.weathernext import (  # noqa: E402
    ENSEMBLE_BASE, GCS_URLS, HISTORICAL_FORECAST_BASE, PREVIOUS_RUNS_BASE,
    SINGLE_RUNS_BASE, WN2_LABEL, WN2_OM_MODEL, WN3_ACCESS_FORM, WN3_BQ_TABLE,
    WN3_LABEL, WN3_OM_CANDIDATES, WeatherNextOpenMeteo, gcp_env_status,
    http_probe, lead_name, member_daily_values, member_fill_summary,
    open_meteo_probe,
)

MIN_MEMBERS = 10
DEFAULT_HIST_START = date(2026, 9, 8)
DEFAULT_HIST_END = date(2026, 9, 12)
SINGLE_RUN_TRIES = ("2026-08-03T00:00", "2026-09-01T00:00", "2026-09-11T00:00",
                    "2026-09-12T00:00")


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


def probe_wn3() -> dict:
    """Sondes WeatherNext 3 : Open-Meteo, GCS, credentials. Zéro score ici."""
    om = []
    for model in WN3_OM_CANDIDATES:
        print(f"   sonde Open-Meteo Ensemble {model} ...", flush=True)
        om.append(open_meteo_probe(ENSEMBLE_BASE, model, extra={"past_days": 3}))
    gcs = []
    for url in GCS_URLS:
        print(f"   sonde GCS {url} ...", flush=True)
        gcs.append(http_probe(url))
    env = gcp_env_status()
    om_ok = [p for p in om if p.get("status") == 200 and (p.get("fill") or {}).get("n_filled_cells")]
    gcs_ok = [p for p in gcs if p.get("status") == 200]
    blocked = not om_ok and not gcs_ok and not env["GOOGLE_APPLICATION_CREDENTIALS_set"]
    reasons = []
    if not om_ok:
        reasons.append(
            "Open-Meteo refuse tous les noms WeatherNext 3 essayés "
            f"({', '.join(WN3_OM_CANDIDATES)})."
        )
    if not gcs_ok:
        statuses = sorted({str(p.get("status")) for p in gcs})
        reasons.append(
            "Les seaux GCS weathernext3_spatial, weathernext3_statistics_spatial "
            f"et weathernext répondent {statuses} sans compte Google autorisé."
        )
    if not env["GOOGLE_APPLICATION_CREDENTIALS_set"]:
        reasons.append(
            "Pas de GOOGLE_APPLICATION_CREDENTIALS : BigQuery "
            f"{WN3_BQ_TABLE} et Earth Engine sont inaccessibles ici."
        )
    return {
        "label": WN3_LABEL,
        "blocked": blocked,
        "open_meteo": om,
        "gcs": gcs,
        "gcp_env": env,
        "reasons": reasons,
        "minimal_next_fetch": {
            "step_1": "Remplir le formulaire Google WeatherNext avec l'e-mail du compte GCP.",
            "form": WN3_ACCESS_FORM,
            "step_2": "Attendre l'ajout à la liste (Google indique 5 à 7 jours ouvrés).",
            "step_3": (
                f"Lire la table BigQuery {WN3_BQ_TABLE} (ou le zarr GCS "
                "weathernext3_spatial) aux 18 stations, inits 00z/12z, "
                "membres ou percentiles, sur au moins 30 jours distincts, "
                "J0 et J-1 séparés."
            ),
            "step_4": "Relancer ce script avec les credentials. Ne pas inventer de scores avant.",
        },
    }


def probe_wn2_paths(lat: float, lon: float) -> dict:
    """Couverture réelle WeatherNext 2 (pas un score)."""
    print("   sonde WeatherNext 2 Ensemble live ...", flush=True)
    ens = open_meteo_probe(ENSEMBLE_BASE, WN2_OM_MODEL,
                           extra={"past_days": 7, "forecast_days": 2}, lat=lat, lon=lon)
    print("   sonde WeatherNext 2 Historical Forecast ...", flush=True)
    hist = _hist_probe(lat, lon, date(2026, 8, 3), date(2026, 8, 6))
    hist_recent = _hist_probe(lat, lon, date(2026, 9, 8), date(2026, 9, 12))
    print("   sonde WeatherNext 2 Previous Runs J-1 ...", flush=True)
    prev = _prev_probe(lat, lon, date(2026, 9, 8), date(2026, 9, 12), lead=1)
    print("   sonde WeatherNext 2 Single Runs ...", flush=True)
    singles = []
    for run in SINGLE_RUN_TRIES:
        singles.append(open_meteo_probe(
            SINGLE_RUNS_BASE, WN2_OM_MODEL,
            extra={"run": run, "forecast_days": 2}, lat=lat, lon=lon,
        ))
    return {
        "label": WN2_LABEL,
        "model": WN2_OM_MODEL,
        "ensemble_live": {k: ens.get(k) for k in ("status", "error", "fill", "body") if k in ens},
        "historical_holdout_aug": hist,
        "historical_recent": hist_recent,
        "previous_day1_recent": prev,
        "single_runs": [{k: s.get(k) for k in ("status", "error", "body", "fill") if k in s}
                        | {"run": run}
                        for s, run in zip(singles, SINGLE_RUN_TRIES)],
    }


def _om_fill(base: str, params: dict) -> dict:
    url = f"{base}?{__import__('urllib.parse', fromlist=['urlencode']).urlencode({k: v for k, v in params.items() if v is not None})}"
    try:
        r = __import__("requests").get(
            url, timeout=60,
            headers={"User-Agent": "aratea-predictor/0.1 (+https://github.com/Elladriel80/aratea)"},
        )
        if r.status_code != 200:
            return {"status": r.status_code, "body": (r.text or "")[:300], "fill": None}
        data = r.json()
        hourly = data.get("hourly") or {}
        variable = str(params.get("hourly") or "temperature_2m").split(",")[0]
        return {"status": 200, "fill": member_fill_summary(hourly, variable), "body": ""}
    except Exception as e:  # noqa: BLE001
        return {"status": None, "error": str(e), "fill": None}


def _hist_probe(lat: float, lon: float, start: date, end: date) -> dict:
    return _om_fill(HISTORICAL_FORECAST_BASE, {
        "latitude": lat, "longitude": lon, "hourly": "temperature_2m",
        "models": WN2_OM_MODEL, "start_date": start.isoformat(),
        "end_date": end.isoformat(), "timezone": "GMT",
        "temperature_unit": "fahrenheit",
    })


def _prev_probe(lat: float, lon: float, start: date, end: date, lead: int) -> dict:
    return _om_fill(PREVIOUS_RUNS_BASE, {
        "latitude": lat, "longitude": lon,
        "hourly": f"temperature_2m_previous_day{lead}",
        "models": WN2_OM_MODEL, "start_date": start.isoformat(),
        "end_date": end.isoformat(), "timezone": "GMT",
        "temperature_unit": "fahrenheit",
    })


def collect_extremes(
    client: WeatherNextOpenMeteo,
    stations: dict,
    start: date,
    end: date,
    kind: str,
) -> tuple[dict, dict]:
    """kind = 'hist' (J0) ou 'prev1' (J-1)."""
    out: dict[tuple, list[float]] = {}
    coverage: dict[str, dict] = {}
    targets = []
    d = start
    while d <= end:
        targets.append(d)
        d += timedelta(days=1)
    for icao, meta in stations.items():
        if kind == "hist":
            members = client.fetch_historical(meta["lat"], meta["lon"], start, end)
        else:
            members = client.fetch_previous_day(meta["lat"], meta["lon"], start, end, lead=1)
        n_mem = len(members)
        days_ok = []
        for target in targets:
            for variable, ext in (("temp_max", "max"), ("temp_min", "min")):
                vals = member_daily_values(members, meta["tz"], target, ext)
                if vals:
                    out[(icao, variable, target, 0 if kind == "hist" else 1)] = vals
                    days_ok.append(target.isoformat())
        coverage[icao] = {
            "n_member_series": n_mem,
            "n_days_with_extreme": len(set(days_ok)),
            "days": sorted(set(days_ok)),
        }
        print(f"   {icao} {kind}: {n_mem} membres, "
              f"{coverage[icao]['n_days_with_extreme']} jours avec extrême",
              flush=True)
    return out, coverage


def score_vs_cli(extremes: dict, cli: dict, lead: int) -> list[dict]:
    rows = []
    for (icao, variable, target, led), vals in extremes.items():
        if led != lead or len(vals) < MIN_MEMBERS:
            continue
        t = cli.get((icao, target))
        obs = nbm_eval.truth_value(t, variable) if t else None
        if obs is None:
            continue
        mu = statistics.fmean(vals)
        for b in kalshi_style_bins(mu, n_central=6):
            if not b.is_central:
                continue
            rows.append({
                "station": icao, "variable": variable, "target": target,
                "lead": lead, "horizon": lead_name(lead),
                "outcome": b.contains(obs),
                "p_wn": prob_in_bin_members(vals, b),
                "p_raw": None, "p_market": None,
                "bin": b.label(), "n_members": len(vals),
            })
    return rows


def score_market(extremes: dict, cli: dict, lead: int) -> tuple[list[dict], dict]:
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
            snap = datetime.strptime(r["snapshot_at"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            led = (target - snap.date()).days
            if led != lead:
                continue
            key = (r["ticker"], lead)
            if key in seen:
                continue
            seen[key] = {**r, "_target": target, "_lead": led, "_pm": pm}

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
        vals = extremes.get((icao, r["variable"], r["_target"], lead))
        if not vals or len(vals) < MIN_MEMBERS:
            skips["no_wn_members"] += 1
            continue
        b = Bin(int(r["lower"]), int(r["upper"]))
        raw_vals = list(r["_pm"].values()) if r["_pm"] else []
        p_raw = None
        if len(raw_vals) >= 2:
            p_raw = prob_in_bin_gaussian(
                statistics.fmean(raw_vals),
                max(SIGMA_FLOOR_F, statistics.pstdev(raw_vals)), b)
        rows.append({
            "station": icao, "variable": r["variable"], "target": r["_target"],
            "lead": lead, "horizon": lead_name(lead),
            "outcome": b.contains(obs),
            "p_wn": prob_in_bin_members(vals, b),
            "p_raw": p_raw, "p_market": float(r["yes_mid"]),
            "bin": b.label(), "n_members": len(vals),
        })
    return rows, dict(skips)


def _dates(rows: list[dict]) -> list[str]:
    return sorted({r["target"].isoformat() for r in rows})


def verdict_text(wn3: dict, j0_dates: int, j1_dates: int) -> str:
    """Verdict du levier nommé WeatherNext 3. Pas un jugement sur WN2 seul."""
    if wn3.get("blocked"):
        return "pas encore mesurable (bloquée)"
    if j0_dates >= 30 or j1_dates >= 30:
        return "mesurée (voir les scores ; promotion seulement si les portes du projet sont franchies)"
    return "pas encore mesurable (bloquée)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", default=DEFAULT_HIST_START.isoformat())
    ap.add_argument("--end", default=DEFAULT_HIST_END.isoformat())
    ap.add_argument("--stations", default="")
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "weathernext"))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    station_meta = {k: v for k, v in stations.items() if k in set(wanted)}
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = out_dir / "om_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    cli_path = TRUTH_DIR / "cli_daily.json"
    if not cli_path.exists():
        print(f"Vérité CLI absente : {cli_path}. Lancer d'abord build_station_truth.py.")
        return 2
    cli = nbm_eval.load_cli(cli_path)

    print("=== WeatherNext 3 : sondes ===", flush=True)
    wn3 = probe_wn3()
    print("   bloquée" if wn3["blocked"] else "   accessible", flush=True)

    probe_st = next(iter(station_meta.values()))
    print("=== WeatherNext 2 : sondes de couverture ===", flush=True)
    wn2_probe = probe_wn2_paths(probe_st["lat"], probe_st["lon"])

    hist_ext: dict = {}
    prev_ext: dict = {}
    hist_cov: dict = {}
    prev_cov: dict = {}
    client = WeatherNextOpenMeteo(cache_dir=cache_dir)
    if args.skip_fetch:
        ext_path = out_dir / "daily_extremes.json"
        if not ext_path.exists():
            print("Aucun extrême en cache. Relancer sans --skip-fetch.")
            return 1
        saved = json.loads(ext_path.read_text(encoding="utf-8"))
        for row in saved.get("hist") or []:
            key = (row["station"], row["variable"], date.fromisoformat(row["target"]), 0)
            hist_ext[key] = list(row["values"])
        for row in saved.get("prev1") or []:
            key = (row["station"], row["variable"], date.fromisoformat(row["target"]), 1)
            prev_ext[key] = list(row["values"])
        hist_cov = saved.get("hist_coverage") or {}
        prev_cov = saved.get("prev_coverage") or {}
        print(f"Relu {ext_path} ({len(hist_ext)} groupes J0, {len(prev_ext)} groupes J-1)")
    else:
        print("=== Téléchargement WeatherNext 2 Historical Forecast (J0) ===", flush=True)
        hist_ext, hist_cov = collect_extremes(client, station_meta, start, end, "hist")
        print("=== Téléchargement WeatherNext 2 Previous Runs J-1 ===", flush=True)
        prev_ext, prev_cov = collect_extremes(client, station_meta, start, end, "prev1")
        packed = {
            "hist": [
                {"station": k[0], "variable": k[1], "target": k[2].isoformat(),
                 "lead": 0, "values": v}
                for k, v in sorted(hist_ext.items(), key=lambda kv: (kv[0][0], kv[0][2].isoformat(), kv[0][1]))
            ],
            "prev1": [
                {"station": k[0], "variable": k[1], "target": k[2].isoformat(),
                 "lead": 1, "values": v}
                for k, v in sorted(prev_ext.items(), key=lambda kv: (kv[0][0], kv[0][2].isoformat(), kv[0][1]))
            ],
            "hist_coverage": hist_cov,
            "prev_coverage": prev_cov,
        }
        (out_dir / "daily_extremes.json").write_text(
            json.dumps(packed, indent=2), encoding="utf-8"
        )

    j0_cli = score_vs_cli(hist_ext, cli, lead=0)
    j1_cli = score_vs_cli(prev_ext, cli, lead=1)
    j0_mkt, j0_skips = score_market(hist_ext, cli, lead=0)
    j1_mkt, j1_skips = score_market(prev_ext, cli, lead=1)

    fields_cli = ("p_wn",)
    fields_mkt = ("p_wn", "p_raw", "p_market")
    j0_all = nbm_eval.summarize(j0_cli, lambda r: "J0", fields_cli)
    j1_all = nbm_eval.summarize(j1_cli, lambda r: "J-1", fields_cli)
    j0_var = nbm_eval.summarize(j0_cli, lambda r: r["variable"], fields_cli)
    j0_mkt_all = nbm_eval.summarize(j0_mkt, lambda r: "J0", fields_mkt)
    j1_mkt_all = nbm_eval.summarize(j1_mkt, lambda r: "J-1", fields_mkt)

    tests = {}
    if j0_mkt:
        tests["wn2_j0_vs_market"] = nbm_eval.sign_test_rows(j0_mkt, "p_wn", "p_market")
        tests["wn2_j0_vs_champion"] = nbm_eval.sign_test_rows(j0_mkt, "p_wn", "p_raw")
    if j1_mkt:
        tests["wn2_j1_vs_market"] = nbm_eval.sign_test_rows(j1_mkt, "p_wn", "p_market")
        tests["wn2_j1_vs_champion"] = nbm_eval.sign_test_rows(j1_mkt, "p_wn", "p_raw")

    n_j0 = len({r["target"] for r in j0_cli})
    n_j1 = len({r["target"] for r in j1_cli})
    verdict = verdict_text(wn3, n_j0, n_j1)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        "# WeatherNext 3 : mesure (ou blocage)",
        "",
        f"Généré : {now}. Fenêtre Open-Meteo demandée {start} → {end}.",
        "Nom stable du levier : WeatherNext 3.",
        f"Verdict : {verdict}.",
        "",
        "Le champion en ligne n'est pas changé. Le site public n'est pas changé.",
        "Pas de pari avec de l'argent réel. Aucun chiffre manquant n'a été inventé.",
        "",
        "## WeatherNext 3",
        "",
    ]
    if wn3["blocked"]:
        lines += ["Bloquée. Rien n'a été noté avec ce modèle.", ""]
        for r in wn3["reasons"]:
            lines.append(f"- {r}")
        lines += [
            "",
            "Prochain fetch minimal pour débloquer :",
            f"1. Formulaire : {WN3_ACCESS_FORM}",
            "2. Attendre l'autorisation Google (ils indiquent 5 à 7 jours ouvrés).",
            f"3. Lire {WN3_BQ_TABLE} (ou GCS weathernext3_spatial) aux 18 stations, "
            "J0 et J-1 séparés, au moins 30 jours distincts.",
            "4. Relancer ce script avec le compte autorisé.",
            "",
        ]
    else:
        lines += ["Accessible. Voir les scores ci-dessous.", ""]

    hist_days = (wn2_probe.get("historical_recent") or {}).get("fill") or {}
    prev_days = (wn2_probe.get("previous_day1_recent") or {}).get("fill") or {}
    lines += [
        "## Version la plus proche disponible : WeatherNext 2 (Open-Meteo)",
        "",
        f"Modèle API : `{WN2_OM_MODEL}`. Ce n'est pas WeatherNext 3 "
        "(pas de grille 0,05°, pas d'init horaire, pas de table BigQuery station).",
        "",
        "Historical Forecast (premières heures de chaque run, donc J0 approximatif) : "
        f"jours remplis {hist_days.get('filled_days')}. "
        f"Holdout d'août (3-6 août) : "
        f"{((wn2_probe.get('historical_holdout_aug') or {}).get('fill') or {}).get('n_filled_cells', 0)} "
        "cellules remplies (zéro = pas d'archive longue).",
        "",
        "Previous Runs `previous_day1` (J-1) : "
        f"cellules remplies {(prev_days.get('n_filled_cells'))}. "
        "Vide = J-1 pas mesurable avec Open-Meteo.",
        "",
        "Single Runs : les runs demandés n'ont pas été servis (voir weathernext_skill.json).",
        "",
        "On note seulement les jours où les membres sont remplis et où le CLI existe.",
        "J0 et J-1 ne sont pas mélangés.",
        "",
    ]
    lines += _table(
        "J0 : WeatherNext 2 contre le chiffre officiel (bins synthétiques)",
        j0_all, "horizon",
        [("Brier WeatherNext 2", "brier_wn")],
    )
    lines += _table(
        "J-1 : WeatherNext 2 contre le chiffre officiel",
        j1_all, "horizon",
        [("Brier WeatherNext 2", "brier_wn")],
    )
    if not j1_cli:
        lines += [
            "J-1 : aucune ligne. Previous Runs n'a renvoyé aucun membre rempli.",
            "Pas de score J-1, pas de score inventé.",
            "",
        ]
    lines += _table(
        "J0 par max / min",
        j0_var, "variable",
        [("Brier WeatherNext 2", "brier_wn")],
    )
    if j0_mkt_all:
        lines += [
            f"Prix de marché J0 (kalshi_mid le jour même). Lignes écartées : {j0_skips}.",
            "",
        ]
        lines += _table(
            "J0 contre le prix et le mélange actuel",
            j0_mkt_all, "horizon",
            [("Brier WeatherNext 2", "brier_wn"),
             ("Brier mélange (champion)", "brier_raw"),
             ("Brier marché", "brier_market")],
        )
    else:
        lines += [f"J0 marché : aucune ligne. Écarts : {j0_skips}.", ""]
    if j1_mkt_all:
        lines += [
            f"Prix de marché J-1 (kalshi_mid la veille). Lignes écartées : {j1_skips}.",
            "",
        ]
        lines += _table(
            "J-1 contre le prix et le mélange actuel",
            j1_mkt_all, "horizon",
            [("Brier WeatherNext 2", "brier_wn"),
             ("Brier mélange (champion)", "brier_raw"),
             ("Brier marché", "brier_market")],
        )
    else:
        lines += [
            "J-1 marché : aucune ligne WeatherNext 2 (membres J-1 absents). "
            f"Écarts : {j1_skips}.",
            "",
        ]
    if tests:
        lines += ["### Victoires jour par jour (WeatherNext 2 seulement)", "",
                  "| comparaison | jours | victoires du premier | chance que ce soit le hasard |",
                  "|---|---|---|---|"]
        for name, t in tests.items():
            lines.append(
                f"| {name} | {t['dates']} | {t['a_wins']} | {_fmt(t['p_one_sided'])} |"
            )
        lines.append("")
    lines += [
        f"Jours J0 notés (CLI) : {n_j0} ({', '.join(_dates(j0_cli)) or 'aucun'}).",
        f"Jours J-1 notés (CLI) : {n_j1} ({', '.join(_dates(j1_cli)) or 'aucun'}).",
        "La règle du projet demande de battre le marché sur au moins 30 jours distincts.",
        "On ne change pas le modèle en ligne.",
        "",
    ]

    report = "\n".join(lines) + "\n"
    (out_dir / "weathernext_skill.md").write_text(report, encoding="utf-8")
    payload = {
        "schema": "weathernext_skill/1",
        "generated_at": now,
        "lever_name": WN3_LABEL,
        "verdict": verdict,
        "champion_changed": False,
        "params": {
            "start": start.isoformat(), "end": end.isoformat(),
            "stations": wanted, "wn2_model": WN2_OM_MODEL,
            "min_members": MIN_MEMBERS,
        },
        "weather_next_3": {
            "blocked": wn3["blocked"],
            "reasons": wn3["reasons"],
            "gcp_env": wn3["gcp_env"],
            "open_meteo_statuses": [
                {"model": p.get("model"), "status": p.get("status"),
                 "body": (p.get("body") or "")[:180]}
                for p in wn3["open_meteo"]
            ],
            "gcs_statuses": [
                {"url": p.get("url"), "status": p.get("status"),
                 "body": (p.get("body") or "")[:180], "error": p.get("error")}
                for p in wn3["gcs"]
            ],
            "minimal_next_fetch": wn3["minimal_next_fetch"],
        },
        "weather_next_2": {
            "label": WN2_LABEL,
            "model": WN2_OM_MODEL,
            "probe": wn2_probe,
            "hist_coverage": hist_cov,
            "prev_coverage": prev_cov,
            "open_meteo_failures": dict(client.failures),
        },
        "n_rows_j0_cli": len(j0_cli),
        "n_rows_j1_cli": len(j1_cli),
        "n_rows_j0_market": len(j0_mkt),
        "n_rows_j1_market": len(j1_mkt),
        "j0_cli_dates": _dates(j0_cli),
        "j1_cli_dates": _dates(j1_cli),
        "j0_market_dates": _dates(j0_mkt),
        "j1_market_dates": _dates(j1_mkt),
        "market_skips_j0": j0_skips,
        "market_skips_j1": j1_skips,
        "j0_cli": j0_all,
        "j1_cli": j1_all,
        "j0_by_variable": j0_var,
        "j0_market": j0_mkt_all,
        "j1_market": j1_mkt_all,
        "sign_tests": tests,
    }
    (out_dir / "weathernext_skill.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    print(report)
    if wn3["blocked"] and not j0_cli and not j1_cli:
        print("WeatherNext 3 bloquée et aucune ligne WeatherNext 2 notée.")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
