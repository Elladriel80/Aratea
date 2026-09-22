"""Inventaire public du catalogue « Marché ouragan Kalshi ».

FR : Lecture seule de l'API Kalshi. Aucun ordre. On ne compte un marché
comme notable que s'il a un prix public ET un résultat, et une vérité
HURDAT2 officielle pour la même saison. Sinon : 0 ou N mince.

EN : Read-only Kalshi hurricane inventory. No live trading.
"""
from __future__ import annotations

import re
import time
from collections import Counter
from typing import Any, Iterable, Optional

from src.kalshi.client import KalshiClient
from src.kalshi.models import Market
from src.truth.hurdat2_atl import climato_exceedance

CATALOGUE_MARKET = "Marché ouragan Kalshi"

# Phase B scaffolding already asks for ≥ 10 seasons to score a seasonal target.
MIN_SEASONS_TO_SCORE = 10
# Project Phase 1 gate talks about 30 dates. Seasonal hurricane is 1 event/year.
# Below 10 settled seasons with a public price, we call the book too thin.
HURRICANE_TITLE_RE = re.compile(r"hurr", re.IGNORECASE)
HURRICANE_TICKER_RE = re.compile(r"HURC|HURCAT|HURN|HURHAT|HURJACK|HURMIA|HURMYR|HURNJ|HURNO|HURNOR|HURNYC|HURORL|HURSAV|HURTB|HURWIL|HURCAL|HURPATH|HURRICANE|FIRSTHURRICANE|NEXTHUR|NEXTCAT5HUR", re.IGNORECASE)
FALSE_POSITIVE_TICKERS = {"KXNCAAFAPCHURN", "KXTOPALBUMBYERICCHURCH"}

# Live 2026 Atlantic count bins (Kalshi "more than K" / "Above K").
HURCTOT_THRESHOLDS = (4, 5, 6, 7, 8, 9, 10, 12, 15)
HURCTOTMAJ_THRESHOLDS = (0, 1, 2, 3, 4, 5, 6, 7)


def is_hurricane_series(ticker: str, title: str, category: str) -> bool:
    """Climate/weather hurricane series. Sports / music false friends dropped."""
    ticker = ticker or ""
    if ticker.upper() in FALSE_POSITIVE_TICKERS:
        return False
    cat = (category or "").lower()
    if "climate" not in cat and "weather" not in cat:
        return False
    if HURRICANE_TITLE_RE.search(title or ""):
        return True
    return bool(HURRICANE_TICKER_RE.search(ticker))


def mid_price(market: Market) -> Optional[float]:
    if market.yes_bid is None or market.yes_ask is None:
        return None
    return (market.yes_bid + market.yes_ask) / 2.0


def two_sided(market: Market) -> bool:
    """Both sides present and the ask is actually offered (ask > 0)."""
    return (
        market.yes_bid is not None
        and market.yes_ask is not None
        and market.yes_ask > 0
    )


def both_sides_positive(market: Market) -> bool:
    return (
        market.yes_bid is not None
        and market.yes_ask is not None
        and market.yes_bid > 0
        and market.yes_ask > 0
    )


