# NBM station contre le chiffre officiel

Généré : 2026-09-12T13:52:03Z. Émissions NBP 2026-05-25 → 2026-09-06, cycles [13] UTC. Cibles holdout ≥ 2026-08-03, leads [1, 2, 3, 4, 5, 6, 7].

NBM = prévision déjà corrigée pour la station (seuils 10, 25, 50, 75 et 90 %). On relie ces seuils par des segments droits pour donner une chance à chaque contrat de 2 °. La vérité est le chiffre officiel de la station (même fichier que A1). Aucun chiffre manquant n'a été inventé.

Comparaison principale : les mêmes contrats que notre ensemble actuel (centrées sur la moyenne des modèles, comme A1). Plus le Brier est petit, mieux c'est.

### Même contrats que l'ensemble (HOLDOUT)

| groupe | n bins | n dates | Brier NBM | Brier ensemble | Brier ensemble + correction station | Brier climatologie station |
|---|---|---|---|---|---|---|
| all | 53928 | 36 | 0.1197 | 0.1250 | 0.1154 | 0.1278 |

### Par horizon (jours d'avance)

| lead | n bins | n dates | Brier NBM | Brier ensemble | Brier ensemble + correction station | Brier climatologie |
|---|---|---|---|---|---|---|
| 1 | 7704 | 36 | 0.1174 | 0.1259 | 0.1126 | 0.1327 |
| 2 | 7704 | 36 | 0.1198 | 0.1262 | 0.1150 | 0.1312 |
| 3 | 7704 | 36 | 0.1193 | 0.1237 | 0.1143 | 0.1276 |
| 4 | 7704 | 36 | 0.1205 | 0.1256 | 0.1161 | 0.1275 |
| 5 | 7704 | 36 | 0.1207 | 0.1238 | 0.1160 | 0.1264 |
| 6 | 7704 | 36 | 0.1200 | 0.1256 | 0.1166 | 0.1255 |
| 7 | 7704 | 36 | 0.1204 | 0.1242 | 0.1171 | 0.1238 |

### Par max / min

| variable | n bins | n dates | Brier NBM | Brier ensemble | Brier ensemble + correction station |
|---|---|---|---|---|---|
| temp_max | 26964 | 36 | 0.1144 | 0.1240 | 0.1120 |
| temp_min | 26964 | 36 | 0.1251 | 0.1260 | 0.1188 |

### Par station

