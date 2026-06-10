"""Convention unique de normalisation des probabilités du pipeline predictor.

Source de vérité partagée pour que le backtest, le simulateur et le run live
(daily_auto) scorent le MÊME modèle (revue 2026-06-10 A3 / finding E3).

Convention cible = celle du LIVE (daily_auto) : chaque bin est scoré de façon
INCONDITIONNELLE sur sa P(YES) brute. Il n'y a PAS de renormalisation
mutuellement exclusive inter-bins.

Pourquoi inconditionnel :
  - daily_auto.py (le modèle réellement déployé) prend la P(YES) brute de
    l'ensemble par bin et score YES/NO indépendamment. C'est ce modèle dont on
    veut mesurer le Brier.
  - L'ancien backtest renormalisait la P(YES) sur les seuls bins centraux
    ("between"), ce qui (a) changeait les chiffres vs live et (b) écrasait
    silencieusement la masse de probabilité des tails. Le Brier produit ne
    mesurait pas le modèle déployé — alors qu'il alimente la gate Phase B.
  - Si un appelant restreint le scoring aux bins centraux (le backtest et
    daily_auto excluent les tails "X ou moins"/"X ou plus" via
    strike_type != "between"), il doit scorer ces bins sur leur P(YES) BRUTE,
    inconditionnellement, et documenter l'exclusion des tails — surtout PAS
    renormaliser les survivants pour qu'ils somment à 1.
"""
from __future__ import annotations

from typing import Iterable, List


def normalize_event_probs(probs: Iterable[float]) -> List[float]:
    """Retourne les P(YES) par bin à scorer, selon la convention LIVE.

    Identité (scoring inconditionnel) : le modèle live score la P(YES) brute de
    chaque bin sans renormalisation inter-bins. Cette fonction existe pour que
    les trois pipelines (backtest, simulate, daily_auto) partagent UNE
    convention explicite et documentée plutôt que trois renormalisations inline
    divergentes. Entrée/sortie : liste de floats dans l'ordre d'entrée.
    """
    return [float(p) for p in probs]
