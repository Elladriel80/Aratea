# Le vrai chiffre de la station

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Kalshi paie selon le chiffre officiel de la station (max et min du jour).
Jusqu'ici, notre modèle apprenait sur un autre chiffre : celui d'une grille météo
(Open-Meteo). Ce ne sont pas les mêmes nombres.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas été changé.
Aucun pari avec de l'argent réel.

## Ce qui a été fait

1. Télécharger le max et le min officiels des 18 villes déjà suivies, jour par jour.
2. Coller ces chiffres sur le carnet de paris papier et sur les prévisions déjà enregistrées, quand c'était possible.
3. Comparer, ville par ville, la grille météo et le chiffre officiel.

Les 18 villes ont bien répondu. Aucun chiffre n'a été inventé.

## La comparaison (1er janvier 2020 au 8 septembre 2026)

Un contrat Kalshi fait 2 degrés. Si la grille se trompe de 2 degrés ou plus,
elle pointe le mauvais contrat.

Lecture du tableau : « écart » = grille moins station. Un écart négatif veut
dire que la grille est plus froide que la station. « Juste » = le degré arrondi
est le même. « Au moins 2 deg » = écart d'au moins 2 degrés.

### Maximum du jour

| Ville | Jours | Écart moyen | Juste | Au moins 2 deg |
|---|---|---|---|---|
| Atlanta | 2440 | -2,35 ° | 8 % | 67 % |
| Austin | 2443 | -1,63 ° | 10 % | 57 % |
| Boston | 2440 | -1,04 ° | 14 % | 45 % |
| Chicago | 2442 | -1,76 ° | 11 % | 53 % |
| Dallas | 2439 | -1,18 ° | 15 % | 50 % |
| Denver | 2443 | -1,84 ° | 9 % | 61 % |
| Houston | 2439 | -3,01 ° | 7 % | 72 % |
| Las Vegas | 2441 | -0,50 ° | 29 % | 20 % |
| Los Angeles | 2441 | -1,26 ° | 13 % | 48 % |
| Miami | 2433 | -2,26 ° | 9 % | 59 % |
| Minneapolis | 2443 | -1,25 ° | 15 % | 47 % |
| New York | 2441 | -0,89 ° | 17 % | 43 % |
| Philadelphie | 2443 | -1,09 ° | 16 % | 42 % |
| Phoenix | 2440 | -2,22 ° | 10 % | 54 % |
| San Antonio | 2441 | -2,01 ° | 11 % | 60 % |
| San Francisco | 2429 | -1,23 ° | 12 % | 58 % |
| Seattle | 2439 | -1,64 ° | 11 % | 54 % |
| Washington | 2435 | -2,00 ° | 10 % | 59 % |

### Minimum du jour (les écarts les plus nets)

| Ville | Jours | Écart moyen | Juste | Au moins 2 deg |
|---|---|---|---|---|
| Austin | 2443 | +4,05 ° | 8 % | 70 % |
| Denver | 2443 | +2,65 ° | 10 % | 64 % |
| Phoenix | 2440 | -2,85 ° | 7 % | 70 % |
| New York | 2441 | -2,55 ° | 11 % | 59 % |
| Chicago | 2442 | -2,53 ° | 10 % | 61 % |
| Washington | 2435 | -2,45 ° | 10 % | 62 % |
| Dallas | 2439 | +0,56 ° | 21 % | 32 % |

Les 12 autres villes sont dans le fichier détaillé `data/truth/era5_vs_cli.md`.

En clair : la grille tombe sur le bon degré 7 à 29 jours sur 100 pour le max.
Elle se trompe d'au moins 2 degrés 20 à 72 jours sur 100, selon la ville.
Houston (max) et Austin (min) sont les plus loin. Las Vegas (max) est la plus proche.

Los Angeles, Miami et Washington manquaient dans l'ancien tableau. Ils sont
mesurés maintenant.

## Collage sur les paris et les prévisions

- Carnet papier + ancien backtest : **1048 lignes sur 1048** ont le chiffre officiel.
- Prévisions déjà enregistrées : **29897 lignes sur 34902** ont le chiffre officiel.
- 4998 prévisions parlent encore d'anciens aéroports (Chicago O'Hare, Houston Intercontinental, Dallas Love Field). Ce ne sont plus les stations de Kalshi. On ne les a pas mélangées avec les stations actuelles.
- 7 prévisions Miami n'ont pas de max ou min officiel ce jour-là. Rien d'inventé.

Deux noms de marchés (Washington max et Seattle max) n'étaient pas reliés à
leur station. C'est corrigé. C'est pour ça que le carnet papier est complet.

## Comment lancer le script

Dans le dossier `predictor`, avec internet :

```
python scripts/build_station_truth.py
```

Pour recoller sans retélécharger (les chiffres station sont déjà là) :

```
python scripts/build_station_truth.py --skip-fetch
```

Le script écrit surtout :

- `data/truth/cli_daily.json` : max et min officiels, jour par jour
- `data/truth/era5_vs_cli.md` : le tableau grille contre station
- `data/truth/cli_joined_ledger.json` : carnet papier + chiffre officiel
- `data/truth/cli_joined_forecasts.json` : prévisions déjà là + chiffre officiel
- `data/truth/join_summary.json` : les comptes de collage

## Ce que cette étape ne fait pas

Le modèle en ligne utilise encore la grille pour sa climatologie. On n'a pas
basculé : le fichier station ici commence en 2020 (environ 7 ans), alors que
la climatologie actuelle regarde 30 ans. Remplacer sans une plus longue
histoire de station serait une autre décision, pas une mesure.

Pas de changement du texte du site. Pas de trading réel.
