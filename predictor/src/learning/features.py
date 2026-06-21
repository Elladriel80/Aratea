"""Feature extraction for the learned predictor.

A feature extractor is a pure function from a forward-capture record
(`predictor/data/predictions/forward_*.json` entry, with `predictions`
dict, `yes_mid`, etc.) to a dict of named numeric features.

Each feature is a separate function so we can easily ADD/DROP features
during the iterative feature engineering loop and track each one's
contribution to model accuracy.

The current registered feature set is exposed as FEATURES_V0 (the
starter set) and incremented to FEATURES_V1, V2, etc. as we validate
new features empirically.

Naming discipline: every feature name MUST evoke an atmospheric or
contextual hypothesis. No f1, f2, x_42 — use names like p_nws_ndfd,
urban_density_5km, forecast_revision_velocity_24h. The catalog of all
features (with hypothesis, source, status, measured Brier delta) lives
in FEATURES.md next to this file.
"""
from __future__ import annotations

import datetime as _dt
import math
from typing import Any, Callable


# ---------- Individual feature extractors ----------

def f_p_climatology(rec: dict[str, Any]) -> float | None:
    """The climatology predictor's P(YES)."""
    return _get_pred(rec, "climatology")


def f_p_forecast_blend(rec: dict[str, Any]) -> float | None:
    """The forecast_blend predictor's P(YES)."""
    return _get_pred(rec, "forecast_blend")


def f_p_ensemble(rec: dict[str, Any]) -> float | None:
    """The meta-ensemble predictor's P(YES)."""
    return _get_pred(rec, "ensemble")


def f_forecast_spread(rec: dict[str, Any]) -> float | None:
    """Spread (max - min) across the per-vendor forecast probabilities.

    Looks inside `predictions.ensemble.inputs.individual_probs` (or
    similar) if available. If not, fall back to abs(blend - climatology)
    as a crude proxy of disagreement.
    """
    ens = rec.get("predictions", {}).get("ensemble", {})
    inputs = ens.get("inputs", {}) if isinstance(ens, dict) else {}
    indiv = inputs.get("individual_probs") or inputs.get("per_model_probs")
    if isinstance(indiv, dict) and indiv:
        vals = [float(v) for v in indiv.values() if v is not None]
        if vals:
            return max(vals) - min(vals)
    # Fallback proxy
    blend = f_p_forecast_blend(rec)
    clim = f_p_climatology(rec)
    if blend is None or clim is None:
        return None
    return abs(blend - clim)


def f_p_consensus(rec: dict[str, Any]) -> float | None:
    """Mean of the three correlated probability views (climatology +
    forecast_blend + ensemble) — the single "location" parameter of the
    prediction.

    Hypothesis: the three probability features are near-collinear (they all
    estimate the same P(YES) by different routes). Under L2 the learner
    splits one signal across three coefficients with compensating signs
    (the +1.07 / -0.87 / -0.40 pattern observed on the v2 run), which is
    noise, not structure. Collapsing them into their mean keeps the shared
    signal on one stable coefficient; the orthogonal disagreement axis is
    carried separately by `forecast_spread`. This is the standard
    mean + spread reparametrisation of a collinear block.

    Returns None (row dropped, never imputed) if any of the three
    underlying probabilities is missing, mirroring the v0/v2 contract.
    """
    parts = [
        f_p_climatology(rec),
        f_p_forecast_blend(rec),
        f_p_ensemble(rec),
    ]
    if any(p is None for p in parts):
        return None
    return sum(parts) / len(parts)


def f_days_ahead(rec: dict[str, Any]) -> float | None:
    """How far ahead (in days) the forecast is — 0 = same day, 7 = a week out.

    Looks first in predictions.forecast_blend.inputs.days_ahead, then
    derives from target_date vs snapshot_at if not present.
    """
    fb = rec.get("predictions", {}).get("forecast_blend", {})
    inputs = fb.get("inputs", {}) if isinstance(fb, dict) else {}
    if "days_ahead" in inputs and inputs["days_ahead"] is not None:
        return float(inputs["days_ahead"])
    # Derive from dates if possible
    target = rec.get("target_date")
    snap = rec.get("snapshot_at") or rec.get("_capture_at")
    if target and snap:
        try:
            from datetime import datetime
            t = datetime.strptime(target, "%Y-%m-%d").date()
            # snap is like "20260508T104500Z"
            s = datetime.strptime(snap[:8], "%Y%m%d").date()
            return float((t - s).days)
        except Exception:
            return None
    return None


