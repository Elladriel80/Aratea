# Sécheresse US : le US Drought Monitor, compté

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Première mesure Phase 2. Cible catalogue : **Sécheresse US**.
Vérité catalogue : **US Drought Monitor**.
Prévision essayée : **Open-Meteo Seasonal**.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle Kalshi en ligne n'a pas été changé. Aucun pari
avec de l'argent réel. Aucun chiffre n'a été inventé. On n'a pas
commencé Méditerranée, Inde, ni ouragan.

## D'où viennent les chiffres

Carte officielle américaine, une par semaine, depuis le 4 janvier 2000
(premier mardi publié). Service REST du US Drought Monitor
(usdmdataservices.unl.edu).

Classes telles que publiées, rien d'ajouté :

- None (pas sec)
- D0 (anormalement sec)
- D1 (sécheresse modérée)
- D2 (sévère)
- D3 (extrême)
- D4 (exceptionnelle)

Midwest et Southwest : ce sont les noms déjà publiés par le service
(hubs USDA, aoi 3 et 10). On n'a pas redessiné la carte.

États listés sur les pages USDA des hubs (continent) :

- Midwest : Illinois, Indiana, Iowa, Michigan, Minnesota, Missouri,
  Ohio, Wisconsin
- Southwest : Arizona, Californie, Nevada, Nouveau-Mexique, Utah

Le Kentucky apparaît dans le texte de la page USDM « Midwest ». Il
n'est pas sur la page USDA du hub Midwest. On ne l'a pas ajouté.
Hawaï est dans le texte USDA Southwest. On n'a pas retranché le hub
publié.

« Midwest + Southwest » = somme des aires des deux hubs, même mardi.

Le seuil 30 % D2+ était déjà écrit dans le scaffolding Phase B. Ici
c'est un compte, pas un produit, pas un prix.

## Combien de semaines et de saisons

Même archive partout : **1393 semaines**, du 4 janvier 2000 au
8 septembre 2026. **Zéro trou**. Mardi après mardi.

27 années civiles avec au moins une carte (2000 à 2026). 26 années
avec 52 semaines ou plus (2026 n'est pas finie).

108 saisons du calendrier météo (DJF, MAM, JJA, SON) avec au moins
une carte. **106 saisons assez pleines** (12 semaines ou plus) :

- DJF : 26
- MAM : 27
- JJA : 27
- SON : 26

La première saison (DJF 2000) et la dernière (SON 2026) sont trop
courtes. On le dit tel quel.

## Ce que ça donne, zone par zone

Chiffres catégoriels (chaque classe toute seule, pas empilée).

| Zone | Semaines | D2+ en moyenne | Semaines D2+ > 0 | Semaines D2+ ≥ 30 % |
|---|---:|---:|---:|---:|
| CONUS | 1393 | 18,00 % | 1391 | 266 |
| Midwest | 1393 | 5,21 % | 935 | 31 |
| Southwest | 1393 | 33,10 % | 1350 | 659 |
| Midwest + Southwest | 1393 | 20,97 % | 1390 | 421 |

Le Midwest est souvent presque sans D2. Le Southwest a souvent du D2
ou pire. Ce n'est pas la même cible.

Sur les 106 saisons assez pleines, part des saisons où la moyenne
D2+ atteint 30 % :

| Zone | DJF | MAM | JJA | SON |
|---|---:|---:|---:|---:|
| Midwest | 1 / 26 | 0 / 27 | 1 / 27 | 1 / 26 |
| Southwest | 10 / 26 | 14 / 27 | 14 / 27 | 13 / 26 |
| les deux ensemble | 6 / 26 | 7 / 27 | 10 / 27 | 10 / 26 |

États du Midwest, semaines D2+ ≥ 30 % sur 1393 : Iowa 167,
Minnesota 120, Missouri 82, Illinois 79, Wisconsin 50, Indiana 48,
Michigan 17, Ohio 16.

États du Southwest continent, mêmes 1393 semaines : Arizona 653,
Nouveau-Mexique 651, Nevada 621, Utah 541, Californie 476.

## La prévision : Open-Meteo Seasonal

C'est le nom du catalogue. Pas besoin de compte Copernicus.

Ce qui bloque un vrai test : l'API refuse toute date avant le
1er septembre 2025. Message mesuré : fenêtre autorisée du
1er septembre 2025 au 16 avril 2027. Pas d'archive depuis 2000.
Les membres ne sont gardés qu'un mois. On a la moyenne d'ensemble
seulement.

On a quand même noté ce qui existe. Règle fixée avant de compter :
mois complets seulement (tous les mardis déjà publiés). Prévision
sèche si l'anomalie de pluie est négative (p = 1), sinon p = 0.
Événement : moyenne D2+ du mois ou de la saison ≥ 30 %.

12 mois complets, du 1er septembre 2025 au 1er août 2026.
4 saisons : SON 2025, DJF 2026, MAM 2026, JJA 2026.
La gate écrite demande **10 saisons** et BSS > 0,05. 4 < 10.
On ne conclut pas.

Midwest, 12 mois : D2+ ≥ 30 % **jamais**. La climato de ces 12 mois
a donc un score d'erreur 0. On ne calcule pas de BSS (ce serait
inventer). La prévision a trop souvent dit « sec » (Brier 0,75).

