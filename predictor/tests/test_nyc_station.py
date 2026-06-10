"""Revue 2026-06-10 A5 / finding E4 — NYC prédit à la station de résolution KNYC.

Avant : open_meteo prédisait sur JFK (40.6413, -73.7781), Kalshi résout à
Central Park (KNYC, 40.7794, -73.9692) — ~17 km, biais systématique côtier.
NYC doit pointer la même station que src/kalshi/resolution.py (CLINYC/KNYC).
"""
from __future__ import annotations

from src.weather.open_meteo import CITIES
from src.kalshi.resolution import NWS_STATIONS


def test_nyc_points_to_central_park_knyc():
    nyc = CITIES["NYC"]
    assert nyc["lat"] == 40.7794
    assert nyc["lon"] == -73.9692
    assert "KNYC" in nyc["label"]


def test_nyc_coords_match_resolution_station():
    nyc = CITIES["NYC"]
    knyc = NWS_STATIONS["CLINYC"]  # la station de résolution Kalshi pour NYC
    assert knyc.icao == "KNYC"
    assert nyc["lat"] == knyc.lat
    assert nyc["lon"] == knyc.lon


def test_nyc_is_no_longer_jfk():
    nyc = CITIES["NYC"]
    # Anciennes coordonnées JFK — ne doivent plus apparaître.
    assert (nyc["lat"], nyc["lon"]) != (40.6413, -73.7781)
    assert "JFK" not in nyc["label"]
