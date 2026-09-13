# SEAS5 SCORE_RESULTS

Copie des chiffres mesurés sur la boîte partagée (CSV PM).
CDS non rappelé. Headline C = MED seulement. Pas de C poolé.

| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A USDM | Midwest | 97 | 0.5464 | 0.0306 | -16.8565 | testée, ça n'aide pas |
| A USDM | Southwest | 97 | 0.5052 | 0.2546 | -0.9844 | testée, ça n'aide pas |
| B SPEI-6 | MED | 123 | 0.5285 | 0.0 | n/d | bloquée |
| B SPEI-6 | India | 123 | 0.5122 | 0.0 | n/d | bloquée |
| B SPEI-6 | US | 0 | n/d | n/d | n/d | bloquée (pas de région forecast us) |
| C CHIRPS | MED (headline) | 125 | 0.24 | 0.254 | 0.0552 | testée, ça aide |
| C CHIRPS | India | 125 | 0.272 | 0.254 | -0.0707 | testée, ça n'aide pas |