Southwest, 12 mois : Brier prévision 0,4167 contre climato 0,2645.
BSS −0,5755. La prévision perd.

Southwest, 4 saisons : Brier prévision 0,25 contre climato 0,3333.
BSS 0,25. Quatre saisons, pas dix. Trop peu pour la gate.

## NMME

Deuxième choix du catalogue. L'IRI répond. Ce qu'on reçoit est une
grille mondiale, ou une moyenne sans dates utilisables. On n'a pas
apparié ça au US Drought Monitor. Pas de score inventé.
**NMME : bloquée.**

SEAS5 / C3S : pas essayés (compte Copernicus, comme demandé).

## Verdicts (noms du catalogue, non renommés)

| Nom | Verdict |
|---|---|
| Sécheresse US | bloquée |
| US Drought Monitor | testée, ça aide |
| Open-Meteo Seasonal | bloquée |
| NMME | bloquée |
| SEAS5 | pas encore testée |
| C3S multi-modèle | pas encore testée |
| SPEI | pas encore testée |
| CHIRPS pluie | pas encore testée |
| Sécheresse Méditerranée | cible Tier 1 (pas encore testée) |
| Sécheresse Inde | cible Tier 1 (pas encore testée) |
| Ouragan formation | cible Tier 1 (pas encore testée) |
| Ouragan intensité | cible Tier 1 (pas encore testée) |
| Ouragan landfall | cible Tier 1 (pas encore testée) |

US Drought Monitor aide : on a enfin le vrai compte, semaine par
semaine, depuis 2000, sans trou. Sécheresse US reste bloquée : la
vérité est là, la prévision n'a pas 10 saisons.

## Décision

On ne change pas le modèle Kalshi en ligne.

Pourquoi : ce n'est pas un test Kalshi. C'est la première vérité
Phase 2. La gate (BSS > 0,05 sur au moins 10 saisons) n'est pas
jouable avec Open-Meteo Seasonal aujourd'hui.

Ensuite, si on veut la gate : il faut une archive saisonnière
datée sur Midwest et Southwest (NMME bien découpé, ou un compte
qui ouvre SEAS5 / C3S). Pas Méditerranée. Pas Inde. Pas ouragan.
D'abord cette vérité, déjà comptée.

## Comment relancer

Dans le dossier `predictor`, avec internet la première fois :

```
python scripts/eval_us_drought.py
```

Les fichiers bruts restent locaux. Les comptes sont dans
`data/truth/usdm/`.

Pas de changement du texte du site. Pas de trading réel.
