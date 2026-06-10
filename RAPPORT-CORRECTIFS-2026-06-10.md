# Rapport — correctifs revue de code 2026-06-10

Branche : `fix/revue-2026-06-10` (partie de `main` à jour = `origin/main` @ `f6eb92d`).
18 correctifs, un commit par item (préfixe `fix(scope):`), tests par item.

> Note de démarrage (problème rencontré, hors périmètre des correctifs) : le `git pull`
> initial a été bloqué par un **`.git/index.lock` périmé** (taille 0, daté du 6 juin, soit
> 4 jours, aucun process git actif). Supprimé pour débloquer le fast-forward. Aucune
> donnée perdue.
>
> Working tree : des modifications WIP non liées préexistaient (`ROADMAP.md`, `STATUS.md`,
> `predictor/data/ledger/paper_bets_backtest.csv`, `rounds/agent/PROMPT*.md`,
> `rounds/scripts/collect_github_activity.py`). Elles ont été **laissées intactes** — seuls
> les fichiers de chaque correctif ont été stagés explicitement. Les fichiers non suivis
> `predictor/scripts/_aggregate_sfo_high.py`, `rounds/scripts/sanitize.py`,
> `rounds/scripts/test_sanitize.py` (référencés par la revue) sont devenus trackés via leurs
> commits respectifs (A1, D3).

---

## Lot A — Predictor

### A1. Dédup backtest par ticker
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `collect()` (`_aggregate_sfo_high.py`) agrégeait tous les
  `report.json` sans dédup ; `_append_backtest_ledger_row` (`backtest.py`) faisait un append
  aveugle ; `_backtest_ledger_summary` (`build_dashboard_manifest.py`) comptait des lignes.
  Une relance du backtest comptait chaque marché plusieurs fois → N/Brier/BSS et
  `n_backtest_strict` gonflables.
- **Fichiers modifiés** :
  - `predictor/scripts/_aggregate_sfo_high.py:30` (`collect`) : dédup par `market_ticker`,
    garde le replay au `ts_replay_utc` max (comparaison lexicographique du format ISO).
  - `predictor/scripts/backtest.py:249` (`_append_backtest_ledger_row`) : upsert par
    `market_ticker` (réécrit le ledger, drop l'ancienne ligne du même ticker).
  - `predictor/scripts/build_dashboard_manifest.py:546` (`_backtest_ledger_summary`) :
    `n_total`/`n_strict_point_in_time`/`n_naive_excluded` comptés sur **tickers uniques** ;
    `by_mode` reste un comptage de lignes brut (informationnel).
- **Tests** : `predictor/tests/test_backtest_dedup.py` (3 tests) — agréger deux fois le même
  run laisse N inchangé sur les trois chemins. ✅
- **Effets de bord** : `_append_backtest_ledger_row` réécrit tout le CSV à chaque appel
  (O(n) par ligne, négligeable pour quelques centaines de lignes de backtest).

### A2. `LearnedPredictor` honore le pin de `CHAMPION.json`
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `_find_latest_run_json` renvoyait le dernier
  `runs_learning/*/run.json` (`20260606T070428Z`, v3) alors que `CHAMPION.json` épingle
  `learned_v2` à `trained_at = 20260512T134515Z`. Les Brier shadow « learned_v2 »
  mesuraient un autre modèle.
- **Fichiers modifiés** :
  - `predictor/src/predictors/learned.py:38` : `_find_latest_run_json` remplacé par
    `_resolve_run_json_from_registry` (résout `runs_learning/<trained_at>/run.json` depuis
    le param `trained_at` ou, à défaut, depuis `CHAMPION.json`) + helper
    `_learned_trained_at_from_registry`. `__init__` prend un param `trained_at` ; plus de
    fallback silencieux « dernier run » → erreur explicite (`FileNotFoundError`/`ValueError`)
    si non résolvable.
  - `predictor/scripts/live_run.py:143` : instancie `LearnedPredictor(trained_at=
    model_meta.get("trained_at"), …)`.
- **Tests** : `predictor/tests/test_learned_pin.py` (5 tests) — avec le run récent
  non-promotable présent, c'est bien le run épinglé qui est chargé ; pin manquant ou cassé
  lève. ✅
- **Effets de bord** : si `CHAMPION.json` pointe un `trained_at` dont le dossier n'existe pas,
  `LearnedPredictor` lève désormais au lieu de charger silencieusement autre chose — c'est
  l'effet voulu (fail-loud). Le script manuel `scripts/test_learned_inference.py` (réseau,
  non collecté par pytest) bénéficie de la même résolution.

