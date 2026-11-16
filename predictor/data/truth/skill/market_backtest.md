# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-11-16T14:35:33Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 56}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 18717 | 130 | 0.198 | 0.1534 | 0.1384 | 0.0857 | +0.0527 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 9513 | 118 | 0.199 | 0.1523 | 0.1366 | 0.0476 | +0.0890 |
| 1 | 9204 | 117 | 0.197 | 0.1544 | 0.1403 | 0.1251 | +0.0152 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 3808 | 23 | 0.208 | 0.1595 | 0.1444 | 0.0848 | +0.0596 |
| 2026-10 | 4256 | 31 | 0.202 | 0.1643 | 0.1411 | 0.0769 | +0.0642 |
| 2026-11 | 1240 | 14 | 0.219 | 0.1869 | 0.1550 | 0.0814 | +0.0736 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 940 | 130 | 0.224 | 0.1702 | 0.1627 | 0.1010 | +0.0617 |
| KATL/temp_min | 888 | 124 | 0.208 | 0.1493 | 0.1358 | 0.0817 | +0.0541 |
| KAUS/temp_min | 880 | 124 | 0.216 | 0.1847 | 0.1642 | 0.0809 | +0.0833 |
| KBOS/temp_max | 940 | 130 | 0.194 | 0.1712 | 0.1436 | 0.0735 | +0.0701 |
| KBOS/temp_min | 880 | 124 | 0.122 | 0.0878 | 0.0882 | 0.0566 | +0.0316 |
| KDCA/temp_min | 880 | 124 | 0.164 | 0.1013 | 0.1031 | 0.0662 | +0.0369 |
| KDEN/temp_min | 592 | 112 | 0.201 | 0.1894 | 0.1492 | 0.0733 | +0.0759 |
| KDFW/temp_max | 940 | 130 | 0.217 | 0.1791 | 0.1656 | 0.0922 | +0.0734 |
| KDFW/temp_min | 880 | 124 | 0.198 | 0.1300 | 0.1316 | 0.0710 | +0.0605 |
| KHOU/temp_max | 933 | 130 | 0.218 | 0.1642 | 0.1592 | 0.0869 | +0.0723 |
| KHOU/temp_min | 388 | 76 | 0.237 | 0.1501 | 0.1499 | 0.0913 | +0.0586 |
| KLAS/temp_max | 932 | 130 | 0.231 | 0.2098 | 0.1224 | 0.0946 | +0.0278 |
| KLAS/temp_min | 380 | 75 | 0.100 | 0.0887 | 0.0854 | 0.0358 | +0.0497 |
| KLAX/temp_min | 384 | 75 | 0.167 | 0.1033 | 0.1036 | 0.0509 | +0.0528 |
| KMDW/temp_min | 880 | 124 | 0.185 | 0.1283 | 0.1279 | 0.0775 | +0.0505 |
| KMIA/temp_min | 372 | 74 | 0.196 | 0.1410 | 0.1350 | 0.0853 | +0.0496 |
| KMSP/temp_max | 932 | 130 | 0.207 | 0.1677 | 0.1557 | 0.0993 | +0.0564 |
| KMSP/temp_min | 340 | 69 | 0.156 | 0.1102 | 0.1111 | 0.0571 | +0.0540 |
| KNYC/temp_min | 332 | 69 | 0.229 | 0.1679 | 0.1586 | 0.1124 | +0.0461 |
| KPHL/temp_min | 288 | 60 | 0.108 | 0.0729 | 0.0659 | 0.0575 | +0.0084 |
| KPHX/temp_max | 924 | 129 | 0.226 | 0.2046 | 0.1515 | 0.1088 | +0.0427 |
| KPHX/temp_min | 264 | 56 | 0.110 | 0.0829 | 0.0809 | 0.0632 | +0.0177 |
| KSAT/temp_max | 932 | 130 | 0.219 | 0.1731 | 0.1628 | 0.0976 | +0.0652 |
| KSAT/temp_min | 268 | 57 | 0.194 | 0.1134 | 0.1337 | 0.0528 | +0.0809 |
| KSEA/temp_max | 932 | 130 | 0.216 | 0.1753 | 0.1547 | 0.1275 | +0.0272 |
| KSEA/temp_min | 268 | 57 | 0.220 | 0.1250 | 0.1233 | 0.0892 | +0.0341 |
| KSFO/temp_max | 888 | 124 | 0.199 | 0.1613 | 0.1554 | 0.1225 | +0.0329 |
| KSFO/temp_min | 260 | 57 | 0.231 | 0.1314 | 0.1333 | 0.0717 | +0.0616 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 4616 | 60 | 0.1648 | 0.1434 | 0.1571 | 0.0376 |
| 1 | 4464 | 59 | 0.1665 | 0.1458 | 0.1553 | 0.1254 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 130 | 111 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 130 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 130 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 67 | 17 | 1.0000 |
| members_vs_market (p_members < p_mkt) | 67 | 0 | 1.0000 |
