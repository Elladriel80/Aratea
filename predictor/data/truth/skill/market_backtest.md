# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-09-09T09:37:34Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 120}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 9525 | 63 | 0.190 | 0.1417 | 0.1325 | 0.0901 | +0.0424 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 4897 | 58 | 0.190 | 0.1406 | 0.1302 | 0.0571 | +0.0731 |
| 1 | 4628 | 57 | 0.189 | 0.1429 | 0.1349 | 0.1249 | +0.0100 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 112 | 1 | 0.188 | 0.1615 | 0.1259 | 0.0389 | +0.0870 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 460 | 63 | 0.233 | 0.1914 | 0.1713 | 0.1275 | +0.0438 |
| KATL/temp_min | 452 | 63 | 0.199 | 0.1469 | 0.1230 | 0.0797 | +0.0433 |
| KAUS/temp_min | 452 | 63 | 0.232 | 0.1671 | 0.1690 | 0.0812 | +0.0878 |
| KBOS/temp_max | 460 | 63 | 0.172 | 0.1580 | 0.1342 | 0.0770 | +0.0572 |
| KBOS/temp_min | 452 | 63 | 0.040 | 0.0374 | 0.0334 | 0.0250 | +0.0084 |
| KDCA/temp_min | 452 | 63 | 0.166 | 0.0956 | 0.0995 | 0.0713 | +0.0282 |
| KDEN/temp_min | 296 | 57 | 0.186 | 0.1818 | 0.1371 | 0.0635 | +0.0736 |
| KDFW/temp_max | 460 | 63 | 0.217 | 0.1635 | 0.1778 | 0.1137 | +0.0641 |
| KDFW/temp_min | 452 | 63 | 0.206 | 0.1241 | 0.1340 | 0.0694 | +0.0646 |
| KHOU/temp_max | 453 | 63 | 0.201 | 0.1353 | 0.1665 | 0.1008 | +0.0658 |
| KHOU/temp_min | 200 | 39 | 0.235 | 0.1399 | 0.1475 | 0.0878 | +0.0597 |
| KLAS/temp_max | 452 | 63 | 0.232 | 0.2189 | 0.1190 | 0.0943 | +0.0247 |
| KLAS/temp_min | 200 | 39 | 0.025 | 0.0404 | 0.0238 | 0.0067 | +0.0171 |
| KLAX/temp_min | 196 | 38 | 0.148 | 0.0767 | 0.0742 | 0.0363 | +0.0378 |
| KMDW/temp_min | 452 | 63 | 0.170 | 0.1094 | 0.1212 | 0.0747 | +0.0465 |
| KMIA/temp_min | 192 | 38 | 0.208 | 0.1494 | 0.1415 | 0.0921 | +0.0494 |
| KMSP/temp_max | 452 | 63 | 0.201 | 0.1493 | 0.1519 | 0.1230 | +0.0289 |
| KMSP/temp_min | 192 | 38 | 0.146 | 0.1105 | 0.1043 | 0.0542 | +0.0501 |
| KNYC/temp_min | 184 | 38 | 0.217 | 0.1610 | 0.1400 | 0.1045 | +0.0356 |
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
| station_vs_raw (p_station < p_raw) | 63 | 50 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 63 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 63 | 1 | 1.0000 |
