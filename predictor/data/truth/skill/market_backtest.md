# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-09-28T12:43:21Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 112}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 12625 | 82 | 0.195 | 0.1465 | 0.1356 | 0.0893 | +0.0463 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 6461 | 77 | 0.195 | 0.1455 | 0.1336 | 0.0544 | +0.0793 |
| 1 | 6164 | 76 | 0.194 | 0.1477 | 0.1377 | 0.1259 | +0.0118 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 3212 | 20 | 0.210 | 0.1613 | 0.1446 | 0.0853 | +0.0593 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 612 | 82 | 0.227 | 0.1763 | 0.1702 | 0.1198 | +0.0504 |
| KATL/temp_min | 604 | 82 | 0.209 | 0.1487 | 0.1281 | 0.0817 | +0.0464 |
| KAUS/temp_min | 604 | 82 | 0.237 | 0.1912 | 0.1724 | 0.0800 | +0.0924 |
| KBOS/temp_max | 612 | 82 | 0.185 | 0.1680 | 0.1413 | 0.0784 | +0.0629 |
| KBOS/temp_min | 604 | 82 | 0.086 | 0.0703 | 0.0706 | 0.0474 | +0.0232 |
| KDCA/temp_min | 604 | 82 | 0.161 | 0.0972 | 0.0990 | 0.0695 | +0.0295 |
| KDEN/temp_min | 396 | 74 | 0.199 | 0.1900 | 0.1460 | 0.0652 | +0.0808 |
| KDFW/temp_max | 612 | 82 | 0.212 | 0.1626 | 0.1703 | 0.1101 | +0.0602 |
| KDFW/temp_min | 604 | 82 | 0.214 | 0.1254 | 0.1323 | 0.0682 | +0.0641 |
| KHOU/temp_max | 605 | 82 | 0.213 | 0.1482 | 0.1647 | 0.0986 | +0.0661 |
| KHOU/temp_min | 264 | 51 | 0.239 | 0.1448 | 0.1480 | 0.0875 | +0.0605 |
| KLAS/temp_max | 604 | 82 | 0.237 | 0.2198 | 0.1257 | 0.0996 | +0.0261 |
| KLAS/temp_min | 256 | 50 | 0.055 | 0.0576 | 0.0461 | 0.0217 | +0.0244 |
| KLAX/temp_min | 260 | 50 | 0.142 | 0.0767 | 0.0762 | 0.0360 | +0.0402 |
| KMDW/temp_min | 604 | 82 | 0.180 | 0.1220 | 0.1279 | 0.0827 | +0.0451 |
| KMIA/temp_min | 248 | 49 | 0.206 | 0.1448 | 0.1367 | 0.0903 | +0.0465 |
| KMSP/temp_max | 604 | 82 | 0.200 | 0.1508 | 0.1499 | 0.1156 | +0.0343 |
| KMSP/temp_min | 248 | 49 | 0.149 | 0.1072 | 0.1044 | 0.0576 | +0.0469 |
| KNYC/temp_min | 240 | 49 | 0.225 | 0.1639 | 0.1501 | 0.1084 | +0.0417 |
| KPHL/temp_min | 224 | 47 | 0.107 | 0.0687 | 0.0644 | 0.0527 | +0.0117 |
| KPHX/temp_max | 596 | 81 | 0.227 | 0.2032 | 0.1515 | 0.1262 | +0.0254 |
| KPHX/temp_min | 200 | 43 | 0.110 | 0.0877 | 0.0835 | 0.0654 | +0.0181 |
| KSAT/temp_max | 604 | 82 | 0.224 | 0.1678 | 0.1741 | 0.1173 | +0.0568 |
| KSAT/temp_min | 204 | 44 | 0.201 | 0.1095 | 0.1342 | 0.0507 | +0.0836 |
| KSEA/temp_max | 604 | 82 | 0.212 | 0.1655 | 0.1543 | 0.1318 | +0.0224 |
| KSEA/temp_min | 204 | 44 | 0.221 | 0.1200 | 0.1178 | 0.0786 | +0.0392 |
| KSFO/temp_max | 604 | 82 | 0.197 | 0.1584 | 0.1507 | 0.1238 | +0.0269 |
| KSFO/temp_min | 200 | 44 | 0.225 | 0.1132 | 0.1186 | 0.0579 | +0.0607 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 1564 | 19 | 0.1606 | 0.1444 | 0.1558 | 0.0458 |
| 1 | 1424 | 18 | 0.1629 | 0.1466 | 0.1562 | 0.1298 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 82 | 66 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 82 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 82 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 19 | 5 | 0.9904 |
| members_vs_market (p_members < p_mkt) | 19 | 0 | 1.0000 |
