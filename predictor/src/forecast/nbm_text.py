"""Parseur des bulletins texte NBM (NBP / NBS / NBE).

FR : Le National Blend of Models publie, station par station, le max et le
min du jour déjà corrigés pour cette station. Le bulletin NBP donne cinq
seuils (10, 25, 50, 75, 90 %) plus la moyenne et l'écart-type. NBS et NBE
donnent le chiffre unique (TXN) et son écart-type (XND).

Rien n'est inventé : une case vide ou -99 est une absence. Les heures
viennent du bulletin (FHR depuis l'heure d'émission). Le max NBM est le
chiffre imprimé à 00 UTC du lendemain ; le min est le chiffre imprimé à
12 UTC du jour.

EN : Parser for NBM station text bulletins. Missing values stay missing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Iterable, Optional

MISSING = -99

HEADER_RE = re.compile(
    r"^[ \t]*(?P<station>[A-Z0-9]{3,6})\s+NBM V(?P<ver>[\d.]+)\s+"
    r"(?P<product>NB[PSEXH]) GUIDANCE\s+"
    r"(?P<mon>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})\s+"
    r"(?P<hhmm>\d{3,4})\s+UTC",
    re.M,
)

# NBP percentile rows → probability mass at or below the printed value.
NBP_PERCENTILE_ROWS = {
    "TXNP1": 0.10,
    "TXNP2": 0.25,
    "TXNP5": 0.50,
    "TXNP7": 0.75,
    "TXNP9": 0.90,
}
NBP_MEAN_ROW = "TXNMN"
NBP_SD_ROW = "TXNSD"
NBE_POINT_ROW = "TXN"
NBE_SD_ROW = "XND"

TXN_ROWS = frozenset(
    {NBP_MEAN_ROW, NBP_SD_ROW, NBE_POINT_ROW, NBE_SD_ROW} | set(NBP_PERCENTILE_ROWS)
)


@dataclass(frozen=True)
class NbmDaily:
    """Une prévision NBM de max ou min pour un jour cible."""
    station: str
    product: str                 # NBP | NBS | NBE
    issued: datetime             # UTC
    target: date
    variable: str                # temp_max | temp_min
    lead: int                    # jours calendaires cible − émission
    fhr: int
    mean_f: Optional[float] = None
    sd_f: Optional[float] = None
    p10: Optional[float] = None
    p25: Optional[float] = None
    p50: Optional[float] = None
    p75: Optional[float] = None
    p90: Optional[float] = None

    def percentiles(self) -> list[tuple[float, float]]:
        """Paires (valeur °F, proba ≤ valeur), sans trou, croissant."""
        raw = [
            (self.p10, 0.10), (self.p25, 0.25), (self.p50, 0.50),
            (self.p75, 0.75), (self.p90, 0.90),
        ]
        pts = [(float(v), p) for v, p in raw if v is not None]
        pts.sort(key=lambda t: (t[0], t[1]))
        return pts

    def center_f(self) -> Optional[float]:
        if self.p50 is not None:
            return float(self.p50)
        if self.mean_f is not None:
            return float(self.mean_f)
        return None

    def to_compact(self) -> dict:
        return {
            "station": self.station, "product": self.product,
            "issued": self.issued.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "target": self.target.isoformat(), "variable": self.variable,
            "lead": self.lead, "fhr": self.fhr,
            "mean": self.mean_f, "sd": self.sd_f,
            "p10": self.p10, "p25": self.p25, "p50": self.p50,
            "p75": self.p75, "p90": self.p90,
        }


@dataclass
class _Column:
    fhr: int
    valid: datetime
    values: dict = field(default_factory=dict)   # row name → float


def _parse_hhmm(hhmm: str) -> int:
    n = int(hhmm)
    if n <= 23:          # "13" or "7"
        return n
    return n // 100      # "1300"


def _to_number(tok: str) -> Optional[float]:
    tok = tok.strip()
    if not tok or tok in (".", "/"):
        return None
    try:
        v = float(tok)
    except ValueError:
        return None
    if v == MISSING:
        return None
    return v


def _split_row(line: str) -> tuple[str, list[Optional[float]]]:
    """Nom d'élément (6 premiers caractères utiles) + valeurs par case."""
    raw = line.rstrip("\n")
    if not raw.strip():
        return "", []
    name = raw[:6].strip().upper()
    rest = raw[6:]
    out: list[Optional[float]] = []
    for chunk in rest.split("|"):
        toks = chunk.split()
        if not toks:
            out.append(None)
            continue
        for tok in toks:
            out.append(_to_number(tok))
    return name, out


