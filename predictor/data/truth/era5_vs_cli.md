# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit

Période / span : 2020-01-01 → 2026-11-22. Généré / generated : 2026-11-23T17:06:33Z.

FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.

EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means the model has been learning to correct the wrong target.

| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |
|---|---|---|---|---|---|---|---|
| KATL | high | 2515 | -2.28 | 2.78 | 2.33 | 9% | 66% |
| KATL | low | 2514 | -2.14 | 2.30 | 1.77 | 10% | 53% |
| KAUS | high | 2518 | -1.57 | 2.51 | 2.66 | 10% | 56% |
| KAUS | low | 2518 | +3.66 | 4.15 | 3.85 | 10% | 67% |
| KBOS | high | 2515 | -1.01 | 2.07 | 2.42 | 15% | 44% |
| KBOS | low | 2515 | -1.37 | 2.07 | 2.25 | 15% | 44% |
| KDCA | high | 2510 | -1.96 | 2.59 | 2.44 | 10% | 59% |
| KDCA | low | 2510 | -2.85 | 3.00 | 2.06 | 7% | 68% |
| KDEN | high | 2518 | -1.72 | 2.76 | 3.07 | 11% | 58% |
| KDEN | low | 2518 | +2.24 | 3.30 | 3.66 | 11% | 60% |
| KDFW | high | 2514 | -1.16 | 2.23 | 2.57 | 15% | 49% |
| KDFW | low | 2514 | +0.18 | 1.47 | 1.95 | 24% | 27% |
| KHOU | high | 2514 | -2.94 | 3.25 | 2.43 | 7% | 71% |
| KHOU | low | 2514 | -1.51 | 1.96 | 1.93 | 15% | 43% |
| KLAS | high | 2516 | -0.44 | 1.21 | 1.58 | 29% | 19% |
| KLAS | low | 2515 | -2.34 | 2.76 | 2.33 | 8% | 63% |
| KLAX | high | 2516 | -1.22 | 2.23 | 2.56 | 14% | 48% |
| KLAX | low | 2516 | -1.37 | 1.86 | 1.97 | 18% | 38% |
| KMDW | high | 2517 | -1.75 | 2.28 | 2.16 | 11% | 52% |
| KMDW | low | 2517 | -3.01 | 3.15 | 2.35 | 8% | 66% |
| KMIA | high | 2508 | -2.19 | 2.41 | 1.82 | 9% | 57% |
| KMIA | low | 2508 | -2.42 | 2.73 | 2.16 | 9% | 62% |
| KMSP | high | 2518 | -1.24 | 2.11 | 2.37 | 15% | 46% |
| KMSP | low | 2518 | -2.08 | 2.47 | 2.48 | 15% | 51% |
| KNYC | high | 2516 | -0.82 | 1.93 | 2.35 | 17% | 41% |
| KNYC | low | 2516 | -2.96 | 3.28 | 2.96 | 10% | 63% |
| KPHL | high | 2518 | -1.08 | 1.91 | 2.14 | 16% | 42% |
| KPHL | low | 2518 | -1.94 | 2.32 | 2.15 | 12% | 52% |
| KPHX | high | 2514 | -2.17 | 2.33 | 1.8 | 10% | 54% |
| KPHX | low | 2514 | -2.99 | 3.29 | 2.45 | 6% | 71% |
| KSAT | high | 2516 | -1.95 | 2.62 | 2.52 | 10% | 59% |
| KSAT | low | 2518 | -0.20 | 1.91 | 2.43 | 15% | 40% |
| KSEA | high | 2514 | -1.56 | 2.46 | 2.67 | 12% | 53% |
| KSEA | low | 2513 | -1.40 | 1.87 | 1.91 | 16% | 39% |
| KSFO | high | 2504 | -1.11 | 2.51 | 2.93 | 12% | 57% |
| KSFO | low | 2511 | -1.43 | 1.92 | 1.88 | 15% | 44% |

Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`.
