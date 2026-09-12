# Thermomètre du jour contre le chiffre officiel et le marché

Généré : 2026-09-12T15:12:59Z. Captures du jour même (lead 0), bins cotés deux côtés. Vérité : chiffre officiel de la station (même fichier que A1). Apprentissage de la hausse restante : jours avant 2026-08-03. Aucune lecture manquante n'a été inventée.

HRRR horaire = run de la veille (Open-Meteo Previous Runs, modèle gfs_hrrr, champ temperature_2m_previous_day1). Le run du matin même est sur S3 mais illisible ici sans eccodes. Aucune heure manquante n'est inventée.

api.weather.gov ne garde que les jours récents. L'été 2026 vient de l'archive IEM (lectures horaires). Sonde NWS (KATL, 12 septembre) : 500 lectures, du 11 septembre 01:45 UTC au 12 septembre 14:50 UTC. Pas l'été 2026.

Stations avec lectures : 18/18.
Lectures IEM : 56302. Stations HRRR : 18.
Captures same-day lues : 5197. Lignes notées : 4921 (59 jours). Jours de test (≥ 2026-08-03) : 12.
Skips : {'pas_encore_de_correction_ville': 88, 'pas_assez_de_lectures': 184, 'pas_de_chiffre_officiel': 4}.
Source du reste de journée : {'hrrr_previous_day1': 4921}.
Échecs de téléchargement : 0.

