"""Learned model wrappers — LogisticRegression L2 and GradientBoosting.

Simple by design. The point of Phase A.3 isn't a fancy model — it's a
trained model where each feature's weight is explicit and we can
iterate on the feature set.

GBMLearnedModel is the GBM hypothesis (2026-06-20): captures non-linear
interactions that LR misses (e.g. p_consensus × forecast_spread coupling).
"""
from __future__ import annotations

from dataclasses import dataclass, field

# sklearn is the only external dep. If it's not installed:
#   pip install --break-system-packages scikit-learn
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


@dataclass
class LearnedModel:
    feature_names: list[str]
    scaler: StandardScaler = field(default_factory=StandardScaler)
    clf: LogisticRegression = field(default_factory=lambda: LogisticRegression(
        penalty="l2",
        C=1.0,           # smaller C = more regularization. Start at 1.0.
        solver="lbfgs",
        max_iter=2000,
        random_state=42,
    ))

    def _matrix(self, X: list[dict]) -> np.ndarray:
        return np.array(
            [[row[name] for name in self.feature_names] for row in X],
            dtype=float,
        )

    def fit(self, X: list[dict], y: list[int]) -> "LearnedModel":
        Xm = self._matrix(X)
        Xs = self.scaler.fit_transform(Xm)
        self.clf.fit(Xs, y)
        return self

    def predict_proba(self, X: list[dict]) -> np.ndarray:
        """Return P(YES) for each row, shape (n,)."""
        Xm = self._matrix(X)
        Xs = self.scaler.transform(Xm)
        return self.clf.predict_proba(Xs)[:, 1]

    def feature_importance(self) -> list[tuple[str, float]]:
        """Coefficients on the standardized feature matrix.

        Bigger absolute value = stronger pull on the prediction. Sign
        indicates direction (positive = pushes toward YES, negative
        pushes toward NO).
        """
        if not hasattr(self.clf, "coef_"):
            return []
        coefs = self.clf.coef_[0]
        return list(zip(self.feature_names, coefs.tolist()))


@dataclass
class GBMLearnedModel:
    """GBM alternative — captures non-linear interactions between features.

    Hypothesis: the relationship between p_consensus and the outcome is
    modulated by forecast_spread (high spread → consensus less reliable).
    A depth-2 tree can model this second-order effect; LR cannot.

    Params kept intentionally weak (depth=2, n_estimators=30, subsample=0.8)
    to avoid overfitting on small weather-date datasets (~400-500 rows).
    """
    feature_names: list[str]
    scaler: StandardScaler = field(default_factory=StandardScaler)
    clf: GradientBoostingClassifier = field(default_factory=lambda: GradientBoostingClassifier(
        n_estimators=30,
        max_depth=2,
        learning_rate=0.1,
        subsample=0.8,
        min_samples_leaf=10,
        random_state=42,
    ))

    def _matrix(self, X: list[dict]) -> np.ndarray:
        return np.array(
            [[row[name] for name in self.feature_names] for row in X],
            dtype=float,
        )

    def fit(self, X: list[dict], y: list[int]) -> "GBMLearnedModel":
        Xm = self._matrix(X)
        Xs = self.scaler.fit_transform(Xm)
        self.clf.fit(Xs, np.asarray(y, dtype=int))
        return self

    def predict_proba(self, X: list[dict]) -> np.ndarray:
        """Return P(YES) for each row, shape (n,)."""
        Xm = self._matrix(X)
        Xs = self.scaler.transform(Xm)
        return self.clf.predict_proba(Xs)[:, 1]

    def feature_importance(self) -> list[tuple[str, float]]:
        """Gini-based feature importances (GBM intrinsic)."""
        if not hasattr(self.clf, "feature_importances_"):
            return []
        return list(zip(self.feature_names, self.clf.feature_importances_.tolist()))


def brier_score(y_true: list[int], p_yes: np.ndarray) -> float:
    y = np.asarray(y_true, dtype=float)
    return float(np.mean((p_yes - y) ** 2))


def log_loss(y_true: list[int], p_yes: np.ndarray, eps: float = 1e-9) -> float:
    y = np.asarray(y_true, dtype=float)
    p = np.clip(p_yes, eps, 1.0 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
