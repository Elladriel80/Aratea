# Les vraies versions du modèle, pas seulement 5 chiffres

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Kalshi paie selon le chiffre officiel de la station.
Jusqu'ici, notre mélange prenait 5 prévisions (un chiffre chacune) et
fabriquait une cloche autour. L'idée de cette étape : utiliser les
vraies versions d'un même modèle (31 versions du modèle américain),
compter combien tombent dans chaque contrat de 2 degrés, et comparer
au chiffre officiel.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle en ligne n'a pas été changé. Aucun pari avec
de l'argent réel.

## Ce qui a été possible, et ce qui a échoué

On a d'abord demandé les versions à Open-Meteo (Europe 51, Europe IA 51,
Amérique 31, Google 64). Open-Meteo n'a répondu avec des versions
remplies que du 9 au 12 septembre. Les jours du test (3 août au
7 septembre) sont vides. Rien n'a été inventé.

L'archive européenne n'a plus les fichiers d'août. On l'écrit ici.

Open-Meteo garde plus longtemps la moyenne des versions, pas les
versions elles-mêmes. Ce n'est pas ce qu'on voulait. On ne s'en sert pas.

On a donc pris l'archive publique américaine (GEFS, 31 versions),
tous les jours à 0 h UTC, du 27 juillet au 6 septembre. Les 18 villes
ont répondu. 164 petits refus temporaires du serveur. Ces heures sont
absentes, pas remplacées. Il restait 28 à 31 versions selon le jour.
Les 36 jours du test sont là. Aucun chiffre n'a été inventé.

La correction ville par ville est la même table que l'étape A1,
apprise avant le 3 août, pas sur les jours de test.

## Le résultat, mêmes 36 jours que A1 et A2 (3 août au 7 septembre 2026)

Plus le score d'erreur est petit, mieux c'est.

| Méthode | Score d'erreur |
|---|---|
| Notre mélange actuel | 0,1250 |
| Notre mélange avec la correction ville par ville | 0,1154 |
| NBM tout seul (étape A2) | 0,1197 |
| Les 31 versions, toutes seules | 0,1486 |
| Les 31 versions avec la correction ville | 0,1430 |

Les 31 versions perdent contre notre mélange actuel : **0 jour sur 36**.
Les 31 versions perdent contre le mélange déjà corrigé ville par ville :
**0 jour sur 36**.
Les 31 versions perdent contre NBM : **0 jour sur 36**.

Même avec la correction ville, les 31 versions restent derrière
(0,1430 contre 0,1154).

À un jour d'avance, les 31 versions font 0,1629. Notre mélange fait
0,1259. Le mélange déjà corrigé fait 0,1125. NBM fait 0,1174.

Sur le maximum du jour, l'écart est plus petit (0,1356 contre 0,1240
pour le mélange). Sur le minimum, les 31 versions sont plus loin
(0,1615 contre 0,1260).

## Contre le prix du marché

15 jours, la veille seulement. On a à la fois le prix et les 31 versions.
C'est moins que les 61 jours de l'étape A2 : on n'avait les versions
que depuis fin juillet. La vérité est le chiffre officiel de la station.

| Méthode | Score d'erreur |
|---|---|
| Les 31 versions | 0,1838 |
| Notre mélange | 0,1449 |
| NBM | 0,1324 |
| Prix du marché | 0,1179 |

Les 31 versions perdent contre le marché : **0 jour sur 15**.
Les 31 versions battent notre mélange : **1 jour sur 15**.

## Décision

On ne change pas le modèle en ligne.

Pourquoi : les 31 versions ne battent ni le marché, ni le mélange
déjà corrigé ville par ville, ni NBM, ni même le mélange actuel.
La règle du projet demande de battre le marché de façon claire, sur
au moins 30 jours. Ce n'est pas le cas.

Compter les versions est plus honnête qu'une cloche sur 5 chiffres.
Sur ces 36 jours, cela n'a pas suffi. Les versions toutes seules
sont trop sûres d'elles : trop de poids sur le mauvais contrat.

## Comment relancer le script

Dans le dossier `predictor`, avec internet :

```
python scripts/eval_ensemble_members_skill.py
```

Sans retélécharger (les versions station sont déjà là) :

```
python scripts/eval_ensemble_members_skill.py --skip-fetch
```

Le script écrit surtout :

- `data/gefs/extracted.json` : les 31 versions, jour par jour
- `data/truth/ensemble/ensemble_skill.md` : le tableau détaillé
- `data/truth/ensemble/ensemble_skill.json` : les mêmes comptes en machine

Pour la lecture GRIB, le script a besoin du paquet `eccodes`
(`pip install eccodes`).

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel, avec la correction ville.
Pas de changement du texte du site. Pas de trading réel.