### A3. Normalisation des probabilités unifiée
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `backtest.py` renormalisait sur les bins centraux (`/s`),
  `simulate.py` sur tous les bins (`/total`), `daily_auto.py` était brut. Le Brier backtesté
  ne mesurait pas le modèle déployé.
- **Fichiers modifiés** :
  - Nouveau `predictor/src/predictors/normalize.py` : `normalize_event_probs` — convention
    LIVE (`daily_auto`) = P(YES) brute par bin, **scoring inconditionnel**, sans
    renormalisation mutuellement exclusive.
  - `predictor/scripts/backtest.py:380` : suppression de la renorm `/s`, route par
    `normalize_event_probs`. Le filtre bins centraux (`strike_type=="between"`) est conservé
    (aligné sur `daily_auto._select_target_bins:346`) et documenté : tails exclus, survivants
    scorés inconditionnellement sur leur P(YES) brute.
  - `predictor/scripts/simulate.py:89` : suppression de la renorm `/total`, route par la même
    fonction.
  - `predictor/scripts/daily_auto.py:709` : route les probas brutes par `normalize_event_probs`
    (identité) pour ancrer la convention au site live.
- **Tests** : `predictor/tests/test_normalize_convention.py` (3 tests) — fonction
  inconditionnelle (somme ≠ 1 préservée) ; les trois mappings d'appel donnent la même sortie. ✅
- **Effets de bord** : **changement numérique attendu** du Brier/BSS backtesté et des probas
  de `simulate` (les valeurs renormalisées étaient différentes du live). C'est l'objectif :
  mesurer le modèle réellement déployé. Toute campagne backtest antérieure doit être relancée
  avant de comparer à la gate.

### A4. Kelly correct
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `sizing.py` calculait `f = edge/b = (p−px)·px/(1−px) =
  Kelly·px` (sous-mise d'un facteur px).
- **Fichiers modifiés** :
  - `predictor/src/simulation/sizing.py:53` : YES → `f* = (p−px)/(1−px)` ; NO →
    `(p_no−px_no)/(1−px_no)`. `px` est clampé à `[0.01, 0.99]` (l.51) donc le dénominateur ne
    s'annule jamais. `kelly_fraction` et `max_fraction_per_bet` inchangés.
- **Tests** : `predictor/tests/test_kelly_sizing.py` (6 tests) — cas chiffré p=0.6, px=0.5 →
  f\*=0.2 ; symétrie NO ; rapport 1/px vs l'ancienne formule ; caps toujours appliqués. Les
  tests de caps existants (`test_portfolio_heat.py`, etc.) restent verts (edge énorme → cap
  binding dans les deux formules). ✅
- **Effets de bord & impact heat (demandé)** : à edge donné, les mises **augmentent d'un
  facteur 1/px** (ex. px=0.5 → ×2 ; px=0.25 → ×4) tant que le cap `max_fraction_per_bet`
  (5 %) ou les caps heat/cluster ne bindent pas. Le calibrage heat de Phase 1 raisonnait sur
  des fractions sous-évaluées : la heat réelle par pari sera plus élevée et le cap per-trade
  sera atteint plus souvent (refus purs plus fréquents).
  - **Ajustement compensatoire proposé (NON appliqué)** : pour neutraliser approximativement
    l'inflation pendant la fenêtre de re-calibrage, multiplier `kelly_fraction` (actuellement
    0.25) par le px̄ moyen des paris (sur l'historique, px̄ ≈ 0.4–0.5 d'après les entrées au
    mid). Soit `kelly_fraction ≈ 0.10–0.125` pour retrouver l'ordre de grandeur des mises
    pré-correctif, le temps de re-mesurer la heat sur données fraîches, puis remonter
    progressivement. À décider par un humain (impacte directement l'exposition).

### A5. NYC → station de résolution KNYC
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `open_meteo.py:44` avait JFK (40.6413, −73.7781) alors que
  `src/kalshi/resolution.py:57` résout à Central Park (KNYC, 40.7794, −73.9692).
- **Fichiers modifiés** :
  - `predictor/src/weather/open_meteo.py:44` : `CITIES["NYC"]` → `lat 40.7794, lon −73.9692`,
    label `"Central Park (KNYC)"`.
- **Cache (vérifié, demandé)** : les **trois** clés de cache open-meteo incluent
  `{lat:.4f}_{lon:.4f}` (`open_meteo.py:222`, `:299`, `:343`). Changer les coordonnées change
  toutes les clés → **aucun ancien cache JFK n'est réutilisé**. Les fichiers
  `data/forecasts/*40.6413_-73.7781*` (non suivis) deviennent orphelins inertes ; pas
  d'invalidation nécessaire (suppression optionnelle, non faite car fichiers non créés par
  moi).
