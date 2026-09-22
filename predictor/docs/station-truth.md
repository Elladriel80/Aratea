# Vérité station et skill hors marché / Station truth and market-free skill

**Date :** 2026-09-09 · **Portée :** predictor Phase 1 · **Origine :** note `pistes-amelioration-prediction-2026-09-09.md`, pistes A1 et A4.

## FR

### Le problème
Le predictor apprenait sur la mauvaise cible : la climatologie et le sigma étaient calculés sur ERA5 (grille 25 km, via Open-Meteo archive), alors que Kalshi résout sur le rapport climatologique quotidien (CLI) de la station ASOS. L'évaluation dépendait en plus de l'existence d'un marché coté, ce qui la bornait aux dates depuis avril 2026 et au lead J-1.

### Ce qui est ajouté
- `src/truth/iem_cli.py` : client de l'archive IEM des rapports CLI (`cli.py?station=KNYC&year=2026`), cache disque par année, mapping séries Kalshi → station → fuseau.
- `src/truth/lst_window.py` : fenêtre exacte du CLI (minuit à minuit en heure standard locale, jamais l'heure d'été). Toute agrégation horaire de prévision passe par là.
- `src/truth/synthetic_bins.py` : échelle de bins Kalshi (2 °F, queues) construite autour de la prévision, P(bin) gaussienne avec la correction d'arrondi ±0,5 °F.
- `src/truth/skill.py` : trois politiques scorées contre la vérité CLI (`raw` = production, `station_bias` = biais et sigma appris sur TRAIN par station/variable/lead, `climato` = CLI des années précédentes), split temporel, sign test par date.
- `src/weather/previous_runs.py` : client Previous Runs en version production (plages de dates, fuseau GMT, couverture mesurée).
- `scripts/build_station_truth.py` : collecte la vérité CLI des 18 stations et chiffre l'écart ERA5 vs CLI (`data/truth/era5_vs_cli.md`).
- `scripts/eval_station_skill.py` : backtest de skill hors marché (`data/truth/skill/skill_report.md`), paramètres de biais station (`station_bias.json`) et mémoire cumulative des prévisions agrégées (`forecast_points.json`).
- `.github/workflows/station-truth.yml` : exécution hebdomadaire sur le runner GitHub (réseau disponible), commit des sorties compactes.

### Ce que ça permet
1. Mesurer le biais ERA5 vs CLI par station et par mois : chiffrage du défaut, avant toute correction.
2. Mesurer le skill de la chaîne prévision → P(bin) par lead et par station sans attendre qu'un marché existe.
3. Obtenir des paramètres de correction station interprétables (deux nombres par station/variable/lead), prêts à être injectés dans `EnsemblePredictor` derrière un flag.
4. Ne plus perdre la fenêtre glissante Previous Runs : `forecast_points.json` fusionne à chaque run.

### Ce que ça ne fait pas
Pas de comparaison au marché (c'est le rôle de `_backfill_dataset.py`), pas de modification du predictor en production, pas de recalibration (NO-GO confirmé trois fois : l'apport ici est informationnel, pas cosmétique).

### Lancer en local
```bash
cd predictor
python scripts/build_station_truth.py --start-year 2020
python scripts/eval_station_skill.py
```
Réseau requis (IEM, Open-Meteo). Le workflow GitHub fait la même chose chaque lundi.

### Décision humaine à prendre ensuite
Si `skill_report.md` montre `station_bias` sous `raw` avec un sign test p < 0,05 sur ≥ 30 dates HOLDOUT, brancher la correction dans `EnsemblePredictor` (flag `ARATEA_ENS_STATION_BIAS`, défaut OFF) et relancer le backtest marché J-1.

## EN

### The problem
The predictor was learning against the wrong target: climatology and sigma came from ERA5 (25 km grid via Open-Meteo archive) while Kalshi settles on the station's NWS Daily Climate Report (CLI). Evaluation also required a quoted market, which limited it to dates since April 2026 and to the J-1 lead.

### What is added
IEM CLI client with yearly disk cache and series → station → timezone mapping; exact CLI window (local standard time, never daylight time); Kalshi-shaped synthetic bins with the ±0.5 °F rounding correction; three scoring policies (raw production, TRAIN-learned station bias, CLI climatology) with a temporal split and per-date sign test; a production-grade Previous Runs client; two scripts producing `data/truth/era5_vs_cli.md` and `data/truth/skill/skill_report.md` plus `station_bias.json`; a weekly GitHub workflow that runs them where network is available and commits the compact outputs, including the cumulative `forecast_points.json` memory.

