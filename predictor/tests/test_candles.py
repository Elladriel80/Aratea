"""Politiques A/B de bougies : 18:00 pile contre dernière cotation 24 h."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.kalshi.candles import (
    POLICY_EXACT_HOUR,
    POLICY_LAST_24H,
    candle_mid,
    classify_window,
    ohlc_close_dollars,
    pick_candle,
    pick_quoted_candle,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "candles_window.json"
CUTOFF = int(datetime(2026, 4, 13, 18, 0, tzinfo=timezone.utc).timestamp())


def _candles():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["candlesticks"]


def test_string_close_is_dollars_not_cents():
    assert ohlc_close_dollars({"close": "0.1000"}) == 0.10
    assert ohlc_close_dollars({"close_dollars": "0.0500"}) == 0.05
    assert ohlc_close_dollars({"close": 5}) == 0.05


def test_exact_hour_keeps_18h_quote():
    c = pick_quoted_candle(_candles(), CUTOFF, POLICY_EXACT_HOUR)
    assert c is not None
    mid = candle_mid(c)
    assert mid is not None
    assert abs(mid[0] - 0.11) < 1e-9


def test_classify_window_both_keep_quoted_18h():
    v = classify_window(_candles(), CUTOFF)
    assert v["policy_a_exact_hour"] is True
    assert v["policy_b_last_24h"] is True
    assert v["recovered"] is False
    assert v["age_s_b"] == 0


def test_last_24h_same_when_18h_quoted():
    a = pick_quoted_candle(_candles(), CUTOFF, POLICY_EXACT_HOUR)
    b = pick_quoted_candle(_candles(), CUTOFF, POLICY_LAST_24H)
    assert candle_mid(a) == candle_mid(b)


def test_last_24h_recovers_when_18h_has_no_quote():
    candles = []
    for c in _candles():
        c = dict(c)
        if c["end_period_ts"] == CUTOFF:
            c = {**c, "yes_bid": {"close": None}, "yes_ask": {"close": None}}
        candles.append(c)
    assert pick_quoted_candle(candles, CUTOFF, POLICY_EXACT_HOUR) is None
    assert pick_candle(candles, CUTOFF, POLICY_EXACT_HOUR) is not None
    b = pick_quoted_candle(candles, CUTOFF, POLICY_LAST_24H)
    assert b is not None
    mid = candle_mid(b)
    assert mid is not None
    assert abs(mid[0] - 0.11) < 1e-9
    verdict = classify_window(candles, CUTOFF)
    assert verdict["policy_a_exact_hour"] is False
    assert verdict["policy_b_last_24h"] is True
    assert verdict["recovered"] is True


def test_exact_hour_drops_when_only_earlier_candles():
    candles = [c for c in _candles() if c["end_period_ts"] < CUTOFF]
    assert pick_quoted_candle(candles, CUTOFF, POLICY_EXACT_HOUR) is None
    b = pick_quoted_candle(candles, CUTOFF, POLICY_LAST_24H)
    assert candle_mid(b)[0] == 0.11


def test_last_24h_ignores_candle_older_than_24h():
    old_ts = CUTOFF - 25 * 3600
    candles = [{
        "end_period_ts": old_ts,
        "yes_bid": {"close": "0.4000"},
        "yes_ask": {"close": "0.5000"},
    }]
    assert pick_quoted_candle(candles, CUTOFF, POLICY_LAST_24H) is None
    assert pick_quoted_candle(candles, CUTOFF, POLICY_EXACT_HOUR) is None
