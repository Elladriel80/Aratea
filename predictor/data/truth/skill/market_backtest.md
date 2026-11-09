# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-11-09T14:58:34Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 112}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 18261 | 123 | 0.198 | 0.1527 | 0.1380 | 0.0861 | +0.0519 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 9313 | 114 | 0.198 | 0.1512 | 0.1360 | 0.0482 | +0.0878 |
| 1 | 8948 | 113 | 0.197 | 0.1543 | 0.1401 | 0.1256 | +0.0145 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 3808 | 23 | 0.208 | 0.1595 | 0.1444 | 0.0848 | +0.0596 |
| 2026-10 | 4256 | 31 | 0.202 | 0.1643 | 0.1411 | 0.0769 | +0.0642 |
| 2026-11 | 784 | 7 | 0.226 | 0.1903 | 0.1562 | 0.0889 | +0.0673 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 908 | 123 | 0.224 | 0.1698 | 0.1630 | 0.1027 | +0.0602 |
| KATL/temp_min | 876 | 121 | 0.208 | 0.1488 | 0.1355 | 0.0821 | +0.0534 |
| KAUS/temp_min | 868 | 121 | 0.218 | 0.1861 | 0.1656 | 0.0818 | +0.0838 |
| KBOS/temp_max | 908 | 123 | 0.192 | 0.1721 | 0.1424 | 0.0742 | +0.0682 |
| KBOS/temp_min | 868 | 121 | 0.122 | 0.0877 | 0.0883 | 0.0567 | +0.0317 |
| KDCA/temp_min | 868 | 121 | 0.162 | 0.1005 | 0.1032 | 0.0661 | +0.0371 |
| KDEN/temp_min | 580 | 109 | 0.202 | 0.1894 | 0.1492 | 0.0737 | +0.0756 |
| KDFW/temp_max | 908 | 123 | 0.216 | 0.1780 | 0.1649 | 0.0933 | +0.0716 |
| KDFW/temp_min | 868 | 121 | 0.198 | 0.1299 | 0.1316 | 0.0706 | +0.0610 |
| KHOU/temp_max | 901 | 123 | 0.219 | 0.1635 | 0.1593 | 0.0887 | +0.0706 |
| KHOU/temp_min | 376 | 73 | 0.237 | 0.1481 | 0.1478 | 0.0888 | +0.0590 |
| KLAS/temp_max | 900 | 123 | 0.230 | 0.2100 | 0.1214 | 0.0942 | +0.0273 |
| KLAS/temp_min | 368 | 72 | 0.095 | 0.0849 | 0.0808 | 0.0360 | +0.0448 |
| KLAX/temp_min | 372 | 72 | 0.167 | 0.1021 | 0.1011 | 0.0497 | +0.0514 |
| KMDW/temp_min | 868 | 121 | 0.184 | 0.1277 | 0.1274 | 0.0775 | +0.0499 |
| KMIA/temp_min | 360 | 71 | 0.200 | 0.1427 | 0.1361 | 0.0863 | +0.0498 |
| KMSP/temp_max | 900 | 123 | 0.208 | 0.1668 | 0.1561 | 0.1016 | +0.0545 |
| KMSP/temp_min | 328 | 66 | 0.155 | 0.1097 | 0.1106 | 0.0582 | +0.0524 |
| KNYC/temp_min | 320 | 66 | 0.231 | 0.1659 | 0.1567 | 0.1130 | +0.0437 |
| KPHL/temp_min | 288 | 60 | 0.108 | 0.0729 | 0.0659 | 0.0575 | +0.0084 |
| KPHX/temp_max | 892 | 122 | 0.228 | 0.2044 | 0.1531 | 0.1118 | +0.0412 |
| KPHX/temp_min | 264 | 56 | 0.110 | 0.0829 | 0.0809 | 0.0632 | +0.0177 |
| KSAT/temp_max | 900 | 123 | 0.220 | 0.1730 | 0.1640 | 0.0995 | +0.0645 |
| KSAT/temp_min | 268 | 57 | 0.194 | 0.1134 | 0.1337 | 0.0528 | +0.0809 |
| KSEA/temp_max | 900 | 123 | 0.214 | 0.1724 | 0.1528 | 0.1249 | +0.0279 |
| KSEA/temp_min | 268 | 57 | 0.220 | 0.1250 | 0.1233 | 0.0892 | +0.0341 |
| KSFO/temp_max | 876 | 121 | 0.200 | 0.1615 | 0.1554 | 0.1229 | +0.0325 |
| KSFO/temp_min | 260 | 57 | 0.231 | 0.1314 | 0.1333 | 0.0717 | +0.0616 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 4416 | 56 | 0.1628 | 0.1425 | 0.1556 | 0.0384 |
| 1 | 4208 | 55 | 0.1668 | 0.1458 | 0.1553 | 0.1265 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 123 | 104 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 123 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 123 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 60 | 16 | 0.9999 |
| members_vs_market (p_members < p_mkt) | 60 | 0 | 1.0000 |
