# Prévision heure par heure du matin même

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

L'idée : pour un contrat « max (ou min) aujourd'hui », utiliser le
run HRRR de 12 h UTC du jour même, pour les heures encore ouvertes
du jour officiel. Pas la prévision de la veille. Pas le thermomètre
déjà mesuré.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle en ligne n'a pas été changé. Aucun pari avec
de l'argent réel.

Les 15 noms du catalogue des variables restent les mêmes. Le nom
stable de cette piste est : HRRR du matin même.

## Ce qu'on a trouvé avant de mesurer

Le robot ne parie pas sur aujourd'hui. Il vise seulement demain.
On n'a pas changé ça.

La prévision de la veille (déjà mesurée avec le thermomètre du jour)
avait empiré le score. On ne l'a pas rejouée.

Le champ « jour 0 » d'Open-Meteo recoud plusieurs runs. Ce n'est pas
le run du matin. On ne s'en est pas servi.

Le run de 12 h UTC est public vers 13 h UTC. On n'a noté un prix
que s'il était pris à 13 h ou plus tard. 152 captures trop tôt :
on ne les a pas inventées.

Archive Open-Meteo Single Runs : depuis le 2 avril 2026. Notre
fenêtre commence le 1er mai. Les 18 villes ont répondu. Le 11 juin,
le run est là (48 heures) mais toutes les températures sont vides.
On n'a rien mis à la place. 133 jours avec des heures, pas 134.

## Comment on a noté

Pour chaque jour, à 12 h UTC :

1. Prendre le run HRRR de ce matin-là seulement.
2. Garder les heures encore dans le jour officiel (heure d'hiver
   locale), après 12 h.
3. En tirer un max et un min.
4. Transformer ça en chance pour chaque case de 2 degrés.
5. Comparer au chiffre officiel de la station (même fichier que
   l'étape A1), au mélange avec la correction ville, et au prix
   du marché.

La largeur de la cloche est apprise avant le 3 août, pas sur les
jours de test. J0 et J-1 restent séparés.

## Le résultat, 60 jours avec un prix le jour même

Plus le score d'erreur est petit, mieux c'est.
4 985 contrats. 18 villes. 1er mai au 11 septembre 2026.
Prix pris à 13 h UTC ou plus tard.

| Méthode | Score d'erreur |
|---|---|
| HRRR du matin même | 0,1418 |
| Notre mélange avec la correction ville | 0,1316 |
| Notre mélange actuel | 0,1425 |
| Prix du marché | 0,0573 |

Le run du matin bat la correction ville : **18 jours sur 60**.

Il perd contre le prix : **0 jour sur 60**.

Sur le maximum du jour, le run du matin est un peu moins mauvais
que la correction ville (0,1470 contre 0,1518).
Sur le minimum, il est plus loin (0,1370 contre 0,1131).
Le prix reste devant partout (0,0903 pour le max, 0,0274 pour le min).

À partir du 3 août seulement : 12 jours, 1 037 contrats.
Même sens (HRRR 0,1398, correction ville 0,1313, prix 0,0540).
12 jours, c'est trop peu tout seul.
Les 60 jours ci-dessus suffisent pour parler du marché.

Hors marché, cases de 2 degrés autour du max ou du min du matin :
0,1244 sur 133 jours (28 722 contrats).
Même fenêtre que A1 (3 août au 7 septembre) : 0,1244 sur 36 jours
(7 776 contrats). Ce ne sont pas les mêmes cases que le 0,1154
de la correction ville. On ne les mélange pas.

## Décision

On ne change pas le modèle en ligne.

Pourquoi : le run du matin ne bat pas le prix (0,0573 contre
0,1418, 0 jour sur 60). Il ne bat pas non plus la correction
ville (0,1316 contre 0,1418, 18 jours sur 60). On a 60 jours,
donc plus que les 30 demandés. Le marché gagne. On ne promeut pas.

Le robot continue de viser demain, pas aujourd'hui.
Le prix du jour même a déjà vu le thermomètre. Un run du matin
ne suffit pas.

Verdict : testée, ça n'aide pas.

## Comment relancer le script

Dans le dossier `predictor`, avec internet :

```
python scripts/eval_hrrr_morning_skill.py
```

Sans retélécharger (les runs du matin sont déjà là) :

```
python scripts/eval_hrrr_morning_skill.py --skip-fetch
```

Le script écrit surtout :

- `data/hrrr_morning/extracted.json` : le run de 12 h, heure par heure
- `data/truth/hrrr_morning/hrrr_morning_skill.md` : le tableau détaillé
- `data/truth/hrrr_morning/hrrr_morning_skill.json` : les mêmes comptes en machine

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel, avec la correction ville.
Le robot continue de viser demain, pas aujourd'hui.
Pas de changement du texte du site. Pas de trading réel.
On n'a pas relancé les essais déjà tranchés le 12 septembre.
On n'a pas commencé la phase 2.