def _issued_from_header(m: re.Match) -> datetime:
    hour = _parse_hhmm(m.group("hhmm"))
    return datetime(
        int(m.group("year")), int(m.group("mon")), int(m.group("day")),
        hour, 0, 0, tzinfo=timezone.utc,
    )


def _blocks(text: str) -> list[tuple[re.Match, str]]:
    matches = list(HEADER_RE.finditer(text))
    out: list[tuple[re.Match, str]] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((m, text[m.start():end]))
    return out


def parse_bulletin(text: str, stations: Optional[Iterable[str]] = None) -> list[NbmDaily]:
    """Lit un bulletin national (ou un extrait) et renvoie les max/min NBM.

    `stations` filtre les ICAO voulus (ex. les 18 villes Kalshi). Sans filtre,
    toutes les stations du fichier sont lues.
    """
    wanted = {s.strip().upper() for s in stations} if stations else None
    rows: list[NbmDaily] = []
    for header, block in _blocks(text):
        station = header.group("station").upper()
        if wanted is not None and station not in wanted:
            continue
        product = header.group("product")
        issued = _issued_from_header(header)
        parsed = _parse_block(station, product, issued, block)
        rows.extend(parsed)
    return rows


def extract_station_blocks(text: str, stations: Iterable[str]) -> dict[str, str]:
    """Garde le texte brut de chaque station demandée (pour le cache)."""
    wanted = {s.strip().upper() for s in stations}
    found: dict[str, str] = {}
    for header, block in _blocks(text):
        station = header.group("station").upper()
        if station in wanted:
            found[station] = block.strip() + "\n"
    return found


def _parse_block(station: str, product: str, issued: datetime, block: str) -> list[NbmDaily]:
    fhrs: list[Optional[float]] = []
    by_row: dict[str, list[Optional[float]]] = {}
    for line in block.splitlines():
        name, vals = _split_row(line)
        if name == "FHR":
            fhrs = vals
        elif name in TXN_ROWS:
            by_row[name] = vals
    if not fhrs or not by_row:
        return []

    n = len(fhrs)
    cols: list[_Column] = []
    for i, fhr_v in enumerate(fhrs):
        if fhr_v is None:
            continue
        fhr = int(fhr_v)
        valid = issued + timedelta(hours=fhr)
        values = {}
        for name, vals in by_row.items():
            if i < len(vals) and vals[i] is not None:
                values[name] = vals[i]
        if values:
            cols.append(_Column(fhr=fhr, valid=valid, values=values))
        n = max(n, i + 1)

    out: list[NbmDaily] = []
    for col in cols:
        mapped = _map_txn_column(col.valid)
        if mapped is None:
            continue
        variable, target = mapped
        lead = (target - issued.date()).days
        v = col.values
        out.append(NbmDaily(
            station=station, product=product, issued=issued,
            target=target, variable=variable, lead=lead, fhr=col.fhr,
            mean_f=_first(v, NBP_MEAN_ROW, NBE_POINT_ROW),
            sd_f=_first(v, NBP_SD_ROW, NBE_SD_ROW),
            p10=v.get("TXNP1"), p25=v.get("TXNP2"), p50=v.get("TXNP5"),
            p75=v.get("TXNP7"), p90=v.get("TXNP9"),
        ))
    return out


def _first(values: dict, *keys: str) -> Optional[float]:
    for k in keys:
        if k in values:
            return values[k]
    return None


def _map_txn_column(valid: datetime) -> Optional[tuple[str, date]]:
    """Max imprimé à 00 UTC du lendemain ; min imprimé à 12 UTC du jour.

    Fenêtre NBM (doc v5.0) : min 00–18 UTC, max 12 UTC → 06 UTC lendemain.
    Ce n'est pas la fenêtre minuit–minuit du CLI. On le garde tel quel :
    c'est le chiffre station que le NBM publie.
    """
    hour = valid.hour
    d = valid.date()
    if hour == 0:
        return "temp_max", d - timedelta(days=1)
    if hour == 12:
        return "temp_min", d
    return None


def from_compact(row: dict) -> NbmDaily:
    issued = datetime.strptime(row["issued"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return NbmDaily(
        station=row["station"], product=row["product"], issued=issued,
        target=date.fromisoformat(row["target"]), variable=row["variable"],
        lead=int(row["lead"]), fhr=int(row["fhr"]),
        mean_f=row.get("mean"), sd_f=row.get("sd"),
        p10=row.get("p10"), p25=row.get("p25"), p50=row.get("p50"),
        p75=row.get("p75"), p90=row.get("p90"),
    )
