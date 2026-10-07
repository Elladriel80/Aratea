# C3S multi-model offline input (no CDS)

Auth stays on the Aratea PM box. Cloud agents do not call CDS and do
not read an API key. Drop already-reduced regional monthly means here.

Stable name: C3S multi-modèle. Equal weight per centre. A missing
centre is a hole and is never filled, including from the SEAS5 CSV.

## Expected files

Search order (no CDS):

1. `/workspace/cds-test/c3s-monthly/c3s_tp_monthly.csv` (PM shared box)
2. `predictor/data/forecasts/c3s/c3s_tp_monthly.csv`

| Path | Role |
|---|---|
| `/workspace/cds-test/c3s-monthly/c3s_tp_monthly.csv` | authoritative PM CSV |
| `predictor/data/forecasts/c3s/c3s_tp_monthly.csv` | local copy, same schema |
| `*.nc` / `*.grib` | raw slices: ignored, never decoded |

The header-only example sits next to this README
(`c3s_tp_monthly.csv.example`). It is not a forecast. Do not invent
scores in git.

## Schema

```
origin,system,region,year,init_month,lead_month,tp_mean_mm,n_members,n_cells
```

| Column | Type | Meaning |
|---|---|---|
| origin | text | `meteo_france`, `dwd`, `cmcc`, `ncep`, `ecmwf` |
| system | int | C3S system id (see below) |
| region | text | PM labels: `MED` `Midwest` `Southwest` `India` |
| year | int | year of the init |
| init_month | int | 1-12 |
| lead_month | int | C3S `leadtime_month`; 1 = valid month equals init month |
| tp_mean_mm | float | ensemble-mean total precipitation, mm/month |
| n_members | int | stored, not used as a weight |
| n_cells | int | stored, not used as a weight |

The multi-model value is the equal-weight mean of the centres present
for the same region, year, init month and lead. `n_members` does not
change the weight.

## Centres

| Origin | System | Role |
|---|---:|---|
| meteo_france | 8 | Météo-France |
| dwd | 21 | DWD |
| cmcc | 35 | CMCC |
| ncep | 2 | NCEP |
| ecmwf | 51 | SEAS5, scored alone as well as inside the mix |

`SEAS5` with system 51 is accepted as ECMWF 51. A centre that is not
in the file is a hole. This reader does not open the SEAS5 CSV to
fill it.

First hindcast years: 1993-2016. A missing year is reported. It is
not invented. Seasons that are present are still scored.

## Run

From `predictor/`:

```
python scripts/eval_c3s_ab.py
```

Missing CSV: dry / blocked, measured N only, no invented score.
Gate: N >= 10 seasons, then BSS > 0.05 vs climato for « ça aide ».
CHIRPS MED is the headline. India stays separate. Do not pool them.
SPEI-6 with climato Brier 0 stays blocked: no SPEI BSS.
