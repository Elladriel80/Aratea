# C3S multi-modèle : trois A/B hors ligne

**Date :** 7 octobre 2026
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

Cette note dit où on en est au 7 octobre 2026. La mesure a été
faite sur la box partagée (checkout
`/workspace/aratea-c3s-score`, commit 973a4ab). Le CSV n'existe
que là. Les chiffres ci-dessous sont recopiés. Ils ne sont pas
recalculés dans ce dépôt. `computed: true` pour ce run. Le bloc
SEAS5 de la PR 246 reste à part, `computed: false`.

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
Les vérités USDM, SPEI-6 et CHIRPS ont été réutilisées depuis le tree SEAS5 local, et elles sont absentes du tree de la PR 260.

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

## Résultat mesuré (box partagée)

Fichier :
`/workspace/cds-test/c3s-monthly/c3s_tp_monthly.csv`.
34560 lignes. 5 centres × 6912. 0 trous.
Tests sur la box : 33 réussis, 2 ignorés.
CDS non appelé. Le champion n'a pas changé.

Headline = CHIRPS MED seulement. India reste à part. Pas de C poolé.

### Mélange C3S (égale pondération)

| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A USDM | Midwest | 69 | 0.4348 | 0.0428 | -9.1537 | testée, ça n'aide pas |
| A USDM | Southwest | 69 | 0.5507 | 0.2561 | -1.1508 | testée, ça n'aide pas |
| B SPEI-6 | MED | 97 | 0.5155 | 0.0 | n/d | bloquée |
| B SPEI-6 | India | 97 | 0.5155 | 0.0 | n/d | bloquée |
| B SPEI-6 | US | 0 | n/d | n/d | n/d | bloquée |
| C CHIRPS | MED (headline) | 97 | 0.268 | 0.253 | -0.0593 | testée, ça n'aide pas |
| C CHIRPS | India | 97 | 0.3196 | 0.2507 | -0.275 | testée, ça n'aide pas |

### ECMWF-51 seul

| A/B | Région | N | Brier prévision | Brier climato | BSS | Verdict |
|---|---|---:|---:|---:|---:|---|
| A USDM | Midwest | 69 | 0.5507 | 0.0428 | -11.8614 | testée, ça n'aide pas |
| A USDM | Southwest | 69 | 0.5072 | 0.2561 | -0.981 | testée, ça n'aide pas |
| B SPEI-6 | MED | 97 | 0.5052 | 0.0 | n/d | bloquée |
| B SPEI-6 | India | 97 | 0.5155 | 0.0 | n/d | bloquée |
| B SPEI-6 | US | 0 | n/d | n/d | n/d | bloquée |
| C CHIRPS | MED (headline) | 97 | 0.2371 | 0.253 | 0.0629 | testée, ça aide |
| C CHIRPS | India | 97 | 0.299 | 0.2507 | -0.1928 | testée, ça n'aide pas |

Comparaison headline, CHIRPS MED : BSS mélange -0.0593, BSS
ECMWF-51 0.0629. Le mélange ne bat pas ECMWF-51.

SPEI-6 reste bloquée. Le Brier climato vaut 0. Il n'y a pas de
BSS SPEI. USDM n'aide pas. India CHIRPS n'aide pas.

C3S multi-modèle : testée, ça n'aide pas.
ECMWF-51 seul, sur ce CSV : testée, ça aide (CHIRPS MED seulement).
La baseline SEAS5 du catalogue reste celle de la PR 246. Ce n'est
pas ce recalcul.

## Décision

On ne change pas le modèle Kalshi en ligne.

Pourquoi : le mélange n'aide pas, et il ne bat pas ECMWF-51 sur
la seule headline (CHIRPS MED). Pas de promo.

## Comment relancer

Dans le dossier `predictor`, après le dépôt du CSV :

```
python scripts/eval_c3s_ab.py
```

Sans fichier, le même ordre tourne en mode bloqué et réécrit
`data/truth/c3s_ab/`. Le tableau de cette note est celui de la
box. Il ne faut pas le remplacer par un passage sans CSV.

Pas de changement du texte du site. Pas de trading réel.
