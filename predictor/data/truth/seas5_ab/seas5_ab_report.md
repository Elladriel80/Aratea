# SEAS5 : A/B hors ligne

Prévision : SEAS5.
Trois A/B séparés contre la climato. Aucun chiffre inventé.
Champion Kalshi inchangé. CDS non appelé.

## Entrée

CSV PM (prioritaire) : `/workspace/cds-test/seas5-monthly/seas5_tp_monthly.csv`.
Dossier local : `data/forecasts/seas5`.
CSV régional : absent.
Labels PM : MED, Midwest, Southwest, India.
Fichiers bruts : aucun.

Aucun CSV SEAS5. Cherché d'abord /workspace/cds-test/seas5-monthly/seas5_tp_monthly.csv, puis data/forecasts/seas5/. Pas d'appel CDS. Pas de score inventé. Le PM dépose seas5_tp_monthly.csv (colonnes region,year,init_month,lead_month,tp_mean_mm ; régions MED / Midwest / Southwest / India).

Gate : 10 saisons et BSS > 0.05.

## Les trois A/B

| A/B | Vérité | N saisons | Brier SEAS5 | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A SEAS5 vs climato, vérité USDM | US Drought Monitor | 0 | n/d | n/d | n/d | bloquée |
| B SEAS5 vs climato, vérité SPEI-6 | SPEI | 0 | n/d | n/d | n/d | bloquée |
| C SEAS5 vs climato, vérité CHIRPS | CHIRPS pluie | 0 | n/d | n/d | n/d | bloquée |

Notes :

- Aucun CSV SEAS5. Cherché d'abord /workspace/cds-test/seas5-monthly/seas5_tp_monthly.csv, puis data/forecasts/seas5/. Pas d'appel CDS. Pas de score inventé. Le PM dépose seas5_tp_monthly.csv (colonnes region,year,init_month,lead_month,tp_mean_mm ; régions MED / Midwest / Southwest / India).

## Par région (N mesuré seulement)

### A. SEAS5 vs climato, vérité USDM

- Midwest (`midwest`) : n=0 BSS n/d → bloquée
- Southwest (`southwest`) : n=0 BSS n/d → bloquée

### B. SEAS5 vs climato, vérité SPEI-6

- MED (`med`) : n=0 BSS n/d → bloquée
- India (`india`) : n=0 BSS n/d → bloquée
- US (`us`) : n=0 BSS n/d → bloquée

### C. SEAS5 vs climato, vérité CHIRPS

- MED (`med`) : n=0 BSS n/d → bloquée
- India (`india`) : n=0 BSS n/d → bloquée

## Boîtes de téléchargement PM (pas le masque de score)

Le score utilise les polygones déjà publiés (PR 240 / 243 / 244).
Ces rectangles CDS [N, W, S, E] servent seulement au téléchargement.

| Région | N | W | S | E | Masque de score |
|---|---:|---:|---:|---:|---|
| Méditerranée (`med`) | 45.0 | -10.0 | 30.0 | 40.0 | IPCC AR6 WGI MED (PR 243 / 244) |
| Midwest (`midwest`) | 49.5 | -97.5 | 36.0 | -80.5 | USDA Climate Hub Midwest (PR 240 / 243) |
| Southwest (`southwest`) | 42.0 | -124.5 | 31.3 | -103.0 | USDA Climate Hub Southwest (PR 240 / 243) |
| India (`india`) | 22.1 | 72.5 | 11.5 | 81.0 | Maharashtra + Karnataka Natural Earth (PR 243 / 244) |

## Verdicts (noms du catalogue, non renommés)

- SEAS5 : bloquée
- US Drought Monitor : testée, ça aide
- SPEI : testée, ça aide
- CHIRPS pluie : testée, ça aide
- Sécheresse US : bloquée
- Sécheresse Méditerranée : cible Tier 1 (pas encore testée)
- Sécheresse Inde : cible Tier 1 (pas encore testée)
- C3S multi-modèle : pas encore testée
- NMME : bloquée
- Open-Meteo Seasonal : bloquée

Pas de clé API dans ce dépôt.
Pas d'appel cdsapi.
Pas de bascule du champion Kalshi.

Schéma CSV : region,year,init_month,lead_month,tp_mean_mm.
