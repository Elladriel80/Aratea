"""eval_century_climato.py — histoire longue de la station vs marché.

FR : Télécharge GHCN-Daily (NCEI) pour les 18 stations Kalshi, mesure la
vraie couverture, construit la distribution par jour de calendrier, estime
une pente descriptive, score une climatologie longue contre la vérité CLI
(même holdout A1) et, s'il y a des prix, compare la certitude du marché
à l'histoire. Le champion en ligne n'est pas touché.

EN : Long official-station climatology vs CLI truth and Kalshi prices.
Does not switch the live champion.

Usage:
    python scripts/eval_century_climato.py
    python scripts/eval_century_climato.py --skip-fetch --skip-iem-probe
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.truth.century import (  # noqa: E402
    FADE_HIST_MAX, FADE_MARKET_MIN, doy_table, empirical_prob, fade_trigger,
    index_by_date, station_spread_summary, trend_report, values_for_window,
)
from src.truth.ghcn_daily import (  # noqa: E402
    ICAO_TO_GHCN, GhcnDailyClient, GhcnDay, coverage_from_days,
)
from src.truth.iem_cli import CITY_TO_ICAO, TRUTH_DIR, IEMCliClient, kalshi_stations  # noqa: E402
from src.truth.skill import sign_test_by_date  # noqa: E402
from src.truth.synthetic_bins import Bin, brier, kalshi_style_bins, prob_in_bin_gaussian  # noqa: E402

GHCN_NOTE = (
    "NCEI GHCN-Daily .dly, IDs USW appariés par coordonnées à ghcnd-stations.txt "
    "le 2026-09-12. QFLAG non vide exclu. Conversion dixièmes °C → °F half-up NWS."
)
A1_SPLIT = date(2026, 8, 3)
A1_END = date(2026, 9, 7)
SIGMA_FLOOR = 1.0
MIN_BIAS_PAIRS = 20
WINDOW_DAYS = 7
CITY_FR = {
    "KATL": "Atlanta", "KAUS": "Austin", "KBOS": "Boston", "KMDW": "Chicago",
    "KDFW": "Dallas", "KDEN": "Denver", "KHOU": "Houston", "KLAS": "Las Vegas",
    "KLAX": "Los Angeles", "KMIA": "Miami", "KMSP": "Minneapolis",
    "KNYC": "New York", "KPHL": "Philadelphie", "KPHX": "Phoenix",
    "KSAT": "San Antonio", "KSFO": "San Francisco", "KSEA": "Seattle",
    "KDCA": "Washington",
}


def load_cli(path: Path) -> dict[tuple[str, date], dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {(r["station"], date.fromisoformat(r["valid"])): r for r in rows}


def truth_value(row: Optional[dict], variable: str) -> Optional[float]:
    if not row:
        return None
    v = row.get("high" if variable == "temp_max" else "low")
    return None if v is None else float(v)


def load_points(path: Path) -> list[dict]:
    pts = json.loads(path.read_text(encoding="utf-8"))
    for p in pts:
        p["_target"] = date.fromisoformat(p["target"])
        p["_mean"] = statistics.fmean(p["per_model"].values())
    return pts


def overlap_ghcn_cli(days: list[GhcnDay], cli: dict, icao: str) -> dict:
    """Accord GHCN (converti) vs CLI sur les jours communs. Rien d'inventé."""
    out: dict[str, dict] = {}
    for var, attr in (("temp_max", "high_f"), ("temp_min", "low_f")):
        n = exact = off1 = off2 = 0
        diffs: list[float] = []
        for d in days:
            row = cli.get((icao, d.valid))
            obs = truth_value(row, var)
            pred = getattr(d, attr)
            if obs is None or pred is None:
                continue
            n += 1
            diff = pred - obs
            diffs.append(diff)
            ad = abs(diff)
            if ad < 0.5:
                exact += 1
            elif ad < 1.5:
                off1 += 1
            else:
                off2 += 1
        if n == 0:
            out[var] = {"n": 0}
            continue
        out[var] = {
            "n": n,
            "exact_share": exact / n,
            "off_by_1_share": off1 / n,
            "off_by_2_or_more_share": off2 / n,
            "mean_ghcn_minus_cli_f": statistics.fmean(diffs),
            "mae_f": statistics.fmean(abs(x) for x in diffs),
        }
    return out


