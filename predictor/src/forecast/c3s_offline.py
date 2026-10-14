"""C3S multi-modèle hors ligne : lecture locale seulement, jamais CDS.

FR : Le PM télécharge les centres C3S sur sa machine. Ici on lit un
CSV de moyennes régionales déjà faites. La moyenne multi-modèle est
équipondérée par centre. Un centre absent est un trou : on ne le
remplit pas, et on ne lit pas le CSV SEAS5 pour le combler.
Pas de cdsapi. Pas de clé. Pas de chiffre inventé.

EN : Offline C3S multi-model reader. Equal weight per centre. A missing
centre is a hole, never filled from the SEAS5 file. No cdsapi.
"""
from __future__ import annotations

import csv
import statistics
from pathlib import Path
from typing import Any, Iterable, Optional

from src.config import DATA_DIR
from src.forecast.seas5_offline import (
    canonical_region,
    met_season,
    valid_year_month,
    _cell,
    _open_text,
    _require_columns,
)

FORECAST_NAME = "C3S multi-modèle"
FORECAST_FILENAME = "c3s_tp_monthly.csv"

C3S_DIR = DATA_DIR / "forecasts" / "c3s"
C3S_OUT = DATA_DIR / "truth" / "c3s_ab"
LOCAL_FORECAST_CSV = C3S_DIR / FORECAST_FILENAME

# Authoritative PM drop. Never call CDS to fill it.
SHARED_FORECAST_DIR = Path("/workspace/cds-test/c3s-monthly")
SHARED_FORECAST_CSV = SHARED_FORECAST_DIR / FORECAST_FILENAME

# First hindcast batch the PM is downloading. A year outside this
# window is reported. It is not invented and it is not required.
HINDCAST_YEAR_MIN = 1993
HINDCAST_YEAR_MAX = 2016

# Centres the PM said would be in the file. System ids are the C3S
# system numbers (ECMWF 51 is SEAS5).
EXPECTED_CENTRES: tuple[tuple[str, int], ...] = (
    ("meteo_france", 8),
    ("dwd", 21),
    ("cmcc", 35),
    ("ncep", 2),
    ("ecmwf", 51),
)
ECMWF_51: tuple[str, int] = ("ecmwf", 51)
EXPECTED_CENTRE_SET = set(EXPECTED_CENTRES)

CENTRE_LABELS = {
    ("meteo_france", 8): "Météo-France système 8",
    ("dwd", 21): "DWD système 21",
    ("cmcc", 35): "CMCC système 35",
    ("ncep", 2): "NCEP système 2",
    ("ecmwf", 51): "ECMWF système 51 (SEAS5)",
}

C3S_REQUIRED = (
    "origin",
    "system",
    "region",
    "year",
    "init_month",
    "lead_month",
    "tp_mean_mm",
    "n_members",
    "n_cells",
)

_ORIGIN_ALIASES = {
    "meteo_france": "meteo_france",
    "météo_france": "meteo_france",
    "mf": "meteo_france",
    "dwd": "dwd",
    "cmcc": "cmcc",
    "ncep": "ncep",
    "ecmwf": "ecmwf",
}

RAW_SUFFIXES = (".nc", ".nc4", ".grib", ".grb", ".grb2", ".zip")


def centre_label(origin: str, system: int) -> str:
    return CENTRE_LABELS.get((origin, system), f"{origin} système {system}")


def centre_record(origin: str, system: int) -> dict[str, Any]:
    return {
        "origin": origin,
        "system": int(system),
        "label": centre_label(origin, system),
    }


def _norm_origin(origin: str) -> str:
    return (origin or "").strip().lower().replace(" ", "_").replace("-", "_")


