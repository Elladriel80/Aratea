# Une seule courbe (piste A5) / Single predictive curve

Généré / generated : 2026-09-12T17:56:40Z.
Split TRAIN < 2026-08-03, HOLDOUT skill 2026-08-03 → 2026-09-07.
H1 = N(mu + biais ville, sigma résiduel), une gaussienne, découpe des cases.
H2 = mélange équipondéré des vendeurs déjà capturés, même biais, même sigma, puis découpe.
Champion rejoué = H1 mélangé à la fréquence climat par bin (formule live, tau = 8 j).
Hors marché le mélange climat n'existe pas : champion = H1.
Vérité : rapport officiel CLI. Aucun chiffre inventé. Champion en ligne inchangé.
Skips marché : {'no_bias_yet': 228, 'no_cli_truth': 96}.

### Skill hors marché (HOLDOUT A1, bins synthétiques centraux)

| groupe | n contrats | n dates | Brier champion (= H1 hors marché) | Brier H1 gauss | Brier H2 mélange |
|---|---|---|---|---|---|
| all | 53928 | 36 | 0.1154 | 0.1154 | 0.1194 |

### Skill par lead

| lead | n contrats | n dates | Brier champion (= H1 hors marché) | Brier H1 gauss | Brier H2 mélange |
|---|---|---|---|---|---|
| 1 | 7704 | 36 | 0.1126 | 0.1126 | 0.1183 |
| 2 | 7704 | 36 | 0.1150 | 0.1150 | 0.1196 |
| 3 | 7704 | 36 | 0.1143 | 0.1143 | 0.1183 |
| 4 | 7704 | 36 | 0.1161 | 0.1161 | 0.1196 |
| 5 | 7704 | 36 | 0.1160 | 0.1160 | 0.1198 |
| 6 | 7704 | 36 | 0.1166 | 0.1166 | 0.1202 |
| 7 | 7704 | 36 | 0.1171 | 0.1171 | 0.1201 |

### Skill par variable

| variable | n contrats | n dates | Brier champion (= H1 hors marché) | Brier H1 gauss | Brier H2 mélange |
|---|---|---|---|---|---|
| temp_max | 26964 | 36 | 0.1120 | 0.1120 | 0.1170 |
| temp_min | 26964 | 36 | 0.1188 | 0.1188 | 0.1218 |

### Sign-test par date (Brier plus petit = gagne)

| comparaison | dates | jours gagnés par a | p unilatéral |
|---|---|---|---|
| h2_vs_h1 (p_h2 < p_h1) | 36 | 4 | 1.0000 |
| h1_vs_champion (p_h1 < p_champion) | 0 | 0 | n/a |

### Marché, cases centrales cotées (J0 et J-1)

| groupe | n contrats | n dates | Brier champion | Brier H1 gauss | Brier H2 mélange | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| all | 9973 | 67 | 0.1336 | 0.1335 | 0.1383 | 0.0907 |

### Marché par lead (0 = jour même, 1 = veille)

| lead | n contrats | n dates | Brier champion | Brier H1 gauss | Brier H2 mélange | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 5097 | 61 | 0.1314 | 0.1314 | 0.1363 | 0.0578 |
| 1 | 4876 | 61 | 0.1359 | 0.1357 | 0.1404 | 0.1251 |

### Marché par variable

| variable | n contrats | n dates | Brier champion | Brier H1 gauss | Brier H2 mélange | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| temp_max | 4789 | 67 | 0.1555 | 0.1560 | 0.1596 | 0.1165 |
| temp_min | 5184 | 67 | 0.1134 | 0.1127 | 0.1186 | 0.0668 |

### Sign-test par date (Brier plus petit = gagne)

