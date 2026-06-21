# Learning loop 20260621T162639Z

- Base: `v3fa` -> final `{'features': ['p_consensus', 'forecast_spread', 'days_ahead', 'series_bias_fa'], 'C': 0.1}`
- Trials: 7, accepted: 1
- VALID: 2026-05-21..2026-06-01 (12 dates) / HOLDOUT: 2026-06-02..2026-06-13 (12 dates)

| # | candidate | Brier valid | vs incumbent | p | verdict |
|---|---|---|---|---|---|
| 1 | set_C(0.1) | 0.1302 | 0.1311 | 0.046 | ACCEPT |
| 2 | set_C(0.3) | 0.1308 | 0.1302 | 0.954 | reject |
| 3 | set_C(3.0) | 0.1312 | 0.1302 | 0.968 | reject |
| 4 | drop_feature(days_ahead) | 0.1302 | 0.1302 | 1.000 | reject |
| 5 | drop_feature(series_bias_fa) | 0.1312 | 0.1302 | 0.867 | reject |
| 6 | add_feature(is_hightemp) | 0.1301 | 0.1302 | 0.235 | reject |
| 7 | add_feature(consensus_x_spread) | 0.1301 | 0.1302 | 0.425 | reject |

## Holdout (single shot)

- initial: 0.1178 / final: 0.1173 / kalshi_mid: 0.1173
- **GENERALIZED**

_This run never edits CHAMPION.json; live promotion follows the existing champion/challenger rule._
