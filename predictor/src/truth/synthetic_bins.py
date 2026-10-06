"""Bins synthétiques au format Kalshi / Kalshi-shaped synthetic bins.

FR : Un marché Kalshi température est une série de bins de 2 °F entiers
inclusifs ("76° to 77°") plus deux queues. Pour mesurer le skill d'une
prévision sur des années où aucun marché n'existait, on fabrique les mêmes
bins autour de la valeur centrale prévue et on score P(bin) contre la
vérité CLI. Le marché n'intervient pas : c'est un backtest de skill pur.

EN : A Kalshi temperature market is a ladder of inclusive 2 °F integer
bins ("76° to 77°") plus two tails. To measure forecast skill over years
without a market we build the same ladder around the forecast centre and
score P(bin) against the CLI truth. Pure skill backtest, no market.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Bin:
    lower: Optional[int]   # inclusif, None = queue basse
    upper: Optional[int]   # inclusif, None = queue haute

    def contains(self, value: float) -> bool:
        v = int(round(value))
        if self.lower is not None and v < self.lower:
            return False
        if self.upper is not None and v > self.upper:
            return False
        return True

    @property
    def is_central(self) -> bool:
        return self.lower is not None and self.upper is not None

    def label(self) -> str:
        if self.lower is None:
            return f"{self.upper}° or below"
        if self.upper is None:
            return f"{self.lower}° or above"
        return f"{self.lower}° to {self.upper}°"


def kalshi_style_bins(center_f: float, n_central: int = 6, width: int = 2) -> list[Bin]:
    """Échelle de `n_central` bins de `width` °F centrée sur center_f + 2 queues.

    Exemple center=76.3, n_central=6 → [70-71, 72-73, 74-75, 76-77, 78-79,
    80-81] + "69 or below" + "82 or above". Les bins sont alignés sur des
    valeurs paires comme le fait Kalshi sur la majorité des séries.
    """
    c = int(math.floor(center_f))
    c -= c % width                      # alignement pair
    half = n_central // 2
    first_lower = c - half * width
    bins: list[Bin] = []
    bins.append(Bin(None, first_lower - 1))
    for i in range(n_central):
        lo = first_lower + i * width
        bins.append(Bin(lo, lo + width - 1))
    bins.append(Bin(first_lower + n_central * width, None))
    return bins


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def prob_in_bin_gaussian(mu: float, sigma: float, b: Bin) -> float:
    """P(bin) sous N(mu, sigma²) avec correction d'arrondi entier ±0.5 °F.

    Le CLI imprime un entier : l'observation continue x tombe dans le bin
    [lo, hi] si lo - 0.5 ≤ x < hi + 0.5. Même convention que
    src/predictors/ensemble.py.
    """
    if sigma <= 0:
        return 1.0 if b.contains(mu) else 0.0
    lo = (b.lower - 0.5) if b.lower is not None else None
    hi = (b.upper + 0.5) if b.upper is not None else None
    p_lo = _normal_cdf((lo - mu) / sigma) if lo is not None else 0.0
    p_hi = _normal_cdf((hi - mu) / sigma) if hi is not None else 1.0
    return max(0.0, min(1.0, p_hi - p_lo))


def brier(p: float, outcome: bool) -> float:
    return (p - (1.0 if outcome else 0.0)) ** 2


def prob_in_bin_members(values: list[float], b: Bin) -> float:
    """P(bin) = part des membres dont le chiffre arrondi tombe dans le bin.

    Même arrondi que le CLI (`Bin.contains` : entier le plus proche).
    Aucune cloche. Liste vide → 0, rien d'inventé.
    """
    if not values:
        return 0.0
    n = 0
    for x in values:
        if b.contains(x):
            n += 1
    return n / len(values)


def prob_in_bin_members_models(per_model: dict[str, list[float]], b: Bin) -> float:
    """Moyenne des fractions, un poids égal par modèle (pas par membre).

    IFS 51 ne noie pas GEFS 31. Un modèle sans membre est ignoré.
    """
    parts = [prob_in_bin_members(vs, b) for vs in per_model.values() if vs]
    if not parts:
        return 0.0
    return sum(parts) / len(parts)


def prob_in_bin_mixture(values: list[float], sigma: float, b: Bin) -> float:
    """P(bin) sous un mélange équipondéré de N(v_i, sigma²).

    Une seule densité continue (somme des cloches), puis découpe du bin.
    Liste vide → 0, rien d'inventé. Même correction d'arrondi que
    `prob_in_bin_gaussian`.
    """
    if not values:
        return 0.0
    return sum(prob_in_bin_gaussian(v, sigma, b) for v in values) / len(values)


BLEND_HORIZON_DAYS = 8.0


def horizon_blend(p_forecast: float, p_climato: float, days_ahead: int,
                  tau: float = BLEND_HORIZON_DAYS) -> float:
    """Mélange par horizon : même formule que `EnsemblePredictor.predict`.

    w = exp(-days_ahead / 8). À J+0, w = 1 (courbe seule). À J+8, w ≈ 0,37.
    Le climat ici est une fréquence par bin, pas une courbe.
    """
    w = math.exp(-float(days_ahead) / tau)
    return w * p_forecast + (1.0 - w) * p_climato