Le robot de paper-trading ne vise que demain (`daily_auto.py`, date = aujourd'hui + 1). On n'a pas changé ça.

Plus le score d'erreur est petit, mieux c'est.

### Tous les jours same-day avec un prix

| groupe | n bins | n dates | Brier thermomètre + reste | Brier reste simple | Brier correction ville | Brier mélange | Brier prix |
|---|---|---|---|---|---|---|---|
| all | 4921 | 59 | 0.1263 | 0.1055 | 0.1317 | 0.1423 | 0.0585 |

### Jours de test (≥ 2026-08-03)

| groupe | n bins | n dates | Brier thermomètre + reste | Brier reste simple | Brier correction ville | Brier mélange | Brier prix |
|---|---|---|---|---|---|---|---|
| all | 1037 | 12 | 0.1237 | 0.1089 | 0.1313 | 0.1433 | 0.0540 |

### Par max / min

| variable | n bins | n dates | Brier thermomètre + reste | Brier reste simple | Brier correction ville | Brier mélange | Brier prix |
|---|---|---|---|---|---|---|---|
| temp_max | 2333 | 59 | 0.1599 | 0.1294 | 0.1511 | 0.1695 | 0.0914 |
| temp_min | 2588 | 58 | 0.0960 | 0.0839 | 0.1141 | 0.1178 | 0.0288 |

### Par source du reste de journée

| source | n bins | n dates | Brier thermomètre + reste | Brier reste simple | Brier correction ville | Brier mélange | Brier prix |
|---|---|---|---|---|---|---|---|
| hrrr_previous_day1 | 4921 | 59 | 0.1263 | 0.1055 | 0.1317 | 0.1423 | 0.0585 |

### Par station

| station/variable | n bins | n dates | Brier thermomètre + reste | Brier reste simple | Brier correction ville | Brier mélange | Brier prix |
|---|---|---|---|---|---|---|---|
| KATL/temp_max | 236 | 59 | 0.1906 | 0.1107 | 0.1654 | 0.1841 | 0.0890 |
| KATL/temp_min | 232 | 58 | 0.0505 | 0.0979 | 0.1215 | 0.1501 | 0.0367 |
| KAUS/temp_min | 232 | 58 | 0.1541 | 0.0983 | 0.1675 | 0.1685 | 0.0177 |
| KBOS/temp_max | 236 | 59 | 0.1398 | 0.0978 | 0.1355 | 0.1618 | 0.0321 |
| KBOS/temp_min | 232 | 58 | 0.0319 | 0.0319 | 0.0387 | 0.0434 | 0.0182 |
| KDCA/temp_min | 232 | 58 | 0.1148 | 0.0930 | 0.1007 | 0.0939 | 0.0336 |
| KDEN/temp_min | 200 | 50 | 0.1870 | 0.1112 | 0.1504 | 0.1967 | 0.0369 |
| KDFW/temp_max | 236 | 59 | 0.1658 | 0.1119 | 0.1690 | 0.1621 | 0.0956 |
| KDFW/temp_min | 232 | 58 | 0.1034 | 0.0828 | 0.1255 | 0.1119 | 0.0073 |
| KHOU/temp_max | 233 | 59 | 0.1431 | 0.1156 | 0.1603 | 0.1373 | 0.0692 |
| KHOU/temp_min | 100 | 25 | 0.0491 | 0.1036 | 0.1450 | 0.1395 | 0.0412 |
| KLAS/temp_max | 232 | 58 | 0.1307 | 0.1576 | 0.1144 | 0.2247 | 0.0812 |
| KLAS/temp_min | 100 | 25 | 0.0237 | 0.0127 | 0.0315 | 0.0446 | 0.0005 |
| KLAX/temp_min | 100 | 25 | 0.1292 | 0.0476 | 0.0740 | 0.0719 | 0.0130 |
| KMDW/temp_min | 232 | 58 | 0.0937 | 0.1070 | 0.1245 | 0.1108 | 0.0475 |
| KMIA/temp_min | 96 | 24 | 0.1134 | 0.1068 | 0.1299 | 0.1517 | 0.0396 |
| KMSP/temp_max | 232 | 58 | 0.1535 | 0.1325 | 0.1497 | 0.1481 | 0.0995 |
| KMSP/temp_min | 96 | 24 | 0.0788 | 0.0668 | 0.1013 | 0.0956 | 0.0134 |
| KNYC/temp_min | 96 | 24 | 0.0941 | 0.1233 | 0.1525 | 0.1850 | 0.0757 |
| KPHL/temp_min | 88 | 22 | 0.0693 | 0.0609 | 0.0615 | 0.0715 | 0.0370 |
| KPHX/temp_max | 232 | 58 | 0.1647 | 0.1477 | 0.1479 | 0.1972 | 0.1159 |
| KPHX/temp_min | 80 | 20 | 0.1154 | 0.0727 | 0.0918 | 0.0850 | 0.0358 |
| KSAT/temp_max | 232 | 58 | 0.1697 | 0.1232 | 0.1738 | 0.1618 | 0.1068 |
| KSAT/temp_min | 80 | 20 | 0.0449 | 0.0771 | 0.1638 | 0.1251 | 0.0095 |
| KSEA/temp_max | 232 | 58 | 0.1668 | 0.1660 | 0.1544 | 0.1680 | 0.1228 |
| KSEA/temp_min | 80 | 20 | 0.1308 | 0.1097 | 0.1271 | 0.1240 | 0.0521 |
| KSFO/temp_max | 232 | 58 | 0.1736 | 0.1318 | 0.1407 | 0.1497 | 0.1034 |
| KSFO/temp_min | 80 | 20 | 0.0827 | 0.0678 | 0.1237 | 0.1002 | 0.0116 |

### Combien de jours on gagne

- thermomètre contre correction ville : 36 jours sur 59 (p = 0.0587)
- thermomètre contre le prix : 1 jours sur 59 (p = 1.0000)
- reste simple contre correction ville : 56 jours sur 59 (p = 0.0000)
- reste simple contre le prix : 0 jours sur 59 (p = 1.0000)
- correction ville contre le prix : 0 jours sur 59 (p = 1.0000)
- thermomètre contre correction ville (test) : 9 jours sur 12 (p = 0.0730)
- thermomètre contre le prix (test) : 0 jours sur 12 (p = 1.0000)

Règle : 30 jours minimum pour parler du marché. Jours avec prix et thermomètre : 59. Promotion : non.

Le modèle en ligne n'est pas changé. Pas de pari avec de l'argent réel.

