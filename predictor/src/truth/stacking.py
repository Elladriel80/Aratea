"""Stacking modèle + marché : le prix est le prior, on n'apprend que le reste.

FR : B3. kalshi_mid est un meilleur estimateur que notre mélange. On le
prend comme point de départ et on apprend un seul nombre w :

    P_stack = prix + w · (modèle − prix)

w est l'ajustement des moindres carrés de (vérité − prix) sur
(modèle − prix), sans intercept : on ne recalibre pas le marché, on
apprend seulement le résidu. w = 0 → on garde le prix. w = 1 → on
garde le modèle.

Aucun prix n'est inventé ici. Les probabilités marché doivent venir
d'une capture réelle (yes_mid) ou du carnet papier.

EN : Residual stack on a real market mid. One-parameter OLS, no intercept.
"""
from __future__ import annotations

from typing import Iterable, Optional, Sequence


EPS = 1e-6
# Un seul nombre : 50 paires minimum pour ne pas ajuster le bruit.
MIN_TRAIN_STACK = 50


def clip_prob(p: float, eps: float = EPS) -> float:
    return min(1.0 - eps, max(eps, float(p)))


def residual_weight(
    p_model: Sequence[float],
    p_market: Sequence[float],
    y: Sequence[float],
) -> Optional[float]:
    """w = Σ (y − marché)(modèle − marché) / Σ (modèle − marché)².

    None s'il n'y a pas assez de lignes ou si le modèle colle au prix.
    """
    n = len(y)
    if n < MIN_TRAIN_STACK or n != len(p_model) or n != len(p_market):
        return None
    num = 0.0
    den = 0.0
    for m, k, yi in zip(p_model, p_market, y):
        r = float(m) - float(k)
        num += (float(yi) - float(k)) * r
        den += r * r
    if den < 1e-12:
        return 0.0
    return num / den


def apply_stack(p_market: float, p_model: float, weight: float) -> float:
    return clip_prob(float(p_market) + float(weight) * (float(p_model) - float(p_market)))


def ece(probs: Sequence[float], y: Sequence[float], n_bins: int = 10) -> Optional[float]:
    """Erreur de calibration (ECE) : écart |chance moyenne − fréquence| par tranche.

    Tranches égales sur [0, 1]. None si la liste est vide.
    """
    n = len(y)
    if n == 0 or n != len(probs):
        return None
    if n_bins < 2:
        n_bins = 2
    totals = [0] * n_bins
    sum_p = [0.0] * n_bins
    sum_y = [0.0] * n_bins
    for p, yi in zip(probs, y):
        p = min(1.0, max(0.0, float(p)))
        i = min(n_bins - 1, int(p * n_bins))
        totals[i] += 1
        sum_p[i] += p
        sum_y[i] += float(yi)
    acc = 0.0
    for i in range(n_bins):
        if totals[i] == 0:
            continue
        conf = sum_p[i] / totals[i]
        freq = sum_y[i] / totals[i]
        acc += totals[i] * abs(freq - conf)
    return acc / n


def mae(probs: Sequence[float], y: Sequence[float]) -> Optional[float]:
    n = len(y)
    if n == 0 or n != len(probs):
        return None
    return sum(abs(float(p) - float(yi)) for p, yi in zip(probs, y)) / n


def disagreement_count(
    p_model: Iterable[float],
    p_market: Iterable[float],
    threshold: float,
) -> tuple[int, int]:
    """(n_vrai_désaccord, n_total) où |modèle − prix| > seuil."""
    n_real = 0
    n = 0
    for m, k in zip(p_model, p_market):
        n += 1
        if abs(float(m) - float(k)) > threshold:
            n_real += 1
    return n_real, n


def brier_mean(probs: Sequence[float], y: Sequence[float]) -> Optional[float]:
    n = len(y)
    if n == 0 or n != len(probs):
        return None
    return sum((float(p) - float(yi)) ** 2 for p, yi in zip(probs, y)) / n
