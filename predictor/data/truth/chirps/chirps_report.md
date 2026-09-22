# CHIRPS pluie : comptes mesurés

Vérité catalogue : CHIRPS pluie.
Cibles : Sécheresse Méditerranée / Sécheresse Inde.
Aucune prévision saisonnière notée. Champion Kalshi inchangé.
Aucun chiffre inventé. Pas de BSS. Pas de seuil inventé.

## Accès mesuré

| URL | HTTP | Octets | Note |
|---|---:|---:|---|
| https://www.chc.ucsb.edu/data/chirps | 200 | 21104 | réponse lue |
| https://data.chc.ucsb.edu/products/CHIRPS-2.0/README-CHIRPS.txt | 200 | 9639 | réponse lue |
| https://wiki.chc.ucsb.edu/CHIRPS_FAQ | 200 | 8192 | réponse lue |
| https://data.chc.ucsb.edu/products/CHIRPS-2.0/ | 200 | 7005 | réponse lue |
| https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/ | 200 | 8192 | réponse lue |
| https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/ | 200 | 1602 | réponse lue |
| https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/byYear/ | 200 | 8192 | réponse lue |
| https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/chirps-v2.0.monthly.nc | 200 | 7740912923 | NetCDF / HDF (en-tête, fichier non entièrement lu ici) |
| https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly_EWX/ | 200 | 1849 | réponse lue |
| https://data.chc.ucsb.edu/products/CHIRPS-2.0/prelim/global_monthly/tifs/ | 200 | 8192 | réponse lue |
| https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.monthly/.global/.precipitation/ | 200 | 4080 | page IRI (pas les pixels) |
| https://storage.googleapis.com/earthengine-stac/catalog/UCSB-CHG/UCSB-CHG_CHIRPS_PENTAD.json | 200 | 5131 | réponse lue |
| https://raw.githubusercontent.com/IPCC-WG1/Atlas/main/reference-regions/IPCC-WGI-reference-regions-v4_coordinates.csv | 200 | 6429 | réponse lue |
| https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson | 200 | 2325694 | réponse lue |
| https://www.chc.ucsb.edu/data/chirps3 | 200 | 33971 | réponse lue |

## Produit publié (docs, pas inventé)

