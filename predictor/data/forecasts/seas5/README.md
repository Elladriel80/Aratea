# SEAS5 offline input (no CDS)

Auth stays on the Aratea PM box. Cloud agents do not call CDS and do
not read `CDS_API_KEY`. Drop already-reduced regional monthly means
here.

## Expected files

| Path | Role |
|---|---|
| `predictor/data/forecasts/seas5/regional_monthly.csv` | preferred forecast input |
| `predictor/data/forecasts/seas5/seas5_regional_monthly.csv` | same schema, alternate name |
| `predictor/data/forecasts/seas5/pairs_usdm.csv` | optional ready A/B A pairs |
| `predictor/data/forecasts/seas5/pairs_spei.csv` | optional ready A/B B pairs |
| `predictor/data/forecasts/seas5/pairs_chirps.csv` | optional ready A/B C pairs |
| `*.nc` / `*.grib` | raw slices: ignored, never decoded |

Header-only examples sit next to this README (`*.csv.example`).
Copy, rename, fill. Do not invent scores in git.

## `regional_monthly.csv` schema

Required columns:

```
region,year,init_month,lead_month,tp_mean_mm
```

| Column | Type | Meaning |
|---|---|---|
| region | text | `midwest` `southwest` `med` `india_mh_ka` `us` |
| year | int | year of the SEAS5 start date (init) |
| init_month | int | 1-12, month of the start date |
| lead_month | int | C3S `leadtime_month`; 1 = valid month equals init month |
| tp_mean_mm | float | ensemble-mean total precipitation, mm/month |

Optional columns: `tp_anom_mm`, `valid_year`, `valid_month`,
`ensemble_size`, `source` (if set, must be `SEAS5`).

Valid month = init month + lead_month - 1, with year rollover.
If several inits cover the same valid month, the shortest lead is kept.
A meteorological season is scored only when all 3 months are present.

Aliases accepted for `region`: Midwest, Southwest, MED, Méditerranée,
Inde, India, Maharashtra+Karnataka, US.

## Truth series (already counted in PRs 240 / 243 / 244)

Inventories alone are not enough to score. Drop or export the time
series:

| File | Schema |
|---|---|
| `predictor/data/truth/usdm/usdm_seasons.csv` | `region,year,season,d2_plus_mean,event_d2_plus_ge_30` |
| `predictor/data/truth/usdm/weeks_Midwest_cat.json` | PR 240 `--write-weeks` |
| `predictor/data/truth/usdm/weeks_Southwest_cat.json` | same |
| `predictor/data/truth/spei/spei6_monthly.csv` | `region,year,month,spei6_mean` |
| `predictor/data/truth/spei/spei6_seasons.csv` | `region,year,season,spei6_mean,event_spei6_le_minus_1_5` |
| `predictor/data/truth/chirps/chirps_monthly.csv` | `region,year,month,tp_mean_mm` |
| `predictor/data/truth/chirps/chirps_seasons.csv` | `region,year,season,tp_mean_mm,event_below_climato` |

`season` is `DJF` `MAM` `JJA` `SON`. DJF year is the January year.

## Pairs schema

```
region,year,season,p_forecast_dry,event
```

`p_forecast_dry` is 0 or 1 (or a probability in between). `event` is
0/1, true/false, oui/non.

## Download boxes (PM only)

CDS area `[North, West, South, East]`. Scoring still uses the published
polygons from PRs 240 / 243 / 244.

```
med          [45, -10, 30, 40]
midwest      [49.5, -97.5, 36.0, -80.5]
southwest    [42.0, -124.5, 31.3, -103.0]
india_mh_ka  [22.1, 72.5, 11.5, 81.0]
```

## Run

From `predictor/`:

```
python scripts/eval_seas5_ab.py
```

Missing forecast files: dry / blocked, measured N only, no invented
score. Gate: N ≥ 10 seasons, then BSS > 0.05 vs climato for
« ça aide ».
