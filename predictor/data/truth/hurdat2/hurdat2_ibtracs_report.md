# HURDAT2 / IBTrACS : comptes mesurés

Vérité catalogue : HURDAT2 / IBTrACS.
Cibles : Ouragan formation / intensité / landfall.
Aucune prévision NHC notée. Champion Kalshi inchangé.
Aucun chiffre inventé.

## HURDAT2 Atlantique (NHC)

Fichier : `hurdat2-1851-2025-02272026.txt`.
URL : https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2025-02272026.txt.
SHA256 : `1b9b0c7beed5b4505838658b1d30e159fc84330c60891a58cfcf43ae55c37202`.

| Mesure | Valeur |
|---|---:|
| Systèmes | 2004 |
| Première année | 1851 |
| Dernière année | 2025 |
| Années avec au moins 1 système | 175 |
| Années manquantes dans l'intervalle | 0 |
| Atteint TS / SS / HU (nommés) | 1773 |
| Atteint HU | 978 |
| Majeur (vent ≥ 96 kt) | 342 |
| Au moins un drapeau L | 732 |
| Points L | 1175 |
| Landfall L en statut HU | 376 |
| Landfall L majeur (vent ≥ 96 kt) | 131 |
| Vent max manquant | 0 |
| Erreurs de parse | 0 |
| Saisons named ≥ 18 | 13 |
| Saisons ACE ≥ 159 | 21 |
| Saisons avec landfall HU (L) | 139 |
| Saisons avec landfall majeur (L) | 89 |

Pic d'intensité (échelle officielle NHC, nœuds) :

| Pic | Systèmes |
|---|---:|
| TD | 228 |
| TS | 777 |
| 1 | 398 |
| 2 | 259 |
| 3 | 164 |
| 4 | 133 |
| 5 | 45 |

Le drapeau L de HURDAT2 marque le centre qui croise une côte. Le PDF de format NHC dit que les landfalls des États-Unis continentaux sont marqués 1851-1970 et depuis 1991 ; les landfalls hors États-Unis seulement 1951-1970 et depuis 1991. On ne redessine pas la côte. On ne sépare pas US / ailleurs.

## IBTrACS Atlantique nord (NCEI v04r01)

Fichier : `ibtracs.NA.list.v04r01.csv`.
URL : https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.NA.list.v04r01.csv.
SHA256 : `cff31db40e816f949475639fc1359699ae597abac8c0b5e4972d7edffcb7418e`.

| Mesure | Valeur |
|---|---:|
| Systèmes dans le fichier | 2299 |
| Systèmes comptés (hors spur) | 2273 |
| Spur exclus | 26 |
| Dont provisoires | 5 |
| Première saison | 1851 |
| Dernière saison | 2026 |
| Saisons manquantes dans l'intervalle | 0 |
| Nommés (USA_STATUS TS/SS/HU/HR) | 1774 |
| Ouragan (USA_STATUS HU/HR) | 977 |
| USA_SSHS ≥ 1 | 977 |
| Majeur (USA_SSHS ≥ 3 ou vent ≥ 96 kt) | 343 |
| LANDFALL = 0 | 1242 |
| Points LANDFALL = 0 | 14931 |
| USA_RECORD L | 731 |
| Points USA_RECORD L | 1177 |
| Erreurs de parse | 0 |

Pic USA_SSHS (échelle publiée NCEI) :

| Pic | Systèmes |
|---|---:|
| unknown | 262 |
| post_tropical | 1 |
| misc_disturbance | 3 |
| subtropical | 32 |
| tropical_depression | 231 |
| tropical_storm | 767 |
| 1 | 375 |
| 2 | 259 |
| 3 | 165 |
| 4 | 133 |
| 5 | 45 |

LANDFALL=0 : le centre croise une terre du masque NCEI (continents et îles > 1400 km²) dans les 3 heures. USA_RECORD L : même drapeau que HURDAT2. Ce n'est pas seulement les États-Unis.

## Recouvrement des identifiants ATCF

Même ID : 1998. HURDAT2 sans ID IBTrACS : 6. IBTrACS avec ID hors HURDAT2 : 13. IBTrACS sans USA_ATCF_ID : 262.

## Verdicts (noms du catalogue, non renommés)

- HURDAT2 / IBTrACS : testée, ça aide
- Ouragan formation : cible Tier 1 (pas encore testée)
- Ouragan intensité : cible Tier 1 (pas encore testée)
- Ouragan landfall : cible Tier 1 (pas encore testée)
- NHC a-decks / b-decks : pas encore testée
- Marché ouragan Kalshi : pas encore testée
- SEAS5 : pas encore testée
- C3S multi-modèle : pas encore testée
- Régime ENSO : pas encore testée
- Sécheresse Méditerranée : cible Tier 1 (pas encore testée)
- Sécheresse Inde : cible Tier 1 (pas encore testée)

Pas de score NHC a-decks / b-decks dans ce run.
Pas de BSS inventé pour la sécheresse US.
