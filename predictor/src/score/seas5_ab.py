"""SEAS5 Phase 2 : trois A/B séparés, hors ligne, vs climato.

A) SEAS5 vs climato → USDM (Midwest, Southwest)
B) SEAS5 vs climato → SPEI-6 (Méditerranée, Inde, US)
C) SEAS5 vs climato → CHIRPS (Méditerranée, Inde)

Gate : N ≥ 10 saisons avant de conclure ; BSS > 0,05 vs climato
pour « ça aide ». Sinon bloquée / ça n'aide pas, avec le N mesuré.
Aucun score n'est inventé. Le champion Kalshi n'est pas touché.
"""
from __future__ import annotations

import statistics
from pathlib import Path
from typing import Any, Optional

from src.config import DATA_DIR
from src.forecast.seas5_offline import (
    FORECAST_NAME, SEAS5_DIR, collapse_shortest_lead, find_forecast_csv,
    find_pairs_csv, forecast_status, inventory_hint, load_forecast_csv,
    load_monthly_truth_csv, load_pairs_csv, load_seasonal_truth_csv,
    load_usdm_weeks_json,
)
from src.truth.synthetic_bins import brier

BSS_GATE = 0.05
MIN_SEASONS_FOR_GATE = 10

AB_SPECS: dict[str, dict[str, Any]] = {
    "A": {
        "id": "A",
        "title": "SEAS5 vs climato, vérité USDM",
        "truth_name": "US Drought Monitor",
        "event_label": "moyenne D2+ catégorielle ≥ 30 % (Phase B §3.2, PR 240)",
        "regions": ("midwest", "southwest"),
        "region_labels": {
            "midwest": "Midwest",
            "southwest": "Southwest",
        },
    },
    "B": {
        "id": "B",
        "title": "SEAS5 vs climato, vérité SPEI-6",
        "truth_name": "SPEI",
        "event_label": "SPEI-6 saisonnier moyen ≤ -1,5 (WMO / Phase B, PR 243)",
        "regions": ("med", "india", "us"),
        "region_labels": {
            "med": "MED",
            "india": "India",
            "us": "US",
        },
    },
    "C": {
        "id": "C",
        "title": "SEAS5 vs climato, vérité CHIRPS",
        "truth_name": "CHIRPS pluie",
        "event_label": (
            "pluie saisonnière sous la moyenne climato leave-one-out "
            "du même type de saison (pas un seuil de sécheresse nommé)"
        ),
        "regions": ("med", "india"),
        "region_labels": {
            "med": "MED",
            "india": "India",
        },
        # Headline is MED only. Never pool MED + India for BSS / N / verdict.
        "headline_region": "med",
    },
}

SPEI_DRY_THRESHOLD = -1.5


def _round(value: Optional[float], nd: int = 4) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), nd)


def leave_one_out_climato(events: list[bool]) -> list[float]:
    n = len(events)
    if n < 2:
        return []
    total = sum(1.0 if e else 0.0 for e in events)
    return [(total - (1.0 if e else 0.0)) / (n - 1) for e in events]


def leave_one_out_mean(values: list[float]) -> list[float]:
    n = len(values)
    if n < 2:
        return []
    total = sum(values)
    return [(total - v) / (n - 1) for v in values]


def brier_skill_score(bs_forecast: float, bs_climato: float) -> Optional[float]:
    """BSS = 1 - BS_fc / BS_clim. None when climato BS is 0 (do not invent)."""
    if bs_climato == 0:
        return None
    return 1.0 - bs_forecast / bs_climato


def skill_block(events: list[bool], p_forecast: list[float]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "n": len(events),
        "base_rate": _round(statistics.fmean(1.0 if e else 0.0 for e in events)) if events else None,
        "brier_forecast": None,
        "brier_climato": None,
        "bss": None,
    }
    if len(events) < 2:
        return out
    p_cl = leave_one_out_climato(events)
    bs_fc = statistics.fmean(brier(a, b) for a, b in zip(p_forecast, events))
    bs_cl = statistics.fmean(brier(a, b) for a, b in zip(p_cl, events))
    out["brier_forecast"] = _round(bs_fc)
    out["brier_climato"] = _round(bs_cl)
    out["bss"] = _round(brier_skill_score(bs_fc, bs_cl))
    return out


