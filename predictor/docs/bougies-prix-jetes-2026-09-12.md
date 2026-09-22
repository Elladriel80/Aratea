# Récupérer les prix jetés

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

On croyait jeter 78 % des contrats faute d'une bougie pile à 18:00 UTC.
On a mesuré. Rien n'a été inventé. Le modèle en ligne n'a pas été
changé. Aucun pari avec de l'argent réel.

## Ce qu'on a regardé

Le gros fichier déjà dans le dépôt (6 villes, du 11 avril au 13 juin
2026, la veille seulement) : 1 467 lignes, 62 jours.

Pour le même périmètre, on a relu les vrais prix horaires Kalshi
(archive historique, lecture seule). 1 535 contrats du milieu, déjà
résolus.

Deux règles, sur ces mêmes 1 535 contrats :

- Règle A : il faut une bougie à 18:00 UTC pile, avec un vrai prix.
- Règle B : on prend la dernière bougie avec un vrai prix dans les
  24 heures avant 18:00.

## Le compte

| Règle | Lignes | Jours |
|---|---|---|
| A, 18:00 pile | 1 496 | 64 |
| B, dernière bougie 24 h | 1 535 | 64 |

39 contrats n'ont pas de bougie à 18:00 pile.
Les 39 ont une bougie plus tôt dans les 24 heures. On les récupère
tous. Ce n'est pas 78 %. Le fichier grandit de 3 % (1,03 fois),
pas de 3 à 4 fois.

Même fenêtre, les 29 séries du catalogue (pas seulement les 6
du fichier backfill) :

| Règle | Lignes | Jours |
|---|---|---|
| A, 18:00 pile | 7 198 | 64 |
| B, dernière bougie 24 h | 7 419 | 64 |

221 contrats sans bougie à 18:00 pile. Les 221 sont récupérés.
Le fichier grandit encore de 3 % (1,03 fois). Ce n'est toujours
pas 78 %.

Le chiffre 5 374 / 78 % venait d'un ancien résumé qui n'est plus
dans le dépôt. On ne l'a pas retrouvé, ni sur les 6 villes, ni
sur les 29.

Les 1 467 lignes déjà gardées dans le dépôt en contiennent déjà
39 de la règle B. L'ancien script prenait déjà la dernière bougie
avant 18:00, pas seulement 18:00 pile.

## Est-ce que ça aide à noter le modèle ?

Un peu, pas assez pour changer la décision.

Plus le score d'erreur est petit, mieux c'est.

Prix tout seul, 6 villes du fichier backfill :

- Ensemble A (1 496 lignes, 64 jours) : 0,1263
- Ensemble B (1 535 lignes, 64 jours) : 0,1237

Prix tout seul, 29 séries (on ne mélange pas avec le champion,
qui n'existe que sur les 6 villes déjà notées) :

- Ensemble A (7 198 lignes, 64 jours) : 0,1320
- Ensemble B (7 419 lignes, 64 jours) : 0,1303

Là où notre mélange a déjà une chance (même fichier backfill,
62 jours, on ne mélange pas avec l'ensemble élargi) :

- Ensemble A : prix 0,1271, mélange 0,1330 (1 428 lignes)
- Ensemble B : prix 0,1243, mélange 0,1300 (1 467 lignes)

Le mélange perd encore contre le prix. 25 jours sur 62 sous B,
24 jours sur 62 sous A.

On a assez de jours (64, la règle en demande 30). On n'a pas
d'avantage clair. On ne promeut pas.

## Captures du quotidien

70 fichiers déjà là. 16 038 lignes avec un prix. Aucune n'est
tamponnée pile à 18:00:00 UTC. La plupart sont vers 19 h UTC.
Ce n'est pas le même problème que les bougies horaires.

## Décision

On ne change pas le modèle en ligne.

Pourquoi : récupérer les 39 prix aide un peu à comparer (plus de
contrats, même 64 jours). Ça ne multiplie pas le fichier par 3.
Le mélange ne bat pas le prix. La règle du projet n'est pas
remplie.

Le script de reconstruction peut maintenant :

- prendre la dernière bougie des 24 heures (règle B, par défaut) ;
- ou exiger 18:00 pile (règle A, pour comparer) ;
- relire l'archive Kalshi quand le marché est trop vieux pour
  l'API du jour (coupure vue le 12 septembre 2026 : 14 juillet).

Les 15 noms du catalogue de variables n'ont pas été renommés.

## Comment relancer le script

Dans le dossier `predictor`, les bougies déjà lues restent en cache :

```
python scripts/eval_candle_recovery.py --offline-only
```

Pour retélécharger ce qui manque (lecture seule, pas d'achat) :

```
python scripts/eval_candle_recovery.py --fetch
```

Le script écrit :

- `data/truth/candles/candle_recovery.md`
- `data/truth/candles/candle_recovery.json`

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel.
Pas de changement du texte du site. Pas de trading réel.
On n'a pas relancé NBM, GEFS, ni les autres essais du 12 septembre.
