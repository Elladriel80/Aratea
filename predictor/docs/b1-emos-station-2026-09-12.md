# Une correction plus complète, ville par ville et par saison

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Kalshi paie selon le chiffre officiel de la station.
Aujourd'hui, on décale déjà le mélange ville par ville (un écart fixe,
une largeur fixe). L'idée de cette étape : corriger aussi la pente et
la largeur, et le faire par saison, pas seulement par ville.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle en ligne n'a pas été changé. Aucun pari avec
de l'argent réel.

## Ce qu'on avait déjà (la correction ville)

La correction ville actuelle prend la moyenne de nos 5 prévisions,
ajoute un écart appris avant le 3 août, et fixe la largeur sur les
erreurs de ces mêmes jours. Deux nombres par ville, par max ou min,
et par horizon. C'est encore le meilleur de nos essais
(score d'erreur 0,1154 sur 36 jours).

## Ce qui a été fait

1. Prendre les mêmes prévisions et le même chiffre officiel que
   l'étape A1.
2. Apprendre quatre nombres par ville, par saison, par max ou min,
   et par horizon : où placer le centre, quelle pente, quelle largeur
   de base, et si la largeur doit grandir quand nos 5 prévisions
   ne sont pas d'accord.
3. Apprendre seulement avant le 3 août. Noter ensuite les mêmes
   36 jours que A1, A2 et A3 (3 août au 7 septembre 2026).
4. Comparer aussi au prix du marché, la veille, quand un prix existait.

Les 18 villes ont répondu. Aucun chiffre n'a été inventé.

## Trop peu de saisons

L'apprentissage va du 12 mai au 2 août 2026. C'est presque tout
l'été. Mai tout seul n'a pas 30 jours par ville : pas assez pour
sa propre saison. Septembre (7 jours de test) n'a aucun jour
d'apprentissage de l'automne. Ces 7 jours ont donc reçu la
correction d'été, sans saison.

On n'a pas l'hiver. On n'a pas un vrai cycle de saisons.
On l'écrit ici. On ne le cache pas.

## Le résultat, mêmes 36 jours que A1, A2 et A3

Plus le score d'erreur est petit, mieux c'est.

| Méthode | Score d'erreur |
|---|---|
| Notre mélange actuel | 0,1250 |
| Notre mélange avec la correction ville | 0,1154 |
| NBM tout seul (étape A2) | 0,1197 |
| Les 31 versions (étape A3) | 0,1486 |
| La correction plus complète (cette étape) | 0,1163 |

La correction plus complète perd contre la correction ville actuelle :
seulement **14 jours sur 36**.

Elle bat NBM : **27 jours sur 36**.
Elle bat notre mélange actuel : **33 jours sur 36**.

À un jour d'avance : 0,1131 contre 0,1126 pour la correction ville,
et 0,1174 pour NBM. L'écart est petit, dans le mauvais sens.

Sur le maximum du jour, la correction ville reste devant
(0,1120 contre 0,1143). Sur le minimum, la nouvelle correction
est un peu mieux (0,1183 contre 0,1188). Ce n'est pas assez
pour changer la conclusion.

## Contre le prix du marché

13 jours seulement, la veille, pendant les 36 jours de test.
On a à la fois le prix et la nouvelle correction. C'est moins
que les 61 jours de l'étape A2. Les jours de juin et juillet
ne peuvent pas servir : les nombres ont été appris jusqu'au
2 août. Les utiliser en juin, ce serait regarder le futur.

La vérité est le chiffre officiel de la station.

| Méthode | Score d'erreur |
|---|---|
| La correction plus complète | 0,1356 |
| La correction ville actuelle | 0,1390 |
| NBM | 0,1340 |
| Prix du marché | 0,1204 |

La nouvelle correction perd contre le marché : **2 jours sur 13**.
13 jours, c'est trop peu. La règle du projet demande 30 jours.

Sur les 61 jours déjà mesurés à l'étape A2, le marché fait 0,1249
et NBM fait 0,1351. On ne recalcule pas ces 61 jours avec la
nouvelle correction.

## Décision

On ne change pas le modèle en ligne.

Pourquoi : la correction plus complète ne bat pas la correction
ville actuelle (0,1163 contre 0,1154). Elle ne bat pas le marché
(0,1204 contre 0,1356, et seulement 13 jours). La règle du projet
demande de battre le marché de façon claire, sur au moins 30 jours.
Ce n'est pas le cas.

Les quatre nombres n'ont pas aidé plus que les deux nombres
déjà en place. On n'a vu qu'un été. Ce n'est pas une raison
de promouvoir. C'est une raison d'attendre plus de jours,
plusieurs saisons.

## Comment relancer le script

Dans le dossier `predictor`, sans internet (les fichiers sont déjà là) :

```
python scripts/eval_emos_skill.py
```

Le script écrit surtout :

- `data/truth/emos/emos_skill.md` : le tableau détaillé
- `data/truth/emos/emos_skill.json` : les mêmes comptes en machine

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel, avec la correction ville.
Pas de changement du texte du site. Pas de trading réel.