- **Tests** : `predictor/tests/test_nyc_station.py` (3 tests) — coords NYC == station de
  résolution `CLINYC`/`KNYC`, plus aucune trace de JFK. ✅
- **Effets de bord** : la climato/forecast NYC seront refetchés aux coords Central Park (biais
  côtier ~17 km supprimé). Les prédictions NYC antérieures (JFK) ne sont pas comparables aux
  nouvelles.

### A6. `simulate.py` idempotent + heat fantôme
- **Statut** : **corrigé différemment** (voir justification).
- **Constat vérifié ?** : partiellement. `simulate.py` écrivait bien dans le ledger live
  partagé (`Ledger()` → `data/ledger/paper_bets.csv`), non idempotent. MAIS l'état actuel du
  ledger ne contient **aucune ligne phantom non résolue** issue de simulate : sur 204 lignes,
  19 non résolues correspondent toutes à un `runs/<NNN>/report.json` (paris live légitimes en
  attente de settlement) ; 1 seule ligne orpheline (bet_id absent des runs) et elle est
  **résolue** (inerte pour la heat). Le risque est donc surtout *going-forward*.
- **Choix** : plutôt qu'un tag `source=simulate` (fragile : deux writers au schéma divergent —
  `live_run._append_ledger_row:228` a un header **hardcodé** distinct de `Ledger.append`, une
  colonne ajoutée désaligne le CSV) ou un script de nettoyage (≈ no-op vu 0 phantom),
  `simulate` écrit désormais dans un **ledger dédié** `paper_bets_simulate.csv`. Ses lignes
  sont donc physiquement absentes du ledger live → exclues de `PortfolioHeat.from_ledger` et
  des compteurs du manifest, sans toucher au schéma partagé. C'est l'esprit de l'option
  « exclu de from_ledger ».
- **Fichiers modifiés** :
  - `predictor/scripts/simulate.py` : `SIMULATE_LEDGER_PATH = LEDGER_DIR/"paper_bets_simulate.csv"`,
    `Ledger(SIMULATE_LEDGER_PATH)` ; helper `_open_bet_keys` + dédup avant append par
    `(event_ticker, market_ticker)` (même granularité que
    `daily_auto._already_captured_bin:390`) → idempotent sur re-run.
- **Tests** : `predictor/tests/test_simulate_idempotent.py` (3 tests) — ledger séparé du live,
  dédup exclut les résolus, re-run sans doublon. ✅
- **Effets de bord** : un éventuel ancien ledger `paper_bets_simulate.csv` n'existe pas encore
  (créé au premier run). La ligne orpheline résolue restante dans le ledger live n'a pas été
  touchée (origine incertaine, inerte ; suppression = décision humaine).

