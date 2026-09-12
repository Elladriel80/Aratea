# Partir du prix, au lieu de le combattre

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Le prix du marché est déjà meilleur que notre mélange.
L'idée de cette étape : partir de ce prix, et n'apprendre que
l'écart entre notre mélange et ce prix.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle en ligne n'a pas été changé. Aucun pari avec
de l'argent réel.

## D'où viennent les prix

Aucun prix n'a été inventé.

Les prix viennent des captures déjà enregistrées (le milieu entre
l'achat et la vente, au moment de la capture). C'est la même source
que les étapes A2 et B1, et que l'ancien apprentissage.

Le carnet papier a aussi des prix réels : 780 lignes, 780 avec un
prix, 61 jours (11 mai au 11 septembre 2026). On les a lus pour
vérifier. On ne les mélange pas avec les captures : ce n'est pas
la même heure.

## Ce qui a été fait

1. Prendre le mélange déjà corrigé ville par ville (le meilleur
   essai maison : score d'erreur 0,1154 sur 36 jours, sans avoir
   besoin d'un prix).
2. Sur les jours avant le 3 août, là où un prix existait, apprendre
   un seul nombre : quelle part de l'écart avec le prix garder.
3. Noter ensuite les jours à partir du 3 août, la veille seulement,
   quand un prix et un modèle existent. Ce sont les mêmes 13 jours
   et les mêmes 1016 contrats que l'étape B1.
4. Comparer aussi à NBM et au prix tout seul.

Nombre appris : 0,255. En clair : on part du prix, on garde un
quart de l'écart. Si ce nombre était 0, on garderait le prix.
S'il était 1, on garderait notre mélange.

48 jours pour apprendre (3860 contrats). 13 jours pour tester
(1016 contrats). Les 18 villes ont répondu. Rien n'a été inventé.

## Le résultat, 13 jours avec un prix

Plus le score d'erreur est petit, mieux c'est.

| Méthode | Score d'erreur |
|---|---|
| Prix du marché tout seul | 0,1204 |
| Prix + un quart de notre écart | 0,1225 |
| NBM tout seul | 0,1340 |
| Notre mélange avec la correction ville | 0,1390 |

Le mélange avec le prix bat la correction ville seule :
**12 jours sur 13**.
Il bat NBM : **10 jours sur 13**.
Il perd contre le prix tout seul : seulement **2 jours sur 13**.

13 jours, c'est trop peu. La règle du projet demande 30 jours
pour parler du marché.

Sur les 61 jours déjà mesurés à l'étape A2 (la veille), le marché
fait 0,1249 et NBM fait 0,1351. On ne change pas ces comptes.

## Quand un désaccord compte

Règle simple : on ne traite un écart mélange / prix comme réel
que s'il est plus grand que l'erreur de réglage mesurée.

Cette erreur, mesurée avant le 3 août, est de 0,6 point
(0,0062). C'est tout petit : nos chances tombent à peu près juste.

Du coup, presque tous les écarts passent la barre :
962 contrats sur 1016 au test, soit 95 sur 100. Les 13 jours
sont encore là.

Même sur ces 962 contrats, le prix reste devant
(0,1233 contre 0,1255). Cette règle ne change rien.

Autre lecture, plus large : l'écart moyen au vrai résultat
est de 27 points pour notre mélange, 26 points pour le prix.
Un écart de 17 points, déjà vu dans le journal, est plus petit
que ça. Ce n'est pas un signal. C'est le bruit habituel.

## Décision

On ne change pas le modèle en ligne.

Pourquoi : 13 jours seulement, et le mélange avec le prix
ne bat pas le prix tout seul (0,1225 contre 0,1204).
Il bat notre mélange et NBM, ce qui est normal : il part
déjà du prix. La règle du projet demande de battre le marché
de façon claire, sur au moins 30 jours. Ce n'est pas le cas.

On n'a pas assez de jours. On ne promeut pas.

## Comment relancer le script

Dans le dossier `predictor`, sans internet (les fichiers sont déjà là) :

```
python scripts/eval_stacking_skill.py
```

Le script écrit surtout :

- `data/truth/stacking/stacking_skill.md` : le tableau détaillé
- `data/truth/stacking/stacking_skill.json` : les mêmes comptes en machine

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel, avec la correction ville.
Pas de changement du texte du site. Pas de trading réel.
