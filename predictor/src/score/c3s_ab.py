"""C3S multi-modèle : trois A/B séparés, hors ligne, mêmes règles que PR 246.

A) C3S multi-modèle vs climato → USDM (Midwest, Southwest)
B) C3S multi-modèle vs climato → SPEI-6 (Méditerranée, Inde, US)
C) C3S multi-modèle vs climato → CHIRPS (Méditerranée, Inde)

La headline de C est MED seulement. India reste à part. On ne pool pas.

Gate : N ≥ 10 saisons ; BSS > 0,05 vs climato pour « ça aide ».
Si le CSV manque, ou si le BSS est indéfini (Brier climato = 0) :
bloquée, aucun score inventé.

ECMWF système 51 (SEAS5) est scoré seul à partir des lignes de ce CSV,
pour voir si le mélange le bat. S'il manque, c'est un trou. On ne
recopie pas la mesure PR 246 dans le BSS de ce run, et on ne lit pas
le CSV SEAS5 pour le remplir.

Le champion Kalshi n'est pas touché. CDS n'est pas appelé.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from src.config import DATA_DIR
from src.forecast.c3s_offline import (
    ECMWF_51,
    FORECAST_NAME,
    SHARED_FORECAST_CSV,
    C3S_DIR,
    aggregate_equal_weight,
    empty_inventory,
    filter_window,
    forecast_status,
    inventory,
    load_c3s_csv,
)
from src.forecast.seas5_offline import collapse_shortest_lead
from src.score.seas5_ab import (
    AB_SPECS,
    BSS_GATE,
    MIN_SEASONS_FOR_GATE,
    _blocked_ab,
    _finish_ab,
    _join_seasons,
    _load_chirps_truth,
    _load_spei_truth,
    _load_usdm_truth,
    _monthly_to_seasons,
    _p_dry_from_forecast_stable,
    _region_verdict_or_untested,
    _score_joined,
)

# Mesure déjà publiée (PR 246, commit aa8d61f). Ce bloc n'est pas un
# score de ce run. Le BSS SPEI reste vide : Brier climato = 0.
PUBLISHED_SEAS5_BASELINE: dict[str, Any] = {
    "label": "SEAS5",
    "centre": {"origin": "ecmwf", "system": 51},
    "source": "PR 246",
    "commit": "aa8d61f",
    "computed": False,
    "pooled": False,
    "headline_region": "med",
    "note": (
        "Mesure déjà publiée. Ce bloc n'est pas recalculé ici. "
        "Il ne comble pas un trou. Le BSS SPEI n'existe pas "
        "(Brier climato = 0 au seuil ≤ -1,5 après moyenne spatiale)."
    ),
    "A": {
        "midwest": {
            "n": 97,
            "brier_forecast": 0.5464,
            "brier_climato": 0.0306,
            "bss": -16.8565,
            "verdict": "testée, ça n'aide pas",
        },
        "southwest": {
            "n": 97,
            "brier_forecast": 0.5052,
            "brier_climato": 0.2546,
            "bss": -0.9844,
            "verdict": "testée, ça n'aide pas",
        },
    },
    "B": {
        "med": {
            "n": 123,
            "brier_forecast": 0.5285,
            "brier_climato": 0.0,
            "bss": None,
            "verdict": "bloquée",
        },
        "india": {
            "n": 123,
            "brier_forecast": 0.5122,
            "brier_climato": 0.0,
            "bss": None,
            "verdict": "bloquée",
        },
        "us": {
            "n": 0,
            "brier_forecast": None,
            "brier_climato": None,
            "bss": None,
            "verdict": "bloquée",
        },
    },
    "C": {
        "med": {
            "n": 125,
            "brier_forecast": 0.24,
            "brier_climato": 0.254,
            "bss": 0.0552,
            "verdict": "testée, ça aide",
            "headline": True,
        },
        "india": {
            "n": 125,
            "brier_forecast": 0.272,
            "brier_climato": 0.254,
            "bss": -0.0707,
            "verdict": "testée, ça n'aide pas",
            "headline": False,
        },
    },
}

_TRUTH_LOADERS = {
    "A": _load_usdm_truth,
    "B": _load_spei_truth,
    "C": _load_chirps_truth,
}


def c3s_specs() -> dict[str, dict[str, Any]]:
    """Same events and regions as PR 246. Titles name this forecast."""
    specs: dict[str, dict[str, Any]] = {}
    for key, spec in AB_SPECS.items():
        item = {
            "id": spec["id"],
            "title": spec["title"].replace("SEAS5", FORECAST_NAME),
            "truth_name": spec["truth_name"],
            "event_label": spec["event_label"],
            "regions": spec["regions"],
            "region_labels": dict(spec["region_labels"]),
        }
        if spec.get("headline_region"):
            item["headline_region"] = spec["headline_region"]
        specs[key] = item
    return specs


def _mark_headline(spec: dict[str, Any], block: dict[str, Any]) -> None:
    headline = spec.get("headline_region")
    for region, row in (block.get("by_region") or {}).items():
        row["headline"] = bool(headline and region == headline)
    block["headline_region"] = headline
    block["pooled"] = False
    block["forecast_name"] = FORECAST_NAME


def _all_blocked(
    specs: dict[str, dict[str, Any]],
    message: str,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, spec in specs.items():
        block = _blocked_ab(spec, message)
        _mark_headline(spec, block)
        out[key] = block
    return out


def seasons_from_monthly(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """PR 246: shortest lead, then a season only if its 3 months exist."""
    ordered = sorted(
        rows,
        key=lambda r: (
            r["region"],
            r["valid_year"],
            r["valid_month"],
            r["lead_month"],
            r.get("init_year", 0),
            r.get("init_month", 0),
        ),
    )
    collapsed = collapse_shortest_lead(ordered)
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
            "tp_anom_mm": row.get("tp_anom_mm"),
        })
    seasons = _monthly_to_seasons(monthly)
    return _p_dry_from_forecast_stable(seasons)


def _score_seasons(
    seasons: list[dict[str, Any]],
    data_dir: Path,
    specs: dict[str, dict[str, Any]],
    forecast_path: str,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, spec in specs.items():
        truth, reason = _TRUTH_LOADERS[key](data_dir)
        if reason:
            block = _blocked_ab(spec, reason)
        else:
            joined = _join_seasons(seasons, truth)
            if not joined:
                block = _blocked_ab(
                    spec,
                    "Prévision et vérité ne se recouvrent sur aucune "
                    "saison complète. Pas de score inventé.",
                )
            else:
                by_region = _score_joined(joined, spec["regions"])
                block = _finish_ab(spec, by_region, {
                    "forecast_path": forecast_path,
                    "input": "c3s_monthly",
                })
        _mark_headline(spec, block)
        out[key] = block
    return out


def _product_verdict(abs_out: dict[str, dict[str, Any]]) -> str:
    """Headline is CHIRPS MED. India is never pooled into it."""
    c_regions = abs_out["C"].get("by_region") or {}
    c_med = c_regions.get("med") or {}
    c_india = c_regions.get("india") or {}
    if c_med.get("verdict") == "testée, ça aide":
        return "testée, ça aide (CHIRPS MED seulement)"
    if abs_out["A"]["verdict"] == "testée, ça aide":
        return "testée, ça aide"
    if abs_out["A"]["verdict"] == "testée, ça n'aide pas":
        return "testée, ça n'aide pas"
    if c_india.get("verdict") == "testée, ça n'aide pas":
        return "testée, ça n'aide pas"
    return "bloquée"


def catalogue_verdicts(
    multi: dict[str, dict[str, Any]],
    ecmwf: dict[str, dict[str, Any]],
) -> dict[str, str]:
    c_regions = multi["C"].get("by_region") or {}
    c_med = c_regions.get("med") or {}
    c_india = c_regions.get("india") or {}
    return {
        FORECAST_NAME: _product_verdict(multi),
        "ECMWF-51": _product_verdict(ecmwf),
        # Catalogue déjà publié. Pas un BSS recalculé par ce run.
        "SEAS5": "testée, ça aide (CHIRPS MED seulement)",
        "US Drought Monitor": "testée, ça aide",
        "SPEI": "testée, ça aide",
        "CHIRPS pluie": "testée, ça aide",
        "Sécheresse US": multi["A"]["verdict"],
        "Sécheresse Méditerranée": _region_verdict_or_untested(c_med),
        "Sécheresse Inde": _region_verdict_or_untested(c_india),
        "NMME": "bloquée",
        "Open-Meteo Seasonal": "bloquée",
    }


def _region_pair(
    multi_row: dict[str, Any],
    ecmwf_row: dict[str, Any],
) -> dict[str, Any]:
    bss_m = multi_row.get("bss")
    bss_e = ecmwf_row.get("bss")
    beats: Optional[bool] = None
    if bss_m is not None and bss_e is not None:
        beats = bool(bss_m > bss_e)
    return {
        "multi_n": int(multi_row.get("n") or 0),
        "multi_bss": bss_m,
        "multi_verdict": multi_row.get("verdict", "bloquée"),
        "ecmwf51_n": int(ecmwf_row.get("n") or 0),
        "ecmwf51_bss": bss_e,
        "ecmwf51_verdict": ecmwf_row.get("verdict", "bloquée"),
        "mix_beats_ecmwf51": beats,
    }


def compare_to_ecmwf51(
    multi: dict[str, dict[str, Any]],
    ecmwf: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Does the mix beat ECMWF-51? Headline is CHIRPS MED only.

    The published PR 246 BSS is not used here. If either BSS is
    undefined, the comparison stays empty.
    """
    by_ab: dict[str, Any] = {}
    for key in ("A", "B", "C"):
        regions = {}
        multi_regions = multi[key].get("by_region") or {}
        ecmwf_regions = ecmwf[key].get("by_region") or {}
        names = list(dict.fromkeys([
            *multi_regions.keys(),
            *ecmwf_regions.keys(),
        ]))
        for region in names:
            regions[region] = _region_pair(
                multi_regions.get(region) or {},
                ecmwf_regions.get(region) or {},
            )
        by_ab[key] = regions
    med = by_ab["C"].get("med") or _region_pair({}, {})
    return {
        "ab": "C",
        "region": "med",
        "truth_name": "CHIRPS pluie",
        "pooled": False,
        "headline_only": True,
        "uses_published_baseline": False,
        "multi_n": med["multi_n"],
        "multi_bss": med["multi_bss"],
        "multi_verdict": med["multi_verdict"],
        "ecmwf51_n": med["ecmwf51_n"],
        "ecmwf51_bss": med["ecmwf51_bss"],
        "ecmwf51_verdict": med["ecmwf51_verdict"],
        "mix_beats_ecmwf51": med["mix_beats_ecmwf51"],
        "by_ab": by_ab,
    }


