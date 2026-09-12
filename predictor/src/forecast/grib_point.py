"""Lecture d'un point de grille dans un message GRIB2 (eccodes).

FR : Dépendance optionnelle, seulement pour le script A3. Si eccodes
n'est pas installé, on le dit et on n'invente aucun chiffre.
"""
from __future__ import annotations

from typing import Optional


def _require_eccodes():
    try:
        from eccodes import codes_get, codes_get_array, codes_new_from_message, codes_release
    except ImportError as e:  # pragma: no cover — environnement sans eccodes
        raise RuntimeError(
            "eccodes manquant. Pour télécharger GEFS : pip install eccodes"
        ) from e
    return codes_new_from_message, codes_get, codes_get_array, codes_release


def kelvin_to_f(k: float) -> float:
    return k * 9.0 / 5.0 - 459.67


def nearest_index(lat: float, lon: float, lat1: float, lon1: float,
                  dlat: float, dlon: float, ni: int, nj: int) -> int:
    """Index 1D du point le plus proche sur une grille lat/lon régulière."""
    lon360 = lon % 360.0
    lon1 = lon1 % 360.0
    j = int(round((lat1 - lat) / dlat)) if dlat else 0
    i = int(round((lon360 - lon1) / dlon)) % ni if dlon else 0
    j = max(0, min(nj - 1, j))
    return j * ni + i


def points_from_message(blob: bytes, coords: dict[str, tuple[float, float]]) -> dict[str, float]:
    """{nom: valeur brute du GRIB} au plus proche voisin. Kelvin pour TMP/TMAX/TMIN."""
    new, get, get_array, release = _require_eccodes()
    h = new(blob)
    try:
        ni = int(get(h, "Ni"))
        nj = int(get(h, "Nj"))
        lat1 = float(get(h, "latitudeOfFirstGridPointInDegrees"))
        lon1 = float(get(h, "longitudeOfFirstGridPointInDegrees"))
        dlat = float(get(h, "jDirectionIncrementInDegrees"))
        dlon = float(get(h, "iDirectionIncrementInDegrees"))
        vals = get_array(h, "values")
        out: dict[str, float] = {}
        for name, (lat, lon) in coords.items():
            idx = nearest_index(lat, lon, lat1, lon1, dlat, dlon, ni, nj)
            out[name] = float(vals[idx])
        return out
    finally:
        release(h)


def parse_idx(text: str) -> list[dict]:
    """Lignes `.idx` wgrib2 → {start, end, name, level, fhr_text}."""
    lines = [ln for ln in (text or "").splitlines() if ln.strip()]
    rows = []
    for i, ln in enumerate(lines):
        parts = ln.split(":")
        if len(parts) < 5:
            continue
        try:
            start = int(parts[1])
        except ValueError:
            continue
        end: Optional[int] = None
        if i + 1 < len(lines):
            nxt = lines[i + 1].split(":")
            if len(nxt) > 1:
                try:
                    end = int(nxt[1]) - 1
                except ValueError:
                    end = None
        rows.append({
            "start": start,
            "end": end,
            "name": parts[3],
            "level": parts[4] if len(parts) > 4 else "",
            "fhr_text": parts[5] if len(parts) > 5 else "",
            "raw": ln,
        })
    return rows


def find_idx_row(rows: list[dict], name: str, level_substr: str = "2 m") -> Optional[dict]:
    for r in rows:
        if r["name"] == name and level_substr in r["level"]:
            return r
    return None
