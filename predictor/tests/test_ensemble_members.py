"""Client Ensemble API (parsing des membres) + EnsembleMembersPredictor, hors ligne."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone

import pytest

from src.predictors.base import ContractSpec
from src.predictors.ensemble_members import EnsembleMembersPredictor
from src.weather.ensemble_api import EnsembleMembersClient, MemberSeries, parse_members


def test_parse_members_single_and_multi_model_key_layouts():
    d = {"hourly": {"time": ["t0", "t1"],
                    "temperature_2m": [70.0, 71.0],                     # contrôle
                    "temperature_2m_member01": [72.0, 73.0],
                    "temperature_2m_member12_gfs025": [69.0, 68.0],     # suffixe modèle
                    "temperature_2m_member03_ecmwf_ifs025": [99.0, 99.0],  # autre modèle : ignoré
                    "precipitation_member01": [0.0, 0.0]}}
    ms = parse_members(d, "temperature_2m", "gfs025")
    assert [(m.member, m.values[0]) for m in ms] == [(0, 70.0), (1, 72.0), (12, 69.0)]
    assert parse_members({}, "temperature_2m", "gfs025") == []


def _hourly(start_utc: datetime, values):
    return [(start_utc + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(len(values))], values


class _FakeMembers:
    """Deux modèles ; membres centrés sur `center` avec dispersion ±spread."""
    def __init__(self, target: date, center: float, spread: float, n=(51, 31)):
        self.target, self.center, self.spread, self.n = target, center, spread, n
        self.failures = {}

    def fetch(self, lat, lon, days=7, variable="temperature_2m"):
        start = datetime(self.target.year, self.target.month, self.target.day, 5, tzinfo=timezone.utc)  # 00:00 EST
        out = {}
        for model, n in zip(("ecmwf_ifs025", "gfs025"), self.n):
            members = []
            for k in range(n):
                peak = self.center + self.spread * (2 * k / max(1, n - 1) - 1)
                vals = [peak - 10.0] * 24
                vals[14] = peak                       # pic à 14 h locale
                times, values = _hourly(start, vals)
                members.append(MemberSeries(model, k, times, values))
            out[model] = members
        return out


def _contract(target, lo, hi):
    return ContractSpec("KXHIGHTNYC-T", "KXHIGHTNYC", "temp_max", "NYC", target, lo, hi, f"{lo}° to {hi}°")


def test_predictor_probabilities_partition_and_follow_members(monkeypatch):
    monkeypatch.delenv("ARATEA_ENS_STATION_BIAS", raising=False)
    target = date.today() + timedelta(days=1)
    pred = EnsembleMembersPredictor(members_client=_FakeMembers(target, 76.0, 3.0), kernel_f=1.0)
    p_center = pred.predict(_contract(target, 76, 77))
    p_far = pred.predict(_contract(target, 90, 91))
    assert p_center.method == "ensemble_members"
    assert p_center.inputs["n_members"] == 82
    assert p_center.inputs["n_members_per_model"] == {"ecmwf_ifs025": 51, "gfs025": 31}
    assert 0.2 < p_center.prob_yes < 0.6 and p_far.prob_yes < 0.01
    assert abs(p_center.inputs["member_mean"] - 76.0) < 0.2
    # partition : la somme sur une échelle de bins couvrant tout vaut 1
    bins = [(lo, lo + 1) for lo in range(60, 92, 2)]
    total = sum(pred.predict(_contract(target, lo, hi)).prob_yes for lo, hi in bins)
    assert abs(total - 1.0) < 1e-6


def test_predictor_applies_station_bias_when_enabled(tmp_path, monkeypatch):
    target = date.today() + timedelta(days=1)
    rows = [{"station": "KNYC", "variable": "temp_max", "lead": 1, "bias_f": 4.0, "sigma_f": 2.0, "n_train": 80}]
    (tmp_path / "sb.json").write_text(json.dumps(rows), encoding="utf-8")
    monkeypatch.setenv("ARATEA_STATION_BIAS_PATH", str(tmp_path / "sb.json"))
    pred = EnsembleMembersPredictor(members_client=_FakeMembers(target, 76.0, 3.0), kernel_f=1.0, station_bias=True)
    p = pred.predict(_contract(target, 80, 81))
    assert p.inputs["station_bias"]["bias_f"] == 4.0
    assert p.prob_yes > p.inputs["p_raw"] + 0.2          # le bin 80-81 devient central après +4 °F


def test_predictor_falls_back_when_too_few_members(monkeypatch):
    monkeypatch.delenv("ARATEA_ENS_STATION_BIAS", raising=False)
    target = date.today() + timedelta(days=1)
    pred = EnsembleMembersPredictor(members_client=_FakeMembers(target, 76.0, 3.0, n=(3, 2)), kernel_f=1.0)
    p = pred.predict(_contract(target, 76, 77))
    assert p.method == "ensemble_members[no_data]" and p.inputs["reason"].startswith("too_few_members")


def test_client_isolates_model_failures(tmp_path, monkeypatch):
    import requests
    from src.weather import open_meteo

    def fake_get(self, base, params):
        if params["models"] == "bad_model":
            raise requests.HTTPError("400 bad model")
        return {"hourly": {"time": ["2026-09-10T00:00"], "temperature_2m": [70.0], "temperature_2m_member01": [71.0]}}

    monkeypatch.setattr(open_meteo.OpenMeteoClient, "_get", fake_get)
    c = EnsembleMembersClient(cache_dir=tmp_path, models=["gfs025", "bad_model"], sleep_s=0)
    out = c.fetch(40.0, -73.0, days=2)
    assert list(out) == ["gfs025"] and len(out["gfs025"]) == 2
    assert "bad_model" in c.failures
