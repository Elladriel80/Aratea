"""eval_settlement_window_rounding.py — Fenêtre d'hiver et Degré entier.

FR : Mesure A/B des deux règles de paiement pas encore chiffrées le
12 septembre 2026. On ne retélécharge pas NBM, GEFS, le thermomètre du
jour, le siècle, les densités, ni NBM + correction ville.

A) Fenêtre d'hiver : max et min du jour en heure murale (heure d'été
   si elle est en vigueur) contre la même journée en heure standard
   locale (décalage d'hiver, toute l'année).
B) Degré entier : valeur continue / demi-degré contre l'arrondi entier
   NWS. Si les lectures locales sont déjà entières, on le dit.

Données par défaut : archive ASOS horaire déjà dans data/asos/extracted.json
(IEM, 18 stations Kalshi) et data/truth/cli_daily.json. Pas de chiffre
inventé.

EN : Settlement A/B only. Champion untouched.

Usage:
    python scripts/eval_settlement_window_rounding.py
    python scripts/eval_settlement_window_rounding.py --skip-fetch
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.truth.asos import IemAsosClient, from_compact  # noqa: E402
from src.truth.ghcn_daily import GhcnDailyClient, ICAO_TO_GHCN  # noqa: E402
from src.truth.iem_cli import CITY_TO_ICAO, STATION_TZ, TRUTH_DIR, kalshi_stations  # noqa: E402
from src.truth.settlement_ab import (  # noqa: E402
    aggregate_station_days,
    rounding_from_values,
    summarize_cli_times,
    summarize_rounding,
    summarize_window,
)

OUT_DIR = TRUTH_DIR / "settlement"
ASOS_EXTRACTED = ROOT / "data" / "asos" / "extracted.json"
CLI_DAILY = TRUTH_DIR / "cli_daily.json"
MIN_OBS = 18

ICAO_TO_CITY = {icao: city for city, icao in CITY_TO_ICAO.items()}
CITY_FR = {
    "ATLANTA": "Atlanta", "AUSTIN": "Austin", "BOSTON": "Boston",
    "CHICAGO": "Chicago", "DALLAS": "Dallas", "DENVER": "Denver",
    "HOUSTON": "Houston", "LASVEGAS": "Las Vegas", "LOSANGELES": "Los Angeles",
    "MIAMI": "Miami", "MINNEAPOLIS": "Minneapolis", "NYC": "New York",
    "PHILADELPHIA": "Philadelphie", "PHOENIX": "Phoenix",
    "SANANTONIO": "San Antonio", "SANFRANCISCO": "San Francisco",
    "SEATTLE": "Seattle", "WASHINGTON": "Washington",
}


def city_label(icao: str) -> str:
    return CITY_FR.get(ICAO_TO_CITY.get(icao, ""), icao)


def load_asos(path: Path) -> list:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [from_compact(r) for r in data]


def load_cli(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def asos_precision(obs) -> dict:
    """Les METAR horaires sont-ils déjà des entiers ? Rien d'inventé."""
    n = len(obs)
    non_int = 0
    frac = Counter()
    by_st: dict[str, list] = {}
    for o in obs:
        by_st.setdefault(o.station.upper(), []).append(o)
        if abs(o.tmp_f - round(o.tmp_f)) > 1e-9:
            non_int += 1
            frac[round(o.tmp_f - int(o.tmp_f), 2)] += 1
    extreme_non_int = 0
    extreme_days = 0
    for station, group in by_st.items():
        tz_name = STATION_TZ.get(station)
        if not tz_name:
            continue
        from src.truth.lst_window import lst_date
        buckets: dict[date, list[float]] = {}
        for o in group:
            buckets.setdefault(lst_date(o.valid, tz_name), []).append(o.tmp_f)
        for vals in buckets.values():
            if len(vals) < MIN_OBS:
                continue
            extreme_days += 1
            mx, mn = max(vals), min(vals)
            if abs(mx - round(mx)) > 1e-9 or abs(mn - round(mn)) > 1e-9:
                extreme_non_int += 1
    stations = sorted(by_st)
    dates = [o.valid.date() for o in obs] if obs else []
    return {
        "source": "IEM ASOS/METAR horaire (data/asos/extracted.json)",
        "n_readings": n,
        "n_stations": len(stations),
        "stations": stations,
        "first": min(dates).isoformat() if dates else None,
        "last": max(dates).isoformat() if dates else None,
        "non_integer_readings": non_int,
        "fractional_parts": {str(k): v for k, v in sorted(frac.items())},
        "n_lst_days_with_min_obs": extreme_days,
        "n_lst_days_extreme_non_integer": extreme_non_int,
    }


