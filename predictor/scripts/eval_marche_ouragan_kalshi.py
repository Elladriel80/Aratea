"""eval_marche_ouragan_kalshi.py — Marché ouragan Kalshi, puis NHC decks.

FR : 1) Inventaire public Kalshi (lecture seule). 2) Prix 2026 contre la
climato HURDAT2 déjà comptée (PR 241). 3) Si le livre est trop mince pour
noter : a-decks / b-decks NHC contre le même HURDAT2. Champion inchangé.
Aucun chiffre inventé. Pas Méditerranée / Inde. Pas de BSS sécheresse.

Usage:
    python scripts/eval_marche_ouragan_kalshi.py
    python scripts/eval_marche_ouragan_kalshi.py --skip-fetch
    python scripts/eval_marche_ouragan_kalshi.py --skip-fetch --skip-decks
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # pragma: no cover
    pass

from src.config import DATA_DIR  # noqa: E402
from src.kalshi.client import KalshiClient  # noqa: E402
from src.truth.hurdat2_atl import (  # noqa: E402
    PR241_HU, PR241_HU_LANDFALL_L, PR241_MAJOR, PR241_SYSTEMS, PR241_YEARS,
    Hurdat2Client, coverage_counts, season_rows,
)
from src.truth.kalshi_hurricane import (  # noqa: E402
    CATALOGUE_MARKET, MIN_SEASONS_TO_SCORE, playability, price_vs_climato,
    series_inventory, settlement_digest,
)
from src.truth.nhc_decks import (  # noqa: E402
    CATALOGUE_DECKS, NhcDeckClient, score_decks,
)

OUT_DIR = DATA_DIR / "truth" / "kalshi_hurricane"
DECK_OUT = DATA_DIR / "truth" / "nhc_decks"
DEFAULT_DECK_FIRST = 2008
DEFAULT_DECK_LAST = 2025


def verdicts(play: dict[str, Any], decks: Optional[dict[str, Any]]) -> dict[str, str]:
    """Catalogue names unchanged. No invented BSS."""
    if play.get("playable_to_score"):
        market = "testée, ça aide"
    elif play.get("too_thin_to_score"):
        market = "bloquée"
    else:
        market = "testée, ça n'aide pas"

    decks_v = "pas encore testée"
    intensity_v = "cible Tier 1 (pas encore testée)"
    if decks is not None:
        overall = (decks.get("intensity") or {}).get("overall") or {}
        if overall.get("n", 0) == 0:
            decks_v = "bloquée"
            intensity_v = "bloquée"
        elif overall.get("ofcl_beats_ocd5"):
            decks_v = "testée, ça aide"
            intensity_v = "testée, ça aide"
        else:
            decks_v = "testée, ça n'aide pas"
            intensity_v = "testée, ça n'aide pas"

    if decks is None:
        formation_v = "cible Tier 1 (pas encore testée)"
        landfall_v = "cible Tier 1 (pas encore testée)"
    else:
        # Genesis is not in a-decks. Binary landfall would need a coastline.
        formation_v = "bloquée"
        landfall_v = "bloquée"
        if decks.get("first_hu_timing", {}).get("genesis_scored"):
            formation_v = "testée, ça aide"
        if decks.get("landfall", {}).get("binary_landfall_scored"):
            landfall_v = "testée, ça aide"

    return {
        CATALOGUE_MARKET: market,
        CATALOGUE_DECKS: decks_v,
        "Ouragan formation": formation_v,
        "Ouragan intensité": intensity_v,
        "Ouragan landfall": landfall_v,
        "HURDAT2 / IBTrACS": "testée, ça aide",
        "Sécheresse Méditerranée": "cible Tier 1 (pas encore testée)",
        "Sécheresse Inde": "cible Tier 1 (pas encore testée)",
    }


def write_kalshi_report(path: Path, payload: dict[str, Any]) -> None:
    play = payload["playability"]
    cov = payload["hurdat2"]["coverage"]
    lines = [
        f"# {CATALOGUE_MARKET} : comptes mesurés",
        "",
        f"Variable catalogue : {CATALOGUE_MARKET}.",
        "Lecture seule. Champion Kalshi inchangé. Aucun chiffre inventé.",
        "",
        "## Inventaire Kalshi (API publique)",
        "",
        "| Mesure | Valeur |",
        "|---|---:|",
        f"| Séries climat ouragan | {play['n_series']} |",
        f"| Événements | {play['n_events']} |",
        f"| Contrats | {play['n_markets']} |",
        f"| Contrats avec volume > 0 | {play['n_markets_volume_gt0']} |",
        f"| Contrats avec un ask > 0 | {play['n_quoted_two_sided']} |",
        f"| Contrats bid et ask > 0 | {play.get('n_quoted_bid_and_ask_positive', 0)} |",
        f"| Contrats réglés oui/non | {play['n_settled_yes_no']} |",
        f"| Réglés avec un prix milieu | {play['n_settled_with_mid']} |",
        f"| Saisons notables (prix + HURDAT2 ≤ 2025) | {play['n_seasons_settled_with_public_mid_and_hurdat2']} |",
        f"| Barre pour noter | {play['min_seasons_to_score']} |",
        f"| Trop mince pour noter | {'oui' if play['too_thin_to_score'] else 'non'} |",
        "",
        play["reason"],
        "",
        "Séries avec volume ou cotation : "
        + (", ".join(play["live_series_tickers"]) or "(aucune)")
        + ".",
        "",
        "Années lues dans les titres des comptes saisonniers : "
        + (", ".join(str(y) for y in play["count_event_years_from_title"]) or "(aucune)")
        + ".",
        "",
        "## Climato HURDAT2 (PR 241, même fichier)",
        "",
        f"Fichier : `{payload['hurdat2']['source']['filename']}`.",
        f"URL : {payload['hurdat2']['source']['url']}.",
        f"Comptes PR 241 : {PR241_SYSTEMS} systèmes, {PR241_HU} HU, "
        f"{PR241_MAJOR} majeurs, {PR241_HU_LANDFALL_L} landfalls HU, "
        f"{PR241_YEARS[0]}–{PR241_YEARS[1]}.",
        f"Relu ici : {cov['n_systems']} systèmes, {cov['n_hurricanes_HU']} HU, "
        f"{cov['n_major_sshws']} majeurs, {cov['n_hu_landfall_L']} landfalls HU, "
        f"{cov['first_year']}–{cov['last_year']}. "
        f"Identique PR 241 : {'oui' if cov.get('matches_pr241') else 'non'}.",
        "",
        "## Prix 2026 contre P(count > K) HURDAT2",
        "",
        "Fenêtre Kalshi : 1er janvier au 1er décembre. On compte aussi "
        "l'année civile complète. Ce n'est pas un score : 2026 n'est pas "
        "dans HURDAT2 officiel.",
        "",
        "| Contrat | Seuil | Prix milieu | Climato au 1er déc. | Climato année | Écart milieu − climato 1er déc. |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["price_vs_climato"]:
        mid = row["mid"]
        p_dec = row["climato_through_dec1"]["p"]
        p_full = row["climato_full_year"]["p"]
        diff = row["mid_minus_climato_dec1"]
        lines.append(
            f"| {row['ticker']} | {row['threshold_more_than']} | "
            f"{'' if mid is None else f'{mid:.4f}'} | "
            f"{'' if p_dec is None else f'{p_dec:.4f}'} | "
            f"{'' if p_full is None else f'{p_full:.4f}'} | "
            f"{'' if diff is None else f'{diff:.4f}'} |"
        )
    lines += [
        "",
        "## Verdicts (noms du catalogue, non renommés)",
        "",
    ]
    for name, status in payload["verdicts"].items():
        lines.append(f"- {name} : {status}")
    lines += ["", "Pas de BSS inventé pour la sécheresse.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_deck_report(path: Path, payload: dict[str, Any]) -> None:
    d = payload["decks"]
    inten = d["intensity"]
    overall = inten.get("overall") or {}
    hu = d["first_hu_timing"]
    land = d["landfall"]
    btk = d["bdeck_vs_hurdat2"]
    lines = [
        f"# {CATALOGUE_DECKS} : comptes mesurés",
        "",
        "Prévision officielle OFCL et climato-persistance OCD5, contre HURDAT2.",
        "Archives : https://ftp.nhc.noaa.gov/atcf/archive/",
        "",
        "| Mesure | Valeur |",
        "|---|---:|",
        f"| Années demandées | {payload['deck_years'][0]}–{payload['deck_years'][1]} |",
        f"| Tempêtes a-deck | {d['n_adeck_storms']} |",
        f"| Tempêtes b-deck | {d['n_bdeck_storms']} |",
        f"| Recouvrement HURDAT2 | {d['n_hurdat2_overlap']} |",
        f"| Paires intensité (OFCL+OCD5+HURDAT2) | {inten.get('n', 0)} |",
        f"| Saisons intensité | {inten.get('n_seasons', 0)} |",
        f"| MAE OFCL (kt) | {overall.get('ofcl_mae_kt')} |",
        f"| MAE OCD5 (kt) | {overall.get('ocd5_mae_kt')} |",
        f"| OFCL plus proche que OCD5 | {overall.get('n_ofcl_closer')} |",
        f"| Égalité | {overall.get('n_tie')} |",
        f"| OCD5 plus proche | {overall.get('n_ocd5_closer')} |",
        f"| MAE b-deck vs HURDAT2 (kt) | {btk.get('mae_kt')} |",
        f"| Points L avec OFCL à la même heure | {land.get('n_ofcl_at_exact_L_time')} |",
        f"| Écart trajectoire au L (km) | {land.get('mae_km')} |",
        "",
        "Par échéance (heures) :",
        "",
        "| Lead | N | MAE OFCL | MAE OCD5 | OFCL bat OCD5 |",
        "|---|---:|---:|---:|---|",
    ]
    for lead, row in (inten.get("by_lead") or {}).items():
        beat = "oui" if row.get("ofcl_beats_ocd5") else "non"
        lines.append(
            f"| {lead} | {row['n']} | {row['ofcl_mae_kt']:.3f} | "
            f"{row['ocd5_mae_kt']:.3f} | {beat} |"
        )
    lines += [
        "",
        "## Formation",
        "",
        hu["genesis_block_reason"],
        f"Ouragans HURDAT2 dans la fenêtre : {hu['n_hurdat2_reached_hu']}. "
        f"A-deck qui commence après le premier point HURDAT2 : "
        f"{hu['n_adeck_starts_after_first_hurdat2_point']}.",
        "",
        "## Landfall",
        "",
        land["binary_block_reason"],
        "",
        "## Verdicts",
        "",
    ]
    for name, status in payload["verdicts"].items():
        lines.append(f"- {name} : {status}")
    lines += ["", "Pas de BSS inventé.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skip-fetch", action="store_true")
    p.add_argument("--skip-decks", action="store_true")
    p.add_argument("--out-dir", default=str(OUT_DIR))
    p.add_argument("--deck-out-dir", default=str(DECK_OUT))
    p.add_argument("--hurdat-cache", default="")
    p.add_argument("--deck-cache", default="")
    p.add_argument("--inventory-json", default="")
    p.add_argument("--deck-first-year", type=int, default=DEFAULT_DECK_FIRST)
    p.add_argument("--deck-last-year", type=int, default=DEFAULT_DECK_LAST)
    args = p.parse_args()
    out_dir = Path(args.out_dir)
    deck_out = Path(args.deck_out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    deck_out.mkdir(parents=True, exist_ok=True)

    print(CATALOGUE_MARKET, flush=True)
    if args.inventory_json:
        raw_inv = json.loads(Path(args.inventory_json).read_text(encoding="utf-8"))
        inventory = raw_inv["inventory"] if isinstance(raw_inv, dict) and "inventory" in raw_inv else raw_inv
    elif args.skip_fetch and (out_dir / "kalshi_hurricane_inventory.json").exists():
        raw_inv = json.loads((out_dir / "kalshi_hurricane_inventory.json").read_text(encoding="utf-8"))
        inventory = raw_inv["inventory"]
        print("Kalshi inventory from disk ...", flush=True)
    else:
        print("Kalshi series ...", flush=True)
        inventory = series_inventory(KalshiClient(), allow_network=not args.skip_fetch)

    play = playability(inventory)
    print(json.dumps({k: play[k] for k in (
        "n_series", "n_events", "n_markets", "n_seasons_settled_with_public_mid_and_hurdat2",
        "too_thin_to_score",
    )}, indent=2), flush=True)

    print("HURDAT2 Atlantique ...", flush=True)
    h_kwargs: dict[str, Any] = {}
    if args.hurdat_cache:
        h_kwargs["cache_dir"] = Path(args.hurdat_cache)
    h_raw = Hurdat2Client(**h_kwargs).fetch_atlantic(allow_network=not args.skip_fetch)
    storms = h_raw["storms"]
    cov = coverage_counts(storms, h_raw["gaps"])
    rows_full = season_rows(storms)
    rows_dec1 = season_rows(storms, through_md=(12, 1))
    prices = price_vs_climato(inventory, rows_full, rows_dec1)

    decks_payload = None
    decks_fetch = None
    if not args.skip_decks and play.get("too_thin_to_score"):
        print(f"{CATALOGUE_DECKS} {args.deck_first_year}-{args.deck_last_year} ...", flush=True)
        d_kwargs: dict[str, Any] = {}
        if args.deck_cache:
            d_kwargs["cache_dir"] = Path(args.deck_cache)
        decks_fetch = NhcDeckClient(**d_kwargs).fetch_range(
            args.deck_first_year, args.deck_last_year,
            allow_network=not args.skip_fetch,
        )
        decks_payload = score_decks(
            decks_fetch["adecks"], decks_fetch["bdecks"], storms,
        )
        decks_payload["years_with_adeck_listing"] = decks_fetch["years_with_adeck_listing"]
        decks_payload["missing_a_n"] = len(decks_fetch["missing_a"])
        decks_payload["missing_b_n"] = len(decks_fetch["missing_b"])
        decks_payload["archive"] = decks_fetch["archive"]

    verd = verdicts(play, decks_payload)
    payload = {
        "catalogue": CATALOGUE_MARKET,
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "champion_switched": False,
        "real_money": False,
        "playability": play,
        "settlement": settlement_digest(inventory),
        "inventory": inventory,
        "price_vs_climato": prices,
        "hurdat2": {
            "source": h_raw["source"],
            "sha256": h_raw["sha256"],
            "coverage": cov,
            "n_seasons_full": len(rows_full),
            "n_seasons_dec1": len(rows_dec1),
        },
        "decks": decks_payload,
        "deck_years": [args.deck_first_year, args.deck_last_year],
        "verdicts": verd,
        "min_seasons_to_score": MIN_SEASONS_TO_SCORE,
    }
    (out_dir / "kalshi_hurricane_inventory.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8"
    )
    write_kalshi_report(out_dir / "kalshi_hurricane_report.md", payload)
    if decks_payload is not None:
        slim = {
            "catalogue": CATALOGUE_DECKS,
            "as_of": payload["as_of"],
            "champion_switched": False,
            "decks": decks_payload,
            "deck_years": payload["deck_years"],
            "hurdat2_coverage": cov,
            "verdicts": verd,
            "missing_a": (decks_fetch or {}).get("missing_a", []),
            "missing_b": (decks_fetch or {}).get("missing_b", []),
        }
        (deck_out / "nhc_decks_counts.json").write_text(
            json.dumps(slim, indent=2, default=str), encoding="utf-8"
        )
        write_deck_report(deck_out / "nhc_decks_report.md", {**payload, "decks": decks_payload})

    print(json.dumps({
        "playable_to_score": play["playable_to_score"],
        "n_seasons_scored": play["n_seasons_settled_with_public_mid_and_hurdat2"],
        "hurdat2_match_pr241": cov.get("matches_pr241"),
        "decks_n": None if decks_payload is None else decks_payload["intensity"].get("n"),
        "verdicts": verd,
    }, indent=2, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
