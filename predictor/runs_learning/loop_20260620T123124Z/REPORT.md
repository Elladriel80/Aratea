# Learning loop 20260620T123124Z

- Base: `v3` -> final `{'features': ['p_consensus', 'forecast_spread', 'days_ahead', 'latitude'], 'C': 0.1}`
- Trials: 10, accepted: 3
- VALID: 2026-05-21..2026-06-01 (12 dates) / HOLDOUT: 2026-06-02..2026-06-13 (12 dates)

| # | candidate | Brier valid | vs incumbent | p | verdict |
|---|---|---|---|---|---|
| 1 | set_C(0.3) | 0.1585 | 0.1590 | 0.039 | ACCEPT |
| 2 | set_C(3.0) | 0.1592 | 0.1585 | 0.968 | reject |
| 3 | set_C(0.1) | 0.1571 | 0.1585 | 0.046 | ACCEPT |
| 4 | drop_feature(days_ahead) | 0.1571 | 0.1571 | 1.000 | reject |
| 5 | add_feature(distance_to_coast_km) | 0.1571 | 0.1571 | 0.367 | reject |
| 6 | add_feature(elevation_m) | 0.1572 | 0.1571 | 0.396 | reject |
| 7 | add_feature(forest_pct_5km) | 0.1567 | 0.1571 | 0.311 | reject |
| 8 | add_feature(latitude) | 0.1571 | 0.1571 | 0.039 | ACCEPT |
| 9 | add_feature(urban_density_5km) | 0.1568 | 0.1571 | 0.311 | reject |
| 10 | add_feature(water_pct_10km) | 0.1569 | 0.1571 | 0.311 | reject |

## Holdout (single shot)

- initial: 0.1370 / final: 0.1367 / kalshi_mid: 0.1340
- **GENERALIZED**

_This run never edits CHAMPION.json; live promotion follows the existing champion/challenger rule._
