# SEAS5 : trois A/B mesurés

**Date :** 13 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Mesure Phase 2. Nom stable : **SEAS5**.
Trois tests séparés, chacun contre la climato :

- A) SEAS5 contre US Drought Monitor (Midwest, Southwest)
- B) SEAS5 contre SPEI-6 (Méditerranée, Inde, US)
- C) SEAS5 contre CHIRPS pluie (Méditerranée, Inde)

Cette note dit ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle Kalshi en ligne n'a pas été changé. Aucun
pari avec de l'argent réel. Aucun chiffre n'a été inventé. On n'a
pas rappelé CDS. La clé Copernicus reste sur la machine du PM.

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

## Résultats

Mesure faite sur la boîte partagée, avec le CSV du PM. CDS n'a
pas été rappelé. Aucun chiffre n'a été inventé. Headline C =
**MED seulement**. On ne mélange pas MED et India.

| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A USDM | Midwest | 97 | 0.5464 | 0.0306 | -16.8565 | testée, ça n'aide pas |
| A USDM | Southwest | 97 | 0.5052 | 0.2546 | -0.9844 | testée, ça n'aide pas |
| B SPEI-6 | MED | 123 | 0.5285 | 0.0 | n/d | bloquée |
| B SPEI-6 | India | 123 | 0.5122 | 0.0 | n/d | bloquée |
| B SPEI-6 | US | 0 | n/d | n/d | n/d | bloquée (pas de région forecast us) |
| C CHIRPS | MED (headline) | 125 | 0.24 | 0.254 | 0.0552 | testée, ça aide |
| C CHIRPS | India | 125 | 0.272 | 0.254 | -0.0707 | testée, ça n'aide pas |

Notes du PM :

- A : ce n'est pas un bug de clé. La règle publiée dit trop souvent
  « sécheresse » face à une climato rare (Midwest, base_rate 0,03).
- B : le seuil SPEI-6 ≤ -1,5 est trop rare après moyenne spatiale.
  Pas de BSS inventé. Pas de région forecast `us` dans le CSV PM.
- C : ça aide **MED seulement** (juste au-dessus de 0,05). India :
  ça n'aide pas. On ne titre pas un C poolé.
- Champion Kalshi inchangé. Pas de promo en ligne.
- Un nouvel essai SPEI seulement avec une autre règle déjà
  publiée, pas un BSS bricolé.

SEAS5 : testée, ça aide (CHIRPS MED seulement).
Sécheresse US : testée, ça n'aide pas.
Sécheresse Méditerranée : testée, ça aide (CHIRPS MED).
Sécheresse Inde : testée, ça n'aide pas (CHIRPS India).

Les vérités US Drought Monitor, SPEI et CHIRPS pluie restent
celles déjà comptées (inventaire).

## Décision

On ne change pas le modèle Kalshi en ligne.

Pourquoi : ce n'est pas un test Kalshi. C'est le score SEAS5
Phase 2. C n'aide que MED. A n'aide pas. B est bloquée. Pas
de promo.

## Comment relancer

Dans le dossier `predictor`, après le dépôt du CSV :

```
python scripts/eval_seas5_ab.py
```

Sans fichier, le même ordre tourne en mode bloqué. Les comptes
sont dans `data/truth/seas5_ab/`.

Pas de changement du texte du site. Pas de trading réel.
