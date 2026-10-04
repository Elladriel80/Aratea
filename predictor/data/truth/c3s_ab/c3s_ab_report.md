# C3S multi-modèle : A/B hors ligne

Prévision : C3S multi-modèle.
Trois A/B séparés contre la climato. Aucun chiffre inventé.
Champion Kalshi inchangé. CDS non appelé.
Moyenne équipondérée par centre. Un trou n'est pas comblé.

## Entrée

CSV PM (prioritaire) : `/workspace/cds-test/c3s-monthly/c3s_tp_monthly.csv`.
Copie locale : `/workspace/predictor/data/forecasts/c3s/c3s_tp_monthly.csv`.
CSV lu : absent.
Fenêtre hindcast attendue en premier : 1993-2016.
Cellules du mélange : 0. Dont un centre manque : 0.

Aucun CSV C3S. Mesure bloquée. Cherché : /workspace/cds-test/c3s-monthly/c3s_tp_monthly.csv, puis /workspace/predictor/data/forecasts/c3s/c3s_tp_monthly.csv. Pas d'appel CDS. Pas de score inventé. Le PM dépose c3s_tp_monthly.csv (colonnes origin,system,region,year,init_month,lead_month,tp_mean_mm,n_members,n_cells ; régions MED, Midwest, Southwest, India).

Gate : 10 saisons et BSS > 0.05.

## Centres

| Centre | Système | Lignes | Statut |
|---|---:|---:|---|
| Météo-France système 8 | 8 | 0 | trou |
| DWD système 21 | 21 | 0 | trou |
| CMCC système 35 | 35 | 0 | trou |
| NCEP système 2 | 2 | 0 | trou |
| ECMWF système 51 (SEAS5) | 51 | 0 | trou |

## Les trois A/B du mélange (par région, jamais poolé)

Headline C = MED seulement. On ne mélange pas MED et India.

| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A US Drought Monitor | Midwest | 0 | n/d | n/d | n/d | bloquée |
| A US Drought Monitor | Southwest | 0 | n/d | n/d | n/d | bloquée |
| B SPEI | MED | 0 | n/d | n/d | n/d | bloquée |
| B SPEI | India | 0 | n/d | n/d | n/d | bloquée |
| B SPEI | US | 0 | n/d | n/d | n/d | bloquée |
| C CHIRPS pluie | MED (headline) | 0 | n/d | n/d | n/d | bloquée |
| C CHIRPS pluie | India | 0 | n/d | n/d | n/d | bloquée |

## ECMWF-51 seul (SEAS5, lignes de ce CSV seulement)

Si le centre manque, la ligne reste bloquée. On ne remplit pas.

| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A US Drought Monitor | Midwest | 0 | n/d | n/d | n/d | bloquée |
| A US Drought Monitor | Southwest | 0 | n/d | n/d | n/d | bloquée |
| B SPEI | MED | 0 | n/d | n/d | n/d | bloquée |
| B SPEI | India | 0 | n/d | n/d | n/d | bloquée |
| B SPEI | US | 0 | n/d | n/d | n/d | bloquée |
| C CHIRPS pluie | MED (headline) | 0 | n/d | n/d | n/d | bloquée |
| C CHIRPS pluie | India | 0 | n/d | n/d | n/d | bloquée |

## Comparaison headline (CHIRPS MED seulement)

N mélange : 0. BSS mélange : n/d.
N ECMWF-51 : 0. BSS ECMWF-51 : n/d.
Verdict : comparaison bloquée (BSS manquant).
India n'entre pas dans cette ligne.

## Baseline SEAS5 déjà mesurée (PR 246, pas un score de ce run)

Ces chiffres viennent du commit aa8d61f. Ils ne sont pas recalculés.
Le BSS SPEI reste n/d. On ne pool pas MED et India.

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

- CSV C3S absent. Mesure bloquée. Aucun BSS inventé.
- Headline C = CHIRPS MED seulement. India à part. Pas de C poolé.
- SPEI-6 publié (PR 246) : Brier climato 0 au seuil ≤ -1,5 après moyenne spatiale. Pas de BSS SPEI inventé.
- ECMWF-51 n'est recalculé que si ses lignes sont dans le CSV C3S. La mesure PR 246 n'est pas recopiée dans les BSS de ce run.
- Champion Kalshi inchangé. Pas d'appel CDS.

## Boîtes de téléchargement PM (pas le masque de score)

Le score utilise les polygones déjà publiés (PR 240 / 243 / 244).

| Région | N | W | S | E | Masque de score |
|---|---:|---:|---:|---:|---|
| Méditerranée (`med`) | 45.0 | -10.0 | 30.0 | 40.0 | IPCC AR6 WGI MED (PR 243 / 244) |
| Midwest (`midwest`) | 49.5 | -97.5 | 36.0 | -80.5 | USDA Climate Hub Midwest (PR 240 / 243) |
| Southwest (`southwest`) | 42.0 | -124.5 | 31.3 | -103.0 | USDA Climate Hub Southwest (PR 240 / 243) |
| India (`india`) | 22.1 | 72.5 | 11.5 | 81.0 | Maharashtra + Karnataka Natural Earth (PR 243 / 244) |

## Verdicts

- C3S multi-modèle : bloquée
- ECMWF-51 : bloquée
- SEAS5 : testée, ça aide (CHIRPS MED seulement)
- US Drought Monitor : testée, ça aide
- SPEI : testée, ça aide
- CHIRPS pluie : testée, ça aide
- Sécheresse US : bloquée
- Sécheresse Méditerranée : cible Tier 1 (pas encore testée)
- Sécheresse Inde : cible Tier 1 (pas encore testée)
- NMME : bloquée
- Open-Meteo Seasonal : bloquée

La ligne SEAS5 du catalogue est la mesure PR 246, pas un recalcul.
US Drought Monitor, SPEI et CHIRPS pluie sont les statuts déjà publiés des vérités.
Le résultat de ce run est le tableau des trois A/B.

Pas de clé API dans ce dépôt.
Pas d'appel cdsapi.
Pas de bascule du champion Kalshi.
