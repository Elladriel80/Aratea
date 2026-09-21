# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit

Période / span : 2020-01-01 → 2026-09-20. Généré / generated : 2026-09-21T11:44:15Z.

FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.

EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means the model has been learning to correct the wrong target.

| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |
|---|---|---|---|---|---|---|---|
| KATL | high | 2452 | -2.34 | 2.83 | 2.35 | 9% | 67% |
| KATL | low | 2451 | -1.77 | 2.15 | 1.97 | 12% | 49% |
| KAUS | high | 2455 | -1.63 | 2.56 | 2.68 | 10% | 57% |
| KAUS | low | 2455 | +4.04 | 4.45 | 3.95 | 8% | 70% |
| KBOS | high | 2452 | -1.03 | 2.10 | 2.46 | 14% | 45% |
| KBOS | low | 2452 | -0.92 | 1.96 | 2.35 | 16% | 41% |
| KDCA | high | 2447 | -2.00 | 2.61 | 2.44 | 10% | 59% |
| KDCA | low | 2447 | -2.45 | 2.76 | 2.23 | 10% | 62% |
| KDEN | high | 2455 | -1.84 | 2.87 | 3.12 | 9% | 61% |
| KDEN | low | 2455 | +2.65 | 3.60 | 3.8 | 10% | 64% |
| KDFW | high | 2451 | -1.17 | 2.27 | 2.61 | 15% | 50% |
| KDFW | low | 2451 | +0.55 | 1.65 | 2.13 | 21% | 32% |
| KHOU | high | 2451 | -3.01 | 3.31 | 2.44 | 7% | 72% |
| KHOU | low | 2451 | -1.21 | 1.90 | 2.05 | 16% | 41% |
| KLAS | high | 2453 | -0.50 | 1.23 | 1.58 | 29% | 20% |
| KLAS | low | 2452 | -2.07 | 2.65 | 2.45 | 9% | 60% |
| KLAX | high | 2087 | -1.15 | 2.15 | 2.48 | 14% | 47% |
| KLAX | low | 2087 | -1.16 | 1.73 | 1.9 | 20% | 35% |
| KMDW | high | 2454 | -1.76 | 2.32 | 2.21 | 11% | 53% |
| KMDW | low | 2454 | -2.52 | 2.89 | 2.53 | 10% | 61% |
| KMIA | high | 2445 | -2.26 | 2.48 | 1.84 | 9% | 59% |
| KMIA | low | 2445 | -2.15 | 2.59 | 2.24 | 10% | 58% |
| KMSP | high | 2455 | -1.25 | 2.15 | 2.42 | 15% | 47% |
| KMSP | low | 2455 | -1.61 | 2.35 | 2.66 | 15% | 47% |
| KNYC | high | 2453 | -0.88 | 1.98 | 2.38 | 17% | 43% |
| KNYC | low | 2453 | -2.54 | 3.10 | 3.15 | 11% | 59% |
| KPHL | high | 2455 | -1.10 | 1.92 | 2.16 | 16% | 42% |
| KPHL | low | 2455 | -1.47 | 2.16 | 2.34 | 15% | 47% |
| KPHX | high | 2452 | -2.23 | 2.37 | 1.79 | 10% | 55% |
| KPHX | low | 2452 | -2.86 | 3.20 | 2.48 | 7% | 70% |
| KSAT | high | 2453 | -2.01 | 2.67 | 2.56 | 11% | 60% |
| KSAT | low | 2455 | +0.15 | 2.04 | 2.65 | 14% | 42% |
| KSEA | high | 2451 | -1.63 | 2.50 | 2.67 | 11% | 54% |
| KSEA | low | 2450 | -1.11 | 1.73 | 1.91 | 18% | 35% |
| KSFO | high | 1718 | -1.24 | 2.46 | 2.79 | 13% | 56% |
| KSFO | low | 1718 | -1.18 | 1.76 | 1.83 | 17% | 39% |

Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`.
