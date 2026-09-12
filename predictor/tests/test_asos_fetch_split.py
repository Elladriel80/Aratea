"""Découpe d'un CSV IEM multi-stations. Hors réseau."""
from __future__ import annotations

from src.truth.asos import parse_iem_csv


def test_multi_station_csv_keeps_each_city_and_drops_missing():
    text = (
        "station,valid,tmpf\n"
        "NYC,2026-08-03 17:51,76.00\n"
        "LAX,2026-08-03 17:53,72.00\n"
        "NYC,2026-08-03 18:51,M\n"
    )
    free = parse_iem_csv(text)
    assert [(r.station, r.tmp_f) for r in free] == [("KNYC", 76.0), ("KLAX", 72.0)]