def region_verdict(n: int, bss: Optional[float]) -> str:
    if n < MIN_SEASONS_FOR_GATE:
        return "bloquée"
    if bss is None:
        return "bloquée"
    if bss > BSS_GATE:
        return "testée, ça aide"
    return "testée, ça n'aide pas"


def ab_verdict(
    region_blocks: dict[str, dict[str, Any]],
    headline_region: Optional[str] = None,
) -> str:
    if headline_region:
        block = region_blocks.get(headline_region) or {}
        return region_verdict(int(block.get("n") or 0), block.get("bss"))
    scored = [b for b in region_blocks.values() if b.get("n", 0) > 0 and not b.get("blocker")]
    if not scored:
        return "bloquée"
    verdicts = [region_verdict(int(b["n"]), b.get("bss")) for b in scored]
    if any(v == "testée, ça aide" for v in verdicts):
        return "testée, ça aide"
    if any(v == "testée, ça n'aide pas" for v in verdicts):
        return "testée, ça n'aide pas"
    return "bloquée"


def _monthly_to_seasons(
    rows: list[dict[str, Any]],
    event_from_mean=None,
) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str, int], list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["region"], row["season"], row["season_year"])
        buckets.setdefault(key, []).append(row)
    out = []
    for (region, season, year), group in sorted(buckets.items(), key=lambda kv: (kv[0][0], kv[0][2], kv[0][1])):
        if len(group) < 3:
            continue
        months = {r["valid_month"] if "valid_month" in r else r["month"] for r in group}
        if len(months) < 3:
            continue
        values = [float(r["value"] if "value" in r else r["tp_mean_mm"]) for r in group]
        mean = statistics.fmean(values)
        anoms = [r.get("tp_anom_mm") for r in group]
        anom_mean = None
        if all(a is not None for a in anoms):
            anom_mean = statistics.fmean(float(a) for a in anoms)
        events = [r.get("event") for r in group]
        event = None
        if all(e is not None for e in events):
            event = bool(statistics.fmean(1.0 if e else 0.0 for e in events) >= 0.5)
        if event is None and event_from_mean is not None:
            event = bool(event_from_mean(mean))
        out.append({
            "region": region,
            "season": season,
            "year": year,
            "n_months": len(group),
            "mean": mean,
            "anom_mean": anom_mean,
            "event": event,
        })
    return out


