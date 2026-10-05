# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-10-05T13:23:47Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 132}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 14021 | 89 | 0.195 | 0.1466 | 0.1360 | 0.0883 | +0.0476 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 7173 | 84 | 0.196 | 0.1454 | 0.1337 | 0.0521 | +0.0816 |
| 1 | 6848 | 83 | 0.195 | 0.1479 | 0.1384 | 0.1263 | +0.0121 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 3808 | 23 | 0.208 | 0.1595 | 0.1444 | 0.0848 | +0.0596 |
| 2026-10 | 800 | 4 | 0.200 | 0.1459 | 0.1362 | 0.0780 | +0.0582 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 668 | 89 | 0.226 | 0.1759 | 0.1696 | 0.1166 | +0.0530 |
| KATL/temp_min | 660 | 89 | 0.209 | 0.1478 | 0.1294 | 0.0817 | +0.0476 |
| KAUS/temp_min | 660 | 89 | 0.229 | 0.1842 | 0.1673 | 0.0771 | +0.0902 |
| KBOS/temp_max | 668 | 89 | 0.181 | 0.1659 | 0.1393 | 0.0751 | +0.0642 |
| KBOS/temp_min | 660 | 89 | 0.100 | 0.0729 | 0.0767 | 0.0516 | +0.0251 |
| KDCA/temp_min | 660 | 89 | 0.162 | 0.0981 | 0.1007 | 0.0680 | +0.0327 |
| KDEN/temp_min | 448 | 81 | 0.201 | 0.1880 | 0.1473 | 0.0721 | +0.0751 |
| KDFW/temp_max | 668 | 89 | 0.213 | 0.1621 | 0.1670 | 0.1070 | +0.0600 |
| KDFW/temp_min | 660 | 89 | 0.205 | 0.1236 | 0.1299 | 0.0687 | +0.0613 |
| KHOU/temp_max | 661 | 89 | 0.213 | 0.1521 | 0.1621 | 0.0961 | +0.0659 |
| KHOU/temp_min | 312 | 58 | 0.240 | 0.1453 | 0.1469 | 0.0879 | +0.0590 |
| KLAS/temp_max | 660 | 89 | 0.235 | 0.2158 | 0.1254 | 0.0971 | +0.0283 |
| KLAS/temp_min | 304 | 57 | 0.079 | 0.0747 | 0.0694 | 0.0320 | +0.0374 |
| KLAX/temp_min | 308 | 57 | 0.156 | 0.0885 | 0.0879 | 0.0419 | +0.0460 |
| KMDW/temp_min | 660 | 89 | 0.183 | 0.1249 | 0.1291 | 0.0830 | +0.0462 |
| KMIA/temp_min | 296 | 56 | 0.203 | 0.1446 | 0.1360 | 0.0916 | +0.0444 |
| KMSP/temp_max | 660 | 89 | 0.205 | 0.1549 | 0.1526 | 0.1125 | +0.0401 |
| KMSP/temp_min | 288 | 56 | 0.149 | 0.1078 | 0.1068 | 0.0583 | +0.0484 |
| KNYC/temp_min | 280 | 56 | 0.229 | 0.1607 | 0.1519 | 0.1012 | +0.0507 |
| KPHL/temp_min | 260 | 53 | 0.112 | 0.0735 | 0.0683 | 0.0574 | +0.0109 |
| KPHX/temp_max | 652 | 88 | 0.225 | 0.2039 | 0.1511 | 0.1195 | +0.0316 |
| KPHX/temp_min | 236 | 49 | 0.106 | 0.0830 | 0.0805 | 0.0593 | +0.0212 |
| KSAT/temp_max | 660 | 89 | 0.220 | 0.1645 | 0.1721 | 0.1149 | +0.0572 |
| KSAT/temp_min | 240 | 50 | 0.192 | 0.1098 | 0.1298 | 0.0494 | +0.0803 |
| KSEA/temp_max | 660 | 89 | 0.215 | 0.1675 | 0.1557 | 0.1318 | +0.0239 |
| KSEA/temp_min | 240 | 50 | 0.221 | 0.1230 | 0.1231 | 0.0860 | +0.0372 |
| KSFO/temp_max | 660 | 89 | 0.195 | 0.1579 | 0.1506 | 0.1226 | +0.0280 |
| KSFO/temp_min | 232 | 50 | 0.228 | 0.1259 | 0.1250 | 0.0678 | +0.0572 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 2276 | 26 | 0.1557 | 0.1413 | 0.1513 | 0.0414 |
| 1 | 2108 | 25 | 0.1588 | 0.1458 | 0.1523 | 0.1297 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 89 | 72 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 89 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 89 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 26 | 9 | 0.9622 |
| members_vs_market (p_members < p_mkt) | 26 | 0 | 1.0000 |
