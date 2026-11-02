# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-11-02T14:44:05Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 132}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 17657 | 117 | 0.197 | 0.1512 | 0.1373 | 0.0860 | +0.0513 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 9021 | 109 | 0.197 | 0.1498 | 0.1355 | 0.0486 | +0.0868 |
| 1 | 8636 | 108 | 0.196 | 0.1527 | 0.1393 | 0.1251 | +0.0142 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 3808 | 23 | 0.208 | 0.1595 | 0.1444 | 0.0848 | +0.0596 |
| 2026-10 | 4256 | 31 | 0.202 | 0.1643 | 0.1411 | 0.0769 | +0.0643 |
| 2026-11 | 180 | 1 | 0.200 | 0.1729 | 0.1483 | 0.0859 | +0.0624 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 868 | 117 | 0.222 | 0.1682 | 0.1624 | 0.1037 | +0.0587 |
| KATL/temp_min | 860 | 117 | 0.207 | 0.1477 | 0.1336 | 0.0803 | +0.0533 |
| KAUS/temp_min | 852 | 117 | 0.218 | 0.1857 | 0.1661 | 0.0815 | +0.0846 |
| KBOS/temp_max | 868 | 117 | 0.189 | 0.1707 | 0.1411 | 0.0746 | +0.0665 |
| KBOS/temp_min | 852 | 117 | 0.120 | 0.0862 | 0.0873 | 0.0555 | +0.0318 |
| KDCA/temp_min | 852 | 117 | 0.162 | 0.0998 | 0.1029 | 0.0653 | +0.0376 |
| KDEN/temp_min | 564 | 105 | 0.200 | 0.1874 | 0.1487 | 0.0738 | +0.0749 |
| KDFW/temp_max | 868 | 117 | 0.214 | 0.1754 | 0.1640 | 0.0935 | +0.0706 |
| KDFW/temp_min | 852 | 117 | 0.198 | 0.1290 | 0.1310 | 0.0676 | +0.0633 |
| KHOU/temp_max | 861 | 117 | 0.217 | 0.1601 | 0.1583 | 0.0870 | +0.0713 |
| KHOU/temp_min | 360 | 69 | 0.236 | 0.1474 | 0.1480 | 0.0876 | +0.0603 |
| KLAS/temp_max | 860 | 117 | 0.229 | 0.2090 | 0.1220 | 0.0966 | +0.0254 |
| KLAS/temp_min | 352 | 68 | 0.091 | 0.0818 | 0.0768 | 0.0366 | +0.0402 |
| KLAX/temp_min | 356 | 68 | 0.163 | 0.0977 | 0.0971 | 0.0482 | +0.0489 |
| KMDW/temp_min | 852 | 117 | 0.183 | 0.1274 | 0.1272 | 0.0779 | +0.0493 |
| KMIA/temp_min | 344 | 67 | 0.201 | 0.1416 | 0.1351 | 0.0863 | +0.0488 |
| KMSP/temp_max | 860 | 117 | 0.206 | 0.1642 | 0.1544 | 0.1025 | +0.0519 |
| KMSP/temp_min | 312 | 62 | 0.154 | 0.1094 | 0.1095 | 0.0577 | +0.0518 |
| KNYC/temp_min | 304 | 62 | 0.230 | 0.1658 | 0.1551 | 0.1094 | +0.0457 |
| KPHL/temp_min | 284 | 59 | 0.109 | 0.0738 | 0.0668 | 0.0583 | +0.0085 |
| KPHX/temp_max | 852 | 116 | 0.227 | 0.2018 | 0.1540 | 0.1145 | +0.0395 |
| KPHX/temp_min | 260 | 55 | 0.108 | 0.0817 | 0.0801 | 0.0626 | +0.0175 |
| KSAT/temp_max | 860 | 117 | 0.221 | 0.1736 | 0.1654 | 0.1013 | +0.0641 |
| KSAT/temp_min | 264 | 56 | 0.193 | 0.1118 | 0.1329 | 0.0502 | +0.0827 |
| KSEA/temp_max | 860 | 117 | 0.214 | 0.1729 | 0.1537 | 0.1273 | +0.0264 |
| KSEA/temp_min | 264 | 56 | 0.220 | 0.1237 | 0.1208 | 0.0868 | +0.0340 |
| KSFO/temp_max | 860 | 117 | 0.199 | 0.1617 | 0.1553 | 0.1228 | +0.0324 |
| KSFO/temp_min | 256 | 56 | 0.230 | 0.1313 | 0.1337 | 0.0718 | +0.0619 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 4124 | 51 | 0.1608 | 0.1418 | 0.1550 | 0.0386 |
| 1 | 3896 | 50 | 0.1643 | 0.1443 | 0.1541 | 0.1254 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 117 | 98 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 117 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 117 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 54 | 14 | 0.9999 |
| members_vs_market (p_members < p_mkt) | 54 | 0 | 1.0000 |
