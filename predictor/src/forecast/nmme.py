"""NMME public-access probe (no CDS account).

FR : Deuxième choix du catalogue si Open-Meteo Seasonal n'a pas
d'archive. On sonde l'IRI et la page CPC. Un site HTML qui répond
n'est pas un hindcast. On n'invente pas de série.

EN : Probe only. A web page is not a scored hindcast.
"""
from __future__ import annotations

from typing import Any

import requests

from src.config import USER_AGENT

FORECAST_NAME = "NMME"

# Tried 2026-09-12. FTP CPC is omitted: it hangs without returning a series.
PROBE_URLS = (
    "https://iridl.ldeo.columbia.edu/SOURCES/.Models/.NMME/dataset_description.html",
    "https://iridl.ldeo.columbia.edu/SOURCES/.Models/.NMME/.NCEP-CFSv2/.HINDCAST/.MONTHLY/.prec/data.tsv",
    "https://www.cpc.ncep.noaa.gov/products/NMME/data.html",
)


def _looks_like_hindcast(content_type: str, sample: bytes) -> bool:
    head = sample[:200].lstrip().lower()
    if b"<html" in head or head.startswith(b"<!doctype"):
        return False
    text = sample.decode("utf-8", errors="replace")
    if "404" in text and "not found" in text.lower():
        return False
    if content_type and "html" in content_type.lower():
        return False
    # A real IRI TSV/ASCII dump starts with numbers or a short header, not HTML.
    return any(ch.isdigit() for ch in text[:80]) and "<html" not in text[:200].lower()


def probe_nmme(timeout: int = 12) -> dict[str, Any]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "*/*"})
    results = []
    hindcast_ok = False
    for url in PROBE_URLS:
        row: dict[str, Any] = {"url": url}
        try:
            r = session.get(url, timeout=(8, timeout), allow_redirects=True, stream=True)
            chunk = b""
            for part in r.iter_content(chunk_size=2048):
                chunk += part
                if len(chunk) >= 2048:
                    break
            r.close()
            row["http_status"] = r.status_code
            row["bytes_sampled"] = len(chunk)
            row["content_type"] = r.headers.get("Content-Type", "")
            row["hindcast_series"] = (
                200 <= r.status_code < 400 and _looks_like_hindcast(row["content_type"], chunk)
            )
            row["ok"] = 200 <= r.status_code < 400
            if row["hindcast_series"]:
                hindcast_ok = True
        except Exception as e:
            row["ok"] = False
            row["hindcast_series"] = False
            row["error"] = f"{type(e).__name__}: {e}"
        results.append(row)
    return {
        "forecast_name": FORECAST_NAME,
        "any_ok": any(r.get("ok") for r in results),
        "hindcast_usable": False,
        "probes": results,
        "blocker": (
            "IRI répond (grille mondiale ou moyenne sans axe de temps). "
            "On n'a pas une série Midwest / Southwest datée à apparier "
            "au US Drought Monitor. Pas de score NMME inventé."
        ),
    }
