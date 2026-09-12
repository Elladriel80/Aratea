# Regarder le thermomètre déjà mesuré aujourd'hui

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

L'idée : pour un contrat « max (ou min) aujourd'hui », regarder
la température déjà mesurée à la station, pas seulement le modèle.
Les humains qui gagnent sur le jour même font ça.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle en ligne n'a pas été changé. Aucun pari avec
de l'argent réel.

## Ce qu'on a trouvé avant de mesurer

Le robot ne parie pas sur aujourd'hui. Il vise seulement demain.
On n'a pas changé ça.

Le site météo américain ne garde que les 7 derniers jours de lectures.
On ne peut pas s'en servir pour l'été 2026. On l'écrit ici.

L'archive de l'Iowa a les lectures heure par heure des 18 villes.
C'est ça qu'on a utilisé. Aucune lecture manquante n'a été inventée.

Pour le reste de la journée (ce qui peut encore monter ou descendre),
on a pris une prévision heure par heure de la veille, quand elle
existait. Le run du matin même existe ailleurs, mais on n'avait pas
l'outil pour le lire. Si cette prévision manquait, on a utilisé une
largeur simple selon les heures encore ouvertes, ou les jours passés
à la même heure. Ce n'est pas une lecture. On le dit.

## Ce qui a été fait

1. Télécharger les lectures heure par heure des 18 villes, du 1er mai
   au 11 septembre 2026.
2. À l'heure de chaque capture déjà enregistrée le jour même, prendre
   le max (ou le min) déjà vu, plus le risque du reste de la journée.
3. Comparer au chiffre officiel de la station (même fichier que
   l'étape A1).
4. Comparer aussi au mélange avec la correction ville, et au prix
   du marché quand un prix du jour même existait.

Les comptes détaillés sont dans `data/truth/nowcast/nowcast_skill.md`.
Ils sont remplis par le script, pas à la main.

## Décision (à relire après le script)

On ne change pas le modèle en ligne tant que le script n'a pas assez
de jours. La règle du projet demande 30 jours pour parler du marché.
On ne promeut pas sans ça.

## Comment relancer le script

Dans le dossier `predictor`, avec internet :

```
python scripts/eval_nowcast_skill.py
```

Sans retélécharger (les lectures sont déjà là) :

```
python scripts/eval_nowcast_skill.py --skip-fetch --skip-nws-probe
```

Le script écrit surtout :

- `data/asos/extracted.json` : les lectures, heure par heure
- `data/hrrr/extracted.json` : la prévision heure par heure de la veille
- `data/truth/nowcast/nowcast_skill.md` : le tableau détaillé
- `data/truth/nowcast/nowcast_skill.json` : les mêmes comptes en machine

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel, avec la correction ville.
Le robot continue de viser demain, pas aujourd'hui.
Pas de changement du texte du site. Pas de trading réel.
