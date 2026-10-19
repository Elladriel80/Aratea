# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit

Période / span : 2020-01-01 → 2026-10-18. Généré / generated : 2026-10-19T11:50:37Z.

FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.

EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means the model has been learning to correct the wrong target.

| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |
|---|---|---|---|---|---|---|---|
| KATL | high | 2480 | -2.26 | 2.77 | 2.35 | 9% | 65% |
| KATL | low | 2479 | -1.98 | 2.20 | 1.84 | 11% | 50% |
| KAUS | high | 2483 | -1.55 | 2.52 | 2.68 | 11% | 56% |
| KAUS | low | 2483 | +3.83 | 4.28 | 3.89 | 9% | 68% |
| KBOS | high | 2480 | -0.96 | 2.06 | 2.46 | 15% | 44% |
| KBOS | low | 2480 | -1.15 | 1.98 | 2.28 | 16% | 41% |
| KDCA | high | 2475 | -1.92 | 2.56 | 2.45 | 10% | 58% |
| KDCA | low | 2475 | -2.67 | 2.87 | 2.11 | 9% | 65% |
| KDEN | high | 2483 | -1.71 | 2.79 | 3.12 | 11% | 59% |
| KDEN | low | 2483 | +2.38 | 3.42 | 3.72 | 11% | 62% |
| KDFW | high | 2479 | -1.10 | 2.24 | 2.61 | 15% | 49% |
| KDFW | low | 2479 | +0.34 | 1.54 | 2.02 | 23% | 29% |
| KHOU | high | 2479 | -2.92 | 3.25 | 2.44 | 7% | 71% |
| KHOU | low | 2479 | -1.40 | 1.92 | 1.96 | 16% | 42% |
| KLAS | high | 2481 | -0.43 | 1.21 | 1.57 | 29% | 19% |
| KLAS | low | 2480 | -2.25 | 2.73 | 2.39 | 9% | 62% |
| KLAX | high | 2481 | -1.21 | 2.23 | 2.58 | 14% | 48% |
| KLAX | low | 2481 | -1.30 | 1.82 | 1.96 | 18% | 37% |
| KMDW | high | 2482 | -1.69 | 2.27 | 2.21 | 12% | 51% |
| KMDW | low | 2482 | -2.80 | 3.02 | 2.43 | 9% | 64% |
| KMIA | high | 2473 | -2.19 | 2.42 | 1.83 | 9% | 58% |
| KMIA | low | 2473 | -2.33 | 2.68 | 2.2 | 9% | 61% |
| KMSP | high | 1752 | -1.26 | 2.14 | 2.43 | 15% | 46% |
| KMSP | low | 1752 | -1.89 | 2.36 | 2.43 | 15% | 50% |
| KNYC | high | 2481 | -0.79 | 1.94 | 2.37 | 17% | 42% |
| KNYC | low | 2481 | -2.76 | 3.16 | 3.05 | 11% | 60% |
| KPHL | high | 2483 | -1.05 | 1.89 | 2.15 | 16% | 42% |
| KPHL | low | 2483 | -1.74 | 2.21 | 2.2 | 15% | 48% |
| KPHX | high | 2479 | -2.15 | 2.31 | 1.79 | 10% | 53% |
| KPHX | low | 2479 | -2.99 | 3.30 | 2.46 | 6% | 71% |
| KSAT | high | 2481 | -1.93 | 2.62 | 2.55 | 11% | 59% |
| KSAT | low | 2483 | -0.06 | 1.96 | 2.51 | 16% | 42% |
| KSEA | high | 2479 | -1.56 | 2.47 | 2.68 | 12% | 53% |
| KSEA | low | 2478 | -1.28 | 1.80 | 1.9 | 17% | 37% |
| KSFO | high | 2469 | -1.12 | 2.53 | 2.94 | 12% | 57% |
| KSFO | low | 2476 | -1.37 | 1.88 | 1.88 | 16% | 43% |

Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`.
