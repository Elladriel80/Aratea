# MED robustness: ECMWF-51 vs C3S mix on CHIRPS MED (2026-11-24)

Offline. No CDS call, no new data. Code: PR 260, branch `cursor/c3s-multimodel-ab-59e8` @ 973a4ab (not merged; modules `src.forecast.c3s_offline` and `src.score.c3s_ab` are not on main). Functions reused: `load_c3s_csv`, `aggregate_equal_weight`, `filter_window`, `collapse_shortest_lead`, `_load_chirps_truth`, `skill_block`. Script: `predictor/scripts/med_robustness.py`.

## How the 7 Oct headline is built (read from code)

- Forecast: for each target month, keep the **shortest lead** (lead 1 = forecast issued on the 1st of that same month). Season = mean of 3 months (DJF/MAM/JJA/SON), so each season mixes 3 different start dates.
- Forecast probability is **0 or 1**: 1 if the forecast season total is below the leave-one-out mean of forecast seasons (same season type).
- Event: CHIRPS season total below its leave-one-out mean (same season type, CHIRPS 1981-2024).
- Reference: leave-one-out base rate of the scored events. BSS = 1 - Brier_fc / Brier_clim.
- Reproduced exactly: ECMWF-51 BSS 0.0629 (N 97), mix -0.0593 (N 97).

## Columns

- CI95: bootstrap over years (2000 resamples, seasons of one year kept together).
- LOYO: min/max BSS when one year is left out.
- p_perm: permutation p-value vs a forecast with no link to the outcome (shuffle years within season). Note: a random 0/1 forecast scores BSS near -1, so p_perm tests 'any information', not 'better than climatology'.
- luck: chance of BSS > 0.05 by luck if the true skill were exactly climatology (bootstrap recentred on 0).
- cal_cv: BSS after turning the 0/1 forecast into honest probabilities (event rate in other years given the same forecast). Reliability check.
- yes / no: observed event rate when the forecast said 'dry' / 'not dry'.