def rounding_from_asos_extremes(obs) -> list:
    """Extrême LST horaire, seulement s'il n'est pas déjà un entier.

    Sert à mesurer l'arrondi quand le METAR a encore un dixième.
    """
    from src.truth.lst_window import lst_date
    triples = []
    by_st: dict[str, list] = {}
    for o in obs:
        by_st.setdefault(o.station.upper(), []).append(o)
    for station, group in by_st.items():
        tz_name = STATION_TZ.get(station)
        if not tz_name:
            continue
        buckets: dict[date, list[float]] = {}
        for o in group:
            buckets.setdefault(lst_date(o.valid, tz_name), []).append(o.tmp_f)
        for d, vals in buckets.items():
            if len(vals) < MIN_OBS:
                continue
            mx, mn = max(vals), min(vals)
            triples.append((station, d, "temp_max", mx, "asos_hourly_lst"))
            triples.append((station, d, "temp_min", mn, "asos_hourly_lst"))
    return rounding_from_values(triples)


def rounding_from_ghcn(icaos: list[str], allow_network: bool) -> tuple[list, dict]:
    """GHCN-Daily : dixièmes de °C convertis en °F, sans ré-arrondir d'abord.

    Hypothèse (écrite comme telle) : pour les stations US, TMAX/TMIN GHCN
    sont souvent déjà convertis depuis un °F entier. On mesure quand même
    l'écart conversion continue vs entier NWS. On n'invente aucun jour
    manquant.
    """
    client = GhcnDailyClient()
    triples = []
    errors: list[str] = []
    fetched = 0
    for icao in icaos:
        if icao not in ICAO_TO_GHCN:
            errors.append(f"{icao}: pas d'ID GHCN")
            continue
        try:
            text = client.fetch_raw(
                ICAO_TO_GHCN[icao]["ghcn_id"],
                use_cache=True,
                allow_network=allow_network,
            )
        except Exception as e:  # noqa: BLE001
            errors.append(f"{icao}: {e}")
            continue
        fetched += 1
        triples.extend(_ghcn_continuous_from_dly(text, icao, ICAO_TO_GHCN[icao]["ghcn_id"]))
    return rounding_from_values(triples), {
        "source": "NCEI GHCN-Daily .dly (dixième de °C, conversion °F continue)",
        "n_stations_loaded": fetched,
        "errors": errors,
        "hypothesis": (
            "Les TMAX/TMIN USW sont souvent stockés depuis un °F entier. "
            "La partie fractionnaire après conversion peut être un artefact "
            "d'unité, pas un vrai demi-degré capteur."
        ),
    }


def _ghcn_continuous_from_dly(text: str, station: str, ghcn_id: str) -> list[tuple]:
    """TMAX/TMIN bruts en dixièmes de °C → °F continu. QFLAG non vide exclu."""
    from src.truth.ghcn_daily import MISSING
    from datetime import date as date_cls
    wanted = {"TMAX": "temp_max", "TMIN": "temp_min"}
    out = []
    for raw in text.splitlines():
        if len(raw) < 21:
            continue
        elem = raw[17:21]
        if elem not in wanted:
            continue
        try:
            year = int(raw[11:15])
            month = int(raw[15:17])
        except ValueError:
            continue
        for day in range(1, 32):
            base = 21 + (day - 1) * 8
            if base + 8 > len(raw):
                break
            try:
                val = int(raw[base:base + 5])
            except ValueError:
                continue
            qflag = raw[base + 6:base + 7]
            if val == MISSING or qflag.strip():
                continue
            try:
                valid = date_cls(year, month, day)
            except ValueError:
                continue
            f_cont = (val / 10.0) * 9.0 / 5.0 + 32.0
            out.append((station, valid, wanted[elem], f_cont, "ghcn_tenths_c"))
    return out


