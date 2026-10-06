"""Politiques de bougies Kalshi pour le backfill (18:00 UTC).

FR : Deux règles, sur le même univers de bougies :

  exact_hour  (politique A) — on garde la bougie dont la fin de période
              est pile l'heure de capture (18:00 UTC).
  last_24h    (politique B) — on garde la dernière bougie dans les 24 h
              avant la capture, y compris pile à 18:00.

Une ligne sans vrai prix deux côtés (bid et ask) est jetée. Aucun prix
n'est inventé. Le champion en ligne n'est pas concerné.

EN : A/B candle pick at a simulated 18:00 UTC capture. No invented mids.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

POLICY_EXACT_HOUR = "exact_hour"
POLICY_LAST_24H = "last_24h"
CANDLE_POLICIES = (POLICY_EXACT_HOUR, POLICY_LAST_24H)

CAPTURE_HOUR_UTC = 18
LAST_24H_S = 24 * 3600
# Legacy fetch window used by the June backfill (wider than 24 h).
LEGACY_LOOKBACK_S = 72 * 3600
CANDLE_SLEEP = 0.12

LIVE_CANDLES = "/series/{series}/markets/{ticker}/candlesticks"
HIST_CANDLES = "/historical/markets/{ticker}/candlesticks"
HIST_CUTOFF_PATH = "/historical/cutoff"

# Cached after the first GET /historical/cutoff in this process.
_MARKET_SETTLED_CUTOFF_TS: Optional[int] = None


def market_settled_cutoff_ts(client) -> Optional[int]:
    """Unix ts of Kalshi's live/historical market split. None if unknown."""
    global _MARKET_SETTLED_CUTOFF_TS
    if _MARKET_SETTLED_CUTOFF_TS is not None:
        return _MARKET_SETTLED_CUTOFF_TS
    try:
        data = client._get(HIST_CUTOFF_PATH)
    except Exception:
        return None
    raw = data.get("market_settled_ts") if isinstance(data, dict) else None
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None
    _MARKET_SETTLED_CUTOFF_TS = int(dt.timestamp())
    return _MARKET_SETTLED_CUTOFF_TS


def capture_cutoff_utc(as_of) -> datetime:
    """18:00 UTC on the simulated capture calendar day."""
    return datetime(as_of.year, as_of.month, as_of.day,
                    CAPTURE_HOUR_UTC, tzinfo=timezone.utc)


def candle_ts(c: dict) -> Optional[int]:
    """End-of-period unix timestamp of a candlestick, defensively."""
    if not isinstance(c, dict):
        return None
    for k in ("end_period_ts", "end_ts", "ts", "period_ts"):
        v = c.get(k)
        if isinstance(v, (int, float)):
            return int(v)
    return None


def ohlc_close_dollars(d: dict) -> Optional[float]:
    """Close value of an OHLC dict, in dollars.

    Schemas observed:
    - close_dollars: "0.0500"  (string dollars, live 2026-06-12)
    - close: "0.0400"          (string dollars, historical 2026-09-12)
    - close: 5                 (numeric cents, documented)
    A string is always dollars. A number is cents. None if missing.
    """
    if not isinstance(d, dict):
        return None
    v = d.get("close_dollars")
    if v is not None:
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    v = d.get("close")
    if v is None:
        return None
    if isinstance(v, str):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None
    try:
        return float(v) / 100.0
    except (TypeError, ValueError):
        return None


def candle_mid(c: dict) -> Optional[tuple[float, float, float]]:
    """(mid, bid, ask) in dollars. None unless two-sided (ask > 0, ask >= bid)."""
    if not isinstance(c, dict):
        return None
    yb, ya = c.get("yes_bid"), c.get("yes_ask")
    b = ohlc_close_dollars(yb) if isinstance(yb, dict) else None
    a = ohlc_close_dollars(ya) if isinstance(ya, dict) else None
    if b is None or a is None:
        return None
    if a <= 0 or a < b:
        return None
    return ((b + a) / 2.0, b, a)


