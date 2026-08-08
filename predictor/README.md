# Aratea Weather Predictor — Kalshi POC

Moteur prédictif d'Aratea — testé en paper-trading sur les contrats Kalshi snow/rain, avant tout déploiement réel. Cette POC valide l'edge prédictif qui motive la suite du projet (DAO, mutuelle paramétrique).

## Objectif

Mesurer un **edge prédictif** sur des contrats météo Kalshi en mode simulation (aucun argent réel engagé).

Critère de succès : Brier score et accuracy meilleurs que les odds Kalshi closing, sur au moins une saison historique complète, sur au moins un type de contrat.

## Architecture

```
                         ┌─────────────────────┐
                         │  Kalshi Public API  │
                         │  (markets + odds)   │
                         └──────────┬──────────┘
                                    │
                                    ▼
   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
   │  Open-Meteo  │────────▶│   Predictor  │────────▶│  Simulation  │
   │  (forecast + │         │  (climato +  │         │   (ledger    │
   │  historical) │         │   ensemble)  │         │    CSV)      │
   └──────────────┘         └──────────────┘         └──────┬───────┘
                                                            │
                                                            ▼
                                                     ┌──────────────┐
                                                     │   Scoring    │
                                                     │  (Brier, ROI │
                                                     │   simulé)    │
                                                     └──────────────┘
```

**Étage 1 (en cours) :** baseline climatologique + ensemble forecast + paper trading.
**Étage 2 (plus tard) :** LLM en lecture de texte météo (NOAA discussions) → feature pour le predictor.

## Setup

```bash
# Depuis le dossier predictor/
python -m venv .venv
.venv\Scripts\activate   # Windows
.venv/bin/activate       # Linux / macOS

# Installation reproductible (recommandé) :
pip install -r requirements.lock --require-hashes

# Ou installation lâche (versions min seulement) :
pip install -r requirements.txt
```

