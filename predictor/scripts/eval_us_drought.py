"""eval_us_drought.py — vérité US Drought Monitor pour « Sécheresse US ».

FR : Compte l'archive hebdomadaire officielle depuis 2000. Midwest et
Southwest = séries nommées des hubs USDA dans le REST USDM. Ensuite
essaie Open-Meteo Seasonal (sans compte). Si l'archive de prévision
est trop courte, le dit. Le champion Kalshi n'est pas touché.

Usage:
    python scripts/eval_us_drought.py
    python scripts/eval_us_drought.py --skip-fetch
    python scripts/eval_us_drought.py --skip-forecast
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.forecast.nmme import probe_nmme  # noqa: E402
from src.forecast.open_meteo_seasonal import (  # noqa: E402
    ALLOWED_END, ALLOWED_START, FORECAST_NAME as OM_NAME, HUB_POINTS,
    OpenMeteoSeasonalClient, monthly_rows,
)
from src.truth.synthetic_bins import brier  # noqa: E402
from src.truth.usdm import (  # noqa: E402
    CLASSES, CLASS_LABELS_EN, CLIMATE_HUB_AOI, D2PLUS_AREA_THRESHOLD,
    MIDWEST_STATES, SOUTHWEST_MAINLAND_STATES, USDM_ARCHIVE_START, USDM_OUT,
    UsdmClient, UsdmWeek, brier_skill_score, combine_area_weeks, coverage_table,
    leave_one_out_climato, met_season, month_is_complete, season_means,
)

CATALOGUE_TARGET = "Sécheresse US"
TRUTH_NAME = "US Drought Monitor"
BSS_GATE = 0.05
MIN_SEASONS_FOR_GATE = 10


def _today() -> date:
    return datetime.now(timezone.utc).date()


def fetch_all(client: UsdmClient, start: date, end: date, allow_network: bool) -> dict[str, list[UsdmWeek]]:
    out: dict[str, list[UsdmWeek]] = {}
    print("  CONUS (catégoriel + cumulatif) ...", flush=True)
    out["CONUS_cat"] = client.fetch_percent(
        "USStatistics", "conus", start, end, 2, "CONUS", allow_network)
    out["CONUS_cum"] = client.fetch_percent(
        "USStatistics", "conus", start, end, 1, "CONUS", allow_network)
    for hub_name, aoi in CLIMATE_HUB_AOI.items():
        print(f"  hub USDA {hub_name} (aoi {aoi}) ...", flush=True)
        out[f"{hub_name}_cat"] = client.fetch_percent(
            "ClimateHubStatistics", str(aoi), start, end, 2, hub_name, allow_network)
        out[f"{hub_name}_area"] = client.fetch_area(
            "ClimateHubStatistics", str(aoi), start, end, 2, hub_name, allow_network)
    print("  somme Midwest + Southwest (aires publiées) ...", flush=True)
    out["Midwest_plus_Southwest_cat"] = combine_area_weeks(
        [out["Midwest_area"], out["Southwest_area"]], "Midwest_plus_Southwest")
    for abbr, fips in {**MIDWEST_STATES, **SOUTHWEST_MAINLAND_STATES}.items():
        print(f"  État {abbr} ...", flush=True)
        out[f"state_{abbr}_cat"] = client.fetch_percent(
            "StateStatistics", fips, start, end, 2, abbr, allow_network)
    return out


def write_weeks(path: Path, weeks: list[UsdmWeek]) -> None:
    path.write_text(
        json.dumps([w.to_json() for w in weeks], indent=2), encoding="utf-8")


def _round(x: Optional[float], nd: int = 4) -> Optional[float]:
    if x is None:
        return None
    return round(float(x), nd)


def score_open_meteo(
    series_weeks: dict[str, list[UsdmWeek]],
    allow_network: bool,
) -> dict[str, Any]:
    """Score the months Open-Meteo Seasonal actually returned. No filler."""
    client = OpenMeteoSeasonalClient()
    blocker: Optional[str] = None
    hist_try = None
    try:
        hist_try = client.fetch_monthly(
            41.6, -93.6, start_date=date(2015, 1, 1), end_date=date(2015, 7, 1),
            allow_network=allow_network,
        )
    except Exception as e:
        hist_try = {"error": True, "reason": f"{type(e).__name__}: {e}"}
    if hist_try.get("error") or not monthly_rows(hist_try):
        blocker = (
            "Open-Meteo Seasonal refuse start_date avant "
            f"{ALLOWED_START.isoformat()} "
            f"({hist_try.get('reason') or hist_try.get('http_status') or 'vide'}). "
            "Pas de hindcast depuis 2000. Fenêtre servie : "
            f"{ALLOWED_START.isoformat()} à {ALLOWED_END.isoformat()}."
        )

    by_hub: dict[str, Any] = {}
    monthly_pairs: list[dict[str, Any]] = []
    window_end = min(_today().replace(day=1), ALLOWED_END)
    for hub, pt in HUB_POINTS.items():
        raw = client.fetch_monthly(
            pt["lat"], pt["lon"],
            start_date=ALLOWED_START, end_date=window_end,
            allow_network=allow_network,
        )
        if raw.get("error"):
            raw = client.fetch_monthly(pt["lat"], pt["lon"], allow_network=allow_network)
        rows = monthly_rows(raw)
        weeks = series_weeks.get(f"{hub}_cat") or []
        have = {w.map_date for w in weeks}
        by_month: dict[str, list[UsdmWeek]] = {}
        for w in weeks:
            by_month.setdefault(w.map_date.strftime("%Y-%m-01"), []).append(w)
        scored = []
        for row in rows:
            month = row["month"]
            mdate = date.fromisoformat(month)
            group = by_month.get(month, [])
            if not group or row["precipitation_anomaly"] is None:
                continue
            if not month_is_complete(mdate.year, mdate.month, have):
                continue
            d2p = statistics.fmean(w.d2_plus() for w in group)
            event = d2p >= D2PLUS_AREA_THRESHOLD
            p_fc = 1.0 if row["precipitation_anomaly"] < 0 else 0.0
            scored.append({
                "hub": hub,
                "month": month,
                "n_weeks": len(group),
                "d2_plus_mean": d2p,
                "event_d2_plus_ge_30": event,
                "precipitation_anomaly": row["precipitation_anomaly"],
                "p_forecast_dry": p_fc,
            })
        by_hub[hub] = {
            "point": pt,
            "error": raw.get("reason") if raw.get("error") else None,
            "n_months_returned": len(rows),
            "months": rows,
            "n_scored": len(scored),
            "scored": scored,
        }
        monthly_pairs.extend(scored)
        by_hub[hub]["skill_months"] = _skill_block(scored, "event_d2_plus_ge_30", "p_forecast_dry")

    season_pairs = _season_pairs(monthly_pairs)
    n_seasons = len({(r["season"], r["year"]) for r in season_pairs})
    skill = {
        "forecast_name": OM_NAME,
        "rule": "p=1 si precipitation_anomaly < 0, sinon 0 (moyenne d'ensemble SEAS5)",
        "event": f"moyenne D2+ catégorielle ≥ {D2PLUS_AREA_THRESHOLD} %",
        "n_complete_months": len(monthly_pairs),
        "n_month_hub_rows": len(monthly_pairs),
        "n_distinct_months": len({r["month"] for r in monthly_pairs}),
        "n_distinct_seasons": n_seasons,
        "by_hub_months": {h: by_hub[h]["skill_months"] for h in by_hub},
        "seasons": season_pairs,
        "skill_seasons_by_hub": {},
        "gate_bss_gt_0_05": False,
        "gate_n_ge_10": n_seasons >= MIN_SEASONS_FOR_GATE,
        "n_seasons_for_gate": n_seasons,
    }
    for hub in by_hub:
        rows = [r for r in season_pairs if r["hub"] == hub]
        skill["skill_seasons_by_hub"][hub] = _skill_block(
            rows, "event_d2_plus_ge_30", "p_forecast_dry")
    # Headline skill = Southwest seasons if present, else Midwest. Never pool hubs.
    headline = skill["skill_seasons_by_hub"].get("Southwest") or skill["skill_seasons_by_hub"].get("Midwest") or {}
    skill["brier_forecast"] = headline.get("brier_forecast")
    skill["brier_climato"] = headline.get("brier_climato")
    skill["bss"] = headline.get("bss")
    skill["n_months"] = skill["n_distinct_months"]
    skill["gate_bss_gt_0_05"] = bool(
        headline.get("bss") is not None and headline["bss"] > BSS_GATE
        and n_seasons >= MIN_SEASONS_FOR_GATE
    )

    return {
        "forecast_name": OM_NAME,
        "historical_start_date_probe": {
            "error": bool(hist_try.get("error")),
            "reason": hist_try.get("reason"),
            "n_months": len(monthly_rows(hist_try)),
        },
        "blocker": blocker,
        "by_hub": by_hub,
        "skill": skill,
    }


def _skill_block(rows: list[dict[str, Any]], event_key: str, p_key: str) -> dict[str, Any]:
    events = [bool(r[event_key]) for r in rows]
    out = {
        "n": len(rows),
        "base_rate": _round(statistics.fmean(1.0 if e else 0.0 for e in events)) if rows else None,
        "brier_forecast": None,
        "brier_climato": None,
        "bss": None,
    }
    if len(rows) < 2:
        return out
    p_fc = [float(r[p_key]) for r in rows]
    p_cl = leave_one_out_climato(events)
    bs_fc = statistics.fmean(brier(a, b) for a, b in zip(p_fc, events))
    bs_cl = statistics.fmean(brier(a, b) for a, b in zip(p_cl, events))
    out["brier_forecast"] = _round(bs_fc)
    out["brier_climato"] = _round(bs_cl)
    out["bss"] = _round(brier_skill_score(bs_fc, bs_cl))
    return out


def _season_pairs(monthly_pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str, int], list[dict[str, Any]]] = {}
    for r in monthly_pairs:
        m = date.fromisoformat(r["month"])
        season, year = met_season(m)
        buckets.setdefault((r["hub"], season, year), []).append(r)
    out = []
    for (hub, season, year), rows in sorted(buckets.items(), key=lambda kv: (kv[0][0], kv[0][2], kv[0][1])):
        if len(rows) < 3:
            continue
        d2p = statistics.fmean(r["d2_plus_mean"] for r in rows)
        anom = statistics.fmean(r["precipitation_anomaly"] for r in rows)
        out.append({
            "hub": hub,
            "season": season,
            "year": year,
            "n_months": len(rows),
            "d2_plus_mean": d2p,
            "event_d2_plus_ge_30": d2p >= D2PLUS_AREA_THRESHOLD,
            "precipitation_anomaly": anom,
            "p_forecast_dry": 1.0 if anom < 0 else 0.0,
        })
    return out


def score_seasons_climato_only(weeks: list[UsdmWeek], event_key: str) -> dict[str, Any]:
    """Climatology frequencies on complete seasons. No forecast here."""
    rows = [r for r in season_means(weeks) if r["complete"]]
    by_type: dict[str, list[bool]] = {"DJF": [], "MAM": [], "JJA": [], "SON": []}
    for r in rows:
        by_type[r["season"]].append(bool(r[event_key]))
    out = {"n_complete_seasons": len(rows), "by_type": {}}
    for season, events in by_type.items():
        n = len(events)
        out["by_type"][season] = {
            "n": n,
            "events": sum(1 for e in events if e),
            "frequency": (sum(1 for e in events if e) / n) if n else None,
        }
    return out


def verdicts(truth_ok: bool, om: dict[str, Any], nmme: dict[str, Any]) -> dict[str, str]:
    """Catalogue statuses. Names are not renamed."""
    skill = om.get("skill") or {}
    om_status = "pas encore testée"
    if skill.get("gate_n_ge_10") and skill.get("gate_bss_gt_0_05"):
        om_status = "testée, ça aide"
    elif skill.get("gate_n_ge_10"):
        om_status = "testée, ça n'aide pas"
    else:
        om_status = "bloquée"

    target = "cible Tier 1 (pas encore testée)"
    if truth_ok and om_status == "testée, ça aide":
        target = "testée, ça aide"
    elif truth_ok and om_status == "testée, ça n'aide pas":
        target = "testée, ça n'aide pas"
    elif truth_ok and om_status == "bloquée":
        target = "bloquée"

    return {
        CATALOGUE_TARGET: target,
        TRUTH_NAME: "testée, ça aide" if truth_ok else "bloquée",
        OM_NAME: om_status,
        "NMME": "bloquée" if not nmme.get("hindcast_usable") else "pas encore testée",
        "SEAS5": "pas encore testée",
        "C3S multi-modèle": "pas encore testée",
        "SPEI": "pas encore testée",
        "CHIRPS pluie": "pas encore testée",
        "Sécheresse Méditerranée": "cible Tier 1 (pas encore testée)",
        "Sécheresse Inde": "cible Tier 1 (pas encore testée)",
        "Ouragan formation": "cible Tier 1 (pas encore testée)",
        "Ouragan intensité": "cible Tier 1 (pas encore testée)",
        "Ouragan landfall": "cible Tier 1 (pas encore testée)",
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    cov = payload["coverage"]
    lines = [
        f"# {TRUTH_NAME} : comptes mesurés",
        "",
        f"Cible catalogue : {CATALOGUE_TARGET}.",
        f"Vérité : {TRUTH_NAME}.",
        f"Prévision essayée : {OM_NAME}.",
        "Aucun chiffre inventé. Champion Kalshi inchangé.",
        "",
        "## Semaines",
        "",
        "| Série | Semaines | Premier | Dernier | Trous | Saisons ≥ 12 semaines |",
        "|---|---:|---|---|---:|---:|",
    ]
    for key in ("CONUS_cat", "Midwest_cat", "Southwest_cat", "Midwest_plus_Southwest_cat"):
        c = cov[key]
        lines.append(
            f"| {c['series']} | {c['n_weeks']} | {c['first_map']} | {c['last_map']} | "
            f"{c['missing_weeks']} | {c['n_seasons_12_plus_weeks']} |"
        )
    lines += ["", "## Classes (part de semaines avec une aire > 0, catégoriel)", ""]
    for key in ("CONUS_cat", "Midwest_cat", "Southwest_cat", "Midwest_plus_Southwest_cat"):
        c = cov[key]
        lines += [f"### {c['series']}", "",
                  "| Classe | Semaines > 0 | Part | Moyenne | Max |",
                  "|---|---:|---:|---:|---:|"]
        for k in CLASSES:
            cl = c["classes"][k]
            lines.append(
                f"| {CLASS_LABELS_EN[k]} | {cl['weeks_with_area']} | "
                f"{cl['share_of_weeks']:.3f} | {cl['mean_value']:.2f} | {cl['max_value']:.2f} |"
            )
        d2 = c["d2_plus"]
        lines += [
            "",
            f"D2+ moyenne {d2['mean']:.2f}. Semaines D2+ > 0 : {d2['weeks_gt_0']}. "
            f"Semaines D2+ ≥ 30 % : {d2['weeks_ge_30']}.",
            "",
        ]
    lines += ["## Verdicts (noms du catalogue, non renommés)", ""]
    for name, status in payload["verdicts"].items():
        lines.append(f"- {name} : {status}")
    om = payload["open_meteo_seasonal"]
    lines += ["", f"## {OM_NAME}", ""]
    if om.get("blocker"):
        lines.append(om["blocker"])
    sk = om.get("skill") or {}
    lines.append(
        f"Mois complets distincts : {sk.get('n_distinct_months')}. "
        f"Saisons distinctes : {sk.get('n_seasons_for_gate')}. "
        f"Gate : {MIN_SEASONS_FOR_GATE} saisons et BSS > {BSS_GATE}."
    )
    for hub, block in (sk.get("skill_seasons_by_hub") or {}).items():
        lines.append(
            f"{hub} (saisons) : n={block.get('n')} Brier prévision {block.get('brier_forecast')} "
            f"Brier climato {block.get('brier_climato')} BSS {block.get('bss')}."
        )
    if payload.get("nmme", {}).get("blocker") or not payload.get("nmme", {}).get("any_ok"):
        lines += ["", "## NMME", "", "Accès public insuffisant pour un hindcast noté (voir nmme_probe.json)."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skip-fetch", action="store_true")
    p.add_argument("--skip-forecast", action="store_true")
    p.add_argument("--write-weeks", action="store_true")
    p.add_argument("--end-date", default="")
    p.add_argument("--out-dir", default=str(USDM_OUT))
    args = p.parse_args()
    end = date.fromisoformat(args.end_date) if args.end_date else _today()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"{TRUTH_NAME} {USDM_ARCHIVE_START} → {end}", flush=True)
    client = UsdmClient()
    series = fetch_all(client, USDM_ARCHIVE_START, end, allow_network=not args.skip_fetch)

    coverage = {k: coverage_table(v) for k, v in series.items() if v and v[0].unit == "percent"}
    climato = {
        k: {
            "d2_plus_gt_0": score_seasons_climato_only(series[k], "event_d2_plus_gt_0"),
            "d2_plus_ge_30": score_seasons_climato_only(series[k], "event_d2_plus_ge_30"),
        }
        for k in ("CONUS_cat", "Midwest_cat", "Southwest_cat", "Midwest_plus_Southwest_cat")
        if k in series
    }

    if args.write_weeks:
        for key in ("CONUS_cat", "Midwest_cat", "Southwest_cat", "Midwest_plus_Southwest_cat"):
            write_weeks(out_dir / f"weeks_{key}.json", series[key])

    if args.skip_forecast:
        om = {
            "forecast_name": OM_NAME,
            "blocker": "prévision non lancée (--skip-forecast)",
            "skill": {"n_months": 0, "bss": None, "gate_bss_gt_0_05": False, "gate_n_ge_10": False},
        }
        nmme = {"forecast_name": "NMME", "any_ok": False, "skipped": True}
    else:
        print(f"{OM_NAME} ...", flush=True)
        om = score_open_meteo(series, allow_network=True)
        print("NMME probe ...", flush=True)
        nmme = probe_nmme()
        if not nmme.get("hindcast_usable"):
            nmme["blocker"] = nmme.get("blocker") or (
                "aucune URL publique NMME n'a renvoyé un hindcast utilisable"
            )

    truth_ok = all(
        coverage[k]["n_weeks"] > 0 and coverage[k]["missing_weeks"] == 0
        for k in ("CONUS_cat", "Midwest_cat", "Southwest_cat")
    )
    payload = {
        "catalogue_target": CATALOGUE_TARGET,
        "truth_name": TRUTH_NAME,
        "forecast_name_used": OM_NAME,
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "archive_start": USDM_ARCHIVE_START.isoformat(),
        "end_date": end.isoformat(),
        "champion_switched": False,
        "real_money": False,
        "classes_published": [CLASS_LABELS_EN[k] for k in CLASSES],
        "region_source": {
            "Midwest": "USDM ClimateHubStatistics aoi=3 (name=Midwest); états USDA Midwest Hub",
            "Southwest": "USDM ClimateHubStatistics aoi=10 (name=Southwest); états USDA Southwest Hub (continent)",
            "combined": "somme des aires catégorielles des deux hubs, même mapDate",
        },
        "coverage": coverage,
        "season_climato": climato,
        "open_meteo_seasonal": om,
        "nmme": nmme,
        "verdicts": verdicts(truth_ok, om, nmme),
        "gate": {
            "bss_gt": BSS_GATE,
            "min_seasons": MIN_SEASONS_FOR_GATE,
            "passed": bool(
                (om.get("skill") or {}).get("gate_bss_gt_0_05")
                and (om.get("skill") or {}).get("gate_n_ge_10")
            ),
        },
    }
    (out_dir / "usdm_counts.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8")
    (out_dir / "nmme_probe.json").write_text(
        json.dumps(nmme, indent=2), encoding="utf-8")
    write_report(out_dir / "usdm_report.md", payload)
    print(json.dumps({
        "n_conus": coverage["CONUS_cat"]["n_weeks"],
        "n_midwest": coverage["Midwest_cat"]["n_weeks"],
        "n_southwest": coverage["Southwest_cat"]["n_weeks"],
        "missing_conus": coverage["CONUS_cat"]["missing_weeks"],
        "om_months": (om.get("skill") or {}).get("n_months"),
        "om_bss": (om.get("skill") or {}).get("bss"),
        "om_blocker": om.get("blocker"),
        "verdicts": payload["verdicts"],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
