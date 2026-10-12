# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-10-12T14:14:08Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 84}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 15073 | 96 | 0.195 | 0.1483 | 0.1362 | 0.0875 | +0.0487 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 7681 | 91 | 0.196 | 0.1471 | 0.1340 | 0.0508 | +0.0832 |
| 1 | 7392 | 90 | 0.195 | 0.1496 | 0.1385 | 0.1255 | +0.0130 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 3808 | 23 | 0.208 | 0.1595 | 0.1444 | 0.0848 | +0.0596 |
| 2026-10 | 1852 | 11 | 0.198 | 0.1600 | 0.1378 | 0.0766 | +0.0612 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 724 | 96 | 0.217 | 0.1687 | 0.1635 | 0.1099 | +0.0535 |
| KATL/temp_min | 716 | 96 | 0.212 | 0.1498 | 0.1320 | 0.0849 | +0.0471 |
| KAUS/temp_min | 708 | 96 | 0.222 | 0.1818 | 0.1644 | 0.0806 | +0.0837 |
| KBOS/temp_max | 724 | 96 | 0.186 | 0.1678 | 0.1408 | 0.0746 | +0.0662 |
| KBOS/temp_min | 708 | 96 | 0.105 | 0.0752 | 0.0783 | 0.0525 | +0.0258 |
| KDCA/temp_min | 708 | 96 | 0.161 | 0.0981 | 0.1013 | 0.0667 | +0.0346 |
| KDEN/temp_min | 480 | 87 | 0.200 | 0.1856 | 0.1475 | 0.0745 | +0.0729 |
| KDFW/temp_max | 724 | 96 | 0.213 | 0.1703 | 0.1683 | 0.1027 | +0.0657 |
| KDFW/temp_min | 708 | 96 | 0.205 | 0.1261 | 0.1306 | 0.0682 | +0.0624 |
| KHOU/temp_max | 717 | 96 | 0.213 | 0.1567 | 0.1609 | 0.0921 | +0.0688 |
| KHOU/temp_min | 332 | 62 | 0.238 | 0.1473 | 0.1484 | 0.0910 | +0.0574 |
| KLAS/temp_max | 716 | 96 | 0.236 | 0.2161 | 0.1246 | 0.0962 | +0.0284 |
| KLAS/temp_min | 324 | 61 | 0.086 | 0.0795 | 0.0742 | 0.0329 | +0.0413 |
| KLAX/temp_min | 328 | 61 | 0.162 | 0.0943 | 0.0923 | 0.0473 | +0.0449 |
| KMDW/temp_min | 708 | 96 | 0.181 | 0.1234 | 0.1271 | 0.0803 | +0.0468 |
| KMIA/temp_min | 316 | 60 | 0.199 | 0.1415 | 0.1338 | 0.0883 | +0.0455 |
| KMSP/temp_max | 716 | 96 | 0.208 | 0.1604 | 0.1548 | 0.1099 | +0.0449 |
| KMSP/temp_min | 300 | 59 | 0.153 | 0.1110 | 0.1101 | 0.0590 | +0.0511 |
| KNYC/temp_min | 292 | 59 | 0.229 | 0.1642 | 0.1538 | 0.1011 | +0.0526 |
| KPHL/temp_min | 272 | 56 | 0.110 | 0.0744 | 0.0679 | 0.0581 | +0.0098 |
| KPHX/temp_max | 708 | 95 | 0.227 | 0.2066 | 0.1531 | 0.1188 | +0.0343 |
| KPHX/temp_min | 248 | 52 | 0.109 | 0.0825 | 0.0812 | 0.0594 | +0.0218 |
| KSAT/temp_max | 716 | 96 | 0.222 | 0.1717 | 0.1703 | 0.1093 | +0.0610 |
| KSAT/temp_min | 252 | 53 | 0.194 | 0.1141 | 0.1348 | 0.0525 | +0.0824 |
| KSEA/temp_max | 716 | 96 | 0.212 | 0.1679 | 0.1527 | 0.1298 | +0.0229 |
| KSEA/temp_min | 252 | 53 | 0.218 | 0.1238 | 0.1214 | 0.0865 | +0.0350 |
| KSFO/temp_max | 716 | 96 | 0.189 | 0.1523 | 0.1463 | 0.1166 | +0.0297 |
| KSFO/temp_min | 244 | 53 | 0.230 | 0.1306 | 0.1340 | 0.0720 | +0.0620 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 2784 | 33 | 0.1584 | 0.1407 | 0.1512 | 0.0397 |
| 1 | 2652 | 32 | 0.1613 | 0.1446 | 0.1530 | 0.1269 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 96 | 79 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 96 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 96 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 33 | 10 | 0.9932 |
| members_vs_market (p_members < p_mkt) | 33 | 0 | 1.0000 |
