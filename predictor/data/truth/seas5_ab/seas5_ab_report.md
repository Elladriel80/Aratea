# SEAS5 : A/B hors ligne

Prévision : SEAS5.
Trois A/B séparés contre la climato. Aucun chiffre inventé.
Champion Kalshi inchangé. CDS non rappelé.

Mesure faite sur la boîte partagée, CSV PM
`/workspace/cds-test/seas5-monthly/seas5_tp_monthly.csv`.

Gate : 10 saisons et BSS > 0.05.

Headline C = MED seulement. On ne mélange pas MED et India.

## Résultats mesurés

| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A USDM | Midwest | 97 | 0.5464 | 0.0306 | -16.8565 | testée, ça n'aide pas |
| A USDM | Southwest | 97 | 0.5052 | 0.2546 | -0.9844 | testée, ça n'aide pas |
| B SPEI-6 | MED | 123 | 0.5285 | 0.0 | n/d | bloquée |
| B SPEI-6 | India | 123 | 0.5122 | 0.0 | n/d | bloquée |
| B SPEI-6 | US | 0 | n/d | n/d | n/d | bloquée (pas de région forecast us) |
| C CHIRPS | MED (headline) | 125 | 0.24 | 0.254 | 0.0552 | testée, ça aide |
| C CHIRPS | India | 125 | 0.272 | 0.254 | -0.0707 | testée, ça n'aide pas |

## Notes du PM

- A : ce n'est pas un bug de clé. La règle publiée dit trop souvent
  « sécheresse » face à une climato rare (Midwest, base_rate 0,03).
- B : le seuil SPEI-6 ≤ -1,5 est trop rare après moyenne spatiale.
  Pas de BSS inventé. Pas de région forecast us dans le CSV PM.
- C : ça aide MED seulement (juste au-dessus de 0,05). India : ça
  n'aide pas. On ne titre pas un C poolé.
- Champion Kalshi inchangé. Pas de promo en ligne.
- Un nouvel essai SPEI seulement avec une autre règle déjà
  publiée, pas un BSS bricolé.

## Verdicts (noms du catalogue, non renommés)

- SEAS5 : testée, ça aide (CHIRPS MED seulement)
- US Drought Monitor : testée, ça aide
- SPEI : testée, ça aide
- CHIRPS pluie : testée, ça aide
- Sécheresse US : testée, ça n'aide pas
- Sécheresse Méditerranée : testée, ça aide
- Sécheresse Inde : testée, ça n'aide pas
- C3S multi-modèle : pas encore testée
- NMME : bloquée
- Open-Meteo Seasonal : bloquée

Pas de clé API dans ce dépôt.
Pas d'appel cdsapi.
Pas de bascule du champion Kalshi.
