# ERA5 vs CLI — audit de la vérité terrain / ground-truth audit

Période / span : 2020-01-01 → 2026-10-11. Généré / generated : 2026-10-12T14:10:10Z.

FR : ERA5 est ce que la climatologie du predictor a utilisé comme « observation ». CLI est ce qui résout les marchés Kalshi. Un biais non nul ou une part de jours à ≥ 2 °F d'écart élevée signifie que le modèle apprend à corriger la mauvaise cible.

EN : ERA5 is what the predictor's climatology has used as 'observation'. CLI is what settles Kalshi markets. A non-zero bias or a high share of days off by ≥ 2 °F means the model has been learning to correct the wrong target.

| Station | Var | n | biais ERA5−CLI (°F) | MAE (°F) | sd (°F) | jours exacts | ≥ 2 °F |
|---|---|---|---|---|---|---|---|
| KATL | high | 2473 | -2.33 | 2.82 | 2.35 | 9% | 66% |
| KATL | low | 2472 | -1.76 | 2.14 | 1.97 | 12% | 49% |
| KAUS | high | 2476 | -1.63 | 2.56 | 2.68 | 10% | 57% |
| KAUS | low | 2476 | +4.03 | 4.44 | 3.94 | 8% | 70% |
| KBOS | high | 2473 | -1.03 | 2.09 | 2.46 | 14% | 44% |
| KBOS | low | 2473 | -0.90 | 1.96 | 2.36 | 16% | 41% |
| KDCA | high | 2468 | -1.99 | 2.60 | 2.44 | 10% | 59% |
| KDCA | low | 2468 | -2.44 | 2.75 | 2.22 | 10% | 62% |
| KDEN | high | 2476 | -1.82 | 2.85 | 3.11 | 9% | 60% |
| KDEN | low | 2476 | +2.63 | 3.58 | 3.79 | 10% | 64% |
| KDFW | high | 2472 | -1.18 | 2.27 | 2.6 | 15% | 50% |
| KDFW | low | 2472 | +0.54 | 1.64 | 2.12 | 21% | 32% |
| KHOU | high | 2472 | -3.00 | 3.30 | 2.43 | 7% | 72% |
| KHOU | low | 2472 | -1.21 | 1.90 | 2.05 | 16% | 41% |
| KLAS | high | 2474 | -0.49 | 1.23 | 1.57 | 29% | 20% |
| KLAS | low | 2473 | -2.06 | 2.64 | 2.45 | 9% | 60% |
| KLAX | high | 2474 | -1.27 | 2.25 | 2.57 | 13% | 48% |
| KLAX | low | 2474 | -1.17 | 1.77 | 1.96 | 19% | 35% |
| KMDW | high | 2475 | -1.76 | 2.31 | 2.2 | 11% | 53% |
| KMDW | low | 2475 | -2.52 | 2.88 | 2.53 | 10% | 61% |
| KMIA | high | 2100 | -2.16 | 2.38 | 1.82 | 10% | 57% |
| KMIA | low | 2100 | -2.17 | 2.60 | 2.23 | 10% | 58% |
| KMSP | high | 2476 | -1.25 | 2.14 | 2.41 | 15% | 47% |
| KMSP | low | 2476 | -1.61 | 2.35 | 2.65 | 15% | 47% |
| KNYC | high | 2474 | -0.87 | 1.97 | 2.38 | 17% | 42% |
| KNYC | low | 2474 | -2.52 | 3.08 | 3.15 | 11% | 59% |
| KPHL | high | 2476 | -1.11 | 1.92 | 2.15 | 16% | 43% |
| KPHL | low | 2476 | -1.47 | 2.16 | 2.34 | 15% | 47% |
| KPHX | high | 2472 | -2.23 | 2.37 | 1.79 | 9% | 55% |
| KPHX | low | 2472 | -2.85 | 3.19 | 2.47 | 7% | 70% |
| KSAT | high | 2474 | -2.01 | 2.67 | 2.55 | 11% | 60% |
| KSAT | low | 2476 | +0.14 | 2.04 | 2.65 | 15% | 42% |
| KSEA | high | 2106 | -1.43 | 2.35 | 2.57 | 13% | 51% |
| KSEA | low | 2105 | -1.06 | 1.69 | 1.9 | 19% | 34% |
| KSFO | high | 2462 | -1.19 | 2.54 | 2.92 | 12% | 58% |
| KSFO | low | 2469 | -1.23 | 1.82 | 1.87 | 16% | 40% |

Détail mensuel dans `era5_vs_cli.json` / monthly detail in `era5_vs_cli.json`.