| Arm | Group | Slice | N | BSS | CI95 | LOYO | p_perm | luck | cal_cv | yes | no | gate |
|---|---|---|---:|---:|---|---|---:|---:|---:|---:|---:|---|
| ecmwf51 | headline | MED toutes saisons, delai court | 97 | 0.0629 | [-0.2883, 0.4159] | [0.0182, 0.1534] | 0.0 | 0.39 | 0.2647 | 0.714 | 0.188 | PASS |
| ecmwf51 | saison | DJF | 24 | 0.3877 | [-0.2595, 0.8469] | [0.3623, 0.5217] | 0.001 | 0.425 | 0.4115 | 0.786 | 0.1 | PASS |
| ecmwf51 | saison | MAM | 25 | 0.4016 | [-0.28, 0.8523] | [0.3702, 0.5376] | 0.002 | 0.403 | 0.4316 | 0.769 | 0.083 | PASS |
| ecmwf51 | saison | JJA | 24 | -0.2595 | [-1.408, 0.3834] | [-0.3361, -0.1331] | 0.081 | 0.506 | 0.063 | 0.8 | 0.429 |  |
| ecmwf51 | saison | SON | 24 | -0.2966 | [-2.1488, 0.5102] | [-0.4442, -0.1273] | 0.03 | 0.571 | 0.1366 | 0.5 | 0.083 |  |
| ecmwf51 | delai_mois | delai 1 (chaque mois prevu 0 mois avant) | 95 | 0.039 | [-0.3471, 0.3856] | [-0.0095, 0.1316] | 0.0 | 0.399 | 0.2525 | 0.702 | 0.188 |  |
| ecmwf51 | delai_mois | delai 2 (chaque mois prevu 1 mois avant) | 95 | -0.7549 | [-1.1576, -0.3863] | [-0.8434, -0.658] | 0.145 | 0.411 | -0.0086 | 0.5 | 0.388 |  |
| ecmwf51 | delai_mois | delai 3 (chaque mois prevu 2 mois avant) | 96 | -1.0213 | [-1.4126, -0.6882] | [-1.0772, -0.9371] | 0.661 | 0.397 | -0.0211 | 0.44 | 0.457 |  |
| ecmwf51 | delai_mois | delai 4 (chaque mois prevu 3 mois avant) | 95 | -1.0798 | [-1.4821, -0.7223] | [-1.1816, -0.9973] | 0.799 | 0.397 | -0.0187 | 0.426 | 0.479 |  |
| ecmwf51 | delai_mois | delai 5 (chaque mois prevu 4 mois avant) | 95 | -0.8303 | [-1.2688, -0.4685] | [-0.9198, -0.7368] | 0.334 | 0.419 | -0.0148 | 0.49 | 0.409 |  |
| ecmwf51 | delai_mois | delai 6 (chaque mois prevu 5 mois avant) | 96 | -0.9312 | [-1.2513, -0.5994] | [-1.0232, -0.8797] | 0.593 | 0.389 | -0.0212 | 0.467 | 0.451 |  |
| ecmwf51 | vraie_saison | une prevision par saison, lancee 0 mois avant | 96 | -0.4025 | [-0.827, 0.0081] | [-0.4713, -0.3287] | 0.001 | 0.407 | 0.0745 | 0.585 | 0.279 |  |
| ecmwf51 | vraie_saison_x_saison | lancee 0 mois avant, DJF | 24 | 0.5408 | [-0.0715, 1.0] | [0.5217, 0.6812] | 0.0 | 0.386 | 0.5276 | 0.846 | 0.091 | PASS |
| ecmwf51 | vraie_saison_x_saison | lancee 0 mois avant, MAM | 24 | -0.417 | [-1.4797, 0.2293] | [-0.5031, -0.295] | 0.181 | 0.492 | -0.0126 | 0.538 | 0.273 |  |
| ecmwf51 | vraie_saison_x_saison | lancee 0 mois avant, JJA | 24 | -0.7318 | [-1.7757, -0.0715] | [-0.8371, -0.6187] | 0.543 | 0.461 | -0.0881 | 0.615 | 0.545 |  |
| ecmwf51 | vraie_saison_x_saison | lancee 0 mois avant, SON | 24 | -1.0375 | [-3.5506, -0.0332] | [-1.2694, -0.8789] | 0.354 | 0.576 | -0.0564 | 0.357 | 0.2 |  |
| ecmwf51 | vraie_saison | une prevision par saison, lancee 1 mois avant | 96 | -1.0625 | [-1.4417, -0.7104] | [-1.1637, -0.9906] | 0.712 | 0.402 | -0.0204 | 0.434 | 0.465 |  |
| ecmwf51 | vraie_saison_x_saison | lancee 1 mois avant, DJF | 24 | -0.5307 | [-1.4491, 0.1836] | [-0.5942, -0.4348] | 0.344 | 0.483 | -0.0626 | 0.583 | 0.417 |  |
| ecmwf51 | vraie_saison_x_saison | lancee 1 mois avant, MAM | 24 | -0.8893 | [-2.0613, -0.1429] | [-1.0041, -0.7806] | 0.663 | 0.475 | -0.093 | 0.417 | 0.417 |  |
| ecmwf51 | vraie_saison_x_saison | lancee 1 mois avant, JJA | 24 | -1.0467 | [-2.0613, -0.3062] | [-1.1712, -0.9425] | 0.871 | 0.453 | -0.0733 | 0.533 | 0.667 |  |
| ecmwf51 | vraie_saison_x_saison | lancee 1 mois avant, SON | 24 | -1.7784 | [-4.9478, -0.722] | [-2.0946, -1.6304] | 0.931 | 0.596 | -0.0552 | 0.214 | 0.4 |  |
| ecmwf51 | vraie_saison | une prevision par saison, lancee 2 mois avant | 96 | -1.31 | [-1.7297, -0.9053] | [-1.4106, -1.2288] | 0.963 | 0.409 | 0.0065 | 0.367 | 0.532 |  |
| ecmwf51 | vraie_saison | une prevision par saison, lancee 3 mois avant | 96 | -0.8079 | [-1.285, -0.3488] | [-0.8941, -0.7515] | 0.327 | 0.409 | -0.0129 | 0.5 | 0.409 |  |
| ecmwf51 | seuil | tres sec: sous le 20e centile | 97 | -0.5424 | [-1.0469, -0.1335] | [-0.6183, -0.4241] | 0.014 | 0.428 | 0.0369 | 0.391 | 0.149 |  |
| ecmwf51 | seuil | sec: tiers le plus sec | 97 | -0.4936 | [-0.8828, -0.099] | [-0.5502, -0.4002] | 0.007 | 0.395 | 0.0535 | 0.471 | 0.206 |  |
| ecmwf51 | seuil | sous la mediane | 97 | -0.0418 | [-0.4011, 0.2707] | [-0.0981, 0.0493] | 0.0 | 0.395 | 0.2281 | 0.653 | 0.167 |  |
| ecmwf51 | seuil | humide: tiers le plus humide | 97 | -0.2828 | [-0.7227, 0.1221] | [-0.3499, -0.202] | 0.001 | 0.421 | 0.0919 | 0.647 | 0.302 |  |
| ecmwf51 | seuil | tres humide: au-dessus du 80e centile | 97 | 0.0165 | [-0.3427, 0.3259] | [-0.0449, 0.1118] | 0.0 | 0.401 | 0.1929 | 0.7 | 0.182 |  |
| ecmwf51 | moitie | 1993-2004 | 47 | -0.146 | [-0.7465, 0.4229] | [-0.2595, 0.0233] | 0.003 | 0.43 | 0.1236 | 0.682 | 0.28 |  |
| ecmwf51 | moitie | 2005-2017 | 50 | 0.2984 | [-0.0826, 0.6739] | [0.2277, 0.4074] | 0.0 | 0.4 | 0.4085 | 0.741 | 0.087 | PASS |
| mix | headline | MED toutes saisons, delai court | 97 | -0.0593 | [-0.4325, 0.2606] | [-0.1099, 0.0228] | 0.0 | 0.396 | 0.2036 | 0.68 | 0.213 |  |
| mix | saison | DJF | 24 | 0.6939 | [0.2128, 1.0] | [0.6812, 0.8406] | 0.0 | 0.388 | 0.6957 | 0.857 | 0.0 | PASS |
| mix | saison | MAM | 25 | 0.1023 | [-0.6457, 0.7008] | [0.0554, 0.2293] | 0.011 | 0.401 | 0.196 | 0.727 | 0.214 | PASS |
| mix | saison | JJA | 24 | -0.1021 | [-1.0664, 0.5376] | [-0.1691, 0.0288] | 0.036 | 0.516 | 0.1197 | 0.818 | 0.385 |  |
| mix | saison | SON | 24 | -1.0375 | [-3.8981, -0.1111] | [-1.2694, -0.8789] | 0.353 | 0.575 | -0.0564 | 0.357 | 0.2 |  |
| mix | delai_mois | delai 1 (chaque mois prevu 0 mois avant) | 95 | -0.0446 | [-0.4155, 0.2985] | [-0.0973, 0.0401] | 0.0 | 0.39 | 0.2147 | 0.673 | 0.196 |  |
| mix | delai_mois | delai 2 (chaque mois prevu 1 mois avant) | 95 | -0.7549 | [-1.1489, -0.4025] | [-0.8434, -0.6788] | 0.109 | 0.386 | -0.0047 | 0.5 | 0.372 |  |
| mix | delai_mois | delai 3 (chaque mois prevu 2 mois avant) | 96 | -0.98 | [-1.3677, -0.6132] | [-1.0772, -0.8941] | 0.545 | 0.402 | -0.0213 | 0.451 | 0.444 |  |
| mix | delai_mois | delai 4 (chaque mois prevu 3 mois avant) | 95 | -0.7471 | [-1.0988, -0.3984] | [-0.8326, -0.6868] | 0.214 | 0.394 | -0.008 | 0.511 | 0.396 |  |
| mix | delai_mois | delai 5 (chaque mois prevu 4 mois avant) | 95 | -0.8719 | [-1.186, -0.535] | [-0.9635, -0.8236] | 0.371 | 0.379 | -0.0191 | 0.478 | 0.429 |  |
| mix | delai_mois | delai 6 (chaque mois prevu 5 mois avant) | 96 | -0.8079 | [-1.1107, -0.5241] | [-0.8941, -0.7515] | 0.283 | 0.383 | -0.0129 | 0.5 | 0.409 |  |
| mix | vraie_saison | une prevision par saison, lancee 0 mois avant | 96 | -0.2375 | [-0.62, 0.1181] | [-0.2982, -0.1623] | 0.001 | 0.415 | 0.1298 | 0.627 | 0.244 |  |
| mix | vraie_saison_x_saison | lancee 0 mois avant, DJF | 24 | 0.5408 | [-0.079, 1.0] | [0.5217, 0.6812] | 0.0 | 0.418 | 0.5276 | 0.846 | 0.091 | PASS |
| mix | vraie_saison_x_saison | lancee 0 mois avant, MAM | 24 | -0.417 | [-1.4108, 0.2591] | [-0.5031, -0.295] | 0.177 | 0.485 | -0.0126 | 0.538 | 0.273 |  |
| mix | vraie_saison_x_saison | lancee 0 mois avant, JJA | 24 | -0.5744 | [-1.4662, 0.0752] | [-0.6701, -0.4569] | 0.39 | 0.48 | -0.0728 | 0.643 | 0.5 |  |
| mix | vraie_saison_x_saison | lancee 0 mois avant, SON | 24 | -0.4818 | [-2.4987, 0.3469] | [-0.6505, -0.3152] | 0.121 | 0.542 | 0.0209 | 0.455 | 0.154 |  |
| mix | vraie_saison | une prevision par saison, lancee 1 mois avant | 96 | -0.815 | [-1.2831, -0.3743] | [-0.9041, -0.7219] | 0.245 | 0.417 | -0.012 | 0.491 | 0.395 |  |
| mix | vraie_saison_x_saison | lancee 1 mois avant, DJF | 24 | -0.5307 | [-1.4662, 0.2128] | [-0.5942, -0.4348] | 0.349 | 0.486 | -0.0622 | 0.571 | 0.4 |  |
| mix | vraie_saison_x_saison | lancee 1 mois avant, MAM | 24 | -0.7318 | [-1.8573, -0.0715] | [-0.8371, -0.6187] | 0.482 | 0.468 | -0.0819 | 0.462 | 0.364 |  |
| mix | vraie_saison_x_saison | lancee 1 mois avant, JJA | 24 | -0.7318 | [-1.7784, -0.0332] | [-0.8371, -0.6187] | 0.523 | 0.465 | -0.0881 | 0.615 | 0.545 |  |
| mix | vraie_saison_x_saison | lancee 1 mois avant, SON | 24 | -1.2227 | [-3.6892, -0.2956] | [-1.4757, -1.0668] | 0.609 | 0.585 | -0.091 | 0.308 | 0.273 |  |
| mix | vraie_saison | une prevision par saison, lancee 2 mois avant | 96 | -1.0213 | [-1.3673, -0.6836] | [-1.1204, -0.9717] | 0.69 | 0.382 | -0.0209 | 0.438 | 0.458 |  |
| mix | vraie_saison | une prevision par saison, lancee 3 mois avant | 96 | -0.849 | [-1.2003, -0.5195] | [-0.9371, -0.7942] | 0.282 | 0.394 | -0.0166 | 0.49 | 0.422 |  |
| mix | seuil | tres sec: sous le 20e centile | 97 | -0.3573 | [-0.7951, -0.0638] | [-0.4241, -0.2946] | 0.003 | 0.42 | 0.0814 | 0.455 | 0.133 |  |
| mix | seuil | sec: tiers le plus sec | 97 | -0.1563 | [-0.4484, 0.0956] | [-0.2001, -0.1001] | 0.0 | 0.36 | 0.1675 | 0.576 | 0.156 |  |
| mix | seuil | sous la mediane | 97 | -0.0835 | [-0.4451, 0.2257] | [-0.142, 0.0061] | 0.0 | 0.383 | 0.2038 | 0.646 | 0.184 |  |
| mix | seuil | humide: tiers le plus humide | 97 | -0.0345 | [-0.4256, 0.3234] | [-0.0886, 0.0555] | 0.0 | 0.404 | 0.1993 | 0.735 | 0.254 |  |
| mix | seuil | tres humide: au-dessus du 80e centile | 97 | -0.1311 | [-0.5584, 0.2101] | [-0.2016, -0.0501] | 0.0 | 0.416 | 0.1235 | 0.619 | 0.197 |  |
| mix | moitie | 1993-2004 | 47 | -0.146 | [-0.6821, 0.3507] | [-0.2595, 0.019] | 0.003 | 0.422 | 0.1352 | 0.654 | 0.238 |  |
| mix | moitie | 2005-2017 | 50 | 0.0645 | [-0.4392, 0.4695] | [-0.0297, 0.2381] | 0.0 | 0.425 | 0.2386 | 0.708 | 0.192 | PASS |

