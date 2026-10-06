"""Second marché : écart Kalshi / Polymarket, sans inventer de prix.

FR : Piste B4. Polymarket cote une échelle quotidienne de température
max. On ne compare que les contrats dont la case (bornes basses et
hautes) est la même des deux côtés. Un prix Polymarket manquant à
l'heure de la capture Kalshi n'est pas fabriqué. La vérité est le
chiffre CLI de la station Kalshi déjà dans le dépôt.

EN : B4. Exact-bound bin match only. No invented Polymarket prints.
Scored against the Kalshi CLI station already in-repo.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Iterable, Optional, Sequence

from src.truth.iem_cli import CITY_TO_ICAO
from src.truth.stacking import apply_stack, brier_mean, residual_weight
from src.truth.synthetic_bins import Bin


GAMMA_BASE = "https://gamma-api.polymarket.com"
CLOB_BASE = "https://clob.polymarket.com"
HIGHEST_TEMP_TAG_ID = "104596"

# Bornes : même forme que Kalshi (« 76° to 77° ») et Polymarket (« 76-77°F »).
_PM_BELOW = re.compile(r"(-?\d+)\s*°?\s*F?\s+or\s+below", re.I)
_PM_ABOVE = re.compile(r"(-?\d+)\s*°?\s*F?\s+or\s+higher", re.I)
_PM_RANGE = re.compile(r"(-?\d+)\s*°?\s*F?\s*-\s*(-?\d+)\s*°?\s*F?", re.I)
_SITE_RE = re.compile(r"[?&]site=([a-z0-9]+)", re.I)
_SAFE_RE = re.compile(r"[^A-Za-z0-9._-]")


@dataclass(frozen=True)
class CityMap:
    """Ville Polymarket qu'on peut tenter d'aligner sur une ville Kalshi."""
    slug: str
    kalshi_key: str
    series_slug: str
    kalshi_icao: str
    pm_icao_note: str
    label_fr: str

    @property
    def same_station_note(self) -> bool:
        return self.kalshi_icao == self.pm_icao_note


# Stations lues sur les textes de résolution Polymarket (12 sept. 2026),
# pas devinées. Kalshi = CITY_TO_ICAO / SERIES_TO_STATION déjà dans le repo.
CITY_MAPS: tuple[CityMap, ...] = (
    CityMap("atlanta", "ATLANTA", "atlanta-daily-weather", "KATL", "KATL", "Atlanta"),
    CityMap("austin", "AUSTIN", "austin-daily-weather", "KAUS", "KAUS", "Austin"),
    CityMap("chicago", "CHICAGO", "chicago-daily-weather", "KMDW", "KORD", "Chicago"),
    CityMap("dallas", "DALLAS", "dallas-daily-weather", "KDFW", "KDAL", "Dallas"),
    CityMap("denver", "DENVER", "denver-daily-weather", "KDEN", "KBKF", "Denver"),
    CityMap("houston", "HOUSTON", "houston-daily-weather", "KHOU", "KHOU", "Houston"),
    CityMap("los-angeles", "LOSANGELES", "los-angeles-daily-weather", "KLAX", "KLAX", "Los Angeles"),
    CityMap("miami", "MIAMI", "miami-daily-weather", "KMIA", "KMIA", "Miami"),
    CityMap("nyc", "NYC", "nyc-daily-weather", "KNYC", "KLGA", "New York"),
    CityMap("san-francisco", "SANFRANCISCO", "san-francisco-daily-weather", "KSFO", "KSFO", "San Francisco"),
    CityMap("seattle", "SEATTLE", "seattle-daily-weather", "KSEA", "KSEA", "Seattle"),
)

MAP_BY_SLUG = {c.slug: c for c in CITY_MAPS}
MAP_BY_KEY = {c.kalshi_key: c for c in CITY_MAPS}

# Villes Kalshi avec beaucoup de captures HIGH, sans série Polymarket
# quotidienne trouvée le 12 sept. 2026 (recherche slug + série).
KALSHI_HIGH_WITHOUT_PM = (
    "BOSTON", "LASVEGAS", "MINNEAPOLIS", "PHOENIX", "SANANTONIO",
)


def parse_pm_bin(title: str) -> Optional[tuple[Optional[int], Optional[int]]]:
    """Lit groupItemTitle / question Polymarket → (lower, upper) inclusifs."""
    s = (title or "").strip()
    if not s:
        return None
    m = _PM_BELOW.search(s)
    if m:
        return (None, int(m.group(1)))
    m = _PM_ABOVE.search(s)
    if m:
        return (int(m.group(1)), None)
    m = _PM_RANGE.search(s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return None


def bin_key(lower, upper) -> tuple[Optional[int], Optional[int]]:
    lo = None if lower is None else int(lower)
    hi = None if upper is None else int(upper)
    return (lo, hi)


def same_bin(kalshi_lo, kalshi_hi, pm_lo, pm_hi) -> bool:
    return bin_key(kalshi_lo, kalshi_hi) == bin_key(pm_lo, pm_hi)


def pm_site_icao(text: str) -> Optional[str]:
    """ICAO annoncé dans le texte de résolution Polymarket (site=klga)."""
    m = _SITE_RE.search(text or "")
    if not m:
        return None
    return m.group(1).upper()


def yes_token_id(market: dict) -> Optional[str]:
    raw = market.get("clobTokenIds")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return None
    if isinstance(raw, list) and raw:
        return str(raw[0])
    return None


def event_target_date(event: dict) -> Optional[date]:
    raw = event.get("eventDate") or ""
    if raw:
        try:
            return date.fromisoformat(str(raw)[:10])
        except ValueError:
            return None
    end = event.get("endDate") or ""
    if end:
        try:
            return datetime.fromisoformat(end.replace("Z", "+00:00")).date()
        except ValueError:
            return None
    return None


def snapshot_unix(snapshot_at: str) -> Optional[int]:
    """'20260910T202833Z' → secondes UTC. None si le format est inconnu."""
    s = (snapshot_at or "").strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return int(datetime.strptime(s, fmt).replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
    return None


def price_at_or_before(
    history: Sequence[dict],
    cutoff_ts: int,
) -> Optional[tuple[float, int]]:
    """Dernier point CLOB dont l'horodatage est ≤ cutoff. Rien n'est interpolé."""
    best_p: Optional[float] = None
    best_t: Optional[int] = None
    for pt in history:
        if not isinstance(pt, dict):
            continue
        t, p = pt.get("t"), pt.get("p")
        if t is None or p is None:
            continue
        try:
            ts = int(t)
            price = float(p)
        except (TypeError, ValueError):
            continue
        if ts > cutoff_ts:
            continue
        if not (0.0 <= price <= 1.0):
            continue
        if best_t is None or ts > best_t:
            best_p, best_t = price, ts
    if best_p is None or best_t is None:
        return None
    return (best_p, best_t)


def two_sided(bid, ask) -> bool:
    if bid is None or ask is None:
        return False
    try:
        b, a = float(bid), float(ask)
    except (TypeError, ValueError):
        return False
    return a > 0 and a >= b


def cache_key(*parts: str) -> str:
    raw = "__".join(parts)
    return _SAFE_RE.sub("_", raw)


def icao_for_kalshi_key(key: str) -> Optional[str]:
    mapped = MAP_BY_KEY.get(key)
    if mapped:
        return mapped.kalshi_icao
    return CITY_TO_ICAO.get(key)


def outcome_from_cli(high_f: float, lower, upper) -> bool:
    lo = None if lower is None else int(lower)
    hi = None if upper is None else int(upper)
    return Bin(lo, hi).contains(high_f)


def mean_abs_gap(pairs: Iterable[tuple[float, float]]) -> Optional[float]:
    diffs = [abs(float(a) - float(b)) for a, b in pairs]
    if not diffs:
        return None
    return sum(diffs) / len(diffs)


def blend_avg(p_k: float, p_p: float) -> float:
    return 0.5 * (float(p_k) + float(p_p))


def days_won(rows: Sequence[dict], a: str, b: str, date_key: str = "target") -> dict:
    """Brier moyen par date : combien de jours a bat b (strict)."""
    by: dict[str, list[dict]] = {}
    for r in rows:
        if r.get(a) is None or r.get(b) is None:
            continue
        by.setdefault(str(r[date_key]), []).append(r)
    wins = losses = ties = 0
    for rs in by.values():
        ba = brier_mean([r[a] for r in rs], [1.0 if r["outcome"] else 0.0 for r in rs])
        bb = brier_mean([r[b] for r in rs], [1.0 if r["outcome"] else 0.0 for r in rs])
        if ba is None or bb is None:
            continue
        if ba < bb:
            wins += 1
        elif ba > bb:
            losses += 1
        else:
            ties += 1
    n = wins + losses
    p = None
    if n:
        p = sum(__import__("math").comb(n, i) for i in range(wins, n + 1)) / (2 ** n)
    return {
        "dates": len(by),
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "n_decisive": n,
        "p_one_sided": p,
    }


def slice_metrics(rows: Sequence[dict]) -> dict:
    ready = [r for r in rows if r.get("p_kalshi") is not None and r.get("p_pm") is not None]
    ys = [1.0 if r["outcome"] else 0.0 for r in ready]
    p_k = [r["p_kalshi"] for r in ready]
    p_p = [r["p_pm"] for r in ready]
    p_avg = [r["p_avg"] for r in ready if r.get("p_avg") is not None]
    y_avg = [1.0 if r["outcome"] else 0.0 for r in ready if r.get("p_avg") is not None]
    p_stack = [r["p_stack"] for r in ready if r.get("p_stack") is not None]
    y_stack = [1.0 if r["outcome"] else 0.0 for r in ready if r.get("p_stack") is not None]
    return {
        "n_bins": len(ready),
        "n_city_days": len({(r["kalshi_key"], r["target"]) for r in ready}),
        "n_dates": len({r["target"] for r in ready}),
        "n_cities": len({r["kalshi_key"] for r in ready}),
        "mean_abs_gap": mean_abs_gap(zip(p_k, p_p)),
        "brier_kalshi": brier_mean(p_k, ys),
        "brier_pm": brier_mean(p_p, ys),
        "brier_avg": brier_mean(p_avg, y_avg),
        "brier_stack": brier_mean(p_stack, y_stack),
        "avg_vs_kalshi": days_won(ready, "p_avg", "p_kalshi"),
        "pm_vs_kalshi": days_won(ready, "p_pm", "p_kalshi"),
        "stack_vs_kalshi": days_won(
            [r for r in ready if r.get("p_stack") is not None],
            "p_stack", "p_kalshi",
        ),
        "cities": sorted({r["kalshi_key"] for r in ready}),
    }


def attach_blends(rows: list[dict], weight: Optional[float]) -> None:
    for r in rows:
        if r.get("p_kalshi") is None or r.get("p_pm") is None:
            r["p_avg"] = None
            r["p_stack"] = None
            continue
        r["p_avg"] = blend_avg(r["p_kalshi"], r["p_pm"])
        r["p_stack"] = (
            apply_stack(r["p_kalshi"], r["p_pm"], weight) if weight is not None else None
        )


def fit_gap_weight(train_rows: Sequence[dict]) -> Optional[float]:
    ready = [r for r in train_rows if r.get("p_kalshi") is not None and r.get("p_pm") is not None]
    return residual_weight(
        [r["p_pm"] for r in ready],
        [r["p_kalshi"] for r in ready],
        [1.0 if r["outcome"] else 0.0 for r in ready],
    )
