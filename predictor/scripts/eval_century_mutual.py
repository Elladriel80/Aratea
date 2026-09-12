"""eval_century_mutual.py — queues chaleur / gel / pluie sur le même fichier siècle.

FR : Relit les .dly déjà téléchargés (pas de nouveau produit, pas de prix).
Compte les jours très chauds, les jours de gel, l'écart d'une année à
l'autre, et la pluie annuelle si PRCP est présent. La mutuelle n'est pas
ouverte. Le champion Kalshi n'est pas touché.

EN : Tail counts on the same GHCN-Daily files. No insurance product, no price.

Usage:
    python scripts/eval_century_mutual.py --skip-fetch
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.truth.century import mutual_station_tails  # noqa: E402
from src.truth.ghcn_daily import ICAO_TO_GHCN, GhcnDailyClient  # noqa: E402
from src.truth.iem_cli import TRUTH_DIR, kalshi_stations  # noqa: E402

CITY_FR = {
    "KATL": "Atlanta", "KAUS": "Austin", "KBOS": "Boston", "KMDW": "Chicago",
    "KDFW": "Dallas", "KDEN": "Denver", "KHOU": "Houston", "KLAS": "Las Vegas",
    "KLAX": "Los Angeles", "KMIA": "Miami", "KMSP": "Minneapolis",
    "KNYC": "New York", "KPHL": "Philadelphie", "KPHX": "Phoenix",
    "KSAT": "San Antonio", "KSFO": "San Francisco", "KSEA": "Seattle",
    "KDCA": "Washington",
}


def _fr(x, nd=1):
    if x is None:
        return "n/a"
    return f"{x:.{nd}f}".replace(".", ",")


def write_md(path: Path, tails: dict, generated_at: str) -> None:
    lines = [
        "# Queues mesurées sur le fichier siècle (mutuelle)",
        "",
        f"Généré : {generated_at}. Même source GHCN-Daily que le holdout Kalshi. "
        "Seuils descriptifs : max ≥ 100 °F, max ≥ 95 °F, min ≤ 32 °F. "
        "Pluie = somme annuelle des jours PRCP présents. "
        "Pas de produit, pas de prix.",
        "",
        "## Chaleur (années ≥ 300 jours avec max)",
        "",
        "| Ville | Années | Plus chaud | Jours ≥ 100 °F (médiane / année) | Années avec au moins 1 jour ≥ 100 °F | Jours ≥ 95 °F (médiane) |",
        "|---|---|---|---|---|---|",
    ]
    for icao in sorted(tails):
        h = tails[icao].get("heat") or {}
        if not h.get("n_complete_years"):
            lines.append(f"| {CITY_FR.get(icao, icao)} | 0 | n/a | n/a | n/a | n/a |")
            continue
        lines.append(
            f"| {CITY_FR.get(icao, icao)} | {h['n_complete_years']} | {h['hottest_f']} °F "
            f"| {h['median_days_ge_100f']} | {h['years_with_any_100f']} / {h['n_complete_years']} "
            f"| {h['median_days_ge_95f']} |"
        )
    lines += [
        "",
        "## Gel (années ≥ 300 jours avec min)",
        "",
        "| Ville | Années | Plus froid | Jours ≤ 32 °F (médiane / année) | Années avec au moins 1 gel |",
        "|---|---|---|---|---|",
    ]
    for icao in sorted(tails):
        f = tails[icao].get("frost") or {}
        if not f.get("n_complete_years"):
            lines.append(f"| {CITY_FR.get(icao, icao)} | 0 | n/a | n/a | n/a |")
            continue
        lines.append(
            f"| {CITY_FR.get(icao, icao)} | {f['n_complete_years']} | {f['coldest_f']} °F "
            f"| {f['median_frost_days']} | {f['years_with_any_frost']} / {f['n_complete_years']} |"
        )
    lines += [
        "",
        "## Pente lente vs écart d'une année à l'autre (max annuel)",
        "",
        "L'écart année à année ne compte que les années qui se suivent. "
        "La pente / 10 ans est la même droite que dans century_report.md.",
        "",
        "| Ville | Sauts d'années qui se suivent | Saut typique | Gros saut (9e décile) | Pente / 10 ans |",
        "|---|---|---|---|---|",
    ]
    for icao in sorted(tails):
        s = tails[icao].get("year_to_year_max")
        if not s:
            lines.append(f"| {CITY_FR.get(icao, icao)} | n/a | n/a | n/a | n/a |")
            continue
        sl = s.get("slope_f_per_decade")
        lines.append(
            f"| {CITY_FR.get(icao, icao)} | {s['n_consecutive_jumps']} "
            f"| {_fr(s['median_abs_jump_f'])} °F | {_fr(s['p90_abs_jump_f'])} °F "
            f"| {('n/a' if sl is None else f'{sl:+.2f} °F')} |"
        )
    lines += [
        "",
        "## Pluie annuelle (années ≥ 300 jours avec PRCP)",
        "",
        "| Ville | Années | Année typique | Année sèche (1er décile) | Plus sèche | Plus humide | Jours sans pluie (médiane) |",
        "|---|---|---|---|---|---|---|",
    ]
    for icao in sorted(tails):
        r = tails[icao].get("rain") or {}
        if not r.get("n_complete_years"):
            lines.append(f"| {CITY_FR.get(icao, icao)} | 0 | n/a | n/a | n/a | n/a | n/a |")
            continue
        lines.append(
            f"| {CITY_FR.get(icao, icao)} | {r['n_complete_years']} "
            f"| {_fr(r['median_year_inches'])} in | {_fr(r['p10_year_inches'])} in "
            f"| {_fr(r['driest_year_inches'])} in | {_fr(r['wettest_year_inches'])} in "
            f"| {r['median_dry_days']} |"
        )
    lines += [
        "",
        "Pas de changement du champion. Pas de produit vendu. Pas de prix.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stations", default="")
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "century"))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    ghcn = GhcnDailyClient()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tails: dict = {}
    for icao in wanted:
        if icao not in ICAO_TO_GHCN:
            print(f"[{icao}] pas d'ID GHCN", flush=True)
            continue
        print(f"[{icao}] queues ...", flush=True)
        days = ghcn.fetch_station(icao, use_cache=True, allow_network=not args.skip_fetch)
        tails[icao] = mutual_station_tails(days)
        h = tails[icao]["heat"]
        print(f"   chaleur années={h.get('n_complete_years')} "
              f"médiane jours ≥100={h.get('median_days_ge_100f')}")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "schema": "century_mutual_tails/1",
        "generated_at": generated_at,
        "note": (
            "Seuils descriptifs seulement. Pas un barème de mutuelle. "
            "Même fichiers GHCN-Daily que eval_century_climato.py."
        ),
        "thresholds_f": {"heat": 100, "heat_near": 95, "frost": 32},
        "stations": tails,
        "champion_switched": False,
    }
    (out_dir / "mutual_tails.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    write_md(out_dir / "mutual_tails.md", tails, generated_at)
    print(f"Écrit : {out_dir / 'mutual_tails.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
