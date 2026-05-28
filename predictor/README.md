     1|# Aratea Weather Predictor — Kalshi POC
     2|
     3|Moteur prédictif d'Aratea — testé en paper-trading sur les contrats Kalshi snow/rain, avant tout déploiement réel. Cette POC valide l'edge prédictif qui motive la suite du projet (DAO, mutuelle paramétrique).
     4|
     5|## Objectif
     6|
     7|Mesurer un **edge prédictif** sur des contrats météo Kalshi en mode simulation (aucun argent réel engagé).
     8|
     9|Critère de succès : Brier score et accuracy meilleurs que les odds Kalshi closing, sur au moins une saison historique complète, sur au moins un type de contrat.
    10|
    11|## Architecture
    12|
    13|```
    14|                         ┌─────────────────────┐
    15|                         │  Kalshi Public API  │
    16|                         │  (markets + odds)   │
    17|                         └──────────┬──────────┘
    18|                                    │
    19|                                    ▼
    20|   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
    21|   │  Open-Meteo  │────────▶│   Predictor  │────────▶│  Simulation  │
    22|   │  (forecast + │         │  (climato +  │         │   (ledger    │
    23|   │  historical) │         │   ensemble)  │         │    CSV)      │
    24|   └──────────────┘         └──────────────┘         └──────┬───────┘
    25|                                                            │
    26|                                                            ▼
    27|                                                     ┌──────────────┐
    28|                                                     │   Scoring    │
    29|                                                     │  (Brier, ROI │
    30|                                                     │   simulé)    │
    31|                                                     └──────────────┘
    32|```
    33|
    34|**Étage 1 (en cours) :** baseline climatologique + ensemble forecast + paper trading.
    35|**Étage 2 (plus tard) :** LLM en lecture de texte météo (NOAA discussions) → feature pour le predictor.
    36|
    37|## Setup
    38|
    39|```bash
    40|# Depuis le dossier predictor/
    41|python -m venv .venv
    42|.venv\Scripts\activate   # Windows
    43|.venv/bin/activate       # Linux / macOS
    44|
    45|# Installation reproductible (recommandé) :
    46|pip install -r requirements.lock --require-hashes
    47|
    48|# Ou installation lâche (versions min seulement) :
    49|pip install -r requirements.txt
    50|```
    51|
    52|**Reproductibilité des dépendances.** `requirements.lock` est généré par
    53|[`pip-tools`](https://pip-tools.readthedocs.io/) à partir de
    54|`requirements.txt`. Il épingle chaque dépendance transitive avec ses
    55|hashs SHA-256, ce qui rend l'install reproductible et bloque la
    56|substitution silencieuse d'un paquet vérolé.
    57|
    58|Pour régénérer après une modification de `requirements.txt` :
    59|
    60|```bash
    61|pip install pip-tools
    62|pip-compile --generate-hashes --output-file=predictor/requirements.lock predictor/requirements.txt
    63|```
    64|
    65|## Pipeline d'exécution
    66|
    67|### Quotidien (automatisé via GitHub Actions)
    68|
    69|Le pipeline quotidien est exécuté automatiquement via `.github/workflows/daily-trading.yml` :
    70|
    71|```bash
    72|# Entrypoint principal — exécute le cycle complet
    73|python scripts/daily_auto.py
    74|```
    75|
    76|Ce script orchestre :
    77|1. `fetch_markets.py` — récupère les marchés Kalshi ouverts
    78|2. `fetch_forecast.py` — récupère les prévisions Open-Meteo
    79|3. `predict.py` — génère les prédictions (climatology + ensemble)
    80|4. `simulate.py` — simule les paris et enregistre dans le ledger
    81|5. `score_forward.py` — score les prédictions résolues
    82|6. `finalize_run.py` — finalise le run et met à jour les métriques
    83|
    84|### Ad-hoc / Debug
    85|
    86|```bash
    87|# Backtesting sur données historiques
    88|python scripts/backtest.py
    89|
    90|# Exécution live (sans GitHub Actions)
    91|python scripts/live_run.py
    92|
    93|# Entraînement du modèle learned challenger
    94|python scripts/train_learned.py
    95|
    96|# Prédiction forward sur nouveaux marchés
    97|python scripts/forward_predict.py
    98|```
    99|
   100|## Structure
   101|
   102|```
   103|predictor/
   104|├── README.md
   105|├── requirements.txt
   106|├── requirements.lock
   107|├── src/
   108|│   ├── kalshi/         # Client API Kalshi
   109|│   ├── weather/        # Open-Meteo, NOAA
   110|│   ├── predictors/     # climatology, ensemble, hybrid
   111|│   └── simulation/     # paper trading + scoring
   112|├── scripts/            # Entrypoints CLI
   113|│   ├── daily_auto.py   # Entrypoint quotidien (GitHub Actions)
   114|│   ├── backtest.py     # Backtesting historique
   115|│   ├── live_run.py     # Exécution live
   116|│   ├── train_learned.py # Entraînement modèle learned
   117|│   ├── forward_predict.py # Prédiction forward
   118|│   └── finalize_run.py # Finalisation des runs
   119|├── data/
   120|│   ├── markets/        # Snapshots des marchés (JSON)
   121|│   ├── forecasts/      # Prévisions cachées
   122|│   └── ledger/         # Paris simulés (CSV)
   123|├── runs/               # Résultats des runs quotidiens
   124|├── runs_backtest/      # Résultats des backtests
   125|├── runs_learning/      # Résultats de l'entraînement
   126|├── tests/              # Tests unitaires
   127|└── docs/               # Documentation additionnelle
   128|```
   129|
   130|## État actuel
   131|
   132|- [x] Bootstrap projet
   133|- [x] Client Kalshi (lecture publique)
   134|- [x] Fetcher Open-Meteo
   135|- [x] Predictor climatologique
   136|- [x] Simulateur paper-trading
   137|- [x] Scoreur de résolutions
   138|- [x] Pipeline quotidien automatisé (GitHub Actions)
   139|- [x] Modèle learned challenger (entraînement)
   140|- [x] Backtesting historique
   141|- [x] Dashboard manifest builder
   142|
   143|## Ce qu'on NE fait PAS dans cette phase
   144|
   145|Pas de smart contract, pas de DAO, pas de bot live, pas de produit de mutuelle, pas d'ouverture de compte Kalshi, pas d'argent réel. Tout vient APRÈS la preuve d'edge.
   146|