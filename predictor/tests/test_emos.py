"""EMOS : CRPS gaussien, saison, ajustement à 4 nombres. Hors réseau."""
from __future__ import annotations

import math
from datetime import date, timedelta

from src.truth.emos import (
    MIN_TRAIN_EMOS, Emos, crps_gaussian, ensemble_variance, fit_emos_group,
    meteo_season,
)
from src.truth.iem_cli import CliDay
from src.truth.skill import ForecastPoint


def test_meteo_season_buckets():
    assert meteo_season(date(2026, 1, 15)) == "DJF"
    assert meteo_season(date(2026, 5, 20)) == "MAM"
    assert meteo_season(date(2026, 8, 3)) == "JJA"
    assert meteo_season(date(2026, 9, 1)) == "SON"


def test_crps_standard_normal_at_mean():
    # CRPS(N(0,1), 0) = √(2/π) − 1/√π = (√2 − 1)/√π
    expected = (math.sqrt(2.0) - 1.0) / math.sqrt(math.pi)
    assert abs(crps_gaussian(0.0, 1.0, 0.0) - expected) < 1e-12


def test_crps_degenerate_is_absolute_error():
    assert crps_gaussian(10.0, 0.0, 13.0) == 3.0


def test_crps_grows_when_observation_leaves_the_center():
    assert crps_gaussian(70.0, 2.0, 80.0) > crps_gaussian(70.0, 2.0, 71.0)


def test_ensemble_variance_matches_population():
    assert abs(ensemble_variance({"a": 1.0, "b": 3.0}) - 1.0) < 1e-12
    assert ensemble_variance({"a": 5.0}) == 0.0


def test_fit_emos_recovers_shift_and_scale():
    # y = 2 + 1.0 * mean + petit bruit ; variance des modèles ≈ 1
    means, variances, obs = [], [], []
    for i in range(40):
        m = 70.0 + (i % 8)
        means.append(m)
        variances.append(1.0)
        obs.append(2.0 + m + (0.2 if i % 2 == 0 else -0.2))
    p = fit_emos_group(means, variances, obs, season="JJA")
    assert p is not None and p.n_train == 40
    # a et b bougent ensemble (moyennes autour de 70 °F). Ce qui compte :
    # la prévision corrigée, pas chaque nombre isolé.
    for m in (70.0, 74.0, 77.0):
        mu, sig = p.apply(m, 1.0)
        assert abs(mu - (2.0 + m)) < 0.6
        assert sig >= 1.0


def test_fit_emos_refuses_short_groups():
    means = [70.0] * (MIN_TRAIN_EMOS - 1)
    variances = [1.0] * (MIN_TRAIN_EMOS - 1)
    obs = [72.0] * (MIN_TRAIN_EMOS - 1)
    assert fit_emos_group(means, variances, obs, season="JJA") is None


def _truth(station, start, n, high):
    return [CliDay(station, start + timedelta(days=i), high, 50, None, None,
                   0.0, False, 0.0, False, None) for i in range(n)]


def test_emos_fit_apply_seasonal_and_pooled_fallback():
    station, var = "KTST", "temp_max"
    # TRAIN : 40 jours de juin (JJA), assez pour saison et pour le repli.
    start = date(2026, 6, 1)
    truth = _truth(station, start, 50, 80)
    truth_by = {(d.station, d.valid): d for d in truth}
    points = [
        ForecastPoint(station, var, d.valid, 1,
                      {"m1": 77.4, "m2": 76.6})
        for d in truth
    ]
    train = [p for p in points if p.target < date(2026, 7, 11)]
    assert len(train) == 40
    emos = Emos().fit(train, truth_by)
    assert (station, var, 1, "JJA") in emos.seasonal
    assert (station, var, 1) in emos.pooled
    # Un jour JJA du test utilise la table saison.
    mid = ForecastPoint(station, var, date(2026, 7, 20), 1, {"m1": 77.4, "m2": 76.6})
    got = emos.apply(mid)
    assert got is not None
    mu, _sig, params = got
    assert abs(mu - 80.0) < 1.5
    assert params.fallback is False
    # Septembre : pas de SON dans TRAIN → repli sans saison.
    son = ForecastPoint(station, var, date(2026, 9, 2), 1, {"m1": 77.4, "m2": 76.6})
    got_son = emos.apply(son)
    assert got_son is not None and got_son[2].fallback is True
    # Hiver : ni saison ni (si on retire le repli) — le repli pooled existe.
    djf = ForecastPoint(station, var, date(2026, 1, 10), 1, {"m1": 77.4, "m2": 76.6})
    assert emos.apply(djf) is not None
