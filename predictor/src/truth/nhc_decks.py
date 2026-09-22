"""NHC a-decks / b-decks (ATCF) against HURDAT2 best-track.

FR : Archives publiques ftp.nhc.noaa.gov/atcf/archive. On garde OFCL
(prévision officielle) et OCD5 (climatologie-persistance déjà dans
l'a-deck). On n'invente pas de côte. Un a-deck commence après le
numérotage : la genèse n'est pas notable ici.

EN : Official NHC ATCF a-decks / b-decks vs HURDAT2. Catalogue name
« NHC a-decks / b-decks ».
"""
from __future__ import annotations

import gzip
import math
import re
import statistics
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Optional

import requests

from src.config import DATA_DIR, USER_AGENT
from src.truth.hurdat2_atl import HurdatStorm, is_major

CATALOGUE_DECKS = "NHC a-decks / b-decks"
ATCF_ARCHIVE = "https://ftp.nhc.noaa.gov/atcf/archive"
ATCF_README = f"{ATCF_ARCHIVE}/README"
ABDECK_DOC = "https://www.nrlmry.navy.mil/atcf_web/docs/database/new/abdeck.txt"
NHC_DECKS_CACHE = DATA_DIR / "truth" / "nhc_decks_cache"

# Standard NHC verification leads (hours).
LEADS = (12, 24, 36, 48, 72, 96, 120)
# Numbered storms only. Invest 90-99 and training 80-89 are skipped (README).
NUMBERED_RE = re.compile(r"^a(al)(\d{2})(\d{4})\.dat\.gz$", re.IGNORECASE)
BDECK_RE = re.compile(r"^b(al)(\d{2})(\d{4})\.dat\.gz$", re.IGNORECASE)
TROPICAL_OR_SUB = ("TD", "TS", "HU", "SD", "SS")
A_DECK_TECHS = ("OFCL", "OCD5")


def parse_atcf_lat(token: str) -> Optional[float]:
    token = token.strip()
    if not token:
        return None
    hemi = token[-1].upper()
    try:
        raw = int(token[:-1])
    except ValueError:
        return None
    value = raw / 10.0
    if hemi == "S":
        return -value
    if hemi == "N":
        return value
    return None


def parse_atcf_lon(token: str) -> Optional[float]:
    token = token.strip()
    if not token:
        return None
    hemi = token[-1].upper()
    try:
        raw = int(token[:-1])
    except ValueError:
        return None
    value = raw / 10.0
    if hemi == "W":
        return -value
    if hemi == "E":
        return value
    return None


def parse_atcf_int(token: str) -> Optional[int]:
    token = token.strip()
    if token == "":
        return None
    try:
        return int(token)
    except ValueError:
        return None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


@dataclass(frozen=True)
class AtcfLine:
    basin: str
    cyclone: str
    init: datetime
    tech: str
    tau: int
    lat: Optional[float]
    lon: Optional[float]
    vmax: Optional[int]
    ty: str
    storm_id: str

    @property
    def valid(self) -> datetime:
        return self.init + timedelta(hours=self.tau)


def parse_atcf_line(line: str, keep_techs: Optional[set[str]] = None) -> Optional[AtcfLine]:
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 9:
        return None
    basin = parts[0].upper()
    cyclone = parts[1].zfill(2)
    if len(parts[2]) < 10 or not parts[2][:10].isdigit():
        return None
    tech = parts[4].upper()
    if keep_techs is not None and tech not in keep_techs:
        return None
    tau = parse_atcf_int(parts[5])
    if tau is None:
        return None
    try:
        init = datetime.strptime(parts[2][:10], "%Y%m%d%H")
    except ValueError:
        return None
    year = init.year
    storm_id = f"{basin}{cyclone}{year}"
    ty = parts[10].upper() if len(parts) > 10 else ""
    return AtcfLine(
        basin=basin,
        cyclone=cyclone,
        init=init,
        tech=tech,
        tau=tau,
        lat=parse_atcf_lat(parts[6]),
        lon=parse_atcf_lon(parts[7]),
        vmax=parse_atcf_int(parts[8]),
        ty=ty,
        storm_id=storm_id,
    )


def parse_adeck_text(text: str, techs: tuple[str, ...] = A_DECK_TECHS) -> list[AtcfLine]:
    keep = set(t.upper() for t in techs)
    out: list[AtcfLine] = []
    for raw in text.splitlines():
        row = parse_atcf_line(raw, keep)
        if row is not None:
            out.append(row)
    return out


