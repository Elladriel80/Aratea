# Phase 1 go / no-go — verdict mécanique (2026-06-03)

> **Statut : BROUILLON — en attente de validation humaine avant publication.**
> Ce document produit le **constat chiffré** et le **verdict mécanique** du
> critère figé. La décision business (capital réel / pivot / arrêt) n'est PAS
> prise ici — voir §7.
>
> Tous les chiffres sont régénérables : `python predictor/scripts/go_no_go_phase1.py`.

---

## FR

### 1. Le critère (cité, figé avant les résultats)

Source : [`predictor/runs/CONVENTION.md`](../runs/CONVENTION.md) §6. La Phase 1 est
validée **si et seulement si**, sur **N > 50 runs résolus en live** :

1. le Brier **moyen** du méta-ensemble est strictement inférieur à celui du
   **meilleur modèle individuel** sur les mêmes N événements ;
2. le Brier **moyen** du méta-ensemble est strictement inférieur à celui de la
   **climatologie** sur les mêmes N événements.

Les deux conditions doivent tenir. Le brief de session ajoute la
**significativité requise** (sign test 1-sided par-trade, p < 0,10), comme pour
la promotion d'un challenger. Les runs de backtest ne sont jamais substitués
aux runs live (§6, dernier paragraphe).

### 2. Les données

- **N = 115 runs résolus live.** Source : les `scoring.by_model` + `resolution`
  des fichiers [`predictor/runs/NNN/report.json`](../runs/) (115 runs portent un
  bloc de scoring complet et une résolution `yes`/`no` ; les autres répertoires
  sont des runs ouverts ou non résolus, exclus proprement).
- **Brier par modèle** : lu directement dans `scoring.by_model.<modèle>.brier`
  de chaque run (champion `vendor_ensemble`, challenger `learned_v2`, baseline
  marché `kalshi_mid_baseline`).
- **Climatologie** : elle **n'est pas loggée** dans le schéma v2. Elle est donc
  **recalculée** sur le même bin et la même date par `ClimatologyPredictor`
  (config `years_back=30, window_days=3`). Cette config est **validée** : sur le
  run 002 (qui logge `brier_climatology = 0,0237`), le recalcul redonne
  **exactement 0,0237** (p_climato = 0,154).

### 3. Tableau Brier (N = 115)

| Modèle | Brier **moyen** | Brier médian |
|---|---|---|
| **`vendor_ensemble`** (méta-ensemble, champion) | **0,1994** | 0,0335 |
| `kalshi_mid_baseline` (le marché) | **0,1853** | 0,1056 |
| `climatology` (recalcul 30/3) | 0,2269 | 0,0209 |
| `learned_v2` (challenger) | 0,2326 | 0,0661 |