def _p_dry_from_forecast_stable(seasons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Same rule as PR 240: dry if below LOO mean / negative anomaly."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in seasons:
        groups.setdefault((row["region"], row["season"]), []).append(row)
    out: list[dict[str, Any]] = []
    for group in groups.values():
        means = [float(r["mean"]) for r in group]
        loo = leave_one_out_mean(means) if len(means) >= 2 else []
        for i, row in enumerate(group):
            copy = dict(row)
            if row.get("anom_mean") is not None:
                copy["p_forecast_dry"] = 1.0 if row["anom_mean"] < 0 else 0.0
            elif loo:
                copy["p_forecast_dry"] = 1.0 if row["mean"] < loo[i] else 0.0
            else:
                copy["p_forecast_dry"] = None
            out.append(copy)
    return sorted(out, key=lambda r: (r["region"], r["year"], r["season"]))


def _chirps_events(seasons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in seasons:
        groups.setdefault((row["region"], row["season"]), []).append(row)
    out: list[dict[str, Any]] = []
    for group in groups.values():
        values = [float(r["mean"]) for r in group]
        loo = leave_one_out_mean(values) if len(values) >= 2 else []
        for i, row in enumerate(group):
            copy = dict(row)
            if row.get("event") is not None:
                copy["event"] = bool(row["event"])
            elif loo:
                copy["event"] = bool(row["mean"] < loo[i])
            else:
                copy["event"] = None
            out.append(copy)
    return out


def _join_seasons(
    forecast: list[dict[str, Any]],
    truth: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fc = {(r["region"], r["year"], r["season"]): r for r in forecast}
    out = []
    for row in truth:
        key = (row["region"], row["year"], row["season"])
        left = fc.get(key)
        if left is None:
            continue
        if left.get("p_forecast_dry") is None or row.get("event") is None:
            continue
        out.append({
            "region": row["region"],
            "year": row["year"],
            "season": row["season"],
            "p_forecast_dry": float(left["p_forecast_dry"]),
            "event": bool(row["event"]),
            "forecast_mean": left.get("mean"),
            "truth_mean": row.get("mean", row.get("value")),
        })
    return out


def _score_joined(joined: list[dict[str, Any]], regions: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    by_region: dict[str, dict[str, Any]] = {}
    for region in regions:
        rows = [r for r in joined if r["region"] == region]
        block = skill_block(
            [r["event"] for r in rows],
            [r["p_forecast_dry"] for r in rows],
        )
        block["verdict"] = region_verdict(block["n"], block["bss"])
        block["gate_n_ge_10"] = block["n"] >= MIN_SEASONS_FOR_GATE
        block["gate_bss_gt_0_05"] = bool(
            block["bss"] is not None
            and block["bss"] > BSS_GATE
            and block["n"] >= MIN_SEASONS_FOR_GATE
        )
        block["seasons"] = rows
        by_region[region] = block
    return by_region


def _blocker(message: str, regions: tuple[str, ...]) -> dict[str, Any]:
    empty = {}
    for region in regions:
        empty[region] = {
            "n": 0,
            "base_rate": None,
            "brier_forecast": None,
            "brier_climato": None,
            "bss": None,
            "verdict": "bloquée",
            "gate_n_ge_10": False,
            "gate_bss_gt_0_05": False,
            "blocker": message,
            "seasons": [],
        }
    return {
        "blocker": message,
        "n_seasons_scored": 0,
        "bss": None,
        "brier_forecast": None,
        "brier_climato": None,
        "gate_n_ge_10": False,
        "gate_bss_gt_0_05": False,
        "verdict": "bloquée",
        "by_region": empty,
    }


def _finish_ab(spec: dict[str, Any], by_region: dict[str, dict[str, Any]], extra: dict[str, Any]) -> dict[str, Any]:
    headline_key = spec.get("headline_region")
    headline = None
    if headline_key:
        headline = by_region.get(headline_key) or {}
    else:
        for region in spec["regions"]:
            block = by_region.get(region) or {}
            if block.get("n"):
                headline = block
                break
    headline = headline or {}
    verdict = ab_verdict(by_region, headline_region=headline_key)
    payload = {
        "id": spec["id"],
        "title": spec["title"],
        "forecast_name": FORECAST_NAME,
        "truth_name": spec["truth_name"],
        "event": spec["event_label"],
        "blocker": headline.get("blocker"),
        "headline_region": headline_key,
        "n_seasons_scored": int(headline.get("n") or 0),
        "brier_forecast": headline.get("brier_forecast"),
        "brier_climato": headline.get("brier_climato"),
        "bss": headline.get("bss"),
        "gate_n_ge_10": bool(headline.get("gate_n_ge_10")),
        "gate_bss_gt_0_05": bool(headline.get("gate_bss_gt_0_05")),
        "verdict": verdict,
        "by_region": by_region,
        "champion_switched": False,
        "cds_called": False,
        "pooled": False,
    }
    payload.update(extra)
    return payload


def _load_usdm_truth(data_dir: Path) -> tuple[list[dict[str, Any]], Optional[str]]:
    seasons: list[dict[str, Any]] = []
    csv_path = data_dir / "truth" / "usdm" / "usdm_seasons.csv"
    if csv_path.is_file() and csv_path.stat().st_size > 0:
        seasons = load_seasonal_truth_csv(
            csv_path, "event_d2_plus_ge_30", value_key="d2_plus_mean"
        )
        seasons = [r for r in seasons if r["region"] in {"midwest", "southwest"}]
        if seasons:
            return seasons, None
    for region, names in (
        ("midwest", ("weeks_Midwest_cat.json", "weeks_midwest_cat.json")),
        ("southwest", ("weeks_Southwest_cat.json", "weeks_southwest_cat.json")),
    ):
        for name in names:
            path = data_dir / "truth" / "usdm" / name
            if path.is_file() and path.stat().st_size > 0:
                seasons.extend(load_usdm_weeks_json(path, region))
                break
    if seasons:
        return seasons, None
    inventory = data_dir / "truth" / "usdm" / "usdm_counts.json"
    if inventory_hint(inventory):
        return [], (
            "Inventaire USDM présent (PR 240), série saisonnière absente "
            "(usdm_seasons.csv ou weeks_*_cat.json). Pas de score inventé."
        )
    return [], (
        "Vérité USDM absente sous data/truth/usdm/ "
        "(usdm_seasons.csv ou weeks_*_cat.json). Pas de score inventé."
    )


def _load_spei_truth(data_dir: Path) -> tuple[list[dict[str, Any]], Optional[str]]:
    monthly = data_dir / "truth" / "spei" / "spei6_monthly.csv"
    seasonal = data_dir / "truth" / "spei" / "spei6_seasons.csv"
    if monthly.is_file() and monthly.stat().st_size > 0:
        rows = load_monthly_truth_csv(
            monthly, "spei6_mean", event_key="event_spei6_le_minus_1_5"
        )
        seasons = _monthly_to_seasons(
            rows, event_from_mean=lambda m: m <= SPEI_DRY_THRESHOLD
        )
        if seasons:
            return seasons, None
    if seasonal.is_file() and seasonal.stat().st_size > 0:
        rows = load_seasonal_truth_csv(
            seasonal, "event_spei6_le_minus_1_5", value_key="spei6_mean"
        )
        if rows:
            return rows, None
    inventory = data_dir / "truth" / "spei" / "spei_counts.json"
    if inventory_hint(inventory):
        return [], (
            "Inventaire SPEI présent (PR 243), série mensuelle absente "
            "(spei6_monthly.csv ou spei6_seasons.csv). Pas de score inventé."
        )
    return [], (
        "Vérité SPEI-6 absente sous data/truth/spei/ "
        "(spei6_monthly.csv ou spei6_seasons.csv). Pas de score inventé."
    )


def _load_chirps_truth(data_dir: Path) -> tuple[list[dict[str, Any]], Optional[str]]:
    monthly = data_dir / "truth" / "chirps" / "chirps_monthly.csv"
    seasonal = data_dir / "truth" / "chirps" / "chirps_seasons.csv"
    if monthly.is_file() and monthly.stat().st_size > 0:
        rows = load_monthly_truth_csv(monthly, "tp_mean_mm")
        seasons = _monthly_to_seasons(rows)
        seasons = _chirps_events(seasons)
        if seasons:
            return seasons, None
    if seasonal.is_file() and seasonal.stat().st_size > 0:
        rows = load_seasonal_truth_csv(
            seasonal, "event_below_climato", value_key="tp_mean_mm"
        )
        if rows:
            return rows, None
    inventory = data_dir / "truth" / "chirps" / "chirps_counts.json"
    if inventory_hint(inventory):
        return [], (
            "Inventaire CHIRPS présent (PR 244), série mensuelle absente "
            "(chirps_monthly.csv ou chirps_seasons.csv). Pas de score inventé."
        )
    return [], (
        "Vérité CHIRPS absente sous data/truth/chirps/ "
        "(chirps_monthly.csv ou chirps_seasons.csv). Pas de score inventé."
    )


def _forecast_seasons(
    directory: Path,
    init_month: Optional[int],
    min_lead: int,
    max_lead: int,
    include_shared: bool = True,
) -> tuple[list[dict[str, Any]], Optional[str], Optional[Path]]:
    path = find_forecast_csv(directory, include_shared=include_shared)
    if path is None:
        return [], None, None
    rows = load_forecast_csv(path)
    if init_month is not None:
        rows = [r for r in rows if r["init_month"] == init_month]
    rows = [r for r in rows if min_lead <= r["lead_month"] <= max_lead]
    collapsed = collapse_shortest_lead(rows)
    monthly = []
    for row in collapsed:
        monthly.append({
            "region": row["region"],
            "valid_year": row["valid_year"],
            "valid_month": row["valid_month"],
            "month": row["valid_month"],
            "season": row["season"],
            "season_year": row["season_year"],
            "value": row["tp_mean_mm"],
            "tp_mean_mm": row["tp_mean_mm"],
            "tp_anom_mm": row["tp_anom_mm"],
        })
    seasons = _monthly_to_seasons(monthly)
    seasons = _p_dry_from_forecast_stable(seasons)
    return seasons, None, path


def _blocked_ab(spec: dict[str, Any], message: str) -> dict[str, Any]:
    payload = _blocker(message, spec["regions"])
    payload.update({
        "id": spec["id"],
        "title": spec["title"],
        "forecast_name": FORECAST_NAME,
        "truth_name": spec["truth_name"],
        "event": spec["event_label"],
        "champion_switched": False,
        "cds_called": False,
    })
    return payload


def _score_from_inputs(
    spec: dict[str, Any],
    forecast_dir: Path,
    pairs_key: str,
    truth_rows: list[dict[str, Any]],
    truth_reason: Optional[str],
    init_month: Optional[int],
    min_lead: int,
    max_lead: int,
    include_shared: bool = True,
) -> dict[str, Any]:
    pairs = find_pairs_csv(pairs_key, forecast_dir)
    fc_seasons, _, fc_path = _forecast_seasons(
        forecast_dir, init_month, min_lead, max_lead,
        include_shared=include_shared,
    )
    if pairs is not None and not fc_seasons:
        joined = load_pairs_csv(pairs)
        by_region = _score_joined(joined, spec["regions"])
        return _finish_ab(spec, by_region, {
            "forecast_path": str(pairs),
            "truth_path": str(pairs),
            "input": "pairs",
        })
    if fc_path is None:
        status = forecast_status(forecast_dir, include_shared=include_shared)
        return _blocked_ab(spec, status["reason"] or "CSV SEAS5 absent.")
    if not fc_seasons:
        return _blocked_ab(
            spec,
            "CSV SEAS5 lu, zéro saison complète de 3 mois. Pas de score inventé.",
        )
    if truth_reason:
        return _blocked_ab(spec, truth_reason)
    joined = _join_seasons(fc_seasons, truth_rows)
    if not joined:
        return _blocked_ab(
            spec,
            "Prévision et vérité ne se recouvrent sur aucune saison complète. "
            "Pas de score inventé.",
        )
    by_region = _score_joined(joined, spec["regions"])
    return _finish_ab(spec, by_region, {
        "forecast_path": str(fc_path),
        "input": "regional_monthly",
    })


def score_ab_a(
    data_dir: Path,
    forecast_dir: Path,
    init_month: Optional[int] = None,
    min_lead: int = 1,
    max_lead: int = 7,
    include_shared: bool = True,
) -> dict[str, Any]:
    truth, truth_reason = _load_usdm_truth(data_dir)
    return _score_from_inputs(
        AB_SPECS["A"], forecast_dir, "usdm", truth, truth_reason,
        init_month, min_lead, max_lead, include_shared=include_shared,
    )


def score_ab_b(
    data_dir: Path,
    forecast_dir: Path,
    init_month: Optional[int] = None,
    min_lead: int = 1,
    max_lead: int = 7,
    include_shared: bool = True,
) -> dict[str, Any]:
    truth, truth_reason = _load_spei_truth(data_dir)
    return _score_from_inputs(
        AB_SPECS["B"], forecast_dir, "spei", truth, truth_reason,
        init_month, min_lead, max_lead, include_shared=include_shared,
    )


def score_ab_c(
    data_dir: Path,
    forecast_dir: Path,
    init_month: Optional[int] = None,
    min_lead: int = 1,
    max_lead: int = 7,
    include_shared: bool = True,
) -> dict[str, Any]:
    truth, truth_reason = _load_chirps_truth(data_dir)
    return _score_from_inputs(
        AB_SPECS["C"], forecast_dir, "chirps", truth, truth_reason,
        init_month, min_lead, max_lead, include_shared=include_shared,
    )


def _region_verdict_or_untested(block: dict[str, Any]) -> str:
    verdict = block.get("verdict")
    if verdict in {"testée, ça aide", "testée, ça n'aide pas"}:
        return verdict
    if int(block.get("n") or 0) > 0:
        return "bloquée"
    return "cible Tier 1 (pas encore testée)"


def catalogue_verdicts(abs_out: dict[str, dict[str, Any]]) -> dict[str, str]:
    """C headline is MED only. India and MED are never pooled."""
    c_regions = abs_out["C"].get("by_region") or {}
    c_med = c_regions.get("med") or {}
    c_india = c_regions.get("india") or {}
    seas5 = "bloquée"
    if c_med.get("verdict") == "testée, ça aide":
        seas5 = "testée, ça aide (CHIRPS MED seulement)"
    elif abs_out["A"]["verdict"] == "testée, ça aide":
        seas5 = "testée, ça aide"
    elif abs_out["A"]["verdict"] == "testée, ça n'aide pas":
        seas5 = "testée, ça n'aide pas"
    elif c_india.get("verdict") == "testée, ça n'aide pas":
        seas5 = "testée, ça n'aide pas"
    return {
        FORECAST_NAME: seas5,
        "US Drought Monitor": "testée, ça aide",
        "SPEI": "testée, ça aide",
        "CHIRPS pluie": "testée, ça aide",
        "Sécheresse US": abs_out["A"]["verdict"],
        "Sécheresse Méditerranée": _region_verdict_or_untested(c_med),
        "Sécheresse Inde": _region_verdict_or_untested(c_india),
        "C3S multi-modèle": "pas encore testée",
        "NMME": "bloquée",
        "Open-Meteo Seasonal": "bloquée",
    }


def score_all(
    data_dir: Path = DATA_DIR,
    forecast_dir: Path = SEAS5_DIR,
    init_month: Optional[int] = None,
    min_lead: int = 1,
    max_lead: int = 7,
    include_shared: bool = True,
) -> dict[str, Any]:
    status = forecast_status(forecast_dir, include_shared=include_shared)
    a = score_ab_a(
        data_dir, forecast_dir, init_month, min_lead, max_lead,
        include_shared=include_shared,
    )
    b = score_ab_b(
        data_dir, forecast_dir, init_month, min_lead, max_lead,
        include_shared=include_shared,
    )
    c = score_ab_c(
        data_dir, forecast_dir, init_month, min_lead, max_lead,
        include_shared=include_shared,
    )
    abs_out = {"A": a, "B": b, "C": c}
    return {
        "forecast_name": FORECAST_NAME,
        "as_of_mode": "offline",
        "cds_called": False,
        "cdsapi_imported": False,
        "champion_switched": False,
        "real_money": False,
        "bss_invented": False,
        "gate": {
            "bss_gt": BSS_GATE,
            "min_seasons": MIN_SEASONS_FOR_GATE,
        },
        "forecast": status,
        "ab": abs_out,
        "verdicts": catalogue_verdicts(abs_out),
    }
