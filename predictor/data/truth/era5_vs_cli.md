# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit

Période / span : 2020-01-01 → 2026-10-25. Généré / generated : 2026-10-26T12:06:13Z.

FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.

EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means the model has been learning to correct the wrong target.

| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |
|---|---|---|---|---|---|---|---|
| KATL | high | 2487 | -2.26 | 2.77 | 2.35 | 9% | 65% |
| KATL | low | 2486 | -1.98 | 2.20 | 1.84 | 11% | 50% |
| KAUS | high | 2490 | -1.55 | 2.52 | 2.68 | 11% | 56% |
| KAUS | low | 2490 | +3.83 | 4.28 | 3.88 | 9% | 69% |
| KBOS | high | 2487 | -0.95 | 2.06 | 2.45 | 15% | 44% |
| KBOS | low | 2487 | -1.16 | 1.98 | 2.28 | 16% | 41% |
| KDCA | high | 2482 | -1.92 | 2.56 | 2.44 | 10% | 58% |
| KDCA | low | 2482 | -2.67 | 2.87 | 2.11 | 9% | 65% |
| KDEN | high | 2490 | -1.71 | 2.79 | 3.12 | 11% | 59% |
| KDEN | low | 2490 | +2.37 | 3.42 | 3.72 | 11% | 62% |
| KDFW | high | 2486 | -1.10 | 2.24 | 2.61 | 15% | 49% |
| KDFW | low | 2486 | +0.34 | 1.54 | 2.02 | 23% | 29% |
| KHOU | high | 2486 | -2.92 | 3.24 | 2.44 | 7% | 71% |
| KHOU | low | 2486 | -1.40 | 1.92 | 1.96 | 16% | 42% |
| KLAS | high | 1392 | -0.25 | 1.20 | 1.63 | 31% | 20% |
| KLAS | low | 1392 | -2.45 | 2.78 | 2.23 | 8% | 63% |
| KLAX | high | 2488 | -1.22 | 2.24 | 2.57 | 14% | 48% |
| KLAX | low | 2488 | -1.30 | 1.83 | 1.96 | 18% | 37% |
| KMDW | high | 2489 | -1.69 | 2.27 | 2.2 | 12% | 51% |
| KMDW | low | 2489 | -2.81 | 3.03 | 2.43 | 9% | 64% |
| KMIA | high | 2480 | -2.19 | 2.42 | 1.83 | 9% | 58% |
| KMIA | low | 2480 | -2.33 | 2.68 | 2.2 | 9% | 61% |
| KMSP | high | 2490 | -1.18 | 2.11 | 2.41 | 15% | 45% |
| KMSP | low | 2490 | -1.88 | 2.38 | 2.54 | 16% | 48% |
| KNYC | high | 2488 | -0.79 | 1.94 | 2.37 | 17% | 41% |
| KNYC | low | 2488 | -2.76 | 3.16 | 3.04 | 11% | 60% |
| KPHL | high | 2490 | -1.05 | 1.89 | 2.15 | 16% | 42% |
| KPHL | low | 2490 | -1.74 | 2.20 | 2.2 | 15% | 48% |
| KPHX | high | 2486 | -2.16 | 2.32 | 1.8 | 10% | 53% |
| KPHX | low | 2486 | -3.00 | 3.30 | 2.46 | 6% | 71% |
| KSAT | high | 2488 | -1.93 | 2.62 | 2.55 | 11% | 59% |
| KSAT | low | 2490 | -0.06 | 1.95 | 2.51 | 16% | 41% |
| KSEA | high | 2486 | -1.56 | 2.46 | 2.68 | 12% | 53% |
| KSEA | low | 2485 | -1.28 | 1.80 | 1.9 | 17% | 37% |
| KSFO | high | 2110 | -1.15 | 2.51 | 2.89 | 12% | 57% |
| KSFO | low | 2117 | -1.47 | 1.93 | 1.86 | 16% | 44% |

Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`.
