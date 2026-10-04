# C3S multi-modèle : trois A/B hors ligne

**Date :** 4 octobre 2026
**Pour :** le propriétaire (pas un document technique)

Mesure Phase 2. Nom stable : **C3S multi-modèle**.
Trois tests séparés, les mêmes que SEAS5 (PR 246), chacun contre
la climato :

- A) C3S multi-modèle contre US Drought Monitor (Midwest, Southwest)
- B) C3S multi-modèle contre SPEI-6 (Méditerranée, Inde, US)
- C) C3S multi-modèle contre CHIRPS pluie (Méditerranée, Inde)

La priorité, c'est C. La headline, c'est **CHIRPS MED seulement**.
L'Inde reste un compte à part. On ne titre jamais un C qui mélange
MED et India.

Le mélange est la moyenne équipondérée des centres présents, pour
la même région, la même année, le même mois d'init et le même lead.
ECMWF système 51 (SEAS5) est aussi noté seul, pour voir si le
mélange le bat. Un centre qui manque est un trou. On ne le remplit
pas.

Cette note dit où on en est. Le CSV du PM n'est pas sur cette
machine. La mesure est **bloquée**. Aucun BSS C3S n'a été écrit.
Le site public n'a pas changé. Le modèle Kalshi en ligne n'a pas
changé. Aucun pari avec de l'argent réel. On n'a pas appelé CDS.
La clé Copernicus reste sur la machine du PM.

## Pourquoi on n'appelle pas CDS

Un agent cloud ne doit pas ouvrir Copernicus. Le PM télécharge les
centres chez lui, puis dépose un fichier déjà réduit. Ce dépôt ne
contient pas de clé.

## Où poser le fichier

Le script lit **d'abord** :

`/workspace/cds-test/c3s-monthly/c3s_tp_monthly.csv`

S'il n'est pas là :

`predictor/data/forecasts/c3s/c3s_tp_monthly.csv`

Des NetCDF à côté du CSV sont ignorés. On ne les décode pas.
L'exemple `c3s_tp_monthly.csv.example` n'est qu'un en-tête. Ce
n'est pas une prévision.

Colonnes exactes :

| Colonne | Sens |
|---|---|
| origin | `meteo_france`, `dwd`, `cmcc`, `ncep`, `ecmwf` |
| system | numéro de système C3S |
| region | labels PM : `MED`, `Midwest`, `Southwest`, `India` |
| year | année de l'init |
| init_month | mois d'init, 1 à 12 |
| lead_month | lead C3S, 1 = le mois d'init |
| tp_mean_mm | pluie moyenne d'ensemble, mm par mois |
| n_members | gardé, pas utilisé comme poids |
| n_cells | gardé, pas utilisé comme poids |

## Centres

| Origine | Système | Nom |
|---|---:|---|
| meteo_france | 8 | Météo-France |
| dwd | 21 | DWD |
| cmcc | 35 | CMCC |
| ncep | 2 | NCEP |
| ecmwf | 51 | ECMWF SEAS5 |

La première fournée d'années est 1993-2016. Une année absente est
signalée. Elle n'est pas inventée. Les saisons qui sont là peuvent
quand même être notées.

`SEAS5` avec le système 51 est lu comme ECMWF 51. Si cette ligne
n'est pas dans le CSV C3S, ECMWF-51 reste un trou. On n'ouvre pas
le CSV SEAS5 pour le copier.

Le poids est un par centre. Cent membres d'un côté et un membre de
l'autre ne changent pas la moyenne.

## Les vérités, inchangées

Ce sont celles des PR 240, 243 et 244, déjà utilisées pour SEAS5.

| A/B | Fichier | Événement |
|---|---|---|
| A | `data/truth/usdm/usdm_seasons.csv` | D2+ ≥ 30 % |
| B | `data/truth/spei/spei6_monthly.csv` | SPEI-6 moyen ≤ -1,5 |
| C | `data/truth/chirps/chirps_monthly.csv` | pluie sous la climato leave-one-out du même type de saison |

## La règle, la même que PR 246

Au moins **10 saisons** par région. Sinon : bloquée, avec le N
mesuré, sans BSS inventé.

Si N ≥ 10 et BSS > 0,05 contre la climato : testée, ça aide.
Sinon : testée, ça n'aide pas.

Climato = fréquence leave-one-out des autres saisons. Si cette
erreur vaut 0, le BSS n'existe pas. On l'écrit n/d.

MED et India ne sont pas additionnés. Midwest et Southwest non plus.

## Ce que SEAS5 a déjà montré

Mesure publiée dans la PR 246 (commit aa8d61f). Ce n'est pas un
nouveau calcul. On la rappelle parce que c'est la barre. On ne la
recopie pas dans les cases C3S.

| A/B | Région | N | BSS | Verdict |
|---|---|---:|---:|---|
| A USDM | Midwest | 97 | -16,8565 | testée, ça n'aide pas |
| A USDM | Southwest | 97 | -0,9844 | testée, ça n'aide pas |
| B SPEI-6 | MED | 123 | n/d | bloquée |
| B SPEI-6 | India | 123 | n/d | bloquée |
| B SPEI-6 | US | 0 | n/d | bloquée |
| C CHIRPS | MED (headline) | 125 | 0,0552 | testée, ça aide |
| C CHIRPS | India | 125 | -0,0707 | testée, ça n'aide pas |

SPEI-6 est bloquée parce que le Brier de la climato vaut 0 au
seuil ≤ -1,5 après la moyenne spatiale. Il n'y a pas de BSS SPEI.
On n'en invente pas un.

SEAS5 aide **MED seulement**. L'Inde CHIRPS n'aide pas. USDM n'aide
pas. On ne pool pas MED et India.

## Résultat de ce passage

Le 4 octobre 2026, le CSV C3S n'est pas sur la machine. Les trois
A/B sont bloqués. N = 0. BSS = n/d. Les cinq centres sont des
trous, parce que le fichier n'est pas là.

On ne dit pas que le mélange bat SEAS5. On ne dit pas qu'il perd.
La comparaison CHIRPS MED est bloquée, elle aussi.

| A/B | Région | N | BSS | Verdict |
|---|---|---:|---:|---|
| A, B, C | toutes | 0 | n/d | bloquée |
| ECMWF-51 seul | toutes | 0 | n/d | bloquée (trou) |
| Mélange contre ECMWF-51, CHIRPS MED | MED | 0 | n/d | comparaison bloquée |

C3S multi-modèle : bloquée.
Sécheresse US : bloquée.
La baseline SEAS5 du catalogue reste celle de la PR 246
(CHIRPS MED seulement). Ce n'est pas un recalcul.

## Décision

On ne change pas le modèle Kalshi en ligne.

Pourquoi : il n'y a pas encore de score C3S. La seule mesure
saisonnière publiée est SEAS5, et elle n'a pas été promue. Pas de
promo tant que le CSV n'a pas été noté avec la règle ci-dessus.

## Comment relancer

Dans le dossier `predictor`, après le dépôt du CSV :

```
python scripts/eval_c3s_ab.py
```

Sans fichier, le même ordre tourne en mode bloqué. Les comptes
sont dans `data/truth/c3s_ab/`.

Pas de changement du texte du site. Pas de trading réel.
