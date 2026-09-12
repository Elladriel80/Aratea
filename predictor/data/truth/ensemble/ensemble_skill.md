# Vrais membres contre le chiffre officiel

Généré : 2026-09-12T14:27:51Z. Émissions GEFS 00z 2026-07-27 → 2026-09-06. Cibles holdout ≥ 2026-08-03, leads [1, 2, 3, 4, 5, 6, 7].

P(bin) = part des 31 versions du modèle américain (GEFS) dans chaque contrat de 2 °. La vérité est le chiffre officiel de la station (même fichier que A1). La correction ville est la table A1, apprise avant le 3 août, pas sur les jours de test.

Open-Meteo ne garde les membres que 3 jours. L'archive européenne n'a plus août. On a donc utilisé l'archive publique NOAA pour GEFS. Aucun chiffre manquant n'a été inventé.

Sonde Open-Meteo (station KATL) : membres remplis seulement {'ecmwf_ifs025': ('2026-09-09', '2026-09-12', 4), 'ecmwf_aifs025': ('2026-09-09', '2026-09-12', 4), 'gfs025': ('2026-09-09', '2026-09-12', 4), 'google_weathernext2_ensemble': ('2026-09-09', '2026-09-12', 4)}. Ce n'est pas le holdout. On ne mélange pas ces 3 jours au test principal.

Téléchargements GEFS en échec : 164. Ces heures sont absentes, pas remplacées. Détail dans ensemble_skill.json.

34020 prévisions NBM déjà là (A2).

Comparaison principale : les mêmes contrats que notre mélange actuel (centrées sur la moyenne des 5 modèles, comme A1 et A2). Plus le score d'erreur est petit, mieux c'est.

### Même contrats que l'ensemble (HOLDOUT)

| groupe | n bins | n dates | Brier membres | Brier membres + correction ville | Brier mélange | Brier mélange + correction ville | Brier NBM |
|---|---|---|---|---|---|---|---|
| all | 53928 | 36 | 0.1486 | 0.1430 | 0.1250 | 0.1154 | 0.1197 |

### Par horizon (jours d'avance)

| lead | n bins | n dates | Brier membres | Brier membres + correction ville | Brier mélange | Brier mélange + correction ville | Brier NBM |
|---|---|---|---|---|---|---|---|
| 1 | 7704 | 36 | 0.1629 | 0.1557 | 0.1259 | 0.1125 | 0.1174 |
| 2 | 7704 | 36 | 0.1566 | 0.1505 | 0.1262 | 0.1150 | 0.1198 |
| 3 | 7704 | 36 | 0.1513 | 0.1444 | 0.1237 | 0.1143 | 0.1193 |
| 4 | 7704 | 36 | 0.1477 | 0.1409 | 0.1256 | 0.1162 | 0.1205 |
| 5 | 7704 | 36 | 0.1419 | 0.1373 | 0.1238 | 0.1161 | 0.1207 |
| 6 | 7704 | 36 | 0.1404 | 0.1371 | 0.1256 | 0.1165 | 0.1200 |
| 7 | 7704 | 36 | 0.1392 | 0.1348 | 0.1242 | 0.1171 | 0.1204 |

### Par max / min

| variable | n bins | n dates | Brier membres | Brier membres + correction ville | Brier mélange | Brier NBM |
|---|---|---|---|---|---|---|
| temp_max | 26964 | 36 | 0.1356 | 0.1304 | 0.1240 | 0.1144 |
| temp_min | 26964 | 36 | 0.1615 | 0.1556 | 0.1260 | 0.1251 |

### Par station

