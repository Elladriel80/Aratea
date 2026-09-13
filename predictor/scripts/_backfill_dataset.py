"""_backfill_dataset.py — reconstruct point-in-time training rows from settled markets.

Exploratory script (underscore prefix — production code under src/ stays
immutable). Goal: massively grow the learned-predictor dataset, whose real
bottleneck is distinct-target_date accumulation (live forward captures add
~1 date/day). PAST settled Kalshi weather markets are abundant, and
Open-Meteo's Previous Runs API archives what each weather model predicted
1-7 days before validity (hourly variables suffixed _previous_day1 ..
_previous_day7). Combining the two reconstructs "what the live pipeline
would have captured" for hundreds of historical event-days.

Workflow:
  1. For each series, pull settled events from Kalshi and keep only
     resolved central bins (strike_type == "between" — same filter as
     scripts/backtest.py and the live daily_auto bin selection).
  2. For each market and each lead N in --days-ahead, simulate a capture
     at as_of = target_date - N days, 18:00 UTC:
       - yes_mid from the Kalshi candlesticks endpoint. Default policy
         last_24h: last hourly candle with a two-sided quote in the 24 h
         before the 18:00 UTC capture (live path, then /historical).
         exact_hour (flag) requires the 18:00 bar itself. Rows without a
         two-sided quote are dropped — the benchmark is kalshi_mid.
       - the three REAL production predictors (climatology, forecast_blend,
         ensemble — same factories as scripts/forward_predict.py) run
         unmodified, with exactly two script-side adaptations:
           a. date.today() is monkeypatched to as_of inside the
              forecast_blend / ensemble modules (tight scope) so
              days_ahead is computed historically;
           b. the weather client is a wrapper that serves Previous Runs
              data at lead N (hourly *_previous_dayN aggregated to daily
              in the station's local timezone). Climatology keeps the REAL
              archive path — it is already strict point-in-time (only uses
              calendar years up to target_date.year - 1, same wiring as
              scripts/backtest.py).
  3. Records are assembled in EXACTLY the forward_*.json schema, then
     features come from src.learning.features.extract() — so the learning
     loop sees feature semantics identical to the live dataset builder.
  4. Output: {"X": [...], "y": [...], "meta": [...]} directly consumable
     by _learning_loop.py --dataset-cache, plus <out>.summary.json with
     skip-reason counters and the per-model Previous Runs coverage
     actually observed (never assumed).

Every HTTP response is cached on disk under data/backfill_cache/ (one JSON
per request key) — reruns are cheap and interrupted runs resume. NOTE: a
full multi-year, all-series run is tens of thousands of HTTP calls; start
with --smoke, then scope with --series / --start-date.

Usage:
    python predictor/scripts/_backfill_dataset.py --smoke --debug
    python predictor/scripts/_backfill_dataset.py --series KXLOWTNYC,KXHIGHTSFO
    python predictor/scripts/_backfill_dataset.py --days-ahead 1,2,3
    python predictor/scripts/_backfill_dataset.py --validate-against-live
    python predictor/scripts/_learning_loop.py \
        --dataset-cache data/backfill/backfill_dataset.json
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.kalshi.candles import (  # noqa: E402
    CAPTURE_HOUR_UTC,
    CANDLE_POLICIES,
    LAST_24H_S,
    POLICY_LAST_24H,
    candle_mid,
    candle_ts,
    fetch_candles,
    pick_candle,
    pick_quoted_candle,
)
from src.kalshi.client import KalshiClient  # noqa: E402
from src.learning.features import FEATURE_SETS, extract  # noqa: E402
from src.predictors.climatology import ClimatologyPredictor  # noqa: E402
from src.predictors.ensemble import EnsemblePredictor  # noqa: E402
from src.predictors.forecast_blend import ForecastBlendPredictor  # noqa: E402
from src.predictors.parsers import (  # noqa: E402
    SERIES_MAP,
    parse_kalshi_date,
    parse_market,
)
from src.weather.open_meteo import (  # noqa: E402
    DEFAULT_ENSEMBLE,
    DailyForecast,
    OpenMeteoClient,
)

PREVIOUS_RUNS_BASE = "https://previous-runs-api.open-meteo.com/v1/forecast"
BACKFILL_CACHE_DIR = ROOT / "data" / "backfill_cache"
DEFAULT_OUT = ROOT / "data" / "backfill" / "backfill_dataset.json"
CANDLE_LOOKBACK_S = LAST_24H_S  # same window as policy last_24h (A/B share it)
PREV_RUNS_SLEEP = 0.2           # polite pacing on cache miss (on top of 429 handling)
MIN_HOURS_FOR_TEMP_EXTREME = 18  # refuse a daily max/min from a partial day

# Features with no historical coverage — adding them drops almost all rows.
FORWARD_ONLY_FEATURES = {"p_nws_ndfd"}

# Features that require train-time fold-aware computation (they read a
# pre-computed field that only exists in augmented dataset files, never in
# raw backfill records).  Excluding these prevents every row from being
# dropped when --features full is used.
FOLD_AWARE_FEATURES = {
    "series_bias_fa",
    "p_consensus_x_series_bias_fa",
    "days_ahead_x_series_bias_fa",
    "forecast_revision",
}

# ------------------------------------------------------------ feature spec

def feature_spec(kind: str) -> list[tuple]:
    """(name, fn) list. 'full' = union of every registered set minus
    forward-only and fold-aware features.  Fold-aware features (series_bias_fa,
    etc.) cannot be extracted from raw records; they are derived at train time
    by the learning loop.  This matches the union _learning_loop.py builds for
    its default candidate queue so the cache passes its coverage check.
    'v3' = just the v3 base set (more rows survive: the geographic
    features only cover stations mapped in src/learning/geographic.py)."""
    cat: dict = {}
    for spec in FEATURE_SETS.values():
        for name, fn in spec:
            cat.setdefault(name, fn)
    SKIP = FORWARD_ONLY_FEATURES | FOLD_AWARE_FEATURES
    if kind == "v3":
        names = [n for n, _ in FEATURE_SETS["v3"]]
    else:
        names = sorted(n for n in cat if n not in SKIP)
    return [(n, cat[n]) for n in names]


# ------------------------------------------------------- pure helpers (tested)

def aggregate_hourly(times: list, values: list | None, target_iso: str,
                     how: str):
    """Aggregate one hourly series to a daily value for target_iso.

    `times` are local-timezone stamps as returned by Open-Meteo when
    timezone=<station tz> is passed — filtering on the date prefix IS the
    local-day aggregation. Daily max/min are refused when fewer than
    MIN_HOURS_FOR_TEMP_EXTREME hours are present (a 5-hour max is not a
    daily high)."""
    vals = [v for t, v in zip(times or [], values or [])
            if t[:10] == target_iso and v is not None]
    if not vals:
        return None
    if how in ("max", "min") and len(vals) < MIN_HOURS_FOR_TEMP_EXTREME:
        return None
    if how == "max":
        return max(vals)
    if how == "min":
        return min(vals)
    if how == "sum":
        return sum(vals)
    raise ValueError(f"unknown aggregation {how!r}")


# --------------------------------------------- Previous Runs weather wrapper

class PreviousRunsWeatherClient:
    """Implements the OpenMeteoClient surface the production predictors
    call, with forecasts served from the Previous Runs API at the lead
    implied by the current (as_of, target_date) context.

    Interface points (read from src/predictors/*.py):
      - historical(...) / historical_observations(lat, lon, start, end,
        timezone=...) — used by ClimatologyPredictor. Delegated UNCHANGED
        to a real OpenMeteoClient (archive API): climatology is already
        strict point-in-time (years <= target.year - 1).
      - forecast(lat, lon, days=..., timezone=..., use_cache=...) — used by
        ForecastBlendPredictor; must return {"daily": {"time": [...],
        "temperature_2m_max": [...], ...}}. The live deterministic
        best-of-models forecast is not archived, so we serve the unweighted
        mean across the ensemble models' previous-run values — the closest
        stable proxy (recorded in the summary as an assumption).
      - forecast_multi_model(lat, lon, models=..., days=..., timezone=...,
        use_cache=...) — used by EnsemblePredictor; returns
        {model: [DailyForecast]} with a single entry at target_date.
    """

    def __init__(self, archive: OpenMeteoClient, prev: OpenMeteoClient,
                 leads: list[int], models: list[str] | None = None,
                 debug: bool = False):
        self.archive = archive
        self.prev = prev  # OpenMeteoClient with cache_dir=data/backfill_cache
        self.leads = sorted(set(leads))
        self.models = list(models or DEFAULT_ENSEMBLE)
        self.debug = debug
        self.as_of: date | None = None
        self.target: date | None = None
        self.coverage = {m: {"first_date_with_data": None,
                             "dates_with_data": 0, "dates_queried": 0}
                         for m in self.models}
        self._coverage_seen: set = set()
        self._logged_keys = False

    def set_context(self, as_of: date, target: date) -> None:
        self.as_of, self.target = as_of, target

    @property
    def lead(self) -> int:
        return (self.target - self.as_of).days

    # -- climatology path: real archive, untouched --
    def historical(self, *a, **kw):
        return self.archive.historical(*a, **kw)

    def historical_observations(self, *a, **kw):
        return self.archive.historical_observations(*a, **kw)

    # -- previous runs fetch + parse --
    def _fetch(self, lat: float, lon: float, tz: str) -> dict:
        target_iso = self.target.isoformat()
        variables = ("temperature_2m", "precipitation", "snowfall")
        hourly_full = [f"{v}_previous_day{n}"
                       for n in self.leads for v in variables]
        hourly_temp = [f"temperature_2m_previous_day{n}" for n in self.leads]

        def params_for(hourly: list[str]) -> dict:
            return {"latitude": lat, "longitude": lon,
                    "start_date": target_iso, "end_date": target_iso,
                    "hourly": ",".join(hourly),
                    "models": ",".join(self.models), "timezone": tz,
                    "temperature_unit": "fahrenheit",
                    "precipitation_unit": "mm"}

        key = (f"{lat:.4f}_{lon:.4f}_{target_iso}"
               f"_l{'-'.join(map(str, self.leads))}"
               f"_{'-'.join(sorted(self.models))}")

        def fetcher() -> dict:
            time.sleep(PREV_RUNS_SLEEP)
            try:
                return self.prev._get(PREVIOUS_RUNS_BASE,
                                      params_for(hourly_full))
            except requests.HTTPError:
                # Some model/variable combos 400 — fall back to temp only
                # (every current SERIES_MAP variable is temp_max/temp_min).
                return self.prev._get(PREVIOUS_RUNS_BASE,
                                      params_for(hourly_temp))

        return self.prev.cached_or_fetch("prevruns", key, fetcher)

    def _model_daily(self, data: dict, model: str) -> dict:
        """Aggregate one model's hourly *_previous_day<lead> series to the
        daily fields the predictors read, in the station's local tz."""
        hourly = data.get("hourly") or {}
        times = hourly.get("time") or []
        n = self.lead

        def series(var: str):
            k = f"{var}_previous_day{n}_{model}"
            if k in hourly:
                return hourly.get(k)
            # Single-model responses come back without the model suffix.
            if len(self.models) == 1:
                return hourly.get(f"{var}_previous_day{n}")
            return None

        t_iso = self.target.isoformat()
        temp = series("temperature_2m")
        return {
            "temperature_2m_max": aggregate_hourly(times, temp, t_iso, "max"),
            "temperature_2m_min": aggregate_hourly(times, temp, t_iso, "min"),
            "precipitation_sum": aggregate_hourly(
                times, series("precipitation"), t_iso, "sum"),
            "snowfall_sum": aggregate_hourly(
                times, series("snowfall"), t_iso, "sum"),
        }

    def _per_model_dailies(self, lat: float, lon: float, tz: str) -> dict:
        data = self._fetch(lat, lon, tz)
        if self.debug and not self._logged_keys:
            keys = sorted((data.get("hourly") or {}).keys())
            print(f"   [debug] previous-runs hourly keys ({len(keys)}): "
                  f"{keys[:8]} ...")
            self._logged_keys = True
        out: dict = {}
        t_iso = self.target.isoformat()
        for m in self.models:
            d = self._model_daily(data, m)
            out[m] = d
            seen = (m, t_iso, self.lead)
            if seen not in self._coverage_seen:
                self._coverage_seen.add(seen)
                cov = self.coverage[m]
                cov["dates_queried"] += 1
                if d["temperature_2m_max"] is not None:
                    cov["dates_with_data"] += 1
                    first = cov["first_date_with_data"]
                    if first is None or t_iso < first:
                        cov["first_date_with_data"] = t_iso
        return out

    # -- predictor-facing surface --
    def forecast(self, lat, lon, days=14, timezone="auto", use_cache=True):
        per_model = self._per_model_dailies(lat, lon, timezone)
        daily: dict = {"time": [self.target.isoformat()]}
        for field in ("temperature_2m_max", "temperature_2m_min",
                      "precipitation_sum", "snowfall_sum"):
            vals = [d[field] for d in per_model.values()
                    if d[field] is not None]
            daily[field] = [statistics.fmean(vals) if vals else None]
        return {"daily": daily}

    def forecast_multi_model(self, lat, lon, models=None, days=7,
                             timezone="auto", use_cache=True):
        per_model = self._per_model_dailies(lat, lon, timezone)
        out: dict = {}
        for m in (models or self.models):
            d = per_model.get(m) or {}
            out[m] = [DailyForecast(
                model=m, date=self.target,
                temperature_max_f=d.get("temperature_2m_max"),
                temperature_min_f=d.get("temperature_2m_min"),
                precipitation_sum_mm=d.get("precipitation_sum"),
                rain_sum_mm=None,
                snowfall_sum_cm=d.get("snowfall_sum"),
            )]
        return out


# ------------------------------------------------------- record reconstruction

def _slim_inputs(inputs: dict) -> dict:
    """Mirror scripts/forward_predict.py::_slim_inputs exactly."""
    drop_keys = {"climato_years_used"}
    return {k: v for k, v in inputs.items() if k not in drop_keys}


def _fake_today(as_of: date):
    class _AsOfDate(date):
        @classmethod
        def today(cls):
            return as_of
    return _AsOfDate


def run_predictors(predictors: dict, spec, as_of: date,
                   weather: PreviousRunsWeatherClient) -> dict:
    """Run the real predictors at a simulated as_of. The date patch is
    scoped to this call and targets only the two modules that compute
    days_ahead from date.today()."""
    weather.set_context(as_of, spec.target_date)
    fake = _fake_today(as_of)
    with mock.patch("src.predictors.forecast_blend.date", fake), \
         mock.patch("src.predictors.ensemble.date", fake):
        return {name: p.predict(spec) for name, p in predictors.items()}


def assemble_record(spec, ev, market, as_of: date, preds: dict,
                    quote: tuple) -> dict:
    """Build a record in EXACTLY the forward_*.json schema (see
    scripts/forward_predict.py) so src.learning.features.extract() sees
    identical structure to a live capture."""
    mid, bid, ask = quote
    snapshot_at = as_of.strftime("%Y%m%d") + f"T{CAPTURE_HOUR_UTC:02d}0000Z"
    return {
        "ticker": market.ticker,
        "event_ticker": ev.event_ticker,
        "series_ticker": ev.series_ticker or market.ticker.split("-")[0],
        "subtitle": market.subtitle,
        "target_date": spec.target_date.isoformat(),
        "variable": spec.variable,
        "location_key": spec.location_key,
        "lower": spec.lower,
        "upper": spec.upper,
        "yes_bid": bid,
        "yes_ask": ask,
        "yes_mid": mid,
        "snapshot_at": snapshot_at,
        "predictions": {
            name: {"prob_yes": p.prob_yes, "method": p.method,
                   "inputs": _slim_inputs(p.inputs)}
            for name, p in preds.items()
        },
    }


# --------------------------------------------------------------- validation

def validate_against_live(out_path: Path) -> int:
    """Anti-leakage / faithfulness check: intersect backfilled rows with
    live captures (loaded the same way src/learning/dataset.py does) on
    ticker, and report absolute differences on the probability-derived
    features and yes_mid. No thresholds — just the verdict table."""
    if not out_path.exists():
        raise SystemExit(f"{out_path} not found — run the backfill first.")
    data = json.loads(out_path.read_text(encoding="utf-8"))
    X, meta = data["X"], data["meta"]
    from src.learning.dataset import (
        keep_earliest_with_quote,
        load_forward_records,
    )
    live = keep_earliest_with_quote(load_forward_records())
    print(f">> live captures (earliest-with-quote): {len(live)} tickers")
    print(f">> backfilled rows: {len(X)}")

    fns = dict(feature_spec("full"))
    by_ticker: dict = {}
    for feats, m in zip(X, meta):
        by_ticker.setdefault(m["ticker"], []).append((feats, m))

    candidate_keys = ["p_climatology", "p_forecast_blend", "p_ensemble",
                      "p_consensus", "forecast_spread", "days_ahead"]
    compare_keys = [k for k in candidate_keys if X and k in X[0]]
    diffs: dict = {k: [] for k in compare_keys + ["yes_mid"]}

    n_compared = 0
    for r in live:
        rows = by_ticker.get(r["ticker"])
        if not rows:
            continue
        live_da = fns["days_ahead"](r)
        ref = live_da if live_da is not None else 0.0
        feats, m = min(rows,
                       key=lambda fm: abs(fm[0].get("days_ahead", 0) - ref))
        n_compared += 1
        for k in compare_keys:
            lv = fns[k](r)
            if lv is not None:
                diffs[k].append(abs(lv - feats[k]))
        if r.get("yes_mid") is not None and m.get("yes_mid") is not None:
            diffs["yes_mid"].append(abs(r["yes_mid"] - m["yes_mid"]))

    print(f">> tickers compared: {n_compared}")
    if n_compared == 0:
        print("!! no overlap between live captures and backfilled rows. "
              "Backfill a date range covered by forward_*.json captures.")
        return 1
    print(f"\n   {'feature':<22} {'n':>5} {'mean|d|':>10} {'median|d|':>10}")
    for k, vals in diffs.items():
        if not vals:
            print(f"   {k:<22} {0:>5} {'-':>10} {'-':>10}")
            continue
        print(f"   {k:<22} {len(vals):>5} "
              f"{statistics.fmean(vals):>10.4f} "
              f"{statistics.median(vals):>10.4f}")
    print("\n   (days_ahead compares the live capture horizon vs the "
          "closest backfilled lead — a nonzero value there means the two "
          "rows are at different horizons, which inflates the other "
          "deltas. yes_mid compares live mid vs candle-close mid.)")
    return 0


# --------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--series", default=",".join(SERIES_MAP),
                    help="comma list of series tickers "
                         "(default: every series in SERIES_MAP)")
    ap.add_argument("--start-date", default="2024-01-01",
                    help="earliest target_date (most models archived since "
                         "2024-01; coverage is probed, not assumed)")
    ap.add_argument("--end-date",
                    default=(date.today() - timedelta(days=7)).isoformat(),
                    help="latest target_date (default: today-7)")
    ap.add_argument("--days-ahead", default="1",
                    help="comma list of leads in 1..7; each lead produces a "
                         "separate row per market (capture_at = target - N)")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--features", choices=["full", "v3"], default="full",
                    help="'full' = union the learning loop's default queue "
                         "needs (geo features drop stations not mapped in "
                         "geographic.py); 'v3' = base set only, more rows")
    ap.add_argument("--smoke", action="store_true",
                    help="1 series, max 20 events — first local validation")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--validate-against-live", action="store_true",
                    help="compare an existing --out dataset against live "
                         "forward captures (no backfill run)")
    ap.add_argument("--candle-policy", choices=list(CANDLE_POLICIES),
                    default=POLICY_LAST_24H,
                    help="exact_hour = bougie pile à 18:00 UTC (A). "
                         "last_24h = dernière bougie cotée dans les 24 h "
                         "avant 18:00 (B, défaut). Même fenêtre de fetch.")
    args = ap.parse_args()

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path

    if args.validate_against_live:
        return validate_against_live(out_path)

    leads = [int(x) for x in args.days_ahead.split(",") if x.strip()]
    if not leads or any(n < 1 or n > 7 for n in leads):
        raise SystemExit("--days-ahead values must be within 1..7 "
                         "(Previous Runs archive depth)")
    series_list = [s.strip() for s in args.series.split(",") if s.strip()]
    unknown = [s for s in series_list if s not in SERIES_MAP]
    if unknown:
        raise SystemExit(f"unknown series (not in SERIES_MAP): {unknown}")
    if args.smoke:
        # Prefer a geo-covered witness series: feature extraction (full
        # spec) drops every row for cities absent from
        # geographic.LOCATION_KEY_TO_ICAO (e.g. Atlanta).
        series_list = (["KXLOWTNYC"] if "KXLOWTNYC" in series_list
                       else series_list[:1])
    start = date.fromisoformat(args.start_date)
    end = date.fromisoformat(args.end_date)
    spec_features = feature_spec(args.features)

    print(f">> series: {len(series_list)}  leads: {leads}  "
          f"range: {start}..{end}  features: {args.features} "
          f"({len(spec_features)})  candle_policy: {args.candle_policy}")
    BACKFILL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    archive = OpenMeteoClient()  # shares the live data/forecasts cache
    prev = OpenMeteoClient(cache_dir=BACKFILL_CACHE_DIR)
    weather = PreviousRunsWeatherClient(archive, prev, leads,
                                        debug=args.debug)
    # Same factories as scripts/forward_predict.py — identical defaults
    # (climatology 30y/±3d; blend & ensemble 15y/±5d).
    predictors = {
        "climatology": ClimatologyPredictor(weather),
        "forecast_blend": ForecastBlendPredictor(weather),
        "ensemble": EnsemblePredictor(weather),
    }
    client = KalshiClient()

    X: list[dict] = []
    y: list[int] = []
    meta: list[dict] = []
    skips: Counter = Counter()
    per_series_rows: dict = {}
    n_events_total = 0
    first_candle_logged = False

    for si, series in enumerate(series_list, 1):
        events = []
        try:
            for ev in client.list_events(series_ticker=series,
                                         status="settled",
                                         with_nested_markets=True):
                parts = ev.event_ticker.split("-")
                d = parse_kalshi_date(parts[1]) if len(parts) >= 2 else None
                if d is None:
                    skips["event_date_unparsable"] += 1
                    continue
                if not (start <= d <= end):
                    continue
                events.append((d, ev))
        except Exception as e:
            print(f"!! {series}: list_events failed: "
                  f"{type(e).__name__}: {e}")
            continue
        events.sort(key=lambda t: t[0])
        if args.smoke:
            # Most RECENT 20: validates the candle/markets schema on data
            # that certainly still has full API coverage. Archive depth
            # is probed by the full run, not the smoke.
            events = events[-20:]
        n_events_total += len(events)
        rows_before = len(X)

        for d, ev in events:
            if not ev.markets:
                # /events?with_nested_markets=true returns some (mostly
                # older) events WITHOUT nested markets. The per-event
                # endpoint nests reliably — refetch once.
                try:
                    ev = client.get_event(ev.event_ticker,
                                          with_nested_markets=True)
                except Exception as e:
                    skips["event_refetch_error"] += 1
                    if args.debug:
                        print(f"   [debug] refetch {ev.event_ticker}: "
                              f"{type(e).__name__}: {e}")
                    continue
                if not ev.markets:
                    skips["event_no_markets"] += 1
                    if args.debug:
                        print(f"   [debug] {ev.event_ticker}: no nested "
                              f"markets; raw keys={sorted(ev.raw.keys())}")
                    continue
            for market in ev.markets:
                if market.result not in ("yes", "no"):
                    skips["unresolved_market"] += 1
                    continue
                # Same central-bin filter as backtest.py / daily_auto:
                # only strike_type == "between" (tail bins are cumulative
                # mass and are not scored by the deployed model).
                raw = next((r for r in (ev.raw.get("markets") or [])
                            if r.get("ticker") == market.ticker), None)
                if raw is None or raw.get("strike_type") != "between":
                    skips["not_between_bin"] += 1
                    continue
                spec = parse_market(market)
                if spec is None:
                    skips["unparsable_market"] += 1
                    continue

                for n in leads:
                    as_of = spec.target_date - timedelta(days=n)
                    cutoff = datetime(as_of.year, as_of.month, as_of.day,
                                      CAPTURE_HOUR_UTC, tzinfo=timezone.utc)
                    cutoff_ts = int(cutoff.timestamp())
                    try:
                        data = fetch_candles(client, series, market.ticker,
                                             cutoff_ts, BACKFILL_CACHE_DIR,
                                             lookback_s=CANDLE_LOOKBACK_S)
                    except Exception as e:
                        skips["candle_fetch_error"] += 1
                        if args.debug:
                            print(f"   [err] candles {market.ticker} J-{n}: "
                                  f"{type(e).__name__}: {e}")
                        continue
                    candles = (data.get("candlesticks")
                               if isinstance(data, dict) else None)
                    if args.debug and candles and not first_candle_logged:
                        print(f"   [debug] first raw candle: "
                              f"{json.dumps(candles[0])[:400]}")
                        first_candle_logged = True
                    raw = pick_candle(candles, cutoff_ts, args.candle_policy)
                    if raw is None:
                        skips["no_candle_at_capture"] += 1
                        continue
                    c = pick_quoted_candle(candles, cutoff_ts,
                                           args.candle_policy)
                    if c is None:
                        skips["no_two_sided_quote"] += 1
                        continue
                    quote = candle_mid(c)
                    if quote is None:
                        skips["no_two_sided_quote"] += 1
                        continue

                    try:
                        preds = run_predictors(predictors, spec, as_of,
                                               weather)
                    except Exception as e:
                        skips["predictor_error"] += 1
                        if args.debug:
                            print(f"   [err] predict {market.ticker} J-{n}: "
                                  f"{type(e).__name__}: {e}")
                        continue
                    # A live capture at this horizon would have had real
                    # forecast data; a climato-only fallback row is not
                    # representative — drop and count.
                    if (preds["forecast_blend"].method != "forecast_blend"
                            or preds["ensemble"].method != "ensemble"):
                        skips["predictor_fallback_no_forecast"] += 1
                        continue

                    rec = assemble_record(spec, ev, market, as_of, preds,
                                          quote)
                    feats = extract(rec, spec_features)
                    if feats is None:
                        miss = next((nm for nm, fn in spec_features
                                     if fn(rec) is None), "?")
                        skips[f"feature_missing:{miss}"] += 1
                        continue
                    X.append(feats)
                    y.append(1 if market.result == "yes" else 0)
                    meta.append({
                        "ticker": market.ticker,
                        "event_ticker": ev.event_ticker,
                        "target_date": rec["target_date"],
                        "capture_at": rec["snapshot_at"],
                        "yes_mid": quote[0],
                        "days_ahead": n,
                        "series_ticker": rec["series_ticker"],
                        "source": "backfill_previous_runs",
                        "candle_policy": args.candle_policy,
                        "candle_end_ts": candle_ts(c),
                    })
        per_series_rows[series] = len(X) - rows_before
        print(f">> [{si}/{len(series_list)}] {series:<13} "
              f"events={len(events):>4}  rows+={len(X) - rows_before:>5}  "
              f"total={len(X)}")

    # ---- summary --------------------------------------------------------
    distinct_dates = len({m["target_date"] for m in meta})
    print(f"\n>> rows kept: {len(X)}   distinct target_dates: "
          f"{distinct_dates}   events scanned: {n_events_total}")
    print(">> skip counts:")
    for reason, cnt in sorted(skips.items(), key=lambda kv: -kv[1]):
        print(f"   {reason:<40} {cnt}")
    print(">> previous-runs coverage observed (per model):")
    for m, cov in weather.coverage.items():
        print(f"   {m:<22} first_date_with_data={cov['first_date_with_data']}"
              f"  dates={cov['dates_with_data']}/{cov['dates_queried']}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"X": X, "y": y, "meta": meta}),
                        encoding="utf-8")
    summary = {
        "schema": "backfill_dataset_summary/1",
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
            "params": {"series": series_list, "start_date": args.start_date,
                   "end_date": args.end_date, "days_ahead": leads,
                   "features": args.features,
                   "feature_names": [n for n, _ in spec_features],
                   "smoke": args.smoke,
                   "candle_policy": args.candle_policy},
        "assumptions": {
            "capture_time_utc": f"{CAPTURE_HOUR_UTC:02d}:00",
            "candle_policy": args.candle_policy,
            "candle_lookback_s": CANDLE_LOOKBACK_S,
            "deterministic_forecast_proxy":
                "mean across ensemble models' previous-run values "
                "(best-of-models forecast is not archived)",
            "min_hours_for_temp_extreme": MIN_HOURS_FOR_TEMP_EXTREME,
        },
        "totals": {"rows": len(X),
                   "distinct_target_dates": distinct_dates,
                   "distinct_tickers": len({m["ticker"] for m in meta}),
                   "events_scanned": n_events_total},
        "rows_per_series": per_series_rows,
        "skips": dict(skips),
        "previous_runs_coverage": weather.coverage,
    }
    summary_path = Path(str(out_path) + ".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2),
                            encoding="utf-8")
    print(f"\n>> wrote {out_path}")
    print(f">> wrote {summary_path}")
    print(">> next: python predictor/scripts/_learning_loop.py "
          f"--dataset-cache {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# end