# ---------- Interaction features ----------

def f_is_hightemp(rec: dict[str, Any]) -> float | None:
    """Binary indicator: 1.0 for high-temperature contracts (KXHIGHT*), 0.0 for low-temp.

    Hypothesis: high-temp (KXHIGHT*) and low-temp (KXLOWT*) contracts show
    systematically different p_consensus biases. On 61 dates, KXHIGHTSFO has
    bias(p_consensus - y) = -0.090 vs -0.081 for KXLOWTCHI and -0.069 for
    KXLOWTNYC. A single global LR intercept cannot correct this per-series
    asymmetry. Adding this binary flag lets the model learn a series-specific
    offset for free (one extra coefficient).

    Source: derived from event_ticker prefix (2026-06-20). Status: experimental.
    """
    ticker = (rec.get("event_ticker") or rec.get("ticker") or "").upper()
    if "HIGHT" in ticker:
        return 1.0
    elif "LOWT" in ticker:
        return 0.0
    return None


def f_consensus_x_spread(rec: dict[str, Any]) -> float | None:
    """Interaction term: p_consensus × forecast_spread.

    Hypothesis: the predictive value of p_consensus is modulated by the
    level of disagreement between vendor models (forecast_spread). When
    spread is high, the "consensus" is fragile — a seemingly high p_consensus
    of 0.7 backed by vendors ranging 0.2–0.9 is far less informative than
    0.7 with spread 0.05. LR cannot learn this coupling from p_consensus and
    forecast_spread alone; giving it the product lets it fit a first-order
    interaction on one coefficient, without the structural changes needed by
    a tree model.

    Source: derived from f_p_consensus and f_forecast_spread (2026-06-20).
    Status: experimental.
    """
    pc = f_p_consensus(rec)
    fs = f_forecast_spread(rec)
    if pc is None or fs is None:
        return None
    return pc * fs


# ---------- V1 feature: NWS NDFD vendor forecast ----------

def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _prob_in_interval(mu: float, sigma: float,
                       lower: float | None, upper: float | None) -> float:
    if sigma <= 0:
        if lower is not None and mu < lower:
            return 0.0
        if upper is not None and mu > upper:
            return 0.0
        return 1.0
    p_lo = _normal_cdf((lower - mu) / sigma) if lower is not None else 0.0
    p_hi = _normal_cdf((upper - mu) / sigma) if upper is not None else 1.0
    return max(0.0, min(1.0, p_hi - p_lo))


def _sigma_from_climato(rec: dict[str, Any]) -> float | None:
    """Estimate sigma the same way ForecastBlendPredictor does: range/4."""
    clim = rec.get("predictions", {}).get("climatology", {})
    inputs = clim.get("inputs", {}) if isinstance(clim, dict) else {}
    vmin, vmax = inputs.get("value_min"), inputs.get("value_max")
    if vmin is None or vmax is None or vmax <= vmin:
        # forecast_blend inputs sometimes carry sigma_climato directly
        fb = rec.get("predictions", {}).get("forecast_blend", {})
        fb_inputs = fb.get("inputs", {}) if isinstance(fb, dict) else {}
        sc = fb_inputs.get("sigma_climato")
        if sc is not None:
            return float(sc)
        return None
    return max(1.0, (float(vmax) - float(vmin)) / 4.0)


def f_p_nws_ndfd(rec: dict[str, Any]) -> float | None:
    """P(YES) computed from the NWS NDFD official forecast.

    Hypothesis: Kalshi weather markets resolve on the NWS Climatological
    Report. A forecast from the same agency that issues the truth should
    dominate generic vendor blends.

    NDFD is forward-only (no historical archives), so for any record with
    target_date < today this returns None and the row is dropped. The
    feature gains coverage as forward captures accumulate going forward.
    """
    target = rec.get("target_date")
    variable = rec.get("variable")
    lower, upper = rec.get("lower"), rec.get("upper")
    location_key = rec.get("location_key")
    if not (target and variable and location_key):
        return None

    # NDFD only covers ~7 days forward. Skip everything outside that window
    # to avoid wasted requests and confusing cache pollution.
    try:
        t = _dt.date.fromisoformat(target)
    except Exception:
        return None
    today = _dt.date.today()
    days_ahead = (t - today).days
    if days_ahead < 0 or days_ahead > 6:
        return None

    # Resolve station coordinates from the project's CITIES table.
    try:
        from src.weather import CITIES  # local import to keep import graph shallow
    except Exception:
        return None
    city = CITIES.get(location_key)
    if not city:
        return None

    # Variable to NDFD field.
    try:
        from src.forecast.nws_ndfd import fetch_forecast
    except Exception:
        return None
    try:
        fc = fetch_forecast(city["lat"], city["lon"], target)
    except Exception:
        return None

    if variable == "temp_max":
        mu = fc.get("temp_max_f")
    elif variable == "temp_min":
        mu = fc.get("temp_min_f")
    elif variable == "precip_in":
        # precipitation_amount_in not yet available from NDFD periods endpoint
        return None
    elif variable == "snow_in":
        return None
    else:
        return None

    if mu is None:
        return None

    sigma = _sigma_from_climato(rec)
    if sigma is None:
        return None

    # Same integer-rounding correction as forecast_blend for temperature bounds.
    is_temp = variable in ("temp_max", "temp_min")
    eff_lower = (lower - 0.5) if (is_temp and lower is not None) else lower
    eff_upper = (upper + 0.5) if (is_temp and upper is not None) else upper
    return _prob_in_interval(float(mu), float(sigma), eff_lower, eff_upper)


