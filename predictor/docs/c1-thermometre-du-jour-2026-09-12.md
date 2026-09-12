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

Le site météo américain ne garde que les tout derniers jours.
Le 12 septembre, pour Atlanta, il n'avait des lectures que depuis
le 11 septembre. Pas l'été 2026. On ne s'en est pas servi pour
noter. On l'écrit ici.

L'archive de l'Iowa a les lectures heure par heure des 18 villes.
Du 1er mai au 11 septembre 2026 : 56 302 lectures. Les 18 villes
ont répondu. Aucune lecture manquante n'a été inventée.

Sur 5 197 contrats déjà capturés le jour même, 184 n'avaient pas
assez de lectures à l'heure de la capture, 4 n'avaient pas le
chiffre officiel, 88 n'avaient pas encore la correction ville.
On ne les a pas inventés. On a noté les 4 921 autres, sur 59 jours.

## Comment on a noté

À l'heure de chaque capture déjà enregistrée le jour même :

1. Prendre le max (ou le min) déjà mesuré ce jour-là.
2. Ajouter un risque simple pour les heures encore ouvertes :
   ce qui restait à monter ou descendre les jours passés, à la
   même heure, avant le 3 août. Si ce n'était pas assez, une
   largeur qui rétrécit quand la journée se termine. Ce n'est
   pas une lecture.
3. Comparer au chiffre officiel de la station (même fichier que
   l'étape A1), au mélange avec la correction ville, et au prix
   du marché.

On a aussi essayé une prévision heure par heure de la veille
pour le reste de la journée. Elle existait pour les 18 villes.
Ça a empiré le score. On le dit plus bas. On n'a pas le run
du matin même dans cet environnement.

## Le résultat, 59 jours avec un prix le jour même

Plus le score d'erreur est petit, mieux c'est.
4 921 contrats. 18 villes. 1er mai au 11 septembre 2026.

| Méthode | Score d'erreur |
|---|---|
| Thermomètre + risque simple | 0,1055 |
| Thermomètre + prévision de la veille | 0,1263 |
| Notre mélange avec la correction ville | 0,1317 |
| Notre mélange actuel | 0,1423 |
| Prix du marché | 0,0585 |

Le thermomètre avec le risque simple bat la correction ville :
**56 jours sur 59**.

Il perd contre le prix : **0 jour sur 59**.

La prévision de la veille pour le reste de la journée bat la
correction ville seulement 36 jours sur 59. Elle est moins
bonne que le risque simple (0,1263 contre 0,1055). On ne
la garde pas.

Sur le minimum du jour, le thermomètre aide plus
(0,0839 contre 0,1141 pour la correction ville).
Sur le maximum, l'écart est plus petit
(0,1294 contre 0,1511). Le prix reste devant partout
(0,0288 pour le min, 0,0914 pour le max).

À partir du 3 août seulement : 12 jours, 1 037 contrats.
Même sens (thermomètre 0,1089, correction ville 0,1313,
prix 0,0540). 12 jours, c'est trop peu tout seul.
Les 59 jours ci-dessus suffisent pour parler du marché.

## Décision

On ne change pas le modèle en ligne.

Pourquoi : regarder le thermomètre bat notre mélange déjà
corrigé ville par ville (0,1055 contre 0,1317, 56 jours
sur 59). Ça ne bat pas le prix (0,0585 contre 0,1055,
0 jour sur 59). On a 59 jours, donc plus que les 30
demandés. Le marché gagne. On ne promeut pas.

Le robot continue de viser demain, pas aujourd'hui.
Le prix du jour même a déjà vu le thermomètre.

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