**Reproductibilité des dépendances.** `requirements.lock` est généré par
[`pip-tools`](https://pip-tools.readthedocs.io/) à partir de
`requirements.txt`. Il épingle chaque dépendance transitive avec ses
hashs SHA-256, ce qui rend l'install reproductible et bloque la
substitution silencieuse d'un paquet vérolé.

Pour régénérer après une modification de `requirements.txt` :

```bash
pip install pip-tools
pip-compile --generate-hashes --output-file=predictor/requirements.lock predictor/requirements.txt
```

## Pipeline d'exécution

```bash
# 1. Récupérer les marchés météo Kalshi ouverts
python scripts/fetch_markets.py

# 2. Pour chaque marché, prédire P(OUI) avec la baseline climatologique
python scripts/predict.py --predictor climatology

# 3. Comparer aux prix marché et logger les paris simulés
python scripts/simulate.py

# 4. Une fois les marchés résolus, scorer les prédictions enregistrées
python scripts/score_forward.py
```

### Entrypoints de production vs ad-hoc / Production vs ad-hoc entrypoints

*FR : La séquence ci-dessus est la marche à suivre pour une exploration manuelle
(POC jour 0). En production, la boucle tourne de façon autonome via le cron
GitHub Actions `.github/workflows/daily-trading.yml`, tous les jours à 18:00 UTC.*

*EN : The sequence above is the manual, day-0 POC walkthrough. In production,
the loop runs autonomously via the `.github/workflows/daily-trading.yml`
GitHub Actions cron, daily at 18:00 UTC.*

**Entrypoints quotidiens (production) / Daily entrypoints (production) :**

| Script | Rôle FR | Role EN |
|---|---|---|
| `scripts/daily_run.py` | Capture d'apprentissage : `fetch_markets --all-weather` → `forward_predict` → `score_forward`. Alimente le dataset d'entraînement (`data/predictions/`, `data/scores/`). | Learning capture: `fetch_markets --all-weather` → `forward_predict` → `score_forward`. Feeds the training dataset (`data/predictions/`, `data/scores/`). |
| `scripts/daily_auto.py` | Paper-trading autonome : finalise les runs résolus, capture de nouveaux runs selon les seuils edge/spread configurés, reconstruit le manifeste du dashboard, commit + push. | Autonomous paper-trading: finalizes settled runs, captures new runs against the configured edge/spread thresholds, rebuilds the dashboard manifest, commits + pushes. |

Les deux scripts sont orchestrés dans cet ordre par le même job cron.
*Both scripts are orchestrated in that order by the same cron job.*

**Entrypoints ad-hoc / debug (usage manuel) / Ad-hoc, debug entrypoints (manual use) :**

- `scripts/live_run.py` — capture manuelle d'un snapshot multi-modèle sur un marché donné. / manual multi-model snapshot capture for a single market.
- `scripts/forward_predict.py` — appelé en interne par `daily_run.py` ; peut aussi être lancé isolément pour du debug. / called internally by `daily_run.py`; can also be run standalone for debugging.
- `scripts/finalize_run.py` — clôture manuelle d'un run une fois l'event résolu par Kalshi. / manual finalization of a run once Kalshi has settled the event.
- `scripts/backtest.py` — backtest historique sur des events déjà résolus (pas de trading live). / historical backtest against already-settled events (no live trading).

## Structure

```
predictor/
├── README.md
├── requirements.txt / requirements.lock
├── src/
│   ├── kalshi/          # Client API Kalshi
│   ├── forecast/        # Open-Meteo, NWS/NDFD
│   ├── predictors/      # climatology, ensemble, forecast_blend
│   ├── learning/        # feature engineering, dataset, modèle appris (v3)
│   └── microstructure/  # biais et distribution des marchés Kalshi
├── scripts/             # Entrypoints CLI (production + ad-hoc, cf. section suivante)
├── data/
│   ├── backfill/        # Données historiques rétro-collectées
│   ├── forecasts/       # Prévisions cachées
│   ├── predictions/     # Sorties forward_predict.py (training fuel)
│   ├── scores/          # Résolutions scorées
│   ├── geographic/      # Features géo statiques (OSM, USGS)
│   ├── audits/          # Journaux d'audit de résolution
│   └── ledger/          # Paris simulés (CSV)
├── runs/                # Runs live individuels (report.json par run)
├── runs_backtest/       # Sorties de backtest.py (schema v2-backtest)
├── runs_learning/       # Boucle champion/challenger + CHAMPION.json
├── tests/                # Suite de tests (pytest)
└── docs/                 # Notes de décision, rapports ponctuels
```

## Learned model — feature engineering / Modèle appris

*FR : Évolution des feature sets. EN : Feature-set history.*

---

### Feature sets — évolution / history

The predictor uses a trained logistic regression (L2) over a set of named features.
Each feature must carry an interpretable hypothesis; opaque or unnamed features are banned.
Le predictor utilise une régression logistique L2 entraînée sur des features nommées.
Chaque feature doit porter une hypothèse interprétable ; les features opaques sont interdites.

| Version | Features | Verdict | Raison / Reason |
|---------|----------|---------|-----------------|
| v0 | p_climatology, p_forecast_blend, p_ensemble, forecast_spread, days_ahead | ❌ NO-GO | Multicollinéarité : les trois proba-features transportent le même signal avec des coefficients compensatoires (+1.07 / −0.87 / −0.40). Collinearity: the three probability features carry one shared signal with compensating L2 coefficients. |
| v2 | v0 + 6 features géographiques statiques (OSM, USGS) | ❌ NO-GO | Features géo évaluées comme bruit additif (\|coef\| < 0.04). Geographic features measured as additive noise. |
| **v3** | **p_consensus, forecast_spread, days_ahead** | ✅ Actif | Correction collinéarité : collapse des trois proba en leur moyenne (p_consensus) + axe orthogonal disagreement (forecast_spread). Collinearity fix: three probability views collapsed into their mean; orthogonal disagreement axis kept as forecast_spread. |

---

### Détail de v3 / v3 detail

**`p_consensus`**
- FR : Moyenne des trois vues probabilistes (climatology, forecast_blend, ensemble). Fixe la collinéarité du bloc v0/v2 — un coefficient stable sur un signal agrégé vaut mieux que trois coefficients compensatoires sur des signaux corrélés.
- EN : Mean of the three correlated probability views. Fixes the v0/v2 collinearity — one stable coefficient on the aggregated signal beats three compensating coefficients on correlated inputs.

**`forecast_spread`**
- FR : Écart max–min entre les probabilités vendeur individuelles. Axe orthogonal à p_consensus : mesure le désaccord entre modèles, pas leur valeur centrale.
- EN : Max–min spread across vendor model probabilities. Orthogonal to p_consensus: measures inter-model disagreement, not the central estimate.

**`days_ahead`**
- FR : Horizon de prévision (jours entre la capture et la date cible). Signal faible mais non colinéaire.
- EN : Forecast horizon (days between capture and target date). Weak but non-collinear signal.

---

### Workflow de découverte / Discovery workflow

```
src/learning/features.py   ← feature extractors (named, hypothesized)
src/learning/FEATURES.md   ← registry: hypothesis | status | measured Brier delta
scripts/train_learned.py   ← train LR on resolved events; gate on promotable flag
scripts/_learning_loop.py  ← champion/challenger loop (local, gitignored): 
                              TRAIN → VALID → HOLDOUT (frozen)
```

FR : Chaque modification est testée en une seule itération (TRAIN/VALID), et la chaîne acceptée est validée **une seule fois** sur le HOLDOUT gelé — qui est le seul nombre sans biais dans le run. Les NO-GO sont consignés dans `FEATURES.md` pour la mémoire institutionnelle.

EN : Each modification is tested in one iteration (TRAIN/VALID), and the accepted chain is scored **once** on the frozen HOLDOUT — the only unbiased number in the run. NO-GO verdicts are recorded in `FEATURES.md` for institutional memory.

---

## État actuel / Current status

- [x] Bootstrap projet / Project bootstrap
- [x] Client Kalshi (lecture publique / public read)
- [x] Fetcher Open-Meteo
- [x] Predictor climatologique / Climatology predictor
- [x] Predictor ensemble (blend de modèles / model blend)
- [x] Simulateur paper-trading / Paper-trading simulator
- [x] Scoreur de résolutions / Resolution scorer
- [x] Modèle appris v3 (LR L2, features p_consensus + forecast_spread + days_ahead)
- [ ] Edge confirmé sur holdout (Brier modèle < Brier marché, sign-test p<0.05)

## Ce qu'on NE fait PAS dans cette phase

Pas de smart contract, pas de DAO, pas de bot live, pas de produit de mutuelle, pas d'ouverture de compte Kalshi, pas d'argent réel. Tout vient APRÈS la preuve d'edge.