def parse_bdeck_text(text: str) -> list[AtcfLine]:
    return parse_adeck_text(text, techs=("BEST",))


def extract_techs_from_gzip(blob: bytes, techs: tuple[str, ...] = A_DECK_TECHS) -> str:
    """Keep only the requested tech lines. Full a-decks are huge."""
    text = gzip.decompress(blob).decode("utf-8", errors="replace")
    keep = set(t.upper() for t in techs)
    kept = []
    for raw in text.splitlines():
        parts = [p.strip() for p in raw.split(",")]
        if len(parts) > 4 and parts[4].upper() in keep:
            kept.append(raw)
    return "\n".join(kept) + ("\n" if kept else "")


def list_year_files(html: str, kind: str = "a") -> list[tuple[int, str, str]]:
    """Parse an NHC year listing. kind='a' or 'b'. Numbered Atlantic only."""
    rx = NUMBERED_RE if kind == "a" else BDECK_RE
    found = []
    for m in re.finditer(r'href="([^"]+\.dat\.gz)"', html, re.IGNORECASE):
        name = m.group(1).split("/")[-1]
        mm = rx.match(name)
        if not mm:
            continue
        num = int(mm.group(2))
        year = int(mm.group(3))
        if 1 <= num <= 30:
            found.append((num, name, f"{ATCF_ARCHIVE}/{year}/{name}"))
    found.sort()
    return found


class NhcDeckClient:
    def __init__(self, cache_dir: Path = NHC_DECKS_CACHE, timeout: int = 90):
        self.cache_dir = cache_dir
        self.timeout = timeout
    def _get(self, url: str) -> requests.Response:
        last: Optional[Exception] = None
        headers = {"User-Agent": USER_AGENT}
        for attempt in range(4):
            try:
                r = requests.get(url, timeout=self.timeout, headers=headers)
                r.raise_for_status()
                return r
            except requests.RequestException as exc:
                last = exc
                if attempt == 3:
                    break
                time.sleep(1.5 * (attempt + 1))
        assert last is not None
        raise last

    def year_listing(self, year: int, allow_network: bool = True) -> str:
        path = self.cache_dir / "listings" / f"{year}.html"
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
        if not allow_network:
            raise FileNotFoundError(f"NHC year listing cache missing: {path}")
        html = self._get(f"{ATCF_ARCHIVE}/{year}/").text
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        return html

    def fetch_extracted(
        self,
        year: int,
        name: str,
        url: str,
        techs: tuple[str, ...],
        allow_network: bool = True,
    ) -> str:
        dest = self.cache_dir / "extracted" / f"{name}.txt"
        if dest.exists():
            return dest.read_text(encoding="utf-8", errors="replace")
        if not allow_network:
            raise FileNotFoundError(f"NHC extracted cache missing: {dest}")
        blob = self._get(url).content
        text = extract_techs_from_gzip(blob, techs)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        return text

    def fetch_range(
        self,
        first_year: int,
        last_year: int,
        allow_network: bool = True,
    ) -> dict[str, Any]:
        """Atlantic numbered a-decks (OFCL/OCD5) and b-decks (BEST)."""
        adecks: dict[str, list[AtcfLine]] = {}
        bdecks: dict[str, list[AtcfLine]] = {}
        missing_a: list[str] = []
        missing_b: list[str] = []
        years_ok: list[int] = []
        for year in range(first_year, last_year + 1):
            try:
                html = self.year_listing(year, allow_network=allow_network)
            except (FileNotFoundError, requests.RequestException) as exc:
                missing_a.append(f"listing {year}: {exc}")
                continue
            a_files = list_year_files(html, "a")
            b_files = list_year_files(html, "b")
            if a_files:
                years_ok.append(year)
            print(
                f"  NHC {year}: {len(a_files)} a-decks, {len(b_files)} b-decks",
                flush=True,
            )
            jobs = (
                [(name, url, A_DECK_TECHS, "a") for _num, name, url in a_files]
                + [(name, url, ("BEST",), "b") for _num, name, url in b_files]
            )

            def _one(job: tuple[str, str, tuple[str, ...], str]) -> tuple[str, str, str]:
                name, url, techs, kind = job
                text = self.fetch_extracted(
                    year, name, url, techs, allow_network=allow_network
                )
                return kind, name, text

            if allow_network and len(jobs) > 1:
                with ThreadPoolExecutor(max_workers=4) as pool:
                    futs = [pool.submit(_one, job) for job in jobs]
                    results = []
                    for fut in as_completed(futs):
                        try:
                            results.append(fut.result())
                        except (FileNotFoundError, requests.RequestException) as exc:
                            results.append(("err", str(exc), ""))
            else:
                results = []
                for job in jobs:
                    try:
                        results.append(_one(job))
                    except (FileNotFoundError, requests.RequestException) as exc:
                        results.append(("err", str(exc), ""))
            for kind, name, text in results:
                if kind == "err":
                    missing_a.append(name)
                    continue
                if kind == "a":
                    lines = parse_adeck_text(text)
                    if lines:
                        adecks[lines[0].storm_id] = lines
                    else:
                        missing_a.append(f"{name}: no OFCL/OCD5 lines")
                else:
                    lines = parse_bdeck_text(text)
                    if lines:
                        bdecks[lines[0].storm_id] = lines
                    else:
                        missing_b.append(f"{name}: empty BEST")
        return {
            "first_year": first_year,
            "last_year": last_year,
            "years_with_adeck_listing": years_ok,
            "n_adeck_storms": len(adecks),
            "n_bdeck_storms": len(bdecks),
            "adecks": adecks,
            "bdecks": bdecks,
            "missing_a": missing_a,
            "missing_b": missing_b,
            "archive": ATCF_ARCHIVE,
            "readme": ATCF_README,
            "format": ABDECK_DOC,
        }


