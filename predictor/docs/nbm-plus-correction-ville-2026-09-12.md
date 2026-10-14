# Mélanger NBM avec la correction ville

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Kalshi paie selon le chiffre officiel de la station.
NBM tout seul et notre correction ville tout seule ont chacun perdu
contre le marché. L'idée de cette étape : les mélanger.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle en ligne n'a pas été changé. Aucun pari avec
de l'argent réel.

## Est-ce que le mélange marche ?

**Non.** Il est un peu mieux que NBM tout seul, et un peu mieux que
la correction ville toute seule. Il perd encore contre le prix du
marché. On ne change rien.

## Ce qui a été fait

1. Prendre les mêmes prévisions NBM et le même chiffre officiel
   que l'étape A2. Rien n'a été retéléchargé. Rien n'a été inventé.
2. Garder seulement les contrats où les deux sources existent.
3. Faire deux mélanges, sans regarder le futur :
   - la moyenne : la moitié de chaque chance ;
   - un seul nombre appris avant le 3 août, comme à l'étape B3.
4. Noter les mêmes 36 jours que A1 et A2 (3 août au 7 septembre 2026).
5. Noter aussi la veille, quand un prix existait. On a retrouvé
   les 61 jours de l'étape A2.

Nombre appris : 0,246. En clair : on part de la correction ville,
on garde un quart de l'écart vers NBM. Si ce nombre était 0, on
garderait la correction ville. S'il était 1, on garderait NBM.

Les 18 villes ont répondu. Sur les 36 jours, aucun contrat n'a
manqué d'un côté. 69 jours ont servi à apprendre le nombre
(99 750 contrats). 36 jours pour tester (53 928 contrats).

## Le résultat, mêmes 36 jours que A1 et A2

Plus le score d'erreur est petit, mieux c'est.

| Méthode | Score d'erreur |
|---|---|
| Notre mélange actuel | 0,1250 |
| Notre mélange avec la correction ville | 0,1154 |
| NBM tout seul | 0,1197 |
| La moyenne des deux | 0,1148 |
| Le mélange avec le nombre appris | 0,1144 |

Le mélange avec le nombre appris bat la correction ville :
**31 jours sur 36**.
Il bat NBM : **35 jours sur 36**.
La moyenne simple bat la correction ville : seulement **22 jours
sur 36**. L'écart est petit.

À un jour d'avance, le mélange ajusté fait 0,1112. La correction
ville fait 0,1126. NBM fait 0,1174. L'écart reste petit.

Sur le maximum du jour, la moyenne est un peu devant
(0,1105 contre 0,1106 pour le nombre appris, et 0,1120 pour
la correction ville). Sur le minimum, le nombre appris est
un peu mieux (0,1182 contre 0,1188). Ce n'est pas assez
pour changer la conclusion.

## Contre le prix du marché

61 jours, la veille. On a retrouvé la fenêtre A2 : 4 948 contrats,
NBM 0,1351, notre mélange 0,1443, le marché 0,1249. Ce sont
les mêmes comptes qu'à l'étape A2.

Pour mélanger sans regarder le futur, la correction ville n'utilise
que les jours déjà passés au moment de la capture. 72 contrats
n'avaient pas encore assez de jours (il en faut 20). Ils sont
absents, pas remplacés. Restent 4 876 contrats, encore **61 jours**.

La vérité est le chiffre officiel de la station.

| Méthode | Score d'erreur |
|---|---|
| Prix du marché | 0,1251 |
| La moyenne NBM + correction ville | 0,1314 |
| NBM tout seul | 0,1351 |
| La correction ville honnête | 0,1357 |
| Notre mélange | 0,1443 |

La moyenne bat la correction ville : **45 jours sur 61**.
Elle bat NBM : **41 jours sur 61**.
Elle perd contre le marché : seulement **15 jours sur 61**.

Après le 3 août seulement (le nombre appris n'a pas le droit
de voir ces jours avant) : 13 jours, 1 016 contrats. Ce sont
les mêmes 13 jours que les étapes B1 et B3. Le marché fait
0,1204. Le mélange ajusté fait 0,1344. Il perd : **1 jour
sur 13**. 13 jours, c'est trop peu. La règle du projet
demande 30 jours.

## Décision

On ne change pas le modèle en ligne.

Pourquoi : le mélange est un peu mieux que nos deux sources
(0,1144 contre 0,1154 et 0,1197). Ce n'est pas rien. Mais il
perd contre le marché (0,1251 contre 0,1314, et seulement
15 jours gagnés sur 61). La règle du projet demande de battre
le marché de façon claire, sur au moins 30 jours. Ce n'est
pas le cas.

Le champion en ligne reste le mélange actuel, avec la
correction ville.

## Comment relancer le script

Dans le dossier `predictor`, sans internet (les fichiers sont déjà là) :

```
python scripts/eval_nbm_station_mix_skill.py
```

Le script écrit surtout :

- `data/truth/nbm_mix/nbm_mix_skill.md` : le tableau détaillé
- `data/truth/nbm_mix/nbm_mix_skill.json` : les mêmes comptes en machine

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel, avec la correction ville.
Pas de changement du texte du site. Pas de trading réel.