def probe_iem_first_year(client: IEMCliClient, icao: str,
                         lo: int = 1970, hi: Optional[int] = None) -> dict:
    """Première année IEM CLI avec ≥ 30 max. Dichotomie. Pas d'année inventée."""
    if hi is None:
        hi = date.today().year
    cache: dict[int, int] = {}

    def n_high(year: int) -> int:
        if year not in cache:
            try:
                days = client.fetch_year(icao, year)
            except Exception:  # noqa: BLE001
                days = []
            cache[year] = sum(1 for d in days if d.high_f is not None)
        return cache[year]

    if n_high(hi) < 30:
        return {"first_year": None, "last_probed": hi, "n_high_last": cache.get(hi, 0)}
    if n_high(lo) >= 30:
        return {"first_year": lo, "n_high_first": cache[lo], "probed": sorted(cache)}
    left, right = lo, hi
    found = hi
    while left <= right:
        mid = (left + right) // 2
        if n_high(mid) >= 30:
            found = mid
            right = mid - 1
        else:
            left = mid + 1
    return {"first_year": found, "n_high_first": cache.get(found, 0), "probed": sorted(cache)}


def fit_bias(points: list[dict], cli: dict, split: date) -> dict[tuple, tuple]:
    resid: dict[tuple, list[float]] = defaultdict(list)
    for p in points:
        if p["_target"] >= split:
            continue
        obs = truth_value(cli.get((p["station"], p["_target"])), p["variable"])
        if obs is None:
            continue
        resid[(p["station"], p["variable"], p["lead"])].append(obs - p["_mean"])
    out = {}
    for k, r in resid.items():
        if len(r) >= MIN_BIAS_PAIRS:
            out[k] = (statistics.fmean(r), max(SIGMA_FLOOR, statistics.pstdev(r)), len(r))
    return out


def century_mu_sigma(vals: list[int]) -> Optional[tuple[float, float]]:
    if len(vals) < 15:
        return None
    return statistics.fmean(vals), max(SIGMA_FLOOR, statistics.pstdev(vals))


def score_a1_holdout(ghcn_by: dict[str, dict], cli: dict, points: list[dict],
                     split: date, end: date, window_days: int) -> list[dict]:
    bias = fit_bias(points, cli, split)
    rows = []
    for p in points:
        t = p["_target"]
        if t < split or t > end:
            continue
        obs = truth_value(cli.get((p["station"], t)), p["variable"])
        if obs is None:
            continue
        by_date = ghcn_by.get(p["station"])
        if not by_date:
            continue
        hist = values_for_window(by_date, p["variable"], t, window_days, t.year)
        hist30 = values_for_window(by_date, p["variable"], t, window_days, t.year, years_back=30)
        cg = century_mu_sigma(hist)
        mu = p["_mean"]
        sig = max(SIGMA_FLOOR, statistics.pstdev(list(p["per_model"].values()))
                  if len(p["per_model"]) >= 2 else SIGMA_FLOOR)
        st = bias.get((p["station"], p["variable"], p["lead"]))
        for b in kalshi_style_bins(mu, n_central=6):
            if not b.is_central:
                continue
            p_emp = empirical_prob(hist, b)
            p_30 = empirical_prob(hist30, b)
            p_cg = prob_in_bin_gaussian(cg[0], cg[1], b) if cg else None
            p_st = prob_in_bin_gaussian(mu + st[0], st[1], b) if st else None
            rows.append({
                "station": p["station"], "variable": p["variable"], "target": t,
                "lead": p["lead"], "outcome": b.contains(obs),
                "p_century_emp": p_emp, "p_century_30": p_30,
                "p_century_gauss": p_cg,
                "p_raw": prob_in_bin_gaussian(mu, sig, b),
                "p_station": p_st, "p_market": None, "bin": b.label(),
                "hist_n": len(hist),
                "hist_std": statistics.pstdev(hist) if len(hist) >= 2 else None,
            })
    return rows


