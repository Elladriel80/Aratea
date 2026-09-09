# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-09-09T07:16:17Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 1032}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 8613 | 63 | 0.192 | 0.1458 | 0.1309 | 0.1019 | +0.0291 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 4437 | 58 | 0.193 | 0.1453 | 0.1294 | 0.0771 | +0.0524 |
| 1 | 4176 | 57 | 0.190 | 0.1463 | 0.1325 | 0.1282 | +0.0043 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 2868 | 20 | 0.181 | 0.1362 | 0.1252 | 0.0935 | +0.0317 |
| 2026-07 | 4044 | 31 | 0.201 | 0.1534 | 0.1374 | 0.1086 | +0.0288 |
| 2026-08 | 1597 | 11 | 0.188 | 0.1426 | 0.1247 | 0.1035 | +0.0212 |
| 2026-09 | 104 | 1 | 0.192 | 0.1642 | 0.1314 | 0.0463 | +0.0851 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 460 | 63 | 0.233 | 0.1914 | 0.1713 | 0.1275 | +0.0438 |
| KATL/temp_min | 452 | 63 | 0.199 | 0.1469 | 0.1230 | 0.0797 | +0.0433 |
| KAUS/temp_min | 452 | 63 | 0.232 | 0.1671 | 0.1690 | 0.0812 | +0.0878 |
| KBOS/temp_max | 460 | 63 | 0.172 | 0.1580 | 0.1342 | 0.0770 | +0.0572 |
| KBOS/temp_min | 452 | 63 | 0.040 | 0.0374 | 0.0334 | 0.0250 | +0.0084 |
| KDCA/temp_min | 452 | 63 | 0.166 | 0.0956 | 0.0995 | 0.0713 | +0.0282 |
| KDEN/temp_min | 296 | 57 | 0.186 | 0.1806 | 0.1368 | 0.0585 | +0.0783 |
| KIAH/temp_max | 453 | 63 | 0.230 | 0.1632 | 0.1442 | 0.1731 | -0.0289 |
| KIAH/temp_min | 200 | 39 | 0.240 | 0.1668 | 0.1663 | 0.2322 | -0.0659 |
| KLAS/temp_max | 452 | 63 | 0.232 | 0.2189 | 0.1190 | 0.0943 | +0.0247 |
| KLAS/temp_min | 200 | 39 | 0.025 | 0.0404 | 0.0238 | 0.0067 | +0.0171 |
| KLAX/temp_min | 196 | 38 | 0.148 | 0.0767 | 0.0742 | 0.0363 | +0.0378 |
| KMIA/temp_min | 192 | 38 | 0.208 | 0.1494 | 0.1415 | 0.0921 | +0.0494 |
| KMSP/temp_max | 452 | 63 | 0.201 | 0.1493 | 0.1519 | 0.1230 | +0.0289 |
| KMSP/temp_min | 192 | 38 | 0.146 | 0.1105 | 0.1043 | 0.0542 | +0.0501 |
| KNYC/temp_min | 184 | 38 | 0.217 | 0.1610 | 0.1400 | 0.1045 | +0.0356 |
| KORD/temp_min | 452 | 63 | 0.226 | 0.1516 | 0.1534 | 0.1698 | -0.0164 |
| KPHL/temp_min | 168 | 36 | 0.089 | 0.0757 | 0.0647 | 0.0561 | +0.0087 |
| KPHX/temp_max | 452 | 63 | 0.228 | 0.1970 | 0.1438 | 0.1310 | +0.0128 |
| KPHX/temp_min | 160 | 35 | 0.119 | 0.0852 | 0.0852 | 0.0720 | +0.0132 |
| KSAT/temp_max | 452 | 63 | 0.228 | 0.1669 | 0.1812 | 0.1289 | +0.0523 |
| KSAT/temp_min | 160 | 35 | 0.200 | 0.1030 | 0.1359 | 0.0448 | +0.0910 |
| KSEA/temp_max | 452 | 63 | 0.212 | 0.1672 | 0.1561 | 0.1416 | +0.0144 |
| KSEA/temp_min | 160 | 35 | 0.219 | 0.1252 | 0.1240 | 0.0879 | +0.0362 |
| KSFO/temp_max | 452 | 63 | 0.201 | 0.1628 | 0.1532 | 0.1328 | +0.0204 |
| KSFO/temp_min | 160 | 35 | 0.225 | 0.1121 | 0.1199 | 0.0653 | +0.0546 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 63 | 54 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 63 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 63 | 1 | 1.0000 |
