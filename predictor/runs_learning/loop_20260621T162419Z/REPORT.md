# Learning loop 20260621T162419Z

- Base: `v3b` -> final `{'features': ['p_consensus', 'forecast_spread', 'days_ahead', 'series_bias_prior'], 'C': 0.1}`
- Trials: 10, accepted: 1
- VALID: 2026-05-21..2026-06-01 (12 dates) / HOLDOUT: 2026-06-02..2026-06-13 (12 dates)

| # | candidate | Brier valid | vs incumbent | p | verdict |
|---|---|---|---|---|---|
| 1 | set_C(0.1) | 0.1300 | 0.1309 | 0.055 | ACCEPT |
| 2 | set_C(0.3) | 0.1306 | 0.1300 | 0.945 | reject |
| 3 | set_C(3.0) | 0.1310 | 0.1300 | 0.954 | reject |
| 4 | drop_feature(days_ahead) | 0.1300 | 0.1300 | 0.750 | reject |
| 5 | drop_feature(series_bias_prior) | 0.1312 | 0.1300 | 0.898 | reject |
| 6 | add_feature(is_hightemp) | 0.1299 | 0.1300 | 0.311 | reject |
| 7 | add_feature(consensus_x_spread) | 0.1299 | 0.1300 | 0.455 | reject |
| 8 | add_feature(distance_to_coast_km) | 0.1300 | 0.1300 | 0.515 | reject |
| 9 | add_feature(elevation_m) | 0.1301 | 0.1300 | 0.604 | reject |
| 10 | add_feature(latitude) | 0.1309 | 0.1300 | 0.987 | reject |

## Holdout (single shot)

- initial: 0.1175 / final: 0.1170 / kalshi_mid: 0.1173
- **GENERALIZED**

_This run never edits CHAMPION.json; live promotion follows the existing champion/challenger rule._
