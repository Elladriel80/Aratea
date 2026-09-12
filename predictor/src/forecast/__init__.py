"""Vendor-specific weather forecast fetchers.

Distinct from `src.predictors` (which compute P(YES) from features)
and `src.weather` (the historical Open-Meteo climatology source).
This package holds the live forecast vendors used as model inputs.

NWS NDFD : `nws_ndfd.py`. NBM station text (NBP/NBS/NBE) : `nbm_text.py`,
`nbm_client.py`, `nbm_prob.py`. NBM is evaluated offline (piste A2) and
is not the live champion.
"""