def _intensity_pairs(
    adecks: dict[str, list[AtcfLine]],
    storms: dict[str, HurdatStorm],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Homogeneous OFCL + OCD5 vs exact HURDAT2 time. No interpolation."""
    pairs = []
    skipped = CounterLike()
    for storm_id, lines in adecks.items():
        storm = storms.get(storm_id)
        if storm is None:
            skipped["no_hurdat2"] += 1
            continue
        by_key: dict[tuple[datetime, int], dict[str, AtcfLine]] = defaultdict(dict)
        for ln in lines:
            if ln.tau not in LEADS:
                continue
            by_key[(ln.init, ln.tau)][ln.tech] = ln
        for (init, tau), techs in by_key.items():
            ofcl = techs.get("OFCL")
            ocd5 = techs.get("OCD5")
            if ofcl is None or ocd5 is None:
                skipped["not_homogeneous"] += 1
                continue
            if ofcl.vmax is None or ofcl.vmax <= 0 or ocd5.vmax is None or ocd5.vmax <= 0:
                skipped["vmax_missing_or_zero"] += 1
                continue
            truth = storm.point_at(ofcl.valid)
            if truth is None:
                skipped["no_exact_hurdat2_time"] += 1
                continue
            if truth.wind_kt is None:
                skipped["hurdat2_wind_missing"] += 1
                continue
            if truth.status not in TROPICAL_OR_SUB:
                skipped["not_tropical_or_sub"] += 1
                continue
            pairs.append({
                "storm_id": storm_id,
                "year": storm.year,
                "init": init.isoformat(),
                "tau": tau,
                "valid": ofcl.valid.isoformat(),
                "ofcl_vmax": ofcl.vmax,
                "ocd5_vmax": ocd5.vmax,
                "hurdat2_vmax": truth.wind_kt,
                "hurdat2_status": truth.status,
                "ofcl_err": ofcl.vmax - truth.wind_kt,
                "ocd5_err": ocd5.vmax - truth.wind_kt,
                "ofcl_abs": abs(ofcl.vmax - truth.wind_kt),
                "ocd5_abs": abs(ocd5.vmax - truth.wind_kt),
                "ofcl_closer": abs(ofcl.vmax - truth.wind_kt) < abs(ocd5.vmax - truth.wind_kt),
                "tie": abs(ofcl.vmax - truth.wind_kt) == abs(ocd5.vmax - truth.wind_kt),
            })
    return pairs, skipped.as_dict()


class CounterLike:
    def __init__(self) -> None:
        self._c: dict[str, int] = defaultdict(int)

    def __getitem__(self, k: str) -> int:
        return self._c[k]

    def __setitem__(self, k: str, v: int) -> None:
        self._c[k] = v

    def as_dict(self) -> dict[str, int]:
        return dict(self._c)


def summarize_intensity(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    if not pairs:
        return {"n": 0, "by_lead": {}, "overall": None}
    by_lead: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for p in pairs:
        by_lead[p["tau"]].append(p)

    def pack(rows: list[dict[str, Any]]) -> dict[str, Any]:
        ofcl_abs = [r["ofcl_abs"] for r in rows]
        ocd5_abs = [r["ocd5_abs"] for r in rows]
        ofcl_err = [r["ofcl_err"] for r in rows]
        closer = sum(1 for r in rows if r["ofcl_closer"])
        tie = sum(1 for r in rows if r["tie"])
        return {
            "n": len(rows),
            "n_storms": len({r["storm_id"] for r in rows}),
            "n_seasons": len({r["year"] for r in rows}),
            "ofcl_mae_kt": statistics.fmean(ofcl_abs),
            "ocd5_mae_kt": statistics.fmean(ocd5_abs),
            "ofcl_bias_kt": statistics.fmean(ofcl_err),
            "ocd5_bias_kt": statistics.fmean([r["ocd5_err"] for r in rows]),
            "n_ofcl_closer": closer,
            "n_tie": tie,
            "n_ocd5_closer": len(rows) - closer - tie,
            "ofcl_beats_ocd5": statistics.fmean(ofcl_abs) < statistics.fmean(ocd5_abs),
        }

    return {
        "n": len(pairs),
        "n_storms": len({p["storm_id"] for p in pairs}),
        "n_seasons": len({p["year"] for p in pairs}),
        "first_year": min(p["year"] for p in pairs),
        "last_year": max(p["year"] for p in pairs),
        "overall": pack(pairs),
        "by_lead": {str(lead): pack(by_lead[lead]) for lead in LEADS if lead in by_lead},
    }


def _bdeck_vs_hurdat2(
    bdecks: dict[str, list[AtcfLine]],
    storms: dict[str, HurdatStorm],
) -> dict[str, Any]:
    """Operational BEST vs final HURDAT2 at the same time. Not a forecast."""
    abs_err = []
    n_match = 0
    n_storms = 0
    skipped = CounterLike()
    for storm_id, lines in bdecks.items():
        storm = storms.get(storm_id)
        if storm is None:
            skipped["no_hurdat2"] += 1
            continue
        used = False
        for ln in lines:
            if ln.tau != 0:
                continue
            if ln.vmax is None or ln.vmax <= 0:
                skipped["vmax_missing_or_zero"] += 1
                continue
            truth = storm.point_at(ln.valid)
            if truth is None or truth.wind_kt is None:
                skipped["no_exact_or_missing_wind"] += 1
                continue
            if truth.status not in TROPICAL_OR_SUB:
                skipped["not_tropical_or_sub"] += 1
                continue
            abs_err.append(abs(ln.vmax - truth.wind_kt))
            n_match += 1
            used = True
        if used:
            n_storms += 1
    return {
        "n_points": n_match,
        "n_storms": n_storms,
        "mae_kt": statistics.fmean(abs_err) if abs_err else None,
        "skipped": skipped.as_dict(),
        "note": (
            "b-deck BEST contre HURDAT2 au même instant. Ce n'est pas une "
            "prévision. C'est l'écart entre le best-track opérationnel et "
            "le fichier final."
        ),
    }


def first_hu_timing(
    adecks: dict[str, list[AtcfLine]],
    storms: dict[str, HurdatStorm],
) -> dict[str, Any]:
    """First HURDAT2 HU time vs first OFCL vmax>=64. Not genesis."""
    n_hu = 0
    n_ofcl_before = 0
    n_ofcl_at_or_after = 0
    n_no_ofcl_hu = 0
    n_adeck_starts_after_first_point = 0
    n_compared = 0
    adeck_years = {int(sid[-4:]) for sid in adecks}
    for storm_id, storm in storms.items():
        if adeck_years and storm.year not in adeck_years:
            continue
        first_hu = storm.first_status_dt("HU")
        if first_hu is None:
            continue
        n_hu += 1
        lines = adecks.get(storm_id)
        if not lines:
            n_no_ofcl_hu += 1
            continue
        ofcl = [ln for ln in lines if ln.tech == "OFCL"]
        if not ofcl:
            n_no_ofcl_hu += 1
            continue
        first_adeck = min(ln.init for ln in ofcl)
        if storm.points and first_adeck > storm.points[0].dt:
            n_adeck_starts_after_first_point += 1
        first_ofcl_hu = None
        for ln in ofcl:
            if ln.tau in LEADS and ln.vmax is not None and ln.vmax >= 64:
                if first_ofcl_hu is None or ln.init < first_ofcl_hu:
                    first_ofcl_hu = ln.init
        n_compared += 1
        if first_ofcl_hu is None:
            n_no_ofcl_hu += 1
        elif first_ofcl_hu < first_hu:
            n_ofcl_before += 1
        else:
            n_ofcl_at_or_after += 1
    return {
        "n_hurdat2_reached_hu": n_hu,
        "n_with_adeck_compared": n_compared,
        "n_ofcl_hu_forecast_before_first_hu": n_ofcl_before,
        "n_ofcl_hu_forecast_at_or_after_first_hu": n_ofcl_at_or_after,
        "n_no_ofcl_hu_forecast": n_no_ofcl_hu,
        "n_adeck_starts_after_first_hurdat2_point": n_adeck_starts_after_first_point,
        "genesis_scored": False,
        "genesis_block_reason": (
            "Les a-decks commencent quand le système est déjà numéroté. "
            "Ce n'est pas une prévision de formation. On ne l'invente pas."
        ),
    }


def landfall_track_error(
    adecks: dict[str, list[AtcfLine]],
    storms: dict[str, HurdatStorm],
) -> dict[str, Any]:
    """OFCL position vs HURDAT2 L point at the exact L time. No coastline."""
    errors = []
    skipped = CounterLike()
    adeck_years = {int(sid[-4:]) for sid in adecks}
    for storm in storms.values():
        if adeck_years and storm.year not in adeck_years:
            continue
        lpts = [p for p in storm.landfall_points if p.status == "HU"]
        if not lpts:
            continue
        lines = adecks.get(storm.storm_id)
        if not lines:
            skipped["no_adeck"] += 1
            continue
        ofcl = [ln for ln in lines if ln.tech == "OFCL" and ln.tau in LEADS]
        for lp in lpts:
            if lp.lat is None or lp.lon is None:
                skipped["l_without_latlon"] += 1
                continue
            matched = [
                ln for ln in ofcl
                if ln.valid == lp.dt and ln.lat is not None and ln.lon is not None
            ]
            if not matched:
                skipped["no_ofcl_at_L_time"] += 1
                continue
            for ln in matched:
                errors.append({
                    "storm_id": storm.storm_id,
                    "tau": ln.tau,
                    "km": haversine_km(ln.lat, ln.lon, lp.lat, lp.lon),
                })
    by_lead: dict[str, Any] = {}
    for lead in LEADS:
        rows = [e for e in errors if e["tau"] == lead]
        if not rows:
            continue
        by_lead[str(lead)] = {
            "n": len(rows),
            "mae_km": statistics.fmean(e["km"] for e in rows),
        }
    return {
        "binary_landfall_scored": False,
        "binary_block_reason": (
            "Oui/non landfall demanderait une côte. Le PDF HURDAT2 dit que "
            "le drapeau L est incomplet sur certaines années. On ne "
            "redessine pas la carte. On mesure seulement l'écart de "
            "trajectoire au point L, quand un OFCL tombe pile à cette heure."
        ),
        "n_ofcl_at_exact_L_time": len(errors),
        "n_storms": len({e["storm_id"] for e in errors}),
        "mae_km": statistics.fmean(e["km"] for e in errors) if errors else None,
        "by_lead": by_lead,
        "skipped": skipped.as_dict(),
    }


def score_decks(
    adecks: dict[str, list[AtcfLine]],
    bdecks: dict[str, list[AtcfLine]],
    storms: Iterable[HurdatStorm],
) -> dict[str, Any]:
    by_id = {s.storm_id: s for s in storms}
    pairs, skipped_int = _intensity_pairs(adecks, by_id)
    intensity = summarize_intensity(pairs)
    intensity["skipped"] = skipped_int
    return {
        "catalogue": CATALOGUE_DECKS,
        "intensity": intensity,
        "bdeck_vs_hurdat2": _bdeck_vs_hurdat2(bdecks, by_id),
        "first_hu_timing": first_hu_timing(adecks, by_id),
        "landfall": landfall_track_error(adecks, by_id),
        "n_adeck_storms": len(adecks),
        "n_bdeck_storms": len(bdecks),
        "n_hurdat2_overlap": sum(1 for sid in adecks if sid in by_id),
    }