*(Brier plus bas = meilleur. La forte différence moyenne ↔ médiane signale que
les moyennes sont tirées par une poignée d'événements à Brier catastrophique.)*

### 4. Conditions et significativité

Sign test 1-sided « le méta-ensemble a un Brier strictement plus bas » :

| Comparaison | Méta-ensemble gagne / perd | p-value | Significatif (p<0,10) ? |
|---|---|---|---|
| vs `learned_v2` | 67 / 48 | **0,0464** | ✅ oui |
| vs `kalshi_mid` (marché) | 57 / 58 | 0,5739 | ❌ non |
| vs `climatology` | **47 / 68** | 0,9801 | ❌ non (et le sens est *défavorable*) |

- **Condition 1 (vs meilleur modèle individuel).** Le meilleur modèle individuel
  par Brier moyen est le marché `kalshi_mid` (0,1853). Le méta-ensemble (0,1994)
  **ne le bat pas** (0,1994 > 0,1853 ; sign test non significatif). Même en
  excluant le marché et en ne retenant que `learned_v2`, le gain (significatif,
  p = 0,046) ne suffit pas seul, car la condition 2 échoue.
- **Condition 2 (vs climatologie).** En **moyenne** seulement, le méta-ensemble
  passe (0,1994 < 0,2269). Mais ce gain moyen est un **artefact d'outliers** : en
  **médiane** la climatologie est meilleure (0,0209 < 0,0335), et en tête-à-tête
  le méta-ensemble **perd 47 contre 68** (p = 0,98). La condition ne tient donc
  **pas** avec la significativité requise.

### 5. Verdict mécanique

> ## ⛔ NO-GO
>
> Le méta-ensemble **n'a pas démontré d'edge prédictif statistiquement robuste**
> sur N = 115 runs live :
> - il **ne bat pas le marché** (`kalshi_mid`) — pourtant défini dans
>   `CONVENTION` comme « le plancher qu'un modèle doit battre pour revendiquer un
>   edge » (Brier moyen 0,1994 > 0,1853 ; 57–58 ; p = 0,57) ;
> - il **ne bat pas la climatologie** de façon significative — son avantage en
>   moyenne s'inverse en médiane et en tête-à-tête (47–68 ; p = 0,98).
>
> La seule victoire nette est sur `learned_v2` (p = 0,046), ce qui ne valide
> aucune des deux conditions du §6.

*Lecture littérale stricte (moyenne seule, sans significativité) :* la condition 2
serait « techniquement vraie » (0,1994 < 0,2269) et la condition 1 dépendrait de
la définition de « meilleur modèle individuel ». Mais cette lecture repose
entièrement sur des outliers et s'effondre dès qu'on applique la médiane, le sign
test, ou qu'on inclut le marché. Le verdict honnête reste **NO-GO**.

### 6. Ce que ce verdict ne dit PAS (honnêteté méthodo)

- **Fenêtre temporelle étroite.** Les 115 runs couvrent ~mai–juin 2026 (une
  seule saison, surtout du `temp_min`). Aucune conclusion inter-saisonnière.
- **Biais de sélection de bin.** La stratégie ne capture que les bins centraux
  avec `|edge_vs_mid| ≥ 0,05` et spread serré : l'échantillon n'est pas un tirage
  neutre de tous les marchés.
- **Biais de venue Kalshi.** `kalshi_mid` est à la fois le baseline ET le marché
  qu'on cherche à battre ; « battre le marché » est le vrai test, pas un détail.
- **Moyenne vs médiane.** Le §6 parle de Brier *moyen* ; or les moyennes sont
  ici dominées par quelques événements extrêmes. Un critère sur la médiane ou un
  test de rang donnerait un classement différent (et tout aussi défavorable au
  méta-ensemble face à la climatologie).
- **Paper-only.** Aucune exécution réelle : ni slippage, ni microstructure, ni
  timing de règlement. Le Brier mesure la qualité prédictive, pas la rentabilité
  nette.
- **Ce n'est pas un échec du pipeline.** L'infrastructure (capture, résolution,
  scoring multi-modèles, dashboard) fonctionne ; c'est l'**edge** qui n'est pas
  démontré sur cet échantillon.

### 7. Options ouvertes → décision humaine (TODO-HUMAIN)

Le verdict mécanique est NO-GO. La suite est une **décision business** que cette
session ne prend pas. Trois options, avec leur déclencheur :

1. **Wind-down honnête du track predictor.** Déclencheur : si « battre le marché »
   est la condition non négociable et qu'aucune piste crédible ne reste. Le
   critère était écrit avant les résultats et ne se déplace pas (CONVENTION §6).
2. **Pivot Phase B (saisonnier / non-linéaire).** Déclencheur : si l'on pense que
   l'edge existe mais que le méta-ensemble linéaire est sous-optimal (cf.
   `PHASE_B_SCAFFOLDING.md`, gate G1 non franchie : BSS > 0,05 jamais atteint).
   À noter : la piste *climato windowed* a déjà été fermée (PIVOT_REJETE,
   décision du 2026-06-02).
3. **Continuer à accumuler N en changeant une variable** (univers de villes,
   horizon, features v3 `p_consensus`) avant de retrancher. Déclencheur : si l'on
   juge l'échantillon trop étroit/saisonnier pour conclure définitivement —
   mais sans déplacer le critère §6, qui reste un NO-GO sur les données actuelles.

**Aucune position en capital réel n'est ouverte ni recommandée par ce document.**

---

## EN

### 1. The criterion (quoted, frozen before results)

Source: [`predictor/runs/CONVENTION.md`](../runs/CONVENTION.md) §6. Phase 1 is
validated **if and only if**, over **N > 50 resolved live runs**:

1. the meta-ensemble's **mean** Brier is strictly lower than the **best
   individual model's** over the same N events;
2. the meta-ensemble's **mean** Brier is strictly lower than **climatology's**
   over the same N events.

Both must hold. The session brief adds the **required significance** (1-sided
per-trade sign test, p < 0.10), as used for challenger promotion. Backtest runs
are never substituted for live runs (§6, last paragraph).

### 2. The data

- **N = 115 resolved live runs.** Source: the `scoring.by_model` + `resolution`
  blocks of [`predictor/runs/NNN/report.json`](../runs/). Other directories are
  open/unresolved runs, cleanly excluded.
- **Per-model Brier**: read straight from `scoring.by_model.<model>.brier`
  (champion `vendor_ensemble`, challenger `learned_v2`, market baseline
  `kalshi_mid_baseline`).
- **Climatology**: **not logged** in schema v2, so **recomputed** on the same
  bin/date with `ClimatologyPredictor` (`years_back=30, window_days=3`). Config
  **validated**: on run 002 (which logs `brier_climatology = 0.0237`) the
  recompute returns **exactly 0.0237** (p_climato = 0.154).

