# SPEI : comptes mesurés

Vérité catalogue : SPEI.
Cibles : Sécheresse Méditerranée / Sécheresse Inde / Sécheresse US.
Aucune prévision saisonnière notée. Champion Kalshi inchangé.
Aucun chiffre inventé. Pas de BSS.

## Accès mesuré

| URL | HTTP | Octets | Note |
|---|---:|---:|---|
| https://spei.csic.es/database.html |  |  | timeout 20s, 0 octet |
| https://spei.csic.es/spei_database_2_9/ |  |  | timeout 20s, 0 octet |
| https://spei.csic.es/spei_database_2_9/spei06.nc |  |  | timeout 20s, 0 octet |
| https://spei.csic.es/spei_database_2_10/ |  |  | timeout 20s, 0 octet |
| https://digital.csic.es/handle/10261/332007 | 200 | 84200 | réponse lue |
| https://digital.csic.es/handle/10261/364137 |  |  | erreur réseau : ConnectionError |
| https://doi.org/10.20350/digitalCSIC/15470 | 200 | 84200 | réponse lue |
| https://storage.googleapis.com/earthengine-stac/catalog/CSIC/CSIC_SPEI_2_11.json | 200 | 24756 | réponse lue |
| https://developers.google.com/earth-engine/datasets/catalog/CSIC_SPEI_2_11 | 200 | 8192 | réponse lue |
| https://earthengine.googleapis.com/v1/projects/earthengine-legacy/imageCollections/CSIC/SPEI/2_11 | 404 | 1623 | HTTP 404 |
| https://raw.githubusercontent.com/IPCC-WG1/Atlas/main/reference-regions/IPCC-WGI-reference-regions-v4_coordinates.csv | 200 | 6429 | réponse lue |
| https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson | 200 | 2325694 | réponse lue |

## Catalogue GEE (métadonnées, pas les pixels)

Id : `CSIC/SPEI/2_11`.
Titre : SPEIbase: Standardised Precipitation-Evapotranspiration Index database, Version 2.11.
Intervalle de temps publié : [['1901-01-01T00:00:00Z', '2025-01-01T00:00:00Z']].
Boîte spatiale : [[-180, -90, 180, 90]].
Cadence : {'interval': 1, 'type': 'cadence', 'unit': 'month'}.
SPEI-6 min/max publiés : -2.33 / 2.33 (estimated_range=False).
Licence : CC-BY-4.0.
DOI : 10.20350/digitalCSIC/16497.
Les pixels ne sont pas dans ce JSON.

## Fichier NetCDF compté (en-tête lu, pas inventé)

Nom : `spei06.nc`.
Chemin relatif : `data/truth/spei_cache/spei06.nc`.
Octets : 379643921.
Titre : Global 6-months SPEI, z-values, 0.5 degree.
Version (en-tête) : 2.10.0.
Dimensions : temps 1476, lat 360, lon 720.
Premier mois du fichier : 1901-01-16.
Dernier mois du fichier : 2023-12-16.
Trous de temps : [].
Résumé : Global dataset of the Standardized Precipitation-Evapotranspiration Index (SPEI) at the 6-months time scale. Using CRU TS 4.08 precipitation and potential evapotranspiration data.
Créé : Wed Jul 10 09:40:38 2024.
Institution : Consejo Superior de Investigaciones Científicas, CSIC.
Source en-tête : http://sac.csic.es/spei.

## Classes publiées (seuils seulement)

Guide WMO n° 1090 (SPI, même type de nombre que le SPEI) :

| Classe | Intervalle |
|---|---|
| extremely_dry | SPEI ≤ -2,0 |
| severely_dry | -2,0 < SPEI ≤ -1,5 |
| moderately_dry | -1,5 < SPEI ≤ -1,0 |
| near_normal | -1,0 < SPEI < 1,0 |
| moderately_wet | 1,0 ≤ SPEI < 1,5 |
| severely_wet | 1,5 ≤ SPEI < 2,0 |
| extremely_wet | SPEI ≥ 2,0 |

Seuil Phase B (compte seulement) : SPEI-6 ≤ -1.5.
Plage affichée CSIC/GEE : -2,33 à +2,33.

## Découpages publiés (polygones, pas les cases SPEI)

Méditerranée : IPCC MED, 1 polygone(s), sommets lus sur le CSV vivant = True.
US : Midwest + Southwest, 19 anneau(x) Natural Earth. États Midwest manquants : []. États Southwest manquants : [].
Inde : Maharashtra + Karnataka, 2 anneau(x). États manquants : [].
Ces anneaux ne sont pas un compte SPEI.

