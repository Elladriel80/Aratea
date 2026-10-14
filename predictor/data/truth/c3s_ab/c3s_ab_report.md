# C3S multi-modèle : A/B hors ligne

Prévision : C3S multi-modèle.
Trois A/B séparés contre la climato. Aucun chiffre inventé.
Champion Kalshi inchangé. CDS non appelé.
Moyenne équipondérée par centre. Un trou n'est pas comblé.

Mesure faite sur la box partagée
(`/workspace/aratea-c3s-score`, commit 973a4ab).
Le CSV n'existe que là :
`/workspace/cds-test/c3s-monthly/c3s_tp_monthly.csv`.
Ces chiffres sont recopiés. Ils ne sont pas recalculés ici.
`computed: true` pour ce run. Le bloc SEAS5 de la PR 246 reste
`computed: false`.

Les vérités USDM, SPEI-6 et CHIRPS ont été réutilisées depuis le
tree SEAS5 local, et elles sont absentes du tree de la PR 260.

Sur cette box : 34560 lignes, 5 centres × 6912, 0 trous.
Tests sur la box : 33 réussis, 2 ignorés.
`cds_called` faux. `champion_switched` faux.
Le mélange ne bat pas ECMWF-51 sur la headline.

## Entrée

CSV PM : `/workspace/cds-test/c3s-monthly/c3s_tp_monthly.csv`.
Copie locale : absente. On ne l'a pas fabriquée.
Fenêtre hindcast attendue en premier : 1993-2016.
Cellules du mélange : 6912. Dont un centre manque : 0.

Gate : 10 saisons et BSS > 0.05.

## Centres

| Centre | Système | Lignes | Statut |
|---|---:|---:|---|
| Météo-France système 8 | 8 | 6912 | présent |
| DWD système 21 | 21 | 6912 | présent |
| CMCC système 35 | 35 | 6912 | présent |
| NCEP système 2 | 2 | 6912 | présent |
| ECMWF système 51 (SEAS5) | 51 | 6912 | présent |

## Les trois A/B du mélange (par région, jamais poolé)

Headline C = MED seulement. On ne mélange pas MED et India.

| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A US Drought Monitor | Midwest | 69 | 0.4348 | 0.0428 | -9.1537 | testée, ça n'aide pas |
| A US Drought Monitor | Southwest | 69 | 0.5507 | 0.2561 | -1.1508 | testée, ça n'aide pas |
| B SPEI | MED | 97 | 0.5155 | 0.0 | n/d | bloquée |
| B SPEI | India | 97 | 0.5155 | 0.0 | n/d | bloquée |
| B SPEI | US | 0 | n/d | n/d | n/d | bloquée |
| C CHIRPS pluie | MED (headline) | 97 | 0.268 | 0.253 | -0.0593 | testée, ça n'aide pas |
| C CHIRPS pluie | India | 97 | 0.3196 | 0.2507 | -0.275 | testée, ça n'aide pas |

## ECMWF-51 seul (SEAS5, lignes de ce CSV seulement)

| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A US Drought Monitor | Midwest | 69 | 0.5507 | 0.0428 | -11.8614 | testée, ça n'aide pas |
| A US Drought Monitor | Southwest | 69 | 0.5072 | 0.2561 | -0.981 | testée, ça n'aide pas |
| B SPEI | MED | 97 | 0.5052 | 0.0 | n/d | bloquée |
| B SPEI | India | 97 | 0.5155 | 0.0 | n/d | bloquée |
| B SPEI | US | 0 | n/d | n/d | n/d | bloquée |
| C CHIRPS pluie | MED (headline) | 97 | 0.2371 | 0.253 | 0.0629 | testée, ça aide |
| C CHIRPS pluie | India | 97 | 0.299 | 0.2507 | -0.1928 | testée, ça n'aide pas |

## Comparaison headline (CHIRPS MED seulement)

N mélange : 97. BSS mélange : -0.0593.
N ECMWF-51 : 97. BSS ECMWF-51 : 0.0629.
Verdict : le mélange ne bat pas ECMWF-51.
India n'entre pas dans cette ligne.

## Baseline SEAS5 déjà mesurée (PR 246, pas un score de ce run)

`computed: false`. Ces chiffres viennent du commit aa8d61f.
Ils ne sont pas recalculés. Le BSS SPEI reste n/d.
On ne pool pas MED et India.

| A/B | Région | N | BSS | Verdict |
|---|---|---:|---:|---|
| A | Midwest | 97 | -16.8565 | testée, ça n'aide pas |
| A | Southwest | 97 | -0.9844 | testée, ça n'aide pas |
| B | MED | 123 | n/d | bloquée |
| B | India | 123 | n/d | bloquée |
| B | US | 0 | n/d | bloquée |
| C | MED (headline) | 125 | 0.0552 | testée, ça aide |
| C | India | 125 | -0.0707 | testée, ça n'aide pas |

## Notes

- Mesure de la box partagée, commit 973a4ab. CSV absent de ce tree.
- Headline C = CHIRPS MED seulement. India à part. Pas de C poolé.
- SPEI-6 : Brier climato 0. Pas de BSS SPEI inventé.
- Le mélange ne bat pas ECMWF-51 sur CHIRPS MED.
- Champion Kalshi inchangé. Pas d'appel CDS.

## Verdicts

- C3S multi-modèle : testée, ça n'aide pas
- ECMWF-51 : testée, ça aide (CHIRPS MED seulement)
- SEAS5 : testée, ça aide (CHIRPS MED seulement)
- US Drought Monitor : testée, ça aide
- SPEI : testée, ça aide
- CHIRPS pluie : testée, ça aide
- Sécheresse US : testée, ça n'aide pas
- Sécheresse Méditerranée : testée, ça n'aide pas
- Sécheresse Inde : testée, ça n'aide pas
- NMME : bloquée
- Open-Meteo Seasonal : bloquée

La ligne SEAS5 du catalogue est la mesure PR 246, pas un recalcul.
US Drought Monitor, SPEI et CHIRPS pluie sont les statuts déjà publiés des vérités.
Le résultat de ce run est le tableau des trois A/B.
Sécheresse Méditerranée et Sécheresse Inde suivent le mélange, pas ECMWF-51.

Pas de clé API dans ce dépôt.
Pas d'appel cdsapi.
Pas de bascule du champion Kalshi.
