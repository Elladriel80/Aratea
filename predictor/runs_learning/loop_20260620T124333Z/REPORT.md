# Learning loop 20260620T124333Z

- Base: `v3` -> final `{'features': ['p_consensus', 'forecast_spread', 'days_ahead'], 'C': 1.0}`
- Trials: 7, accepted: 0
- VALID: 2026-05-21..2026-06-01 (12 dates) / HOLDOUT: 2026-06-02..2026-06-13 (12 dates)

| # | candidate | Brier valid | vs incumbent | p | verdict |
|---|---|---|---|---|---|
| 1 | drop_feature(days_ahead) | 0.1601 | 0.1601 | 1.000 | reject |
| 2 | add_feature(distance_to_coast_km) | 0.1600 | 0.1601 | 0.455 | reject |
| 3 | add_feature(elevation_m) | 0.1600 | 0.1601 | 0.396 | reject |
| 4 | add_feature(forest_pct_5km) | 0.1600 | 0.1601 | 0.455 | reject |
| 5 | add_feature(latitude) | 0.1600 | 0.1601 | 0.396 | reject |
| 6 | add_feature(urban_density_5km) | 0.1600 | 0.1601 | 0.455 | reject |
| 7 | add_feature(water_pct_10km) | 0.1600 | 0.1601 | 0.455 | reject |

## Holdout (single shot)

- initial: 0.1389 / final: 0.1389 / kalshi_mid: 0.1340
- **DID NOT GENERALIZE**

_This run never edits CHAMPION.json; live promotion follows the existing champion/challenger rule._
