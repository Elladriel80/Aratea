# Régime ENSO

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Question : a-t-on une histoire officielle El Niño / La Niña / neutre,
assez longue pour la mutuelle (3 à 12 mois) ?

Cette note dit seulement ce qui a été compté. Le site public n'a pas
été changé. Le modèle Kalshi en ligne n'a pas été changé. Aucun pari
avec de l'argent réel. Aucun chiffre n'a été inventé. On n'a pas noté
Kalshi J+1. On n'a pas ouvert SEAS5 ni C3S.

## D'où viennent les chiffres

Depuis le 1er février 2026, le centre américain du climat (NOAA / CPC)
surveille ENSO avec le RONI, pas avec l'ancien ONI. On a compté le
RONI. On n'a pas mélangé les deux.

Fichier officiel :
https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt

Page des règles :
https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/

Annonce du 1er février 2026 :
https://www.weather.gov/media/notification/pdf_2026/pns26-05_Relative_ONI.pdf

Seuils écrits par CPC (on ne les change pas) :

- El Niño : RONI plus grand que 0,5 °C
- La Niña : RONI plus petit que -0,5 °C
- Neutre : entre les deux, y compris pile 0,5 ou pile -0,5
- Un épisode officiel (celui qu'ils colorient) : au moins 5 saisons
  de 3 mois qui se suivent et se chevauchent

CPC compte des saisons (DJF, JFM, …), pas une année civile. DJF 1950
contient aussi décembre 1949. On le dit. On n'invente pas une année.

La page web arrondit à un chiffre après la virgule. On compte le
fichier, à deux chiffres. On ne mélange pas.

## Ce qui est dans le fichier

Du DJF 1950 au JJA 2026.

77 années civiles (1950 à 2026). 919 saisons. 919 saisons attendues.
0 trou. 0 doublon.

2026 n'est pas finie : 7 saisons sont là, 5 manquent encore
(JAS à NDJ). Ce n'est pas un trou au milieu. CPC dit aussi que les
toutes dernières valeurs peuvent encore bouger un peu.

## Les trois phases (chaque saison)

| Phase | Saisons |
|---|---|
| El Niño | 239 |
| La Niña | 229 |
| Neutre | 451 |
| Total | 919 |

## Les épisodes officiels (5 saisons d'affilée)

22 El Niño. 21 La Niña.

218 saisons dans un El Niño colorié. 216 dans une La Niña coloriée.
485 saisons hors épisode (neutre, ou trop court pour être colorié).

Le plus long El Niño ici : 17 saisons (JAS 1986 à NDJ 1987), pic +1,46.
Le plus fort El Niño : +2,40 (AMJ 1982 à AMJ 1983).
Le plus long La Niña : 35 saisons (AMJ 2020 à FMA 2023), pic -1,46.
Le plus fort La Niña : -1,95 (MAM 1988 à AMJ 1989).

Aujourd'hui (MJJ et JJA 2026) : 2 saisons déjà au-dessus de 0,5 °C.
Pas encore 5. Donc pas encore un El Niño colorié. On ne l'invente pas.

## Les années (attention, ce n'est pas une case unique)

CPC ne classe pas une année. Une année peut avoir les deux.

| Lecture | Années |
|---|---|
| Au moins une saison El Niño | 47 |
| Au moins une saison La Niña | 41 |
| Les deux dans la même année | 17 |
| Seulement neutre | 6 |
| Année incomplète | 1 (2026) |

Les 6 années seulement neutre : 1960, 1961, 1962, 1967, 1981, 1990.

Les tables saison par saison et année par année sont dans
`data/truth/enso/enso_report.md`.

## Est-ce que ça aide Kalshi demain ?

Non. On ne l'a pas noté, et on ne le notera pas ici. Une saison de
3 mois ne dit pas le degré de demain. Le catalogue le disait déjà :
utile mutuelle / Phase 2, pas pour Kalshi J+1.

## Décision

**Verdict : testée, ça aide.**

Ça aide comme contexte pour la mutuelle (sécheresse, ouragans, 3 à
12 mois) : l'histoire officielle est là, sans trou, avec les vrais
seuils CPC. Ça n'aide pas les paris du jour. On n'a pas changé le
champion. On n'a pas ouvert une autre mesure après celle-ci.

Pour relancer : `python scripts/eval_enso.py --skip-fetch`

Pas de changement du texte du site. Pas de trading réel.
