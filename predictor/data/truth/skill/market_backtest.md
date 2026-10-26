# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-10-26T12:08:49Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 84}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 16561 | 110 | 0.197 | 0.1505 | 0.1376 | 0.0869 | +0.0506 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 8445 | 102 | 0.197 | 0.1491 | 0.1356 | 0.0499 | +0.0856 |
| 1 | 8116 | 101 | 0.197 | 0.1520 | 0.1397 | 0.1254 | +0.0142 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 3808 | 23 | 0.208 | 0.1595 | 0.1444 | 0.0848 | +0.0596 |
| 2026-10 | 3340 | 25 | 0.205 | 0.1656 | 0.1439 | 0.0789 | +0.0650 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 812 | 110 | 0.220 | 0.1667 | 0.1636 | 0.1068 | +0.0568 |
| KATL/temp_min | 804 | 110 | 0.211 | 0.1500 | 0.1337 | 0.0825 | +0.0511 |
| KAUS/temp_min | 796 | 110 | 0.219 | 0.1845 | 0.1660 | 0.0811 | +0.0849 |
| KBOS/temp_max | 812 | 110 | 0.190 | 0.1668 | 0.1424 | 0.0767 | +0.0657 |
| KBOS/temp_min | 796 | 110 | 0.113 | 0.0831 | 0.0844 | 0.0534 | +0.0309 |
| KDCA/temp_min | 796 | 110 | 0.166 | 0.1006 | 0.1036 | 0.0663 | +0.0373 |
| KDEN/temp_min | 528 | 98 | 0.199 | 0.1872 | 0.1479 | 0.0735 | +0.0744 |
| KDFW/temp_max | 812 | 110 | 0.214 | 0.1757 | 0.1664 | 0.0964 | +0.0700 |
| KDFW/temp_min | 796 | 110 | 0.202 | 0.1278 | 0.1309 | 0.0664 | +0.0645 |
| KHOU/temp_max | 805 | 110 | 0.217 | 0.1596 | 0.1583 | 0.0871 | +0.0712 |
| KHOU/temp_min | 340 | 64 | 0.238 | 0.1490 | 0.1503 | 0.0907 | +0.0596 |
| KLAS/temp_max | 804 | 110 | 0.230 | 0.2108 | 0.1235 | 0.0973 | +0.0263 |
| KLAS/temp_min | 332 | 63 | 0.084 | 0.0780 | 0.0728 | 0.0329 | +0.0400 |
| KLAX/temp_min | 336 | 63 | 0.164 | 0.0969 | 0.0967 | 0.0477 | +0.0490 |
| KMDW/temp_min | 796 | 110 | 0.186 | 0.1285 | 0.1279 | 0.0795 | +0.0484 |
| KMIA/temp_min | 324 | 62 | 0.201 | 0.1419 | 0.1346 | 0.0900 | +0.0445 |
| KMSP/temp_max | 804 | 110 | 0.205 | 0.1611 | 0.1526 | 0.1045 | +0.0481 |
| KMSP/temp_min | 300 | 59 | 0.153 | 0.1110 | 0.1101 | 0.0590 | +0.0511 |
| KNYC/temp_min | 292 | 59 | 0.229 | 0.1642 | 0.1538 | 0.1011 | +0.0526 |
| KPHL/temp_min | 272 | 56 | 0.110 | 0.0744 | 0.0679 | 0.0581 | +0.0098 |
| KPHX/temp_max | 796 | 109 | 0.225 | 0.2016 | 0.1540 | 0.1156 | +0.0384 |
| KPHX/temp_min | 248 | 52 | 0.109 | 0.0825 | 0.0812 | 0.0594 | +0.0218 |
| KSAT/temp_max | 804 | 110 | 0.224 | 0.1762 | 0.1695 | 0.1041 | +0.0655 |
| KSAT/temp_min | 252 | 53 | 0.194 | 0.1141 | 0.1348 | 0.0525 | +0.0824 |
| KSEA/temp_max | 804 | 110 | 0.216 | 0.1720 | 0.1560 | 0.1317 | +0.0243 |
| KSEA/temp_min | 252 | 53 | 0.218 | 0.1238 | 0.1214 | 0.0865 | +0.0350 |
| KSFO/temp_max | 804 | 110 | 0.195 | 0.1566 | 0.1521 | 0.1243 | +0.0278 |
| KSFO/temp_min | 244 | 53 | 0.230 | 0.1306 | 0.1340 | 0.0720 | +0.0620 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 3548 | 44 | 0.1608 | 0.1430 | 0.1550 | 0.0400 |
| 1 | 3376 | 43 | 0.1644 | 0.1461 | 0.1548 | 0.1263 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 110 | 91 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 110 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 110 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 47 | 13 | 0.9995 |
| members_vs_market (p_members < p_mkt) | 47 | 0 | 1.0000 |
