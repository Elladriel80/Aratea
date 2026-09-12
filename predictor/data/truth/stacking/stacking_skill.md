# Combiner avec le prix du marché

Généré : 2026-09-12T14:53:39Z. Apprentissage des poids < 2026-08-03. Test ≥ 2026-08-03, la veille seulement, mêmes contrats que B1 quand un prix existe.

On part du prix réel (kalshi_mid des captures, jamais inventé). On apprend un seul nombre : quelle part de l'écart entre le mélange déjà corrigé ville par ville et ce prix garder. La vérité est le chiffre officiel de la station (même fichier que A1).

Nombre appris w = 0.2553. w = 0 voudrait dire : garder le prix. w = 1 voudrait dire : garder le mélange corrigé.

Lignes d'apprentissage (prix + modèle) : 3860 (48 jours). Lignes de test : 1016 (13 jours). Dont avec NBM : 1016.

Carnet papier : 780 lignes, 780 avec un prix, 61 jours (2026-05-11 → 2026-09-11). Ces prix ne remplacent pas ceux des captures : ce n'est pas le même instant. On les lit pour confirmer que des prix réels existent. Le module d'apprentissage utilise déjà yes_mid des mêmes captures.

Erreur de calibration du mélange corrigé (apprentissage) : 0.0062. Celle du prix : 0.0131. Écart moyen au vrai résultat, mélange corrigé : 0.2650. Un désaccord n'est traité comme réel que s'il est plus grand que l'erreur de calibration du mélange.

Désaccords réels à l'apprentissage : 3624 / 3860 (0.9389).
Désaccords réels au test : 962 / 1016 (0.9469), 13 jours.

34020 prévisions NBM déjà là (A2).

Lignes écartées à la lecture des captures : {'no_cli_truth': 60}.

Comparaison principale : les mêmes contrats que A2/B1, la veille, seulement quand un prix et un modèle existent. Plus le score d'erreur est petit, mieux c'est.

### Test, la veille (prix + mélange corrigé)

| groupe | n bins | n dates | Brier mélange+prix | Brier correction ville | Brier marché | Brier NBM | Brier mélange brut |
|---|---|---|---|---|---|---|---|
| all | 1016 | 13 | 0.1225 | 0.1390 | 0.1204 | 0.1340 | 0.1478 |

### Apprentissage (même règle, avant le split)

| groupe | n bins | n dates | Brier mélange+prix | Brier correction ville | Brier marché | Brier NBM |
|---|---|---|---|---|---|---|
| all | 3860 | 48 | 0.1256 | 0.1319 | 0.1263 | 0.1354 |

### Test par max / min

| variable | n bins | n dates | Brier mélange+prix | Brier correction ville | Brier marché | Brier NBM |
|---|---|---|---|---|---|---|
| temp_max | 456 | 13 | 0.1340 | 0.1601 | 0.1306 | 0.1441 |
| temp_min | 560 | 12 | 0.1131 | 0.1218 | 0.1122 | 0.1257 |

### Test, seulement les lignes avec NBM

| groupe | n bins | n dates | Brier mélange+prix | Brier correction ville | Brier marché | Brier NBM |
|---|---|---|---|---|---|---|
| all | 1016 | 13 | 0.1225 | 0.1390 | 0.1204 | 0.1340 |

### Victoires jour par jour

| comparaison | jours | victoires du premier | chance que ce soit le hasard |
|---|---|---|---|
| stack_vs_market | 13 | 2 | 0.9983 |
| stack_vs_station | 13 | 12 | 0.0017 |
| station_vs_market | 13 | 1 | 0.9999 |
| stack_vs_nbm | 13 | 10 | 0.0461 |
| nbm_vs_market | 13 | 3 | 0.9888 |

Décision : on ne change pas le modèle en ligne. Pas de promotion : 13 jours de test avec un prix, il en faut 30.

Le modèle en ligne n'est pas changé. Le site public n'est pas changé. Pas de pari avec de l'argent réel.

