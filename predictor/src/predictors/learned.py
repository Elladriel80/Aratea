"""LearnedPredictor — live inference for the sklearn LR L2 model trained in
runs_learning/.

This predictor reconstructs the trained model in-memory from the run.json
written by `scripts/train_learned.py` (schema v2+). No pickling: we replay
the exact closed-form formula

    p_yes = sigmoid(intercept + Σ coef_i · (x_i − mean_i) / std_i)

where `coef_i`, `mean_i`, `std_i` and `intercept` are serialised in run.json
and `x_i` is the feature value computed at inference time on the live
ContractSpec via the shared extractors in `src.learning.features`.

The predictor composes the existing sub-predictors (climatology,
forecast_blend, ensemble) to materialise a record dict that matches the
forward_*.json schema, then runs the feature extractors against it. This
guarantees train-time and inference-time features stay consistent — same
code path on both sides.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

from src.weather import OpenMeteoClient
from src.learning.features import FEATURE_SETS, extract
from .base import ContractSpec, Prediction, Predictor
from .climatology import ClimatologyPredictor
from .forecast_blend import ForecastBlendPredictor
from .ensemble import EnsemblePredictor


REQUIRED_SCHEMA_VERSION = 2


def _learned_trained_at_from_registry(registry: dict) -> Optional[str]:
    """Pick the learned model's `trained_at` pin from a CHAMPION.json dict.

    Prefers a model entry whose `method`/`name` marks it as learned and that
    carries a `trained_at`; falls back to any entry with a feature_set +
    trained_at. Returns None if no learned entry is pinned.
    """
    for m in registry.get("models") or []:
        method = (m.get("method") or "")
        name = (m.get("name") or "")
        if (method.startswith("learned") or name.startswith("learned")) \
                and m.get("trained_at"):
            return m.get("trained_at")
    for m in registry.get("models") or []:
        if m.get("feature_set") and m.get("trained_at"):
            return m.get("trained_at")
    return None


def _resolve_run_json_from_registry(
    runs_root: Path,
    trained_at: Optional[str] = None,
    registry: Optional[dict] = None,
) -> Path:
    """Resolve the PINNED runs_learning/<trained_at>/run.json.

    The run is pinned by CHAMPION.json: each model entry carries a `trained_at`
    timestamp that names its runs_learning/<trained_at>/ folder. We deliberately
    do NOT fall back to "the latest run.json": a freshly trained, non-promotable
    run would silently shadow the pinned model and invalidate every Brier
    comparison labelled with that model's name (revue 2026-06-10 A2 / E1).

    Resolution order:
      1. `trained_at` passed by the caller (live_run reads it from the registry).
      2. else read CHAMPION.json next to `runs_root` and pick the learned entry.
    Raises if nothing can be pinned, rather than guessing another run.
    """
    runs_root = Path(runs_root)
    if trained_at is None:
        if registry is None:
            champion_path = runs_root / "CHAMPION.json"
            if not champion_path.exists():
                raise FileNotFoundError(
                    f"Cannot resolve the pinned learned run: no CHAMPION.json "
                    f"under {runs_root} and no trained_at/run_json_path provided. "
                    f"Refusing to fall back to the latest run.json (revue A2)."
                )
            registry = json.loads(champion_path.read_text(encoding="utf-8"))
        trained_at = _learned_trained_at_from_registry(registry)

    if not trained_at:
        raise ValueError(
            "Cannot resolve the pinned learned run: CHAMPION.json has no learned "
            "model entry with a `trained_at` timestamp. Refusing to load the "
            "latest run.json instead (would shadow the pinned model — revue A2)."
        )
    run_json_path = runs_root / str(trained_at) / "run.json"
    if not run_json_path.exists():
        raise FileNotFoundError(
            f"Pinned learned run {run_json_path} (trained_at={trained_at} from "
            f"CHAMPION.json) does not exist. Train it or fix the registry pin; "
            f"NOT falling back to another run (revue A2)."
        )
    return run_json_path


def _sigmoid(z: float) -> float:
    # Guard against overflow on extreme logits.
    if z >= 0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    ez = math.exp(z)
    return ez / (1.0 + ez)


class LearnedPredictor(Predictor):
    """Sklearn LR L2 over named features. Live inference, no refit."""

    name = "learned"

    def __init__(
        self,
        weather_client: Optional[OpenMeteoClient] = None,
        run_json_path: Optional[Path] = None,
        runs_root: Optional[Path] = None,
        trained_at: Optional[str] = None,
        sub_climato: Optional[ClimatologyPredictor] = None,
        sub_forecast_blend: Optional[ForecastBlendPredictor] = None,
        sub_ensemble: Optional[EnsemblePredictor] = None,
    ):
        # Resolve run.json path. Priority:
        #   1. explicit run_json_path (tests, ad-hoc inference)
        #   2. registry pin: runs_learning/<trained_at>/run.json, where
        #      `trained_at` comes from the caller (live_run reads it off the
        #      CHAMPION.json model entry) or, if None, is read straight from
        #      CHAMPION.json here.
        # We NEVER silently load "the latest run.json": that let a fresh
        # non-promotable run masquerade as the pinned model (revue A2 / E1).
        if run_json_path is None:
            if runs_root is None:
                # Project default: <repo>/predictor/runs_learning
                from src.config import DATA_DIR  # type: ignore
                runs_root = DATA_DIR.parent / "runs_learning"
            run_json_path = _resolve_run_json_from_registry(
                Path(runs_root), trained_at=trained_at
            )
        run_json_path = Path(run_json_path)

        record = json.loads(run_json_path.read_text(encoding="utf-8"))
        schema = int(record.get("schema_version", 1))
        if schema < REQUIRED_SCHEMA_VERSION:
            raise ValueError(
                f"run.json at {run_json_path} has schema_version={schema}, "
                f"need >= {REQUIRED_SCHEMA_VERSION}. Re-run train_learned.py to "
                f"regenerate with full inference fields (intercept, feature_means, "
                f"feature_stds)."
            )

        # Required model state
        try:
            self.feature_names: list[str] = record["feature_names"]
            self.intercept: float = float(record["intercept"])
            self.coefs: dict[str, float] = {
                k: float(v) for k, v in record["feature_importances"].items()
            }
            self.means: dict[str, float] = {
                k: float(v) for k, v in record["feature_means"].items()
            }
            self.stds: dict[str, float] = {
                k: float(v) for k, v in record["feature_stds"].items()
            }
            self.feature_set_used: str = record["feature_set_used"]
        except KeyError as e:
            raise ValueError(
                f"run.json at {run_json_path} missing required field {e}. "
                "Regenerate via train_learned.py."
            ) from e

        if self.feature_set_used not in FEATURE_SETS:
            raise ValueError(
                f"Unknown feature_set '{self.feature_set_used}'. Known: "
                f"{sorted(FEATURE_SETS.keys())}"
            )
        self.feature_spec = FEATURE_SETS[self.feature_set_used]
        self.trained_at: str = record.get("timestamp_utc", "unknown")
        self.run_json_path = run_json_path

        # Expose a richer name (e.g. "learned_v2") so multi-model reports stay legible.
        self.name = f"learned_{self.feature_set_used}"

        # Sub-predictors. Reusable — caller can inject mocks for tests or share
        # a single OpenMeteoClient across all three to dedupe cache hits.
        self.weather = weather_client or OpenMeteoClient()
        self.climato = sub_climato or ClimatologyPredictor(self.weather)
        self.forecast_blend = sub_forecast_blend or ForecastBlendPredictor(self.weather)
        self.ensemble = sub_ensemble or EnsemblePredictor(self.weather)

    def predict(self, contract: ContractSpec) -> Prediction:
        # 1. Materialise sub-predictions (same code path as forward_predict.py).
        clim_pred = self.climato.predict(contract)
        fb_pred = self.forecast_blend.predict(contract)
        ens_pred = self.ensemble.predict(contract)

        # 2. Build a record dict matching the forward_*.json shape that the
        #    feature extractors expect. The keys here mirror what forward_predict
        #    writes per market, so we can call `extract()` unchanged.
        record = {
            "location_key": contract.location_key,
            "target_date": contract.target_date.isoformat(),
            "variable": contract.variable,
            "lower": contract.lower,
            "upper": contract.upper,
            "predictions": {
                "climatology": {
                    "prob_yes": clim_pred.prob_yes,
                    "inputs": clim_pred.inputs,
                },
                "forecast_blend": {
                    "prob_yes": fb_pred.prob_yes,
                    "inputs": fb_pred.inputs,
                },
                "ensemble": {
                    "prob_yes": ens_pred.prob_yes,
                    "inputs": ens_pred.inputs,
                },
            },
        }

        # 3. Extract features (same FEATURE_SETS[set] as training).
        feats = extract(record, self.feature_spec)
        if feats is None:
            # One or more features came back None — typically a missing geo entry
            # in stations.json or an out-of-horizon forecast. Fall back to the
            # climatology prior rather than guess. The Prediction.method field
            # signals the degradation so downstream reports can flag it.
            missing = [
                name for name, fn in self.feature_spec if fn(record) is None
            ]
            return Prediction(
                contract=contract,
                prob_yes=clim_pred.prob_yes,
                method=f"{self.name}[fallback_climato]",
                inputs={
                    "reason": "feature_extraction_returned_none",
                    "missing_features": missing,
                    "feature_set": self.feature_set_used,
                    "trained_at": self.trained_at,
                    "sub_p_climatology": clim_pred.prob_yes,
                    "sub_p_forecast_blend": fb_pred.prob_yes,
                    "sub_p_ensemble": ens_pred.prob_yes,
                },
                confidence=clim_pred.confidence,
            )

        # 4. Z-score using the means/stds frozen at training time.
        z = {}
        for name in self.feature_names:
            mu = self.means[name]
            sigma = self.stds[name]
            # Guard against degenerate scaler stds (column was constant in training).
            denom = sigma if sigma > 1e-9 else 1.0
            z[name] = (feats[name] - mu) / denom

        # 5. Apply the closed-form LR: logit = intercept + Σ coef · z.
        logit = self.intercept + sum(
            self.coefs[name] * z[name] for name in self.feature_names
        )
        p_yes = _sigmoid(logit)
        # Numerical clamp — sigmoid is mathematically in (0,1) but report a clean range.
        p_yes = max(0.0, min(1.0, p_yes))

        return Prediction(
            contract=contract,
            prob_yes=p_yes,
            method=self.name,
            inputs={
                "feature_set": self.feature_set_used,
                "trained_at": self.trained_at,
                "run_json_path": str(self.run_json_path),
                "raw_features": feats,
                "z_scored": z,
                "logit": logit,
                "intercept": self.intercept,
                "sub_p_climatology": clim_pred.prob_yes,
                "sub_p_forecast_blend": fb_pred.prob_yes,
                "sub_p_ensemble": ens_pred.prob_yes,
            },
            confidence=ens_pred.confidence,
        )
