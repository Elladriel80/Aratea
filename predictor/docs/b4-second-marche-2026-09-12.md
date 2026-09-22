# Second marché

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

**Variable :** Second marché. Polymarket cote chaque jour la température
max sur des dizaines de villes. La question : l'écart de prix entre
Kalshi et Polymarket aide-t-il notre modèle de chances ?

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle en ligne n'a pas été changé. Aucun pari avec
de l'argent réel.

## D'où viennent les prix

Aucun prix n'a été inventé.

Kalshi : les captures déjà dans le dépôt (`forward_*.json`). 70 fichiers,
16 158 lignes, dont 7 770 contrats de max, 7 710 avec un prix des deux
côtés, 70 jours (8 mai au 12 septembre 2026). Au départ : zéro fichier
Polymarket.

Polymarket : lu le 12 septembre 2026 sur l'API publique
`gamma-api.polymarket.com` (liste des événements) et
`clob.polymarket.com/prices-history` (dernier prix avant notre capture).
Sans une fenêtre de dates (`startTs` / `endTs`), l'historique des
vieux marchés revient souvent vide. On l'a demandé. On n'a pas
fabriqué de point manquant.

Vérité : le chiffre officiel de la station Kalshi, déjà dans
`cli_daily.json`.

## Comment on a comparé

1. Garder les villes où les deux marchés existent (Atlanta, Dallas,
   Houston, Miami, San Francisco, Seattle pour le max).
2. Ne comparer que si la case de 2 °F est la même (exemple : 76 à 77
   des deux côtés). Si les échelles sont décalées d'un degré, on jette
   la ligne. On ne coupe pas une case en deux.
3. Prendre le prix Kalshi de la capture, et le dernier prix Polymarket
   à la même heure ou juste avant. Pas après.
4. Noter les deux contre le chiffre officiel Kalshi (Brier, comme
   d'habitude).
5. Essayer aussi la moyenne des deux prix, et Kalshi plus un peu de
   l'écart (un seul nombre appris avant le 3 août).

Le robot vise surtout la veille. C'est la lecture principale.

## Ce qui n'a pas pu être comparé

Sur 3 732 lignes Kalshi max dans une ville mappable :

- 2 341 : la case n'est pas la même (les deux marchés ne coupent pas
  le thermomètre au même endroit ce jour-là).
- 60 : pas d'événement Polymarket ce jour-là.
- 8 : pas encore de chiffre officiel.

Boston, Las Vegas, Minneapolis, Phoenix et San Antonio ont beaucoup
de max Kalshi, mais pas de série Polymarket quotidienne trouvée le
12 septembre. New York et Los Angeles ont Polymarket, mais pas de
captures Kalshi max dans le dépôt.

Le 12 septembre, Polymarket avait 48 villes « Highest temperature »
ouvertes (compte mesuré). Le journal parlait de 44. On garde le nom
Second marché. On n'invente pas 44.

Dallas : Kalshi paie DFW, Polymarket paie Love Field. On le dit. On
a aussi regardé le sous-ensemble où la station est la même.

Polymarket paie souvent le max horaire NOAA. Kalshi paie le rapport
officiel du jour. Même aéroport, ce n'est pas forcément le même
chiffre. On n'a pas inventé de correction.

## Le résultat, la veille, 58 jours

649 contrats. 159 villes-jours. 6 villes. 11 mai au 11 septembre 2026.
Plus le score d'erreur est petit, mieux c'est.

| Méthode | Score d'erreur |
|---|---|
| Prix Kalshi | 0,1397 |
| Prix Polymarket | 0,1422 |
| Moyenne des deux | 0,1393 |
| Kalshi + un peu de l'écart | 0,1395 |

Écart moyen entre les deux prix : 6,2 points (0,0615).

Polymarket bat Kalshi : 27 jours sur 58.
La moyenne bat Kalshi : 27 jours sur 58.
Kalshi plus l'écart bat Kalshi : 30 jours sur 58 (p = 0,45).

12 jours seulement à partir du 3 août : trop peu tout seuls
(moyenne 0,1200 contre 0,1227 pour Kalshi).

Même station (Atlanta, Houston, Miami, San Francisco, Seattle) :
520 contrats, 128 villes-jours, 57 jours. Kalshi 0,1437,
Polymarket 0,1433, moyenne 0,1419. La moyenne gagne 28 jours,
perd 29.

Le jour même (61 jours) : Kalshi 0,0930, Polymarket 0,1315.
Le prix Kalshi du jour a déjà vu le thermomètre. Polymarket
n'aide pas.

Nombre appris pour l'écart, avant le 3 août : 0,057. Presque
zéro : on garde Kalshi.

## Décision

On ne change pas le modèle en ligne.

**Verdict : testée ça n'aide pas.**

Pourquoi : 58 jours, donc assez pour parler du marché. Polymarket
seul est moins bon que Kalshi (0,1422 contre 0,1397, 27 jours
gagnés sur 58). La moyenne est presque égale à Kalshi (0,1393
contre 0,1397) et perd 31 jours sur 58. L'écart comme petit
correctif ne passe pas le test habituel (p = 0,45, il en faut
moins de 0,05). Ce n'est pas un signal utile.

Pour débloquer une mesure plus large : capturer les deux prix
le même jour sur la même case (aujourd'hui 2 341 lignes sont
jetées parce que les cases ne tombent pas juste), et avoir des
max Kalshi pour New York et Los Angeles, déjà cotés chez
Polymarket.

## Comment relancer le script

Dans le dossier `predictor`, sans retélécharger (les lignes
jointes sont déjà là) :

```
python scripts/eval_second_marche.py --skip-fetch
```

Avec internet, pour relire Gamma et CLOB :

```
python scripts/eval_second_marche.py
```

Le script écrit surtout :

- `data/polymarket/extracted_events.json` : les événements lus
- `data/truth/second_marche/joined_rows.json` : les lignes comparées
- `data/truth/second_marche/second_marche_skill.md` : le tableau
- `data/truth/second_marche/second_marche_skill.json` : les mêmes
  comptes en machine

## Ce que cette étape ne fait pas

Le modèle en ligne reste le mélange actuel, avec la correction ville.
Pas de changement du texte du site. Pas de trading réel.
