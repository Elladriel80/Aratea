"""EnsembleMembersPredictor — P(bin) depuis les vrais membres d'ensemble.

FR : Part des membres dans chaque contrat de 2 °F (piste A3), pas une
cloche sur 5 modèles. Extrême journalier dans la fenêtre LST du CLI,
biais station si ARATEA_ENS_STATION_BIAS=1, un poids égal par modèle.
ARATEA_ENS_MEMBERS_P=kernel remet l'ancien lissage. Challenger seulement.

EN : Member fraction in each 2 °F bin (A3). Shadow predictor, not champion.
"""
from __future__ import annotations

import math
import os
import statistics
from datetime import date
from typing import Optional

from src.truth.lst_window import daily_extreme_lst
from src.truth.synthetic_bins import Bin, prob_in_bin_gaussian, prob_in_bin_members_models
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
        self.p_mode = os.environ.get("ARATEA_ENS_MEMBERS_P", "fraction").strip().lower()
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
        shifted = {m: [x + shift for x in vals] for m, vals in per_model_values.items()}
        p_frac_raw = prob_in_bin_members_models(per_model_values, b)
        p_frac_corr = prob_in_bin_members_models(shifted, b)
        n_models = len(per_model_values)
        p_kern_raw = p_kern_corr = 0.0
        pooled: list[float] = []
        for model, vals in per_model_values.items():
            w = 1.0 / (n_models * len(vals))
            for x in vals:
                p_kern_raw += w * prob_in_bin_gaussian(x, self.kernel_f, b)
                p_kern_corr += w * prob_in_bin_gaussian(x + shift, self.kernel_f, b)
                pooled.append(x)
        if self.p_mode == "kernel":
            p_raw, p_corr = p_kern_raw, p_kern_corr
        else:
            p_raw, p_corr = p_frac_raw, p_frac_corr
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
                "p_mode": self.p_mode,
                "p_raw": p_raw,
                "p_fraction": p_frac_corr,
                "p_kernel": p_kern_corr,
                "station_bias": bias_applied,
                "days_ahead": days_ahead,
                "api_failures": dict(self.members.failures),
            },
            confidence=min(1.0, n_total / 100.0),
        )
