"""build_station_truth.py — vérité CLI par station + audit ERA5 vs CLI.

FR : Télécharge (avec cache) les rapports climatologiques quotidiens du NWS
pour les 18 stations de résolution Kalshi via l'archive IEM, écrit un
fichier compact `data/truth/cli_daily.json`, mesure l'écart entre la
« vérité » ERA5 utilisée jusqu'ici par la climatologie (Open-Meteo archive)
et la vérité CLI réelle, puis joint cette vérité au ledger paper et aux
prévisions déjà stockées.

EN : Downloads (cached) the NWS Daily Climate Reports for the 18 Kalshi
resolution stations from the IEM archive, writes a compact
`data/truth/cli_daily.json`, measures ERA5 vs CLI, then joins CLI to the
paper ledger and stored forecast points.

Réseau requis / Network required (IEM + Open-Meteo archive), sauf
`--skip-fetch` (relit `cli_daily.json`).

Usage:
    python scripts/build_station_truth.py                  # 2018 → hier, 18 stations
    python scripts/build_station_truth.py --stations KNYC,KPHX --start-year 2024
    python scripts/build_station_truth.py --no-era5-audit
    python scripts/build_station_truth.py --skip-fetch --no-era5-audit
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.truth.era5_compare import compare_era5_to_cli  # noqa: E402
from src.truth.iem_cli import TRUTH_DIR, CliDay, IEMCliClient, kalshi_stations  # noqa: E402
from src.truth.join_cli import (  # noqa: E402
    BACKTEST_LEDGER,
    FORECAST_POINTS,
    PAPER_LEDGER,
    forecast_vs_cli_by_station,
    index_cli_days,
    join_forecast_points,
    join_ledger_rows,
    read_csv_rows,
    summarize_joins,
)
from src.weather.open_meteo import OpenMeteoClient  # noqa: E402


def compact(d: CliDay) -> dict:
    return {
        "station": d.station, "valid": d.valid.isoformat(),
        "high": d.high_f, "low": d.low_f,
        "high_time": d.high_time, "low_time": d.low_time,
        "precip": d.precip_in, "precip_trace": d.precip_trace,
        "snow": d.snow_in, "snow_trace": d.snow_trace,
    }


def days_from_compact(rows: list[dict], icao: str, start: date, end: date) -> list[CliDay]:
    out: list[CliDay] = []
    for r in rows:
        if r.get("station") != icao:
            continue
        try:
            valid = date.fromisoformat(str(r["valid"])[:10])
        except (KeyError, ValueError):
            continue
        if not (start <= valid <= end):
            continue
        out.append(CliDay(
            station=icao, valid=valid,
            high_f=r.get("high"), low_f=r.get("low"),
            high_time=r.get("high_time"), low_time=r.get("low_time"),
            precip_in=r.get("precip"), precip_trace=bool(r.get("precip_trace")),
            snow_in=r.get("snow"), snow_trace=bool(r.get("snow_trace")),
            product=None,
        ))
    return out


def write_report(path: Path, audit: dict, span: tuple[date, date]) -> None:
    lines = [
        "# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit",
        "",
        f"Période / span : {span[0]} → {span[1]}. Généré / generated : "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}.",
        "",
        "FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». "
        "CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours "
        "à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.",
        "",
        "EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what "
        "settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means "
        "the model has been learning to correct the wrong target.",
        "",
        "| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |",
        "|---|---|---|---|---|---|---|---|",
    ]
    failed: list[str] = []
    for icao, per in sorted(audit.items()):
        if not isinstance(per, dict) or per.get("error"):
            failed.append(f"| {icao} | - | - | erreur : {per.get('error') if isinstance(per, dict) else per} |")
            continue
        for var in ("high", "low"):
            r = per.get(f"{var}:all")
            if not r:
                continue
            lines.append(
                f"| {icao} | {var} | {r['n']} | {r['bias_era5_minus_cli_f']:+.2f} | {r['mae_f']:.2f} "
                f"| {r['sd_f']} | {r['exact_share']:.0%} | {r['share_off_by_2_or_more']:.0%} |"
            )
    if failed:
        lines += ["", "Stations sans comparaison (source en échec, rien d'inventé) :", ""]
        lines.extend(failed)
    lines += ["", "Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_joins(out_dir: Path, all_days: list[dict]) -> dict:
    cli = index_cli_days(all_days)
    paper = join_ledger_rows(read_csv_rows(PAPER_LEDGER), cli, "paper")
    backtest = join_ledger_rows(read_csv_rows(BACKTEST_LEDGER), cli, "backtest")
    ledger = paper + backtest
    forecast_rows: list[dict] = []
    if FORECAST_POINTS.exists():
        points = json.loads(FORECAST_POINTS.read_text(encoding="utf-8"))
        if isinstance(points, list):
            forecast_rows = join_forecast_points(points, cli)
    summary = summarize_joins(ledger, forecast_rows)
    summary["forecast_vs_cli"] = forecast_vs_cli_by_station(forecast_rows)
    (out_dir / "cli_joined_ledger.json").write_text(
        json.dumps(ledger, separators=(",", ":")), encoding="utf-8"
    )
    (out_dir / "cli_joined_forecasts.json").write_text(
        json.dumps(forecast_rows, separators=(",", ":")), encoding="utf-8"
    )
    (out_dir / "join_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stations", default="", help="ICAO séparés par des virgules (défaut : 18 stations Kalshi)")
    ap.add_argument("--start-year", type=int, default=2018)
    ap.add_argument("--end-date", default=(date.today() - timedelta(days=1)).isoformat())
    ap.add_argument("--no-era5-audit", action="store_true")
    ap.add_argument("--skip-fetch", action="store_true",
                    help="Relit data/truth/cli_daily.json au lieu d'appeler IEM")
    ap.add_argument("--no-join", action="store_true",
                    help="Ne pas joindre le ledger ni les prévisions stockées")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    unknown = [s for s in wanted if s not in stations]
    if unknown:
        print(f"Stations inconnues : {unknown}. Connues : {sorted(stations)}")
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    start = date(args.start_year, 1, 1)
    end = date.fromisoformat(args.end_date)

    cli = IEMCliClient(cache_dir=out_dir / "iem_cache")
    om = OpenMeteoClient()
    all_days: list[dict] = []
    existing: list[dict] = []
    existing_path = out_dir / "cli_daily.json"
    if args.skip_fetch:
        if not existing_path.exists():
            print(f"--skip-fetch : fichier absent {existing_path}")
            return 2
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
        print(f"Relu {existing_path} ({len(existing)} lignes)", flush=True)

    summary: dict = {"schema": "station_truth_summary/1",
                     "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "span": [start.isoformat(), end.isoformat()], "stations": {},
                     "skip_fetch": bool(args.skip_fetch)}
    audit: dict = {}

    for icao in wanted:
        meta = stations[icao]
        print(f"[{icao}] CLI {start} → {end} ...", flush=True)
        days: list[CliDay] = []
        if args.skip_fetch:
            days = days_from_compact(existing, icao, start, end)
        else:
            try:
                days = cli.fetch_range(icao, start, end)
            except Exception as e:  # noqa: BLE001 — on continue station suivante
                print(f"   ÉCHEC IEM : {e}")
                summary["stations"][icao] = {"error": str(e)}
                continue
        n_high = sum(1 for d in days if d.high_f is not None)
        summary["stations"][icao] = {
            "n_days": len(days), "n_high": n_high,
            "n_low": sum(1 for d in days if d.low_f is not None),
            "first": days[0].valid.isoformat() if days else None,
            "last": days[-1].valid.isoformat() if days else None,
        }
        print(f"   {len(days)} jours, {n_high} avec max")
        all_days.extend(compact(d) for d in days)
        if not args.no_era5_audit and days:
            try:
                audit[icao] = compare_era5_to_cli(om, meta, days, start, end)
                if audit[icao].get("error"):
                    print(f"   audit ERA5 impossible : {audit[icao]['error']}")
                else:
                    a = audit[icao].get("high:all", {})
                    print(f"   ERA5 vs CLI (high) : biais {a.get('bias_era5_minus_cli_f')} °F, "
                          f"MAE {a.get('mae_f')} °F, exact {a.get('exact_share')}")
            except Exception as e:  # noqa: BLE001
                print(f"   audit ERA5 impossible : {e}")
                audit[icao] = {"error": str(e)}

    write_cli_daily = (not args.skip_fetch) or (set(wanted) == set(stations))
    if write_cli_daily:
        (out_dir / "cli_daily.json").write_text(
            json.dumps(all_days, separators=(",", ":")), encoding="utf-8"
        )
    else:
        print("skip-fetch + sous-ensemble : cli_daily.json n'est pas écrasé")
    if audit:
        (out_dir / "era5_vs_cli.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        write_report(out_dir / "era5_vs_cli.md", audit, (start, end))
    if not args.no_join:
        join_sum = write_joins(out_dir, all_days)
        summary["joins"] = {
            "ledger_n": join_sum["ledger"]["n"],
            "ledger_joined": join_sum["ledger"]["n_joined"],
            "forecasts_n": join_sum["forecasts"]["n"],
            "forecasts_joined": join_sum["forecasts"]["n_joined"],
        }
        print(f"Joint ledger : {join_sum['ledger']['n_joined']}/{join_sum['ledger']['n']}  "
              f"prévisions : {join_sum['forecasts']['n_joined']}/{join_sum['forecasts']['n']}")
    (out_dir / "truth_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nÉcrit : {out_dir / 'cli_daily.json'} ({len(all_days)} lignes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
