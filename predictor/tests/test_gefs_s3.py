"""Index GEFS et agrégation LST, hors ligne."""
from datetime import date, datetime, timezone

from src.forecast.gefs_s3 import (
    WindowSample, aggregate_from_records, member_number, needed_fhrs,
    window_overlaps_lst,
)
from src.forecast.grib_point import find_idx_row, nearest_index, parse_idx


IDX = """\
1:0:d=2026080300:VIS:surface:24 hour fcst:ENS=low-res ctl
10:3696947:d=2026080300:TMP:2 m above ground:24 hour fcst:ENS=low-res ctl
11:4129024:d=2026080300:DPT:2 m above ground:24 hour fcst:ENS=low-res ctl
13:5233410:d=2026080300:TMAX:2 m above ground:18-24 hour max fcst:ENS=low-res ctl
14:5660496:d=2026080300:TMIN:2 m above ground:18-24 hour min fcst:ENS=low-res ctl
15:6000000:d=2026080300:UGRD:10 m above ground:24 hour fcst:ENS=low-res ctl
"""


def test_parse_idx_finds_tmax_tmin():
    rows = parse_idx(IDX)
    tmax = find_idx_row(rows, "TMAX")
    tmin = find_idx_row(rows, "TMIN")
    assert tmax is not None and tmax["start"] == 5233410
    assert tmax["end"] == 5660495
    assert tmin is not None and tmin["start"] == 5660496


def test_nearest_index_nyc_on_gefs_grid():
    # Même grille que le fichier GEFS 0,25° (90N, 0E, pas 0,25).
    idx = nearest_index(40.7794, -73.9692, 90.0, 0.0, 0.25, 0.25, 1440, 721)
    assert idx == 197 * 1440 + 1144


def test_window_overlaps_lst_nyc_lead1():
    issued = datetime(2026, 8, 2, 0, tzinfo=timezone.utc)
    tz = "America/New_York"
    target = date(2026, 8, 3)
    assert window_overlaps_lst(issued, 36, tz, target)
    assert not window_overlaps_lst(issued, 12, tz, target)


def test_aggregate_needs_enough_windows():
    issued = datetime(2026, 8, 2, 0, tzinfo=timezone.utc)
    stations = {"KNYC": {"tz": "America/New_York"}}
    samples = [
        WindowSample(issued, 30, 0, "KNYC", "TMAX", 80.0),
        WindowSample(issued, 36, 0, "KNYC", "TMAX", 84.0),
        WindowSample(issued, 42, 0, "KNYC", "TMAX", 82.0),
        WindowSample(issued, 48, 0, "KNYC", "TMAX", 79.0),
    ]
    rows = aggregate_from_records(samples, stations, [1], min_windows=3)
    assert len(rows) == 1
    assert rows[0].value_f == 84.0 and rows[0].variable == "temp_max"
    assert aggregate_from_records(samples[:2], stations, [1], min_windows=3) == []


def test_grouped_extract_roundtrip():
    from src.forecast.gefs_s3 import GefsDaily, GefsS3Client
    issued = datetime(2026, 8, 2, 0, tzinfo=timezone.utc)
    rows = [
        GefsDaily("KNYC", "temp_max", date(2026, 8, 3), 1, issued, 0, 80.1, 4),
        GefsDaily("KNYC", "temp_max", date(2026, 8, 3), 1, issued, 1, 81.2, 4),
    ]
    client = GefsS3Client(cache_dir=__import__("pathlib").Path("/tmp/gefs-test-cache"),
                          extracted_path=__import__("pathlib").Path("/tmp/gefs-test-extract.json"))
    client.extracted_path.write_text("[]", encoding="utf-8")
    client.persist_extracted(rows)
    back = client.load_extracted()
    assert {(r.member, r.value_f) for r in back} == {(0, 80.1), (1, 81.2)}


def test_member_ids_and_needed_fhrs():
    assert member_number("gec00") == 0
    assert member_number("gep07") == 7
    fhrs = needed_fhrs([1])
    assert 30 in fhrs and 54 in fhrs
    assert all(h % 6 == 0 for h in fhrs)