### What it does not do
No market comparison (that stays in `_backfill_dataset.py`), no production predictor change, no recalibration (NO-GO confirmed three times; this is an information lever).

### Next human decision
If `skill_report.md` shows `station_bias` below `raw` with sign-test p < 0.05 over ≥ 30 HOLDOUT dates, wire the correction into `EnsemblePredictor` behind `ARATEA_ENS_STATION_BIAS` (default OFF) and rerun the J-1 market backtest.

---

## Résultats du premier run et activation du flag (2026-09-09) / First run results and flag activation

**Run hebdo #1** (18 stations, CLI 2020 → 2026-09-08, skill 2026-05-12 → 2026-09-07, HOLDOUT ≥ 2026-08-03, 36 dates) :

| Politique | Brier HOLDOUT hors marché |
|---|---|
| raw (production) | 0,1258 |
| station_bias | 0,1151 |
| climato CLI | 0,1273 |

station_bias bat raw sur 35 dates sur 36 (p < 0,0001). raw ne bat la climato que 22/36 (p = 0,12).

**Audit ERA5 vs CLI** (`data/truth/era5_vs_cli.md`) : ERA5 tombe sur le bon entier 7 à 29 % des jours et se trompe d'un bin complet (≥ 2 °F) 20 à 70 % des jours selon la station. Cible fausse confirmée.

**Backtest marché hors ligne** (`scripts/eval_station_bias_market.py`, captures live rejouées, biais point-in-time, issue par CLI, 8 613 bins, 63 dates) :