# ---------- Registry ----------

# A feature spec is (name, extractor_fn). Order matters for the model's
# coefficient inspection.

FEATURES_V0: list[tuple[str, Callable[[dict[str, Any]], float | None]]] = [
    ("p_climatology",   f_p_climatology),
    ("p_forecast_blend", f_p_forecast_blend),
    ("p_ensemble",       f_p_ensemble),
    ("forecast_spread",  f_forecast_spread),
    ("days_ahead",       f_days_ahead),
]

# V1: adds NWS NDFD vendor probability. Note that p_nws_ndfd is None on
# rows whose target_date is in the past — historical captures predate the
# NDFD integration. V1's effective row count will be very small until
# daily forward captures start carrying NDFD natively.
FEATURES_V1: list[tuple[str, Callable[[dict[str, Any]], float | None]]] = (
    FEATURES_V0 + [
        ("p_nws_ndfd", f_p_nws_ndfd),
    ]
)


# ---------- V2 features: static geographic context per station ----------

def _geo_value(rec: dict[str, Any], key: str) -> float | None:
    """Look up a static geographic value for the record's location_key.

    Returns None if the station hasn't been built into stations.json yet
    or if the value is missing — so the row is dropped instead of
    silently zero-imputed.
    """
    loc = rec.get("location_key")
    if not loc:
        return None
    try:
        from src.learning.geographic import lookup_for_location_key
    except Exception:
        return None
    s = lookup_for_location_key(loc)
    if not s:
        return None
    v = s.get(key)
    return float(v) if v is not None else None


def f_urban_density_5km(rec: dict[str, Any]) -> float | None:
    """OSM building feature count within 5 km of the station.

    Proxy for the urban heat island. Dense urban cores retain nighttime
    warmth and bias the low-temperature distribution upward vs. the
    climatology built from older / less built-up neighbouring stations.
    Count rather than %-area because computing %-area would require
    polygon geometry parsing (shapely) which is out of scope here.
    """
    return _geo_value(rec, "urban_density_5km")


def f_water_pct_10km(rec: dict[str, Any]) -> float | None:
    """Count of OSM water features (natural=water + waterway) within 10 km.

    Proxy for water-thermal-mass dampening of diurnal swings. Stations
    near large water bodies should see narrower temp ranges. Naming
    keeps the V2 "_pct_" suffix from the spec for continuity but the
    units are counts; see FEATURES.md.
    """
    return _geo_value(rec, "water_pct_10km")


def f_forest_pct_5km(rec: dict[str, Any]) -> float | None:
    """Count of OSM forest patches (natural=wood + landuse=forest) within 5 km.

    Proxy for surface shading and evapotranspiration. Forest cover
    cools daytime highs (shade + evap) and limits radiative night
    cooling (canopy traps).
    """
    return _geo_value(rec, "forest_pct_5km")


def f_elevation_m(rec: dict[str, Any]) -> float | None:
    """USGS elevation in meters at the station point.

    Thinner air at high altitude amplifies the diurnal swing — bigger
    daily max-min spread, larger sensitivity to insolation. Denver vs.
    Miami sits at opposite ends of this axis.
    """
    return _geo_value(rec, "elevation_m")


