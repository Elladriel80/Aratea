# CHIRPS pluie : la vérité pluie, comptée

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Mesure Phase 2. Vérité catalogue : **CHIRPS pluie**.
Cibles catalogue : **Sécheresse Méditerranée**, **Sécheresse Inde**.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle Kalshi en ligne n'a pas été changé. Aucun pari
avec de l'argent réel. Aucun chiffre n'a été inventé. On n'a pas noté
de prévision saisonnière. On n'a pas ouvert SEAS5 ni C3S (compte
Copernicus). On n'a pas inventé de BSS. On n'a pas inventé de seuil.

## Qu'est-ce que CHIRPS pluie

C'est une carte de pluie, mois par mois, faite par le Climate
Hazards Center (université de Californie, Santa Barbara), avec
l'aide de FEWS NET. Satellites plus stations. Uniquement sur la
terre, entre 50° sud et 50° nord.

Produit compté : **CHIRPS v2.0 mensuel**. Pas CHIRPS v3 (annoncé,
production v2 jusqu'à décembre 2026). Pas le produit rapide
« prelim ». Pas les dossiers EWX anomaly / zscore.

Ce qui est écrit dans la FAQ et le README, pas inventé :

- maille : 0,05 degré (7200 × 2000 cases)
- unité : millimètres par mois
- case vide : -9999
- depuis 1981 jusqu'à presque aujourd'hui
- version finale : vers la troisième semaine du mois suivant
- aucun seuil de sécheresse dans ces documents

On n'a donc pas classé les mois en « sec » ou « humide ». Ce n'est
pas un produit. Ce n'est pas un prix.

## D'où viennent les fichiers

Arbre officiel UCSB (gratuit, sans compte) :

https://data.chc.ucsb.edu/products/CHIRPS-2.0/

GeoTIFF mensuels finaux :

https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/

NetCDF par année :

https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/netcdf/byYear/

Page et FAQ :

https://www.chc.ucsb.edu/data/chirps
https://wiki.chc.ucsb.edu/CHIRPS_FAQ
https://data.chc.ucsb.edu/products/CHIRPS-2.0/README-CHIRPS.txt

Pour ouvrir seulement Méditerranée et Inde, ce run lit la même
série via IRI Data Library (public, sans compte) :

https://iridl.ldeo.columbia.edu/SOURCES/.UCSB/.CHIRPS/.v2p0/.monthly/.global/.precipitation/

NOAA ERDDAP copie la même série, mais cette machine est sur leur
liste noire (HTTP 403). On ne l'a pas utilisée pour les pixels.

Le gros fichier unique UCSB `chirps-v2.0.monthly.nc` fait
7 740 912 923 octets. On n'a lu que l'en-tête.

## Index officiel UCSB (noms de fichiers)

Lu sur l'index GeoTIFF mensuel final, le 12 septembre 2026 :

- 548 fichiers `chirps-v2.0.AAAA.MM.tif.gz`
- premier mois : janvier 1981
- dernier mois : août 2026
- **zéro mois manquant** dans cet intervalle
- 46 années civiles (1981 à 2026)
- 2026 n'a que janvier à août (déposé le 11 septembre 2026)

Index NetCDF par année : 46 fichiers, 1981 à 2026, **zéro année
manquante**. Le fichier 2026 pèse 114 544 358 octets (moins que
~163 Mo les autres années) : année encore incomplète.

Prelim mensuel (non compté) : 140 fichiers, janvier 2015 à
août 2026. Pas de septembre 2026 sur cet index.

## Les deux découpages (publiés, pas redessinés)

Même méthode que SPEI (PR 243).

Méditerranée : boîte IPCC AR6 WGI **MED**, sommets lus sur le CSV
vivant : (-10, 30), (-10, 45), (40, 45), (40, 30). 1 polygone.
Libellé publié : terre et mer.

Inde : Maharashtra et Karnataka seulement (pas toute l'Inde).
2 anneaux Natural Earth 50 m. Aucun État manquant.

Ces anneaux ne sont pas un compte CHIRPS. Le compte est plus bas.

## Cellules mesurées (IRI, janvier 1981 à juillet 2026)

Même série partout. **46 années** (1981 à 2026). **Zéro année
vide**. **547 mois** ouverts, tous avec au moins une case finie.
**Zéro mois vide**. Dernier mois IRI : juillet 2026.

| Zone | Cases du découpage | Cases utilisables | Cases jamais valides | Mois-cellules finis | Mois-cellules à 0 mm |
|---|---:|---:|---:|---:|---:|
| Sécheresse Méditerranée | 299 700 | 176 612 | 123 088 | 96 606 764 | 6 753 |
| Sécheresse Inde | 16 983 | 16 983 | 0 | 9 289 701 | 0 |

Méditerranée : la boîte publiée contient la mer. 123 088 cases
n'ont jamais de nombre (CHIRPS est sur la terre). On ne les
invente pas. On ne les remplace pas. 6 753 mois-cellules à 0 mm
sont de la vraie pluie nulle, pas un trou.

Inde : toutes les cases du découpage ont une valeur chaque mois.

## Août 2026 (fichier UCSB, pas mélangé)

IRI n'a pas donné août 2026. Le fichier officiel
`chirps-v2.0.2026.monthly.nc` (114 544 358 octets) a 8 mois,
janvier à août 2026. Autre grille, donc autre nombre de cases.
On ne mélange pas les deux totaux.

| Zone | Cases UCSB 2026 | Utilisables | Mois absents d'IRI |
|---|---:|---:|---|
| Sécheresse Méditerranée | 300 000 | 176 612 | 2026-08 |
| Sécheresse Inde | 16 978 | 16 978 | 2026-08 |

Les 176 612 cases utilisables Méditerranée sont les mêmes sur
les deux grilles. L'Inde change de 5 cases (bord du polygone).
On n'arrondit pas. On n'invente pas août dans le total IRI.

## On n'a pas noté de prévision

Pas de SEAS5. Pas de C3S. Pas de NMME découpé ici. Pas de BSS.
La gate (BSS > 0,05 sur au moins 10 saisons) n'est pas jouable
sans une prévision datée. On ne l'invente pas.

Ensuite, si on veut cette gate : une prévision saisonnière de
pluie datée, comparée aux mois CHIRPS déjà comptés. Pas avant.

## Verdicts (noms du catalogue, non renommés)

| Nom | Verdict |
|---|---|
| CHIRPS pluie | testée, ça aide |
| Sécheresse Méditerranée | cible Tier 1 (pas encore testée) |
| Sécheresse Inde | cible Tier 1 (pas encore testée) |
| Sécheresse US | bloquée |
| SPEI | testée, ça aide |
| US Drought Monitor | testée, ça aide |
| SEAS5 | pas encore testée |
| C3S multi-modèle | pas encore testée |
| NMME | bloquée |
| Open-Meteo Seasonal | bloquée |
| HURDAT2 / IBTrACS | testée, ça aide |

CHIRPS pluie aide : on a le vrai compte, région par région, de
1981 à 2026, sans chiffre inventé. Les deux cibles sécheresse
restent sans prévision notée.

## Décision

On ne change pas le modèle Kalshi en ligne.

Pourquoi : ce n'est pas un test Kalshi. C'est la vérité CHIRPS
pluie Phase 2. Compter la vérité n'est pas scorer une prévision.

## Comment relancer

Dans le dossier `predictor` :

```
python scripts/eval_chirps.py
```

Les comptes sont dans `data/truth/chirps/`.
Les gros fichiers restent locaux (`data/truth/chirps_cache/`).

Pas de changement du texte du site. Pas de trading réel.