def classify_centre(origin: str, system: int) -> tuple[str, int, bool]:
    """Return (origin, system, expected).

    SEAS5 copied into this file is ECMWF system 51. Any other origin
    stays out of the mean and is reported. It does not fill a hole.
    """
    key = _norm_origin(origin)
    if not key:
        raise ValueError("origine vide")
    if key in {"seas5", "ecmwf_seas5"} and int(system) == 51:
        return "ecmwf", 51, True
    mapped = _ORIGIN_ALIASES.get(key)
    if mapped is None:
        return key, int(system), False
    pair = (mapped, int(system))
    return mapped, int(system), pair in EXPECTED_CENTRE_SET


def _blocked_no_forecast_message(
    include_shared: bool = True,
    explicit: Optional[Path] = None,
) -> str:
    if explicit is not None:
        where = str(explicit)
    elif include_shared:
        where = f"{SHARED_FORECAST_CSV}, puis {LOCAL_FORECAST_CSV}"
    else:
        where = str(LOCAL_FORECAST_CSV)
    return (
        "Aucun CSV C3S. Mesure bloquée. Cherché : "
        f"{where}. "
        "Pas d'appel CDS. Pas de score inventé. "
        "Le PM dépose c3s_tp_monthly.csv "
        "(colonnes origin,system,region,year,init_month,lead_month,"
        "tp_mean_mm,n_members,n_cells ; "
        "régions MED, Midwest, Southwest, India)."
    )


def _usable_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def _parse_int(text: str, path: Path, line: int, column: str) -> int:
    if text == "":
        raise ValueError(f"{path}:{line}: {column} vide")
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError(
            f"{path}:{line}: {column} entier attendu, reçu {text!r}"
        ) from exc


def _parse_float(text: str, path: Path, line: int, column: str) -> float:
    if text == "":
        raise ValueError(f"{path}:{line}: {column} vide")
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(
            f"{path}:{line}: {column} nombre attendu, reçu {text!r}"
        ) from exc


def candidate_paths(
    directory: Optional[Path] = None,
    include_shared: bool = True,
    explicit: Optional[Path] = None,
) -> list[Path]:
    """Shared PM CSV first, then the repo copy, unless a path is given."""
    if explicit is not None:
        return [Path(explicit)]
    out: list[Path] = []
    if include_shared:
        out.append(SHARED_FORECAST_CSV)
    if directory is not None:
        folder = Path(directory)
        if folder.suffix.lower() == ".csv":
            out.append(folder)
        else:
            out.append(folder / FORECAST_FILENAME)
    out.append(LOCAL_FORECAST_CSV)
    seen: set[str] = set()
    unique: list[Path] = []
    for path in out:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def find_c3s_csv(
    directory: Optional[Path] = None,
    include_shared: bool = True,
    explicit: Optional[Path] = None,
) -> Optional[Path]:
    for path in candidate_paths(directory, include_shared, explicit):
        if _usable_file(path):
            return path
    return None


def list_raw_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in RAW_SUFFIXES
    )