def f_distance_to_coast_km(rec: dict[str, Any]) -> float | None:
    """Haversine distance in km to the nearest Natural Earth 50m coastline vertex.

    Continental stations (Denver, Oklahoma City) see big seasonal swings
    and weak inertia; maritime stations (Boston, Miami) carry far more
    thermal mass from the adjacent ocean and have damped extremes.
    """
    return _geo_value(rec, "distance_to_coast_km")


def f_latitude(rec: dict[str, Any]) -> float | None:
    """Station absolute latitude.

    Controls insolation, daylight length, seasonal amplitude. Trivial
    feature but worth including explicitly so the model can learn the
    season-vs-latitude interaction without us baking it into climatology.
    """
    return _geo_value(rec, "latitude")


# V2: V0 baseline + the 6 static geographic context features.
# p_nws_ndfd is intentionally *not* in V2: NDFD has no historical archive,
# so adding it forces every old row to drop and the training set vanishes.
# It gets its own training pass (--feature-set v1) once forward captures
# accumulate NDFD readings.
FEATURES_V2: list[tuple[str, Callable[[dict[str, Any]], float | None]]] = (
    FEATURES_V0 + [
        ("urban_density_5km",     f_urban_density_5km),
        ("water_pct_10km",        f_water_pct_10km),
        ("forest_pct_5km",        f_forest_pct_5km),
        ("elevation_m",           f_elevation_m),
        ("distance_to_coast_km",  f_distance_to_coast_km),
        ("latitude",              f_latitude),
    ]
)


# ---------- V3 features: collinearity fix, geographic noise removed ----------

# V3 is the corrected Phase 1 feature set decided on 2026-06-04 (NO-GO
# verdict on v2). Two changes vs v0/v2, both motivated by the v2 run's
# measured feature signal:
#
#   1. Collapse the three near-collinear probability features
#      (p_climatology, p_forecast_blend, p_ensemble) into a single
#      `p_consensus` (their mean). The v2 run showed the classic L2
#      multicollinearity pattern — large compensating coefficients
#      (+1.07 / -0.87 / -0.40) on what is essentially one signal. The
#      orthogonal "how much do the vendors disagree" axis stays as
#      `forecast_spread`.
#   2. Drop the six static geographic features (urban_density_5km,
#      water_pct_10km, forest_pct_5km, elevation_m, distance_to_coast_km,
#      latitude). Measured as pure noise as additive linear terms on v2
#      (|coef| < 0.04, Brier deltas in the 1e-5 band). Kept in FEATURES.md
#      as `dropped` for institutional memory; candidates for re-test as
#      interactions, not additive features.
#
# `days_ahead` is retained: it is neither collinear with the probability
# block nor geographic, and the forecast-horizon axis is a legitimate
# (if weak) signal that is orthogonal to both v3 changes. A 2-feature
# variant {p_consensus, forecast_spread} can be A/B-tested later if
# days_ahead proves to be noise on v3 as well.
FEATURES_V3: list[tuple[str, Callable[[dict[str, Any]], float | None]]] = [
    ("p_consensus",     f_p_consensus),
    ("forecast_spread", f_forecast_spread),
    ("days_ahead",      f_days_ahead),
]

# V3+: V3 extended with experimental features tested 2026-06-20.
# Not promoted to a numbered version until holdout verdict is known.
FEATURES_V3_EXPERIMENTAL: list[tuple[str, Callable[[dict[str, Any]], float | None]]] = [
    ("p_consensus",          f_p_consensus),
    ("forecast_spread",      f_forecast_spread),
    ("days_ahead",           f_days_ahead),
    ("consensus_x_spread",   f_consensus_x_spread),
    ("is_hightemp",          f_is_hightemp),
]


# ---------- V3b: hierarchical per-series calibration (B24) ----------

# Observed mean bias per series_ticker on backfill_dataset (61 dates, 1467 rows).
# Bias = mean(p_consensus - y): negative → model overestimates.
# WARNING: these values were estimated on the full dataset (incl. holdout).
# For a proper cross-validated evaluation, re-estimate from the training fold
# only. Treating this as a fixed prior is an approximation valid only if the
# per-series bias is structurally stable across time.
_SERIES_BIAS_PRIOR: dict[str, float] = {
    "KXHIGHTSFO": -0.090,
    "KXLOWTCHI":  -0.081,
    "KXLOWTNYC":  -0.069,
    "KXLOWTMIA":  -0.055,
    "KXLOWTBOS":  -0.002,
    "KXLOWTLAX":   0.000,
}