## Multiple testing (29 slices per arm, headline excluded)

- **ecmwf51**: 4 pass the gate (DJF, MAM, lancee 0 mois avant, DJF, 2005-2017). By luck: between 0.1 (if forecasts were random 0/1) and 12.7 (if every slice were exactly as good as climatology); each N=24 slice has about 40 % chance to show BSS > 0.05 by luck. CI95 fully above 0: 0 (none), about 0.7 expected by luck.
- **mix**: 4 pass the gate (DJF, MAM, lancee 0 mois avant, DJF, 2005-2017). By luck: between 0.1 (if forecasts were random 0/1) and 12.6 (if every slice were exactly as good as climatology); each N=24 slice has about 40 % chance to show BSS > 0.05 by luck. CI95 fully above 0: 1 (DJF), about 0.7 expected by luck.

## Verdict

**Fragile, most likely noise as a general edge.** The 0.063 has CI95 [-0.29, 0.42] (not distinguishable from 0), is negative in 1993-2004 (-0.15) and positive in 2005-2017 (+0.30), fails at every other threshold, and comes only from lead-1 months (each month forecast on its own 1st day). From lead 2 on, BSS is about -0.75 to -1.1 and cal_cv about 0: no usable information one month ahead. A true seasonal product (one forecast on the season's first day) scores -0.40 overall.

Only slice worth pursuing: **winter DJF, forecast issued on 1 December** (leads 1-3): BSS 0.54 for both ECMWF-51 and the mix (identical 0/1 calls), N=24, CI95 [-0.07, 1.0], cal_cv 0.53; event rate 85 % when it says dry vs 9 % otherwise. It disappears when issued 1 November (-0.53). With 4 passes out of 29 and roughly 40 % luck per small slice, treat it as a hypothesis, not an edge. Only the mix DJF (shortest lead) has CI95 above 0 [0.21, 1.0], about 0.7 such slices expected by luck.

## Limits

- Per-member reliability not possible: the CSV holds only ensemble means and ECMWF raw members are not on the box. Reliability here = conditional event rates of the 0/1 forecast and the cross-validated recalibration.
- Thresholds are leave-one-out on each series (forecast 1993-2016, CHIRPS 1981-2024), as in the repo.
- No out-of-sample period (2017-2025 forecasts) available offline.
- Champion Kalshi unchanged. PR 260 not merged. CDS not called.
