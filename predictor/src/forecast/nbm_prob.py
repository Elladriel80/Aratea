"""P(bin) à partir des seuils NBM / Probability in a bin from NBM percentiles.

FR : On relie les cinq seuils (10, 25, 50, 75, 90 %) par des segments
droits. En dessous de 10 % et au-dessus de 90 %, on prolonge le même
segment, puis on coupe entre 0 et 1. Pour un contrat « entre A et B »,
on prend la différence des deux bords, avec le même arrondi ±0,5 °F
que le reste du predictor.

Si les cinq seuils manquent, on utilise la moyenne et l'écart-type
imprimés (NBP TXNMN/TXNSD ou NBE TXN/XND) comme une cloche simple.
On n'invente aucun chiffre manquant.

EN : Piecewise-linear CDF through NBM percentiles; Gaussian fallback
from printed mean/sd only. Same ±0.5 °F rounding as synthetic_bins.
"""
from __future__ import annotations

from typing import Optional

from src.forecast.nbm_text import NbmDaily
from src.truth.synthetic_bins import Bin, prob_in_bin_gaussian


def cdf_from_percentiles(x: float, pts: list[tuple[float, float]]) -> float:
    """F(x) = P(T ≤ x) par interpolation des seuils, bornée à [0, 1]."""
    if not pts:
        raise ValueError("aucun seuil")
    # Seuils identiques : tout le poids est sur cette valeur.
    vals = [p[0] for p in pts]
    if max(vals) - min(vals) < 1e-9:
        return 0.0 if x < vals[0] else 1.0

    # Un seul point : on ne peut pas interpoler.
    if len(pts) == 1:
        v, p = pts[0]
        return 0.0 if x < v else (p if x == v else 1.0)

    anchors = _with_tails(pts)
    if x <= anchors[0][0]:
        return 0.0
    if x >= anchors[-1][0]:
        return 1.0
    for (x0, p0), (x1, p1) in zip(anchors, anchors[1:]):
        if x0 <= x <= x1:
            if x1 <= x0:
                return max(p0, p1)
            t = (x - x0) / (x1 - x0)
            return max(0.0, min(1.0, p0 + t * (p1 - p0)))
    return 1.0


def _with_tails(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Ajoute les bords F=0 et F=1 en prolongeant le premier et le dernier segment."""
    clean: list[tuple[float, float]] = []
    for v, p in pts:
        if clean and v < clean[-1][0]:
            continue                      # seuil qui recule : on l'ignore
        if clean and v == clean[-1][0]:
            clean[-1] = (v, max(clean[-1][1], p))
            continue
        clean.append((v, p))
    if len(clean) < 2:
        v, p = clean[0]
        return [(v - 1.0, 0.0), (v, p), (v + 1.0, 1.0)]

    (x0, p0), (x1, p1) = clean[0], clean[1]
    slope0 = (p1 - p0) / (x1 - x0) if x1 != x0 else 0.0
    left = x0 - (p0 / slope0) if slope0 > 1e-9 else x0 - 2.0

    (y0, q0), (y1, q1) = clean[-2], clean[-1]
    slope1 = (q1 - q0) / (y1 - y0) if y1 != y0 else 0.0
    right = y1 + ((1.0 - q1) / slope1) if slope1 > 1e-9 else y1 + 2.0

    return [(left, 0.0)] + clean + [(right, 1.0)]


def prob_in_bin_percentiles(pts: list[tuple[float, float]], b: Bin) -> float:
    """P(bin) sous la courbe des seuils, arrondi entier ±0,5 °F."""
    if not pts:
        raise ValueError("aucun seuil")
    lo = (b.lower - 0.5) if b.lower is not None else None
    hi = (b.upper + 0.5) if b.upper is not None else None
    p_lo = cdf_from_percentiles(lo, pts) if lo is not None else 0.0
    p_hi = cdf_from_percentiles(hi, pts) if hi is not None else 1.0
    return max(0.0, min(1.0, p_hi - p_lo))


def prob_in_bin_nbm(fc: NbmDaily, b: Bin) -> Optional[float]:
    """P(bin) NBM : seuils interpolés, sinon cloche moyenne/écart-type.

    Renvoie None si le bulletin n'a ni seuils ni moyenne : rien d'inventé.
    """
    pts = fc.percentiles()
    if len(pts) >= 2:
        return prob_in_bin_percentiles(pts, b)
    if len(pts) == 1:
        return 1.0 if b.contains(pts[0][0]) else 0.0
    if fc.mean_f is None:
        return None
    sigma = fc.sd_f if fc.sd_f is not None and fc.sd_f > 0 else 1.0
    return prob_in_bin_gaussian(fc.mean_f, sigma, b)
