"""Vendor-specific weather forecast fetchers.

Distinct from `src.predictors` (which compute P(YES) from features)
and `src.weather` (the historical Open-Meteo climatology source).
This package holds the live forecast vendors used as model inputs.

NWS NDFD : `nws_ndfd.py`. NBM station text (NBP/NBS/NBE) : `nbm_text.py`,
`nbm_client.py`, `nbm_prob.py`. NBM is evaluated offline (piste A2) and
is not the live champion. GEFS members from NOAA S3 : `gefs_s3.py`
(piste A3, offline only). Same-day station observations (C1) live in
`src/truth/asos.py` ; remaining-day HRRR hourly is `src/weather/hrrr_hourly.py`.
"""