## Cellules par région

### Sécheresse Méditerranée

| Mesure | Valeur |
|---|---:|
| Cases dans le découpage publié | 3000 |
| Cases utilisables (au moins 1 mois fini) | 1969 |
| Cases jamais valides | 1031 |
| Premier mois du fichier | 1901-01-16 |
| Dernier mois du fichier | 2023-12-16 |
| Premier mois avec une valeur | 1901-06 |
| Dernier mois avec une valeur | 2023-12 |
| Mois avec au moins une case finie | 1471 |
| Mois sans aucune case finie | 5 |
| Années avec une valeur | 123 |
| Années manquantes dans l'intervalle du fichier | 0 |
| Mois-cellules finis | 2896399 |
| Mois-cellules SPEI <= -1,5 | 202374 |

Mois-cellules par classe WMO n° 1090 (valeurs finies seulement) :

| Classe | Mois-cellules |
|---|---:|
| extremely_dry | 45982 |
| severely_dry | 156392 |
| moderately_dry | 300451 |
| near_normal | 1907535 |
| moderately_wet | 291305 |
| severely_wet | 141812 |
| extremely_wet | 52922 |

### Sécheresse Inde

| Mesure | Valeur |
|---|---:|
| Cases dans le découpage publié | 170 |
| Cases utilisables (au moins 1 mois fini) | 170 |
| Cases jamais valides | 0 |
| Premier mois du fichier | 1901-01-16 |
| Dernier mois du fichier | 2023-12-16 |
| Premier mois avec une valeur | 1901-06 |
| Dernier mois avec une valeur | 2023-12 |
| Mois avec au moins une case finie | 1471 |
| Mois sans aucune case finie | 5 |
| Années avec une valeur | 123 |
| Années manquantes dans l'intervalle du fichier | 0 |
| Mois-cellules finis | 250070 |
| Mois-cellules SPEI <= -1,5 | 16207 |

Mois-cellules par classe WMO n° 1090 (valeurs finies seulement) :

| Classe | Mois-cellules |
|---|---:|
| extremely_dry | 3415 |
| severely_dry | 12792 |
| moderately_dry | 26944 |
| near_normal | 162881 |
| moderately_wet | 25856 |
| severely_wet | 13968 |
| extremely_wet | 4214 |

### Sécheresse US

| Mesure | Valeur |
|---|---:|
| Cases dans le découpage publié | 1204 |
| Cases utilisables (au moins 1 mois fini) | 1204 |
| Cases jamais valides | 0 |
| Premier mois du fichier | 1901-01-16 |
| Dernier mois du fichier | 2023-12-16 |
| Premier mois avec une valeur | 1901-06 |
| Dernier mois avec une valeur | 2023-12 |
| Mois avec au moins une case finie | 1471 |
| Mois sans aucune case finie | 5 |
| Années avec une valeur | 123 |
| Années manquantes dans l'intervalle du fichier | 0 |
| Mois-cellules finis | 1771084 |
| Mois-cellules SPEI <= -1,5 | 116285 |

Mois-cellules par classe WMO n° 1090 (valeurs finies seulement) :

| Classe | Mois-cellules |
|---|---:|
| extremely_dry | 25958 |
| severely_dry | 90327 |
| moderately_dry | 190577 |
| near_normal | 1154523 |
| moderately_wet | 188085 |
| severely_wet | 93126 |
| extremely_wet | 28488 |

## Verdicts (noms du catalogue, non renommés)

- SPEI : testée, ça aide
- Sécheresse Méditerranée : cible Tier 1 (pas encore testée)
- Sécheresse Inde : cible Tier 1 (pas encore testée)
- Sécheresse US : bloquée
- US Drought Monitor : testée, ça aide
- CHIRPS pluie : pas encore testée
- SEAS5 : pas encore testée
- C3S multi-modèle : pas encore testée
- NMME : bloquée
- Open-Meteo Seasonal : bloquée
- HURDAT2 / IBTrACS : testée, ça aide

Pas de score saisonnier dans ce run.
Pas de BSS inventé.
SEAS5 / C3S non ouverts (compte Copernicus).

Notes de téléchargement :
- https://digital.csic.es/handle/10261/364137 : ConnectionError
- https://doi.org/10.20350/digitalCSIC/15470 : ConnectionError
