# Marché ouragan Kalshi : comptes mesurés

Variable catalogue : Marché ouragan Kalshi.
Lecture seule. Champion Kalshi inchangé. Aucun chiffre inventé.

## Inventaire Kalshi (API publique)

| Mesure | Valeur |
|---|---:|
| Séries climat ouragan | 59 |
| Événements | 181 |
| Contrats | 381 |
| Contrats avec volume > 0 | 266 |
| Contrats avec un ask > 0 | 381 |
| Contrats bid et ask > 0 | 202 |
| Contrats réglés oui/non | 96 |
| Réglés avec un prix milieu | 96 |
| Saisons notables (prix + HURDAT2 ≤ 2025) | 0 |
| Barre pour noter | 10 |
| Trop mince pour noter | oui |

Zéro saison réglée avec un prix public et une vérité HURDAT2 officielle (fichier arrêté à 2025). Les événements 2022-2025 existent sans marchés. La saison 2026 a des prix mais pas de HURDAT2 officiel.

Séries avec volume ou cotation : KXFIRSTHURRICANE, KXHURCAL, KXHURCAT, KXHURCTOT, KXHURCTOTMAJ, KXHURPATHHAWAII, KXHURPATHNC, KXHURRICANE, KXHURRICANENAMES, KXNEXTCAT5HURDATE, KXNEXTHURDATE.

Années lues dans les titres des comptes saisonniers : 2022, 2023, 2024, 2025, 2026.

## Climato HURDAT2 (PR 241, même fichier)

Fichier : `hurdat2-1851-2025-02272026.txt`.
URL : https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-02272026.txt.
Comptes PR 241 : 2004 systèmes, 978 HU, 342 majeurs, 376 landfalls HU, 1851 a 2025.
Relu ici : 2004 systèmes, 978 HU, 342 majeurs, 376 landfalls HU, 1851 a 2025. Identique PR 241 : oui.

## Prix 2026 contre P(count > K) HURDAT2

Fenêtre Kalshi : 1er janvier au 1er décembre. On compte aussi l'année civile complète. Ce n'est pas un score : 2026 n'est pas dans HURDAT2 officiel.

| Contrat | Seuil | Prix milieu | Climato au 1er déc. | Climato année | Écart milieu − climato 1er déc. |
|---|---:|---:|---:|---:|---:|
| KXHURCTOT-26DEC01-T9 | 9 | 0.0050 | 0.0971 | 0.0971 | -0.0921 |
| KXHURCTOT-26DEC01-T8 | 8 | 0.0050 | 0.1371 | 0.1371 | -0.1321 |
| KXHURCTOT-26DEC01-T7 | 7 | 0.0150 | 0.1829 | 0.1886 | -0.1679 |
| KXHURCTOT-26DEC01-T6 | 6 | 0.0450 | 0.3200 | 0.3257 | -0.2750 |
| KXHURCTOT-26DEC01-T5 | 5 | 0.0500 | 0.4629 | 0.4629 | -0.4129 |
| KXHURCTOT-26DEC01-T4 | 4 | 0.0750 | 0.5829 | 0.5886 | -0.5079 |
| KXHURCTOT-26DEC01-T15 | 15 | 0.0050 | 0.0000 | 0.0000 | 0.0050 |
| KXHURCTOT-26DEC01-T12 | 12 | 0.0050 | 0.0114 | 0.0114 | -0.0064 |
| KXHURCTOT-26DEC01-T10 | 10 | 0.0050 | 0.0457 | 0.0514 | -0.0407 |
| KXHURCTOTMAJ-26DEC01-T7 | 7 | 0.0100 | 0.0000 | 0.0000 | 0.0100 |
| KXHURCTOTMAJ-26DEC01-T6 | 6 | 0.0100 | 0.0114 | 0.0114 | -0.0014 |
| KXHURCTOTMAJ-26DEC01-T5 | 5 | 0.0100 | 0.0457 | 0.0457 | -0.0357 |
| KXHURCTOTMAJ-26DEC01-T4 | 4 | 0.0250 | 0.0971 | 0.0971 | -0.0721 |
| KXHURCTOTMAJ-26DEC01-T3 | 3 | 0.0450 | 0.1600 | 0.1600 | -0.1150 |
| KXHURCTOTMAJ-26DEC01-T2 | 2 | 0.0950 | 0.2857 | 0.2857 | -0.1907 |
| KXHURCTOTMAJ-26DEC01-T1 | 1 | 0.1550 | 0.5429 | 0.5429 | -0.3879 |
| KXHURCTOTMAJ-26DEC01-T0 | 0 | 0.4100 | 0.8114 | 0.8114 | -0.4014 |

## Verdicts (noms du catalogue, non renommés)

- Marché ouragan Kalshi : bloquée
- NHC a-decks / b-decks : testée, ça aide
- Ouragan formation : bloquée
- Ouragan intensité : testée, ça aide
- Ouragan landfall : bloquée
- HURDAT2 / IBTrACS : testée, ça aide
- Sécheresse Méditerranée : cible Tier 1 (pas encore testée)
- Sécheresse Inde : cible Tier 1 (pas encore testée)

Pas de BSS inventé pour la sécheresse.
