# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit

Période / span : 2020-01-01 → 2026-09-27. Généré / generated : 2026-09-28T12:39:18Z.

FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.

EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means the model has been learning to correct the wrong target.

| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |
|---|---|---|---|---|---|---|---|
| KATL | high | 2459 | -2.34 | 2.82 | 2.35 | 9% | 66% |
| KATL | low | 2458 | -1.77 | 2.15 | 1.97 | 12% | 49% |
| KAUS | high | 2462 | -1.63 | 2.55 | 2.68 | 10% | 57% |
| KAUS | low | 2462 | +4.04 | 4.45 | 3.94 | 8% | 70% |
| KBOS | high | 2459 | -1.03 | 2.09 | 2.46 | 14% | 45% |
| KBOS | low | 2459 | -0.90 | 1.96 | 2.36 | 16% | 42% |
| KDCA | high | 2454 | -2.00 | 2.61 | 2.44 | 10% | 59% |
| KDCA | low | 2454 | -2.45 | 2.76 | 2.23 | 10% | 62% |
| KDEN | high | 2462 | -1.83 | 2.86 | 3.12 | 9% | 60% |
| KDEN | low | 2462 | +2.64 | 3.59 | 3.8 | 10% | 64% |
| KDFW | high | 2458 | -1.17 | 2.27 | 2.61 | 15% | 50% |
| KDFW | low | 2458 | +0.55 | 1.64 | 2.12 | 21% | 32% |
| KHOU | high | 2458 | -3.01 | 3.31 | 2.44 | 7% | 72% |
| KHOU | low | 2458 | -1.21 | 1.90 | 2.05 | 16% | 41% |
| KLAS | high | 2094 | -0.42 | 1.22 | 1.6 | 30% | 20% |
| KLAS | low | 2094 | -2.08 | 2.65 | 2.47 | 10% | 60% |
| KLAX | high | 2460 | -1.27 | 2.26 | 2.58 | 13% | 48% |
| KLAX | low | 2460 | -1.18 | 1.77 | 1.96 | 19% | 35% |
| KMDW | high | 2461 | -1.76 | 2.31 | 2.21 | 11% | 53% |
| KMDW | low | 2461 | -2.52 | 2.89 | 2.53 | 10% | 61% |
| KMIA | high | 2452 | -2.26 | 2.48 | 1.84 | 9% | 59% |
| KMIA | low | 2452 | -2.15 | 2.59 | 2.24 | 10% | 58% |
| KMSP | high | 2462 | -1.25 | 2.15 | 2.41 | 15% | 47% |
| KMSP | low | 2462 | -1.61 | 2.35 | 2.65 | 15% | 47% |
| KNYC | high | 2460 | -0.87 | 1.97 | 2.38 | 17% | 42% |
| KNYC | low | 2460 | -2.53 | 3.09 | 3.15 | 11% | 59% |
| KPHL | high | 2462 | -1.10 | 1.92 | 2.16 | 16% | 42% |
| KPHL | low | 2462 | -1.47 | 2.16 | 2.34 | 15% | 47% |
| KPHX | high | 2458 | -2.23 | 2.37 | 1.78 | 9% | 55% |
| KPHX | low | 2458 | -2.86 | 3.20 | 2.48 | 7% | 70% |
| KSAT | high | 1729 | -1.92 | 2.57 | 2.43 | 11% | 59% |
| KSAT | low | 1731 | -0.07 | 2.05 | 2.65 | 14% | 43% |
| KSEA | high | 2458 | -1.63 | 2.50 | 2.67 | 11% | 54% |
| KSEA | low | 2457 | -1.11 | 1.72 | 1.91 | 18% | 35% |
| KSFO | high | 2448 | -1.22 | 2.53 | 2.89 | 12% | 57% |
| KSFO | low | 2455 | -1.24 | 1.82 | 1.87 | 16% | 40% |

Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`.
