# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-09-21T11:48:06Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 72}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 11413 | 75 | 0.193 | 0.1446 | 0.1350 | 0.0902 | +0.0448 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 5829 | 70 | 0.194 | 0.1436 | 0.1329 | 0.0562 | +0.0767 |
| 1 | 5584 | 69 | 0.193 | 0.1456 | 0.1373 | 0.1257 | +0.0116 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 2000 | 13 | 0.212 | 0.1592 | 0.1467 | 0.0879 | +0.0588 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 556 | 75 | 0.232 | 0.1821 | 0.1736 | 0.1249 | +0.0487 |
| KATL/temp_min | 548 | 75 | 0.208 | 0.1483 | 0.1265 | 0.0827 | +0.0438 |
| KAUS/temp_min | 548 | 75 | 0.235 | 0.1812 | 0.1694 | 0.0805 | +0.0889 |
| KBOS/temp_max | 556 | 75 | 0.182 | 0.1648 | 0.1402 | 0.0787 | +0.0615 |
| KBOS/temp_min | 548 | 75 | 0.073 | 0.0491 | 0.0528 | 0.0371 | +0.0157 |
| KDCA/temp_min | 548 | 75 | 0.159 | 0.0951 | 0.0973 | 0.0670 | +0.0303 |
| KDEN/temp_min | 356 | 67 | 0.194 | 0.1889 | 0.1428 | 0.0667 | +0.0762 |
| KDFW/temp_max | 556 | 75 | 0.216 | 0.1629 | 0.1723 | 0.1137 | +0.0586 |
| KDFW/temp_min | 548 | 75 | 0.214 | 0.1252 | 0.1348 | 0.0689 | +0.0659 |
| KHOU/temp_max | 549 | 75 | 0.209 | 0.1455 | 0.1671 | 0.1008 | +0.0663 |
| KHOU/temp_min | 236 | 46 | 0.237 | 0.1437 | 0.1473 | 0.0896 | +0.0577 |
| KLAS/temp_max | 548 | 75 | 0.235 | 0.2187 | 0.1258 | 0.0992 | +0.0266 |
| KLAS/temp_min | 228 | 45 | 0.044 | 0.0519 | 0.0365 | 0.0121 | +0.0244 |
| KLAX/temp_min | 232 | 45 | 0.134 | 0.0713 | 0.0735 | 0.0332 | +0.0403 |
| KMDW/temp_min | 548 | 75 | 0.181 | 0.1199 | 0.1279 | 0.0835 | +0.0444 |
| KMIA/temp_min | 220 | 44 | 0.214 | 0.1519 | 0.1409 | 0.0914 | +0.0495 |
| KMSP/temp_max | 548 | 75 | 0.199 | 0.1462 | 0.1486 | 0.1136 | +0.0350 |
| KMSP/temp_min | 220 | 44 | 0.159 | 0.1157 | 0.1100 | 0.0615 | +0.0485 |
| KNYC/temp_min | 212 | 44 | 0.222 | 0.1663 | 0.1465 | 0.1049 | +0.0416 |
| KPHL/temp_min | 196 | 42 | 0.087 | 0.0719 | 0.0607 | 0.0521 | +0.0086 |
| KPHX/temp_max | 548 | 75 | 0.228 | 0.2028 | 0.1541 | 0.1306 | +0.0235 |
| KPHX/temp_min | 180 | 39 | 0.117 | 0.0926 | 0.0881 | 0.0710 | +0.0170 |
| KSAT/temp_max | 548 | 75 | 0.221 | 0.1644 | 0.1742 | 0.1230 | +0.0512 |
| KSAT/temp_min | 180 | 39 | 0.200 | 0.1049 | 0.1339 | 0.0482 | +0.0857 |
| KSEA/temp_max | 548 | 75 | 0.212 | 0.1640 | 0.1565 | 0.1368 | +0.0196 |
| KSEA/temp_min | 180 | 39 | 0.222 | 0.1204 | 0.1197 | 0.0822 | +0.0376 |
| KSFO/temp_max | 548 | 75 | 0.195 | 0.1578 | 0.1506 | 0.1244 | +0.0262 |
| KSFO/temp_min | 180 | 39 | 0.228 | 0.1141 | 0.1200 | 0.0624 | +0.0576 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 932 | 12 | 0.1594 | 0.1474 | 0.1564 | 0.0516 |
| 1 | 844 | 11 | 0.1597 | 0.1495 | 0.1553 | 0.1305 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 75 | 59 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 75 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 75 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 12 | 5 | 0.8062 |
| members_vs_market (p_members < p_mkt) | 12 | 0 | 1.0000 |