def maybe_fetch_asos(client: IemAsosClient, icaos: list[str],
                     start: date, end: date, skip: bool) -> tuple[list, list[str]]:
    """Recharge l'extrait local. Réseau seulement si --skip-fetch est absent
    et que l'extrait ne couvre pas la plage demandée."""
    rows = client.load_extracted()
    if not rows and ASOS_EXTRACTED.exists():
        rows = load_asos(ASOS_EXTRACTED)
    if skip:
        return rows, []
    if rows:
        have = {o.station.upper() for o in rows}
        if set(icaos) <= have:
            return rows, []
    all_rows = []
    failed_all: list[str] = []
    for icao in icaos:
        part, err = client.fetch_range(icao, start, end, use_cache=True)
        all_rows.extend(part)
        failed_all.extend(err)
    if all_rows:
        client.persist_extracted(all_rows)
    return all_rows, failed_all


def render_md(report: dict) -> str:
    w = report["fenetre_hiver"]
    r_asos = report["degre_entier"]["asos_hourly"]
    r_ghcn = report["degre_entier"].get("ghcn")
    cli_t = report["fenetre_hiver"].get("cli_printed_times") or {}
    lines = [
        "# Fenêtre d'hiver et Degré entier (comptes machine)",
        "",
        f"Date du run : {report['run_at']}",
        "Champion en ligne : non modifié. Aucun chiffre inventé.",
        "",
        "## Fenêtre d'hiver (ASOS horaire, LST vs heure murale)",
        "",
        f"Source : {report['fenetre_hiver']['source']}",
        f"Jours comparables : {w['summary']['n_comparable_days']}",
        f"Stations : {w['summary']['n_stations']}",
        f"Première / dernière : {w['summary']['first']} / {w['summary']['last']}",
        "",
        "| Ensemble | Jours | Max différent | Min différent | Entier max | Entier min | Case 2° |",
        "|---|---|---|---|---|---|---|",
    ]
    for key, label in (("all", "Tous"), ("dst_days", "Jours avec heure d'été"),
                       ("standard_days", "Jours sans heure d'été")):
        s = w["summary"][key]
        lines.append(
            f"| {label} | {s['n_days']} | {s['max_value_differs']} | "
            f"{s['min_value_differs']} | {s['max_int_differs']} | "
            f"{s['min_int_differs']} | {s['either_bin_differs']} |"
        )
    lines += [
        "",
        "### Par station",
        "",
        "| Ville | Jours | Max différent | Min différent | Case 2° |",
        "|---|---|---|---|---|",
    ]
    by_st = w["summary"]["by_station"]
    for icao in sorted(by_st, key=lambda k: (-by_st[k]["either_value_differs"], k)):
        s = by_st[icao]
        lines.append(
            f"| {city_label(icao)} | {s['n_days']} | {s['max_value_differs']} | "
            f"{s['min_value_differs']} | {s['either_bin_differs']} |"
        )
    lines += [
        "",
        "## Heures imprimées du CLI (complément, pas un changement de valeur)",
        "",
        f"Jours CLI : {cli_t.get('n_cli_days', 0)}",
        f"Max à 00:xx en heure d'été : {cli_t.get('high_disputed', 0)} "
        f"sur {cli_t.get('high_readable', 0)} heures lisibles",
        f"Min à 00:xx en heure d'été : {cli_t.get('low_disputed', 0)} "
        f"sur {cli_t.get('low_readable', 0)} heures lisibles",
        f"Heures max illisibles : {cli_t.get('high_unreadable', 0)} ; "
        f"min illisibles : {cli_t.get('low_unreadable', 0)}",
        "",
        "## Degré entier",
        "",
        "### METAR horaire déjà dans le dépôt",
        "",
        f"Lectures : {r_asos['precision']['n_readings']}",
        f"Lectures non entières : {r_asos['precision']['non_integer_readings']}",
        f"Jours LST avec assez de lectures : {r_asos['precision']['n_lst_days_with_min_obs']}",
        f"Jours dont le max ou le min horaire n'est pas entier : "
        f"{r_asos['precision']['n_lst_days_extreme_non_integer']}",
    ]
    if r_ghcn and r_ghcn.get("summary"):
        g = r_ghcn["summary"]["all"]
        lines += [
            "",
            "### GHCN-Daily (dixième de °C → °F continu)",
            "",
            r_ghcn.get("meta", {}).get("hypothesis", ""),
            f"Jours × variables : {g['n']}",
            f"Déjà un entier °F : {g['already_integer']}",
            f"Exactement x.5 : {g['exactly_half']}",
            f"Entier NWS ≠ partie entière : {g['int_vs_floor']}",
            f"Entier NWS ≠ arrondi Python : {g['int_vs_banker']}",
            f"Case 2° différente (entier vs partie entière) : {g['bin_vs_floor']}",
            f"Case 2° différente (entier vs demi-degré puis partie entière) : "
            f"{g['bin_vs_half_floor']}",
        ]
        if r_ghcn.get("meta", {}).get("errors"):
            lines.append("Erreurs GHCN : " + " ; ".join(r_ghcn["meta"]["errors"]))
    else:
        lines += [
            "",
            "### GHCN-Daily",
            "",
            "Non mesuré ici (cache absent et pas de réseau, ou chargement vide).",
        ]
    blocked = report.get("blocked") or []
    if blocked:
        lines += ["", "## Ce qui a bloqué", ""]
        lines.extend(f"- {b}" for b in blocked)
    lines += [
        "",
        "Aucun pari avec de l'argent réel. Le modèle en ligne n'est pas changé.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Mesure Fenêtre d'hiver et Degré entier")
    parser.add_argument("--skip-fetch", action="store_true",
                        help="ne rien télécharger ; seulement les fichiers locaux")
    parser.add_argument("--skip-ghcn", action="store_true",
                        help="ne pas charger GHCN même si le cache est là")
    parser.add_argument("--stations", default="",
                        help="ICAO séparés par des virgules (vide = 18 villes Kalshi)")
    parser.add_argument("--min-obs", type=int, default=MIN_OBS)
    parser.add_argument("--asos-path", default=str(ASOS_EXTRACTED))
    parser.add_argument("--cli-path", default=str(CLI_DAILY))
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    args = parser.parse_args()

    stations = kalshi_stations()
    if args.stations.strip():
        icaos = [s.strip().upper() for s in args.stations.split(",") if s.strip()]
    else:
        icaos = sorted(stations)

    blocked: list[str] = []
    asos_path = Path(args.asos_path)
    obs = load_asos(asos_path)
    fetch_errors: list[str] = []
    if not args.skip_fetch and not obs:
        client = IemAsosClient()
        obs, fetch_errors = maybe_fetch_asos(
            client, icaos, date(2026, 5, 1), date(2026, 9, 12), skip=False)
    if not obs:
        blocked.append(
            "Fenêtre d'hiver : aucune lecture ASOS locale "
            f"({asos_path}). Il faut data/asos/extracted.json "
            "(IEM ASOS/METAR horaire, déjà produit par eval_nowcast_skill.py)."
        )

    wanted = set(icaos)
    obs = [o for o in obs if o.station.upper() in wanted]

    window_rows = aggregate_station_days(obs, min_obs=args.min_obs) if obs else []
    window_summary = summarize_window(window_rows)
    precision = asos_precision(obs) if obs else {
        "n_readings": 0, "non_integer_readings": 0,
        "n_lst_days_with_min_obs": 0, "n_lst_days_extreme_non_integer": 0,
        "stations": [], "first": None, "last": None, "fractional_parts": {},
        "source": "absent", "n_stations": 0,
    }

    cli_rows = load_cli(Path(args.cli_path))
    cli_rows = [r for r in cli_rows if str(r.get("station") or "").upper() in wanted]
    cli_times = summarize_cli_times(cli_rows) if cli_rows else {
        "n_cli_days": 0, "high_disputed": 0, "low_disputed": 0,
        "high_readable": 0, "low_readable": 0,
        "high_unreadable": 0, "low_unreadable": 0, "by_station": {},
        "first": None, "last": None,
        "note": "cli_daily.json absent ou vide",
    }
    if not cli_rows:
        blocked.append(
            "Complément heures CLI : data/truth/cli_daily.json absent. "
            "Lancer build_station_truth.py pour le produire."
        )

    asos_round_rows = rounding_from_asos_extremes(obs) if obs else []
    asos_round = summarize_rounding(asos_round_rows)

    ghcn_block = None
    if not args.skip_ghcn:
        ghcn_rows, ghcn_meta = rounding_from_ghcn(icaos, allow_network=not args.skip_fetch)
        if ghcn_rows:
            ghcn_block = {"meta": ghcn_meta, "summary": summarize_rounding(ghcn_rows)}
        else:
            blocked.append(
                "Degré entier GHCN : pas de fichier .dly en cache et/ou "
                "réseau refusé. Source minimale pour débloquer : "
                "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/{USW}.dly "
                "pour les 18 stations, ou archive ASOS 1 minute IEM "
                "(températures au dixième)."
            )
            ghcn_block = {"meta": ghcn_meta, "summary": None}
    else:
        blocked.append("Degré entier GHCN : --skip-ghcn, non mesuré.")

    if precision["n_lst_days_extreme_non_integer"] == 0 and precision["n_readings"]:
        blocked.append(
            "Degré entier sur le max/min quotidien : les METAR horaires du "
            "dépôt sont déjà des degrés entiers (sauf quelques lectures isolées "
            "qui n'étaient pas l'extrême du jour). Pour mesurer un vrai "
            "demi-degré capteur, il manque l'ASOS 1 minute IEM/NCEI."
        )

    run = {
        "run_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "champion_untouched": True,
        "min_obs": args.min_obs,
        "stations_requested": icaos,
        "fetch_errors": fetch_errors,
        "blocked": blocked,
        "fenetre_hiver": {
            "variable": "Fenêtre d'hiver",
            "source": "IEM ASOS/METAR horaire déjà dans data/asos/extracted.json",
            "method": (
                "Même lectures. Jour A = date en heure murale (DST). "
                "Jour B = date en heure standard locale (lst_window)."
            ),
            "summary": window_summary,
            "cli_printed_times": cli_times,
        },
        "degre_entier": {
            "variable": "Degré entier",
            "asos_hourly": {
                "precision": precision,
                "daily_extremes": asos_round,
            },
            "ghcn": ghcn_block,
            "nws_rounding": "apply_nws_rounding half-up (75.5 → 76, 76.5 → 77)",
        },
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "settlement_ab.json"
    md_path = out_dir / "settlement_ab.md"
    json_path.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_md(run), encoding="utf-8")

    all_s = window_summary["all"]
    print(
        f"Fenêtre d'hiver : {all_s['n_days']} jours comparables, "
        f"max différent {all_s['max_value_differs']}, "
        f"min différent {all_s['min_value_differs']}.",
        flush=True,
    )
    print(
        f"Degré entier METAR : {precision['non_integer_readings']} lectures "
        f"non entières / {precision['n_readings']}.",
        flush=True,
    )
    if ghcn_block and ghcn_block.get("summary"):
        g = ghcn_block["summary"]["all"]
        print(
            f"Degré entier GHCN : {g['n']} valeurs, "
            f"case 2° vs partie entière {g['bin_vs_floor']}.",
            flush=True,
        )
    print(f"Écrit : {json_path}", flush=True)
    print(f"Écrit : {md_path}", flush=True)
    if blocked:
        print("Limites :", flush=True)
        for b in blocked:
            print(f"  - {b}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
