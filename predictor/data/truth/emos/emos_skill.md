# EMOS par station et par saison contre le chiffre officiel

Généré : 2026-09-12T14:38:11Z. Split TRAIN < 2026-08-03, HOLDOUT ≥ 2026-08-03 jusqu'au 2026-09-07. Leads [1, 2, 3, 4, 5, 6, 7].

EMOS = corriger à la fois le centre et la largeur de la cloche, ville par ville et saison par saison. Quatre nombres par groupe, ajustés pour coller au mieux au chiffre officiel (score CRPS). La vérité est le chiffre officiel de la station (même fichier que A1). Aucun chiffre manquant n'a été inventé.

Jours d'apprentissage par saison (points prévision) : {'MAM': 5040, 'JJA': 15876}. Jours de test par saison : {'JJA': 7308, 'SON': 1680}. Un groupe n'est ajusté que s'il a au moins 30 jours. S'il en a moins, on garde la correction ville actuelle.

Groupes EMOS saison : 252. Groupes EMOS sans saison (repli) : 252. Saisons vraiment ajustées : ['JJA'].

Lignes de test avec EMOS saison : 43848. Avec EMOS sans saison : 10080. Sans EMOS (repli correction ville) : 0.

34020 prévisions NBM déjà là (A2).

Comparaison principale : les mêmes contrats que notre mélange actuel (comme A1, A2 et A3). Plus le score d'erreur est petit, mieux c'est.

### Même contrats que l'ensemble (HOLDOUT)

| groupe | n bins | n dates | Brier EMOS (repli ville) | Brier EMOS seul | Brier correction ville | Brier mélange | Brier NBM |
|---|---|---|---|---|---|---|---|
| all | 53928 | 36 | 0.1163 | 0.1163 | 0.1154 | 0.1250 | 0.1197 |

### Par horizon (jours d'avance)

| lead | n bins | n dates | Brier EMOS (repli ville) | Brier correction ville | Brier NBM |
|---|---|---|---|---|---|
| 1 | 7704 | 36 | 0.1131 | 0.1126 | 0.1174 |
| 2 | 7704 | 36 | 0.1170 | 0.1150 | 0.1198 |
| 3 | 7704 | 36 | 0.1153 | 0.1143 | 0.1193 |
| 4 | 7704 | 36 | 0.1168 | 0.1161 | 0.1205 |
| 5 | 7704 | 36 | 0.1173 | 0.1160 | 0.1207 |
| 6 | 7704 | 36 | 0.1170 | 0.1166 | 0.1200 |
| 7 | 7704 | 36 | 0.1174 | 0.1171 | 0.1204 |

### Par saison météo (test)

| saison | n bins | n dates | Brier EMOS (repli ville) | Brier correction ville | Brier NBM |
|---|---|---|---|---|---|
| JJA | 43848 | 29 | 0.1164 | 0.1156 | 0.1204 |
| SON | 10080 | 7 | 0.1158 | 0.1145 | 0.1171 |

### Par max / min

| variable | n bins | n dates | Brier EMOS (repli ville) | Brier correction ville | Brier NBM |
|---|---|---|---|---|---|
| temp_max | 26964 | 36 | 0.1143 | 0.1120 | 0.1144 |
| temp_min | 26964 | 36 | 0.1183 | 0.1188 | 0.1251 |

### Par station

