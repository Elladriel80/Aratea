"""eval_chirps.py : vérité CHIRPS pluie (Méditerranée / Inde).

FR : Compte d'abord la vérité catalogue « CHIRPS pluie ». Pas de
prévision saisonnière. Pas de SEAS5 / C3S. Pas de BSS. Le champion
Kalshi n'est pas touché. Aucun chiffre inventé.

Usage:
    python scripts/eval_chirps.py
    python scripts/eval_chirps.py --skip-fetch
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.truth.chirps import (  # noqa: E402
    CATALOGUE_TRUTH, CHIRPS_BYYEAR, CHIRPS_DATA_ROOT, CHIRPS_EWX,
    CHIRPS_FAQ, CHIRPS_HOME, CHIRPS_MONTHLY_NC, CHIRPS_NETCDF, CHIRPS_OUT,
    CHIRPS_README, CHIRPS_TIFS, CHIRPS_V3_NOTE, FAQ_FILL, FAQ_GRID_NX,
    FAQ_GRID_NY, FAQ_LAT_MAX, FAQ_LAT_MIN, FAQ_RESOLUTION_DEG, FAQ_UNITS,
    FUNK_2015, GEE_HTML_PENTAD, GEE_STAC_PENTAD, IPCC_REGIONS_CSV,
    IRI_PRECIP, NE_ADMIN1_URL, TARGET_INDE, TARGET_MED, USGS_DS832,
    ChirpsClient, RegionAccumulator, empty_region_row, gee_catalog_excerpt,
    mask_from_rings, parse_prelim_tif_index, parse_ucsb_tif_index,
    parse_ucsb_year_index, read_iri_netcdf, read_ucsb_year_netcdf,
    regions_from_sources, rings_bbox,
)

TARGETS = (TARGET_MED, TARGET_INDE)


def _rel_to_predictor(path: Path | None) -> str | None:
    """Keep committed paths relative. Do not write /workspace/..."""
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return path.name


def verdicts(pixels_ok: bool) -> dict[str, str]:
    """Catalogue statuses. Names are not renamed. No forecast scored."""
    chirps = "testée, ça aide" if pixels_ok else "bloquée"
    return {
        CATALOGUE_TRUTH: chirps,
        TARGET_MED: "cible Tier 1 (pas encore testée)",
        TARGET_INDE: "cible Tier 1 (pas encore testée)",
        "Sécheresse US": "bloquée",
        "SPEI": "testée, ça aide",
        "US Drought Monitor": "testée, ça aide",
        "SEAS5": "pas encore testée",
        "C3S multi-modèle": "pas encore testée",
        "NMME": "bloquée",
        "Open-Meteo Seasonal": "bloquée",
        "HURDAT2 / IBTrACS": "testée, ça aide",
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    probes = payload["access"]["probes"]
    gee = payload.get("gee_catalog") or {}
    tifs = payload.get("ucsb_tif_index") or {}
    years = payload.get("ucsb_year_index") or {}
    prelim = payload.get("prelim_tif_index") or {}
    lines = [
        f"# {CATALOGUE_TRUTH} : comptes mesurés",
        "",
        f"Vérité catalogue : {CATALOGUE_TRUTH}.",
        "Cibles : Sécheresse Méditerranée / Sécheresse Inde.",
        "Aucune prévision saisonnière notée. Champion Kalshi inchangé.",
        "Aucun chiffre inventé. Pas de BSS. Pas de seuil inventé.",
        "",
        "## Accès mesuré",
        "",
        "| URL | HTTP | Octets | Note |",
        "|---|---:|---:|---|",
    ]
    for p in probes:
        status = p.get("http_status")
        status_s = "" if status is None else str(status)
        nbytes = p.get("n_bytes")
        nbytes_s = "" if nbytes is None else str(nbytes)
        lines.append(
            f"| {p['url']} | {status_s} | {nbytes_s} | {p.get('note', '')} |"
        )
    lines += [
        "",
        "## Produit publié (docs, pas inventé)",
        "",
        f"Nom : CHIRPS v2.0 mensuel, UCSB Climate Hazards.",
        f"Résolution publiée (FAQ) : {FAQ_RESOLUTION_DEG} degré.",
        f"Grille publiée : {FAQ_GRID_NX} × {FAQ_GRID_NY} (50S-50N).",
        f"Latitude publiée : {FAQ_LAT_MIN} à {FAQ_LAT_MAX}.",
        f"Unités : {FAQ_UNITS}.",
        f"Valeur manquante : {FAQ_FILL}.",
        "Seuils de sécheresse dans le README / la FAQ / l'en-tête : aucun.",
        "Les dossiers EWX anomaly / zscore existent à part. On ne les a pas notés.",
        f"CHIRPS v3 est annoncé ({CHIRPS_V3_NOTE}). Ce compte est v2.",
        "",
        "## Index officiel UCSB (noms de fichiers, pas les pixels)",
        "",
    ]
    if tifs.get("n_files") is not None:
        lines += [
            f"GeoTIFF mensuels finaux : {tifs.get('n_files')} fichiers, "
            f"{tifs.get('first_month')} à {tifs.get('last_month')}.",
            f"Mois manquants dans cet intervalle : {tifs.get('n_missing_months_in_span')}.",
            f"Liste des trous : {tifs.get('missing_months_in_span')}.",
            f"Source : {tifs.get('source')}.",
            "",
        ]
    else:
        lines += ["Index GeoTIFF non lu.", ""]
    if years.get("n_files") is not None:
        lines += [
            f"NetCDF par année : {years.get('n_files')} fichiers, "
            f"{years.get('first_year')} à {years.get('last_year')}.",
            f"Années manquantes : {years.get('missing_years_in_span')}.",
            f"Source : {years.get('source')}.",
            "",
        ]
    if prelim.get("n_files") is not None:
        lines += [
            f"Prelim mensuel (non compté) : {prelim.get('n_files')} fichiers, "
            f"{prelim.get('first_month')} à {prelim.get('last_month')}.",
            "",
        ]
    lines += [
        "## Catalogue GEE (métadonnées pentade, pas les pixels)",
        "",
    ]
    if gee:
        lines += [
            f"Id : `{gee.get('id')}`.",
            f"Titre : {gee.get('title')}.",
            f"Intervalle de temps publié : {gee.get('temporal_interval')}.",
            f"Boîte spatiale : {gee.get('spatial_bbox')}.",
            f"Cadence : {gee.get('cadence')}.",
            f"Licence / termes : public domain (texte GEE).",
            "Les pixels ne sont pas dans ce JSON. Ce n'est pas le fichier mensuel.",
            "",
        ]
    else:
        lines += ["Catalogue GEE non lu.", ""]
    lines += [
        "## Découpages publiés (polygones, pas les cases CHIRPS)",
        "",
    ]
    cuts = payload.get("region_cuts") or {}
    med = cuts.get(TARGET_MED) or {}
    inde = cuts.get(TARGET_INDE) or {}
    lines += [
        f"Méditerranée : IPCC MED, {med.get('n_rings')} polygone(s), "
        f"sommets lus sur le CSV vivant = {med.get('vertices_from_live_csv')}.",
        f"Inde : Maharashtra + Karnataka, {inde.get('n_rings')} anneau(x). "
        f"États manquants : {inde.get('inde_missing')}.",
        "Ces anneaux ne sont pas un compte CHIRPS.",
        "",
        "## Cellules par région",
        "",
    ]
    for name in TARGETS:
        row = payload["regions"].get(name) or {}
        lines.append(f"### {name}")
        lines.append("")
        if not row.get("usable_measured"):
            lines.append(
                f"Non mesuré. Raison : {row.get('reason', 'fichier CHIRPS absent')}."
            )
            lines.append("Aucun nombre de cellules n'est écrit.")
            lines.append("")
            continue
        lines += [
            "| Mesure | Valeur |",
            "|---|---:|",
            f"| Cases dans le découpage publié | {row.get('n_cells_in_published_cut')} |",
            f"| Cases utilisables (au moins 1 mois fini) | {row.get('n_cells_usable_any_month')} |",
            f"| Cases jamais valides | {row.get('n_cells_never_valid')} |",
            f"| Premier mois ouvert | {row.get('first_month')} |",
            f"| Dernier mois ouvert | {row.get('last_month')} |",
            f"| Premier mois avec une valeur | {row.get('first_month_with_a_value')} |",
            f"| Dernier mois avec une valeur | {row.get('last_month_with_a_value')} |",
            f"| Mois avec au moins une case finie | {row.get('n_months_with_any_valid')} |",
            f"| Mois sans aucune case finie | {row.get('n_months_without_any_valid')} |",
            f"| Années avec une valeur | {row.get('n_calendar_years_with_a_value')} |",
            f"| Années manquantes dans l'intervalle ouvert | {row.get('n_missing_years_in_span')} |",
            f"| Mois-cellules finis | {row.get('n_finite_cell_months')} |",
            f"| Mois-cellules à 0 mm (valeur réelle, pas un trou) | {row.get('n_zero_rain_cell_months')} |",
            "",
        ]
    ucsb = payload.get("ucsb_2026_check") or {}
    if ucsb.get("regions"):
        lines += [
            "## Contrôle UCSB 2026 (fichier officiel par année, autre grille)",
            "",
            f"Fichier : `{ucsb.get('path')}` ({ucsb.get('n_bytes')} octets).",
            "Ce n'est pas mélangé avec les totaux IRI. Grilles un peu différentes.",
            "",
        ]
        for name in TARGETS:
            row = (ucsb.get("regions") or {}).get(name) or {}
            if not row:
                continue
            lines += [
                f"{name} : {row.get('n_times')} mois ({row.get('first_month')} à "
                f"{row.get('last_month')}), "
                f"{row.get('n_cells_in_published_cut')} cases, "
                f"{row.get('n_cells_usable_any_month')} utilisables, "
                f"mois absents d'IRI {row.get('months_not_in_iri')}.",
            ]
        lines.append("")
    lines += [
        "## Verdicts (noms du catalogue, non renommés)",
        "",
    ]
    for name, status in payload["verdicts"].items():
        lines.append(f"- {name} : {status}")
    lines += [
        "",
        "Pas de score saisonnier dans ce run.",
        "Pas de BSS inventé.",
        "SEAS5 / C3S non ouverts (compte Copernicus).",
        "",
    ]
    notes = (payload.get("access") or {}).get("download_notes") or []
    if notes:
        lines.append("Notes de téléchargement :")
        for note in notes:
            lines.append(f"- {note}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _cut_summary(regions: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, spec in regions.items():
        row: dict[str, Any] = {
            k: spec[k]
            for k in spec
            if k not in ("rings", "states")
        }
        row["n_rings"] = len(spec.get("rings") or [])
        row["inde_missing"] = (spec.get("states") or {}).get("missing_names")
        out[name] = row
    return out


def _windows(regions: dict[str, Any]) -> dict[str, tuple[float, float, float, float]]:
    windows: dict[str, tuple[float, float, float, float]] = {}
    for label, spec in regions.items():
        rings = spec.get("rings") or []
        if not rings:
            continue
        box = rings_bbox(rings)
        if box is not None:
            windows[label] = box
    return windows


def _add_slab(
    accs: dict[str, RegionAccumulator],
    label: str,
    slab: Any,
    rings: list[Any],
    download_notes: list[str],
    path: Path,
) -> None:
    if label not in accs:
        mask = mask_from_rings(slab.lats, slab.lons, rings)
        accs[label] = RegionAccumulator.start(label, mask)
        download_notes.append(
            f"{label} : grille {slab.lats.size} lat × {slab.lons.size} lon, "
            f"{int(mask.sum())} cases du découpage, "
            f"fichier {_rel_to_predictor(path)}"
        )
    have = set(accs[label].months_any) | set(accs[label].months_none)
    for i, t in enumerate(slab.times):
        iso = f"{t.year:04d}-{t.month:02d}"
        if iso in have:
            continue
        accs[label].add(slab.values[i], t)


def _open_pixels(
    client: ChirpsClient,
    regions: dict[str, Any],
    download_notes: list[str],
    start_year: int,
    end_year: int,
    fetch: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Count IRI yearly subsets. UCSB 2026 is a separate measured check."""
    windows = _windows(regions)
    keys = {TARGET_MED: "med", TARGET_INDE: "inde"}
    accs: dict[str, RegionAccumulator] = {}
    ucsb_check: dict[str, Any] = {}
    if not windows:
        empty = {
            name: empty_region_row(
                name, "Découpage publié sans polygone lisible. Pas de compte inventé."
            )
            for name in TARGETS
        }
        return empty, ucsb_check

    years = list(range(start_year, end_year + 1))
    if not fetch:
        cached = sorted(client.cache_dir.glob("iri_*.nc"))
        if not cached:
            reason = (
                "Run --skip-fetch sans dalle locale. "
                "Aucun compte de cellules n'est inventé."
            )
            return {name: empty_region_row(name, reason) for name in TARGETS}, ucsb_check
        download_notes.append(f"cache IRI : {len(cached)} fichier(s)")
        for path in cached:
            try:
                slab = read_iri_netcdf(path)
            except Exception as exc:
                download_notes.append(f"lecture {path.name} : {type(exc).__name__}")
                continue
            key = "med" if "_med_" in path.name else "inde" if "_inde_" in path.name else ""
            label = TARGET_MED if key == "med" else TARGET_INDE if key == "inde" else ""
            if not label or label not in regions:
                continue
            if not (regions[label].get("rings") or []):
                download_notes.append(
                    f"{label} : dalle {path.name} ignorée, polygone absent"
                )
                continue
            _add_slab(accs, label, slab, regions[label]["rings"], download_notes, path)
    else:
        for year in years:
            for label, box in windows.items():
                lon0, lon1, lat0, lat1 = box
                key = keys[label]
                try:
                    path = client.download_iri_year(
                        key, lon0, lon1, lat0, lat1, year, last_month=12
                    )
                    slab = read_iri_netcdf(path)
                except Exception as exc:
                    download_notes.append(
                        f"IRI {key} {year} : {type(exc).__name__}: {exc}"
                    )
                    continue
                _add_slab(accs, label, slab, regions[label]["rings"], download_notes, path)
            print(f"année {year} ...", flush=True)

        if end_year >= 2026:
            try:
                ucsb_2026 = client.download_ucsb_year(2026)
                ucsb_check["path"] = _rel_to_predictor(ucsb_2026)
                ucsb_check["n_bytes"] = ucsb_2026.stat().st_size
                ucsb_check["regions"] = {}
                for label, box in windows.items():
                    lon0, lon1, lat0, lat1 = box
                    extra = read_ucsb_year_netcdf(ucsb_2026, lat0, lat1, lon0, lon1)
                    extra_mask = mask_from_rings(
                        extra.lats, extra.lons, regions[label]["rings"]
                    )
                    extra_acc = RegionAccumulator.start(label, extra_mask)
                    for i, t in enumerate(extra.times):
                        extra_acc.add(extra.values[i], t)
                    row = extra_acc.finish()
                    iri_have = set()
                    if label in accs:
                        iri_have = set(accs[label].months_any) | set(
                            accs[label].months_none
                        )
                    row["months_not_in_iri"] = [
                        m for m in (extra_acc.months_any + extra_acc.months_none)
                        if m not in iri_have
                    ]
                    ucsb_check["regions"][label] = row
                    download_notes.append(
                        f"UCSB 2026 {label} : {len(extra.times)} mois, "
                        f"dernier {extra.times[-1].isoformat()[:7] if extra.times else None}, "
                        f"mois absents d'IRI {row['months_not_in_iri']}"
                    )
            except Exception as exc:
                download_notes.append(f"UCSB 2026 yearly : {type(exc).__name__}: {exc}")

    if not accs:
        reason = (
            "Aucune dalle CHIRPS ouverte. IRI ou UCSB n'a pas donné de NetCDF. "
            "Aucun compte de cellules n'est inventé."
        )
        return {name: empty_region_row(name, reason) for name in TARGETS}, ucsb_check

    out: dict[str, Any] = {}
    for name in TARGETS:
        if name in accs:
            out[name] = accs[name].finish()
        else:
            out[name] = empty_region_row(
                name,
                "Découpage publié sans polygone lisible, ou aucune dalle ouverte.",
            )
    return out, ucsb_check


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skip-fetch", action="store_true")
    p.add_argument("--out-dir", default=str(CHIRPS_OUT))
    p.add_argument("--cache-dir", default="")
    p.add_argument("--start-year", type=int, default=1981)
    p.add_argument("--end-year", type=int, default=2026)
    args = p.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    kwargs: dict[str, Any] = {}
    if args.cache_dir:
        kwargs["cache_dir"] = Path(args.cache_dir)
    client = ChirpsClient(**kwargs)

    print(CATALOGUE_TRUTH, flush=True)
    probes: list[dict[str, Any]] = []
    gee_raw: dict[str, Any] = {}
    ipcc_csv: str | None = None
    ne_geo: dict[str, Any] | None = None
    tif_html = ""
    year_html = ""
    prelim_html = ""
    download_notes: list[str] = []
    cuts_dir = client.cache_dir
    cuts_dir.mkdir(parents=True, exist_ok=True)
    ipcc_cache = cuts_dir / "ipcc_regions.csv"
    ne_cache = cuts_dir / "ne_admin1.geojson"
    if not args.skip_fetch:
        print("sondes HTTP ...", flush=True)
        probes = client.probe_all()
        try:
            gee_raw = client.fetch_json(GEE_STAC_PENTAD)
        except Exception as exc:
            probes.append({
                "url": GEE_STAC_PENTAD,
                "ok": False,
                "note": f"relecture JSON : {type(exc).__name__}",
            })
        try:
            ipcc_csv = client.fetch_text(IPCC_REGIONS_CSV)
            ipcc_cache.write_text(ipcc_csv, encoding="utf-8")
        except Exception:
            ipcc_csv = ipcc_cache.read_text(encoding="utf-8") if ipcc_cache.exists() else None
        try:
            ne_geo = client.fetch_json(NE_ADMIN1_URL)
            ne_cache.write_text(json.dumps(ne_geo), encoding="utf-8")
        except Exception:
            ne_geo = (
                json.loads(ne_cache.read_text(encoding="utf-8"))
                if ne_cache.exists()
                else None
            )
        try:
            tif_html = client.fetch_text(CHIRPS_TIFS)
        except Exception as exc:
            download_notes.append(f"index tifs : {type(exc).__name__}")
        try:
            year_html = client.fetch_text(CHIRPS_BYYEAR)
        except Exception as exc:
            download_notes.append(f"index byYear : {type(exc).__name__}")
        try:
            prelim_html = client.fetch_text(
                "https://data.chc.ucsb.edu/products/CHIRPS-2.0/prelim/global_monthly/tifs/"
            )
        except Exception as exc:
            download_notes.append(f"index prelim : {type(exc).__name__}")
    else:
        print("sondes HTTP ignorées (--skip-fetch)", flush=True)
        if ipcc_cache.exists():
            ipcc_csv = ipcc_cache.read_text(encoding="utf-8")
        if ne_cache.exists():
            ne_geo = json.loads(ne_cache.read_text(encoding="utf-8"))

    gee = gee_catalog_excerpt(gee_raw) if gee_raw else {}
    regions = regions_from_sources(ipcc_csv, ne_geo)
    tif_index = parse_ucsb_tif_index(tif_html) if tif_html else {}
    year_index = parse_ucsb_year_index(year_html) if year_html else {}
    prelim_index = parse_prelim_tif_index(prelim_html) if prelim_html else {}

    print("grilles ...", flush=True)
    grid_counts, ucsb_check = _open_pixels(
        client,
        regions,
        download_notes,
        args.start_year,
        args.end_year,
        fetch=not args.skip_fetch,
    )
    pixels_ok = any(r.get("usable_measured") for r in grid_counts.values())

    payload = {
        "catalogue_truth": CATALOGUE_TRUTH,
        "targets": list(TARGETS),
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "champion_switched": False,
        "real_money": False,
        "forecast_scored": False,
        "seas5_started": False,
        "c3s_started": False,
        "bss_invented": False,
        "thresholds_invented": False,
        "sources": {
            "chirps_home": CHIRPS_HOME,
            "ucsb_root": CHIRPS_DATA_ROOT,
            "ucsb_tifs": CHIRPS_TIFS,
            "ucsb_netcdf": CHIRPS_NETCDF,
            "ucsb_byyear": CHIRPS_BYYEAR,
            "ucsb_monthly_nc": CHIRPS_MONTHLY_NC,
            "ucsb_ewx": CHIRPS_EWX,
            "readme": CHIRPS_README,
            "faq": CHIRPS_FAQ,
            "iri": IRI_PRECIP,
            "gee_stac_pentad": GEE_STAC_PENTAD,
            "gee_html_pentad": GEE_HTML_PENTAD,
            "ipcc_med": IPCC_REGIONS_CSV,
            "natural_earth_admin1": NE_ADMIN1_URL,
            "funk_2015": FUNK_2015,
            "usgs_ds832": USGS_DS832,
            "chirps_v3_announcement": CHIRPS_V3_NOTE,
        },
        "published_product": {
            "name": "CHIRPS v2.0 global monthly",
            "resolution_deg": FAQ_RESOLUTION_DEG,
            "grid_nx": FAQ_GRID_NX,
            "grid_ny": FAQ_GRID_NY,
            "lat_min": FAQ_LAT_MIN,
            "lat_max": FAQ_LAT_MAX,
            "units": FAQ_UNITS,
            "fill_value": FAQ_FILL,
            "drought_thresholds_in_file_docs": [],
        },
        "access": {
            "probes": probes,
            "download_notes": download_notes,
        },
        "gee_catalog": gee,
        "ucsb_tif_index": {
            k: tif_index[k]
            for k in tif_index
            if k != "months"
        } | (
            {"n_months_listed": tif_index.get("n_files")}
            if tif_index
            else {}
        ),
        "ucsb_year_index": year_index,
        "prelim_tif_index": prelim_index,
        "region_cuts": _cut_summary(regions),
        "ucsb_2026_check": ucsb_check,
        "regions": grid_counts,
        "verdicts": verdicts(pixels_ok),
        "next_forecast_step": (
            "Quand la vérité CHIRPS pluie est comptée : une prévision "
            "saisonnière datée de pluie (NMME découpé, ou un compte qui "
            "ouvre SEAS5 / C3S), comparée aux mois CHIRPS déjà comptés. "
            "Pas de BSS inventé si N < 10 saisons. Pas avant."
        ),
    }
    (out_dir / "chirps_counts.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    write_report(out_dir / "chirps_report.md", payload)
    print(json.dumps({
        "pixels_ok": pixels_ok,
        "n_probes": len(probes),
        "tif_files": tif_index.get("n_files"),
        "regions_measured": {
            k: v.get("usable_measured") for k, v in grid_counts.items()
        },
        "verdicts": payload["verdicts"],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
