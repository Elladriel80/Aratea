"""Téléchargement des bulletins NBM (archive S3 NOAA, repli IEM).

FR : L'archive publique est
`https://noaa-nbm-grib2-pds.s3.amazonaws.com/blend.YYYYMMDD/HH/text/`.
Un fichier national pèse ~35 Mo. On le lit, on garde seulement les
18 stations Kalshi, puis on jette le fichier. Si S3 échoue, on tente
le bulletin station IEM (produit AFOS NBP***), et on le dit.

EN : Download NBM text from NOAA S3, keep 18 Kalshi stations, record
failures instead of inventing values.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

import requests

from src.config import DATA_DIR, USER_AGENT
from src.forecast.nbm_text import NbmDaily, extract_station_blocks, from_compact, parse_bulletin
from src.truth.iem_cli import kalshi_stations

S3_BASE = "https://noaa-nbm-grib2-pds.s3.amazonaws.com"
IEM_AFOS = "https://mesonet.agron.iastate.edu/cgi-bin/afos/retrieve.py"
NBM_DIR = DATA_DIR / "nbm"
CACHE_DIR = NBM_DIR / "cache"
EXTRACTED_PATH = NBM_DIR / "extracted.json"

PRODUCT_FILE = {
    "NBP": "nbptx",
    "NBS": "nbstx",
    "NBE": "nbetx",
}

# Cycles NBP complets (doc v5.0) : 01 / 07 / 13 / 19 UTC.
NBP_CYCLES = (1, 7, 13, 19)


@dataclass
class FetchFailure:
    source: str
    url: str
    issued_date: str
    cycle: int
    product: str
    error: str


@dataclass
class FetchResult:
    forecasts: list[NbmDaily] = field(default_factory=list)
    failures: list[FetchFailure] = field(default_factory=list)
    fetched_urls: list[str] = field(default_factory=list)
    from_cache: int = 0


class NbmTextClient:
    """Client S3 + cache disque des extraits station."""

    def __init__(
        self,
        cache_dir: Path = CACHE_DIR,
        extracted_path: Path = EXTRACTED_PATH,
        sleep_s: float = 0.2,
        timeout_s: float = 90.0,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.extracted_path = Path(extracted_path)
        self.extracted_path.parent.mkdir(parents=True, exist_ok=True)
        self.sleep_s = sleep_s
        self.timeout_s = timeout_s
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/plain, application/octet-stream, */*",
        })

    @staticmethod
    def s3_url(issued: date, cycle: int, product: str = "NBP") -> str:
        key = PRODUCT_FILE[product]
        ymd = issued.strftime("%Y%m%d")
        hh = f"{cycle:02d}"
        return f"{S3_BASE}/blend.{ymd}/{hh}/text/blend_{key}.t{hh}z"

    def _extract_cache_path(self, issued: date, cycle: int, product: str) -> Path:
        return self.cache_dir / f"{product.lower()}_{issued.strftime('%Y%m%d')}_t{cycle:02d}z.json"

    def fetch_cycle(
        self,
        issued: date,
        cycle: int,
        product: str = "NBP",
        stations: Optional[Iterable[str]] = None,
        use_cache: bool = True,
    ) -> tuple[list[NbmDaily], Optional[FetchFailure], bool]:
        """Télécharge un cycle. Renvoie (prévisions, échec ou None, depuis_cache)."""
        wanted = [s.upper() for s in (stations or kalshi_stations())]
        cache = self._extract_cache_path(issued, cycle, product)
        if use_cache and cache.exists():
            try:
                payload = json.loads(cache.read_text(encoding="utf-8"))
                rows = [from_compact(r) for r in payload.get("forecasts", [])]
                if payload.get("stations_found"):
                    return rows, None, True
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                pass

        url = self.s3_url(issued, cycle, product)
        try:
            time.sleep(self.sleep_s)
            resp = self.session.get(url, timeout=self.timeout_s)
            if resp.status_code == 404:
                fail = FetchFailure("s3", url, issued.isoformat(), cycle, product,
                                    "fichier absent (404)")
                return [], fail, False
            resp.raise_for_status()
            text = resp.content.decode("ascii", errors="replace")
        except requests.RequestException as e:
            return [], FetchFailure("s3", url, issued.isoformat(), cycle, product, str(e)), False

        blocks = extract_station_blocks(text, wanted)
        forecasts = parse_bulletin(text, wanted)
        cache.write_text(json.dumps({
            "issued": issued.isoformat(), "cycle": cycle, "product": product,
            "url": url, "stations_found": sorted(blocks),
            "stations_missing": sorted(set(wanted) - set(blocks)),
            "n_forecasts": len(forecasts),
            "forecasts": [f.to_compact() for f in forecasts],
        }, separators=(",", ":")), encoding="utf-8")
        return forecasts, None, False

    def fetch_range(
        self,
        start: date,
        end: date,
        cycles: Iterable[int] = (13,),
        product: str = "NBP",
        stations: Optional[Iterable[str]] = None,
        workers: int = 3,
    ) -> FetchResult:
        """Tous les cycles de `start` à `end` inclus. Les échecs sont listés."""
        wanted = [s.upper() for s in (stations or kalshi_stations())]
        jobs = []
        d = start
        while d <= end:
            for cyc in cycles:
                jobs.append((d, int(cyc)))
            d += timedelta(days=1)

        result = FetchResult()
        if not jobs:
            return result

        def _one(job):
            issued, cyc = job
            return issued, cyc, self.fetch_cycle(issued, cyc, product, wanted)

        workers = max(1, min(workers, len(jobs)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futs = [pool.submit(_one, job) for job in jobs]
            for fut in as_completed(futs):
                issued, cyc, (rows, fail, cached) = fut.result()
                result.forecasts.extend(rows)
                if fail:
                    result.failures.append(fail)
                else:
                    result.fetched_urls.append(self.s3_url(issued, cyc, product))
                    if cached:
                        result.from_cache += 1
        result.forecasts.sort(key=lambda f: (f.station, f.issued, f.target, f.variable))
        return result

    def persist_extracted(self, forecasts: list[NbmDaily]) -> Path:
        """Fusionne dans extracted.json (mémoire compacte, sans les 35 Mo)."""
        existing: dict[str, dict] = {}
        if self.extracted_path.exists():
            try:
                for r in json.loads(self.extracted_path.read_text(encoding="utf-8")):
                    existing[_key(r)] = r
            except (json.JSONDecodeError, TypeError, KeyError):
                existing = {}
        for f in forecasts:
            row = f.to_compact()
            existing[_key(row)] = row
        rows = sorted(existing.values(), key=lambda r: (
            r["station"], r["issued"], r["target"], r["variable"]))
        self.extracted_path.write_text(
            json.dumps(rows, separators=(",", ":")), encoding="utf-8"
        )
        return self.extracted_path

    def load_extracted(self) -> list[NbmDaily]:
        if not self.extracted_path.exists():
            return []
        rows = json.loads(self.extracted_path.read_text(encoding="utf-8"))
        return [from_compact(r) for r in rows]


def _key(r: dict) -> str:
    return "|".join([
        r["station"], r["product"], r["issued"], r["target"],
        r["variable"], str(r["lead"]), str(r["fhr"]),
    ])


def try_iem_afos_latest(station: str, timeout_s: float = 30.0) -> tuple[list[NbmDaily], Optional[str]]:
    """Derniers bulletins NBP d'une station via IEM AFOS. Pas d'historique long.

    IEM ne garde ici que les émissions récentes. Utile pour vérifier qu'une
    station existe ; insuffisant pour le holdout d'août.
    """
    pil = "NBP" + station.upper()[-3:]
    url = f"{IEM_AFOS}?pil={pil}&limit=2"
    try:
        resp = requests.get(
            url, timeout=timeout_s,
            headers={"User-Agent": USER_AGENT, "Accept": "text/plain"},
        )
        resp.raise_for_status()
        text = resp.text
    except requests.RequestException as e:
        return [], f"IEM AFOS {pil} : {e}"
    if "ERROR:" in text[:80] or "NBM" not in text:
        return [], f"IEM AFOS {pil} : pas de bulletin ({text.strip()[:80]})"
    return parse_bulletin(text, [station]), None
