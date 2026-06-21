# Learning loop 20260621T163554Z

- Base: `v3fa` -> final `{'features': ['p_consensus', 'forecast_spread', 'days_ahead', 'series_bias_fa'], 'C': 0.1}`
- Trials: 3, accepted: 1
- VALID: 2026-05-21..2026-06-01 (12 dates) / HOLDOUT: 2026-06-02..2026-06-13 (12 dates)

| # | candidate | Brier valid | vs incumbent | p | verdict |
|---|---|---|---|---|---|
| 1 | set_C(0.1) | 0.1302 | 0.1311 | 0.046 | ACCEPT |
| 2 | add_feature(month_sin) | 0.1299 | 0.1302 | 0.102 | reject |
| 3 | add_feature(month_cos) | 0.1300 | 0.1302 | 0.102 | reject |

## Holdout (single shot)

- initial: 0.1178 / final: 0.1173 / kalshi_mid: 0.1173
- **GENERALIZED**

_This run never edits CHAMPION.json; live promotion follows the existing champion/challenger rule._
