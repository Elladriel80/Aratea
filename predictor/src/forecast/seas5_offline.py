"""SEAS5 hors ligne : lecture locale seulement, jamais CDS.

FR : Le PM télécharge les tranches SEAS5 sur sa machine (compte
Copernicus). Ici on lit un CSV de moyennes régionales déjà faites.
Pas de cdsapi. Pas de clé. Pas de chiffre inventé.

EN : Offline SEAS5 reader. Auth stays on the Aratea PM box. Cloud
agents never call CDS.
"""
from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional

from src.config import DATA_DIR

FORECAST_NAME = "SEAS5"
SEAS5_DIR = DATA_DIR / "forecasts" / "seas5"
SEAS5_OUT = DATA_DIR / "truth" / "seas5_ab"

# C3S / CDS area boxes the PM uses to download. Scoring still uses the
# published polygons from PRs 240 / 243 / 244, not these rectangles.
# Order is CDS [North, West, South, East].
DOWNLOAD_ENVELOPES: dict[str, dict[str, Any]] = {
    "med": {
        "label": "Méditerranée",
        "cds_area": [45.0, -10.0, 30.0, 40.0],
        "mask": "IPCC AR6 WGI MED (PR 243 / 244)",
    },
    "midwest": {
        "label": "Midwest",
        "cds_area": [49.5, -97.5, 36.0, -80.5],
        "mask": "USDA Climate Hub Midwest (PR 240 / 243)",
    },
    "southwest": {
        "label": "Southwest",
        "cds_area": [42.0, -124.5, 31.3, -103.0],
        "mask": "USDA Climate Hub Southwest (PR 240 / 243)",
    },
    "india_mh_ka": {
        "label": "Inde Maharashtra+Karnataka",
        "cds_area": [22.1, 72.5, 11.5, 81.0],
        "mask": "Maharashtra + Karnataka Natural Earth (PR 243 / 244)",
    },
}

FORECAST_REQUIRED = ("region", "year", "init_month", "lead_month", "tp_mean_mm")
FORECAST_OPTIONAL = ("tp_anom_mm", "valid_year", "valid_month", "ensemble_size", "source")

FORECAST_FILENAMES = (
    "regional_monthly.csv",
    "seas5_regional_monthly.csv",
    "seas5.csv",
)

PAIRS_FILENAMES = {
    "usdm": "pairs_usdm.csv",
    "spei": "pairs_spei.csv",
    "chirps": "pairs_chirps.csv",
}

REGION_ALIASES = {
    "midwest": "midwest",
    "us_midwest": "midwest",
    "midwest_us": "midwest",
    "southwest": "southwest",
    "us_southwest": "southwest",
    "southwest_us": "southwest",
    "med": "med",
    "mediterranee": "med",
    "méditerranée": "med",
    "mediterranean": "med",
    "ipcc_med": "med",
    "india_mh_ka": "india_mh_ka",
    "inde": "india_mh_ka",
    "india": "india_mh_ka",
    "mh_ka": "india_mh_ka",
    "maharashtra_karnataka": "india_mh_ka",
    "maharashtra+karnataka": "india_mh_ka",
    "us": "us",
    "usa": "us",
    "secheresse_us": "us",
    "sécheresse us": "us",
}

RAW_SUFFIXES = (".nc", ".nc4", ".grib", ".grb", ".grb2", ".zip")

_BLOCKED_NO_FORECAST = (
    "Aucun CSV SEAS5 sous data/forecasts/seas5/. "
    "Pas d'appel CDS. Pas de score inventé. "
    "Le PM dépose regional_monthly.csv (colonnes "
    "region,year,init_month,lead_month,tp_mean_mm)."
)


def canonical_region(raw: str) -> str:
    key = (raw or "").strip().lower().replace(" ", "_")
    if key not in REGION_ALIASES:
        raise ValueError(f"région SEAS5 inconnue : {raw!r}")
    return REGION_ALIASES[key]


def valid_year_month(init_year: int, init_month: int, lead_month: int) -> tuple[int, int]:
    """C3S leadtime_month : 1 = le mois d'init. Rien n'est inventé."""
    if not (1 <= init_month <= 12):
        raise ValueError(f"init_month hors 1-12 : {init_month}")
    if lead_month < 1:
        raise ValueError(f"lead_month < 1 : {lead_month}")
    total = init_month + lead_month - 1
    year = init_year + (total - 1) // 12
    month = ((total - 1) % 12) + 1
    return year, month


def met_season(year: int, month: int) -> tuple[str, int]:
    """Saison météo. L'année de DJF est l'année de janvier."""
    if month == 12:
        return "DJF", year + 1
    if month in (1, 2):
        return "DJF", year
    if month in (3, 4, 5):
        return "MAM", year
    if month in (6, 7, 8):
        return "JJA", year
    return "SON", year


def _open_text(path: Path) -> Any:
    return path.open(newline="", encoding="utf-8-sig")


