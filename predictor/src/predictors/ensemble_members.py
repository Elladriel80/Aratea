"""EnsembleMembersPredictor — P(bin) depuis les vrais membres d'ensemble.

FR : Remplace l'approximation gaussienne sur 5 sorties déterministes par la
distribution empirique des membres (IFS 51, AIFS ENS 51, GEFS 31 par défaut,
~130 membres). Chaque membre est agrégé en extrême journalier dans la fenêtre
LST du CLI, décalé du biais station si la table est active (même flag
ARATEA_ENS_STATION_BIAS que l'ensemble déterministe), puis lissé par un noyau
gaussien de largeur `kernel_f` (défaut 1 °F : arrondi entier du CLI + un peu
de sous-dispersion). Les modèles pèsent autant les uns que les autres, quel
que soit leur nombre de membres.

P(bin) = Σ_modèles (1/M) Σ_membres (1/n_m) · P_N(x_i + biais, kernel)(bin)

Challenger : capturé chaque jour par forward_predict à côté de `ensemble`,
scoré par score_forward, comparé au marché par eval_station_bias_market. Ne
remplace pas le champion tant que le holdout ne l'a pas dit.

EN : Empirical member distribution (~130 members) in place of a 5-point
gaussian. Daily extremes in the CLI LST window per member, optional station
bias shift, gaussian kernel smoothing (default 1 °F), equal weight per model.
Shadow predictor captured daily and scored like the others.
"""
from __future__ import annotations

import math
import os
import statistics
from datetime import date
from typing import Optional

from src.truth.lst_window import daily_extreme_lst
from src.truth.synthetic_bins import Bin, prob_in_bin_gaussian
from src.weather import CITIES
from src.weather.ensemble_api import EnsembleMembersClient
from .base import ContractSpec, Prediction, Predictor
from .climatology import ClimatologyPredictor


class EnsembleMembersPredictor(Predictor):
    name = "ensemble_members"

    def __init__(
        self,
        weather_client=None,                       # ignoré : compat factory forward_predict
        members_client: Optional[EnsembleMembersClient] = None,
        kernel_f: Optional[float] = None,
        max_horizon_days: int = 14,
        station_bias: Optional[bool] = None,
        min_members: int = 10,
        climato: Optional[ClimatologyPredictor] = None,
    ):
        self.members = members_client or EnsembleMembersClient()
        self.kernel_f = float(os.environ.get("ARATEA_ENS_MEMBERS_KERNEL_F", "1.0")) if kernel_f is None else kernel_f
        self.max_horizon = max_horizon_days
        self.min_members = min_members
        # Fallback climatologique quand l'API ne répond pas (même contrat que ensemble.py).
        self.climato = climato or (ClimatologyPredictor(weather_client) if weather_client is not None else None)
        if station_bias is None:
            station_bias = os.environ.get("ARATEA_ENS_STATION_BIAS", "0").strip().lower() in ("1", "true", "on")
        self.station_bias_table = None
        if station_bias:
            from src.truth.station_bias_table import StationBiasTable
            self.station_bias_table = StationBiasTable()

    # -- helpers --

    def _fallback(self, contract: ContractSpec, reason: str) -> Prediction:
        if self.climato is not None:
            clim = self.climato.predict(contract)
            return Prediction(contract, clim.prob_yes, self.name + "[climato_only]",
                              {"reason": reason, **clim.inputs}, clim.confidence)
        return Prediction(contract, 0.5, self.name + "[no_data]", {"reason": reason}, 0.0)

    @staticmethod
    def _bin(contract: ContractSpec) -> Bin:
        lo = None if contract.lower is None else int(round(contract.lower))
        hi = None if contract.upper is None else int(round(contract.upper))
        return Bin(lo, hi)

    # -- API --

    def predict(self, contract: ContractSpec) -> Prediction:
        city = CITIES.get(contract.location_key)
        if city is None:
            raise KeyError(f"Ville non mappée: {contract.location_key}")
        if contract.variable not in ("temp_max", "temp_min"):
            return self._fallback(contract, f"variable_not_supported:{contract.variable}")

        days_ahead = (contract.target_date - date.today()).days
        if days_ahead < 0 or days_ahead > self.max_horizon:
            return self._fallback(contract, "out_of_horizon")

        try:
            by_model = self.members.fetch(city["lat"], city["lon"], days=min(16, days_ahead + 2))
        except Exception as e:  # noqa: BLE001 — jamais planter la capture quotidienne
            return self._fallback(contract, f"ensemble_api_error: {e}")

        kind = "max" if contract.variable == "temp_max" else "min"
        per_model_values: dict[str, list[float]] = {}
        for model, members in by_model.items():
            vals = []
            for s in members:
                v = daily_extreme_lst(s.times_utc, s.values, city["tz"], contract.target_date, kind)
                if v is not None:
                    vals.append(v)
            if vals:
                per_model_values[model] = sorted(vals)
        n_total = sum(len(v) for v in per_model_values.values())
        if n_total < self.min_members:
            return self._fallback(contract, f"too_few_members:{n_total}")

        bias_applied = None
        shift = 0.0
        if self.station_bias_table is not None:
            sb = self.station_bias_table.lookup(contract.location_key, contract.variable, days_ahead)
            if sb is not None:
                shift = sb[0]
                bias_applied = {"bias_f": sb[0], "sigma_f": sb[1], "n_train": sb[2]}

        b = self._bin(contract)
        n_models = len(per_model_values)
        p_raw = p_corr = 0.0
        pooled: list[float] = []
        for model, vals in per_model_values.items():
            w = 1.0 / (n_models * len(vals))
            for x in vals:
                p_raw += w * prob_in_bin_gaussian(x, self.kernel_f, b)
                p_corr += w * prob_in_bin_gaussian(x + shift, self.kernel_f, b)
                pooled.append(x)
        prob = min(1.0, max(0.0, p_corr))
        pooled.sort()

        def q(p: float) -> float:
            return pooled[min(len(pooled) - 1, int(p * len(pooled)))]

        return Prediction(
            contract=contract,
            prob_yes=prob,
            method=self.name,
            inputs={
                "n_members": n_total,
                "n_members_per_model": {m: len(v) for m, v in per_model_values.items()},
                "member_values_per_model": {m: [round(x, 1) for x in v] for m, v in per_model_values.items()},
                "member_mean": statistics.fmean(pooled),
                "member_sd": statistics.pstdev(pooled) if len(pooled) > 1 else 0.0,
                "member_q10": q(0.10), "member_q50": q(0.50), "member_q90": q(0.90),
                "kernel_f": self.kernel_f,
                "p_raw": p_raw,
                "station_bias": bias_applied,
                "days_ahead": days_ahead,
                "api_failures": dict(self.members.failures),
            },
            confidence=min(1.0, n_total / 100.0),
        )
