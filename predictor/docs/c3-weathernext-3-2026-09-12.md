# WeatherNext 3

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)
**Nom stable :** WeatherNext 3
**Verdict :** pas encore mesurable (bloquée)

Kalshi paie selon le chiffre officiel de la station.
L'idée : Google a sorti en août 2026 un modèle d'intelligence artificielle
qui vise justement la température à la station (WeatherNext 3).
On a voulu le noter comme les autres pistes, sans changer le modèle en ligne
et sans pari avec de l'argent réel.

Cette note dit seulement ce qui a été possible. Aucun chiffre manquant
n'a été inventé. Les 15 noms du catalogue n'ont pas été touchés.

## WeatherNext 3 : bloquée

On n'a pas pu lire une seule prévision WeatherNext 3.

Pourquoi, exactement :

1. Open-Meteo (le chemin gratuit déjà utilisé par le projet) refuse
   tous les noms essayés. Réponse 400 : ce modèle n'existe pas chez eux.
2. Les fichiers Google (GCS `weathernext3_spatial` et `weathernext`)
   répondent 401 ou 403 sans compte autorisé.
3. Il n'y a pas de compte Google Cloud ici. Donc pas de BigQuery
   (`weathernext_3_0_0_0p05deg`) et pas d'Earth Engine.

Sans ces données, on ne peut pas donner un score WeatherNext 3.
On n'en invente pas.

## Ce qu'il faut pour débloquer (un seul prochain fetch)

1. Remplir le formulaire Google avec l'e-mail du compte Google Cloud :
   https://developers.google.com/weathernext/guides/access-forecast
2. Attendre que Google ajoute le compte (ils indiquent 5 à 7 jours ouvrés).
3. Lire la table station `weathernext_3_0_0_0p05deg` (ou les fichiers GCS)
   pour les 18 villes, le jour même (J0) et la veille (J-1) séparés,
   sur au moins 30 jours différents.
4. Relancer le script. Encore une fois : pas de score inventé avant ça.

## Version la plus proche, clairement étiquetée : WeatherNext 2

Open-Meteo sert déjà WeatherNext 2 (64 versions, grille plus large,
pas le modèle station de 2026). Ce n'est pas WeatherNext 3.
On l'a noté quand même, pour ne pas rentrer les mains vides.

Ce qui a marché :

- Les 18 villes ont répondu.
- Les versions étaient remplies du 9 au 12 septembre 2026 seulement.
- Août 2026 est vide chez Open-Meteo. Pas d'archive longue. Rien n'a
  été remplacé.
- On a noté le jour même (J0) contre le chiffre officiel.

Ce qui a échoué, et qu'on écrit ici :

- La veille (J-1) : Open-Meteo a les cases, mais toutes vides.
  Donc **aucun score J-1**. Pas de chiffre inventé.
- Six villes de l'Ouest n'avaient pas encore assez d'heures le 12
  septembre (Denver, Las Vegas, Los Angeles, Phoenix, San Francisco,
  Seattle). Ces villes sont notées sur 3 jours, pas 4.

## Le résultat J0 (9 au 12 septembre 2026)

Plus le score d'erreur est petit, mieux c'est.

Contre le chiffre officiel de la station, 4 jours, 18 villes :

| Méthode | Score d'erreur |
|---|---|
| WeatherNext 2, jour même | 0,1400 |

Sur le maximum du jour : 0,1417.
Sur le minimum du jour : 0,1383.

## Contre le prix du marché, jour même seulement

3 jours (9, 10 et 11 septembre). On a à la fois le prix, notre mélange,
et WeatherNext 2. La vérité est le chiffre officiel. La veille n'est
pas dans ce tableau : on n'avait pas WeatherNext 2 pour la veille.

| Méthode | Score d'erreur |
|---|---|
| WeatherNext 2 | 0,2113 |
| Notre mélange actuel (champion) | 0,1770 |
| Prix du marché | 0,0742 |

WeatherNext 2 perd contre le marché : **0 jour sur 3**.
WeatherNext 2 bat notre mélange : **1 jour sur 3**.

3 jours, ce n'est pas 30. On ne conclut pas que « ça aide » ou
« ça n'aide pas ». On dit seulement ces trois jours.

## Décision

On ne change pas le modèle en ligne.

Pourquoi : WeatherNext 3 n'a pas pu être lue. La règle du projet
demande de battre le marché de façon claire, sur au moins 30 jours.
WeatherNext 2, sur 3 jours de prix, perd 0 jour sur 3 contre le marché.
Ce n'est pas assez, et ce n'est pas le modèle demandé.

## Comment relancer le script

Dans le dossier `predictor`, avec internet :

```
python scripts/eval_weathernext_skill.py
```

Sans retélécharger (les extrêmes jour par jour sont déjà là) :

```
python scripts/eval_weathernext_skill.py --skip-fetch
```

Le script écrit surtout :

- `data/truth/weathernext/weathernext_skill.md` : le tableau détaillé
- `data/truth/weathernext/weathernext_skill.json` : les mêmes comptes en machine
- `data/truth/weathernext/daily_extremes.json` : les versions, jour par jour

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel.
Pas de changement du texte du site. Pas de trading réel.
Pas de nouveau nom dans le catalogue des 15 variables.
On n'a pas relancé les tests déjà tranchés le 12 septembre
(NBM, versions américaines seules, thermomètre du jour, siècle,
densités, NBM plus ville, et les demandes 234 à 237).