def _search_dirs(
    directory: Optional[Path],
    include_shared: bool,
) -> list[Path]:
    dirs: list[Path] = []
    if include_shared:
        dirs.append(SHARED_FORECAST_DIR)
    if directory is not None:
        folder = Path(directory)
        if folder.suffix.lower() != ".csv":
            dirs.append(folder)
    dirs.append(C3S_DIR)
    seen: set[str] = set()
    unique: list[Path] = []
    for path in dirs:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def load_c3s_csv(path: Path) -> list[dict[str, Any]]:
    """Read one row per centre. Empty file → no rows. No invented values."""
    with _open_text(path) as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames, C3S_REQUIRED, path)
        rows: list[dict[str, Any]] = []
        seen: set[tuple[Any, ...]] = set()
        for i, raw in enumerate(reader, start=2):
            if not any((v or "").strip() for v in raw.values()):
                continue
            origin_raw = _cell(raw, "origin")
            system = _parse_int(_cell(raw, "system"), path, i, "system")
            try:
                origin, system, expected = classify_centre(origin_raw, system)
            except ValueError as exc:
                raise ValueError(f"{path}:{i}: {exc}") from exc
            try:
                region = canonical_region(_cell(raw, "region"))
            except ValueError as exc:
                raise ValueError(
                    f"{path}:{i}: région C3S inconnue : {_cell(raw, 'region')!r}"
                ) from exc
            init_year = _parse_int(_cell(raw, "year"), path, i, "year")
            init_month = _parse_int(_cell(raw, "init_month"), path, i, "init_month")
            lead_month = _parse_int(_cell(raw, "lead_month"), path, i, "lead_month")
            tp = _parse_float(_cell(raw, "tp_mean_mm"), path, i, "tp_mean_mm")
            n_members = _parse_int(_cell(raw, "n_members"), path, i, "n_members")
            n_cells = _parse_int(_cell(raw, "n_cells"), path, i, "n_cells")
            key = (origin, system, region, init_year, init_month, lead_month)
            if key in seen:
                raise ValueError(
                    f"{path}:{i}: doublon {origin} système {system} "
                    f"{region} {init_year}-{init_month} lead {lead_month}. "
                    "Pas de moyenne inventée entre deux copies."
                )
            seen.add(key)
            valid_year, valid_month = valid_year_month(
                init_year, init_month, lead_month
            )
            season, season_year = met_season(valid_year, valid_month)
            rows.append({
                "origin": origin,
                "system": system,
                "expected": expected,
                "region": region,
                "init_year": init_year,
                "init_month": init_month,
                "lead_month": lead_month,
                "tp_mean_mm": tp,
                "n_members": n_members,
                "n_cells": n_cells,
                "valid_year": valid_year,
                "valid_month": valid_month,
                "season": season,
                "season_year": season_year,
                "path": str(path),
            })
        return rows


