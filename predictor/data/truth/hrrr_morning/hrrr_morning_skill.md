# HRRR du matin même contre le chiffre officiel et le marché

Généré : 2026-09-12T18:22:50Z. Run 12 h UTC du jour même, heures encore dans le jour LST après 12 h. Vérité : chiffre officiel de la station (même fichier que A1). Sigma appris avant 2026-08-03. Prix notés seulement s'ils sont pris à 13 h UTC ou plus tard (le run est alors public). Aucune heure manquante n'a été inventée.

HRRR du matin même = run 12 h UTC du jour, API Single Runs Open-Meteo, modèle gfs_hrrr, champ temperature_2m. Ce n'est pas la veille (previous_day1). Ce n'est pas le jour 0 recousu. Archive depuis le 2 avril 2026. Aucune heure manquante n'est inventée.

Ce fichier ne mélange pas la prévision de la veille. Il ne relance pas le thermomètre du jour.

Stations avec un run du matin : 18/18.
Lignes hors marché : 28722. Holdout A1 (2026-08-03 → 2026-09-07) : 7776.
Captures same-day lues : 5197. Lignes marché : 4985 (60 jours). Jours de test (≥ 2026-08-03) : 12.
Skips : {'prix_avant_le_run_du_matin': 152, 'pas_encore_de_correction_ville': 56, 'pas_de_chiffre_officiel': 4}.
Échecs de téléchargement : 0.
Verdict : testée ça n'aide pas. Promotion : non.

Le robot de paper-trading ne vise que demain. On n'a pas changé ça.

Plus le score d'erreur est petit, mieux c'est.

### Hors marché, cases synthétiques autour du max/min du matin

| groupe | n bins | n dates | Brier HRRR matin |
|---|---|---|---|
| all | 28722 | 133 | 0.1244 |

### Hors marché, holdout A1 (2026-08-03 → 2026-09-07)

| groupe | n bins | n dates | Brier HRRR matin |
|---|---|---|---|
| all | 7776 | 36 | 0.1244 |

### Hors marché, par max / min

| variable | n bins | n dates | Brier HRRR matin |
|---|---|---|---|
| temp_max | 14364 | 133 | 0.1182 |
| temp_min | 14358 | 133 | 0.1306 |

### Jour même avec un prix (après 13 h UTC)

| groupe | n bins | n dates | Brier HRRR matin | Brier correction ville | Brier mélange | Brier prix |
|---|---|---|---|---|---|---|
| all | 4985 | 60 | 0.1418 | 0.1316 | 0.1425 | 0.0573 |

### Jour même, test (≥ 2026-08-03)

| groupe | n bins | n dates | Brier HRRR matin | Brier correction ville | Brier mélange | Brier prix |
|---|---|---|---|---|---|---|
| all | 1037 | 12 | 0.1398 | 0.1313 | 0.1433 | 0.0540 |

### Jour même, par max / min

| variable | n bins | n dates | Brier HRRR matin | Brier correction ville | Brier mélange | Brier prix |
|---|---|---|---|---|---|---|
| temp_max | 2373 | 60 | 0.1470 | 0.1518 | 0.1699 | 0.0903 |
| temp_min | 2612 | 59 | 0.1370 | 0.1131 | 0.1176 | 0.0274 |

### Jour même, par station

| station/variable | n bins | n dates | Brier HRRR matin | Brier correction ville | Brier mélange | Brier prix |
|---|---|---|---|---|---|---|
| KATL/temp_max | 240 | 60 | 0.1740 | 0.1655 | 0.1838 | 0.0865 |
| KATL/temp_min | 236 | 59 | 0.1557 | 0.1225 | 0.1532 | 0.0361 |
| KAUS/temp_min | 236 | 59 | 0.2040 | 0.1667 | 0.1686 | 0.0174 |
| KBOS/temp_max | 240 | 60 | 0.1287 | 0.1327 | 0.1617 | 0.0287 |
| KBOS/temp_min | 236 | 59 | 0.0441 | 0.0385 | 0.0440 | 0.0179 |
| KDCA/temp_min | 236 | 59 | 0.1382 | 0.0997 | 0.0925 | 0.0331 |
| KDEN/temp_min | 200 | 50 | 0.1871 | 0.1505 | 0.1974 | 0.0364 |
| KDFW/temp_max | 240 | 60 | 0.1536 | 0.1727 | 0.1631 | 0.0938 |
| KDFW/temp_min | 236 | 59 | 0.1387 | 0.1244 | 0.1116 | 0.0071 |
| KHOU/temp_max | 237 | 60 | 0.1459 | 0.1605 | 0.1398 | 0.0665 |
| KHOU/temp_min | 100 | 25 | 0.1539 | 0.1439 | 0.1394 | 0.0410 |
| KLAS/temp_max | 236 | 59 | 0.1148 | 0.1146 | 0.2213 | 0.0804 |
| KLAS/temp_min | 100 | 25 | 0.0453 | 0.0314 | 0.0444 | 0.0004 |
| KLAX/temp_min | 100 | 25 | 0.1359 | 0.0722 | 0.0723 | 0.0078 |
| KMDW/temp_min | 236 | 59 | 0.1383 | 0.1232 | 0.1103 | 0.0422 |
| KMIA/temp_min | 96 | 24 | 0.1499 | 0.1290 | 0.1506 | 0.0399 |
| KMSP/temp_max | 236 | 59 | 0.1469 | 0.1516 | 0.1493 | 0.1006 |
| KMSP/temp_min | 96 | 24 | 0.1337 | 0.1074 | 0.1035 | 0.0126 |
| KNYC/temp_min | 96 | 24 | 0.1854 | 0.1469 | 0.1772 | 0.0758 |
| KPHL/temp_min | 88 | 22 | 0.0740 | 0.0586 | 0.0659 | 0.0369 |
| KPHX/temp_max | 236 | 59 | 0.1459 | 0.1462 | 0.1987 | 0.1148 |
| KPHX/temp_min | 80 | 20 | 0.0888 | 0.0871 | 0.0817 | 0.0251 |
| KSAT/temp_max | 236 | 59 | 0.1534 | 0.1767 | 0.1622 | 0.1057 |
| KSAT/temp_min | 80 | 20 | 0.1210 | 0.1574 | 0.1244 | 0.0092 |
| KSEA/temp_max | 236 | 59 | 0.1609 | 0.1555 | 0.1681 | 0.1217 |
| KSEA/temp_min | 80 | 20 | 0.1348 | 0.1269 | 0.1243 | 0.0477 |
| KSFO/temp_max | 236 | 59 | 0.1456 | 0.1422 | 0.1507 | 0.1054 |
| KSFO/temp_min | 80 | 20 | 0.1823 | 0.1212 | 0.0997 | 0.0116 |

### Combien de jours on gagne

- HRRR matin contre correction ville : 18 jours sur 60 (p = 0.9995)
- HRRR matin contre le prix : 0 jours sur 60 (p = 1.0000)
- correction ville contre le prix : 0 jours sur 60 (p = 1.0000)
- HRRR matin contre correction ville (test) : 5 jours sur 12 (p = 0.8062)
- HRRR matin contre le prix (test) : 0 jours sur 12 (p = 1.0000)

Règle : 30 jours minimum pour parler du marché. Jours avec prix et HRRR du matin : 60. Promotion : non.

Le modèle en ligne n'est pas changé. Pas de pari avec de l'argent réel.