| comparaison | dates | jours gagnés par a | p unilatéral |
|---|---|---|---|
| h1_vs_champion (p_h1 < p_champion) | 61 | 32 | 0.3991 |
| h2_vs_champion (p_h2 < p_champion) | 67 | 15 | 1.0000 |
| h2_vs_h1 (p_h2 < p_h1) | 67 | 15 | 1.0000 |
| h1_vs_mid (p_h1 < p_mid) | 67 | 2 | 1.0000 |
| h2_vs_mid (p_h2 < p_mid) | 67 | 2 | 1.0000 |
| champion_vs_mid (p_champion < p_mid) | 67 | 2 | 1.0000 |

### Sign-test marché par lead

Lead 0

### Sign-test par date (Brier plus petit = gagne)

| comparaison | dates | jours gagnés par a | p unilatéral |
|---|---|---|---|
| h1_vs_champion (p_h1 < p_champion) | 0 | 0 | n/a |
| h2_vs_champion (p_h2 < p_champion) | 61 | 16 | 1.0000 |
| h2_vs_h1 (p_h2 < p_h1) | 61 | 16 | 1.0000 |
| h1_vs_mid (p_h1 < p_mid) | 61 | 0 | 1.0000 |
| h2_vs_mid (p_h2 < p_mid) | 61 | 0 | 1.0000 |
| champion_vs_mid (p_champion < p_mid) | 61 | 0 | 1.0000 |

Lead 1

### Sign-test par date (Brier plus petit = gagne)

| comparaison | dates | jours gagnés par a | p unilatéral |
|---|---|---|---|
| h1_vs_champion (p_h1 < p_champion) | 61 | 32 | 0.3991 |
| h2_vs_champion (p_h2 < p_champion) | 61 | 18 | 0.9996 |
| h2_vs_h1 (p_h2 < p_h1) | 61 | 17 | 0.9999 |
| h1_vs_mid (p_h1 < p_mid) | 61 | 12 | 1.0000 |
| h2_vs_mid (p_h2 < p_mid) | 61 | 9 | 1.0000 |
| champion_vs_mid (p_champion < p_mid) | 61 | 13 | 1.0000 |

### Cohérence (somme des P sur les cases listées du même événement)

Événements (ville-jour-lead) : 2494. Avec les deux queues listées : 2493.

| série | n | somme moyenne | min | max | |somme−1| > 0,05 | |somme−1| > 0,20 |
|---|---|---|---|---|---|---|
| champion rejoué | 2494 | 1.0243 | 0.0060 | 1.2350 | 264 | 250 |
| H1 gauss | 2494 | 0.9996 | 0.0060 | 1.0000 | 1 | 1 |
| H2 mélange | 2494 | 0.9996 | 0.0730 | 1.0000 | 1 | 1 |
| kalshi_mid | 2494 | 1.0171 | 0.0100 | 1.3850 | 590 | 8 |

### Cohérence lead 0

Événements (ville-jour-lead) : 1275. Avec les deux queues listées : 1274.

| série | n | somme moyenne | min | max | |somme−1| > 0,05 | |somme−1| > 0,20 |
|---|---|---|---|---|---|---|
| champion rejoué | 1275 | 0.9992 | 0.0060 | 1.0000 | 1 | 1 |
| H1 gauss | 1275 | 0.9992 | 0.0060 | 1.0000 | 1 | 1 |
| H2 mélange | 1275 | 0.9993 | 0.0730 | 1.0000 | 1 | 1 |
| kalshi_mid | 1275 | 1.0166 | 0.0100 | 1.3450 | 238 | 4 |

### Cohérence lead 1

Événements (ville-jour-lead) : 1219. Avec les deux queues listées : 1219.

| série | n | somme moyenne | min | max | |somme−1| > 0,05 | |somme−1| > 0,20 |
|---|---|---|---|---|---|---|
| champion rejoué | 1219 | 1.0505 | 1.0014 | 1.2350 | 263 | 249 |
| H1 gauss | 1219 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 |
| H2 mélange | 1219 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 |
| kalshi_mid | 1219 | 1.0175 | 0.8700 | 1.3850 | 352 | 4 |

