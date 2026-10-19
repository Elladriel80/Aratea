# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-10-19T11:54:25Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 20}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 15833 | 103 | 0.196 | 0.1492 | 0.1369 | 0.0874 | +0.0495 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 8037 | 96 | 0.196 | 0.1478 | 0.1348 | 0.0507 | +0.0841 |
| 1 | 7796 | 96 | 0.196 | 0.1507 | 0.1391 | 0.1253 | +0.0138 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 3808 | 23 | 0.208 | 0.1595 | 0.1444 | 0.0848 | +0.0596 |
| 2026-10 | 2612 | 18 | 0.201 | 0.1620 | 0.1417 | 0.0797 | +0.0621 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 768 | 103 | 0.219 | 0.1671 | 0.1638 | 0.1069 | +0.0569 |
| KATL/temp_min | 760 | 103 | 0.213 | 0.1511 | 0.1343 | 0.0849 | +0.0494 |
| KAUS/temp_min | 752 | 103 | 0.219 | 0.1822 | 0.1635 | 0.0828 | +0.0807 |
| KBOS/temp_max | 768 | 103 | 0.190 | 0.1679 | 0.1425 | 0.0760 | +0.0664 |
| KBOS/temp_min | 752 | 103 | 0.105 | 0.0791 | 0.0801 | 0.0526 | +0.0275 |
| KDCA/temp_min | 752 | 103 | 0.162 | 0.0968 | 0.1010 | 0.0660 | +0.0350 |
| KDEN/temp_min | 504 | 92 | 0.202 | 0.1890 | 0.1487 | 0.0744 | +0.0744 |
| KDFW/temp_max | 768 | 103 | 0.212 | 0.1710 | 0.1676 | 0.0997 | +0.0678 |
| KDFW/temp_min | 752 | 103 | 0.202 | 0.1258 | 0.1295 | 0.0674 | +0.0621 |
| KHOU/temp_max | 761 | 103 | 0.216 | 0.1588 | 0.1599 | 0.0893 | +0.0706 |
| KHOU/temp_min | 340 | 64 | 0.238 | 0.1490 | 0.1503 | 0.0907 | +0.0596 |
| KLAS/temp_max | 760 | 103 | 0.234 | 0.2160 | 0.1245 | 0.0978 | +0.0267 |
| KLAS/temp_min | 332 | 63 | 0.084 | 0.0780 | 0.0728 | 0.0329 | +0.0400 |
| KLAX/temp_min | 336 | 63 | 0.164 | 0.0969 | 0.0967 | 0.0477 | +0.0490 |
| KMDW/temp_min | 752 | 103 | 0.182 | 0.1254 | 0.1275 | 0.0806 | +0.0470 |
| KMIA/temp_min | 324 | 62 | 0.201 | 0.1419 | 0.1346 | 0.0900 | +0.0445 |
| KMSP/temp_max | 760 | 103 | 0.203 | 0.1575 | 0.1508 | 0.1066 | +0.0443 |
| KMSP/temp_min | 300 | 59 | 0.153 | 0.1110 | 0.1101 | 0.0590 | +0.0511 |
| KNYC/temp_min | 292 | 59 | 0.229 | 0.1642 | 0.1538 | 0.1011 | +0.0526 |
| KPHL/temp_min | 272 | 56 | 0.110 | 0.0744 | 0.0679 | 0.0581 | +0.0098 |
| KPHX/temp_max | 752 | 102 | 0.229 | 0.2023 | 0.1562 | 0.1197 | +0.0365 |
| KPHX/temp_min | 248 | 52 | 0.109 | 0.0825 | 0.0812 | 0.0594 | +0.0218 |
| KSAT/temp_max | 760 | 103 | 0.222 | 0.1742 | 0.1711 | 0.1080 | +0.0632 |
| KSAT/temp_min | 252 | 53 | 0.194 | 0.1141 | 0.1348 | 0.0525 | +0.0824 |
| KSEA/temp_max | 760 | 103 | 0.214 | 0.1707 | 0.1543 | 0.1310 | +0.0233 |
| KSEA/temp_min | 252 | 53 | 0.218 | 0.1238 | 0.1214 | 0.0865 | +0.0350 |
| KSFO/temp_max | 760 | 103 | 0.192 | 0.1551 | 0.1494 | 0.1190 | +0.0304 |
| KSFO/temp_min | 244 | 53 | 0.230 | 0.1306 | 0.1340 | 0.0720 | +0.0620 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 3140 | 38 | 0.1590 | 0.1419 | 0.1517 | 0.0407 |
| 1 | 3056 | 38 | 0.1624 | 0.1455 | 0.1529 | 0.1262 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 103 | 84 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 103 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 103 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 40 | 13 | 0.9917 |
| members_vs_market (p_members < p_mkt) | 40 | 0 | 1.0000 |