### A7. Marchés void
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `finalize_run.py` faisait `outcome = 1 if result == "yes" else 0`
  (l.135 legacy v1, l.364 v2) → un `result` "void"/"" comptait comme NO (outcome=0).
- **Fichiers modifiés** :
  - `predictor/scripts/finalize_run.py` : `_finalize_v2` route un `result ∉ {yes,no}` vers le
    nouveau `_finalize_v2_void` (résolution `outcome="void"`, scoring void `n_datapoints=0`,
    ligne ledger du champion marquée resolved-void P&L=0, report persisté pour ne plus être
    re-finalisé). Chemin legacy v1 : même garde void inline. Hypothèse documentée : un run =
    un bin (daily_auto capture un seul marché par run).
- **Tests** : `predictor/tests/test_finalize_void.py` (5 tests) — `void`/`""`/`VOID`/`cancelled`
  marqués void et exclus ; non-régression `yes` toujours scoré outcome=1. ✅
- **Effets de bord** : un run void est désormais « finalisé » (rc=0) côté
  `daily_auto.step_finalize`, donc compté dans `finalized` et plus retenté. Sa mise est
  considérée remboursée (P&L=0), il n'alimente ni le Brier ni la gate.

---

## Lot B — Contrats / oracle

### B1. Gater `submitMeasurement`
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `ReclaimWeatherSource.submitMeasurement` était permissionless
  (aucun `onlyRole`), le NatSpec disait « trusts the keeper ».
- **Choix** : AccessControl `KEEPER_ROLE` (suggestion primaire du prompt), admin = deployer.
- **Fichiers modifiés** :
  - `oracle-poc/contracts/src/sources/ReclaimWeatherSource.sol` : hérite d'`AccessControl` ;
    `KEEPER_ROLE = keccak256("KEEPER_ROLE")` ; `submitMeasurement(...) … onlyRole(KEEPER_ROLE)` ;
    constructeur prend `address admin` (→ `DEFAULT_ADMIN_ROLE` + `KEEPER_ROLE`), check
    `ZeroAddressAdmin`. NatSpec mis en cohérence.
  - `oracle-poc/contracts/script/DeployPOC.s.sol` : passe `deployer` comme admin.
  - `oracle-poc/contracts/test/ReclaimWeatherSource.t.sol` : constructeurs à 4 args ; setUp
    accorde `KEEPER_ROLE` au EOA `KEEPER` ; nouveaux tests `test_submit_nonKeeper_reverts`,
    `test_constructor_zeroAdmin_reverts`, `test_constructor_grantsRolesToAdmin`.
- **Tests** : `forge test` oracle-poc — **23 passed** (dont le « non-keeper revert » exigé). ✅
- **Effets de bord** : le keeper off-chain doit désormais détenir `KEEPER_ROLE` (le deployer
  l'a par construction). Le déploiement on-chain existant n'est pas modifié rétroactivement
  (nouveau déploiement requis pour appliquer la garde).

### B2. Réparer `VerifyDeployment`
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `VerifyDeployment.s.sol:51` attendait `"Aratea POC Token"`,
  mais `AugPocToken.sol:44` déploie `ERC20("Augure POC Token", "AUG-POC")` →
  l'assertion `name` échouait toujours. (Confirmé aussi par `DeployArateaPhase1.t.sol` qui
  asserte déjà `name() == "Augure POC Token"`.)
