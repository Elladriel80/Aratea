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

La vérité est le chiffre officiel de la station.
228 contrats sans correction ville encore apprise, 96 sans
chiffre officiel : absents, pas remplacés.

## Le résultat

Plus le score d'erreur est petit, mieux c'est.

### Hors marché, mêmes 36 jours que A1 (3 août au 7 septembre 2026)

53928 contrats.

| Méthode | Score d'erreur |
|---|---|
| Champion (= H1 hors marché) | 0,1154 |
| H1, une cloche | 0,1154 |
| H2, mélange des vendeurs | 0,1194 |

H2 perd contre H1 : **4 jours sur 36**.

C'est le même 0,1154 que la correction ville déjà mesurée.
Hors marché, "une seule courbe" est déjà ce qu'on fait.

À un jour d'avance : H1 0,1126, H2 0,1183.
Sur le maximum : H1 0,1120, H2 0,1170.
Sur le minimum : H1 0,1188, H2 0,1218.

### Contre le prix, 67 jours, 9973 contrats (cases du milieu)

Jour même et veille ensemble.

| Méthode | Score d'erreur |
|---|---|
| Prix du marché | 0,0907 |
| H1, une cloche | 0,1335 |
| Champion (cloche + passé) | 0,1336 |
| H2, mélange des vendeurs | 0,1383 |

H1 bat le champion : **32 jours sur 61** (p = 0,40). Pile ou face.
H1 bat le prix : **2 jours sur 67**.
H2 bat le prix : **2 jours sur 67**.
Le champion bat le prix : **2 jours sur 67**.

### Jour même (lead 0), 61 jours, 5097 contrats

| Méthode | Score d'erreur |
|---|---|
| Prix du marché | 0,0578 |
| Champion | 0,1314 |
| H1, une cloche | 0,1314 |
| H2, mélange des vendeurs | 0,1363 |

H1 et le champion sont identiques (0 jour d'écart).
H1 bat le prix : **0 jour sur 61**.
H2 bat le prix : **0 jour sur 61**.

### La veille (lead 1), 61 jours, 4876 contrats

| Méthode | Score d'erreur |
|---|---|
| Prix du marché | 0,1251 |
| H1, une cloche | 0,1357 |
| Champion | 0,1359 |
| H2, mélange des vendeurs | 0,1404 |

H1 bat le champion : **32 jours sur 61** (p = 0,40).
H1 bat le prix : **12 jours sur 61**.
H2 bat le prix : **9 jours sur 61**.
Le champion bat le prix : **13 jours sur 61**.

61 jours, c'est assez pour parler du marché.
Aucun des deux essais ne bat le prix.

### Les chances d'un même jour s'ajoutent-elles à 1 ?

2494 échelles ville-jour (1275 le jour même, 1219 la veille).
2493 ont les deux queues.

La veille, la cloche seule (H1) s'ajoute à **1,0000**.
Le champion (cloche + passé) s'ajoute à **1,0505**.
Sur 1219 échelles de la veille, 263 dépassent 1 de plus de 0,05,
et 249 de plus de 0,20.

Le jour même, champion et H1 sont la même cloche
(somme moyenne 0,9992).

Le prix s'ajoute à 1,0171 (2494 échelles). 590 fois l'écart
à 1 dépasse 0,05.

En clair : enlever le mélange avec le passé remet l'échelle
à 1. Ça ne suffit pas à battre le prix, ni vraiment le
champion (32 jours sur 61, p = 0,40).

## Décision

On ne change pas le modèle en ligne.

**Verdict : testée, ça n'aide pas.**

Pourquoi : le cœur du champion est déjà une seule courbe.
Enlever le mélange avec le passé (H1) change très peu
(0,1335 contre 0,1336, 32 jours sur 61). Le mélange des
vendeurs (H2) est moins bon (0,1383). Ni H1 ni H2 ne battent
le prix (2 jours sur 67). La règle du projet demande de
battre le marché de façon claire, sur au moins 30 jours.
Ce n'est pas le cas.

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
