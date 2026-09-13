# SEAS5 : trois A/B, en attendant les fichiers

**Date :** 13 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Mesure Phase 2. Nom stable : **SEAS5**.
Trois tests séparés, chacun contre la climato :

- A) SEAS5 contre US Drought Monitor (Midwest, Southwest)
- B) SEAS5 contre SPEI-6 (Méditerranée, Inde, US)
- C) SEAS5 contre CHIRPS pluie (Méditerranée, Inde)

Cette note dit seulement ce qui est prêt. Le site public n'a pas
été changé. Le modèle Kalshi en ligne n'a pas été changé. Aucun
pari avec de l'argent réel. Aucun chiffre n'a été inventé. On n'a
pas appelé CDS. La clé Copernicus reste sur la machine du PM.

## Pourquoi on n'appelle pas CDS

`CDS_API_KEY` n'est pas un secret GitHub. Un agent cloud ne doit
pas ouvrir Copernicus. Le PM télécharge les tranches SEAS5 chez
lui, puis dépose un fichier déjà réduit.

## Où poser les fichiers

Le script lit **d'abord** le fichier partagé du PM :

`/workspace/cds-test/seas5-monthly/seas5_tp_monthly.csv`

S'il n'est pas là, copie locale acceptée :

`predictor/data/forecasts/seas5/seas5_tp_monthly.csv`

(ou `regional_monthly.csv` dans le même dossier)

Des NetCDF à côté du CSV sont ignorés. On ne les décode pas.

Colonnes exactes :

| Colonne | Sens |
|---|---|
| region | labels PM : `MED`, `Midwest`, `Southwest`, `India` |
| year | année de l'init (la date de départ SEAS5) |
| init_month | mois d'init, 1 à 12 |
| lead_month | lead C3S, 1 = le mois d'init |
| tp_mean_mm | pluie moyenne d'ensemble, mm par mois |

## Noms de régions (labels PM)

| Label PM | Slug interne | Zone notée |
|---|---|---|
| MED | med | Méditerranée (IPCC MED) |
| Midwest | midwest | USDA Midwest |
| Southwest | southwest | USDA Southwest |
| India | india | Maharashtra + Karnataka |

On accepte aussi Méditerranée, Inde, india_mh_ka. Même chose.

Colonnes en plus, si le PM les a : `tp_anom_mm`, `valid_year`,
`valid_month`, `ensemble_size`, `source` (si remplie : SEAS5).

Un mois valide = mois d'init + lead - 1. Si le même mois existe
plusieurs fois, on garde le lead le plus court.

Série déjà jointe, autre choix :

- `pairs_usdm.csv`
- `pairs_spei.csv`
- `pairs_chirps.csv`

Colonnes : `region,year,season,p_forecast_dry,event`.
`season` = DJF, MAM, JJA ou SON.

Un fichier brut `.nc` / `.grib` sans CSV : on s'arrête. On ne
décode pas. On n'invente pas de score.

## Les vérités déjà comptées

Elles viennent des PR 240, 243 et 244. Pour noter, il faut la
série dans le temps, pas seulement l'inventaire.

| A/B | Fichier | Événement |
|---|---|---|
| A | `data/truth/usdm/usdm_seasons.csv` ou `weeks_*_cat.json` | D2+ ≥ 30 % |
| B | `data/truth/spei/spei6_monthly.csv` | SPEI-6 moyen ≤ -1,5 |
| C | `data/truth/chirps/chirps_monthly.csv` | pluie sous la climato leave-one-out du même type de saison |

CHIRPS n'a pas de classe de sécheresse dans ses docs. On ne
l'invente pas. On compare juste sous / dessus la moyenne.

## Boîtes de téléchargement (pas le masque)

Le PM peut couper CDS avec ces rectangles [N, W, S, E]. Le score
garde les polygones déjà publiés.

| Zone | N | W | S | E |
|---|---:|---:|---:|---:|
| Méditerranée | 45 | -10 | 30 | 40 |
| Midwest | 49,5 | -97,5 | 36,0 | -80,5 |
| Southwest | 42,0 | -124,5 | 31,3 | -103,0 |
| India (MH+KA) | 22,1 | 72,5 | 11,5 | 81,0 |

## La règle avant de conclure

Au moins **10 saisons** par région. Sinon : bloquée, avec le N
mesuré, sans BSS inventé.

Si N ≥ 10 et BSS > 0,05 contre la climato : testée, ça aide.
Sinon : testée, ça n'aide pas, avec le N mesuré.

Climato = fréquence leave-one-out des autres saisons. Si cette
erreur vaut 0, le BSS n'existe pas. On l'écrit n/d.

Les régions ne sont pas mélangées. Midwest et Southwest restent
deux comptes.

## Ce que dit le run d'aujourd'hui

Pas de fichier à
`/workspace/cds-test/seas5-monthly/seas5_tp_monthly.csv`,
ni de copie sous `data/forecasts/seas5/`. Donc les trois A/B
sont **bloquées**. Zéro score inventé. N = 0 partout. BSS n/d.

SEAS5 : bloquée.
Sécheresse US : bloquée.
Sécheresse Méditerranée / Inde : cible Tier 1 (pas encore testée).

Les vérités US Drought Monitor, SPEI et CHIRPS pluie restent
celles déjà comptées.

## Décision

On ne change pas le modèle Kalshi en ligne.

Pourquoi : ce n'est pas un test Kalshi. C'est le tuyau SEAS5
Phase 2. Sans fichier du PM, on ne conclut pas.

## Comment relancer

Dans le dossier `predictor`, après le dépôt du CSV :

```
python scripts/eval_seas5_ab.py
```

Sans fichier, le même ordre tourne en mode bloqué. Les comptes
sont dans `data/truth/seas5_ab/`.

Pas de changement du texte du site. Pas de trading réel.
