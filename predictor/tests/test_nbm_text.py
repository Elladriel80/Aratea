"""Tests hors ligne du parseur NBM et de P(bin) par interpolation.

Aucun réseau : bulletin KNYC réel du 1er septembre 2026 13 UTC, plus
quelques cas construits pour l'interpolation. On vérifie aussi qu'une
case vide ou -99 ne devient pas un chiffre inventé.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from src.forecast.nbm_prob import (
    cdf_from_percentiles, prob_in_bin_nbm, prob_in_bin_percentiles,
)
from src.forecast.nbm_text import NbmDaily, parse_bulletin
from src.truth.synthetic_bins import Bin, kalshi_style_bins

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "nbm_knyc_nbp.txt"


def test_parse_knyc_nbp_maps_max_min_and_percentiles():
    text = FIXTURE.read_text(encoding="utf-8")
    rows = parse_bulletin(text, ["KNYC"])
    assert rows
    assert {r.variable for r in rows} == {"temp_max", "temp_min"}
    assert all(r.station == "KNYC" and r.product == "NBP" for r in rows)
    issued = datetime(2026, 9, 1, 13, tzinfo=timezone.utc)
    assert all(r.issued == issued for r in rows)

    mins = {r.target: r for r in rows if r.variable == "temp_min"}
    maxs = {r.target: r for r in rows if r.variable == "temp_max"}
    # Premier min : 12 UTC le 2 septembre (FHR 23) → jour CLI 2026-09-02
    m = mins[date(2026, 9, 2)]
    assert m.lead == 1 and m.mean_f == 68 and m.p10 == 66 and m.p90 == 70
    # Premier max : 00 UTC le 3 septembre (FHR 35) → jour CLI 2026-09-02
    x = maxs[date(2026, 9, 2)]
    assert x.lead == 1 and x.mean_f == 75 and x.p50 == 76 and x.p90 == 78
    assert date(2026, 9, 10) in maxs
    assert maxs[date(2026, 9, 10)].p50 == 77


def test_parse_skips_other_stations_and_missing_minus99():
    text = FIXTURE.read_text(encoding="utf-8")
    assert parse_bulletin(text, ["KPHX"]) == []
    bogus = (
        "KNYC    NBM V5.0 NBP GUIDANCE    9/01/2026  1300 UTC\n"
        " UTC    12| 00\n"
        " FHR    23| 35\n"
        " TXNMN  68|-99\n"
        " TXNP5 -99| 76\n"
    )
    rows = parse_bulletin(bogus, ["KNYC"])
    mins = [r for r in rows if r.variable == "temp_min"]
    maxs = [r for r in rows if r.variable == "temp_max"]
    # -99 reste une absence. Une colonne entièrement vide n'est pas créée.
    assert mins[0].mean_f == 68 and mins[0].p50 is None
    assert maxs[0].mean_f is None and maxs[0].p50 == 76


def test_cdf_interpolation_and_bin_probability():
    pts = [(70.0, 0.10), (72.0, 0.25), (76.0, 0.50), (80.0, 0.75), (82.0, 0.90)]
    assert cdf_from_percentiles(76.0, pts) == pytest.approx(0.50)
    assert cdf_from_percentiles(72.0, pts) == pytest.approx(0.25)
    # Entre 72 et 76 : 73.5 → 0.25 + 0.375 * 0.25 = 0.34375
    assert cdf_from_percentiles(73.5, pts) == pytest.approx(0.34375)
    # Bin 74–75 : F(75.5) − F(73.5) = 0.46875 − 0.34375
    p = prob_in_bin_percentiles(pts, Bin(74, 75))
    assert p == pytest.approx(0.125)
    # Queue haute : au-delà de 90 %
    assert 0.90 < cdf_from_percentiles(83.0, pts) <= 1.0
    assert cdf_from_percentiles(100.0, pts) == 1.0
    assert cdf_from_percentiles(-20.0, pts) == 0.0


def test_identical_percentiles_are_a_point_mass():
    pts = [(76.0, 0.10), (76.0, 0.50), (76.0, 0.90)]
    assert cdf_from_percentiles(75.4, pts) == 0.0
    assert cdf_from_percentiles(76.0, pts) == 1.0
    fc = NbmDaily(
        station="KNYC", product="NBP",
        issued=datetime(2026, 9, 1, 13, tzinfo=timezone.utc),
        target=date(2026, 9, 2), variable="temp_max", lead=1, fhr=35,
        p10=76, p25=76, p50=76, p75=76, p90=76,
    )
    assert prob_in_bin_nbm(fc, Bin(76, 77)) == 1.0
    assert prob_in_bin_nbm(fc, Bin(74, 75)) == 0.0


def test_gaussian_fallback_when_percentiles_absent():
    fc = NbmDaily(
        station="KNYC", product="NBE",
        issued=datetime(2026, 9, 1, 13, tzinfo=timezone.utc),
        target=date(2026, 9, 2), variable="temp_max", lead=1, fhr=35,
        mean_f=80.0, sd_f=2.0,
    )
    p = prob_in_bin_nbm(fc, Bin(80, 81))
    assert p is not None and 0.2 < p < 0.6
    empty = NbmDaily(
        station="KNYC", product="NBP",
        issued=datetime(2026, 9, 1, 13, tzinfo=timezone.utc),
        target=date(2026, 9, 2), variable="temp_max", lead=1, fhr=35,
    )
    assert prob_in_bin_nbm(empty, Bin(80, 81)) is None


def test_synthetic_bins_around_nbm_median_sum_near_one():
    text = FIXTURE.read_text(encoding="utf-8")
    fc = next(r for r in parse_bulletin(text, ["KNYC"])
              if r.variable == "temp_max" and r.target == date(2026, 9, 2))
    bins = kalshi_style_bins(fc.center_f(), n_central=6)
    total = sum(prob_in_bin_nbm(fc, b) or 0.0 for b in bins)
    assert 0.98 <= total <= 1.02