| station | n bins | n dates | Brier membres | Brier membres + correction ville | Brier mélange | Brier NBM |
|---|---|---|---|---|---|---|
| KATL/temp_max | 1512 | 36 | 0.1140 | 0.1243 | 0.1180 | 0.1039 |
| KATL/temp_min | 1512 | 36 | 0.1269 | 0.1438 | 0.1168 | 0.1220 |
| KAUS/temp_max | 1512 | 36 | 0.1171 | 0.1198 | 0.1177 | 0.1143 |
| KAUS/temp_min | 1512 | 36 | 0.1871 | 0.1662 | 0.1571 | 0.1324 |
| KBOS/temp_max | 1512 | 36 | 0.1086 | 0.1133 | 0.1216 | 0.1087 |
| KBOS/temp_min | 1512 | 36 | 0.1167 | 0.1217 | 0.1330 | 0.1227 |
| KDCA/temp_max | 1512 | 36 | 0.1283 | 0.1276 | 0.1279 | 0.1168 |
| KDCA/temp_min | 1512 | 36 | 0.1416 | 0.1402 | 0.1293 | 0.1346 |
| KDEN/temp_max | 1470 | 35 | 0.1163 | 0.1134 | 0.1187 | 0.1038 |
| KDEN/temp_min | 1470 | 35 | 0.1609 | 0.1288 | 0.1477 | 0.1212 |
| KDFW/temp_max | 1512 | 36 | 0.1319 | 0.1412 | 0.1186 | 0.1301 |
| KDFW/temp_min | 1512 | 36 | 0.1944 | 0.1810 | 0.1329 | 0.1197 |
| KHOU/temp_max | 1512 | 36 | 0.1485 | 0.1574 | 0.1191 | 0.1136 |
| KHOU/temp_min | 1512 | 36 | 0.2111 | 0.2098 | 0.1049 | 0.1068 |
| KLAS/temp_max | 1470 | 35 | 0.1815 | 0.1737 | 0.1428 | 0.1158 |
| KLAS/temp_min | 1470 | 35 | 0.1783 | 0.1610 | 0.1297 | 0.1234 |
| KLAX/temp_max | 1470 | 35 | 0.1551 | 0.1246 | 0.1417 | 0.1241 |
| KLAX/temp_min | 1470 | 35 | 0.1748 | 0.1731 | 0.1086 | 0.1112 |
| KMDW/temp_max | 1512 | 36 | 0.1279 | 0.1284 | 0.1217 | 0.1226 |
| KMDW/temp_min | 1512 | 36 | 0.1297 | 0.1249 | 0.1145 | 0.1177 |
| KMIA/temp_max | 1512 | 36 | 0.1681 | 0.0892 | 0.1305 | 0.0902 |
| KMIA/temp_min | 1512 | 36 | 0.2135 | 0.2076 | 0.1392 | 0.1537 |
| KMSP/temp_max | 1512 | 36 | 0.1324 | 0.1342 | 0.1269 | 0.1239 |
| KMSP/temp_min | 1512 | 36 | 0.1357 | 0.1352 | 0.1225 | 0.1233 |
| KNYC/temp_max | 1512 | 36 | 0.1528 | 0.1518 | 0.1271 | 0.1239 |
| KNYC/temp_min | 1512 | 36 | 0.1697 | 0.1685 | 0.1365 | 0.1252 |
| KPHL/temp_max | 1512 | 36 | 0.1199 | 0.1207 | 0.1270 | 0.1130 |
| KPHL/temp_min | 1512 | 36 | 0.1533 | 0.1425 | 0.1320 | 0.1380 |
| KPHX/temp_max | 1470 | 35 | 0.1196 | 0.1021 | 0.1172 | 0.0948 |
| KPHX/temp_min | 1470 | 35 | 0.1254 | 0.1259 | 0.1241 | 0.1256 |
| KSAT/temp_max | 1512 | 36 | 0.1223 | 0.1227 | 0.1070 | 0.1178 |
| KSAT/temp_min | 1512 | 36 | 0.1824 | 0.1827 | 0.1116 | 0.1254 |
| KSEA/temp_max | 1470 | 35 | 0.1229 | 0.1276 | 0.1226 | 0.1167 |
| KSEA/temp_min | 1470 | 35 | 0.1483 | 0.1202 | 0.1071 | 0.1221 |
| KSFO/temp_max | 1470 | 35 | 0.1758 | 0.1757 | 0.1258 | 0.1246 |
| KSFO/temp_min | 1470 | 35 | 0.1564 | 0.1655 | 0.1207 | 0.1263 |

Prix de marché (kalshi_mid) quand une capture existait, membres GEFS émis avant la date cible, vérité CLI.
Lignes écartées : {'no_members': 248, 'no_cli_truth': 56}.

### Contre le prix de marché

| groupe | n bins | n dates | Brier membres | Brier mélange | Brier NBM | Brier marché |
|---|---|---|---|---|---|---|
| all | 1276 | 15 | 0.1838 | 0.1449 | 0.1324 | 0.1179 |

### Marché par horizon

| lead | n bins | n dates | Brier membres | Brier mélange | Brier marché |
|---|---|---|---|---|---|
| 1 | 1276 | 15 | 0.1838 | 0.1449 | 0.1179 |

### Victoires jour par jour

| comparaison | jours | victoires du premier | chance que ce soit le hasard |
|---|---|---|---|
| members_vs_raw | 36 | 0 | 1.0000 |
| members_vs_station | 36 | 0 | 1.0000 |
| members_bias_vs_station | 36 | 0 | 1.0000 |
| members_vs_nbm | 36 | 0 | 1.0000 |
| members_bias_vs_nbm | 36 | 0 | 1.0000 |
| members_vs_market | 15 | 0 | 1.0000 |
| members_vs_raw_market_rows | 15 | 1 | 1.0000 |

Le modèle en ligne n'est pas changé. Le site public n'est pas changé. Pas de pari avec de l'argent réel.

