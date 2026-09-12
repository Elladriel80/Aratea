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

## Index officiel UCSB (noms de fichiers)

Lu sur l'index GeoTIFF mensuel final, le 12 septembre 2026 :

- 548 fichiers `chirps-v2.0.AAAA.MM.tif.gz`
- premier mois : janvier 1981
- dernier mois : août 2026
- **zéro mois manquant** dans cet intervalle
- 46 années civiles (1981 à 2026)
- 2026 n'a que janvier à août (le produit final d'août a été
  déposé le 11 septembre 2026)

Index NetCDF par année : 1981 à 2026, **zéro année manquante**.
Le fichier 2026 pèse moins (109,2 Mo contre ~163 Mo) : année
encore incomplète.

Prelim mensuel (non compté) : va aussi jusqu'à août 2026. Pas de
septembre 2026 sur cet index.

Le gros fichier unique `chirps-v2.0.monthly.nc` fait 7,2 Gio
(déposé le 14 août 2026). On ne l'a pas téléchargé.

## Les deux découpages (publiés, pas redessinés)

Même méthode que SPEI (PR 243).

Méditerranée : boîte IPCC AR6 WGI **MED** (Iturbide 2020), sommets
(-10, 30), (-10, 45), (40, 45), (40, 30). Libellé publié : terre
et mer.
https://raw.githubusercontent.com/IPCC-WG1/Atlas/main/reference-regions/IPCC-WGI-reference-regions-v4_coordinates.csv

Inde : Maharashtra et Karnataka seulement (pas toute l'Inde).
Polygones Natural Earth 50 m.

Ces anneaux ne sont pas un compte CHIRPS. Le compte des cases
est dans `data/truth/chirps/chirps_report.md` après le run
`python scripts/eval_chirps.py`.

## On n'a pas noté de prévision

Pas de SEAS5. Pas de C3S. Pas de NMME découpé ici. Pas de BSS.
La gate (BSS > 0,05 sur au moins 10 saisons) n'est pas jouable
sans une prévision datée. On ne l'invente pas.

Ensuite, si on veut cette gate : une prévision saisonnière de
pluie datée, comparée aux mois CHIRPS déjà comptés. Pas avant.

## Verdicts (noms du catalogue, non renommés)

Les verdicts mesurés sont dans `data/truth/chirps/chirps_report.md`.
Tant que les cases n'ont pas été lues, **CHIRPS pluie** reste
bloquée. Les cibles Sécheresse Méditerranée et Sécheresse Inde
restent « pas encore testée » : compter la pluie n'est pas
scorer une prévision.

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
