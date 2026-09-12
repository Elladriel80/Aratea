"""Mesure A/B des règles de paiement Kalshi : fenêtre LST vs heure d'été,
et arrondi entier vs demi-degré.

FR : Ce module ne change pas le champion. Il compare deux façons de
fabriquer le max / min du jour, sur des lectures déjà là. Rien n'est
inventé : une heure absente reste absente.

EN : Settlement A/B only. No live-predictor change. Missing readings
stay missing.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable, Optional
from zoneinfo import ZoneInfo

from src.kalshi.resolution import apply_nws_rounding
from src.truth.asos import StationObs
from src.truth.iem_cli import STATION_TZ
from src.truth.lst_window import lst_date

# Un contrat Kalshi température du milieu fait 2 °F, bornes paires.
KALSHI_BIN_WIDTH = 2


def wall_date(utc_dt: datetime, tz_name: str) -> date:
    """Jour calendaire en heure murale locale (heure d'été si elle est en vigueur)."""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    return utc_dt.astimezone(ZoneInfo(tz_name)).date()


def dst_offset(utc_dt: datetime, tz_name: str) -> timedelta:
    """Décalage d'heure d'été à cet instant. Zéro hors DST (ex. Phoenix)."""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    local = utc_dt.astimezone(ZoneInfo(tz_name))
    return local.dst() or timedelta(0)


def observes_dst(tz_name: str, when: Optional[datetime] = None) -> bool:
    """Le fuseau a-t-il une heure d'été à cette date (midi UTC) ?"""
    when = when or datetime(2026, 7, 15, 12, tzinfo=timezone.utc)
    return dst_offset(when, tz_name) != timedelta(0)


def in_disputed_hour(utc_dt: datetime, tz_name: str) -> bool:
    """00:00-00:59 heure murale, seulement quand l'heure d'été est en vigueur.

    Cette heure-là est encore la veille en heure standard locale.
    """
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    if dst_offset(utc_dt, tz_name) == timedelta(0):
        return False
    local = utc_dt.astimezone(ZoneInfo(tz_name))
    return local.hour == 0


def nws_int(value: float) -> int:
    """Entier officiel NWS (half-up), celui qui paie Kalshi."""
    return int(apply_nws_rounding(float(value), "nearest_int"))


def nearest_half(value: float) -> float:
    """Demi-degré, même half-up que le NWS (75.25 → 75.5, 75.75 → 76.0)."""
    return math.floor(float(value) * 2.0 + 0.5) / 2.0


def even_bin(integer: int) -> tuple[int, int]:
    """Case Kalshi de 2 °F alignée sur un pair : 76 et 77 → (76, 77)."""
    lo = integer - (integer % KALSHI_BIN_WIDTH)
    return lo, lo + KALSHI_BIN_WIDTH - 1


def parse_cli_clock(raw: Optional[str]) -> Optional[tuple[int, int]]:
    """Heure imprimée du CLI ('420 PM', '1258 AM') → (heure 0-23, minute).

    'MM' et les chaînes illisibles → None. On n'invente pas l'heure.
    """
    if raw is None:
        return None
    s = str(raw).strip().upper().replace(":", "").replace(".", "")
    s = "".join(s.split())
    if not s:
        return None
    if s.endswith("AM"):
        ampm, digits = "AM", s[:-2]
    elif s.endswith("PM"):
        ampm, digits = "PM", s[:-2]
    else:
        return None
    if not digits.isdigit():
        return None
    if len(digits) <= 2:
        hour, minute = int(digits), 0
    elif len(digits) == 3:
        hour, minute = int(digits[0]), int(digits[1:])
    elif len(digits) == 4:
        hour, minute = int(digits[:2]), int(digits[2:])
    else:
        return None
    if hour < 0 or hour > 12 or minute > 59:
        return None
    if ampm == "AM":
        if hour == 12:
            hour = 0
    elif hour != 12:
        hour += 12
    if hour > 23:
        return None
    return hour, minute


def cli_time_is_disputed(raw: Optional[str], valid: date, tz_name: str) -> Optional[bool]:
    """L'heure imprimée tombe-t-elle dans 00:00-00:59 un jour d'heure d'été ?

    None si l'heure est illisible. On prend midi UTC du jour CLI pour
    savoir si l'heure d'été était en vigueur ce jour-là.
    """
    clock = parse_cli_clock(raw)
    if clock is None:
        return None
    noon = datetime(valid.year, valid.month, valid.day, 12, tzinfo=timezone.utc)
    if dst_offset(noon, tz_name) == timedelta(0):
        return False
    return clock[0] == 0


@dataclass
class DayAB:
    """Un jour comparable : les deux fenêtres ont assez de lectures."""
    station: str
    valid: date
    tz_name: str
    dst_that_day: bool
    n_obs_lst: int
    n_obs_wall: int
    max_lst: float
    max_wall: float
    min_lst: float
    min_wall: float
    max_lst_disputed: bool
    min_lst_disputed: bool

    @property
    def max_value_differs(self) -> bool:
        return abs(self.max_lst - self.max_wall) > 1e-9

    @property
    def min_value_differs(self) -> bool:
        return abs(self.min_lst - self.min_wall) > 1e-9

    @property
    def max_int_differs(self) -> bool:
        return nws_int(self.max_lst) != nws_int(self.max_wall)

    @property
    def min_int_differs(self) -> bool:
        return nws_int(self.min_lst) != nws_int(self.min_wall)

    @property
    def max_bin_differs(self) -> bool:
        return even_bin(nws_int(self.max_lst)) != even_bin(nws_int(self.max_wall))

    @property
    def min_bin_differs(self) -> bool:
        return even_bin(nws_int(self.min_lst)) != even_bin(nws_int(self.min_wall))


@dataclass
class RoundingRow:
    """Une valeur continue (ou demi-degré) face à l'entier officiel."""
    station: str
    valid: date
    variable: str                # "temp_max" | "temp_min"
    continuous_f: float
    source: str

    @property
    def official_int(self) -> int:
        return nws_int(self.continuous_f)

    @property
    def half_f(self) -> float:
        return nearest_half(self.continuous_f)

    @property
    def is_integer(self) -> bool:
        return abs(self.continuous_f - round(self.continuous_f)) < 1e-9

    @property
    def is_half_degree(self) -> bool:
        frac = abs(self.continuous_f - math.floor(self.continuous_f))
        return abs(frac - 0.5) < 1e-9

    @property
    def int_vs_floor_differs(self) -> bool:
        return self.official_int != int(math.floor(self.continuous_f))

    @property
    def int_vs_banker_differs(self) -> bool:
        return self.official_int != int(round(self.continuous_f))

    @property
    def int_vs_half_floor_differs(self) -> bool:
        return self.official_int != int(math.floor(self.half_f))

    @property
    def bin_vs_floor_differs(self) -> bool:
        return even_bin(self.official_int) != even_bin(int(math.floor(self.continuous_f)))

    @property
    def bin_vs_half_floor_differs(self) -> bool:
        return even_bin(self.official_int) != even_bin(int(math.floor(self.half_f)))

    @property
    def bin_vs_half_as_int_differs(self) -> bool:
        """Si on paie le demi-degré comme s'il était l'entier (76.5 ≠ 77)."""
        if self.is_integer:
            return False
        return even_bin(self.official_int) != even_bin(nws_int(self.half_f))

    @property
    def in_official_bin_raw(self) -> bool:
        """Case [lo, hi] sans élargir : lo ≤ x ≤ hi."""
        lo, hi = even_bin(self.official_int)
        return lo <= self.continuous_f <= hi

    @property
    def in_official_bin_pm05(self) -> bool:
        """Même fenêtre que synthetic_bins / ensemble : lo-0.5 ≤ x < hi+0.5."""
        lo, hi = even_bin(self.official_int)
        return (lo - 0.5) <= self.continuous_f < (hi + 0.5)

    @property
    def pm05_changes_membership(self) -> bool:
        """L'élargissement ±0.5 °F est-il ce qui place x dans la case payée ?"""
        return self.in_official_bin_pm05 and not self.in_official_bin_raw


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def aggregate_windows(
    obs: Iterable[StationObs],
    tz_name: str,
    min_obs: int = 18,
) -> list[DayAB]:
    """Pour chaque jour, max/min en LST et en heure murale.

    Un jour n'est gardé que si les deux fenêtres ont au moins `min_obs`
    lectures. On n'invente aucune température manquante.
    """
    lst_vals: dict[date, list[tuple[datetime, float]]] = {}
    wall_vals: dict[date, list[tuple[datetime, float]]] = {}
    for o in obs:
        valid = _as_utc(o.valid)
        lst_vals.setdefault(lst_date(valid, tz_name), []).append((valid, o.tmp_f))
        wall_vals.setdefault(wall_date(valid, tz_name), []).append((valid, o.tmp_f))

    days = sorted(set(lst_vals) & set(wall_vals))
    out: list[DayAB] = []
    for d in days:
        lv = lst_vals[d]
        wv = wall_vals[d]
        if len(lv) < min_obs or len(wv) < min_obs:
            continue
        max_l = max(v for _, v in lv)
        min_l = min(v for _, v in lv)
        max_w = max(v for _, v in wv)
        min_w = min(v for _, v in wv)
        noon = datetime(d.year, d.month, d.day, 12, tzinfo=timezone.utc)
        out.append(DayAB(
            station="",
            valid=d,
            tz_name=tz_name,
            dst_that_day=observes_dst(tz_name, noon),
            n_obs_lst=len(lv),
            n_obs_wall=len(wv),
            max_lst=max_l,
            max_wall=max_w,
            min_lst=min_l,
            min_wall=min_w,
            max_lst_disputed=any(
                abs(v - max_l) < 1e-9 and in_disputed_hour(t, tz_name) for t, v in lv
            ),
            min_lst_disputed=any(
                abs(v - min_l) < 1e-9 and in_disputed_hour(t, tz_name) for t, v in lv
            ),
        ))
    return out


def aggregate_station_days(
    obs: Iterable[StationObs],
    tz_lookup: Optional[dict[str, str]] = None,
    min_obs: int = 18,
) -> list[DayAB]:
    """Agrège toutes les stations. `tz_lookup` défaut : STATION_TZ."""
    tz_lookup = tz_lookup or STATION_TZ
    by_st: dict[str, list[StationObs]] = {}
    for o in obs:
        by_st.setdefault(o.station.upper(), []).append(o)
    rows: list[DayAB] = []
    for station, group in sorted(by_st.items()):
        tz_name = tz_lookup.get(station)
        if not tz_name:
            continue
        for row in aggregate_windows(group, tz_name, min_obs=min_obs):
            row.station = station
            rows.append(row)
    return rows


def rounding_from_values(
    rows: Iterable[tuple[str, date, str, float, str]],
) -> list[RoundingRow]:
    """(station, date, variable, continuous_f, source) → lignes d'arrondi."""
    out: list[RoundingRow] = []
    for station, valid, variable, value, source in rows:
        if value is None:
            continue
        out.append(RoundingRow(
            station=station, valid=valid, variable=variable,
            continuous_f=float(value), source=source,
        ))
    return out


def summarize_window(rows: list[DayAB]) -> dict:
    """Comptes uniquement. Aucun chiffre inventé : n=0 si la liste est vide."""
    n = len(rows)
    dst_rows = [r for r in rows if r.dst_that_day]
    std_rows = [r for r in rows if not r.dst_that_day]
    stations = sorted({r.station for r in rows})

    def _pack(subset: list[DayAB]) -> dict:
        m = len(subset)
        return {
            "n_days": m,
            "max_value_differs": sum(1 for r in subset if r.max_value_differs),
            "min_value_differs": sum(1 for r in subset if r.min_value_differs),
            "max_int_differs": sum(1 for r in subset if r.max_int_differs),
            "min_int_differs": sum(1 for r in subset if r.min_int_differs),
            "max_bin_differs": sum(1 for r in subset if r.max_bin_differs),
            "min_bin_differs": sum(1 for r in subset if r.min_bin_differs),
            "either_value_differs": sum(
                1 for r in subset if r.max_value_differs or r.min_value_differs
            ),
            "either_int_differs": sum(
                1 for r in subset if r.max_int_differs or r.min_int_differs
            ),
            "either_bin_differs": sum(
                1 for r in subset if r.max_bin_differs or r.min_bin_differs
            ),
            "max_diff_lst_extreme_in_disputed": sum(
                1 for r in subset if r.max_value_differs and r.max_lst_disputed
            ),
            "min_diff_lst_extreme_in_disputed": sum(
                1 for r in subset if r.min_value_differs and r.min_lst_disputed
            ),
        }

    by_station = {}
    for st in stations:
        sub = [r for r in rows if r.station == st]
        pack = _pack(sub)
        pack["city_tz"] = sub[0].tz_name if sub else None
        pack["n_dst_days"] = sum(1 for r in sub if r.dst_that_day)
        by_station[st] = pack

    dates = [r.valid for r in rows]
    return {
        "n_comparable_days": n,
        "n_stations": len(stations),
        "first": min(dates).isoformat() if dates else None,
        "last": max(dates).isoformat() if dates else None,
        "all": _pack(rows),
        "dst_days": _pack(dst_rows),
        "standard_days": _pack(std_rows),
        "by_station": by_station,
    }


def summarize_rounding(rows: list[RoundingRow]) -> dict:
    n = len(rows)
    dates = [r.valid for r in rows]
    stations = sorted({r.station for r in rows})

    def _pack(subset: list[RoundingRow]) -> dict:
        m = len(subset)
        return {
            "n": m,
            "already_integer": sum(1 for r in subset if r.is_integer),
            "exactly_half": sum(1 for r in subset if r.is_half_degree),
            "int_vs_floor": sum(1 for r in subset if r.int_vs_floor_differs),
            "int_vs_banker": sum(1 for r in subset if r.int_vs_banker_differs),
            "int_vs_half_floor": sum(1 for r in subset if r.int_vs_half_floor_differs),
            "bin_vs_floor": sum(1 for r in subset if r.bin_vs_floor_differs),
            "bin_vs_half_floor": sum(1 for r in subset if r.bin_vs_half_floor_differs),
            "bin_vs_half_as_int": sum(1 for r in subset if r.bin_vs_half_as_int_differs),
            "outside_raw_bin": sum(1 for r in subset if not r.in_official_bin_raw),
            "pm05_changes_membership": sum(
                1 for r in subset if r.pm05_changes_membership
            ),
        }

    by_station = {st: _pack([r for r in rows if r.station == st]) for st in stations}
    by_var = {}
    for var in ("temp_max", "temp_min"):
        by_var[var] = _pack([r for r in rows if r.variable == var])
    return {
        "n": n,
        "n_stations": len(stations),
        "first": min(dates).isoformat() if dates else None,
        "last": max(dates).isoformat() if dates else None,
        "all": _pack(rows),
        "by_variable": by_var,
        "by_station": by_station,
        "sources": sorted({r.source for r in rows}),
    }


def summarize_cli_times(records: Iterable[dict], tz_lookup: Optional[dict[str, str]] = None) -> dict:
    """Heures imprimées du CLI : combien tombent dans l'heure litigieuse.

    Ce n'est pas une preuve que la *valeur* du max change (égalité possible).
    On le dit dans le rapport. Heure illisible = compte à part, pas inventée.
    """
    tz_lookup = tz_lookup or STATION_TZ
    n = 0
    high_ok = low_ok = 0
    high_disputed = low_disputed = 0
    high_unreadable = low_unreadable = 0
    by_station: dict[str, dict] = {}
    first = last = None
    for rec in records:
        station = str(rec.get("station") or "").upper()
        tz_name = tz_lookup.get(station)
        valid_s = rec.get("valid")
        if not station or not tz_name or not valid_s:
            continue
        try:
            valid = date.fromisoformat(str(valid_s)[:10])
        except ValueError:
            continue
        n += 1
        first = valid if first is None or valid < first else first
        last = valid if last is None or valid > last else last
        slot = by_station.setdefault(station, {
            "n": 0, "high_ok": 0, "low_ok": 0,
            "high_disputed": 0, "low_disputed": 0,
            "high_unreadable": 0, "low_unreadable": 0,
        })
        slot["n"] += 1
        hd = cli_time_is_disputed(rec.get("high_time"), valid, tz_name)
        ld = cli_time_is_disputed(rec.get("low_time"), valid, tz_name)
        if hd is None:
            high_unreadable += 1
            slot["high_unreadable"] += 1
        else:
            high_ok += 1
            slot["high_ok"] += 1
            if hd:
                high_disputed += 1
                slot["high_disputed"] += 1
        if ld is None:
            low_unreadable += 1
            slot["low_unreadable"] += 1
        else:
            low_ok += 1
            slot["low_ok"] += 1
            if ld:
                low_disputed += 1
                slot["low_disputed"] += 1
    return {
        "n_cli_days": n,
        "first": first.isoformat() if first else None,
        "last": last.isoformat() if last else None,
        "high_readable": high_ok,
        "low_readable": low_ok,
        "high_unreadable": high_unreadable,
        "low_unreadable": low_unreadable,
        "high_disputed": high_disputed,
        "low_disputed": low_disputed,
        "by_station": by_station,
        "note": (
            "Heure officielle dans 00:00-00:59 heure murale un jour d'heure d'été. "
            "Ce n'est pas le compte des valeurs qui changent."
        ),
    }