Nom : CHIRPS v2.0 mensuel, UCSB Climate Hazards.
Résolution publiée (FAQ) : 0.05 degré.
Grille publiée : 7200 × 2000 (50S-50N).
Latitude publiée : -50.0 à 50.0.
Unités : mm/month.
Valeur manquante : -9999.0.
Seuils de sécheresse dans le README / la FAQ / l'en-tête : aucun.
Les dossiers EWX anomaly / zscore existent à part. On ne les a pas notés.
CHIRPS v3 est annoncé (https://www.chc.ucsb.edu/data/chirps3). Ce compte est v2.

## Index officiel UCSB (noms de fichiers, pas les pixels)

GeoTIFF mensuels finaux : 548 fichiers, 1981-01 à 2026-08.
Mois manquants dans cet intervalle : 0.
Liste des trous : [].
Source : https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/.

NetCDF par année : 46 fichiers, 1981 à 2026.
Années manquantes : [].
Source : https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/byYear/.

Prelim mensuel (non compté) : 140 fichiers, 2015-01 à 2026-08.

## Catalogue GEE (métadonnées pentade, pas les pixels)

Id : `UCSB-CHG/CHIRPS/PENTAD`.
Titre : CHIRPS Precipitation Pentad: Climate Hazards Center InfraRed Precipitation With Station Data (Version 2.0 Final).
Intervalle de temps publié : [['1981-01-01T00:00:00Z', '2026-07-26T00:00:00Z']].
Boîte spatiale : [[-180, -50, 180, 50]].
Cadence : {'description': 'Each asset spans a pentad. Each of first 5 pentads in a month\nhave 5 days. The last pentad contains all the days from the 26th to the\nend of the month.\n', 'interval': 1, 'name': 'pentad', 'type': 'cadence', 'unit': 'custom_time_unit'}.
Licence / termes : public domain (texte GEE).
Les pixels ne sont pas dans ce JSON. Ce n'est pas le fichier mensuel.

## Découpages publiés (polygones, pas les cases CHIRPS)

Méditerranée : IPCC MED, 1 polygone(s), sommets lus sur le CSV vivant = True.
Inde : Maharashtra + Karnataka, 2 anneau(x). États manquants : [].
Ces anneaux ne sont pas un compte CHIRPS.

## Cellules par région

### Sécheresse Méditerranée

| Mesure | Valeur |
|---|---:|
| Cases dans le découpage publié | 299700 |
| Cases utilisables (au moins 1 mois fini) | 176612 |
| Cases jamais valides | 123088 |
| Premier mois ouvert | 1981-01 |
| Dernier mois ouvert | 2026-07 |
| Premier mois avec une valeur | 1981-01 |
| Dernier mois avec une valeur | 2026-07 |
| Mois avec au moins une case finie | 547 |
| Mois sans aucune case finie | 0 |
| Années avec une valeur | 46 |
| Années manquantes dans l'intervalle ouvert | 0 |
| Mois-cellules finis | 96606764 |
| Mois-cellules à 0 mm (valeur réelle, pas un trou) | 6753 |

### Sécheresse Inde

| Mesure | Valeur |
|---|---:|
| Cases dans le découpage publié | 16983 |
| Cases utilisables (au moins 1 mois fini) | 16983 |
| Cases jamais valides | 0 |
| Premier mois ouvert | 1981-01 |
| Dernier mois ouvert | 2026-07 |
| Premier mois avec une valeur | 1981-01 |
| Dernier mois avec une valeur | 2026-07 |
| Mois avec au moins une case finie | 547 |
| Mois sans aucune case finie | 0 |
| Années avec une valeur | 46 |
| Années manquantes dans l'intervalle ouvert | 0 |
| Mois-cellules finis | 9289701 |
| Mois-cellules à 0 mm (valeur réelle, pas un trou) | 0 |

## Contrôle UCSB 2026 (fichier officiel par année, autre grille)

Fichier : `data/truth/chirps_cache/ucsb_2026.monthly.nc` (114544358 octets).
Ce n'est pas mélangé avec les totaux IRI. Grilles un peu différentes.

Sécheresse Méditerranée : 8 mois (2026-01 à 2026-08), 300000 cases, 176612 utilisables, mois absents d'IRI ['2026-08'].
Sécheresse Inde : 8 mois (2026-01 à 2026-08), 16978 cases, 16978 utilisables, mois absents d'IRI ['2026-08'].

## Verdicts (noms du catalogue, non renommés)

- CHIRPS pluie : testée, ça aide
- Sécheresse Méditerranée : cible Tier 1 (pas encore testée)
- Sécheresse Inde : cible Tier 1 (pas encore testée)
- Sécheresse US : bloquée
- SPEI : testée, ça aide
- US Drought Monitor : testée, ça aide
- SEAS5 : pas encore testée
- C3S multi-modèle : pas encore testée
- NMME : bloquée
- Open-Meteo Seasonal : bloquée
- HURDAT2 / IBTrACS : testée, ça aide

Pas de score saisonnier dans ce run.
Pas de BSS inventé.
SEAS5 / C3S non ouverts (compte Copernicus).

Notes de téléchargement :
- Sécheresse Méditerranée : grille 306 lat × 1005 lon, 299700 cases du découpage, fichier data/truth/chirps_cache/iri_med_1981.nc
- Sécheresse Inde : grille 213 lat × 170 lon, 16983 cases du découpage, fichier data/truth/chirps_cache/iri_inde_1981.nc
- UCSB 2026 Sécheresse Méditerranée : 8 mois, dernier 2026-08, mois absents d'IRI ['2026-08']
- UCSB 2026 Sécheresse Inde : 8 mois, dernier 2026-08, mois absents d'IRI ['2026-08']
