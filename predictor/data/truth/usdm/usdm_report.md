# US Drought Monitor : comptes mesurés

Cible catalogue : Sécheresse US.
Vérité : US Drought Monitor.
Prévision essayée : Open-Meteo Seasonal.
Aucun chiffre inventé. Champion Kalshi inchangé.

## Semaines

| Série | Semaines | Premier | Dernier | Trous | Saisons ≥ 12 semaines |
|---|---:|---|---|---:|---:|
| CONUS | 1393 | 2000-01-04 | 2026-09-08 | 0 | 106 |
| Midwest | 1393 | 2000-01-04 | 2026-09-08 | 0 | 106 |
| Southwest | 1393 | 2000-01-04 | 2026-09-08 | 0 | 106 |
| Midwest_plus_Southwest | 1393 | 2000-01-04 | 2026-09-08 | 0 | 106 |

## Classes (part de semaines avec une aire > 0, catégoriel)

### CONUS

| Classe | Semaines > 0 | Part | Moyenne | Max |
|---|---:|---:|---:|---:|
| None | 1393 | 1.000 | 50.01 | 91.16 |
| D0 Abnormally Dry | 1393 | 1.000 | 18.27 | 43.78 |
| D1 Moderate Drought | 1393 | 1.000 | 13.72 | 30.21 |
| D2 Severe Drought | 1391 | 0.999 | 10.34 | 28.71 |
| D3 Extreme Drought | 1339 | 0.961 | 5.84 | 19.93 |
| D4 Exceptional Drought | 1087 | 0.780 | 1.82 | 11.96 |

D2+ moyenne 18.00. Semaines D2+ > 0 : 1391. Semaines D2+ ≥ 30 % : 266.

### Midwest

| Classe | Semaines > 0 | Part | Moyenne | Max |
|---|---:|---:|---:|---:|
| None | 1393 | 1.000 | 67.39 | 100.00 |
| D0 Abnormally Dry | 1359 | 0.976 | 17.34 | 57.56 |
| D1 Moderate Drought | 1206 | 0.866 | 10.06 | 47.47 |
| D2 Severe Drought | 935 | 0.671 | 3.98 | 37.34 |
| D3 Extreme Drought | 505 | 0.363 | 1.19 | 34.54 |
| D4 Exceptional Drought | 115 | 0.083 | 0.05 | 7.72 |

D2+ moyenne 5.21. Semaines D2+ > 0 : 935. Semaines D2+ ≥ 30 % : 31.

### Southwest

| Classe | Semaines > 0 | Part | Moyenne | Max |
|---|---:|---:|---:|---:|
| None | 1389 | 0.997 | 29.87 | 91.93 |
| D0 Abnormally Dry | 1393 | 1.000 | 18.40 | 84.60 |
| D1 Moderate Drought | 1393 | 1.000 | 18.64 | 58.95 |
| D2 Severe Drought | 1350 | 0.969 | 18.14 | 55.51 |
| D3 Extreme Drought | 1194 | 0.857 | 11.17 | 48.09 |
| D4 Exceptional Drought | 779 | 0.559 | 3.79 | 43.92 |

D2+ moyenne 33.10. Semaines D2+ > 0 : 1350. Semaines D2+ ≥ 30 % : 659.

### Midwest_plus_Southwest

| Classe | Semaines > 0 | Part | Moyenne | Max |
|---|---:|---:|---:|---:|
| None | 1393 | 1.000 | 46.19 | 94.02 |
| D0 Abnormally Dry | 1393 | 1.000 | 17.94 | 64.83 |
| D1 Moderate Drought | 1393 | 1.000 | 14.90 | 38.90 |
| D2 Severe Drought | 1390 | 0.998 | 11.98 | 43.59 |
| D3 Extreme Drought | 1261 | 0.905 | 6.83 | 27.61 |
| D4 Exceptional Drought | 825 | 0.592 | 2.16 | 24.81 |

D2+ moyenne 20.97. Semaines D2+ > 0 : 1390. Semaines D2+ ≥ 30 % : 421.

## Verdicts (noms du catalogue, non renommés)

- Sécheresse US : bloquée
- US Drought Monitor : testée, ça aide
- Open-Meteo Seasonal : bloquée
- NMME : bloquée
- SEAS5 : pas encore testée
- C3S multi-modèle : pas encore testée
- SPEI : pas encore testée
- CHIRPS pluie : pas encore testée
- Sécheresse Méditerranée : cible Tier 1 (pas encore testée)
- Sécheresse Inde : cible Tier 1 (pas encore testée)
- Ouragan formation : cible Tier 1 (pas encore testée)
- Ouragan intensité : cible Tier 1 (pas encore testée)
- Ouragan landfall : cible Tier 1 (pas encore testée)

## Open-Meteo Seasonal

Open-Meteo Seasonal refuse start_date avant 2025-09-01 (Parameter 'start_date' is out of allowed range from 2025-09-01 to 2027-04-16). Pas de hindcast depuis 2000. Fenêtre servie : 2025-09-01 à 2027-04-16.
Mois complets distincts : 12. Saisons distinctes : 4. Gate : 10 saisons et BSS > 0.05.
Midwest (saisons) : n=4 Brier prévision 0.75 Brier climato 0.0 BSS None.
Southwest (saisons) : n=4 Brier prévision 0.25 Brier climato 0.3333 BSS 0.25.

## NMME

Accès public insuffisant pour un hindcast noté (voir nmme_probe.json).
