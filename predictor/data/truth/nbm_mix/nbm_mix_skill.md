# Mélanger NBM et la correction ville

Généré : 2026-09-12T15:48:45Z. Split TRAIN < 2026-08-03, HOLDOUT ≥ 2026-08-03 jusqu'au 2026-09-07. Leads [1, 2, 3, 4, 5, 6, 7].

On ne garde que les contrats où NBM et la correction ville existent tous les deux. Aucun chiffre manquant n'a été inventé. La vérité est le chiffre officiel de la station (même fichier que A1).

Nombre appris w = 0.2456. w = 0 voudrait dire : garder la correction ville. w = 1 voudrait dire : garder NBM. La moyenne simple est 0,5 / 0,5, sans apprentissage.

Lignes d'apprentissage (NBM + correction ville) : 99750 (69 jours). Lignes de test skill : 53928 (36 jours). Lignes skill avec NBM mais sans correction ville : 0.

34020 prévisions NBM déjà là (A2).

Comparaison principale : les mêmes contrats que A2, 36 jours, seulement là où les deux sources existent. Plus le score d'erreur est petit, mieux c'est.

### Même contrats que l'ensemble (HOLDOUT, NBM + correction ville)

| groupe | n bins | n dates | Brier moyenne | Brier ajusté | Brier correction ville | Brier NBM | Brier mélange brut |
|---|---|---|---|---|---|---|---|
| all | 53928 | 36 | 0.1148 | 0.1144 | 0.1154 | 0.1197 | 0.1250 |

### Apprentissage (même règle, avant le split)

| groupe | n bins | n dates | Brier moyenne | Brier ajusté | Brier correction ville | Brier NBM |
|---|---|---|---|---|---|---|
| all | 99750 | 69 | 0.1120 | 0.1114 | 0.1119 | 0.1165 |

### Par horizon (jours d'avance)

| lead | n bins | n dates | Brier moyenne | Brier ajusté | Brier correction ville | Brier NBM |
|---|---|---|---|---|---|---|
| 1 | 7704 | 36 | 0.1116 | 0.1112 | 0.1126 | 0.1174 |
| 2 | 7704 | 36 | 0.1141 | 0.1138 | 0.1150 | 0.1198 |
| 3 | 7704 | 36 | 0.1138 | 0.1133 | 0.1143 | 0.1193 |
| 4 | 7704 | 36 | 0.1156 | 0.1152 | 0.1161 | 0.1205 |
| 5 | 7704 | 36 | 0.1158 | 0.1153 | 0.1160 | 0.1207 |
| 6 | 7704 | 36 | 0.1160 | 0.1157 | 0.1166 | 0.1200 |
| 7 | 7704 | 36 | 0.1167 | 0.1163 | 0.1171 | 0.1204 |

### Par max / min

| variable | n bins | n dates | Brier moyenne | Brier ajusté | Brier correction ville | Brier NBM |
|---|---|---|---|---|---|---|
| temp_max | 26964 | 36 | 0.1105 | 0.1106 | 0.1120 | 0.1144 |
| temp_min | 26964 | 36 | 0.1191 | 0.1182 | 0.1188 | 0.1251 |

Prix de marché (kalshi_mid), la veille seulement. La fenêtre A2 compte les jours avec un prix et un bulletin NBM. Le mélange n'est noté que si la correction ville existe aussi, sans regarder le futur : on apprend le biais seulement sur les jours déjà passés à l'heure de la capture.
Lignes écartées à la lecture des captures : {'no_cli_truth': 60}.
Fenêtre A2 reconstruite : 4948 contrats, 61 jours.
Dont avec correction ville honnête : 4876 contrats, 61 jours.
HOLDOUT seulement (correction figée + poids appris) : 1016 contrats, 13 jours.

### Contre le prix, fenêtre A2 (NBM + prix, comme A2)

| groupe | n bins | n dates | Brier NBM | Brier mélange brut | Brier marché |
|---|---|---|---|---|---|
| all | 4948 | 61 | 0.1351 | 0.1443 | 0.1249 |

### Contre le prix, jours avec NBM + correction ville honnête

| groupe | n bins | n dates | Brier moyenne | Brier correction ville | Brier NBM | Brier mélange brut | Brier marché |
|---|---|---|---|---|---|---|---|
| all | 4876 | 61 | 0.1314 | 0.1357 | 0.1351 | 0.1443 | 0.1251 |

### Contre le prix, HOLDOUT seulement (poids appris, correction figée)

| groupe | n bins | n dates | Brier moyenne | Brier ajusté | Brier correction ville | Brier NBM | Brier marché |
|---|---|---|---|---|---|---|---|
| all | 1016 | 13 | 0.1319 | 0.1344 | 0.1390 | 0.1340 | 0.1204 |

### Victoires jour par jour

| comparaison | jours | victoires du premier | chance que ce soit le hasard |
|---|---|---|---|
| avg_vs_station | 36 | 22 | 0.1215 |
| avg_vs_nbm | 36 | 35 | 0.0000 |
| avg_vs_raw | 36 | 34 | 0.0000 |
| nbm_vs_station | 36 | 5 | 1.0000 |
| station_vs_raw | 36 | 34 | 0.0000 |
| fit_vs_station | 36 | 31 | 0.0000 |
| fit_vs_nbm | 36 | 35 | 0.0000 |
| fit_vs_avg | 36 | 22 | 0.1215 |
| avg_vs_market_a2 | 61 | 15 | 1.0000 |
| avg_vs_station_a2 | 61 | 45 | 0.0001 |
| avg_vs_nbm_a2 | 61 | 41 | 0.0049 |
| nbm_vs_market_a2 | 61 | 14 | 1.0000 |
| station_vs_market_a2 | 61 | 12 | 1.0000 |
| nbm_vs_market_a2_all | 61 | 14 | 1.0000 |
| avg_vs_market_hold | 13 | 1 | 0.9999 |
| station_vs_market_hold | 13 | 1 | 0.9999 |
| fit_vs_market_hold | 13 | 1 | 0.9999 |
| fit_vs_station_hold | 13 | 13 | 0.0001 |

Décision : on ne change pas le modèle en ligne. Le mélange (moyenne) bat la correction ville sur 61 jours, mais pas le marché. On ne promeut pas.

Le modèle en ligne n'est pas changé. Le site public n'est pas changé. Pas de pari avec de l'argent réel.

