# La prévision déjà corrigée pour la station

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Kalshi paie selon le chiffre officiel de la station.
Le service météo américain publie aussi, pour chaque station, une prévision
déjà corrigée : cinq seuils (10 %, 25 %, 50 %, 75 %, 90 %). On ne l'utilisait pas.
On l'appelle NBM dans les fichiers.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas été changé.
Le modèle en ligne n'a pas été changé. Aucun pari avec de l'argent réel.

## Ce qui a été fait

1. Télécharger ces prévisions pour les 18 villes, du 25 mai au 6 septembre 2026,
   une fois par jour à 13 h UTC.
2. Relier les cinq seuils pour donner une chance à chaque contrat de 2 degrés.
3. Comparer au chiffre officiel de la station (même fichier que l'étape A1).
4. Comparer aussi à notre mélange actuel, à la moyenne des années passées
   à la station, et au prix du marché quand on l'avait.

Les 18 villes ont bien répondu. Aucun fichier du 25 mai au 6 septembre n'a
manqué. Aucun chiffre n'a été inventé.

Une autre source (IEM) n'a que les tout derniers bulletins, pas l'été 2026.
On l'écrit ici. On a utilisé l'archive publique NOAA.

Le 1er septembre, on a aussi ouvert les deux autres bulletins (un chiffre
unique plus un écart). Ils ont répondu pour les 18 villes. Le test principal
utilise le bulletin à cinq seuils.

## Le résultat, mêmes 36 jours que A1 (3 août au 7 septembre 2026)

Plus le score d'erreur est petit, mieux c'est.

| Méthode | Score d'erreur |
|---|---|
| Notre mélange actuel | 0,1250 |
| Notre mélange avec la correction ville par ville | 0,1154 |
| Moyenne des années passées à la station | 0,1278 |
| NBM tout seul | 0,1197 |

NBM tout seul bat notre mélange actuel : **31 jours sur 36**.
NBM tout seul bat la moyenne des années passées : **33 jours sur 36**.
NBM tout seul perd contre notre mélange déjà corrigé ville par ville :
seulement **5 jours sur 36**.

Sur le maximum du jour, NBM aide plus (0,1144 contre 0,1240 pour le mélange).
Sur le minimum, l'écart est petit (0,1251 contre 0,1260).

À un jour d'avance, NBM fait 0,1174. Notre mélange fait 0,1259.
Notre mélange déjà corrigé ville par ville fait 0,1126. Il reste devant.

## Contre le prix du marché

61 jours, la veille seulement. On a à la fois le prix et le bulletin NBM.
La vérité est le chiffre officiel de la station.

| Méthode | Score d'erreur |
|---|---|
| Notre mélange | 0,1443 |
| NBM tout seul | 0,1351 |
| Prix du marché | 0,1249 |

NBM bat notre mélange : **44 jours sur 61**.
NBM perd contre le marché : seulement **14 jours sur 61**.

## Décision

On ne change pas le modèle en ligne.

Pourquoi : le mélange avec la correction ville par ville reste meilleur
que NBM tout seul (0,1154 contre 0,1197). Le marché reste meilleur que NBM
(0,1249 contre 0,1351). La règle du projet demande de battre le marché
de façon claire, sur au moins 30 jours. Ce n'est pas le cas.

On pourra plus tard mélanger NBM avec notre correction. Ce n'est pas
cette étape.

## Comment relancer le script

Dans le dossier `predictor`, avec internet :

```
python scripts/eval_nbm_skill.py
```

Sans retélécharger (les prévisions station sont déjà là) :

```
python scripts/eval_nbm_skill.py --skip-fetch
```

Le script écrit surtout :

- `data/nbm/extracted.json` : les prévisions station, jour par jour
- `data/truth/nbm/nbm_skill.md` : le tableau détaillé
- `data/truth/nbm/nbm_skill.json` : les mêmes comptes en machine

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel, avec la correction ville.
Pas de changement du texte du site. Pas de trading réel.
