# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-11-23T17:09:20Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 56}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 19026 | 135 | 0.198 | 0.1532 | 0.1385 | 0.0854 | +0.0530 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 9669 | 121 | 0.199 | 0.1521 | 0.1365 | 0.0473 | +0.0893 |
| 1 | 9357 | 121 | 0.197 | 0.1544 | 0.1404 | 0.1248 | +0.0156 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 3808 | 23 | 0.208 | 0.1595 | 0.1444 | 0.0848 | +0.0596 |
| 2026-10 | 4256 | 31 | 0.202 | 0.1643 | 0.1411 | 0.0769 | +0.0642 |
| 2026-11 | 1549 | 19 | 0.214 | 0.1784 | 0.1525 | 0.0785 | +0.0740 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 965 | 135 | 0.221 | 0.1668 | 0.1603 | 0.0996 | +0.0607 |
| KATL/temp_min | 896 | 126 | 0.209 | 0.1487 | 0.1354 | 0.0813 | +0.0541 |
| KAUS/temp_min | 888 | 126 | 0.216 | 0.1854 | 0.1646 | 0.0809 | +0.0838 |
| KBOS/temp_max | 964 | 135 | 0.193 | 0.1709 | 0.1428 | 0.0725 | +0.0703 |
| KBOS/temp_min | 888 | 126 | 0.123 | 0.0887 | 0.0887 | 0.0568 | +0.0319 |
| KDCA/temp_min | 888 | 126 | 0.164 | 0.1021 | 0.1034 | 0.0664 | +0.0369 |
| KDEN/temp_min | 600 | 114 | 0.198 | 0.1873 | 0.1478 | 0.0730 | +0.0748 |
| KDFW/temp_max | 964 | 135 | 0.217 | 0.1788 | 0.1654 | 0.0912 | +0.0742 |
| KDFW/temp_min | 888 | 126 | 0.197 | 0.1301 | 0.1314 | 0.0712 | +0.0602 |
| KHOU/temp_max | 957 | 135 | 0.216 | 0.1647 | 0.1584 | 0.0858 | +0.0726 |
| KHOU/temp_min | 396 | 78 | 0.237 | 0.1518 | 0.1522 | 0.0925 | +0.0596 |
| KLAS/temp_max | 956 | 135 | 0.230 | 0.2064 | 0.1244 | 0.0955 | +0.0289 |
| KLAS/temp_min | 388 | 77 | 0.101 | 0.0886 | 0.0853 | 0.0355 | +0.0499 |
| KLAX/temp_min | 392 | 77 | 0.168 | 0.1053 | 0.1067 | 0.0521 | +0.0546 |
| KMDW/temp_min | 888 | 126 | 0.186 | 0.1285 | 0.1280 | 0.0773 | +0.0507 |
| KMIA/temp_min | 380 | 76 | 0.197 | 0.1418 | 0.1362 | 0.0846 | +0.0516 |
| KMSP/temp_max | 956 | 135 | 0.208 | 0.1672 | 0.1560 | 0.0980 | +0.0581 |
| KMSP/temp_min | 348 | 71 | 0.158 | 0.1096 | 0.1113 | 0.0579 | +0.0534 |
| KNYC/temp_min | 340 | 71 | 0.226 | 0.1675 | 0.1589 | 0.1127 | +0.0462 |
| KPHL/temp_min | 292 | 61 | 0.110 | 0.0745 | 0.0673 | 0.0567 | +0.0106 |
| KPHX/temp_max | 940 | 132 | 0.227 | 0.2059 | 0.1512 | 0.1072 | +0.0440 |
| KPHX/temp_min | 264 | 56 | 0.110 | 0.0829 | 0.0809 | 0.0632 | +0.0177 |
| KSAT/temp_max | 948 | 133 | 0.218 | 0.1722 | 0.1619 | 0.0969 | +0.0650 |
| KSAT/temp_min | 268 | 57 | 0.194 | 0.1134 | 0.1337 | 0.0528 | +0.0809 |
| KSEA/temp_max | 948 | 133 | 0.216 | 0.1754 | 0.1546 | 0.1267 | +0.0279 |
| KSEA/temp_min | 268 | 57 | 0.220 | 0.1250 | 0.1233 | 0.0892 | +0.0341 |
| KSFO/temp_max | 896 | 126 | 0.200 | 0.1603 | 0.1555 | 0.1230 | +0.0325 |
| KSFO/temp_min | 260 | 57 | 0.231 | 0.1314 | 0.1333 | 0.0717 | +0.0616 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 4772 | 63 | 0.1638 | 0.1431 | 0.1571 | 0.0372 |
| 1 | 4617 | 63 | 0.1660 | 0.1459 | 0.1548 | 0.1249 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 135 | 113 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 135 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 135 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 72 | 20 | 1.0000 |
| members_vs_market (p_members < p_mkt) | 72 | 0 | 1.0000 |
