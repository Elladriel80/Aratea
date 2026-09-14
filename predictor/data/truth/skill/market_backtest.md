# Correction station vs marché Kalshi / Station bias vs Kalshi market

Généré / generated : 2026-09-14T11:34:01Z. Captures live `forward_*.json`, bins centraux cotés deux côtés, première capture par (ticker, lead). Issue des bins : vérité CLI. Biais station appris point-in-time (cibles < date de capture, ≥ 20 paires). Skips : {'no_bias_yet': 152, 'no_cli_truth': 72}.

FR : `raw` = politique de production recalculée à l'identique sur toutes les captures. `station` = raw + biais station, sigma résiduel. `kalshi_mid` = prix marché à la capture. Négatif dans la dernière colonne = on bat le marché.
EN : raw = production policy recomputed uniformly; station = raw + point-in-time station bias and residual sigma; kalshi_mid = market mid at capture. Negative last column = beats the market.

### Global / overall

| groupe | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| all | 10229 | 68 | 0.192 | 0.1435 | 0.1340 | 0.0905 | +0.0435 |

### Par lead / by lead (jours entre capture et cible)

| lead | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 0 | 5233 | 63 | 0.192 | 0.1424 | 0.1319 | 0.0574 | +0.0744 |
| 1 | 4996 | 62 | 0.191 | 0.1446 | 0.1363 | 0.1251 | +0.0112 |

### Par mois de cible / by target month

| mois | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| 2026-06 | 3132 | 20 | 0.179 | 0.1313 | 0.1250 | 0.0839 | +0.0411 |
| 2026-07 | 4524 | 31 | 0.196 | 0.1490 | 0.1380 | 0.0964 | +0.0416 |
| 2026-08 | 1757 | 11 | 0.191 | 0.1404 | 0.1320 | 0.0881 | +0.0440 |
| 2026-09 | 816 | 6 | 0.217 | 0.1660 | 0.1509 | 0.0883 | +0.0625 |

### Par station / by station

| station/variable | n bins | n dates | base rate | Brier raw | Brier station | Brier kalshi_mid | station − marché |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 500 | 68 | 0.230 | 0.1855 | 0.1703 | 0.1264 | +0.0439 |
| KATL/temp_min | 492 | 68 | 0.203 | 0.1478 | 0.1257 | 0.0814 | +0.0443 |
| KAUS/temp_min | 492 | 68 | 0.234 | 0.1741 | 0.1673 | 0.0804 | +0.0869 |
| KBOS/temp_max | 500 | 68 | 0.174 | 0.1591 | 0.1357 | 0.0759 | +0.0598 |
| KBOS/temp_min | 492 | 68 | 0.057 | 0.0417 | 0.0418 | 0.0307 | +0.0111 |
| KDCA/temp_min | 492 | 68 | 0.165 | 0.0967 | 0.1001 | 0.0689 | +0.0312 |
| KDEN/temp_min | 316 | 61 | 0.187 | 0.1838 | 0.1387 | 0.0620 | +0.0766 |
| KDFW/temp_max | 500 | 68 | 0.220 | 0.1670 | 0.1790 | 0.1150 | +0.0640 |
| KDFW/temp_min | 492 | 68 | 0.209 | 0.1240 | 0.1337 | 0.0698 | +0.0639 |
| KHOU/temp_max | 493 | 68 | 0.205 | 0.1421 | 0.1689 | 0.1013 | +0.0676 |
| KHOU/temp_min | 204 | 40 | 0.235 | 0.1401 | 0.1475 | 0.0877 | +0.0598 |
| KLAS/temp_max | 492 | 68 | 0.234 | 0.2202 | 0.1227 | 0.0990 | +0.0237 |
| KLAS/temp_min | 204 | 40 | 0.029 | 0.0431 | 0.0272 | 0.0086 | +0.0186 |
| KLAX/temp_min | 200 | 39 | 0.145 | 0.0754 | 0.0730 | 0.0362 | +0.0368 |
| KMDW/temp_min | 492 | 68 | 0.173 | 0.1129 | 0.1231 | 0.0802 | +0.0429 |
| KMIA/temp_min | 196 | 39 | 0.209 | 0.1496 | 0.1414 | 0.0937 | +0.0477 |
| KMSP/temp_max | 492 | 68 | 0.205 | 0.1493 | 0.1527 | 0.1191 | +0.0335 |
| KMSP/temp_min | 196 | 39 | 0.148 | 0.1112 | 0.1048 | 0.0566 | +0.0483 |
| KNYC/temp_min | 188 | 39 | 0.218 | 0.1602 | 0.1407 | 0.1048 | +0.0358 |
| KPHL/temp_min | 172 | 37 | 0.087 | 0.0759 | 0.0640 | 0.0559 | +0.0081 |
| KPHX/temp_max | 492 | 68 | 0.230 | 0.1998 | 0.1491 | 0.1312 | +0.0179 |
| KPHX/temp_min | 164 | 36 | 0.116 | 0.0844 | 0.0838 | 0.0709 | +0.0129 |
| KSAT/temp_max | 492 | 68 | 0.230 | 0.1696 | 0.1806 | 0.1271 | +0.0534 |
| KSAT/temp_min | 164 | 36 | 0.201 | 0.1017 | 0.1354 | 0.0450 | +0.0904 |
| KSEA/temp_max | 492 | 68 | 0.211 | 0.1660 | 0.1566 | 0.1398 | +0.0168 |
| KSEA/temp_min | 164 | 36 | 0.220 | 0.1263 | 0.1233 | 0.0872 | +0.0361 |
| KSFO/temp_max | 492 | 68 | 0.197 | 0.1599 | 0.1509 | 0.1260 | +0.0248 |
| KSFO/temp_min | 164 | 36 | 0.226 | 0.1141 | 0.1205 | 0.0653 | +0.0552 |

### Challenger ensemble_members (lignes où il est capturé)

| lead | n bins | n dates | Brier raw | Brier station | Brier members | Brier kalshi_mid |
|---|---|---|---|---|---|---|
| 0 | 336 | 5 | 0.1680 | 0.1566 | 0.1551 | 0.0625 |
| 1 | 256 | 4 | 0.1720 | 0.1585 | 0.1519 | 0.1306 |

### Sign tests par date

| comparaison | dates | victoires a | p unilatéral |
|---|---|---|---|
| station_vs_raw (p_station < p_raw) | 68 | 55 | 0.0000 |
| raw_vs_market (p_raw < p_mkt) | 68 | 1 | 1.0000 |
| station_vs_market (p_station < p_mkt) | 68 | 1 | 1.0000 |
| members_vs_station (p_members < p_station) | 5 | 4 | 0.1875 |
| members_vs_market (p_members < p_mkt) | 5 | 0 | 1.0000 |