def parse_threshold(rules: str, subtitle: str) -> Optional[int]:
    """Read 'more than K' from Kalshi rules. Missing stays missing."""
    for text in (rules or "", subtitle or ""):
        m = re.search(r"more than\s+(\d+)", text, re.IGNORECASE)
        if m:
            return int(m.group(1))
        m = re.search(r"Above\s+(\d+)", text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def market_row(m: Market) -> dict[str, Any]:
    return {
        "ticker": m.ticker,
        "event_ticker": m.event_ticker,
        "status": m.status,
        "result": m.result,
        "subtitle": m.subtitle,
        "yes_bid": m.yes_bid,
        "yes_ask": m.yes_ask,
        "last_price": m.last_price,
        "mid": mid_price(m),
        "volume": m.volume,
        "two_sided": two_sided(m),
        "both_sides_positive": both_sides_positive(m),
        "rules_primary": m.rules_primary,
        "threshold_more_than": parse_threshold(m.rules_primary, m.subtitle),
        "close_time": m.close_time.isoformat() if m.close_time else None,
        "expiration_time": m.expiration_time.isoformat() if m.expiration_time else None,
    }


def series_inventory(client: KalshiClient, allow_network: bool = True) -> list[dict[str, Any]]:
    """List climate hurricane series and their public events / markets."""
    if not allow_network:
        raise RuntimeError("series_inventory needs the public Kalshi API or a fixture")
    out = []
    for s in client.list_series():
        if not is_hurricane_series(s.ticker, s.title, s.category or ""):
            continue
        events = list(client.list_events(series_ticker=s.ticker, with_nested_markets=True))
        markets: list[Market] = []
        # /markets is the volume/quote source; nested events often have empty markets.
        cursor_markets = _list_markets_raw(client, s.ticker)
        for raw in cursor_markets:
            markets.append(Market.from_api(raw))
        ev_years = sorted({
            (e.raw.get("close_time") or e.raw.get("expiration_time") or "")[:4]
            for e in events
            if (e.raw.get("close_time") or e.raw.get("expiration_time"))
        })
        ev_years = [y for y in ev_years if y.isdigit()]
        title_years = sorted(_years_from_titles(e.title for e in events))
        rows = [market_row(m) for m in markets]
        n_vol = sum(1 for r in rows if (r.get("volume") or 0) > 0)
        n_quoted = sum(1 for r in rows if r["two_sided"])
        n_both = sum(1 for r in rows if r.get("both_sides_positive"))
        n_settled = sum(1 for r in rows if r["result"] in ("yes", "no"))
        n_settled_priced = sum(
            1 for r in rows
            if r["result"] in ("yes", "no") and r["mid"] is not None
        )
        out.append({
            "series_ticker": s.ticker,
            "title": s.title,
            "category": s.category,
            "frequency": s.raw.get("frequency"),
            "contract_url": s.raw.get("contract_url"),
            "settlement_sources": s.raw.get("settlement_sources") or [],
            "n_events": len(events),
            "n_markets": len(markets),
            "event_tickers": [e.event_ticker for e in events],
            "event_titles": [e.title for e in events],
            "event_years_from_close": ev_years,
            "event_years_from_title": title_years,
            "market_status": dict(Counter(r["status"] for r in rows)),
            "volume_sum": round(sum(float(r["volume"] or 0) for r in rows), 4),
            "n_markets_volume_gt0": n_vol,
            "n_quoted_two_sided": n_quoted,
            "n_quoted_bid_and_ask_positive": n_both,
            "n_settled_yes_no": n_settled,
            "n_settled_with_mid": n_settled_priced,
            "markets": rows,
        })
    out.sort(key=lambda r: r["series_ticker"])
    return out


def _years_from_titles(titles: Iterable[str]) -> set[int]:
    years: set[int] = set()
    for title in titles:
        for m in re.finditer(r"\b(20\d{2})\b", title or ""):
            years.add(int(m.group(1)))
    return years


def _list_markets_raw(client: KalshiClient, series_ticker: str) -> list[dict]:
    """Paginate /markets for one series. Uses the existing retrying client."""
    items = []
    cursor = None
    while True:
        params = {"series_ticker": series_ticker, "limit": 200}
        if cursor:
            params["cursor"] = cursor
        data = client._get("/markets", params)
        chunk = data.get("markets") or []
        items.extend(chunk)
        cursor = data.get("cursor") or None
        if not cursor or not chunk:
            break
        time.sleep(0.05)
    return items


def playability(inventory: list[dict[str, Any]]) -> dict[str, Any]:
    """Can we score Kalshi hurricane prices against official HURDAT2?

    Settled + mid + HURDAT2 season (file ends 2025) is the bar. 2026 live
    books have prices but no official HURDAT2 outcome yet.
    """
    n_series = len(inventory)
    n_events = sum(r["n_events"] for r in inventory)
    n_markets = sum(r["n_markets"] for r in inventory)
    n_vol = sum(r["n_markets_volume_gt0"] for r in inventory)
    n_quoted = sum(r["n_quoted_two_sided"] for r in inventory)
    n_both = sum(r.get("n_quoted_bid_and_ask_positive", 0) for r in inventory)
    n_settled = sum(r["n_settled_yes_no"] for r in inventory)
    n_settled_priced = sum(r["n_settled_with_mid"] for r in inventory)
    live = [r for r in inventory if r["n_markets_volume_gt0"] > 0 or r["n_quoted_two_sided"] > 0]
    # Historical count seasons visible as event titles, markets gone from the API.
    count_series = [r for r in inventory if r["series_ticker"] in ("KXHURCTOT", "KXHURCTOTMAJ", "HURCTOT", "HURCTOTMAJ")]
    titled_years = sorted({y for r in count_series for y in r["event_years_from_title"]})
    settled_years_with_price: list[int] = []
    for r in count_series:
        for m in r["markets"]:
            if m["result"] in ("yes", "no") and m["mid"] is not None:
                years = _years_from_titles([m.get("rules_primary") or "", m.get("event_ticker") or ""])
                settled_years_with_price.extend(years)
    settled_years_with_price = sorted(set(y for y in settled_years_with_price if y <= 2025))
    n_seasons_scored = len(settled_years_with_price)
    thin = n_seasons_scored < MIN_SEASONS_TO_SCORE
    return {
        "catalogue": CATALOGUE_MARKET,
        "n_series": n_series,
        "n_events": n_events,
        "n_markets": n_markets,
        "n_markets_volume_gt0": n_vol,
        "n_quoted_two_sided": n_quoted,
        "n_quoted_bid_and_ask_positive": n_both,
        "n_settled_yes_no": n_settled,
        "n_settled_with_mid": n_settled_priced,
        "n_live_series_with_volume_or_quote": len(live),
        "live_series_tickers": [r["series_ticker"] for r in live],
        "count_event_years_from_title": titled_years,
        "n_seasons_settled_with_public_mid_and_hurdat2": n_seasons_scored,
        "seasons_settled_with_public_mid_and_hurdat2": settled_years_with_price,
        "min_seasons_to_score": MIN_SEASONS_TO_SCORE,
        "too_thin_to_score": thin,
        "playable_to_score": n_seasons_scored >= MIN_SEASONS_TO_SCORE,
        "reason": (
            "Zéro saison réglée avec un prix public et une vérité HURDAT2 "
            "officielle (fichier arrêté à 2025). Les événements 2022-2025 "
            "existent sans marchés. La saison 2026 a des prix mais pas de "
            "HURDAT2 officiel."
            if n_seasons_scored == 0
            else f"Seulement {n_seasons_scored} saison(s) notables, barre à {MIN_SEASONS_TO_SCORE}."
        ),
    }


def price_vs_climato(
    inventory: list[dict[str, Any]],
    season_rows_full: list[dict[str, Any]],
    season_rows_dec1: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Compare live 2026 'more than K' mids to HURDAT2 P(count > K)."""
    wanted = {
        "KXHURCTOT": ("n_hurricanes", HURCTOT_THRESHOLDS),
        "KXHURCTOTMAJ": ("n_major", HURCTOTMAJ_THRESHOLDS),
    }
    out = []
    by_ticker = {r["series_ticker"]: r for r in inventory}
    for series_ticker, (field, _ths) in wanted.items():
        row = by_ticker.get(series_ticker)
        if not row:
            continue
        for m in row["markets"]:
            if m["event_ticker"] not in (
                f"{series_ticker}-26DEC01",
                f"{series_ticker}-26JUN30",
            ):
                continue
            if "JUN30" in (m["event_ticker"] or ""):
                continue  # monthly contract, not the seasonal climato
            k = m.get("threshold_more_than")
            if k is None:
                continue
            full = climato_exceedance(season_rows_full, field, k)
            dec1 = climato_exceedance(season_rows_dec1, field, k)
            out.append({
                "series_ticker": series_ticker,
                "ticker": m["ticker"],
                "subtitle": m["subtitle"],
                "threshold_more_than": k,
                "field": field,
                "yes_bid": m["yes_bid"],
                "yes_ask": m["yes_ask"],
                "last_price": m["last_price"],
                "mid": m["mid"],
                "volume": m["volume"],
                "rules_primary": m["rules_primary"],
                "climato_full_year": full,
                "climato_through_dec1": dec1,
                "mid_minus_climato_dec1": (
                    None if m["mid"] is None or dec1["p"] is None
                    else m["mid"] - dec1["p"]
                ),
            })
    return out


def settlement_digest(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per series: who pays, from the published rules / sources."""
    digest = []
    for r in inventory:
        rules = []
        for m in r["markets"]:
            rp = (m.get("rules_primary") or "").strip()
            if rp and rp not in rules:
                rules.append(rp)
        digest.append({
            "series_ticker": r["series_ticker"],
            "title": r["title"],
            "frequency": r["frequency"],
            "contract_url": r["contract_url"],
            "settlement_sources": r["settlement_sources"],
            "n_distinct_rules": len(rules),
            "rules_primary_sample": rules[:3],
            "n_events": r["n_events"],
            "n_markets": r["n_markets"],
            "volume_sum": r["volume_sum"],
        })
    return digest