def _cell(row: dict[str, str], key: str) -> str:
    if key in row and row[key] is not None:
        return str(row[key]).strip()
    lower = {k.lower().strip(): k for k in row}
    if key.lower() in lower:
        return str(row[lower[key.lower()]] or "").strip()
    return ""


def _require_columns(fieldnames: Optional[Iterable[str]], required: Iterable[str], path: Path) -> None:
    have = {((name or "").strip().lower()) for name in (fieldnames or [])}
    missing = [c for c in required if c not in have]
    if missing:
        raise ValueError(
            f"{path}: colonnes manquantes {missing}. "
            f"Attendu : {', '.join(required)}."
        )


def list_raw_forecast_files(directory: Path = SEAS5_DIR) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in RAW_SUFFIXES
    )


def find_forecast_csv(directory: Path = SEAS5_DIR) -> Optional[Path]:
    if not directory.is_dir():
        return None
    for name in FORECAST_FILENAMES:
        path = directory / name
        if path.is_file() and path.stat().st_size > 0:
            return path
    extras = []
    for path in sorted(directory.glob("*.csv")):
        if path.name.endswith(".example"):
            continue
        if path.name in PAIRS_FILENAMES.values():
            continue
        if path.name in FORECAST_FILENAMES:
            continue
        extras.append(path)
    for path in extras:
        if path.stat().st_size == 0:
            continue
        with _open_text(path) as handle:
            reader = csv.DictReader(handle)
            have = {((name or "").strip().lower()) for name in (reader.fieldnames or [])}
            if set(FORECAST_REQUIRED) <= have:
                return path
    return None


def find_pairs_csv(truth: str, directory: Path = SEAS5_DIR) -> Optional[Path]:
    name = PAIRS_FILENAMES.get(truth)
    if not name:
        return None
    path = directory / name
    if path.is_file() and path.stat().st_size > 0:
        return path
    return None


def forecast_status(directory: Path = SEAS5_DIR) -> dict[str, Any]:
    """What is on disk. Never invents a forecast row."""
    csv_path = find_forecast_csv(directory)
    pairs = {key: find_pairs_csv(key, directory) for key in PAIRS_FILENAMES}
    raw = list_raw_forecast_files(directory)
    present = csv_path is not None or any(pairs.values())
    reason = None
    if not present:
        if raw:
            reason = (
                "Fichiers bruts SEAS5 présents "
                f"({', '.join(p.name for p in raw)}), "
                "mais pas de CSV régional. "
                "Pas d'appel CDS. Pas de décodage NetCDF/GRIB. "
                "Pas de score inventé."
            )
        else:
            reason = _BLOCKED_NO_FORECAST
    return {
        "forecast_name": FORECAST_NAME,
        "directory": str(directory),
        "present": present,
        "csv_path": str(csv_path) if csv_path else None,
        "pairs": {k: (str(v) if v else None) for k, v in pairs.items()},
        "raw_files": [p.name for p in raw],
        "reason": reason,
        "cds_called": False,
        "cdsapi_imported": False,
    }


def load_forecast_csv(path: Path) -> list[dict[str, Any]]:
    """Read regional monthly means. Empty / header-only → no rows."""
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames, FORECAST_REQUIRED, path)
        rows: list[dict[str, Any]] = []
        for i, raw in enumerate(reader, start=2):
            if not any((v or "").strip() for v in raw.values()):
                continue
            region = canonical_region(_cell(raw, "region"))
            init_year = int(_cell(raw, "year"))
            init_month = int(_cell(raw, "init_month"))
            lead_month = int(_cell(raw, "lead_month"))
            tp = _cell(raw, "tp_mean_mm")
            if tp == "":
                raise ValueError(f"{path}:{i}: tp_mean_mm vide")
            source = _cell(raw, "source")
            if source and source.strip().upper() not in ("SEAS5", "ECMWF SEAS5"):
                raise ValueError(
                    f"{path}:{i}: source={source!r} (nom stable : SEAS5)"
                )
            vy_s, vm_s = _cell(raw, "valid_year"), _cell(raw, "valid_month")
            if vy_s and vm_s:
                valid_year, valid_month = int(vy_s), int(vm_s)
            else:
                valid_year, valid_month = valid_year_month(
                    init_year, init_month, lead_month
                )
            anom_s = _cell(raw, "tp_anom_mm")
            ens_s = _cell(raw, "ensemble_size")
            season, season_year = met_season(valid_year, valid_month)
            rows.append({
                "region": region,
                "init_year": init_year,
                "init_month": init_month,
                "lead_month": lead_month,
                "tp_mean_mm": float(tp),
                "tp_anom_mm": float(anom_s) if anom_s else None,
                "valid_year": valid_year,
                "valid_month": valid_month,
                "season": season,
                "season_year": season_year,
                "ensemble_size": int(ens_s) if ens_s else None,
                "source": FORECAST_NAME,
                "path": str(path),
            })
        return rows