| station | n bins | n dates | Brier NBM | Brier ensemble | Brier ensemble + correction station |
|---|---|---|---|---|---|
| KATL/temp_max | 1512 | 36 | 0.1039 | 0.1180 | 0.1077 |
| KATL/temp_min | 1512 | 36 | 0.1220 | 0.1168 | 0.1190 |
| KAUS/temp_max | 1512 | 36 | 0.1143 | 0.1177 | 0.1022 |
| KAUS/temp_min | 1512 | 36 | 0.1324 | 0.1571 | 0.1338 |
| KBOS/temp_max | 1512 | 36 | 0.1087 | 0.1216 | 0.1059 |
| KBOS/temp_min | 1512 | 36 | 0.1227 | 0.1330 | 0.1195 |
| KDCA/temp_max | 1512 | 36 | 0.1168 | 0.1279 | 0.1195 |
| KDCA/temp_min | 1512 | 36 | 0.1346 | 0.1293 | 0.1252 |
| KDEN/temp_max | 1470 | 35 | 0.1038 | 0.1187 | 0.1049 |
| KDEN/temp_min | 1470 | 35 | 0.1212 | 0.1477 | 0.1143 |
| KDFW/temp_max | 1512 | 36 | 0.1301 | 0.1186 | 0.1221 |
| KDFW/temp_min | 1512 | 36 | 0.1197 | 0.1329 | 0.1184 |
| KHOU/temp_max | 1512 | 36 | 0.1136 | 0.1191 | 0.1258 |
| KHOU/temp_min | 1512 | 36 | 0.1068 | 0.1049 | 0.1093 |
| KLAS/temp_max | 1470 | 35 | 0.1158 | 0.1428 | 0.1082 |
| KLAS/temp_min | 1470 | 35 | 0.1234 | 0.1297 | 0.1172 |
| KLAX/temp_max | 1470 | 35 | 0.1241 | 0.1417 | 0.1154 |
| KLAX/temp_min | 1470 | 35 | 0.1112 | 0.1086 | 0.0944 |
| KMDW/temp_max | 1512 | 36 | 0.1226 | 0.1217 | 0.1195 |
| KMDW/temp_min | 1512 | 36 | 0.1177 | 0.1145 | 0.1202 |
| KMIA/temp_max | 1512 | 36 | 0.0902 | 0.1305 | 0.0845 |
| KMIA/temp_min | 1512 | 36 | 0.1537 | 0.1392 | 0.1263 |
| KMSP/temp_max | 1512 | 36 | 0.1239 | 0.1269 | 0.1227 |
| KMSP/temp_min | 1512 | 36 | 0.1233 | 0.1225 | 0.1156 |
| KNYC/temp_max | 1512 | 36 | 0.1239 | 0.1271 | 0.1236 |
| KNYC/temp_min | 1512 | 36 | 0.1252 | 0.1365 | 0.1233 |
| KPHL/temp_max | 1512 | 36 | 0.1130 | 0.1270 | 0.1114 |
| KPHL/temp_min | 1512 | 36 | 0.1380 | 0.1320 | 0.1225 |
| KPHX/temp_max | 1470 | 35 | 0.0948 | 0.1172 | 0.0915 |
| KPHX/temp_min | 1470 | 35 | 0.1256 | 0.1241 | 0.1195 |
| KSAT/temp_max | 1512 | 36 | 0.1178 | 0.1070 | 0.1098 |
| KSAT/temp_min | 1512 | 36 | 0.1254 | 0.1116 | 0.1197 |
| KSEA/temp_max | 1470 | 35 | 0.1167 | 0.1226 | 0.1145 |
| KSEA/temp_min | 1470 | 35 | 0.1221 | 0.1071 | 0.1162 |
| KSFO/temp_max | 1470 | 35 | 0.1246 | 0.1258 | 0.1259 |
| KSFO/temp_min | 1470 | 35 | 0.1263 | 0.1207 | 0.1231 |

Contrats centrés sur le chiffre NBM (50 %) : autre lecture, pas les mêmes contrats.

### Contrats autour du NBM (HOLDOUT)

| groupe | n bins | n dates | Brier NBM | Brier climatologie station |
|---|---|---|---|---|
| all | 58392 | 41 | 0.1229 | 0.1307 |

Prix de marché (kalshi_mid) quand une capture existait, émission NBM avant la capture, vérité CLI.
Lignes écartées : {'no_cli_truth': 60}.

### Contre le prix de marché

| groupe | n bins | n dates | Brier NBM | Brier ensemble | Brier marché |
|---|---|---|---|---|---|
| all | 4948 | 61 | 0.1351 | 0.1443 | 0.1249 |

### Marché par horizon

| lead | n bins | n dates | Brier NBM | Brier ensemble | Brier marché |
|---|---|---|---|---|---|
| 1 | 4948 | 61 | 0.1351 | 0.1443 | 0.1249 |

### Victoires jour par jour

| comparaison | jours | victoires du premier | chance que ce soit le hasard |
|---|---|---|---|
| nbm_vs_raw | 36 | 31 | 0.0000 |
| nbm_vs_station | 36 | 5 | 1.0000 |
| nbm_vs_climo | 36 | 33 | 0.0000 |
| nbm_vs_climo_own_bins | 41 | 37 | 0.0000 |
| nbm_vs_market | 61 | 14 | 1.0000 |
| nbm_vs_raw_market_rows | 61 | 44 | 0.0004 |

Le modèle en ligne n'est pas changé. Le site public n'est pas changé. Pas de pari avec de l'argent réel.

