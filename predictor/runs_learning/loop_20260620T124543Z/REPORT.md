# Learning loop 20260620T124543Z

- Base: `v3` -> final `{'features': ['p_consensus', 'forecast_spread', 'days_ahead'], 'C': 0.1}`
- Trials: 4, accepted: 1
- VALID: 2026-05-21..2026-06-01 (12 dates) / HOLDOUT: 2026-06-02..2026-06-13 (12 dates)

| # | candidate | Brier valid | vs incumbent | p | verdict |
|---|---|---|---|---|---|
| 1 | set_C(0.1) | 0.1571 | 0.1590 | 0.046 | ACCEPT |
| 2 | add_feature(consensus_x_spread) | 0.1572 | 0.1571 | 0.661 | reject |
| 3 | set_C(0.3) | 0.1585 | 0.1571 | 0.961 | reject |
| 4 | set_C(3.0) | 0.1592 | 0.1571 | 0.961 | reject |

## Holdout (single shot)

- initial: 0.1370 / final: 0.1369 / kalshi_mid: 0.1340
- **GENERALIZED**

_This run never edits CHAMPION.json; live promotion follows the existing champion/challenger rule._