| lead | Brier raw | Brier station | Brier kalshi_mid |
|---|---|---|---|
| J0 (capture l'après-midi même) | 0,1453 | 0,1294 | 0,0771 |
| J-1 | 0,1463 | 0,1325 | 0,1282 |

station bat raw 54/63 dates. À J-1 l'écart au marché passe de +0,018 à +0,004. À J0 le marché a déjà vu la température de l'après-midi : hors d'atteinte sans observations temps réel (piste C1 de la note).

**Décision** : flag `ARATEA_ENS_STATION_BIAS=1` activé dans `daily-trading.yml` (PR #221). Table `station_bias.json` rafraîchie chaque lundi. Réversible en passant le flag à 0. Limite connue : biais appris sur une saison (mai-septembre), à surveiller au changement de saison via le rapport hebdo.

EN: first weekly run confirms the wrong-target diagnosis (ERA5 off by a full bin 20-70 % of days), station_bias beats the raw policy 35/36 holdout dates (Brier 0.1258 → 0.1151), and on live captures replayed offline it closes the J-1 gap to kalshi_mid from +0.018 to +0.004 (J0 stays out of reach without real-time observations). Flag enabled in daily-trading.yml, reversible, table refreshed weekly; known limit: single-season bias.

---

## Challenger `ensemble_members` (2026-09-09) / `ensemble_members` challenger

FR : Nouveau predictor `ensemble_members` (`src/predictors/ensemble_members.py`, client `src/weather/ensemble_api.py`) : P(bin) calculée sur les vrais membres d'ensemble Open-Meteo (ECMWF IFS 51, ECMWF AIFS ENS 51, GEFS 31 par défaut, réglable par `ARATEA_ENS_MEMBER_MODELS`), extrêmes journaliers dans la fenêtre LST du CLI, biais station si `ARATEA_ENS_STATION_BIAS=1`, lissage gaussien de 1 °F (`ARATEA_ENS_MEMBERS_KERNEL_F`), poids égal par modèle. Capturé chaque jour par `forward_predict` à côté de `ensemble` (défaut élargi), scoré par `score_forward`, comparé au marché sur ses propres lignes par `eval_station_bias_market.py` (tableau « Challenger ensemble_members »). Pas d'archive Previous Runs pour les ensembles : l'évaluation est forward uniquement, il faut compter 3 à 4 semaines de captures avant un verdict. Ne touche pas au champion.

EN : New shadow predictor built on real ensemble members (~130), CLI LST window, optional station bias, 1 °F kernel, equal model weight. Captured daily next to `ensemble`, scored by `score_forward`, compared to the market on its own rows. No archive exists for ensemble members, so the evaluation is forward-only: expect 3-4 weeks before a verdict. Champion untouched.

---

## Revue des stations de résolution (2026-09-09) / Resolution station review

FR : En cherchant pourquoi Dallas n'avait aucun rapport CLI sous KDAL, vérification des règles Kalshi (pages de marché) : **Chicago résout à Midway (KMDW), Houston à Hobby (KHOU), Dallas à DFW (KDFW)**. Le repo prévoyait et vérifiait à O'Hare, Intercontinental et Love Field : 25 à 40 km d'écart, climats différents (lac Michigan pour Chicago, baie de Galveston pour Houston). Corrigé dans `CITIES` (coordonnées de prévision), `SERIES_TO_STATION` / `NWS_STATIONS` (résolution), `CITY_TO_ICAO` (vérité CLI) et `LOCATION_KEY_TO_ICAO`. Conséquences : tous les Brier passés sur CHI, HOU et DAL mesuraient le mauvais marché ; la table `station_bias.json` n'a pas encore d'entrée KMDW / KHOU / KDFW (politique brute sur ces trois villes jusqu'au prochain run hebdo, qui les ajoutera). Les 15 autres villes sont confirmées par les règles (KNYC Central Park, KDEN, KMIA, KLAX, KPHX, KATL, KAUS, KSAT, KLAS, KMSP, KPHL, KSEA, KDCA, KBOS, KSFO). Test de verrouillage : `test_kalshi_resolution_stations_match_market_rules`.

EN : Kalshi rules name Chicago Midway (KMDW), Houston Hobby (KHOU) and DFW (KDFW); the repo forecast and verified at O'Hare, Intercontinental and Love Field (25-40 km apart, different microclimates). Fixed in forecast coordinates, resolution mapping and CLI truth mapping. Past Brier numbers for CHI/HOU/DAL measured the wrong market; `station_bias.json` gets KMDW/KHOU/KDFW entries at the next weekly run. Locked by a test.

---

## Histoire longue GHCN-Daily (2026-09-12) / Century station climatology

FR : Hypothèse du propriétaire : ~100 ans du thermomètre officiel, distribution par jour de calendrier, pente, et « fade » si le marché est plus sûr que l'histoire. Mesure dans `scripts/eval_century_climato.py`, note `docs/a1-climato-siecle-station-2026-09-12.md`, comptes `data/truth/century/`. GHCN-Daily (IDs USW appariés par coordonnées) est le même degré que le CLI sur les jours communs (≥ 99 %). Ce n'est pas un siècle partout (Midway 1997, Denver 1994, Austin trou 1971-1991). Brier histoire longue 0,1332 vs station_bias 0,1154 (36 jours A1). Fade : 695/2567 échelles, mais le marché a raison (0,0401 vs 0,2020 sur ces contrats, 63 jours). Champion inchangé.

EN : Owner hypothesis measured: long official-station history vs market tightness. GHCN matches CLI on overlap. Coverage is not 100 years at every airport. Long climatology loses to the city-corrected mix and to the market; fading a tight market vs history loses. Champion untouched.

FR (mutuelle, 2026-09-12) : le même fichier sert à compter chaleur (≥ 100 °F), gel (≤ 32 °F), pluie annuelle et le saut d'une année à l'autre. Note `docs/a1-climato-siecle-mutuelle-2026-09-12.md`, comptes `data/truth/century/mutual_tails.md`. Pas de produit, pas de prix. NYC 157 ans, Midway 28, Denver 30. Une année folle (saut typique ~1 °F, gros saut 2 à 3,6 °F) pèse plus qu'une décennie de pente. Champion toujours inchangé.

EN (mutual): same century files scored for heat / frost / dry-year tails and year-to-year swing. No product invented. Champion still untouched.

---

## Fenêtre d'hiver et Degré entier (2026-09-12) / Winter window and integer degree

FR : Les deux règles de paiement pas encore chiffrées le 12 septembre. Mesure A/B dans `scripts/eval_settlement_window_rounding.py` (A = `lst_date` de `lst_window.py` vs jour mural ; B = entier NWS et fenêtre ±0,5 °F de `synthetic_bins.py`). Note `docs/b2-fenetre-hiver-degre-entier-2026-09-12.md`, comptes `data/truth/settlement/`. ASOS horaire déjà là (2314 jours, 18 villes) : se tromper d'heure change le min 185 jours, le max 18 jours, la case de 2 °F 129 jours. Phoenix (pas d'heure d'été) : 0. METAR déjà entier sauf 44 / 56302 lectures ; ±0,5 °F ne déplace aucun des 4628 extrêmes. Champion inchangé.

EN : Settlement A/B for LST vs wall-clock day and integer vs half-degree. Hourly ASOS already in-repo. Wrong hour moves the daily min far more than the max. Official published values are already integers in this archive. Champion untouched.