- **Fichiers modifiés** :
  - `contracts/script/VerifyDeployment.s.sol:51` : assertion → `"Augure POC Token"` (aligné
    sur l'on-chain qui ne change pas). TODO(humain) ajouté : un rename « Aratea POC Token »
    exige un **redéploiement** (le nom est le domaine EIP-712 du permit).
  - Nouveau `contracts/test/unit/VerifyDeployment.t.sol` : exécute `run()` contre un
    déploiement frais (aurait attrapé le bug) + garde-fou de non-vacuité (revert sur admin
    erroné).
- **Tests** : `contracts/test/unit/VerifyDeployment.t.sol` (2 tests). ✅
- **Effets de bord** : aucun on-chain (script read-only). Le filet est de nouveau utilisable.

### B3. Challenges multiples
- **Statut** : corrigé (faisable en POC, aucun invariant cassé).
- **Constat vérifié ?** : oui. `challengeRound` revertait si `status != Proposed` → un seul
  challenge possible ; un griefer pouvait consommer le slot avec une raison vide, sans trace.
- **Fichiers modifiés** :
  - `contracts/src/rounds/RoundRegistry.sol:107` (`challengeRound`) : autorise `Proposed` OU
    `Challenged` dans la fenêtre. 1er challenge → `Proposed→Challenged` ; suivants → statut
    inchangé (reste `Challenged`) mais **ré-émettent `RoundChallenged`** (trace on-chain).
    Machine à états inchangée.
  - `contracts/test/unit/RoundRegistry.t.sol` : `test_Challenge_RevertsOnAlreadyChallenged`
    (qui actait l'ancien comportement) remplacé par
    `test_Challenge_AllowsMultipleChallengesEmitsEachTime` + garde-fou hors fenêtre. Bornes
    (fenêtre exacte, round inconnu) inchangées.
- **Invariants** : non cassés. Le handler invariant (`RoundRegistryInvariant.t.sol:79`)
  ne re-challenge jamais (garde `!= Proposed`) ; les invariants portent sur supply/minter, que
  la ré-émission d'event n'affecte pas. `forge test` contracts — **98 passed**. ✅
- **Effets de bord** : le panel hors-chaîne doit lire **tous** les events `RoundChallenged`
  d'un round (pas seulement le premier) pour récupérer toutes les raisons. Pas de stake/anti-
  griefing ajouté (hors périmètre B3) : le slot n'est plus « consommable », mais un spam
  d'events reste possible (coût gas de l'attaquant).

---

## Lot C — Web

### C1. `ipfsHttpUrl` allowlist + gateway
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `format.ts` renvoyait l'URI on-chain telle quelle pour tout
  schéma non-`ipfs://` (`javascript:`/`data:` en `href` = XSS) et utilisait le gateway mort
  `cloudflare-ipfs.com`.
- **Fichiers modifiés** :
  - `dashboard/src/lib/format.ts` (`ipfsHttpUrl`) : allowlist `{ ipfs://, https:// }` ; tout
    autre schéma → `""`. `ipfs://` → `https://ipfs.io/ipfs/<cid>`.
  - `dashboard/src/app/round/[hash]/page.tsx:138` : si `ipfsHttpUrl` renvoie `""`, rend l'URI
    en **texte** (`<span>`) sans `href`.
- **Tests** : `dashboard/src/lib/format.test.ts` (4 cas ipfs : gateway, https passthrough,
  schémas dangereux rejetés, vide). Runner **vitest** ajouté (devDep) + script `test`. ✅
- **Effets de bord** : une URI on-chain à schéma exotique (mais légitime, ex. `ipns://`) n'est
  plus cliquable (rendue en texte). Acceptable (sécurité > confort).

### C2. Formulaire contributeur
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `maxLength` client-only (contournables), aucune neutralisation
  des mentions Discord, pas d'anti-bot.
- **Fichiers modifiés** :
  - `site/src/app/actions.ts` : troncature serveur (`name`/`skill` ≤ 80, `email` ≤ 120,
    `message` ≤ 600) avant le payload ; `allowed_mentions: { parse: [] }` ; honeypot caché
    `website` non vide → rejet silencieux (faux succès, pas d'envoi).
  - `site/src/components/ContributeForm.tsx` : champ honeypot hors écran, non focusable,
    `aria-hidden`.
- **Tests** : `site/src/app/actions.test.ts` (4 tests : troncature, `allowed_mentions`,
  honeypot, validation). Vitest ajouté au projet `site`. ✅
- **Effets de bord** : `email` est aussi tronqué à 120 (= `maxLength` client existant) — au-delà
  du strict « name/skill 80, message 600 » du prompt, mais cohérent avec le durcissement du
  même payload.

### C3. Cache `fetchAllRounds` + validation du hash
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. 4 `getContractEvents` full-range sans cache (pages
  `force-dynamic`) ; `round/[hash]` scannait tous les rounds avant de valider le param.
- **Fichiers modifiés** :
  - `dashboard/src/lib/rounds.ts` : scan RPC renommé `_scanAllRounds`, wrappé dans
    `unstable_cache(…, { revalidate: 60 })`. Les `bigint` (`proposedAt`, `amounts`,
    `totalAmount`, `lastEventBlock`) sont **stringifiés** pour le Data Cache de Next (qui ne
    sérialise pas BigInt) puis revivés dans `fetchAllRounds`.
  - `dashboard/src/lib/format.ts` : `isValidRoundHash` (`/^0x[0-9a-fA-F]{64}$/`).
  - `dashboard/src/app/round/[hash]/page.tsx` : `notFound()` si hash invalide **avant**
    `fetchAllRounds`.
- **Tests** : `dashboard/src/lib/format.test.ts` (+2 cas hash : longueur/préfixe/hex). Cache
  validé au build (`npm run build` ✅, pas d'erreur de sérialisation BigInt).
- **Effets de bord** : données rounds jusqu'à 60 s de retard (acceptable pour un dashboard
  read-only). La sérialisation bigint↔string ajoute un map au coût négligeable.

### C4. Headers de sécurité
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. Aucun header de sécurité sur les deux apps.
- **Fichiers modifiés** :
  - `dashboard/next.config.js` + `site/next.config.js` : `headers()` sur `/:path*` →
    `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`,
    `X-Frame-Options: DENY`, et CSP `frame-ancestors 'none'` (defense-in-depth).
- **Tests** : `next.config.test.mjs` (dashboard + site, 1 test chacun) — la config expose les
  4 en-têtes. ✅
- **Effets de bord** : `X-Frame-Options: DENY` + `frame-ancestors 'none'` bloquent tout
  embarquement en iframe (voulu, le dashboard/site n'a pas vocation à être framé).

### C5. FilterBar statut value vs label (locale FR)
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. Les chips passaient le libellé localisé comme valeur d'URL
  (FR `status_open = "ouvert"`, `fr.tsx:277`) comparé au champ brut `r.resolution.status =
  "open"` (`page.tsx:73,87`) → tableaux vides en FR. EN fonctionnait par coïncidence
  (`en.tsx:268` : `status_open = "open"` == valeur brute).
- **Fichiers modifiés** :
  - `dashboard/src/components/FilterBar.tsx` : type `FilterOption { value, label }` ; chips
    togglent/matchent par `value`, affichent `label`.
  - `dashboard/src/app/predictor/page.tsx` : `statusOptions` via `statusFilterOptions`
    (value brute `open`/`resolved`, label localisé) ; `seriesOptions` mappées en
    `{value,label}` ; filtres via `matchesStatusFilter`.
  - Nouveau `dashboard/src/lib/runFilters.ts` (helpers purs).
- **Tests** : `dashboard/src/lib/runFilters.test.ts` (5 cas, dont le scénario FR : la chip
  « ouvert » a value `"open"` qui matche ; filtrer sur le libellé FR ne matche rien =
  reproduction du bug). Vérifié en FR : le filtre statut fonctionne (la value est désormais
  locale-indépendante). ✅
- **Effets de bord** : aucun. La forme `{value,label}` est rétro-compatible pour series
  (value=label=ticker).

---

## Lot D — CI

### D1. Pin des actions par SHA
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. Toutes les actions étaient sur tags mutables.
- **Fichiers modifiés** : les 9 workflows `.github/workflows/*.yml`. 29 `uses:` épinglés au SHA
  de commit (résolu via `gh api repos/.../commits/<tag>`), commentaire `# vX.Y.Z` :
  - `actions/checkout` `34e11487…` # v4.3.1 ; `actions/setup-node` `49933ea5…` # v4.4.0 ;
    `actions/upload-artifact` `ea165f8d…` # v4.6.2 ; `actions/setup-python` `a309ff8b…` # v6.2.0 ;
    `actions/stale` `eb5cf3af…` # v10.3.0 ; `github/codeql-action/{init,autobuild,analyze}`
    `dd903d2e…` # v3.36.2 ; **`foundry-rs/foundry-toolchain` `c7450ba6…` # v1.8.0** ;
    **`crytic/slither-action` `f197989d…` # v0.4.0** (priorités traitées).
- **Tests** : N/A (config). Vérif : `grep` → **0** `uses:` non épinglé (40 hex + `# v`).
- **Effets de bord** : les actions ne se mettront plus à jour automatiquement ; renouveler les
  SHAs périodiquement (Dependabot/manuel).

### D2. `daily-trading.yml` — credentials
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. Le checkout utilisait `token: ${{ secrets.BOT_PAT }}` → PAT
  persisté dans `.git/config` pendant tout le job.
- **Fichiers modifiés** :
  - `.github/workflows/daily-trading.yml` : checkout `persist-credentials: false` (plus de
    `token: BOT_PAT` ; clone via `GITHUB_TOKEN` par défaut). Étape « Commit and push » :
    `env: BOT_PAT: ${{ secrets.BOT_PAT }}` + `git push
    "https://x-access-token:${BOT_PAT}@github.com/${{ github.repository }}.git" HEAD:main`.
- **Tests** : N/A (config). Vérif : YAML parsé + assertions (persist-credentials=false, pas de
  token au checkout, BOT_PAT dans l'env de l'étape push). ✅
- **Effets de bord** : le PAT n'est plus sur disque ; GitHub masque `BOT_PAT` dans les logs. Le
  push cible explicitement `github.com/<owner>/<repo>` au lieu de `origin` (équivalent ici).

### D3. `sanitize.py` — `_xml_escape`
- **Statut** : corrigé.
- **Constat vérifié ?** : oui. `_xml_escape` n'échappait pas `"` ni `'`, alors qu'il produit la
  valeur d'attribut `field="…"` → un `"` permettait de sortir de l'attribut.
- **Fichiers modifiés** :
  - `rounds/scripts/sanitize.py` : `_xml_escape` échappe `"`→`&quot;` et `'`→`&#39;` (`&`
    reste en premier). `detect_injection` : docstring précisant qu'il est **best-effort**
    (heuristiques EN, pas la barrière de sécurité — c'est le wrapping XML).
  - `rounds/scripts/test_sanitize.py` : `test_field_name_xml_escaped` corrigé (l'ancienne
    assertion `'"' not in …split(">")[0]` était fausse — elle butait sur les guillemets
    délimiteurs d'attribut) ; ajout `test_xml_escape_quotes_in_body` et
    `test_field_name_with_apostrophe_escaped`.
- **Tests** : `rounds/scripts/test_sanitize.py` — **22/22** (self-runner + pytest). ✅
- **Effets de bord** : aucun fonctionnel (les agents voient `&quot;`/`&#39;`, sémantiquement
  équivalents). `detect_injection` reste volontairement contournable (assumé par la revue).

---

## Vérifications finales

| # | Vérification | Résultat |
|---|---|---|
| 1 | `cd contracts && forge test` | ✅ **98 passed**, 0 failed (9 suites) |
| 1 | `cd oracle-poc/contracts && forge test` | ✅ **23 passed**, 0 failed |
| 2 | `cd predictor && pytest` | ✅ **120 passed** (92 baseline + 28 nouveaux), 0 failed |
| 3 | `cd dashboard && npm run build` | ✅ Compiled successfully, types OK, 5 pages générées |
| 3 | `cd site && npm run build` | ✅ Compiled successfully, types OK, 5 pages générées |
| 4 | `slither` contrats modifiés | ⚠️ **non installé localement** → laissé à la CI (`crytic/slither-action`, désormais pinné). |
| 5 | `gitleaks detect --no-git` | ⚠️ non installé → **grep manuel** sur le diff `main..HEAD` : aucun secret réel (seules des références `secrets.BOT_PAT`, le *nom* "Augure POC Token", et des inputs de test factices `discord.test/webhook`, `file:///etc/passwd`). |
| 5 | `git log --all --diff-filter=A -- "*.env"` | ✅ **vide** (aucun `.env` jamais ajouté à Git). |

Tests web ajoutés (hors liste obligatoire, infra vitest introduite) : dashboard **12 passed**
(format + runFilters + next.config), site **5 passed** (actions + next.config).

### Liste des commits (`git log --oneline main..`)

```
2e3f46b fix(rounds): _xml_escape échappe aussi guillemets " et '
0f3fc12 fix(ci): daily-trading n'expose plus BOT_PAT tout le job
89488d8 fix(ci): pin toutes les GitHub Actions par SHA de commit
db1487a fix(dashboard): FilterBar statut value (brut) vs label (localisé) — fix FR
6689528 fix(web): en-têtes de sécurité sur les deux apps Next
b696926 fix(dashboard): cache fetchAllRounds (60s) + valide le hash avant scan
b495589 fix(site): durcissement formulaire contributeur (troncature + mentions + honeypot)
2665397 fix(dashboard): ipfsHttpUrl allowlist de schémas + gateway ipfs.io
0c869b0 fix(contracts): challenges multiples (trace on-chain) sans changer la FSM
a42c679 fix(contracts): VerifyDeployment aligne le nom token sur l'on-chain
45a98e4 fix(oracle): gate submitMeasurement par KEEPER_ROLE (AccessControl)
aed95a0 fix(predictor): marchés void exclus du scoring (pas comptés NO)
2e1c1fb fix(predictor): simulate.py idempotent + ledger isolé (heat fantôme)
9d6da8f fix(predictor): NYC predit a la station de resolution KNYC (Central Park)
113a4ba fix(predictor): formule Kelly correcte (f* = (p-px)/(1-px))
559dc79 fix(predictor): convention unique de normalisation des probas (live)
3806386 fix(predictor): LearnedPredictor honore le pin de CHAMPION.json
b61079a fix(predictor): dedup backtest par ticker (gate Phase B non gonflable)
```

### Problèmes NOUVEAUX découverts en cours de route (non corrigés)

1. **`.git/index.lock` périmé** (taille 0, 6 juin) bloquait `git pull`. Supprimé pour
   débloquer (geste d'infra, pas un correctif de code). Symptôme possible : un process git
   tué brutalement lors d'un run antérieur.
2. **Build artifacts non gitignorés côté predictor data** : `data/forecasts/` n'est PAS
   gitignoré (`git check-ignore` négatif) et contient des fichiers cache (untracked). Après
   A5, des fichiers cache JFK orphelins y subsistent (inertes). À nettoyer/ignorer un jour
   (hors périmètre).
3. **Ledger live `paper_bets.csv` : 1 ligne orpheline** (bet_id absent de tout
   `runs/<NNN>/report.json`), résolue donc inerte. Origine incertaine (peut-être un ancien
   run simulate sur le ledger partagé). Non supprimée (décision humaine — impacte le P&L
   réalisé / bankroll de `daily_auto`).
4. **`ReclaimWeatherSource` — warning `block-timestamp`** (`forge build` / forge-lint, l.168
   et l.~155) sur les comparaisons `block.timestamp`. **Préexistant** (non introduit par B1) ;
   atténué par les fenêtres `MAX_FUTURE_SECONDS`/`MAX_PAST_SECONDS`. À évaluer.
5. **Deux writers du ledger live au schéma divergent** : `live_run._append_ledger_row:228`
   (header hardcodé 16 champs) vs `Ledger.append` (champs de `PaperBet`). Toute évolution du
   schéma `PaperBet` doit mettre à jour les deux, sinon désalignement CSV. C'est ce qui a
   motivé le choix « ledger séparé » en A6.
6. **Infra de test web introduite** : vitest ajouté en devDep au `dashboard` et au `site`
   (lockfiles modifiés). Aucun job CI ne les exécute encore — à câbler dans
   `dashboard-ci.yml`/un futur `site-ci.yml` si on veut les faire tourner en CI (hors
   périmètre des items listés).
