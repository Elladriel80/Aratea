"""eval_spei.py : vérité SPEI (Méditerranée / Inde / US).

FR : Compte d'abord la vérité catalogue « SPEI ». Pas de prévision
saisonnière. Pas de SEAS5 / C3S. Pas de BSS. Le champion Kalshi n'est
pas touché. Aucun chiffre inventé.

Usage:
    python scripts/eval_spei.py
    python scripts/eval_spei.py --skip-fetch
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

from src.truth.spei import (  # noqa: E402
    CATALOGUE_TRUTH, DEFAULT_TIMESCALE, DIGITAL_CSIC_V29, DIGITAL_CSIC_V210,
    DIGITAL_CSIC_V29_DOI,
    GEE_HTML_211, GEE_STAC_211, IPCC_REGIONS_CSV, NE_ADMIN1_URL,
    PHASE_B_DRY_THRESHOLD, SPEI_CSIC_PAGE, SPEI_OUT, TARGET_INDE, TARGET_MED,
    TARGET_US, VICENTE_2010, WMO_SPI_GUIDE, WMO_SPI_CLASSES, SpeiClient,
    empty_region_row, gee_catalog_excerpt, inventory_from_netcdf,
    regions_from_sources,
)

TARGETS = (TARGET_MED, TARGET_INDE, TARGET_US)


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
    spei = "testée, ça aide" if pixels_ok else "bloquée"
    return {
        CATALOGUE_TRUTH: spei,
        TARGET_MED: "cible Tier 1 (pas encore testée)",
        TARGET_INDE: "cible Tier 1 (pas encore testée)",
        TARGET_US: "bloquée",
        "US Drought Monitor": "testée, ça aide",
        "CHIRPS pluie": "pas encore testée",
        "SEAS5": "pas encore testée",
        "C3S multi-modèle": "pas encore testée",
        "NMME": "bloquée",
        "Open-Meteo Seasonal": "bloquée",
        "HURDAT2 / IBTrACS": "testée, ça aide",
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    probes = payload["access"]["probes"]
    gee = payload.get("gee_catalog") or {}
    lines = [
        f"# {CATALOGUE_TRUTH} : comptes mesurés",
        "",
        f"Vérité catalogue : {CATALOGUE_TRUTH}.",
        "Cibles : Sécheresse Méditerranée / Sécheresse Inde / Sécheresse US.",
        "Aucune prévision saisonnière notée. Champion Kalshi inchangé.",
        "Aucun chiffre inventé. Pas de BSS.",
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
        "## Catalogue GEE (métadonnées, pas les pixels)",
        "",
    ]
    header = payload.get("spei_file") or {}
    if gee:
        lines += [
            f"Id : `{gee.get('id')}`.",
            f"Titre : {gee.get('title')}.",
            f"Intervalle de temps publié : {gee.get('temporal_interval')}.",
            f"Boîte spatiale : {gee.get('spatial_bbox')}.",
            f"Cadence : {gee.get('cadence')}.",
            f"SPEI-6 min/max publiés : {gee.get('spei06_min')} / {gee.get('spei06_max')} "
            f"(estimated_range={gee.get('spei06_range_is_estimated')}).",
            f"Licence : {gee.get('license')}.",
            f"DOI : {gee.get('doi')}.",
            "Les pixels ne sont pas dans ce JSON.",
            "",
        ]
    else:
        lines += ["Catalogue GEE non lu.", ""]
    lines += [
        "## Fichier NetCDF compté (en-tête lu, pas inventé)",
        "",
    ]
    if header.get("filename"):
        lines += [
            f"Nom : `{header.get('filename')}`.",
            f"Chemin relatif : `{header.get('path')}`.",
            f"Octets : {header.get('n_bytes')}.",
            f"Titre : {header.get('title')}.",
            f"Version (en-tête) : {header.get('version')}.",
            f"Dimensions : temps {header.get('n_times')}, lat {header.get('n_lat')}, "
            f"lon {header.get('n_lon')}.",
            f"Premier mois du fichier : {header.get('first_month')}.",
            f"Dernier mois du fichier : {header.get('last_month')}.",
            f"Trous de temps : {header.get('time_gaps')}.",
            f"Résumé : {header.get('summary')}.",
            f"Créé : {header.get('date_created')}.",
            f"Institution : {header.get('institution')}.",
            f"Source en-tête : {header.get('source')}.",
            "",
        ]
    else:
        lines += ["Aucun fichier SPEI compté dans ce run.", ""]
    lines += [
        "## Classes publiées (seuils seulement)",
        "",
        "Guide WMO n° 1090 (SPI, même type de nombre que le SPEI) :",
        "",
        "| Classe | Intervalle |",
        "|---|---|",
        "| extremely_dry | SPEI ≤ -2,0 |",
        "| severely_dry | -2,0 < SPEI ≤ -1,5 |",
        "| moderately_dry | -1,5 < SPEI ≤ -1,0 |",
        "| near_normal | -1,0 < SPEI < 1,0 |",
        "| moderately_wet | 1,0 ≤ SPEI < 1,5 |",
        "| severely_wet | 1,5 ≤ SPEI < 2,0 |",
        "| extremely_wet | SPEI ≥ 2,0 |",
        "",
        f"Seuil Phase B (compte seulement) : SPEI-6 ≤ {PHASE_B_DRY_THRESHOLD}.",
        "Plage affichée CSIC/GEE : -2,33 à +2,33.",
        "",
        "## Découpages publiés (polygones, pas les cases SPEI)",
        "",
    ]
    cuts = payload.get("region_cuts") or {}
    med = cuts.get(TARGET_MED) or {}
    us = cuts.get(TARGET_US) or {}
    inde = cuts.get(TARGET_INDE) or {}
    lines += [
        f"Méditerranée : IPCC MED, {med.get('n_rings')} polygone(s), "
        f"sommets lus sur le CSV vivant = {med.get('vertices_from_live_csv')}.",
        f"US : Midwest + Southwest, {us.get('n_rings')} anneau(x) Natural Earth. "
        f"États Midwest manquants : {us.get('midwest_missing')}. "
        f"États Southwest manquants : {us.get('southwest_missing')}.",
        f"Inde : Maharashtra + Karnataka, {inde.get('n_rings')} anneau(x). "
        f"États manquants : {inde.get('inde_missing')}.",
        "Ces anneaux ne sont pas un compte SPEI.",
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
                f"Non mesuré. Raison : {row.get('reason', 'fichier SPEI absent')}."
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
            f"| Premier mois du fichier | {row.get('first_month')} |",
            f"| Dernier mois du fichier | {row.get('last_month')} |",
            f"| Premier mois avec une valeur | {row.get('first_month_with_a_value')} |",
            f"| Dernier mois avec une valeur | {row.get('last_month_with_a_value')} |",
            f"| Mois avec au moins une case finie | {row.get('n_months_with_any_valid')} |",
            f"| Mois sans aucune case finie | {row.get('n_months_without_any_valid')} |",
            f"| Années avec une valeur | {row.get('n_calendar_years_with_a_value')} |",
            f"| Années manquantes dans l'intervalle du fichier | {row.get('n_missing_years_in_span')} |",
            f"| Mois-cellules finis | {row.get('n_finite_cell_months')} |",
            f"| Mois-cellules SPEI <= -1,5 | {row.get('n_cell_months_spei_le_minus_1_5')} |",
            "",
        ]
        classes = row.get("wmo_class_cell_months") or {}
        if classes:
            lines += [
                "Mois-cellules par classe WMO n° 1090 (valeurs finies seulement) :",
                "",
                "| Classe | Mois-cellules |",
                "|---|---:|",
            ]
            for name, _, _ in WMO_SPI_CLASSES:
                lines.append(f"| {name} | {classes.get(name)} |")
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


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skip-fetch", action="store_true")
    p.add_argument("--out-dir", default=str(SPEI_OUT))
    p.add_argument("--cache-dir", default="")
    p.add_argument("--spei-nc", default="")
    args = p.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    kwargs: dict[str, Any] = {}
    if args.cache_dir:
        kwargs["cache_dir"] = Path(args.cache_dir)
    client = SpeiClient(**kwargs)

    print(CATALOGUE_TRUTH, flush=True)
    probes: list[dict[str, Any]] = []
    gee_raw: dict[str, Any] = {}
    ipcc_csv: str | None = None
    ne_geo: dict[str, Any] | None = None
    download_notes: list[str] = []
    if not args.skip_fetch:
        print("sondes HTTP ...", flush=True)
        probes = client.probe_all()
        try:
            gee_raw = client.fetch_json(GEE_STAC_211)
        except Exception as exc:
            probes.append({
                "url": GEE_STAC_211,
                "ok": False,
                "note": f"relecture JSON : {type(exc).__name__}",
            })
        try:
            ipcc_csv = client.fetch_text(IPCC_REGIONS_CSV)
        except Exception:
            ipcc_csv = None
        try:
            ne_geo = client.fetch_json(NE_ADMIN1_URL)
        except Exception:
            ne_geo = None
        for page in (DIGITAL_CSIC_V210, DIGITAL_CSIC_V29_DOI):
            try:
                html = client.fetch_text(page)
            except Exception as exc:
                download_notes.append(f"{page} : {type(exc).__name__}")
                continue
            links = client.bitstream_urls(html, page)
            spei_links = [u for u in links if "spei06" in u.lower()]
            download_notes.append(
                f"{page} : {len(links)} lien(s) bitstream, "
                f"{len(spei_links)} nommé(s) spei06"
            )
            if spei_links and not client.cached_spei06():
                try:
                    path = client.download_spei06(spei_links[0])
                    download_notes.append(f"téléchargé {path} depuis {spei_links[0]}")
                except Exception as exc:
                    download_notes.append(
                        f"téléchargement spei06 échoué : {type(exc).__name__}: {exc}"
                    )
    else:
        print("sondes HTTP ignorées (--skip-fetch)", flush=True)

    gee = gee_catalog_excerpt(gee_raw) if gee_raw else {}
    regions = regions_from_sources(ipcc_csv, ne_geo)

    nc_path = Path(args.spei_nc) if args.spei_nc else client.cached_spei06()
    pixel_error = ""
    grid_counts: dict[str, Any] = {}
    pixels_ok = False
    file_header: dict[str, Any] = {}
    if nc_path and nc_path.exists():
        print(f"grille {nc_path} ...", flush=True)
        try:
            grid_counts, file_header = inventory_from_netcdf(
                nc_path, regions, timescale_months=DEFAULT_TIMESCALE
            )
            file_header["path"] = _rel_to_predictor(nc_path)
            pixels_ok = any(r.get("usable_measured") for r in grid_counts.values())
        except Exception as exc:
            pixel_error = f"{type(exc).__name__}: {exc}"
            grid_counts = {
                name: empty_region_row(name, pixel_error) for name in TARGETS
            }
    else:
        reason = (
            "Fichier SPEIbase spei06.nc absent du cache. "
            "spei.csic.es : timeout, 0 octet. "
            "DIGITAL.CSIC : page parfois lue, fichier .nc non obtenu. "
            "GEE : catalogue seulement, API pixels 404. "
            "Aucun compte de cellules n'est inventé."
        )
        grid_counts = {name: empty_region_row(name, reason) for name in TARGETS}

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
        "timescale_months": DEFAULT_TIMESCALE,
        "sources": {
            "csic_page": SPEI_CSIC_PAGE,
            "digital_csic_v29": DIGITAL_CSIC_V29,
            "digital_csic_v210": DIGITAL_CSIC_V210,
            "gee_stac": GEE_STAC_211,
            "gee_html": GEE_HTML_211,
            "ipcc_med": IPCC_REGIONS_CSV,
            "natural_earth_admin1": NE_ADMIN1_URL,
            "vicente_2010": VICENTE_2010,
            "wmo_spi": WMO_SPI_GUIDE,
        },
        "published_classes": {
            "wmo_spi": [
                {"name": n, "lo": lo, "hi": hi} for n, lo, hi in WMO_SPI_CLASSES
            ],
            "phase_b_spei6_le": PHASE_B_DRY_THRESHOLD,
        },
        "access": {
            "probes": probes,
            "spei06_local": _rel_to_predictor(nc_path) if nc_path else None,
            "pixel_error": pixel_error or None,
            "download_notes": download_notes,
        },
        "gee_catalog": gee,
        "spei_file": file_header,
        "region_cuts": {
            name: {
                k: spec[k]
                for k in spec
                if k != "rings" and k != "midwest" and k != "southwest" and k != "states"
            }
            | (
                {
                    "n_rings": len(spec.get("rings") or []),
                    "midwest_missing": (spec.get("midwest") or {}).get("missing_names"),
                    "southwest_missing": (spec.get("southwest") or {}).get("missing_names"),
                    "inde_missing": (spec.get("states") or {}).get("missing_names"),
                }
            )
            for name, spec in regions.items()
        },
        "regions": grid_counts,
        "verdicts": verdicts(pixels_ok),
        "next_forecast_step": (
            "Quand la vérité SPEI est comptée : une prévision saisonnière "
            "datée (NMME découpé, ou un compte qui ouvre SEAS5 / C3S), "
            "comparée à SPEI-6, sans inventer de BSS si N < 10 saisons."
        ),
    }
    (out_dir / "spei_counts.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    write_report(out_dir / "spei_report.md", payload)
    print(json.dumps({
        "pixels_ok": pixels_ok,
        "n_probes": len(probes),
        "gee_id": gee.get("id"),
        "regions_measured": {
            k: v.get("usable_measured") for k, v in grid_counts.items()
        },
        "verdicts": payload["verdicts"],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