def aggregate_equal_weight(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Equal-weight mean of expected centres on one cell.

    Weight is one per centre, not per member. A centre missing on that
    cell is listed and left empty. Unexpected centres are ignored here
    (they are reported by the inventory, not mixed in).
    """
    buckets: dict[tuple[str, int, int, int], dict[tuple[str, int], dict[str, Any]]] = {}
    for row in rows:
        if not row.get("expected"):
            continue
        key = (
            row["region"],
            int(row["init_year"]),
            int(row["init_month"]),
            int(row["lead_month"]),
        )
        centre = (row["origin"], int(row["system"]))
        slot = buckets.setdefault(key, {})
        if centre in slot:
            raise ValueError(
                f"doublon {centre} {key}. Pas de moyenne inventée."
            )
        slot[centre] = row
    out: list[dict[str, Any]] = []
    for key in sorted(buckets):
        present = buckets[key]
        if not present:
            continue
        # Insertion follows EXPECTED_CENTRES so the mean order is stable.
        used = [c for c in EXPECTED_CENTRES if c in present]
        values = [float(present[c]["tp_mean_mm"]) for c in used]
        sample = present[used[0]]
        missing = [c for c in EXPECTED_CENTRES if c not in present]
        out.append({
            "region": sample["region"],
            "init_year": sample["init_year"],
            "init_month": sample["init_month"],
            "lead_month": sample["lead_month"],
            "tp_mean_mm": float(statistics.fmean(values)),
            "tp_anom_mm": None,
            "valid_year": sample["valid_year"],
            "valid_month": sample["valid_month"],
            "season": sample["season"],
            "season_year": sample["season_year"],
            "n_centres": len(used),
            "centres_used": [centre_record(*c) for c in used],
            "missing_centres": [centre_record(*c) for c in missing],
            "weighting": "equal_centre",
        })
    return out


def filter_window(
    rows: Iterable[dict[str, Any]],
    init_month: Optional[int],
    min_lead: int,
    max_lead: int,
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for row in rows:
        if init_month is not None and int(row["init_month"]) != init_month:
            continue
        lead = int(row["lead_month"])
        if lead < min_lead or lead > max_lead:
            continue
        kept.append(row)
    return kept


def _unexpected(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    found: dict[tuple[str, int], int] = {}
    for row in rows:
        if row.get("expected"):
            continue
        key = (row["origin"], int(row["system"]))
        found[key] = found.get(key, 0) + 1
    return [
        {**centre_record(origin, system), "n_rows": n}
        for (origin, system), n in sorted(found.items())
    ]


def inventory(
    rows: Iterable[dict[str, Any]],
    aggregated: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Holes are counted. Nothing is filled."""
    raw = list(rows)
    agg = list(aggregated)
    counts = {c: 0 for c in EXPECTED_CENTRES}
    years: set[int] = set()
    for row in raw:
        years.add(int(row["init_year"]))
        key = (row["origin"], int(row["system"]))
        if key in counts and row.get("expected"):
            counts[key] += 1
    cells_missing = {f"{o}:{s}": 0 for o, s in EXPECTED_CENTRES}
    for row in agg:
        for hole in row["missing_centres"]:
            cells_missing[f"{hole['origin']}:{hole['system']}"] += 1
    present_years = sorted(years)
    window = range(HINDCAST_YEAR_MIN, HINDCAST_YEAR_MAX + 1)
    return {
        "weighting": "equal_centre",
        "filled_from_seas5": False,
        "expected_centres": [
            {
                **centre_record(origin, system),
                "n_rows": counts[(origin, system)],
                "present": counts[(origin, system)] > 0,
                "hole": counts[(origin, system)] == 0,
            }
            for origin, system in EXPECTED_CENTRES
        ],
        "missing_centres": [
            centre_record(origin, system)
            for origin, system in EXPECTED_CENTRES
            if counts[(origin, system)] == 0
        ],
        "unexpected_centres": _unexpected(raw),
        "n_rows": len(raw),
        "n_cells": len(agg),
        "n_cells_with_hole": sum(1 for row in agg if row["missing_centres"]),
        "cells_missing_by_centre": cells_missing,
        "years_present": present_years,
        "hindcast_years_expected": [HINDCAST_YEAR_MIN, HINDCAST_YEAR_MAX],
        "missing_years_in_window": [y for y in window if y not in years],
        "years_outside_window": [
            y for y in present_years
            if y < HINDCAST_YEAR_MIN or y > HINDCAST_YEAR_MAX
        ],
    }


def empty_inventory() -> dict[str, Any]:
    return inventory([], [])


def forecast_status(
    directory: Optional[Path] = None,
    include_shared: bool = True,
    explicit: Optional[Path] = None,
) -> dict[str, Any]:
    """What is on disk. Never invents a row and never calls CDS."""
    searched = candidate_paths(directory, include_shared, explicit)
    csv_path = find_c3s_csv(directory, include_shared, explicit)
    raw: list[Path] = []
    for folder in _search_dirs(directory, include_shared and explicit is None):
        raw.extend(list_raw_files(folder))
    reason = None
    if csv_path is None:
        if raw:
            reason = (
                "Fichiers bruts C3S présents "
                f"({', '.join(p.name for p in raw)}), "
                "mais pas de CSV régional. "
                "Pas d'appel CDS. Pas de décodage NetCDF/GRIB. "
                "Pas de score inventé. Mesure bloquée."
            )
        else:
            reason = _blocked_no_forecast_message(include_shared, explicit)
    return {
        "forecast_name": FORECAST_NAME,
        "directory": str(Path(directory) if directory is not None else C3S_DIR),
        "searched": [str(p) for p in searched],
        "present": csv_path is not None,
        "csv_path": str(csv_path) if csv_path else None,
        "raw_files": [p.name for p in raw],
        "reason": reason,
        "cds_called": False,
        "cdsapi_imported": False,
        "filled_from_seas5": False,
        "weighting": "equal_centre",
        "hindcast_years_expected": [HINDCAST_YEAR_MIN, HINDCAST_YEAR_MAX],
        "expected_centres": [centre_record(*c) for c in EXPECTED_CENTRES],
    }
