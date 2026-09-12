"""eval_second_marche.py — mesurer le Second marché (piste B4).

FR : Compare le prix Kalshi déjà capturé au prix Polymarket du même
jour, même ville, même case de 2 °F, à la même heure (ou juste avant).
Note les deux contre le chiffre officiel CLI de la station Kalshi.
Essaie aussi la moyenne des deux prix, et Kalshi plus l'écart (un
seul nombre appris avant le 3 août). Le champion en ligne n'est pas
touché. Aucun pari avec de l'argent réel.

Les prix Polymarket ne sont pas dans le dépôt : l'API publique Gamma
(événements) et CLOB (historique) sont lues, puis mises en cache.
Sans réseau, relancer avec --skip-fetch sur les fichiers déjà écrits.

EN : A/B Kalshi mid vs Polymarket last print on exact-bound overlapping
city-days. CLI truth. No live champion change.

Usage:
    python scripts/eval_second_marche.py
    python scripts/eval_second_marche.py --skip-fetch
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
import time
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.config import USER_AGENT  # noqa: E402
from src.truth.iem_cli import TRUTH_DIR  # noqa: E402
from src.truth.second_marche import (  # noqa: E402
    CITY_MAPS, CLOB_BASE, GAMMA_BASE, HIGHEST_TEMP_TAG_ID,
    KALSHI_HIGH_WITHOUT_PM, attach_blends, cache_key, event_target_date,
    fit_gap_weight, icao_for_kalshi_key, outcome_from_cli, parse_pm_bin,
    pm_site_icao, price_at_or_before, same_bin, slice_metrics,
    snapshot_unix, two_sided, yes_token_id,
)

A1_SPLIT = date(2026, 8, 3)
MIN_MARKET_DAYS = 30
CACHE_DIR = ROOT / "data" / "polymarket" / "cache"
EXTRACT_DIR = ROOT / "data" / "polymarket"
OUT_DEFAULT = TRUTH_DIR / "second_marche"
SLEEP_S = 0.12


def _get_json(url: str, timeout: int = 30) -> object:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    last: Optional[BaseException] = None
    for attempt in range(4):
        try:
            with urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            last = exc
            if exc.code != 429 or attempt == 3:
                raise
            time.sleep(min(30.0, 2 ** attempt))
        except URLError as exc:
            last = exc
            if attempt == 3:
                raise
            time.sleep(1 + attempt)
    if last:
        raise last
    return {}


def cache_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def load_cached(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def inventory_repo(pred_dir: Path) -> dict:
    """Compte ce qui est déjà dans le dépôt. Aucun chiffre inventé."""
    forward = sorted(glob.glob(str(pred_dir / "forward_*.json")))
    n_rec = n_high = n_high_quote = 0
    high_cities: Counter = Counter()
    high_dates: set[str] = set()
    series: Counter = Counter()
    for f in forward:
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in data.get("records", []):
            n_rec += 1
            ticker = r.get("ticker") or ""
            is_high = r.get("variable") == "temp_max" or "HIGHT" in ticker or ticker.startswith("KXHIGH")
            if not is_high:
                continue
            n_high += 1
            high_cities[r.get("location_key") or "?"] += 1
            if r.get("target_date"):
                high_dates.add(r["target_date"])
            series[r.get("series_ticker") or ticker.split("-")[0]] += 1
            if two_sided(r.get("yes_bid"), r.get("yes_ask")) and r.get("yes_mid") is not None:
                n_high_quote += 1
    pm_tracked = list((ROOT / "data" / "polymarket").glob("*.json")) if (ROOT / "data" / "polymarket").exists() else []
    return {
        "n_forward_files": len(forward),
        "n_records": n_rec,
        "n_high_records": n_high,
        "n_high_two_sided": n_high_quote,
        "high_cities": dict(high_cities),
        "n_high_dates": len(high_dates),
        "high_date_min": min(high_dates) if high_dates else None,
        "high_date_max": max(high_dates) if high_dates else None,
        "high_series": dict(series),
        "n_polymarket_tracked_json": len(pm_tracked),
        "cli_path": str(TRUTH_DIR / "cli_daily.json"),
        "cli_present": (TRUTH_DIR / "cli_daily.json").exists(),
    }


def load_truth(path: Path) -> dict[tuple[str, date], dict]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {(r["station"], date.fromisoformat(r["valid"])): r for r in rows}


def load_kalshi_high(pred_dir: Path, cities: set[str]) -> list[dict]:
    seen: dict[tuple[str, int], dict] = {}
    for f in sorted(glob.glob(str(pred_dir / "forward_*.json"))):
        data = json.loads(Path(f).read_text(encoding="utf-8"))
        for r in data.get("records", []):
            if r.get("location_key") not in cities:
                continue
            if r.get("variable") != "temp_max":
                continue
            if not two_sided(r.get("yes_bid"), r.get("yes_ask")):
                continue
            if r.get("yes_mid") is None:
                continue
            if r.get("lower") is None and r.get("upper") is None:
                continue
            target = date.fromisoformat(r["target_date"])
            snap = datetime.strptime(r["snapshot_at"], "%Y%m%dT%H%M%SZ").replace(
                tzinfo=timezone.utc
            )
            lead = (target - snap.date()).days
            if lead < 0:
                continue
            key = (r["ticker"], lead)
            if key in seen:
                continue
            seen[key] = {
                "ticker": r["ticker"],
                "kalshi_key": r["location_key"],
                "target": target.isoformat(),
                "snapshot_at": r["snapshot_at"],
                "lead": lead,
                "lower": r.get("lower"),
                "upper": r.get("upper"),
                "subtitle": r.get("subtitle"),
                "p_kalshi": float(r["yes_mid"]),
                "yes_bid": float(r["yes_bid"]),
                "yes_ask": float(r["yes_ask"]),
            }
    return list(seen.values())


def fetch_series_events(series_slug: str, allow_network: bool) -> list[dict]:
    path = CACHE_DIR / f"events_{cache_key(series_slug)}.json"
    cached = load_cached(path)
    if cached is not None:
        return cached
    if not allow_network:
        return []
    out: list[dict] = []
    offset = 0
    while offset < 800:
        url = f"{GAMMA_BASE}/events?{urlencode({'series_slug': series_slug, 'limit': 50, 'offset': offset})}"
        time.sleep(SLEEP_S)
        page = _get_json(url)
        if not isinstance(page, list) or not page:
            break
        out.extend(page)
        if len(page) < 50:
            break
        offset += 50
    cache_json(path, out)
    return out


def compact_event(event: dict, city_slug: str) -> Optional[dict]:
    title = event.get("title") or ""
    if not title.lower().startswith("highest temperature"):
        return None
    target = event_target_date(event)
    if target is None:
        return None
    desc = event.get("description") or ""
    site = pm_site_icao(desc) or pm_site_icao(event.get("resolutionSource") or "")
    markets = []
    for m in event.get("markets") or []:
        bounds = parse_pm_bin(m.get("groupItemTitle") or "") or parse_pm_bin(m.get("question") or "")
        token = yes_token_id(m)
        if bounds is None or token is None:
            continue
        markets.append({
            "title": m.get("groupItemTitle") or m.get("question"),
            "lower": bounds[0],
            "upper": bounds[1],
            "yes_token": token,
        })
    if not markets:
        return None
    return {
        "slug": event.get("slug"),
        "title": title,
        "city_slug": city_slug,
        "target": target.isoformat(),
        "pm_icao": site,
        "n_markets": len(markets),
        "markets": markets,
        "closed": bool(event.get("closed")),
    }


def load_or_fetch_events(allow_network: bool, extract_path: Path) -> list[dict]:
    if extract_path.exists() and not allow_network:
        return json.loads(extract_path.read_text(encoding="utf-8"))
    events: list[dict] = []
    for cmap in CITY_MAPS:
        raw = fetch_series_events(cmap.series_slug, allow_network)
        for ev in raw:
            compact = compact_event(ev, cmap.slug)
            if compact:
                events.append(compact)
    if events:
        extract_path.parent.mkdir(parents=True, exist_ok=True)
        extract_path.write_text(json.dumps(events), encoding="utf-8")
    elif extract_path.exists():
        events = json.loads(extract_path.read_text(encoding="utf-8"))
    return events


def fetch_history(token: str, allow_network: bool) -> list[dict]:
    path = CACHE_DIR / f"hist_{cache_key(token[:40])}.json"
    cached = load_cached(path)
    if cached is not None:
        return cached.get("history") if isinstance(cached, dict) else cached
    if not allow_network:
        return []
    url = f"{CLOB_BASE}/prices-history?{urlencode({'market': token, 'interval': 'max', 'fidelity': 60})}"
    time.sleep(SLEEP_S)
    data = _get_json(url)
    hist = data.get("history") if isinstance(data, dict) else []
    if not isinstance(hist, list):
        hist = []
    cache_json(path, {"history": hist})
    return hist


def discover_open_high_cities(allow_network: bool) -> dict:
    """Compte les villes 'Highest temperature' ouvertes le jour de la mesure."""
    path = CACHE_DIR / "open_highest_tag.json"
    payload = load_cached(path)
    if payload is None:
        if not allow_network:
            return {"n_events": 0, "n_cities_sept12": 0, "cities_sept12": [], "source": None}
        events: list[dict] = []
        offset = 0
        while offset < 400:
            url = (
                f"{GAMMA_BASE}/events?"
                f"{urlencode({'tag_id': HIGHEST_TEMP_TAG_ID, 'closed': 'false', 'limit': 100, 'offset': offset})}"
            )
            time.sleep(SLEEP_S)
            page = _get_json(url)
            if not isinstance(page, list) or not page:
                break
            events.extend(page)
            if len(page) < 100:
                break
            offset += 100
        payload = [{"title": e.get("title"), "seriesSlug": e.get("seriesSlug")} for e in events]
        cache_json(path, payload)
    sept12 = []
    for e in payload:
        title = e.get("title") or ""
        if title.startswith("Highest temperature") and "September 12" in title:
            sept12.append(title)
    cities = sorted({t.split(" in ", 1)[-1].split(" on ", 1)[0] for t in sept12 if " in " in t})
    return {
        "n_events": len(payload),
        "n_cities_sept12": len(cities),
        "cities_sept12": cities,
        "source": f"{GAMMA_BASE}/events?tag_id={HIGHEST_TEMP_TAG_ID}&closed=false",
    }


def index_pm_events(events: list[dict]) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    for ev in events:
        cmap = next((c for c in CITY_MAPS if c.slug == ev.get("city_slug")), None)
        if cmap is None:
            continue
        out[(cmap.kalshi_key, ev["target"])] = ev
    return out


def join_rows(
    kalshi_rows: list[dict],
    pm_index: dict[tuple[str, str], dict],
    truth: dict,
    allow_network: bool,
    hist_cache: dict[str, list],
) -> tuple[list[dict], dict]:
    skips: Counter = Counter()
    joined: list[dict] = []

    for kr in kalshi_rows:
        ev = pm_index.get((kr["kalshi_key"], kr["target"]))
        if ev is None:
            skips["no_pm_event"] += 1
            continue
        match = None
        for m in ev["markets"]:
            if same_bin(kr["lower"], kr["upper"], m["lower"], m["upper"]):
                match = m
                break
        if match is None:
            skips["no_exact_bin"] += 1
            continue
        icao = icao_for_kalshi_key(kr["kalshi_key"])
        t = truth.get((icao, date.fromisoformat(kr["target"]))) if icao else None
        high = None if not t or t.get("high") is None else float(t["high"])
        if high is None:
            skips["no_cli"] += 1
            continue
        cutoff = snapshot_unix(kr["snapshot_at"])
        if cutoff is None:
            skips["bad_snapshot"] += 1
            continue
        joined.append({
            **kr,
            "pm_slug": ev.get("slug"),
            "pm_title": match.get("title"),
            "pm_icao": ev.get("pm_icao"),
            "kalshi_icao": icao,
            "same_station": bool(ev.get("pm_icao") and icao and ev["pm_icao"] == icao),
            "cli_high": high,
            "outcome": outcome_from_cli(high, kr["lower"], kr["upper"]),
            "yes_token": match["yes_token"],
            "cutoff_ts": cutoff,
            "p_pm": None,
            "pm_price_ts": None,
        })

    # Fetch only tokens that appear in an exact match with CLI.
    tokens = sorted({r["yes_token"] for r in joined})
    for i, token in enumerate(tokens):
        if token not in hist_cache:
            hist_cache[token] = fetch_history(token, allow_network)
        if (i + 1) % 50 == 0:
            print(f"  historiques CLOB {i + 1}/{len(tokens)}", flush=True)

    kept: list[dict] = []
    for r in joined:
        picked = price_at_or_before(hist_cache.get(r["yes_token"]) or [], r["cutoff_ts"])
        if picked is None:
            skips["no_pm_price_before_snapshot"] += 1
            continue
        r["p_pm"] = picked[0]
        r["pm_price_ts"] = picked[1]
        r["gap"] = r["p_pm"] - r["p_kalshi"]
        kept.append(r)
    return kept, dict(skips)


def _fmt(x) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, float):
        return f"{x:.4f}"
    return str(x)


def _fr_dec(x) -> str:
    if x is None:
        return "n/a"
    return f"{x:.4f}".replace(".", ",")


def write_reports(out_dir: Path, payload: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "second_marche_skill.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    inv = payload["inventory"]
    disc = payload["discovery"]
    prim = payload["primary"]
    same = payload["same_station"]
    lines = [
        "# Second marché : Kalshi contre Polymarket",
        "",
        "Mesure reproductible. Aucun prix inventé. Champion inchangé.",
        "",
        "## Données déjà dans le dépôt",
        "",
        f"- Captures `forward_*.json` : {inv['n_forward_files']} fichiers, {inv['n_records']} lignes.",
        f"- Contrats max Kalshi : {inv['n_high_records']} dont {inv['n_high_two_sided']} avec un prix deux côtés.",
        f"- Jours Kalshi max : {inv['n_high_dates']} ({inv['high_date_min']} à {inv['high_date_max']}).",
        f"- Fichiers Polymarket suivis dans git au départ : {inv['n_polymarket_tracked_json']}.",
        f"- Vérité CLI : {'oui' if inv['cli_present'] else 'non'} (`cli_daily.json`).",
        "",
        "## Polymarket lu sur l'API publique",
        "",
        f"- Source événements : `{GAMMA_BASE}` (séries `*-daily-weather`).",
        f"- Source prix : `{CLOB_BASE}/prices-history` (dernier point ≤ heure de capture).",
        f"- Villes « Highest temperature » ouvertes le 12 septembre 2026 : "
        f"{disc['n_cities_sept12']} (liste mesurée, pas le chiffre 44 du journal).",
        f"- Événements HIGH extraits pour les villes mappables : {payload['n_pm_events']}.",
        "",
        "## Recouvrement",
        "",
        f"- Lignes Kalshi max dans une ville mappable : {payload['n_kalshi_mapped']}.",
        f"- Lignes gardées (même case, prix Polymarket avant la capture, CLI) : {prim['n_bins']}.",
        f"- Villes-jours : {prim['n_city_days']}. Jours calendaires : {prim['n_dates']}.",
        f"- Villes : {', '.join(prim['cities']) or 'aucune'}.",
        f"- Lignes écartées : {json.dumps(payload['skips'], ensure_ascii=False)}.",
        "",
        "Villes Kalshi max sans série Polymarket quotidienne trouvée : "
        + ", ".join(KALSHI_HIGH_WITHOUT_PM) + ".",
        "",
        "## Résultat principal (la veille, lead 1)",
        "",
        "Plus le score d'erreur (Brier) est petit, mieux c'est.",
        "",
        f"| Méthode | Score d'erreur |",
        f"|---|---|",
        f"| Prix Kalshi | {_fmt(prim['brier_kalshi'])} |",
        f"| Prix Polymarket | {_fmt(prim['brier_pm'])} |",
        f"| Moyenne des deux | {_fmt(prim['brier_avg'])} |",
        f"| Kalshi + écart (poids { _fmt(payload.get('gap_weight')) }) | {_fmt(prim['brier_stack'])} |",
        "",
        f"Écart absolu moyen des prix : {_fmt(prim['mean_abs_gap'])}.",
        f"Polymarket bat Kalshi : {prim['pm_vs_kalshi']['wins']} jours "
        f"sur {prim['pm_vs_kalshi']['n_decisive']} (p={_fmt(prim['pm_vs_kalshi']['p_one_sided'])}).",
        f"La moyenne bat Kalshi : {prim['avg_vs_kalshi']['wins']} jours "
        f"sur {prim['avg_vs_kalshi']['n_decisive']} (p={_fmt(prim['avg_vs_kalshi']['p_one_sided'])}).",
        "",
        "## Même station NOAA (sous-ensemble)",
        "",
        f"Lignes : {same['n_bins']}. Villes-jours : {same['n_city_days']}. "
        f"Jours : {same['n_dates']}.",
        f"Brier Kalshi {_fmt(same['brier_kalshi'])} / Polymarket {_fmt(same['brier_pm'])} / "
        f"moyenne {_fmt(same['brier_avg'])}.",
        "",
        "## Autres tranches",
        "",
    ]
    for name, block in payload["slices"].items():
        lines.append(
            f"- {name} : n={block['n_bins']} bins, {block['n_city_days']} villes-jours, "
            f"{block['n_dates']} jours ; Brier K {_fmt(block['brier_kalshi'])} / "
            f"PM {_fmt(block['brier_pm'])} / moy {_fmt(block['brier_avg'])} ; "
            f"|écart| {_fmt(block['mean_abs_gap'])}."
        )
    lines += [
        "",
        f"Seuil habituel du projet pour parler du marché : {MIN_MARKET_DAYS} jours.",
        f"Jours (lead 1) : {prim['n_dates']}.",
        "",
        f"Verdict machine : {payload['verdict']}",
        "",
    ]
    (out_dir / "second_marche_skill.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def decide_verdict(primary: dict, skips: dict) -> str:
    if primary["n_bins"] == 0:
        return "blocked"
    if (primary["n_dates"] or 0) < MIN_MARKET_DAYS:
        # Mesuré, mais trop peu pour les portes habituelles.
        avg = primary.get("brier_avg")
        k = primary.get("brier_kalshi")
        if avg is not None and k is not None and avg < k and primary["avg_vs_kalshi"]["wins"] > primary["avg_vs_kalshi"]["losses"]:
            return "testee_thin_helps"
        return "testee_thin"
    avg = primary.get("brier_avg")
    stack = primary.get("brier_stack")
    k = primary.get("brier_kalshi")
    avg_wins = primary["avg_vs_kalshi"]
    stack_wins = primary["stack_vs_kalshi"]
    helps = False
    if avg is not None and k is not None and avg < k and avg_wins["wins"] > avg_wins["losses"]:
        helps = True
    if stack is not None and k is not None and stack < k and stack_wins["wins"] > stack_wins["losses"]:
        helps = True
    return "testee_ca_aide" if helps else "testee_ca_n_aide_pas"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-fetch", action="store_true", help="ne pas appeler Gamma/CLOB")
    ap.add_argument("--pred-dir", default=str(ROOT / "data" / "predictions"))
    ap.add_argument("--truth", default=str(TRUTH_DIR / "cli_daily.json"))
    ap.add_argument("--out-dir", default=str(OUT_DEFAULT))
    ap.add_argument("--extract", default=str(EXTRACT_DIR / "extracted_events.json"))
    ap.add_argument("--joined", default=str(OUT_DEFAULT / "joined_rows.json"))
    args = ap.parse_args()

    allow_network = not args.skip_fetch
    pred_dir = Path(args.pred_dir)
    out_dir = Path(args.out_dir)
    extract_path = Path(args.extract)
    joined_path = Path(args.joined)

    print("Inventaire dépôt…", flush=True)
    inv = inventory_repo(pred_dir)
    print(
        f"  forward={inv['n_forward_files']} high={inv['n_high_records']} "
        f"two_sided={inv['n_high_two_sided']} pm_json={inv['n_polymarket_tracked_json']}",
        flush=True,
    )

    print("Vérité CLI…", flush=True)
    truth = load_truth(Path(args.truth))

    mapped_keys = {c.kalshi_key for c in CITY_MAPS}
    kalshi_rows = load_kalshi_high(pred_dir, mapped_keys)
    print(f"  lignes Kalshi max mappables : {len(kalshi_rows)}", flush=True)

    print("Événements Polymarket…", flush=True)
    events = load_or_fetch_events(allow_network, extract_path)
    print(f"  événements HIGH extraits : {len(events)}", flush=True)
    pm_index = index_pm_events(events)

    print("Villes ouvertes (tag)…", flush=True)
    discovery = discover_open_high_cities(allow_network)
    print(f"  villes 12 sept. : {discovery['n_cities_sept12']}", flush=True)

    hist_cache: dict[str, list] = {}
    if joined_path.exists() and args.skip_fetch:
        print("Reprise des lignes déjà jointes (--skip-fetch).", flush=True)
        rows = json.loads(joined_path.read_text(encoding="utf-8"))
        skips = {"reused_joined": len(rows)}
    else:
        print("Jointure cases + historiques CLOB…", flush=True)
        rows, skips = join_rows(kalshi_rows, pm_index, truth, allow_network, hist_cache)
        out_dir.mkdir(parents=True, exist_ok=True)
        slim = [{k: v for k, v in r.items()} for r in rows]
        joined_path.parent.mkdir(parents=True, exist_ok=True)
        joined_path.write_text(json.dumps(slim), encoding="utf-8")
        print(f"  jointes : {len(rows)}  skips={skips}", flush=True)

    train = [r for r in rows if date.fromisoformat(r["target"]) < A1_SPLIT]
    test = [r for r in rows if date.fromisoformat(r["target"]) >= A1_SPLIT]
    weight = fit_gap_weight(train)
    attach_blends(rows, weight)

    def take(lead: Optional[int], same_station: Optional[bool] = None, after_split: Optional[bool] = None):
        out = []
        for r in rows:
            if lead is not None and r.get("lead") != lead:
                continue
            if same_station is True and not r.get("same_station"):
                continue
            if after_split is True and date.fromisoformat(r["target"]) < A1_SPLIT:
                continue
            if after_split is False and date.fromisoformat(r["target"]) >= A1_SPLIT:
                continue
            out.append(r)
        return out

    slices = {
        "tous_leads": slice_metrics(rows),
        "lead_0": slice_metrics(take(0)),
        "lead_1": slice_metrics(take(1)),
        "lead_1_meme_station": slice_metrics(take(1, same_station=True)),
        "lead_1_avant_3_aout": slice_metrics(take(1, after_split=False)),
        "lead_1_depuis_3_aout": slice_metrics(take(1, after_split=True)),
    }
    primary = slices["lead_1"]
    same = slices["lead_1_meme_station"]
    verdict = decide_verdict(primary, skips)

    payload = {
        "variable": "Second marché",
        "inventory": inv,
        "discovery": discovery,
        "n_pm_events": len(events),
        "n_kalshi_mapped": len(kalshi_rows),
        "skips": skips,
        "gap_weight": weight,
        "n_train_for_weight": len(train),
        "n_test_after_split": len(test),
        "primary": primary,
        "same_station": same,
        "slices": slices,
        "verdict": verdict,
        "min_market_days": MIN_MARKET_DAYS,
        "sources": {
            "kalshi_captures": "predictor/data/predictions/forward_*.json",
            "cli": "predictor/data/truth/cli_daily.json",
            "polymarket_events": GAMMA_BASE,
            "polymarket_prices": CLOB_BASE + "/prices-history",
        },
        "city_maps": [
            {
                "slug": c.slug,
                "kalshi_key": c.kalshi_key,
                "kalshi_icao": c.kalshi_icao,
                "pm_icao_note": c.pm_icao_note,
                "same_station_note": c.same_station_note,
            }
            for c in CITY_MAPS
        ],
        "kalshi_high_without_pm": list(KALSHI_HIGH_WITHOUT_PM),
    }
    write_reports(out_dir, payload)
    print(f"Verdict : {verdict}", flush=True)
    print(f"Lead 1 : n={primary['n_bins']} city-days={primary['n_city_days']} "
          f"dates={primary['n_dates']} |écart|={primary['mean_abs_gap']} "
          f"Brier K={primary['brier_kalshi']} PM={primary['brier_pm']} "
          f"moy={primary['brier_avg']}", flush=True)
    print(f"Écrit {out_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
