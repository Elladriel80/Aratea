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

## Résultat

Les comptes mesurés seront remplis après l'exécution du script.
Aucun chiffre n'est inventé ici.
