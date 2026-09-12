"""EMOS gaussien par station et par saison / Gaussian EMOS per station-season.

FR : La correction ville actuelle (StationBias) est un EMOS à deux nombres :
mu = moyenne_des_modèles + biais, sigma = écart des restes, figé. B1 demande
le modèle à quatre nombres de Gneiting et al. (2005) :

    y ~ N(a + b · moyenne_ensemble, c + d · variance_ensemble)

paramètres par (station, variable, lead, saison), ajustés en minimisant le
CRPS moyen (formule fermée pour une loi normale). c > 0, d ≥ 0.

La saison est la saison météo (DJF, MAM, JJA, SON). Sur le jeu A1, TRAIN
s'arrête au 2 août : MAM et JJA seulement. SON (septembre) n'a aucun jour
d'apprentissage. On le dit, on ne l'invente pas.

EN : Four-parameter Gaussian EMOS (Gneiting et al. 2005), CRPS-fitted,
per station / variable / lead / meteorological season. Seasonal groups
with fewer than MIN_TRAIN_EMOS pairs are not fitted.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Optional

from .iem_cli import CliDay
from .skill import SIGMA_FLOOR_F, ForecastPoint

# 4 paramètres : 30 paires minimum pour ne pas ajuster le bruit.
MIN_TRAIN_EMOS = 30
# Plancher numérique sur c (variance) : 0.01 °F², pas le plancher Brier 1 °F.
C_FLOOR = 0.01
# d peut être nul (l'écart des modèles n'aide pas).
D_FLOOR = 0.0


def meteo_season(d: date) -> str:
    """Saison météo : DJF / MAM / JJA / SON."""
    m = d.month
    if m in (12, 1, 2):
        return "DJF"
    if m in (3, 4, 5):
        return "MAM"
    if m in (6, 7, 8):
        return "JJA"
    return "SON"


def _phi(z: float) -> float:
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def _phi_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def crps_gaussian(mu: float, sigma: float, y: float) -> float:
    """CRPS d'une N(mu, sigma²) contre y (Gneiting et al. 2005, éq. 5).

    CRPS = σ [ z (2Φ(z) − 1) + 2φ(z) − 1/√π ] avec z = (y − μ) / σ.
    Si σ ≤ 0, le score devient |y − μ| (loi dégénérée).
    """
    if sigma <= 1e-12:
        return abs(y - mu)
    z = (y - mu) / sigma
    return sigma * (z * (2.0 * _phi_cdf(z) - 1.0) + 2.0 * _phi(z) - 1.0 / math.sqrt(math.pi))


def ensemble_variance(per_model: dict) -> float:
    """Variance population des modèles (même convention que ForecastPoint.spread)."""
    vals = list(per_model.values())
    if len(vals) < 2:
        return 0.0
    mu = sum(vals) / len(vals)
    return sum((v - mu) ** 2 for v in vals) / len(vals)


@dataclass(frozen=True)
class EmosParams:
    a: float
    b: float
    c: float
    d: float
    n_train: int
    crps_train: float
    season: str
    fallback: bool = False  # True = groupé sans saison (pas assez de jours)

    def apply(self, mean: float, variance: float) -> tuple[float, float]:
        mu = self.a + self.b * mean
        var = self.c + self.d * max(0.0, variance)
        sigma = math.sqrt(max(C_FLOOR, var))
        return mu, max(SIGMA_FLOOR_F, sigma)


def _ols(xs: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den < 1e-9:
        return my - mx, 1.0
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    return my - b * mx, b


def _mean_crps(params: tuple[float, float, float, float],
               means: list[float], variances: list[float], obs: list[float]) -> float:
    a, b, c, d = params
    c = max(C_FLOOR, c)
    d = max(D_FLOOR, d)
    total = 0.0
    for m, v, y in zip(means, variances, obs):
        mu = a + b * m
        sigma = math.sqrt(max(C_FLOOR, c + d * max(0.0, v)))
        total += crps_gaussian(mu, sigma, y)
    return total / len(obs)


def _nelder_mead(fn, x0: list[float], max_iter: int = 250, tol: float = 1e-7) -> list[float]:
    """Nelder-Mead standard, sans dépendance externe.

    Simplexe initial : x0 et x0 ± 0.05·(|x_i|+0.1) sur chaque axe.
    """
    n = len(x0)
    simplex = [list(x0)]
    for i in range(n):
        y = list(x0)
        y[i] += 0.05 * (abs(x0[i]) + 0.1)
        simplex.append(y)
    scores = [fn(s) for s in simplex]
    alpha, gamma, rho, sigma = 1.0, 2.0, 0.5, 0.5
    for _ in range(max_iter):
        order = sorted(range(n + 1), key=lambda i: scores[i])
        simplex = [simplex[i] for i in order]
        scores = [scores[i] for i in order]
        best, worst = scores[0], scores[-1]
        if worst - best < tol:
            break
        centroid = [sum(simplex[i][j] for i in range(n)) / n for j in range(n)]
        reflected = [centroid[j] + alpha * (centroid[j] - simplex[-1][j]) for j in range(n)]
        fr = fn(reflected)
        if scores[0] <= fr < scores[-2]:
            simplex[-1], scores[-1] = reflected, fr
            continue
        if fr < scores[0]:
            expanded = [centroid[j] + gamma * (reflected[j] - centroid[j]) for j in range(n)]
            fe = fn(expanded)
            if fe < fr:
                simplex[-1], scores[-1] = expanded, fe
            else:
                simplex[-1], scores[-1] = reflected, fr
            continue
        contracted = [centroid[j] + rho * (simplex[-1][j] - centroid[j]) for j in range(n)]
        fc = fn(contracted)
        if fc < scores[-1]:
            simplex[-1], scores[-1] = contracted, fc
            continue
        for i in range(1, n + 1):
            simplex[i] = [simplex[0][j] + sigma * (simplex[i][j] - simplex[0][j]) for j in range(n)]
            scores[i] = fn(simplex[i])
    return simplex[0]


def _pack(a: float, b: float, log_c: float, raw_d: float) -> tuple[float, float, float, float]:
    return a, b, math.exp(log_c), max(D_FLOOR, raw_d)


def fit_emos_group(means: list[float], variances: list[float], obs: list[float],
                   season: str, fallback: bool = False) -> Optional[EmosParams]:
    """Ajuste (a, b, c, d) par CRPS minimum. None si trop peu de paires."""
    n = len(obs)
    if n < MIN_TRAIN_EMOS:
        return None
    a0, b0 = _ols(means, obs)
    resid = [y - (a0 + b0 * m) for m, y in zip(means, obs)]
    var_r = sum(r * r for r in resid) / n
    c0 = max(C_FLOOR, var_r)
    d0 = 0.0
    x0 = [a0, b0, math.log(c0), d0]

    def objective(x):
        return _mean_crps(_pack(x[0], x[1], x[2], x[3]), means, variances, obs)

    x = _nelder_mead(objective, x0)
    a, b, c, d = _pack(x[0], x[1], x[2], x[3])
    crps = _mean_crps((a, b, c, d), means, variances, obs)
    return EmosParams(a=a, b=b, c=c, d=d, n_train=n, crps_train=crps,
                      season=season, fallback=fallback)


@dataclass
class Emos:
    """Tables EMOS : saisonnière, puis repli sans saison (même lead)."""
    seasonal: dict = None   # (station, var, lead, season) → EmosParams
    pooled: dict = None     # (station, var, lead) → EmosParams

    def __post_init__(self):
        if self.seasonal is None:
            self.seasonal = {}
        if self.pooled is None:
            self.pooled = {}

    def fit(self, points: list[ForecastPoint],
            truth_by: dict[tuple[str, date], CliDay]) -> "Emos":
        seasonal_rows: dict[tuple, list[tuple[float, float, float]]] = defaultdict(list)
        pooled_rows: dict[tuple, list[tuple[float, float, float]]] = defaultdict(list)
        for p in points:
            d = truth_by.get((p.station, p.target))
            if d is None:
                continue
            obs = d.value_for(p.variable)
            if obs is None:
                continue
            triple = (p.mean, ensemble_variance(p.per_model), obs)
            season = meteo_season(p.target)
            seasonal_rows[(p.station, p.variable, p.lead, season)].append(triple)
            pooled_rows[(p.station, p.variable, p.lead)].append(triple)
        for key, rows in seasonal_rows.items():
            params = fit_emos_group(
                [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows],
                season=key[3], fallback=False,
            )
            if params is not None:
                self.seasonal[key] = params
        for key, rows in pooled_rows.items():
            params = fit_emos_group(
                [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows],
                season="all", fallback=True,
            )
            if params is not None:
                self.pooled[key] = params
        return self

    def apply(self, p: ForecastPoint) -> Optional[tuple[float, float, EmosParams]]:
        """(mu, sigma, params) ou None. Saison d'abord, sinon repli sans saison."""
        season = meteo_season(p.target)
        params = self.seasonal.get((p.station, p.variable, p.lead, season))
        if params is None:
            params = self.pooled.get((p.station, p.variable, p.lead))
        if params is None:
            return None
        mu, sig = params.apply(p.mean, ensemble_variance(p.per_model))
        return mu, sig, params

    def coverage(self) -> dict:
        n_seasonal = len(self.seasonal)
        n_pooled = len(self.pooled)
        seasons = sorted({k[3] for k in self.seasonal})
        return {
            "n_seasonal_groups": n_seasonal,
            "n_pooled_groups": n_pooled,
            "seasons_fitted": seasons,
            "min_train_emos": MIN_TRAIN_EMOS,
        }