def load_market_records(min_date: date, leads: set[int]) -> list[dict]:
    seen: dict[tuple, dict] = {}
    for f in sorted(glob.glob(str(ROOT / "data" / "predictions" / "forward_*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in d.get("records", []):
            if r.get("lower") is None or r.get("upper") is None:
                continue
            if r.get("yes_bid") is None or r.get("yes_ask") is None:
                continue
            if r["yes_ask"] <= 0 or r["yes_ask"] < r["yes_bid"]:
                continue
            if r.get("yes_mid") is None:
                continue
            ens = (r.get("predictions") or {}).get("ensemble") or {}
            pm = (ens.get("inputs") or {}).get("per_model_value") or {}
            target = date.fromisoformat(r["target_date"])
            if target < min_date:
                continue
            snap = datetime.strptime(r["snapshot_at"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            lead = (target - snap.date()).days
            if lead < 0 or lead not in leads:
                continue
            key = (r["ticker"], lead)
            if key in seen:
                continue
            seen[key] = {**r, "_target": target, "_snap": snap, "_lead": lead, "_pm": pm}
    return list(seen.values())


def score_market(ghcn_by: dict[str, dict], cli: dict, window_days: int,
                 min_date: date, leads: set[int]) -> tuple[list[dict], dict]:
    records = load_market_records(min_date, leads)
    rows = []
    skips: dict[str, int] = defaultdict(int)
    groups: dict[tuple, list] = defaultdict(list)
    for r in records:
        icao = CITY_TO_ICAO.get(r["location_key"])
        if not icao:
            skips["no_station"] += 1
            continue
        obs = truth_value(cli.get((icao, r["_target"])), r["variable"])
        if obs is None:
            skips["no_cli_truth"] += 1
            continue
        by_date = ghcn_by.get(icao)
        if not by_date:
            skips["no_ghcn"] += 1
            continue
        b = Bin(int(r["lower"]), int(r["upper"]))
        hist = values_for_window(by_date, r["variable"], r["_target"], window_days, r["_target"].year)
        p_emp = empirical_prob(hist, b)
        if p_emp is None:
            skips["no_hist"] += 1
            continue
        vals = list(r["_pm"].values()) if r["_pm"] else []
        p_raw = None
        if len(vals) >= 2:
            p_raw = prob_in_bin_gaussian(
                statistics.fmean(vals), max(SIGMA_FLOOR, statistics.pstdev(vals)), b)
        rec = {
            "station": icao, "variable": r["variable"], "target": r["_target"],
            "lead": r["_lead"], "outcome": b.contains(obs),
            "p_century_emp": p_emp, "p_raw": p_raw, "p_station": None,
            "p_market": float(r["yes_mid"]), "bin": b.label(),
            "hist_n": len(hist),
            "hist_std": statistics.pstdev(hist) if len(hist) >= 2 else None,
            "ticker": r["ticker"],
        }
        rows.append(rec)
        groups[(icao, r["variable"], r["_target"], r["_lead"])].append(rec)

    n_tight = 0
    n_groups = 0
    for recs in groups.values():
        n_groups += 1
        fav = max(recs, key=lambda x: x["p_market"])
        if fade_trigger(fav["p_market"], fav["p_century_emp"]):
            n_tight += 1
            for r in recs:
                r["fade_group"] = True
                r["p_fade"] = r["p_century_emp"]
        else:
            for r in recs:
                r["fade_group"] = False
                r["p_fade"] = r["p_market"]
    meta = {
        "n_bins": len(rows),
        "n_dates": len({r["target"] for r in rows}),
        "n_ladders": n_groups,
        "n_ladders_market_tighter_than_history": n_tight,
        "share_ladders_tighter": (n_tight / n_groups) if n_groups else None,
        "rule": (
            f"favori marché ≥ {FADE_MARKET_MIN:.0%} et fréquence historique "
            f"du même contrat ≤ {FADE_HIST_MAX:.0%}"
        ),
        "skips": dict(skips),
    }
    return rows, meta


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


def _fr(x, nd=2):
    if x is None:
        return "n/a"
    return f"{x:.{nd}f}".replace(".", ",")


def write_reports(out_dir: Path, payload: dict) -> None:
    cov = payload["coverage"]
    lines = [
        "# Histoire longue de la station (GHCN-Daily)",
        "",
        f"Généré : {payload['generated_at']}. Source : fichiers .dly NCEI, "
        "IDs USW appariés par coordonnées le 2026-09-12. "
        "Aucune année n'est inventée : first / last viennent des jours lus.",
        "",
        "## Couverture réelle par station (max du jour)",
        "",
        "| Ville | ID GHCN | Premier jour | Dernier jour | Jours avec max | Jours manquants dans l'intervalle | Années ≥ 300 jours | Premier CLI IEM |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for icao in sorted(cov):
        c = cov[icao]
        if c.get("error") or "temp_max" not in c:
            lines.append(
                f"| {CITY_FR.get(icao, icao)} | {c.get('ghcn_id', '')} | "
                f"échec : {c.get('error', 'pas de max')} | | | | | |"
            )
            continue
        hi = c["temp_max"]
        iem = c.get("iem_cli", {})
        iem_y = iem.get("first_year") if isinstance(iem, dict) else None
        lines.append(
            f"| {CITY_FR.get(icao, icao)} | {c['ghcn_id']} | {hi.get('first')} | {hi.get('last')} "
            f"| {hi.get('n_days')} | {hi.get('missing_days')} | {hi.get('n_complete_years')} "
            f"| {iem_y if iem_y is not None else 'n/a'} |"
        )
    lines += [
        "",
        "Jours manquants = jours calendaires entre le premier et le dernier jour "
        "mesuré, sans max exploitable (valeur absente ou rejetée pour qualité). "
        "On ne compte pas avant le premier jour ni après le dernier.",
        "",
        "Austin : trou de 21 années sans max (1971 à 1991), mesuré sur le fichier. "
        "Chicago Midway commence en 1997. Denver (aéroport actuel) en 1994. "
        "On n'a pas collé un ancien aéroport à la place.",
        "",
        "## Accord GHCN converti vs CLI (jours communs, rien d'inventé)",
        "",
        "| Ville | Var | Jours communs | Exact | Écart 2° ou plus | GHCN − CLI |",
        "|---|---|---|---|---|---|",
    ]
    for icao, ov in sorted(payload["overlap"].items()):
        for var, r in ov.items():
            if not r.get("n"):
                lines.append(f"| {CITY_FR.get(icao, icao)} | {var} | 0 | n/a | n/a | n/a |")
                continue
            lines.append(
                f"| {CITY_FR.get(icao, icao)} | {var} | {r['n']} | {r['exact_share']:.0%} "
                f"| {r['off_by_2_or_more_share']:.0%} | {r['mean_ghcn_minus_cli_f']:+.2f} |"
            )
    lines += [
        "",
        "## Température typique et écart (jour de calendrier, max)",
        "",
        "Pour chaque jour de l'année (1er janv., 2 janv., …) : moyenne et "
        "écart-type des max historiques à cette station. Tableau : médiane "
        "sur les 365/366 jours.",
        "",
        "| Ville | Jours de calendrier | Temp. typique (médiane des moyennes) | Écart typique | Écart élevé (9e décile) | Obs. par jour (médiane) |",
        "|---|---|---|---|---|---|",
    ]
    for icao, s in sorted(payload["spread"].items()):
        hi = s.get("temp_max") or {}
        if not hi:
            continue
        lines.append(
            f"| {CITY_FR.get(icao, icao)} | {hi['n_calendar_days']} | {_fr(hi['typical_mean_f'])} °F "
            f"| {_fr(hi['median_daily_std_f'])} °F | {_fr(hi['p90_daily_std_f'])} °F "
            f"| {hi['median_n_per_doy']:.0f} |"
        )
    lines += [
        "",
        "## Tendance (max annuel, années ≥ 300 jours)",
        "",
        "Pente des moindres carrés : année → moyenne du max. "
        "Descriptive seulement (instrument, ville, climat).",
        "",
        "| Ville | Années | Première | Dernière | Pente / 10 ans | R² | 30 dernières − 30 premières |",
        "|---|---|---|---|---|---|---|",
    ]
    for icao, tr in sorted(payload["trend"].items()):
        t = tr.get("temp_max") or {}
        sl = t.get("slope")
        e30 = t.get("early30_vs_late30") or {}
        if not sl:
            lines.append(
                f"| {CITY_FR.get(icao, icao)} | {t.get('n_complete_years', 0)} | n/a | n/a | "
                f"pas assez d'années | n/a | n/a |"
            )
            continue
        delta = e30.get("late_minus_early_f")
        lines.append(
            f"| {CITY_FR.get(icao, icao)} | {sl['n_years']} | {sl['first_year']} | {sl['last_year']} "
            f"| {sl['slope_f_per_decade']:+.2f} °F | {sl['r_squared']:.2f} "
            f"| {('n/a' if delta is None else f'{delta:+.2f} °F')} |"
        )
    a1 = payload["a1_holdout"]
    lines += [
        "",
        "## Score sur le holdout A1 (3 août au 7 septembre 2026)",
        "",
        "Mêmes bins de 2 °F que A1 (centrées sur la moyenne des modèles). "
        "Vérité = CLI. Plus le score est petit, mieux c'est.",
        "",
        f"| Méthode | Score d'erreur | Jours |",
        f"|---|---|---|",
        f"| Mélange brut | {_fmt(a1['overall'].get('brier_raw'))} | {a1['n_dates']} |",
        f"| Mélange corrigé ville par ville | {_fmt(a1['overall'].get('brier_station'))} | {a1['n_dates']} |",
        f"| Histoire longue (fréquence) | {_fmt(a1['overall'].get('brier_century_emp'))} | {a1['n_dates']} |",
        f"| Histoire 30 ans récents (fréquence) | {_fmt(a1['overall'].get('brier_century_30'))} | {a1['n_dates']} |",
        f"| Histoire longue (cloche) | {_fmt(a1['overall'].get('brier_century_gauss'))} | {a1['n_dates']} |",
        "",
    ]
    for name, t in a1["sign_tests"].items():
        p = "n/a" if t.get("p_one_sided") is None else f"{t['p_one_sided']:.4f}"
        lines.append(
            f"- {name} : {t.get('a_wins')} victoires sur {t.get('dates')} jours (p = {p})"
        )
    mk = payload["market"]
    lines += [
        "",
        "## Marché : certitude vs histoire",
        "",
        f"Règle simple : le marché met {FADE_MARKET_MIN:.0%} ou plus sur un contrat "
        f"de 2 degrés, alors que l'histoire met ce contrat à {FADE_HIST_MAX:.0%} ou moins.",
        "",
        f"Échelles (ville × jour × variable × avance) : {mk['n_ladders']}. "
        f"Dont marché plus sûr que l'histoire : {mk['n_ladders_market_tighter_than_history']} "
        f"({_fr((mk.get('share_ladders_tighter') or 0) * 100, 1)} %).",
        "",
        f"Jours avec un prix : {mk['n_dates']}. Bins : {mk['n_bins']}. "
        f"Si c'est court, le verdict fade n'est pas solide.",
        "",
        f"| Méthode | Score d'erreur |",
        f"|---|---|",
        f"| Prix du marché | {_fmt(mk['overall'].get('brier_market'))} |",
        f"| Histoire longue (fréquence) | {_fmt(mk['overall'].get('brier_century_emp'))} |",
        f"| Règle fade (histoire si marché trop sûr, sinon prix) | {_fmt(mk['overall'].get('brier_fade'))} |",
        "",
    ]
    for name, t in mk["sign_tests"].items():
        p = "n/a" if t.get("p_one_sided") is None else f"{t['p_one_sided']:.4f}"
        lines.append(
            f"- {name} : {t.get('a_wins')} victoires sur {t.get('dates')} jours (p = {p})"
        )
    fade_only = mk.get("fade_only") or {}
    if fade_only:
        lines += [
            "",
            "Sur les seuls contrats où la règle fade s'applique :",
            "",
            f"| Méthode | Score | Bins | Jours |",
            f"|---|---|---|---|",
            f"| Prix | {_fmt(fade_only.get('brier_market'))} | {fade_only.get('n_bins')} | {fade_only.get('n_dates')} |",
            f"| Histoire / fade | {_fmt(fade_only.get('brier_century_emp'))} | {fade_only.get('n_bins')} | {fade_only.get('n_dates')} |",
        ]
    lines += [
        "",
        "## Décision champion",
        "",
        payload["decision"],
        "",
        "Pas de changement du site. Pas de trading réel.",
        "",
    ]
    (out_dir / "century_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stations", default="")
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--skip-iem-probe", action="store_true")
    ap.add_argument("--window-days", type=int, default=WINDOW_DAYS)
    ap.add_argument("--split-date", default=A1_SPLIT.isoformat())
    ap.add_argument("--end-date", default=A1_END.isoformat())
    ap.add_argument("--market-min-date", default="2026-04-11")
    ap.add_argument("--market-leads", default="0,1")
    ap.add_argument("--out-dir", default=str(TRUTH_DIR / "century"))
    args = ap.parse_args()

    stations = kalshi_stations()
    wanted = [s.strip().upper() for s in args.stations.split(",") if s.strip()] or list(stations)
    unknown = [s for s in wanted if s not in ICAO_TO_GHCN]
    if unknown:
        print(f"Stations sans ID GHCN : {unknown}")
        return 2
    split = date.fromisoformat(args.split_date)
    end = date.fromisoformat(args.end_date)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ghcn = GhcnDailyClient()
    iem = IEMCliClient(cache_dir=TRUTH_DIR / "iem_cache", sleep_s=0.35)
    cli_path = TRUTH_DIR / "cli_daily.json"
    cli = load_cli(cli_path) if cli_path.exists() else {}

    coverage: dict = {}
    overlap: dict = {}
    spread: dict = {}
    trend: dict = {}
    doy_compact: dict = {}
    ghcn_index: dict[str, dict] = {}

    for icao in wanted:
        meta = ICAO_TO_GHCN[icao]
        print(f"[{icao}] GHCN {meta['ghcn_id']} ...", flush=True)
        try:
            days = ghcn.fetch_station(
                icao, use_cache=True, allow_network=not args.skip_fetch)
        except Exception as e:  # noqa: BLE001
            print(f"   ÉCHEC GHCN : {e}")
            coverage[icao] = {"ghcn_id": meta["ghcn_id"], "error": str(e)}
            continue
        ghcn_index[icao] = index_by_date(days)
        cov = {
            "ghcn_id": meta["ghcn_id"],
            "ghcn_name": meta["ghcn_name"],
            "temp_max": coverage_from_days(days, "temp_max"),
            "temp_min": coverage_from_days(days, "temp_min"),
        }
        if not args.skip_iem_probe:
            print(f"   sonde IEM CLI ...", flush=True)
            try:
                cov["iem_cli"] = probe_iem_first_year(iem, icao)
            except Exception as e:  # noqa: BLE001
                cov["iem_cli"] = {"error": str(e)}
        else:
            cov["iem_cli"] = {"skipped": True}
        coverage[icao] = cov
        overlap[icao] = overlap_ghcn_cli(days, cli, icao)
        spread[icao] = {}
        trend[icao] = {}
        doy_compact[icao] = {}
        for var in ("temp_max", "temp_min"):
            doy = doy_table(days, var, before_year=2026)
            doy_compact[icao][var] = {
                k: {kk: (round(vv, 3) if isinstance(vv, float) else vv)
                    for kk, vv in rec.items()}
                for k, rec in doy.items()
            }
            spread[icao][var] = station_spread_summary(doy)
            trend[icao][var] = trend_report(days, var)
        hi = cov["temp_max"]
        print(f"   max {hi['first']} → {hi['last']}, {hi['n_days']} jours, "
              f"manque {hi['missing_days']}, années complètes {hi['n_complete_years']}")

    points_path = TRUTH_DIR / "skill" / "forecast_points.json"
    a1_rows: list[dict] = []
    if points_path.exists() and cli:
        points = load_points(points_path)
        a1_rows = score_a1_holdout(ghcn_index, cli, points, split, end, args.window_days)
        print(f"Holdout A1 : {len(a1_rows)} bins, {len({r['target'] for r in a1_rows})} jours")
    a1_fields = ("p_raw", "p_station", "p_century_emp", "p_century_30", "p_century_gauss")
    a1_overall = summarize(a1_rows, lambda r: "all", a1_fields).get("all", {})
    a1_sign = {
        "century_emp_vs_station": sign_test_rows(a1_rows, "p_century_emp", "p_station"),
        "century_emp_vs_raw": sign_test_rows(a1_rows, "p_century_emp", "p_raw"),
        "station_vs_century_emp": sign_test_rows(a1_rows, "p_station", "p_century_emp"),
    }

    leads = {int(x) for x in args.market_leads.split(",") if x.strip()}
    mk_rows, mk_meta = score_market(
        ghcn_index, cli, args.window_days,
        date.fromisoformat(args.market_min_date), leads,
    ) if cli else ([], {"n_bins": 0, "n_dates": 0, "n_ladders": 0,
                        "n_ladders_market_tighter_than_history": 0,
                        "share_ladders_tighter": None, "skips": {}})
    mk_fields = ("p_market", "p_century_emp", "p_fade", "p_raw")
    mk_overall = summarize(mk_rows, lambda r: "all", mk_fields).get("all", {})
    mk_sign = {
        "century_vs_market": sign_test_rows(mk_rows, "p_century_emp", "p_market"),
        "fade_vs_market": sign_test_rows(mk_rows, "p_fade", "p_market"),
        "market_vs_century": sign_test_rows(mk_rows, "p_market", "p_century_emp"),
    }
    fade_rows = [r for r in mk_rows if r.get("fade_group")]
    fade_only = summarize(fade_rows, lambda r: "all", ("p_market", "p_century_emp")).get("all", {})

    b_cent = a1_overall.get("brier_century_emp")
    b_st = a1_overall.get("brier_station")
    b_mkt = mk_overall.get("brier_market")
    n_dates = a1_overall.get("n_dates") or 0
    beats_station = (
        b_cent is not None and b_st is not None and b_cent < b_st and n_dates >= 30
        and a1_sign["century_emp_vs_station"].get("p_one_sided") is not None
        and a1_sign["century_emp_vs_station"]["p_one_sided"] < 0.05
    )
    beats_mkt = (
        b_cent is not None and b_mkt is not None and b_cent < b_mkt
        and (mk_overall.get("n_dates") or 0) >= 30
        and mk_sign["century_vs_market"].get("p_one_sided") is not None
        and mk_sign["century_vs_market"]["p_one_sided"] < 0.05
    )
    if beats_station or beats_mkt:
        decision = (
            "La climatologie longue bat clairement le mélange corrigé ou le marché "
            "sur assez de jours. Relire avant toute bascule : ce script ne change "
            "pas le champion tout seul."
        )
    else:
        decision = (
            "On ne change pas le modèle en ligne. La climatologie longue ne bat "
            f"pas clairement le mélange corrigé ville par ville "
            f"(A1 : { _fmt(b_cent) } contre { _fmt(b_st) }, {n_dates} jours) "
            f"ni le marché ({ _fmt(b_cent) if False else _fmt(mk_overall.get('brier_century_emp')) } "
            f"contre { _fmt(b_mkt) }, {mk_overall.get('n_dates', 0)} jours)."
        )

    payload = {
        "schema": "century_climato/1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_days": args.window_days,
        "split": split.isoformat(),
        "end": end.isoformat(),
        "ghcn_source": GHCN_NOTE,
        "coverage": coverage,
        "overlap": overlap,
        "spread": spread,
        "trend": trend,
        "a1_holdout": {
            "n_bins": len(a1_rows),
            "n_dates": len({r["target"] for r in a1_rows}),
            "overall": a1_overall,
            "by_variable": summarize(a1_rows, lambda r: r["variable"], a1_fields),
            "sign_tests": a1_sign,
        },
        "market": {
            **mk_meta,
            "overall": mk_overall,
            "by_lead": summarize(mk_rows, lambda r: r["lead"], mk_fields),
            "sign_tests": mk_sign,
            "fade_only": fade_only,
        },
        "decision": decision,
        "champion_switched": False,
    }
    # doy compact can be large ; write separately
    (out_dir / "coverage.json").write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    (out_dir / "overlap_cli.json").write_text(json.dumps(overlap, indent=2), encoding="utf-8")
    (out_dir / "spread.json").write_text(json.dumps(spread, indent=2), encoding="utf-8")
    (out_dir / "trend.json").write_text(json.dumps(trend, indent=2), encoding="utf-8")
    (out_dir / "skill.json").write_text(json.dumps({
        "a1_holdout": payload["a1_holdout"], "market": payload["market"],
        "decision": decision, "champion_switched": False,
        "generated_at": payload["generated_at"],
    }, indent=2, default=str), encoding="utf-8")
    (out_dir / "doy_stats.json").write_text(
        json.dumps(doy_compact, separators=(",", ":")), encoding="utf-8"
    )
    write_reports(out_dir, payload)
    print(f"\nÉcrit : {out_dir / 'century_report.md'}")
    print(decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
