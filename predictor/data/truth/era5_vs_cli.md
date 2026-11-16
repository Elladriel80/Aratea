# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit

Période / span : 2020-01-01 → 2026-11-15. Généré / generated : 2026-11-16T14:32:15Z.

FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.

EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means the model has been learning to correct the wrong target.

| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |
|---|---|---|---|---|---|---|---|
| KATL | high | 2508 | -2.28 | 2.78 | 2.33 | 9% | 66% |
| KATL | low | 2507 | -2.15 | 2.30 | 1.77 | 10% | 53% |
| KAUS | high | 2511 | -1.57 | 2.51 | 2.66 | 10% | 56% |
| KAUS | low | 2511 | +3.66 | 4.15 | 3.85 | 10% | 67% |
| KBOS | high | 2508 | -1.01 | 2.07 | 2.43 | 15% | 44% |
| KBOS | low | 2508 | -1.36 | 2.07 | 2.25 | 15% | 44% |
| KDCA | high | 2503 | -1.96 | 2.59 | 2.44 | 10% | 59% |
| KDCA | low | 2503 | -2.85 | 3.00 | 2.06 | 7% | 68% |
| KDEN | high | 2511 | -1.73 | 2.76 | 3.07 | 11% | 58% |
| KDEN | low | 2511 | +2.23 | 3.30 | 3.66 | 11% | 60% |
| KDFW | high | 2507 | -1.15 | 2.23 | 2.57 | 15% | 48% |
| KDFW | low | 2507 | +0.18 | 1.47 | 1.95 | 24% | 27% |
| KHOU | high | 2507 | -2.94 | 3.25 | 2.43 | 8% | 72% |
| KHOU | low | 2507 | -1.51 | 1.96 | 1.93 | 15% | 43% |
| KLAS | high | 2509 | -0.44 | 1.21 | 1.57 | 29% | 19% |
| KLAS | low | 2508 | -2.34 | 2.76 | 2.34 | 9% | 63% |
| KLAX | high | 2509 | -1.22 | 2.23 | 2.57 | 14% | 48% |
| KLAX | low | 2509 | -1.38 | 1.86 | 1.97 | 18% | 38% |
| KMDW | high | 2510 | -1.75 | 2.28 | 2.17 | 11% | 51% |
| KMDW | low | 2510 | -3.01 | 3.15 | 2.35 | 8% | 66% |
| KMIA | high | 2501 | -2.20 | 2.41 | 1.82 | 9% | 58% |
| KMIA | low | 2501 | -2.42 | 2.73 | 2.17 | 9% | 62% |
| KMSP | high | 2511 | -1.24 | 2.12 | 2.38 | 15% | 46% |
| KMSP | low | 2511 | -2.08 | 2.47 | 2.48 | 15% | 51% |
| KNYC | high | 2509 | -0.82 | 1.94 | 2.35 | 17% | 41% |
| KNYC | low | 2509 | -2.95 | 3.28 | 2.96 | 10% | 63% |
| KPHL | high | 2511 | -1.07 | 1.91 | 2.14 | 16% | 42% |
| KPHL | low | 2511 | -1.94 | 2.33 | 2.15 | 12% | 52% |
| KPHX | high | 2507 | -2.17 | 2.32 | 1.8 | 10% | 54% |
| KPHX | low | 2507 | -2.99 | 3.30 | 2.45 | 6% | 71% |
| KSAT | high | 2509 | -1.95 | 2.62 | 2.52 | 10% | 59% |
| KSAT | low | 2511 | -0.20 | 1.91 | 2.43 | 16% | 40% |
| KSEA | high | 2507 | -1.56 | 2.46 | 2.67 | 12% | 53% |
| KSEA | low | 2506 | -1.40 | 1.87 | 1.91 | 16% | 39% |
| KSFO | high | 2497 | -1.11 | 2.52 | 2.93 | 12% | 57% |
| KSFO | low | 2504 | -1.43 | 1.93 | 1.87 | 15% | 44% |

Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`.
