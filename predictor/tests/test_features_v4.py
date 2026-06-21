"""Tests for the V4 feature set and the revision drift annotation (B23, 2026-06-21).

V4 adds `forecast_revision` — the change in p_consensus between the earliest
and latest capture of the same market ticker.  The annotation step
`dataset.annotate_revision_drift()` must be called on ALL records (before
`keep_earliest_with_quote`) to populate the `_revision` field.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.learning.features import (
    FEATURES_V4,
    FEATURE_SETS,
    extract,
    f_forecast_revision,
    f_series_bias_prior,
)
from src.learning.dataset import annotate_revision_drift


# ---------- helpers ----------

def _rec(p_clim, p_blend, p_ens, ticker="T-ALPHA", capture_at="20260619T120000Z",
         series_ticker="KXLOWTCHI"):
    return {
        "ticker": ticker,
        "event_ticker": series_ticker + "-26JUN20",
        "series_ticker": series_ticker,
        "predictions": {
            "climatology": {"prob_yes": p_clim},
            "forecast_blend": {
                "prob_yes": p_blend,
                "inputs": {"days_ahead": 2},
            },
            "ensemble": {
                "prob_yes": p_ens,
                "inputs": {"individual_probs": {"ecmwf": 0.5, "gfs": 0.5}},
            },
        },
        "target_date": "2026-06-21",
        "_capture_at": capture_at,
        "yes_mid": 0.55,
    }


# ---------- annotate_revision_drift ----------

class TestAnnotateRevisionDrift:
    def test_single_capture_gives_none(self):
        records = [_rec(0.6, 0.5, 0.55, capture_at="20260619T120000Z")]
        annotate_revision_drift(records)
        assert records[0]["_revision"] is None

    def test_two_captures_computes_revision(self):
        early = _rec(0.4, 0.4, 0.4, capture_at="20260618T120000Z")
        late  = _rec(0.7, 0.7, 0.7, capture_at="20260619T120000Z")
        records = [early, late]
        annotate_revision_drift(records)
        # mean early = 0.4, mean late = 0.7 → revision = 0.7 - 0.4 = 0.3
        assert records[0]["_revision"] is not None
        assert abs(records[0]["_revision"] - 0.3) < 1e-9
        assert records[0]["_revision"] == records[1]["_revision"]

    def test_two_tickers_independent(self):
        r1a = _rec(0.3, 0.3, 0.3, ticker="T-A", capture_at="20260618T120000Z")
        r1b = _rec(0.6, 0.6, 0.6, ticker="T-A", capture_at="20260619T120000Z")
        r2a = _rec(0.8, 0.8, 0.8, ticker="T-B", capture_at="20260618T120000Z")
        r2b = _rec(0.5, 0.5, 0.5, ticker="T-B", capture_at="20260619T120000Z")
        records = [r1a, r1b, r2a, r2b]
        annotate_revision_drift(records)
        # T-A: 0.6 - 0.3 = 0.3
        assert abs(r1a["_revision"] - 0.3) < 1e-9
        # T-B: 0.5 - 0.8 = -0.3
        assert abs(r2a["_revision"] - (-0.3)) < 1e-9

    def test_missing_consensus_gives_none(self):
        # Record with None p_consensus (missing ensemble)
        r_early = {
            "ticker": "T-MISS",
            "event_ticker": "KXLOWTCHI-26JUN20",
            "_capture_at": "20260618T120000Z",
            "predictions": {},
        }
        r_late = _rec(0.6, 0.6, 0.6, ticker="T-MISS", capture_at="20260619T120000Z")
        records = [r_early, r_late]
        annotate_revision_drift(records)
        assert r_early["_revision"] is None


# ---------- f_forecast_revision ----------

class TestForecastRevision:
    def test_reads_revision_field(self):
        rec = _rec(0.5, 0.5, 0.5)
        rec["_revision"] = 0.15
        assert abs(f_forecast_revision(rec) - 0.15) < 1e-9

    def test_missing_field_returns_none(self):
        rec = _rec(0.5, 0.5, 0.5)
        # No _revision key
        assert f_forecast_revision(rec) is None

    def test_none_revision_returns_none(self):
        rec = _rec(0.5, 0.5, 0.5)
        rec["_revision"] = None
        assert f_forecast_revision(rec) is None


# ---------- FEATURES_V4 registration ----------

class TestFeaturesV4:
    def test_v4_in_feature_sets_registry(self):
        assert "v4" in FEATURE_SETS
        assert FEATURE_SETS["v4"] is FEATURES_V4

    def test_v4_has_five_features(self):
        names = [n for n, _ in FEATURES_V4]
        assert names == [
            "p_consensus",
            "forecast_spread",
            "days_ahead",
            "series_bias_prior",
            "forecast_revision",
        ]

    def test_v4_extract_drops_row_without_revision(self):
        rec = _rec(0.6, 0.5, 0.55, series_ticker="KXLOWTCHI")
        # No _revision annotated → extract returns None (row dropped)
        result = extract(rec, FEATURES_V4)
        assert result is None

    def test_v4_extract_succeeds_with_revision(self):
        rec = _rec(0.6, 0.5, 0.55, series_ticker="KXLOWTCHI")
        rec["_revision"] = 0.08
        result = extract(rec, FEATURES_V4)
        assert result is not None
        assert "forecast_revision" in result
        assert abs(result["forecast_revision"] - 0.08) < 1e-9
        assert "series_bias_prior" in result