def _candidates(candles, cutoff_ts: int, policy: str) -> list[tuple[int, dict]]:
    """Candles allowed by the named policy, newest last."""
    if policy not in CANDLE_POLICIES:
        raise ValueError(f"unknown candle policy {policy!r}")
    window_start = cutoff_ts - LAST_24H_S if policy == POLICY_LAST_24H else cutoff_ts
    out: list[tuple[int, dict]] = []
    for c in candles or []:
        ts = candle_ts(c)
        if ts is None or ts > cutoff_ts:
            continue
        if policy == POLICY_EXACT_HOUR and ts != cutoff_ts:
            continue
        if ts < window_start:
            continue
        out.append((ts, c))
    out.sort(key=lambda t: t[0])
    return out


def pick_candle(candles, cutoff_ts: int, policy: str = POLICY_LAST_24H):
    """Last candle allowed by policy, quote or not. None if the window is empty."""
    cands = _candidates(candles, cutoff_ts, policy)
    return cands[-1][1] if cands else None


def pick_quoted_candle(candles, cutoff_ts: int, policy: str = POLICY_LAST_24H):
    """Last candle in the policy window that has a two-sided quote.

    last_24h walks back inside the 24 h window when the 18:00 bar has
    no bid/ask. exact_hour never walks back.
    """
    cands = _candidates(candles, cutoff_ts, policy)
    if policy == POLICY_EXACT_HOUR:
        if not cands:
            return None
        return cands[-1][1] if candle_mid(cands[-1][1]) else None
    for _ts, c in reversed(cands):
        if candle_mid(c) is not None:
            return c
    return None


def classify_window(candles, cutoff_ts: int) -> dict:
    """A/B verdict on one already-fetched candle list. No network."""
    a = pick_quoted_candle(candles, cutoff_ts, POLICY_EXACT_HOUR)
    b = pick_quoted_candle(candles, cutoff_ts, POLICY_LAST_24H)
    qa = candle_mid(a) if a is not None else None
    qb = candle_mid(b) if b is not None else None
    ts_a = candle_ts(a) if a is not None else None
    ts_b = candle_ts(b) if b is not None else None
    ages = []
    for c in candles or []:
        ts = candle_ts(c)
        if ts is not None and ts <= cutoff_ts:
            ages.append(cutoff_ts - ts)
    return {
        "policy_a_exact_hour": qa is not None,
        "policy_b_last_24h": qb is not None,
        "recovered": qa is None and qb is not None,
        "yes_mid_a": qa[0] if qa else None,
        "yes_mid_b": qb[0] if qb else None,
        "candle_ts_a": ts_a,
        "candle_ts_b": ts_b,
        "age_s_b": (cutoff_ts - ts_b) if ts_b is not None else None,
        "n_candles_at_or_before": len(ages),
        "n_candles_in_24h": sum(1 for a_s in ages if a_s <= LAST_24H_S),
    }


def fetch_candles(client, series_ticker: str, market_ticker: str,
                  cutoff_ts: int, cache_dir: Path,
                  lookback_s: int = LAST_24H_S) -> dict:
    """Hourly candles in [cutoff - lookback, cutoff]. Live path, then historical.

    Only real JSON with a candlesticks key is cached. 404 on the live
    path is expected for markets settled before GET /historical/cutoff
    (2026-09-12: market_settled_ts = 2026-07-14).
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "_"
                   for ch in f"{market_ticker}__{cutoff_ts}")
    path = cache_dir / f"kalshi_candles__{safe}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    params = {"start_ts": cutoff_ts - lookback_s,
              "end_ts": cutoff_ts, "period_interval": 60}
    live = LIVE_CANDLES.format(series=series_ticker, ticker=market_ticker)
    hist = HIST_CANDLES.format(ticker=market_ticker)
    settled_cut = market_settled_cutoff_ts(client)
    # Capture is the day before resolution; if that instant is older than
    # the live/historical split, the live path 404s. Skip it.
    prefer_hist = settled_cut is not None and cutoff_ts < settled_cut
    paths = [hist, live] if prefer_hist else [live, hist]
    data: dict = {}
    last_err: Optional[BaseException] = None
    for i, url in enumerate(paths):
        time.sleep(CANDLE_SLEEP)
        try:
            data = client._get(url, params=params)
            last_err = None
            break
        except requests.HTTPError as e:
            last_err = e
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status == 404 and i + 1 < len(paths):
                continue
            data = {}
            break
    if last_err is not None and not (isinstance(data, dict) and "candlesticks" in data):
        raise last_err
    if isinstance(data, dict) and "candlesticks" in data:
        path.write_text(json.dumps(data), encoding="utf-8")
    return data