### 3. Brier table (N = 115)

| Model | **Mean** Brier | Median Brier |
|---|---|---|
| **`vendor_ensemble`** (meta-ensemble, champion) | **0.1994** | 0.0335 |
| `kalshi_mid_baseline` (the market) | **0.1853** | 0.1056 |
| `climatology` (30/3 recompute) | 0.2269 | 0.0209 |
| `learned_v2` (challenger) | 0.2326 | 0.0661 |

*(Lower Brier = better. The large mean↔median gap shows the means are dragged by
a handful of catastrophic-Brier events.)*

### 4. Conditions and significance

1-sided sign test, "meta-ensemble has strictly lower Brier":

| Comparison | Ensemble wins / losses | p-value | Significant (p<0.10)? |
|---|---|---|---|
| vs `learned_v2` | 67 / 48 | **0.0464** | ✅ yes |
| vs `kalshi_mid` (market) | 57 / 58 | 0.5739 | ❌ no |
| vs `climatology` | **47 / 68** | 0.9801 | ❌ no (and the sign is *adverse*) |

- **Condition 1 (vs best individual model).** Best individual model by mean Brier
  is the market `kalshi_mid` (0.1853). The meta-ensemble (0.1994) **does not beat
  it** (0.1994 > 0.1853; sign test n.s.). Even excluding the market and keeping
  only `learned_v2`, the (significant) win is not enough on its own, because
  condition 2 fails.
- **Condition 2 (vs climatology).** On the **mean** only, the meta-ensemble passes
  (0.1994 < 0.2269). But that mean edge is an **outlier artifact**: on the
  **median**, climatology is better (0.0209 < 0.0335), and head-to-head the
  meta-ensemble **loses 47 to 68** (p = 0.98). The condition does **not** hold
  with the required significance.

### 5. Mechanical verdict

> ## ⛔ NO-GO
>
> Over N = 115 live runs the meta-ensemble shows **no statistically robust
> predictive edge**:
> - it **does not beat the market** (`kalshi_mid`) — which `CONVENTION` itself
>   defines as "the floor a model must beat to claim any edge" (mean Brier
>   0.1994 > 0.1853; 57–58; p = 0.57);
> - it **does not significantly beat climatology** — its mean advantage reverses
>   on the median and head-to-head (47–68; p = 0.98).
>
> Its only clean win is over `learned_v2` (p = 0.046), which validates neither §6
> condition.

*Strict literal reading (mean only, no significance):* condition 2 would be
"technically true" (0.1994 < 0.2269) and condition 1 would hinge on the
definition of "best individual model." But that reading rests entirely on
outliers and collapses under the median, the sign test, or once the market is
included. The honest verdict stays **NO-GO**.

### 6. What this verdict does NOT say (methodological honesty)

- **Narrow time window.** The 115 runs span ~May–June 2026 (one season, mostly
  `temp_min`). No cross-seasonal claim.
- **Bin-selection bias.** The strategy only captures central bins with
  `|edge_vs_mid| ≥ 0.05` and tight spread — not a neutral draw of all markets.
- **Kalshi venue bias.** `kalshi_mid` is both the baseline AND the market we try
  to beat; "beating the market" is the real test, not a side note.
- **Mean vs median.** §6 uses *mean* Brier; here means are dominated by a few
  extreme events. A median- or rank-based criterion would rank differently (and
  just as unfavourably for the meta-ensemble vs climatology).
- **Paper-only.** No live execution: no slippage, microstructure, or settlement
  timing. Brier measures predictive quality, not net profitability.
- **This is not a pipeline failure.** The infrastructure (capture, resolution,
  multi-model scoring, dashboard) works; it is the **edge** that is not
  demonstrated on this sample.

### 7. Open options → human decision (TODO-HUMAN)

The mechanical verdict is NO-GO. What follows is a **business decision** this
session does not take. Three options, with triggers:

1. **Honest wind-down of the predictor track.** Trigger: if "beat the market" is
   the non-negotiable bar and no credible lead remains. The criterion was written
   before the results and does not move (CONVENTION §6).
2. **Pivot to Phase B (seasonal / non-linear).** Trigger: if the edge is believed
   to exist but the linear meta-ensemble is suboptimal (cf.
   `PHASE_B_SCAFFOLDING.md`, gate G1 not crossed: BSS > 0.05 never reached). Note:
   the *windowed climatology* lead is already closed (PIVOT_REJECTED, 2026-06-02).
3. **Keep accumulating N while changing one variable** (city universe, horizon,
   v3 `p_consensus` features) before cutting. Trigger: if the sample is judged too
   narrow/seasonal to conclude definitively — without moving the §6 criterion,
   which remains a NO-GO on current data.

**No real-money position is opened or recommended by this document.**