def _series_ticker_from_rec(rec: dict[str, Any]) -> str | None:
    """Extract series_ticker (e.g. 'KXLOWTCHI') from event_ticker or ticker."""
    et = rec.get("series_ticker") or rec.get("event_ticker") or rec.get("ticker") or ""
    if not et:
        return None
    # event_ticker = 'KXLOWTCHI-26APR14' → split at '-' and take the first part
    part = et.split("-")[0].upper()
    return part if part else None


def f_series_bias_prior(rec: dict[str, Any]) -> float | None:
    """Known structural bias for the market series — mean(p_consensus - y) per series.

    Hypothesis: each Kalshi weather series (KXHIGHTSFO, KXLOWTCHI…) shows a
    stable, series-specific offset between the consensus forecast and the
    realised outcome. On 61 dates the offsets range from -0.090 (SFO high)
    to ~0.000 (LAX/BOS). `is_hightemp` only captures the largest-bias split
    (SFO vs all others); this feature generalises it to a continuous prior,
    letting LR learn a single correction coefficient instead of per-series
    dummies. Expected learned coefficient ≈ -1 (full bias correction).

    Leakage caveat: the bias values in `_SERIES_BIAS_PRIOR` were estimated on
    the full 61-date dataset. Treat as a prior/hyperparameter, not a live
    label-derived feature. Re-estimate from the training fold before any
    holdout evaluation.

    Source: backfill_dataset analysis 2026-06-21. Status: experimental (B24).
    """
    st = _series_ticker_from_rec(rec)
    if st is None:
        return None
    return _SERIES_BIAS_PRIOR.get(st)


# V3b = V3 + series_bias_prior (generalised calibration). Replaces is_hightemp.
# Evaluation pending (B24): run learning loop on backfill_dataset with
# --feature-set v3b and compare holdout Brier vs v3 baseline.
FEATURES_V3B: list[tuple[str, Callable[[dict[str, Any]], float | None]]] = [
    ("p_consensus",        f_p_consensus),
    ("forecast_spread",    f_forecast_spread),
    ("days_ahead",         f_days_ahead),
    ("series_bias_prior",  f_series_bias_prior),
]


# ---------- V3fa: fold-aware bias (B35 — biais estimés depuis TRAIN uniquement) ----------

# Same concept as V3b but the bias values are estimated from the TRAIN fold
# only (no leakage into VALID/HOLDOUT).  Stored in pre-computed dataset files
# as the key "series_bias_fa" (see backfill_dataset_v3b_fa.json).
# The extractor just reads the pre-computed value from the record dict.

def f_series_bias_fa(rec: dict[str, Any]) -> float | None:
    """Fold-aware series bias — estimated from TRAIN dates only.

    Same semantics as f_series_bias_prior but without data leakage:
    bias values are computed from the TRAIN window before being applied
    to VALID/HOLDOUT. Must use a pre-augmented dataset (backfill_dataset_v3b_fa.json)
    where the key 'series_bias_fa' is already present.

    Source: B35 fold-aware evaluation 2026-06-21.
    """
    v = rec.get("series_bias_fa")
    return float(v) if v is not None else None


FEATURES_V3FA: list[tuple[str, Callable[[dict[str, Any]], float | None]]] = [
    ("p_consensus",      f_p_consensus),
    ("forecast_spread",  f_forecast_spread),
    ("days_ahead",       f_days_ahead),
    ("series_bias_fa",   f_series_bias_fa),
]


# ---------- V4 features: forecast revision drift (B23) ----------

def f_forecast_revision(rec: dict[str, Any]) -> float | None:
    """Change in p_consensus between the earliest and latest capture of the same ticker.

    Revision = p_consensus(latest capture, fewest days_ahead)
              − p_consensus(earliest capture, most days_ahead).

    Hypothesis: when the model consensus moves materially between the first and last
    observed snapshot of a market, the direction of that move (toward YES or toward
    NO) carries information about atmospheric persistence.  A rising consensus
    (positive revision) suggests the atmosphere is "confirming" the event; a falling
    consensus (negative revision) suggests the event is becoming less likely as
    measurement uncertainty resolves.  This is distinct from days_ahead (which
    captures horizon-level accuracy decay) and from p_consensus (which captures
    current level) — the revision is the VELOCITY component of the forecast signal.

    Data requirement: at least two captures of the same ticker must exist in
    `data/predictions/`.  `dataset.annotate_revision_drift()` must be called on
    all records BEFORE `keep_earliest_with_quote`.  Use `dataset.build_with_revision`
    instead of `dataset.build` when this feature is in the spec.

    Returns None (row dropped) when only one capture exists for the ticker or when
    p_consensus is unavailable in either capture.

    Source: derived across multiple forward_*.json captures (B23, 2026-06-21).
    Status: experimental — evaluation pending once daily captures accumulate
    (need ≥ 2 captures per ticker → run for 2+ consecutive days without backfilling).
    """
    return rec.get("_revision")


