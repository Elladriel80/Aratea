# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit

Période / span : 2020-01-01 → 2026-10-04. Généré / generated : 2026-10-05T13:20:01Z.

FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.

EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means the model has been learning to correct the wrong target.

| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |
|---|---|---|---|---|---|---|---|
| KATL | high | 2466 | -2.34 | 2.82 | 2.35 | 9% | 66% |
| KATL | low | 2465 | -1.77 | 2.14 | 1.97 | 12% | 49% |
| KAUS | high | 2469 | -1.63 | 2.55 | 2.68 | 10% | 57% |
| KAUS | low | 2469 | +4.03 | 4.44 | 3.94 | 8% | 70% |
| KBOS | high | 2466 | -1.03 | 2.09 | 2.46 | 14% | 44% |
| KBOS | low | 2466 | -0.90 | 1.96 | 2.36 | 16% | 42% |
| KDCA | high | 1730 | -1.96 | 2.63 | 2.54 | 10% | 58% |
| KDCA | low | 1730 | -2.51 | 2.83 | 2.31 | 10% | 63% |
| KDEN | high | 2469 | -1.83 | 2.86 | 3.12 | 9% | 60% |
| KDEN | low | 2469 | +2.64 | 3.59 | 3.8 | 10% | 64% |
| KDFW | high | 2465 | -1.17 | 2.26 | 2.6 | 15% | 50% |
| KDFW | low | 2465 | +0.55 | 1.64 | 2.13 | 21% | 32% |
| KHOU | high | 2465 | -3.00 | 3.31 | 2.44 | 7% | 72% |
| KHOU | low | 2465 | -1.21 | 1.90 | 2.05 | 16% | 41% |
| KLAS | high | 2467 | -0.49 | 1.23 | 1.57 | 29% | 20% |
| KLAS | low | 2466 | -2.07 | 2.65 | 2.46 | 9% | 60% |
| KLAX | high | 2467 | -1.27 | 2.26 | 2.58 | 13% | 48% |
| KLAX | low | 2467 | -1.18 | 1.77 | 1.96 | 19% | 35% |
| KMDW | high | 2468 | -1.76 | 2.31 | 2.21 | 11% | 53% |
| KMDW | low | 2468 | -2.52 | 2.88 | 2.53 | 10% | 61% |
| KMIA | high | 2459 | -2.26 | 2.47 | 1.84 | 9% | 59% |
| KMIA | low | 2459 | -2.15 | 2.59 | 2.25 | 10% | 58% |
| KMSP | high | 2103 | -1.34 | 2.19 | 2.42 | 15% | 48% |
| KMSP | low | 2103 | -1.60 | 2.32 | 2.59 | 15% | 48% |
| KNYC | high | 2467 | -0.87 | 1.97 | 2.38 | 17% | 42% |
| KNYC | low | 2467 | -2.53 | 3.09 | 3.15 | 11% | 59% |
| KPHL | high | 2469 | -1.11 | 1.92 | 2.15 | 16% | 43% |
| KPHL | low | 2469 | -1.47 | 2.16 | 2.34 | 15% | 47% |
| KPHX | high | 2465 | -2.23 | 2.37 | 1.79 | 9% | 55% |
| KPHX | low | 2465 | -2.86 | 3.20 | 2.48 | 7% | 70% |
| KSAT | high | 2467 | -2.01 | 2.67 | 2.55 | 11% | 60% |
| KSAT | low | 2469 | +0.14 | 2.04 | 2.65 | 14% | 42% |
| KSEA | high | 2465 | -1.63 | 2.49 | 2.67 | 11% | 54% |
| KSEA | low | 2464 | -1.11 | 1.72 | 1.91 | 18% | 35% |
| KSFO | high | 2455 | -1.20 | 2.54 | 2.91 | 12% | 57% |
| KSFO | low | 2462 | -1.24 | 1.82 | 1.87 | 16% | 40% |

Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`.
