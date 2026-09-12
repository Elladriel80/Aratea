# Une seule courbe

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Kalshi paie une seule case de 2 degrés par ville et par jour.
Les cases d'un même jour s'excluent : une seule peut gagner.
L'idée de cette étape : prédire une courbe continue pour le max
ou le min, puis découper les cases (et les queues).

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle en ligne n'a pas été changé. Aucun pari avec
de l'argent réel. Aucun chiffre n'a été inventé.

## Comment le champion assigne P(case) aujourd'hui

Ce n'est pas un modèle qui prédit chaque case toute seule
(comme l'ancien apprentissage). Le mélange actuel fait déjà
ceci, dans l'ordre :

1. Il prend la moyenne des prévisions (nos 5 chiffres).
2. Il fabrique une cloche autour (largeur = désaccord des
   modèles, plancher 1 degré, ou largeur apprise ville par ville).
3. Il découpe cette cloche pour chaque case de 2 degrés
   (avec l'arrondi officiel de plus ou moins 0,5 degré).
4. Ensuite, il mélange chaque case avec une fréquence du passé
   (combien de fois cette case est tombée, les années d'avant).
   Le poids de ce passé grandit quand on est loin du jour.
   Le jour même, ce poids est zéro : on garde la cloche seule.
   La veille, on garde encore beaucoup la cloche, plus un peu
   de passé.
5. Il ne remet pas les chances à 1 entre les cases d'un même jour.

Donc : le cœur est déjà une seule courbe. Ce qui casse
l'échelle, c'est le mélange case par case avec le passé
(étape 4), et l'absence de remise à 1 (étape 5).

La correction ville ne change pas ça : elle décale le centre
et fixe la largeur, puis on découpe encore la même cloche.

## Les deux hypothèses mesurées

Même prévisions, même correction ville, mêmes contrats.

**H1, courbe gauss.** La cloche déjà calculée, sans le mélange
avec le passé. C'est "une seule courbe, puis on découpe".

**H2, courbe mélange.** Une cloche autour de chaque prévision
(même décalage ville, même largeur), on les moyenne, puis on
découpe. C'est encore une seule densité, avec plusieurs bosses
si les modèles ne sont pas d'accord. Ce n'est pas les 31 versions
du modèle américain (déjà mesuré, ça n'aide pas).

**A, champion.** H1, plus le mélange avec le passé case par case
(formule actuelle).

**Prix.** Le milieu du marché, quand il existe.

Hors marché (36 jours déjà utilisés pour A1), le mélange avec
le passé n'existe pas. A et H1 sont donc la même chose.
Seul H2 peut changer le score.

Le jour même, le mélange avec le passé pèse zéro. A et H1
sont encore la même chose. Seul H2 peut changer le score.
La veille, A et H1 peuvent différer.

## Le résultat

Les comptes machine sont dans `data/truth/curve/curve_skill.json`.
Le tableau détaillé est dans `data/truth/curve/curve_skill.md`.
Les chiffres ci-dessous viennent de ce script, rien d'autre.

Plus le score d'erreur est petit, mieux c'est.

### Hors marché, mêmes 36 jours que A1 (3 août au 7 septembre 2026)

À remplir après l'exécution du script. Ne pas inventer.

### Contre le prix, jour même et veille, séparés

À remplir après l'exécution du script. Ne pas inventer.

## Décision

À remplir après l'exécution du script.

Règle inchangée : on ne parle de promotion que si on bat le prix
de façon claire, sur au moins 30 jours distincts.

## Comment relancer le script

Dans le dossier `predictor`, sans internet (les fichiers sont déjà là) :

```
python scripts/eval_single_curve_skill.py
```

Le script écrit surtout :

- `data/truth/curve/curve_skill.md` : le tableau détaillé
- `data/truth/curve/curve_skill.json` : les mêmes comptes en machine

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel, avec la correction ville.
Pas de changement du texte du site. Pas de trading réel.
Pas de NBM, pas de 31 versions, pas de thermomètre du jour,
pas d'histoire-siècle, pas de densités, pas de second marché,
pas de récupération de bougies. WeatherNext 3 n'est pas commencé.