# V4 = V3b + forecast revision drift.
# REQUIRES dataset.build_with_revision (not dataset.build) to annotate _revision.
# Rows without multi-capture history are dropped (feature returns None).
# Expected to activate once the daily forward pipeline has run for ≥ 2 days on
# the same markets — the backfill_dataset.json has only one capture per ticker.
FEATURES_V4: list[tuple[str, Callable[[dict[str, Any]], float | None]]] = [
    ("p_consensus",        f_p_consensus),
    ("forecast_spread",    f_forecast_spread),
    ("days_ahead",         f_days_ahead),
    ("series_bias_prior",  f_series_bias_prior),
    ("forecast_revision",  f_forecast_revision),
]


# ---------- V3fb: interaction features on fold-aware bias (B38) ----------

def f_p_consensus_x_series_bias_fa(rec: dict[str, Any]) -> float | None:
    """Interaction p_consensus × series_bias_fa (fold-aware).

    Hypothesis: the series-specific bias correction should scale with
    forecast confidence. When p_consensus is high (0.85) and the series
    systematically overestimates (bias_fa = -0.090), the calibration error
    is larger in absolute probability space than at moderate consensus (0.50).
    An additive series_bias_fa (v3fa) removes a fixed offset; this interaction
    lets LR learn a conditional correction that grows with p_consensus.

    Requires series_bias_fa to be pre-annotated in the record (same as v3fa).
    Source: B38, 2026-06-21.
    """
    pc = f_p_consensus(rec)
    sb = f_series_bias_fa(rec)
    if pc is None or sb is None:
        return None
    return pc * sb


def f_days_ahead_x_series_bias_fa(rec: dict[str, Any]) -> float | None:
    """Interaction days_ahead × series_bias_fa (fold-aware).

    Hypothesis: the per-series calibration bias may be horizon-dependent.
    At 3 days ahead, NWP forecasts carry more uncertainty; the market may
    over- or under-correct relative to the 1-day-ahead case differently
    per series. This lets LR learn a horizon-scaled bias correction per
    series without full series × horizon dummies.

    Requires series_bias_fa to be pre-annotated in the record (same as v3fa).
    Source: B38, 2026-06-21.
    """
    da = f_days_ahead(rec)
    sb = f_series_bias_fa(rec)
    if da is None or sb is None:
        return None
    return da * sb


FEATURES_V3FB: list[tuple[str, Callable[[dict[str, Any]], float | None]]] = [
    ("p_consensus",                  f_p_consensus),
    ("forecast_spread",              f_forecast_spread),
    ("days_ahead",                   f_days_ahead),
    ("series_bias_fa",               f_series_bias_fa),
    ("p_consensus_x_series_bias_fa", f_p_consensus_x_series_bias_fa),
    ("days_ahead_x_series_bias_fa",  f_days_ahead_x_series_bias_fa),
]


# Convenience map for --feature-set CLI flag.
FEATURE_SETS: dict[str, list[tuple[str, Callable[[dict[str, Any]], float | None]]]] = {
    "v0":   FEATURES_V0,
    "v1":   FEATURES_V1,
    "v2":   FEATURES_V2,
    "v3":   FEATURES_V3,
    "v3x":  FEATURES_V3_EXPERIMENTAL,
    "v3b":  FEATURES_V3B,
    "v3fa": FEATURES_V3FA,
    "v3fb": FEATURES_V3FB,
    "v4":   FEATURES_V4,
}


# ---------- Helpers ----------

def _get_pred(rec: dict[str, Any], predictor_name: str) -> float | None:
    pred = rec.get("predictions", {}).get(predictor_name, {})
    p = pred.get("prob_yes") if isinstance(pred, dict) else None
    return float(p) if p is not None else None


def extract(rec: dict[str, Any],
            spec: list[tuple[str, Callable]]) -> dict[str, float] | None:
    """Run all extractors against `rec`. Returns None if any feature is
    missing (so the row is dropped from training rather than silently
    imputed with 0/mean)."""
    out: dict[str, float] = {}
    for name, fn in spec:
        v = fn(rec)
        if v is None:
            return None
        out[name] = v
    return out