def _ecmwf_monthly(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        if (row["origin"], int(row["system"])) != ECMWF_51:
            continue
        if not row.get("expected"):
            continue
        out.append({
            "region": row["region"],
            "init_year": row["init_year"],
            "init_month": row["init_month"],
            "lead_month": row["lead_month"],
            "tp_mean_mm": row["tp_mean_mm"],
            "tp_anom_mm": None,
            "valid_year": row["valid_year"],
            "valid_month": row["valid_month"],
            "season": row["season"],
            "season_year": row["season_year"],
            "n_centres": 1,
            "missing_centres": [],
        })
    return out


def _arm_blocker_no_rows(kind: str) -> str:
    if kind == "ecmwf":
        return (
            "Centre ECMWF système 51 absent. Trou non comblé. "
            "Le CSV SEAS5 n'est pas lu pour le remplir. "
            "Pas de score inventé."
        )
    return (
        "CSV C3S lu, zéro saison complète de 3 mois sur les centres "
        "attendus. Pas de score inventé."
    )


def score_all(
    data_dir: Path = DATA_DIR,
    forecast_dir: Path = C3S_DIR,
    forecast_csv: Optional[Path] = None,
    init_month: Optional[int] = None,
    min_lead: int = 1,
    max_lead: int = 7,
    include_shared: bool = True,
) -> dict[str, Any]:
    specs = c3s_specs()
    explicit = Path(forecast_csv) if forecast_csv else None
    status = forecast_status(
        forecast_dir,
        include_shared=include_shared,
        explicit=explicit,
    )
    multi: dict[str, Any]
    ecmwf: dict[str, Any]
    holes = empty_inventory()
    if not status["present"]:
        multi = _all_blocked(specs, status["reason"] or "CSV C3S absent.")
        ecmwf = _all_blocked(
            specs,
            (status["reason"] or "CSV C3S absent.")
            + " ECMWF-51 non scoré.",
        )
    else:
        path = Path(status["csv_path"])
        raw = load_c3s_csv(path)
        window = filter_window(raw, init_month, min_lead, max_lead)
        aggregated = aggregate_equal_weight(window)
        holes = inventory(raw, aggregated)
        status["n_rows"] = len(raw)
        if not raw:
            reason = "CSV C3S lu, zéro ligne. Pas de score inventé."
            multi = _all_blocked(specs, reason)
            ecmwf = _all_blocked(specs, _arm_blocker_no_rows("ecmwf"))
        else:
            seasons = seasons_from_monthly(aggregated) if aggregated else []
            if not seasons:
                multi = _all_blocked(specs, _arm_blocker_no_rows("multi"))
            else:
                multi = _score_seasons(seasons, data_dir, specs, str(path))
            ecmwf_rows = _ecmwf_monthly(window)
            ecmwf_seasons = seasons_from_monthly(ecmwf_rows) if ecmwf_rows else []
            if not ecmwf_seasons:
                ecmwf = _all_blocked(specs, _arm_blocker_no_rows("ecmwf"))
            else:
                ecmwf = _score_seasons(
                    ecmwf_seasons, data_dir, specs, str(path)
                )
    status["inventory"] = holes
    comparison = compare_to_ecmwf51(multi, ecmwf)
    return {
        "forecast_name": FORECAST_NAME,
        "as_of_mode": "offline",
        "cds_called": False,
        "cdsapi_imported": False,
        "champion_switched": False,
        "real_money": False,
        "bss_invented": False,
        "pooled": False,
        "filled_from_seas5": False,
        "weighting": "equal_centre",
        "headline_ab": "C",
        "headline_region": "med",
        "shared_csv": str(SHARED_FORECAST_CSV),
        "gate": {
            "bss_gt": BSS_GATE,
            "min_seasons": MIN_SEASONS_FOR_GATE,
        },
        "forecast": status,
        "published_seas5_baseline": PUBLISHED_SEAS5_BASELINE,
        "ab": multi,
        "ecmwf51": {
            "forecast_name": "ECMWF-51",
            "role": "baseline SEAS5 recalculée seulement si les lignes sont dans le CSV C3S",
            "filled_from_seas5_csv": False,
            "ab": ecmwf,
            "verdict": _product_verdict(ecmwf),
        },
        "comparison": comparison,
        "verdicts": catalogue_verdicts(multi, ecmwf),
    }
