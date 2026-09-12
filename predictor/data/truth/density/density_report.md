# Ville, végétation, eau autour de la station

Généré : 2026-09-12T15:24:31Z. Habitants : WorldPop 2020 (fichier de comptage 1 km). Vert et eau : ESA WorldCover 2021 (10 m). Point = coordonnées officielles A1. Aucun chiffre inventé.

## D'où viennent les nombres

- Ville : WorldPop 2020, fichier usa_ppp_2020_1km_Aggregated.tif (habitants par pixel, 30 secondes d'arc, WGS84). Densité = somme des habitants dans le disque / surface du disque (π r²). Pixel sans donnée = 0 habitant. https://dx.doi.org/10.5258/SOTON/WP00674
- Végétation : ESA WorldCover 10 m 2021 v200, classes 10/20/30/40/90/95/100 (arbre, buisson, herbe, culture, marais, mangrove, mousse). Densité = pixels verts / pixels lus. https://doi.org/10.5281/zenodo.7254221
- Eau : ESA WorldCover 10 m 2021 v200, classe 80 (eau permanente), y compris mer et lacs. Densité = pixels eau / pixels lus. https://doi.org/10.5281/zenodo.7254221

Les anciens comptages OSM (bâtiments, arbres, rivières) ne sont pas utilisés.

À 1 km, beaucoup d'aéroports ont 0 habitant : la carte WorldPop fait 1 km de côté, et la piste est vide. Le 5 km commence à voir le quartier. Le 20 km voit la mer pour Boston, San Francisco, Los Angeles, Seattle.

## Les 18 stations, rayon 5 km

| Ville | Habitants / km² | Part verte | Part d'eau | Max typique | Min typique | Jours ≥ 100 °F | Jours de gel |
|---|---|---|---|---|---|---|---|
| Atlanta | 677 | 51 % | 0 % | 73 °F | 52 °F | 0 | 42 |
| Austin | 303 | 71 % | 1 % | 81 °F | 57 °F | 16 | 26 |
| Boston | 2544 | 12 % | 47 % | 59 °F | 43 °F | 0 | 96 |
| Washington | 2525 | 42 % | 17 % | 69 °F | 49 °F | 0 | 68 |
| Denver | 0 | 73 % | 0 % | 63 °F | 36 °F | 1 | 158 |
| Dallas | 196 | 50 % | 0 % | 78 °F | 56 °F | 15 | 34 |
| Houston | 1662 | 58 % | 1 % | 81 °F | 61 °F | 0 | 8 |
| Las Vegas | 1713 | 6 % | 1 % | 80 °F | 55 °F | 78 | 22 |
| Los Angeles | 2011 | 12 % | 16 % | 70 °F | 55 °F | 0 | 0 |
| Chicago | 2783 | 15 % | 1 % | 62 °F | 44 °F | 0 | 102 |
| Miami | 2640 | 21 % | 2 % | 84 °F | 71 °F | 0 | 0 |
| Minneapolis | 853 | 60 % | 6 % | 59 °F | 39 °F | 0 | 154 |
| New York | 16653 | 15 % | 22 % | 63 °F | 47 °F | 0 | 79 |
| Philadelphie | 697 | 42 % | 22 % | 66 °F | 46 °F | 0 | 89 |
| Phoenix | 1430 | 10 % | 0 % | 87 °F | 59 °F | 106 | 2 |
| San Antonio | 1416 | 56 % | 0 % | 82 °F | 60 °F | 10 | 18 |
| Seattle | 1263 | 51 % | 12 % | 58 °F | 43 °F | 0 | 28 |
| San Francisco | 886 | 14 % | 43 % | 66 °F | 50 °F | 0 | 0 |

## Tous les rayons (habitants / km², part verte, part d'eau)

| Ville | 1 km hab | 1 km vert | 1 km eau | 2 km hab | 5 km hab | 10 km hab | 20 km hab | 20 km vert | 20 km eau |
|---|---|---|---|---|---|---|---|---|---|
| Atlanta | 0 | 11 % | 0 % | 0 | 677 | 899 | 831 | 76 % | 1 % |
| Austin | 0 | 47 % | 0 % | 91 | 303 | 625 | 631 | 80 % | 1 % |
| Boston | 0 | 28 % | 8 % | 573 | 2544 | 2797 | 1591 | 42 % | 35 % |
| Washington | 0 | 23 % | 26 % | 743 | 2525 | 3194 | 1957 | 69 % | 5 % |
| Denver | 0 | 1 % | 0 % | 0 | 0 | 38 | 207 | 83 % | 1 % |
| Dallas | 0 | 7 % | 0 % | 0 | 196 | 948 | 1151 | 50 % | 4 % |
| Houston | 49 | 36 % | 0 % | 342 | 1662 | 1661 | 1324 | 60 % | 2 % |
| Las Vegas | 33 | 1 % | 0 % | 754 | 1713 | 2657 | 1860 | 10 % | 0 % |
| Los Angeles | 0 | 0 % | 0 % | 854 | 2011 | 2585 | 2681 | 13 % | 35 % |
| Chicago | 2019 | 17 % | 2 % | 2711 | 2783 | 3076 | 2504 | 36 % | 10 % |
| Miami | 0 | 9 % | 1 % | 703 | 2640 | 2983 | 1750 | 33 % | 26 % |
| Minneapolis | 0 | 17 % | 0 % | 6 | 853 | 1422 | 1221 | 68 % | 4 % |
| New York | 21593 | 44 % | 9 % | 32777 | 16653 | 11868 | 7377 | 29 % | 17 % |
| Philadelphie | 0 | 27 % | 0 % | 18 | 697 | 1695 | 1563 | 67 % | 6 % |
| Phoenix | 1 | 0 % | 0 % | 32 | 1430 | 1780 | 1524 | 29 % | 1 % |
| San Antonio | 0 | 47 % | 0 % | 72 | 1416 | 1609 | 1262 | 65 % | 0 % |
| Seattle | 19 | 44 % | 0 % | 789 | 1263 | 1020 | 885 | 51 % | 29 % |
| San Francisco | 0 | 17 % | 9 % | 13 | 886 | 831 | 1086 | 29 % | 51 % |

## Lien avec le climat officiel (fichier siècle)

On range les 18 villes. On regarde si l'ordre des densités suit l'ordre des températures. n = 18 partout où le siècle a un chiffre. Un lien n'est retenu que si |r| ≥ 0,47 et p < 0,05 (ordre, n=18).

| Rayon | Densité | Climat | r | p approx |
|---|---|---|---|---|
| 20 km | eau | écart jour-nuit | -0,88 | 0,000 |
| 10 km | eau | écart jour-nuit | -0,75 | 0,000 |
| 20 km | eau | jours ≥ 100 °F | -0,72 | 0,001 |
| 5 km | eau | écart jour-nuit | -0,70 | 0,001 |
| 5 km | eau | jours ≥ 100 °F | -0,66 | 0,003 |
| 10 km | eau | jours ≥ 100 °F | -0,59 | 0,010 |
| 5 km | habitants | écart jour-nuit | -0,59 | 0,010 |
| 2 km | habitants | écart jour-nuit | -0,56 | 0,016 |
| 2 km | eau | jours ≥ 100 °F | -0,55 | 0,017 |
| 20 km | eau | max typique | -0,53 | 0,024 |
| 20 km | végétation | jours de gel | 0,50 | 0,036 |
| 5 km | eau | max typique | -0,50 | 0,036 |
| 2 km | eau | max typique | -0,49 | 0,039 |
| 2 km | eau | min typique | -0,48 | 0,045 |

### Le plus fort r, même s'il est trop faible pour compter

| Rayon | Habitants × min | Végétation × max | Eau × écart jour-nuit |
|---|---|---|---|
| 1 km | 0,10 | -0,18 | -0,37 |
| 2 km | 0,03 | -0,16 | -0,45 |
| 5 km | 0,10 | -0,07 | -0,70 |
| 10 km | 0,04 | 0,02 | -0,75 |
| 20 km | 0,08 | -0,12 | -0,88 |

## Skill Kalshi (holdout A1, 3 août au 7 septembre 2026)

Correctif unique pour toutes les villes : on apprend sur TRAIN l'écart prévision − station à partir des trois densités, puis on l'applique au HOLDOUT. Ce n'est pas un biais par ville. Le champion reste le mélange corrigé ville par ville (0,1154) sauf victoire claire.

| Méthode | Score d'erreur |
|---|---|
| Mélange brut | 0,1250 |
| Mélange corrigé ville par ville | 0,1154 |
| Densités à 1 km | 0,1230 |
| Densités à 2 km | 0,1230 |
| Densités à 5 km | 0,1232 |
| Densités à 10 km | 0,1231 |
| Densités à 20 km | 0,1229 |

- dens1_vs_station : 2/36 jours (p = 1,0000).
- dens1_vs_raw : 25/36 jours (p = 0,0144).
- dens2_vs_station : 1/36 jours (p = 1,0000).
- dens2_vs_raw : 25/36 jours (p = 0,0144).
- dens5_vs_station : 1/36 jours (p = 1,0000).
- dens5_vs_raw : 25/36 jours (p = 0,0144).
- dens10_vs_station : 2/36 jours (p = 1,0000).
- dens10_vs_raw : 25/36 jours (p = 0,0144).
- dens20_vs_station : 2/36 jours (p = 1,0000).
- dens20_vs_raw : 26/36 jours (p = 0,0057).

## Décision

On ne change pas le modèle en ligne. Les densités ne battent pas le mélange corrigé ville par ville (0,1229 contre 0,1154 au meilleur rayon, 36 jours). Sur les contrats avec un prix (la veille, 62 jours) : densités 0,1437 contre marché 0,1253. L'eau à 20 km est le lien le plus net avec l'écart entre le jour et la nuit. Utile pour décrire un lieu (mutuelle), pas pour remplacer la correction ville par ville.

## Contre le prix du marché (la veille, si on a le prix)

| Méthode | Score d'erreur |
|---|---|
| Prix du marché | 0,1253 |
| Mélange brut | 0,1446 |
| Densités à 1 km | 0,1442 |
| Densités à 2 km | 0,1439 |
| Densités à 5 km | 0,1437 |
| Densités à 10 km | 0,1438 |
| Densités à 20 km | 0,1439 |
Jours : 62. Contrats : 4932.

Pas de changement du site public. Pas de trading réel. Pas de bascule du champion sauf victoire claire ci-dessus.

Pour relancer : `python scripts/eval_land_density.py` (ou `--skip-fetch` si WorldPop est déjà en cache).
