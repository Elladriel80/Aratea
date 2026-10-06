"""enso.py — official CPC RONI inventory (no forecast skill).

FR : Compte la série officielle NOAA / CPC (RONI depuis le 1er février
2026). Seuils lus sur la page CPC, pas inventés. Pas de score Kalshi.
Pas de prévision saisonnière.

EN : Inventory of the official NOAA CPC Relative Oceanic Niño Index.
Thresholds are quoted from CPC. No Kalshi score. No seasonal forecast.

Official sources (do not substitute another index without saying so):

- Series file: https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt
- Definition page: https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/
- Official switch (1 Feb 2026): NWS PNS 26-05
  https://www.weather.gov/media/notification/pdf_2026/pns26-05_Relative_ONI.pdf

Quoted CPC wording (RONI page, fetched 2026-09-12):

- "Warm (red) and cold (blue) periods based on a threshold of +/- 0.5°C
  for the Relative Oceanic Niño Index (RONI)"
- "Warm value: The three month running average where the Relative
  Oceanic Niño Index (RONI) is greater than 0.5 degrees Celsius
  (El Niño)."
- "Cold value: The three month running average where the Relative
  Oceanic Niño Index (RONI) is less than -0.5 degrees Celsius
  (La Niña)."
- "For historical purposes, periods of below and above normal SSTs are
  colored in blue and red when the threshold is met for a minimum of
  five (5) consecutive overlapping seasons."

A season with RONI exactly ±0.5 is therefore neutre (not greater than
0.5, not less than -0.5). CPC classifies overlapping 3-month seasons,
not calendar years.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

RONI_ASCII_URL = "https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt"
RONI_PAGE_URL = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/"
PNS_26_05_URL = (
    "https://www.weather.gov/media/notification/pdf_2026/pns26-05_Relative_ONI.pdf"
)
ONI_HISTORICAL_PAGE_URL = (
    "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/"
)

# Published CPC RONI-page thresholds. Do not change without a new CPC quote.
WARM_GT = 0.5
COLD_LT = -0.5
MIN_CONSECUTIVE_SEASONS = 5

SEASON_ORDER = (
    "DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ",
    "JJA", "JAS", "ASO", "SON", "OND", "NDJ",
)
SEASON_MONTHS = {
    "DJF": ("Dec", "Jan", "Feb"),
    "JFM": ("Jan", "Feb", "Mar"),
    "FMA": ("Feb", "Mar", "Apr"),
    "MAM": ("Mar", "Apr", "May"),
    "AMJ": ("Apr", "May", "Jun"),
    "MJJ": ("May", "Jun", "Jul"),
    "JJA": ("Jun", "Jul", "Aug"),
    "JAS": ("Jul", "Aug", "Sep"),
    "ASO": ("Aug", "Sep", "Oct"),
    "SON": ("Sep", "Oct", "Nov"),
    "OND": ("Oct", "Nov", "Dec"),
    "NDJ": ("Nov", "Dec", "Jan"),
}

PHASE_EL_NINO = "el_nino"
PHASE_LA_NINA = "la_nina"
PHASE_NEUTRE = "neutre"


@dataclass(frozen=True)
class RoniSeason:
    season: str
    year: int
    anom: float
    value_phase: str
    in_official_episode: bool = False
    episode_phase: str | None = None
    episode_id: int | None = None

    @property
    def label(self) -> str:
        return f"{self.season} {self.year}"


@dataclass
class OfficialEpisode:
    episode_id: int
    phase: str
    start_season: str
    start_year: int
    end_season: str
    end_year: int
    n_seasons: int
    peak_anom: float
    open_at_end: bool = False

    @property
    def start_label(self) -> str:
        return f"{self.start_season} {self.start_year}"

    @property
    def end_label(self) -> str:
        return f"{self.end_season} {self.end_year}"


def value_phase(anom: float) -> str:
    """One overlapping season, CPC RONI-page wording (strict > / <)."""
    if anom > WARM_GT:
        return PHASE_EL_NINO
    if anom < COLD_LT:
        return PHASE_LA_NINA
    return PHASE_NEUTRE


def parse_roni_ascii(text: str) -> list[RoniSeason]:
    """Parse the official CPC `RONI.ascii.txt` (`SEAS YR ANOM`)."""
    rows: list[RoniSeason] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.upper().startswith("SEAS"):
            continue
        parts = line.split()
        if len(parts) < 3:
            raise ValueError(f"ligne RONI illisible: {raw!r}")
        season, year_s, anom_s = parts[0], parts[1], parts[2]
        if season not in SEASON_MONTHS:
            raise ValueError(f"saison CPC inconnue: {season!r}")
        year = int(year_s)
        anom = float(anom_s)
        rows.append(RoniSeason(
            season=season, year=year, anom=anom,
            value_phase=value_phase(anom),
        ))
    return rows


def _season_key(season: str, year: int) -> tuple[int, int]:
    return (year, SEASON_ORDER.index(season))


def next_season(season: str, year: int) -> tuple[str, int]:
    i = SEASON_ORDER.index(season)
    if i == len(SEASON_ORDER) - 1:
        return SEASON_ORDER[0], year + 1
    return SEASON_ORDER[i + 1], year


def expected_seasons(first: RoniSeason, last: RoniSeason) -> list[tuple[str, int]]:
    out = [(first.season, first.year)]
    while out[-1] != (last.season, last.year):
        out.append(next_season(*out[-1]))
        if len(out) > 2000:
            raise RuntimeError("séquence de saisons trop longue")
    return out


def find_gaps(rows: Iterable[RoniSeason]) -> list[dict]:
    """Missing overlapping seasons inside the file span. Trailing open year is separate."""
    seq = list(rows)
    if not seq:
        return [{"kind": "empty_file"}]
    keys = {_season_key(r.season, r.year) for r in seq}
    expected = expected_seasons(seq[0], seq[-1])
    missing = []
    for season, year in expected:
        key = _season_key(season, year)
        if key not in keys:
            missing.append({
                "kind": "hole",
                "season": season,
                "year": year,
                "label": f"{season} {year}",
            })
    dups = []
    seen: dict[tuple[int, int], int] = {}
    for r in seq:
        k = _season_key(r.season, r.year)
        seen[k] = seen.get(k, 0) + 1
    for k, n in seen.items():
        if n > 1:
            dups.append({
                "kind": "duplicate",
                "season": SEASON_ORDER[k[1]],
                "year": k[0],
                "n": n,
            })
    return missing + dups


def mark_official_episodes(rows: list[RoniSeason]) -> tuple[list[RoniSeason], list[OfficialEpisode]]:
    """Color a run only if it has ≥ 5 consecutive same-sign threshold seasons."""
    if not rows:
        return [], []
    marked = [RoniSeason(**asdict(r)) for r in rows]
    episodes: list[OfficialEpisode] = []
    i = 0
    eid = 0
    n = len(marked)
    while i < n:
        phase = marked[i].value_phase
        if phase == PHASE_NEUTRE:
            i += 1
            continue
        j = i + 1
        while j < n and marked[j].value_phase == phase:
            j += 1
        length = j - i
        if length >= MIN_CONSECUTIVE_SEASONS:
            eid += 1
            peak = marked[i].anom
            for k in range(i, j):
                if phase == PHASE_EL_NINO:
                    peak = max(peak, marked[k].anom)
                else:
                    peak = min(peak, marked[k].anom)
                marked[k] = RoniSeason(
                    season=marked[k].season,
                    year=marked[k].year,
                    anom=marked[k].anom,
                    value_phase=marked[k].value_phase,
                    in_official_episode=True,
                    episode_phase=phase,
                    episode_id=eid,
                )
            episodes.append(OfficialEpisode(
                episode_id=eid,
                phase=phase,
                start_season=marked[i].season,
                start_year=marked[i].year,
                end_season=marked[j - 1].season,
                end_year=marked[j - 1].year,
                n_seasons=length,
                peak_anom=peak,
                open_at_end=(j == n),
            ))
        i = j
    return marked, episodes


def _year_roll(rows: list[RoniSeason]) -> list[dict]:
    by_year: dict[int, list[RoniSeason]] = {}
    for r in rows:
        by_year.setdefault(r.year, []).append(r)
    out = []
    for year in sorted(by_year):
        group = by_year[year]
        n_el = sum(1 for r in group if r.value_phase == PHASE_EL_NINO)
        n_la = sum(1 for r in group if r.value_phase == PHASE_LA_NINA)
        n_ne = sum(1 for r in group if r.value_phase == PHASE_NEUTRE)
        n_el_ep = sum(1 for r in group if r.episode_phase == PHASE_EL_NINO)
        n_la_ep = sum(1 for r in group if r.episode_phase == PHASE_LA_NINA)
        if n_el and n_la:
            mix = "el_nino_et_la_nina"
        elif n_el:
            mix = "el_nino"
        elif n_la:
            mix = "la_nina"
        else:
            mix = "neutre"
        out.append({
            "year": year,
            "n_seasons_in_file": len(group),
            "complete_year": len(group) == 12,
            "n_el_nino_seasons": n_el,
            "n_la_nina_seasons": n_la,
            "n_neutre_seasons": n_ne,
            "n_official_el_nino_seasons": n_el_ep,
            "n_official_la_nina_seasons": n_la_ep,
            "value_mix": mix,
        })
    return out


def inventory(rows: list[RoniSeason]) -> dict:
    """Measured counts only. No skill score."""
    marked, episodes = mark_official_episodes(rows)
    gaps = find_gaps(rows)
    years = _year_roll(marked)
    n_el = sum(1 for r in marked if r.value_phase == PHASE_EL_NINO)
    n_la = sum(1 for r in marked if r.value_phase == PHASE_LA_NINA)
    n_ne = sum(1 for r in marked if r.value_phase == PHASE_NEUTRE)
    n_el_ep = sum(1 for r in marked if r.episode_phase == PHASE_EL_NINO)
    n_la_ep = sum(1 for r in marked if r.episode_phase == PHASE_LA_NINA)
    n_ne_ep = sum(1 for r in marked if not r.in_official_episode)
    years_el = [y["year"] for y in years if y["n_el_nino_seasons"]]
    years_la = [y["year"] for y in years if y["n_la_nina_seasons"]]
    years_ne_only = [y["year"] for y in years if y["value_mix"] == "neutre"]
    years_both = [y["year"] for y in years if y["value_mix"] == "el_nino_et_la_nina"]
    years_incomplete = [y["year"] for y in years if not y["complete_year"]]
    trailing = []
    if marked:
        last_complete = 12 if marked[-1].season == "NDJ" else SEASON_ORDER.index(marked[-1].season) + 1
        if last_complete < 12:
            missing_tail = []
            s, y = marked[-1].season, marked[-1].year
            while True:
                s, y = next_season(s, y)
                if y != marked[-1].year:
                    break
                missing_tail.append(f"{s} {y}")
            trailing.append({
                "kind": "year_not_finished",
                "year": marked[-1].year,
                "last_present": marked[-1].label,
                "missing_seasons": missing_tail,
                "n_present": last_complete,
                "n_missing": 12 - last_complete,
            })
    short_warm_runs = _short_runs(marked, PHASE_EL_NINO)
    short_cold_runs = _short_runs(marked, PHASE_LA_NINA)
    return {
        "source": {
            "index": "RONI",
            "agency": "NOAA / NCEP CPC",
            "official_since": "2026-02-01",
            "ascii": RONI_ASCII_URL,
            "page": RONI_PAGE_URL,
            "pns": PNS_26_05_URL,
            "older_oni_page_not_counted": ONI_HISTORICAL_PAGE_URL,
            "thresholds_quoted": {
                "warm_el_nino": "RONI > 0.5 °C",
                "cold_la_nina": "RONI < -0.5 °C",
                "neutre": "-0.5 ≤ RONI ≤ 0.5",
                "official_episode": (
                    f"{MIN_CONSECUTIVE_SEASONS} saisons qui se chevauchent d'affilée"
                ),
            },
        },
        "coverage": {
            "first": marked[0].label if marked else None,
            "last": marked[-1].label if marked else None,
            "first_year": marked[0].year if marked else None,
            "last_year": marked[-1].year if marked else None,
            "n_calendar_years": len(years),
            "n_seasons": len(marked),
            "n_expected_seasons_in_span": (
                len(expected_seasons(marked[0], marked[-1])) if marked else 0
            ),
            "n_holes": sum(1 for g in gaps if g.get("kind") == "hole"),
            "n_duplicates": sum(1 for g in gaps if g.get("kind") == "duplicate"),
            "gaps": gaps,
            "trailing_open_year": trailing,
        },
        "seasons_by_value": {
            "el_nino": n_el,
            "la_nina": n_la,
            "neutre": n_ne,
        },
        "seasons_by_official_episode": {
            "el_nino": n_el_ep,
            "la_nina": n_la_ep,
            "hors_episode": n_ne_ep,
        },
        "years_by_value": {
            "n_years_with_el_nino_season": len(years_el),
            "n_years_with_la_nina_season": len(years_la),
            "n_years_neutre_only": len(years_ne_only),
            "n_years_with_both": len(years_both),
            "n_years_incomplete": len(years_incomplete),
            "years_with_el_nino_season": years_el,
            "years_with_la_nina_season": years_la,
            "years_neutre_only": years_ne_only,
            "years_with_both": years_both,
            "years_incomplete": years_incomplete,
        },
        "episodes": [asdict(e) | {
            "start_label": e.start_label,
            "end_label": e.end_label,
        } for e in episodes],
        "n_el_nino_episodes": sum(1 for e in episodes if e.phase == PHASE_EL_NINO),
        "n_la_nina_episodes": sum(1 for e in episodes if e.phase == PHASE_LA_NINA),
        "short_runs_below_5": {
            "el_nino": short_warm_runs,
            "la_nina": short_cold_runs,
        },
        "years": years,
        "seasons": [asdict(r) | {"label": r.label, "months": list(SEASON_MONTHS[r.season])}
                    for r in marked],
    }


def _short_runs(rows: list[RoniSeason], phase: str) -> list[dict]:
    """Threshold seasons that never reach the official 5-season coloring."""
    out = []
    i = 0
    n = len(rows)
    while i < n:
        if rows[i].value_phase != phase:
            i += 1
            continue
        j = i + 1
        while j < n and rows[j].value_phase == phase:
            j += 1
        length = j - i
        if length < MIN_CONSECUTIVE_SEASONS:
            out.append({
                "phase": phase,
                "start_label": rows[i].label,
                "end_label": rows[j - 1].label,
                "n_seasons": length,
                "reason": (
                    f"moins de {MIN_CONSECUTIVE_SEASONS} saisons d'affilée "
                    "(CPC ne colorie pas l'épisode)"
                ),
            })
        i = j
    return out