def collapse_shortest_lead(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """One forecast per (region, valid year, valid month): shortest lead."""
    best: dict[tuple[str, int, int], dict[str, Any]] = {}
    for row in rows:
        key = (row["region"], row["valid_year"], row["valid_month"])
        prev = best.get(key)
        if prev is None or row["lead_month"] < prev["lead_month"]:
            best[key] = row
    return [best[k] for k in sorted(best)]


def load_pairs_csv(path: Path) -> list[dict[str, Any]]:
    """Ready-made (region, year, season, p_forecast_dry, event) rows."""
    required = ("region", "year", "season", "p_forecast_dry", "event")
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames, required, path)
        rows: list[dict[str, Any]] = []
        for i, raw in enumerate(reader, start=2):
            if not any((v or "").strip() for v in raw.values()):
                continue
            season = _cell(raw, "season").upper()
            if season not in {"DJF", "MAM", "JJA", "SON"}:
                raise ValueError(f"{path}:{i}: saison inconnue {season!r}")
            rows.append({
                "region": canonical_region(_cell(raw, "region")),
                "year": int(_cell(raw, "year")),
                "season": season,
                "p_forecast_dry": float(_cell(raw, "p_forecast_dry")),
                "event": _as_bool(_cell(raw, "event"), path, i),
                "path": str(path),
            })
        return rows


def _as_bool(value: str, path: Path, line: int) -> bool:
    text = value.strip().lower()
    if text in {"1", "true", "yes", "oui"}:
        return True
    if text in {"0", "false", "no", "non"}:
        return False
    raise ValueError(f"{path}:{line}: booléen invalide {value!r}")


def load_monthly_truth_csv(
    path: Path,
    value_key: str,
    event_key: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Monthly truth. value_key is spei6_mean or tp_mean_mm."""
    required = ["region", "year", "month", value_key]
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames, required, path)
        rows: list[dict[str, Any]] = []
        for i, raw in enumerate(reader, start=2):
            if not any((v or "").strip() for v in raw.values()):
                continue
            year = int(_cell(raw, "year"))
            month = int(_cell(raw, "month"))
            if not (1 <= month <= 12):
                raise ValueError(f"{path}:{i}: month hors 1-12 : {month}")
            season, season_year = met_season(year, month)
            value_s = _cell(raw, value_key)
            if value_s == "":
                continue
            event = None
            if event_key and _cell(raw, event_key) != "":
                event = _as_bool(_cell(raw, event_key), path, i)
            rows.append({
                "region": canonical_region(_cell(raw, "region")),
                "year": year,
                "month": month,
                "season": season,
                "season_year": season_year,
                "value": float(value_s),
                "event": event,
                "path": str(path),
            })
        return rows


def load_seasonal_truth_csv(
    path: Path,
    event_key: str,
    value_key: Optional[str] = None,
) -> list[dict[str, Any]]:
    required = ["region", "year", "season", event_key]
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames, required, path)
        rows: list[dict[str, Any]] = []
        for i, raw in enumerate(reader, start=2):
            if not any((v or "").strip() for v in raw.values()):
                continue
            season = _cell(raw, "season").upper()
            if season not in {"DJF", "MAM", "JJA", "SON"}:
                raise ValueError(f"{path}:{i}: saison inconnue {season!r}")
            value = None
            if value_key and _cell(raw, value_key) != "":
                value = float(_cell(raw, value_key))
            rows.append({
                "region": canonical_region(_cell(raw, "region")),
                "year": int(_cell(raw, "year")),
                "season": season,
                "event": _as_bool(_cell(raw, event_key), path, i),
                "value": value,
                "path": str(path),
            })
        return rows


def load_usdm_weeks_json(path: Path, region: str) -> list[dict[str, Any]]:
    """PR 240 --write-weeks JSON → saisons D2+ (seuil 30 %, déjà publié)."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path}: JSON liste attendue")
    buckets: dict[tuple[str, int], list[float]] = {}
    for raw in payload:
        stamp = raw.get("map_date") or raw.get("mapDate")
        if not stamp:
            raise ValueError(f"{path}: semaine sans map_date")
        d = date.fromisoformat(str(stamp)[:10])
        d2 = float(raw.get("d2") or 0.0)
        d3 = float(raw.get("d3") or 0.0)
        d4 = float(raw.get("d4") or 0.0)
        season, year = met_season(d.year, d.month)
        buckets.setdefault((season, year), []).append(d2 + d3 + d4)
    rows = []
    for (season, year), values in sorted(buckets.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if len(values) < 12:
            continue
        mean = sum(values) / len(values)
        rows.append({
            "region": region,
            "year": year,
            "season": season,
            "event": mean >= 30.0,
            "value": mean,
            "n_weeks": len(values),
            "path": str(path),
        })
    return rows


def inventory_hint(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0
