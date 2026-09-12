"""eval_candle_recovery.py — récupérer les prix jetés (bougie 18:00 vs 24 h).

FR : On mesure, sur le même univers, deux règles de prix :

  A  exact_hour  : une bougie horaire pile à 18:00 UTC, avec un vrai
                   prix achat/vente.
  B  last_24h    : la dernière bougie cotée dans les 24 h avant 18:00.

Aucun prix n'est inventé. Les 15 noms du catalogue de features ne
bougent pas. Le champion en ligne n'est pas touché. Pas de trading réel.

Sans cache de bougies (et sans --fetch), on note seulement ce qui est
déjà dans le dépôt : le dataset backfill et les captures live.

Usage:
    python scripts/eval_candle_recovery.py
    python scripts/eval_candle_recovery.py --fetch
    python scripts/eval_candle_recovery.py --offline-only
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.kalshi.candles import (  # noqa: E402
    CAPTURE_HOUR_UTC,
    LAST_24H_S,
    classify_window,
    fetch_candles,
)
from src.kalshi.client import KalshiClient  # noqa: E402
from src.predictors.parsers import SERIES_MAP, parse_kalshi_date  # noqa: E402
from src.truth.stacking import brier_mean  # noqa: E402

BACKFILL_DEFAULT = ROOT / "data" / "backfill" / "backfill_dataset_v3fb.json"
CACHE_DIR = ROOT / "data" / "backfill_cache"
PRED_DIR = ROOT / "data" / "predictions"
OUT_DIR = ROOT / "data" / "truth" / "candles"
MIN_MARKET_DAYS = 30
PROMOTION_SIGN_N = 10


def load_backfill(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    X, y, meta = data["X"], data["y"], data["meta"]
    if not (len(X) == len(y) == len(meta)):
        raise SystemExit(f"backfill length mismatch X/y/meta in {path}")
    return data


def backfill_universe(meta: list[dict]) -> dict:
    series = sorted({m.get("series_ticker") for m in meta if m.get("series_ticker")})
    dates = sorted(d for d in ({m.get("target_date") for m in meta}) if d)
    leads = sorted({int(m["days_ahead"]) for m in meta if m.get("days_ahead") is not None})
    return {
        "n_rows": len(meta),
        "n_tickers": len({m.get("ticker") for m in meta}),
        "n_dates": len(dates),
        "date_min": dates[0] if dates else None,
        "date_max": dates[-1] if dates else None,
        "series": series,
        "leads": leads or [1],
        "capture_hour_tokens": dict(Counter(
            (m.get("capture_at") or "")[9:15] for m in meta
        )),
    }


def score_rows(rows: list[dict], label: str) -> dict:
    """Brier on rows that already carry y and a price / model field."""
    out = {
        "label": label,
        "n_rows": len(rows),
        "n_dates": len({r["target_date"] for r in rows if r.get("target_date")}),
        "brier_kalshi_mid": None,
        "brier_champion_ensemble": None,
        "brier_p_consensus": None,
        "dates_ensemble_beats_mid": None,
        "dates_consensus_beats_mid": None,
        "n_scored_mid": 0,
        "n_scored_ensemble": 0,
        "n_scored_consensus": 0,
    }
    mid_rows = [r for r in rows if r.get("yes_mid") is not None]
    ens_rows = [r for r in mid_rows if r.get("p_ensemble") is not None]
    cons_rows = [r for r in mid_rows if r.get("p_consensus") is not None]
    if mid_rows:
        out["brier_kalshi_mid"] = brier_mean(
            [r["yes_mid"] for r in mid_rows], [float(r["y"]) for r in mid_rows])
        out["n_scored_mid"] = len(mid_rows)
    if ens_rows:
        out["brier_champion_ensemble"] = brier_mean(
            [r["p_ensemble"] for r in ens_rows], [float(r["y"]) for r in ens_rows])
        out["n_scored_ensemble"] = len(ens_rows)
    if cons_rows:
        out["brier_p_consensus"] = brier_mean(
            [r["p_consensus"] for r in cons_rows], [float(r["y"]) for r in cons_rows])
        out["n_scored_consensus"] = len(cons_rows)

    def _date_wins(field: str) -> tuple[int, int] | None:
        by: dict[str, list] = defaultdict(list)
        for r in mid_rows:
            if r.get(field) is None:
                continue
            by[r["target_date"]].append(r)
        if not by:
            return None
        wins = 0
        for recs in by.values():
            bm = brier_mean([r["yes_mid"] for r in recs], [float(r["y"]) for r in recs])
            bf = brier_mean([r[field] for r in recs], [float(r["y"]) for r in recs])
            if bm is not None and bf is not None and bf < bm:
                wins += 1
        return wins, len(by)

    we = _date_wins("p_ensemble")
    wc = _date_wins("p_consensus")
    if we:
        out["dates_ensemble_beats_mid"] = {"wins": we[0], "dates": we[1]}
    if wc:
        out["dates_consensus_beats_mid"] = {"wins": wc[0], "dates": wc[1]}
    out["enough_dates_for_market_gate"] = out["n_dates"] >= MIN_MARKET_DAYS
    return out


def live_snapshot_hours(pred_dir: Path) -> dict:
    hours = Counter()
    exact_18 = 0
    n_rec = 0
    n_mid = 0
    n_between = 0
    tickers: set[str] = set()
    dates: set[str] = set()
    for path in sorted(pred_dir.glob("forward_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        file_snap = data.get("snapshot_at") or ""
        for r in data.get("records", []):
            n_rec += 1
            if r.get("ticker"):
                tickers.add(r["ticker"])
            if r.get("target_date"):
                dates.add(r["target_date"])
            if r.get("yes_mid") is not None:
                n_mid += 1
            if r.get("lower") is not None and r.get("upper") is not None:
                n_between += 1
            snap = r.get("snapshot_at") or file_snap or ""
            hour = snap[9:11] if len(snap) >= 11 else "?"
            hours[hour] += 1
            if len(snap) >= 16 and snap[9:16] == "180000Z":
                exact_18 += 1
    return {
        "n_files": sum(1 for _ in pred_dir.glob("forward_*.json")),
        "n_records": n_rec,
        "n_with_yes_mid": n_mid,
        "n_between_like": n_between,
        "n_tickers": len(tickers),
        "n_target_dates": len(dates),
        "n_exact_180000Z": exact_18,
        "records_by_utc_hour": dict(sorted(hours.items())),
        "note": "Captures live : horodatage du fichier, pas une bougie horaire.",
    }


def iter_historical_between(client: KalshiClient, series: str,
                            start: date, end: date) -> list[dict]:
    """Resolved strike_type=between markets in [start, end] for one series."""
    out: list[dict] = []
    cursor = None
    while True:
        params = {"series_ticker": series, "limit": 200}
        if cursor:
            params["cursor"] = cursor
        data = client._get("/historical/markets", params)
        markets = data.get("markets") or []
        for m in markets:
            if m.get("strike_type") != "between":
                continue
            if m.get("result") not in ("yes", "no"):
                continue
            ev = m.get("event_ticker") or ""
            parts = ev.split("-")
            d = parse_kalshi_date(parts[1]) if len(parts) >= 2 else None
            if d is None or not (start <= d <= end):
                continue
            out.append({
                "ticker": m.get("ticker"),
                "event_ticker": ev,
                "series_ticker": series,
                "target_date": d.isoformat(),
                "result": m["result"],
                "y": 1 if m["result"] == "yes" else 0,
            })
        cursor = data.get("cursor") or None
        if not cursor or not markets:
            break
    return out


def classify_row(client, cache_dir: Path, row: dict, lead: int) -> dict:
    target = date.fromisoformat(row["target_date"])
    as_of = target - timedelta(days=lead)
    cutoff = datetime(as_of.year, as_of.month, as_of.day,
                      CAPTURE_HOUR_UTC, tzinfo=timezone.utc)
    cutoff_ts = int(cutoff.timestamp())
    data = fetch_candles(client, row["series_ticker"], row["ticker"],
                         cutoff_ts, cache_dir, lookback_s=LAST_24H_S)
    candles = data.get("candlesticks") if isinstance(data, dict) else None
    verdict = classify_window(candles, cutoff_ts)
    verdict.update({
        "ticker": row["ticker"],
        "event_ticker": row.get("event_ticker"),
        "series_ticker": row["series_ticker"],
        "target_date": row["target_date"],
        "y": row["y"],
        "lead": lead,
        "cutoff_ts": cutoff_ts,
        "n_candles_returned": len(candles or []),
    })
    return verdict


def attach_models(verdicts: list[dict], X: list[dict], meta: list[dict],
                  y: list) -> list[dict]:
    by_key = {}
    for feats, m, yi in zip(X, meta, y):
        key = (m.get("ticker"), int(m.get("days_ahead") or 1))
        by_key[key] = {**feats, "y": yi, "yes_mid": m.get("yes_mid"),
                       "target_date": m.get("target_date")}
    out = []
    for v in verdicts:
        rec = dict(v)
        hit = by_key.get((v["ticker"], int(v["lead"])))
        if hit:
            rec["p_ensemble"] = hit.get("p_ensemble")
            rec["p_consensus"] = hit.get("p_consensus")
            rec["in_backfill"] = True
        else:
            rec["p_ensemble"] = None
            rec["p_consensus"] = None
            rec["in_backfill"] = False
        out.append(rec)
    return out


def policy_rows(verdicts: list[dict], which: str) -> list[dict]:
    rows = []
    for v in verdicts:
        if which == "a" and not v.get("policy_a_exact_hour"):
            continue
        if which == "b" and not v.get("policy_b_last_24h"):
            continue
        mid = v["yes_mid_a"] if which == "a" else v["yes_mid_b"]
        rows.append({
            "ticker": v["ticker"],
            "target_date": v["target_date"],
            "y": v["y"],
            "yes_mid": mid,
            "p_ensemble": v.get("p_ensemble"),
            "p_consensus": v.get("p_consensus"),
        })
    return rows


def summarize_ab(verdicts: list[dict], X, meta, y) -> dict:
    verdicts = attach_models(verdicts, X, meta, y)
    n = len(verdicts)
    n_a = sum(1 for v in verdicts if v["policy_a_exact_hour"])
    n_b = sum(1 for v in verdicts if v["policy_b_last_24h"])
    n_rec = sum(1 for v in verdicts if v["recovered"])
    dropped_a = n - n_a
    ages = [v["age_s_b"] for v in verdicts if v.get("age_s_b") is not None]
    return {
        "n_resolved_between": n,
        "n_policy_a_exact_hour": n_a,
        "n_policy_b_last_24h": n_b,
        "n_dropped_by_exact_hour": dropped_a,
        "n_recovered_by_last_24h": n_rec,
        "pct_dropped_by_exact_hour": (dropped_a / n) if n else None,
        "pct_recovered_of_dropped": (n_rec / dropped_a) if dropped_a else None,
        "pct_recovered_of_universe": (n_rec / n) if n else None,
        "multiplier_b_over_a": (n_b / n_a) if n_a else None,
        "n_in_backfill": sum(1 for v in verdicts if v.get("in_backfill")),
        "n_dates_a": len({v["target_date"] for v in verdicts if v["policy_a_exact_hour"]}),
        "n_dates_b": len({v["target_date"] for v in verdicts if v["policy_b_last_24h"]}),
        "age_hours_b": {
            "n": len(ages),
            "n_exact_zero": sum(1 for a in ages if a == 0),
            "n_positive": sum(1 for a in ages if a > 0),
        },
        "score_exact_hour_set": score_rows(policy_rows(verdicts, "a"),
                                           "exact_hour"),
        "score_last_24h_set": score_rows(policy_rows(verdicts, "b"),
                                         "last_24h"),
        "score_exact_hour_with_champion": score_rows(
            [r for r in policy_rows(verdicts, "a") if r.get("p_ensemble") is not None],
            "exact_hour_with_champion"),
        "score_last_24h_with_champion": score_rows(
            [r for r in policy_rows(verdicts, "b") if r.get("p_ensemble") is not None],
            "last_24h_with_champion"),
    }


def write_markdown(summary: dict) -> str:
    u = summary.get("inrepo_backfill") or {}
    ab = summary.get("ab_same_universe")
    live = summary.get("live_snapshots") or {}
    lines = [
        "# Récupérer les prix jetés (bougie 18:00)",
        "",
        f"Date de mesure : {summary.get('generated_at')}",
        "Aucun chiffre n'est inventé. Champion en ligne inchangé.",
        "",
        "## Dataset backfill déjà dans le dépôt",
        "",
        f"Lignes : {u.get('n_rows')}. Jours : {u.get('n_dates')}. "
        f"Du {u.get('date_min')} au {u.get('date_max')}.",
        f"Séries : {len(u.get('series') or [])}. Capture tamponnée : 18:00 UTC.",
        "",
    ]
    sc = summary.get("score_inrepo_backfill") or {}
    if sc.get("brier_kalshi_mid") is not None:
        lines += [
            f"Score d'erreur (plus petit = mieux), mêmes {sc['n_rows']} lignes :",
            "",
            f"- Prix du marché : {sc['brier_kalshi_mid']:.4f}",
            f"- Champion (mélange vendor_ensemble) : {sc['brier_champion_ensemble']:.4f}",
            f"- Consensus v3 : {sc['brier_p_consensus']:.4f}",
            "",
        ]
        de = sc.get("dates_ensemble_beats_mid") or {}
        if de:
            lines.append(
                f"Le mélange bat le prix : {de.get('wins')} jours sur {de.get('dates')}."
            )
            lines.append("")
    if ab and ab.get("n_resolved_between"):
        lines += [
            "## Même univers, règle A contre règle B",
            "",
            f"Contrats résolus (bin du milieu) : {ab['n_resolved_between']}.",
            f"Règle A (18:00 pile) : {ab['n_policy_a_exact_hour']} lignes, "
            f"{ab['n_dates_a']} jours.",
            f"Règle B (dernière bougie 24 h) : {ab['n_policy_b_last_24h']} lignes, "
            f"{ab['n_dates_b']} jours.",
            f"Jetées par A : {ab['n_dropped_by_exact_hour']}.",
            f"Récupérées par B : {ab['n_recovered_by_last_24h']}.",
            "",
        ]
        if ab.get("pct_recovered_of_dropped") is not None:
            lines.append(
                f"Part récupérée parmi les jetées de A : "
                f"{100 * ab['pct_recovered_of_dropped']:.1f} %."
            )
        if ab.get("multiplier_b_over_a") is not None:
            lines.append(
                f"Taille B / taille A : {ab['multiplier_b_over_a']:.2f}."
            )
        lines.append("")
        sa = ab.get("score_exact_hour_set") or {}
        sb = ab.get("score_last_24h_set") or {}
        if sa.get("brier_kalshi_mid") is not None:
            lines += [
                "Score d'erreur du prix, ensemble A (18:00 pile) : "
                f"{sa['brier_kalshi_mid']:.4f} ({sa['n_rows']} lignes, "
                f"{sa['n_dates']} jours).",
                "Score d'erreur du prix, ensemble B (24 h) : "
                f"{sb.get('brier_kalshi_mid'):.4f} ({sb.get('n_rows')} lignes, "
                f"{sb.get('n_dates')} jours).",
                "",
            ]
        ca = ab.get("score_exact_hour_with_champion") or {}
        cb = ab.get("score_last_24h_with_champion") or {}
        if ca.get("brier_champion_ensemble") is not None:
            lines += [
                "Là où le champion a déjà une chance (dataset backfill) :",
                f"- Ensemble A : prix {ca.get('brier_kalshi_mid'):.4f}, "
                f"champion {ca.get('brier_champion_ensemble'):.4f} "
                f"({ca.get('n_rows')} lignes, {ca.get('n_dates')} jours).",
                f"- Ensemble B : prix {cb.get('brier_kalshi_mid'):.4f}, "
                f"champion {cb.get('brier_champion_ensemble'):.4f} "
                f"({cb.get('n_rows')} lignes, {cb.get('n_dates')} jours).",
                "",
            ]
    else:
        lines += [
            "## Règle A contre règle B",
            "",
            "Pas mesuré : aucune bougie en cache, et le script n'a pas "
            "téléchargé (--offline-only, ou --fetch absent et cache vide).",
            "",
        ]
    lines += [
        "## Captures live déjà dans le dépôt",
        "",
        f"Fichiers : {live.get('n_files')}. Lignes : {live.get('n_records')}. "
        f"Avec un prix : {live.get('n_with_yes_mid')}.",
        f"Pile à 18:00:00 UTC : {live.get('n_exact_180000Z')}.",
        "",
        "## Décision",
        "",
        summary.get("verdict_fr") or "",
        "",
        "Pas de trading avec de l'argent réel.",
        "",
    ]
    return "\n".join(lines) + "\n"


def verdict_from(summary: dict) -> str:
    ab = summary.get("ab_same_universe")
    sc = summary.get("score_inrepo_backfill") or {}
    if not ab or not ab.get("n_resolved_between"):
        return (
            "Mesure A/B bloquée : pas de bougies dans le dépôt. "
            "Le dataset backfill déjà là a "
            f"{sc.get('n_rows', 0)} lignes et {sc.get('n_dates', 0)} jours. "
            "On ne change pas le champion."
        )
    n_a = ab["n_policy_a_exact_hour"]
    n_b = ab["n_policy_b_last_24h"]
    n_rec = ab["n_recovered_by_last_24h"]
    dates_b = ab["n_dates_b"]
    ca = ab.get("score_exact_hour_with_champion") or {}
    cb = ab.get("score_last_24h_with_champion") or {}
    parts = [
        f"Règle B garde {n_b} lignes contre {n_a} pour la règle A "
        f"({n_rec} récupérées).",
        f"Jours sous B : {dates_b} (il en faut {MIN_MARKET_DAYS} pour parler du marché).",
    ]
    if cb.get("brier_champion_ensemble") is not None and cb.get("brier_kalshi_mid") is not None:
        parts.append(
            f"Là où le champion est noté, son score reste "
            f"{cb['brier_champion_ensemble']:.4f} contre "
            f"{cb['brier_kalshi_mid']:.4f} pour le prix "
            f"({cb.get('n_dates')} jours)."
        )
        beats = (cb.get("dates_ensemble_beats_mid") or {}).get("wins", 0)
        nd = (cb.get("dates_ensemble_beats_mid") or {}).get("dates", 0)
        if nd:
            parts.append(f"Le mélange bat le prix {beats} jours sur {nd}.")
    promote = (
        dates_b >= MIN_MARKET_DAYS
        and cb.get("brier_champion_ensemble") is not None
        and cb.get("brier_kalshi_mid") is not None
        and cb["brier_champion_ensemble"] < cb["brier_kalshi_mid"]
        and (cb.get("dates_ensemble_beats_mid") or {}).get("dates", 0) >= PROMOTION_SIGN_N
        and (cb.get("dates_ensemble_beats_mid") or {}).get("wins", 0)
        > (cb.get("dates_ensemble_beats_mid") or {}).get("dates", 0) / 2
    )
    if promote:
        parts.append(
            "Les portes de promotion ne sont pas franchies ici : "
            "on n'a pas relancé l'apprentissage ni changé le champion."
        )
    else:
        parts.append("On ne change pas le champion.")
    return " ".join(parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--backfill", default=str(BACKFILL_DEFAULT))
    ap.add_argument("--cache-dir", default=str(CACHE_DIR))
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--fetch", action="store_true",
                    help="télécharger les bougies manquantes (lecture seule)")
    ap.add_argument("--offline-only", action="store_true",
                    help="ne jamais appeler Kalshi")
    ap.add_argument("--series", default="",
                    help="liste de séries (défaut : celles du backfill)")
    ap.add_argument("--lead", type=int, default=1)
    args = ap.parse_args(argv)

    backfill_path = Path(args.backfill)
    if not backfill_path.is_absolute():
        backfill_path = ROOT / backfill_path
    data = load_backfill(backfill_path)
    X, y, meta = data["X"], data["y"], data["meta"]
    uni = backfill_universe(meta)
    scored_inrepo = score_rows([
        {
            "y": yi,
            "yes_mid": m.get("yes_mid"),
            "p_ensemble": feats.get("p_ensemble"),
            "p_consensus": feats.get("p_consensus"),
            "target_date": m.get("target_date"),
            "ticker": m.get("ticker"),
        }
        for feats, m, yi in zip(X, meta, y)
    ], "inrepo_backfill")

    series_list = [s.strip() for s in args.series.split(",") if s.strip()]
    if not series_list:
        series_list = list(uni["series"])

    start = date.fromisoformat(uni["date_min"]) if uni["date_min"] else None
    end = date.fromisoformat(uni["date_max"]) if uni["date_max"] else None

    cache_dir = Path(args.cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = ROOT / cache_dir

    ab = None
    fetch_note = "not_run"
    if start and end and series_list and not args.offline_only and args.fetch:
        client = KalshiClient()
        universe: list[dict] = []
        for series in series_list:
            print(f">> list {series} {start}..{end}")
            universe.extend(iter_historical_between(client, series, start, end))
        print(f">> universe resolved between-bins: {len(universe)}")
        verdicts = []
        for i, row in enumerate(universe, 1):
            try:
                verdicts.append(classify_row(client, cache_dir, row, args.lead))
            except Exception as e:
                print(f"   [err] {row.get('ticker')}: {type(e).__name__}: {e}")
            if i % 50 == 0:
                print(f"   ... {i}/{len(universe)}")
        ab = summarize_ab(verdicts, X, meta, y)
        fetch_note = "fetched"
    elif args.offline_only:
        fetch_note = "offline_only"
    else:
        cached = list(cache_dir.glob("kalshi_candles__*.json")) if cache_dir.exists() else []
        fetch_note = f"no_fetch cache_files={len(cached)}"

    summary = {
        "schema": "candle_recovery/1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "params": {
            "backfill": str(backfill_path),
            "series": series_list,
            "start": uni["date_min"],
            "end": uni["date_max"],
            "lead": args.lead,
            "fetch": args.fetch,
            "offline_only": args.offline_only,
            "fetch_note": fetch_note,
        },
        "inrepo_backfill": uni,
        "score_inrepo_backfill": scored_inrepo,
        "live_snapshots": live_snapshot_hours(PRED_DIR),
        "ab_same_universe": ab,
        "promotion_gates": {
            "min_market_dates": MIN_MARKET_DAYS,
            "champion": "vendor_ensemble",
            "champion_changed": False,
        },
        "catalogue_variables_renamed": False,
    }
    summary["verdict_fr"] = verdict_from(summary)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "candle_recovery.json"
    md_path = out_dir / "candle_recovery.md"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    md_path.write_text(write_markdown(summary), encoding="utf-8")
    print(f">> wrote {json_path}")
    print(f">> wrote {md_path}")
    print(summary["verdict_fr"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
