"""Vérité de résolution par station / Station-level resolution truth.

FR : Kalshi résout ses marchés température sur le rapport climatologique
quotidien du NWS (produit CLI) de la station ASOS nommée dans les règles.
Ce paquet fournit cette vérité (archive IEM), la fenêtre horaire exacte du
CLI (heure standard locale, jamais l'heure d'été) et des bins synthétiques
au format Kalshi pour mesurer le skill des prévisions sans dépendre de
l'existence d'un marché.

EN : Kalshi settles temperature markets on the NWS Daily Climate Report
(CLI product) of the ASOS station named in the rules. This package serves
that truth (IEM archive), the exact CLI observation window (local standard
time, never daylight time) and Kalshi-shaped synthetic bins so forecast
skill can be measured without a market existing.
"""
from .iem_cli import CliDay, IEMCliClient, station_for_series  # noqa: F401
from .lst_window import daily_extreme_lst, standard_utc_offset  # noqa: F401
from .synthetic_bins import kalshi_style_bins, prob_in_bin_gaussian  # noqa: F401
from .nowcast import prob_bin_nowcast  # noqa: F401