| station | n bins | n dates | Brier EMOS (repli ville) | Brier correction ville | Brier NBM |
|---|---|---|---|---|---|
| KATL/temp_max | 1512 | 36 | 0.1043 | 0.1077 | 0.1039 |
| KATL/temp_min | 1512 | 36 | 0.1155 | 0.1190 | 0.1220 |
| KAUS/temp_max | 1512 | 36 | 0.1245 | 0.1022 | 0.1143 |
| KAUS/temp_min | 1512 | 36 | 0.1423 | 0.1338 | 0.1324 |
| KBOS/temp_max | 1512 | 36 | 0.1064 | 0.1059 | 0.1087 |
| KBOS/temp_min | 1512 | 36 | 0.1180 | 0.1195 | 0.1227 |
| KDCA/temp_max | 1512 | 36 | 0.1160 | 0.1195 | 0.1168 |
| KDCA/temp_min | 1512 | 36 | 0.1276 | 0.1252 | 0.1346 |
| KDEN/temp_max | 1470 | 35 | 0.1031 | 0.1049 | 0.1038 |
| KDEN/temp_min | 1470 | 35 | 0.1151 | 0.1143 | 0.1212 |
| KDFW/temp_max | 1512 | 36 | 0.1389 | 0.1221 | 0.1301 |
| KDFW/temp_min | 1512 | 36 | 0.1145 | 0.1184 | 0.1197 |
| KHOU/temp_max | 1512 | 36 | 0.1202 | 0.1258 | 0.1136 |
| KHOU/temp_min | 1512 | 36 | 0.1044 | 0.1093 | 0.1068 |
| KLAS/temp_max | 1470 | 35 | 0.1009 | 0.1082 | 0.1158 |
| KLAS/temp_min | 1470 | 35 | 0.1168 | 0.1172 | 0.1234 |
| KLAX/temp_max | 1470 | 35 | 0.1261 | 0.1154 | 0.1241 |
| KLAX/temp_min | 1470 | 35 | 0.0898 | 0.0944 | 0.1112 |
| KMDW/temp_max | 1512 | 36 | 0.1192 | 0.1195 | 0.1226 |
| KMDW/temp_min | 1512 | 36 | 0.1215 | 0.1202 | 0.1177 |
| KMIA/temp_max | 1512 | 36 | 0.0817 | 0.0845 | 0.0902 |
| KMIA/temp_min | 1512 | 36 | 0.1270 | 0.1263 | 0.1537 |
| KMSP/temp_max | 1512 | 36 | 0.1216 | 0.1227 | 0.1239 |
| KMSP/temp_min | 1512 | 36 | 0.1165 | 0.1156 | 0.1233 |
| KNYC/temp_max | 1512 | 36 | 0.1191 | 0.1236 | 0.1239 |
| KNYC/temp_min | 1512 | 36 | 0.1162 | 0.1233 | 0.1252 |
| KPHL/temp_max | 1512 | 36 | 0.1087 | 0.1114 | 0.1130 |
| KPHL/temp_min | 1512 | 36 | 0.1227 | 0.1225 | 0.1380 |
| KPHX/temp_max | 1470 | 35 | 0.0915 | 0.0915 | 0.0948 |
| KPHX/temp_min | 1470 | 35 | 0.1228 | 0.1195 | 0.1256 |
| KSAT/temp_max | 1512 | 36 | 0.1359 | 0.1098 | 0.1178 |
| KSAT/temp_min | 1512 | 36 | 0.1135 | 0.1197 | 0.1254 |
| KSEA/temp_max | 1470 | 35 | 0.1152 | 0.1145 | 0.1167 |
| KSEA/temp_min | 1470 | 35 | 0.1132 | 0.1162 | 0.1221 |
| KSFO/temp_max | 1470 | 35 | 0.1237 | 0.1259 | 0.1246 |
| KSFO/temp_min | 1470 | 35 | 0.1307 | 0.1231 | 0.1263 |

Prix de marché (kalshi_mid), la veille seulement. EMOS n'est noté que sur le HOLDOUT : les nombres viennent de dates avant 2026-08-03. Les 61 jours déjà mesurés à l'étape A2 mélangent juin et juillet ; on ne leur applique pas EMOS (ce serait regarder le futur).
Lignes écartées : {'emos_pre_split': 3860, 'no_cli_truth': 60}.

### Contre le prix de marché (HOLDOUT seulement, lead 1)

| groupe | n bins | n dates | Brier EMOS | Brier correction ville | Brier NBM | Brier marché |
|---|---|---|---|---|---|---|
| all | 1016 | 13 | 0.1356 | 0.1390 | 0.1340 | 0.1204 |

### Victoires jour par jour

| comparaison | jours | victoires du premier | chance que ce soit le hasard |
|---|---|---|---|
| emos_vs_station | 36 | 14 | 0.9338 |
| emos_vs_raw | 36 | 33 | 0.0000 |
| emos_vs_nbm | 36 | 27 | 0.0020 |
| emos_only_vs_station | 36 | 14 | 0.9338 |
| emos_vs_market_holdout | 13 | 2 | 0.9983 |
| station_vs_market_holdout | 13 | 1 | 0.9999 |
| nbm_vs_market_all | 61 | 14 | 1.0000 |

Décision : on ne change pas le modèle en ligne. EMOS ne bat pas la correction ville actuelle sur les 36 jours de test. Contre le marché, 13 jours seulement : trop peu, et EMOS perd.

Le modèle en ligne n'est pas changé. Le site public n'est pas changé. Pas de pari avec de l'argent réel.

