# Status

*Last updated: 2026-06-24*

Snapshot of where Aratea actually stands across its three live tracks
(predictor, contracts, dashboard) and the infrastructure around them.
Every numeric claim below has a source file in this repo — paths are
quoted inline so anything can be verified without trusting this page.

For the phased plan that frames these tracks, see [`ROADMAP.md`](ROADMAP.md).

---

## Project arc — 4 phases

| Phase | Scope | Status |
|---|---|---|
| **Phase 1** | POC — predictor edge + settlement layer (RoundRegistry, MintGovernor) | ✅ **live** |
| **Phase 2** | DAO — governance collective on-chain (MintGovernor Phase 2, testnet) | ✅ **live** (2026-06-23) |
| **Phase 3** | Parametric mutual — premium engine, policy lifecycle, auto-payout | 🔮 design (pending edge confirmation + D-capital + D-réglementation) |
| **Phase 4** | Mainnet & scale — external audit, Safe multisig, real members + capital | 🔮 future (post-Phase 3 testnet validated) |

**Current focus:** G2 (confirm edge), operate Phase 2 DAO on testnet.

---

## Predictor — Phase 1 Kalshi POC

Mode: **paper trading only**. No real-money position has been opened.

### Live model lineup

Registry: [`predictor/runs_learning/CHAMPION.json`](predictor/runs_learning/CHAMPION.json).

| Role | Model | Feature set | Status |
|---|---|---|---|
| Champion | `learned_v3` | v3 — p_consensus, forecast_spread, days_ahead | Active since 2026-06-04 (sigma-bascule) |
| Baseline | `kalshi_mid_baseline` | — | Floor the model must beat |

### Training — backfill dataset (2026-06-20)

| Metric | Value |
|---|---|
| Total rows | 1 467 |
| Distinct `target_date` | **62** (G1 target: 60 ✅) |
| Series covered | KXLOWTNYC, KXHIGHTSFO, KXLOWTCHI, KXLOWTBOS, KXLOWTMIA, KXLOWTLAX |
| Feature set built | v3 + interaction features |

### Latest learning loop results (2026-06-22, B44)

62 dates, chronological split TRAIN 38 / VALID 12 / HOLDOUT 12. Two independent
runs on the same dataset (shifted holdout windows) both show model below market:

| Run | HOLDOUT dates | Model Brier | Market Brier | Gap |
|---|---|---|---|---|
| loop_20260622T063316Z | 2026-06-02..06-13 | **0.1172** | 0.1173 | −0.0001 |
| loop_20260622T070606Z | 2026-06-04..06-15 | **0.1155** | 0.1208 | −0.0053 |

Best config: v3fa + forest_pct_5km (C=0.1).

**Key finding (B44):** Pipeline fix (fold-aware injection) unlocked the geo feature
`forest_pct_5km` as an additive term. Both independent holdout windows show model
below market — consistent signal. Gap ranges from 0.0001 to 0.0053 depending on
period; not yet statistically robust (need >= 20 dates, sign-test p < 0.05).

**Power analysis (B54, `scripts/power_analysis.py`):**
- At theta=65% win rate (observed 8/12=67% on VALID): need **30 HOLDOUT dates**.
- At theta=70%: need **18 HOLDOUT dates** (6 more than current).
- Run: `python scripts/power_analysis.py --current-wins 8 --current-n 12`

NO-GO hypotheses tested (62-date dataset):
`GBM depth=2`, `consensus×spread`, `is_hightemp (p=0.117)`, `month_sin/cos (p=0.102)`,
`p_consensus×series_bias_fa (p=0.912)`, `days_ahead×series_bias_fa (p=0.633)`,
`v3fb interactions (p=0.912/0.633)`.

**Current verdict:** consistent below-market signal across two holdout windows.
Not statistically significant yet (12 dates). **Next lever:** expand Kalshi universe
to 10-12 series (B45) — target >= 20 HOLDOUT dates for robust sign-test.

### Feature sets

| Key | Features | Holdout | Status |
|---|---|---|---|
| `v3` | p_consensus, forecast_spread, days_ahead | 0.1369 | Committed champion |
| `v3b` | v3 + series_bias_prior (global lookup) | 0.1170 | Experimental (leakage) |
| `v3fa` | v3 + series_bias_fa (TRAIN-only) | 0.1173 = market | Clean tie |
| **`v3fa + forest_pct_5km`** | **v3fa + C=0.1 + forest geo** | **0.1172 < market** | **Best result (B44)** |
| `v4` | v3fa + forecast_revision | pending | Activates with ≥2 captures/ticker |

### Control-group tracking (PR #170, 2026-06-21)

`PaperBet.algo_signal: "bet" | "no_bet"`. Control-group positions are
tracked at zero stake to measure counterfactual P&L. Dashboard P&L
filters to `algo_signal == "bet"` rows only.

---

## Contracts — Phase 1+2 settlement layer

### Milestones

| Milestone | Scope | Status |
|---|---|---|
| **M0** | Foundry scaffold, CI, threat model, bilingual docs | ✅ done |
| **M1** | `AugPocToken` — ERC-20 + Permit + AccessControl + Pausable | ✅ done |
| **M2** | ~~`MonthlyMintCap`~~ — removed (quality gated off-chain) | — |
| **M3** | `RoundRegistry` — propose / challenge / execute / cancel | ✅ done |
| **M3b** | `MintGovernor` — Phase 2 auto-mint, token-weighted vote | ✅ done (PR #163) |
| **M4** | Deploy scripts + dry-run forge anvil validated | ✅ done (PR #164) |
| **M5** | Testnet Arbitrum Sepolia — live deploy | ✅ done (2026-06-23 — Phase 2 live, 17 Ledger confirmations) |
| **M6** | Governance UI `/governance` — wallet + on-chain vote | ✅ done (PR #166) |

### Test coverage (as of 2026-06-21)

| Contract | Line | Branch | Function |
|---|---|---|---|
| `AugPocToken` | 100% | 100% | 100% |
| `RoundRegistry` | 100% | 100% | 100% |
| `MintGovernor` | 100% | ≥91% | 100% |
| **Full suite** | — | — | **182 tests** |

> Branch coverage: last measured on 162-test suite (91.49% MintGovernor). B46 added 12 more tests (challengeWindow seconds refactor) — re-run `forge coverage` to refresh branch numbers.

### Security (internal audit 2026-06-21)

Full report: [`contracts/docs/SECURITY-AUDIT-2026-06-21.md`](contracts/docs/SECURITY-AUDIT-2026-06-21.md) (~620 SLOC, 7 findings).

**Testnet: GO. Mainnet: NO-GO** (requires external audit + Safe multisig + Timelock + GOV-1 fix).

Key open items for mainnet: GOV-1 (param changes no Timelock — Safe + TimelockController), TOK-2 (admin EOA → Safe).
✅ Resolved: GOV-2 (`forceResolveStuck()` B40), REG-1 (test `DeployArateaPhase2.t.sol` B41), INFRA-1 (Slither CI).

### Deployment state

- **Dry-run:** validated on `forge anvil` — Phase 1 + Phase 2 + ProposeGenesisRound — see [`contracts/docs/DRY-RUN-ANVIL.md`](contracts/docs/DRY-RUN-ANVIL.md).
- **Testnet (Arbitrum Sepolia):** ✅ **live since 2026-06-23** — Phase 1 + Genesis + Phase 2 deployed (17 Ledger confirmations, VerifyDeploymentPhase2 11/11). Canonical addresses:
  - `TOKEN` — `0x0d8b96f84d3a8fe9d4b28b703c89d34c810fb6ec`
  - `REGISTRY` — `0xbb25c0adf2fc9e0ae2dc47882f3b314e53e4570c`
  - `GOVERNOR` — `0x3126edc0baaaac75802aea086a0cb713fa7ad598`
  - `KEEPER` — `0xcE4900f254c6DDE560DdB76751f6882c7D418598`
  - Old Phase 1 addresses (obsolete): `TOKEN=0x56a754…`, `REGISTRY=0xA2324…`
- **Dashboard wiring (pending JS):** set `NEXT_PUBLIC_TOKEN_ADDRESS`, `NEXT_PUBLIC_REGISTRY_ADDRESS`, `NEXT_PUBLIC_GOVERNOR_ADDRESS` in Vercel env vars + `KEEPER_PRIVATE_KEY` in GitHub Secrets.
- **Mainnet:** blocked — external audit required.

---

## Dashboard

Live: **[aratea-app.vercel.app](https://aratea-app.vercel.app/)**.

| Page | What it shows |
|---|---|
| `/` | ERC-20 state, total supply, Arbiscan links |
| `/rounds` | Round registry, lifecycle, challenge window |
| `/round/[hash]` | Per-round metadata, IPFS link, beneficiary breakdown |
| `/predictor` | Training run card, feature registry, Brier trajectory |
| `/governance` | Propose/vote/finalize via MetaMask — shows "not deployed" until `NEXT_PUBLIC_GOVERNOR_ADDRESS` set |

Stack: Next.js 15 + React 19, TypeScript strict, viem 2.x, Tailwind. No backend, no database.

---

## CI

| Workflow | Trigger | Purpose |
|---|---|---|
| `daily-trading.yml` | cron `0 18 * * *` UTC + manual | Finalize + capture + manifest rebuild + Vercel redeploy |
| `contracts-ci.yml` | push/PR on `contracts/**` | forge build + test + coverage + Slither |
| `dashboard-ci.yml` | push/PR on `dashboard/**` | typecheck + Next.js build |
| `security-scan.yml` | push/PR | gitleaks secret scan, SHA-pinned (PR #161) |
| `announce-release.yml` | `run-*` tags | Discord announcements |
| `weekly-recap.yml` | weekly | Weekly summary |
| `codeql.yml` | push/PR + schedule | GitHub security scanning |

---

## Recent changes (since 2026-06-10)

- **2026-06-24** — **Keeper CI fix (B52)** — `aratea-keeper.yml`: `window_days` input renamed `window_seconds` (default 604800s = 7d), env var `ROUND_WINDOW_DAYS` → `ROUND_WINDOW_SECONDS` — syncs with `KeeperProposeRound.s.sol` post-B46 refactor.
- **2026-06-24** — **Power analysis tool (B54)** — `predictor/scripts/power_analysis.py`: sign-test sample size for G2. At theta=65% win rate, need 30 HOLDOUT dates for p<0.05; at theta=70%, need 18.
- **2026-06-24** — **G2 update** — second independent loop run confirms below-market signal on different holdout window (0.1155 < 0.1208, gap 0.0053). Both runs show consistent edge.
- **2026-06-23** — **Phase 3 interfaces scaffolded (B51)** — `contracts/src/interfaces/`: `IPricingEngine.sol` (actuarial quote), `IPolicyRegistry.sol` (policy lifecycle PENDING→ACTIVE→CLAIMED/EXPIRED), `IPremiumPool.sol` (USDC capital pool, MCR, reserves). Pre-implementation; gated on D-capital + D-réglementation decisions.
- **2026-06-23** — **Phase 3 design notes (B47-B49)** — Aratea-Vault/Design-Phase3/: 01-modele-mutualiste, 02-moteur-tarification, 03-schema-contrats-police. Capital pilot ~13 k$ (C2 paramétrique pur). Pending D-capital + D-réglementation.
- **2026-06-23** — **Phase 2 LIVE on Arbitrum Sepolia** — full redeploy (17 Ledger confirmations): Phase 1 → Genesis mint → Phase 2 (MintGovernor). VerifyDeploymentPhase2 11/11 ✅. REG-1 confirmed: admin no longer holds ROUND_EXECUTOR_ROLE. Canonical addresses in `contracts/.env`. `challengeWindow` refactored to seconds (B46, 182 tests) — one-session testnet deploy now possible.
- **2026-06-21** — GOV-2 escape hatch `forceResolveStuck()` + Phase 2 wiring test (REG-1) — 170 tests — PR #173.
- **2026-06-21** — v3fb interaction features (B38 NO-GO): p_consensus×bias, days_ahead×bias both rejected (p=0.912/0.633). 160 tests. Universe expansion B39 documented. — PR #172 + housekeeping.
- **2026-06-21** — v3fa (fold-aware series bias), HOLDOUT ties market; v4 revision feature; algo_signal control group — PR #170.
- **2026-06-21** — Internal security audit (B33) — 7 findings, testnet GO, mainnet NO-GO — PR #167.
- **2026-06-21** — Governance UI `/governance` with MetaMask + on-chain vote — PR #166.
- **2026-06-20** — gitleaks CI secret scanning (SHA-pinned) — PR #161.
- **2026-06-20** — MintGovernor Phase 2 (+28 tests, >91% branch coverage) — PR #163.
- **2026-06-20** — Dry-run forge anvil validated + bilingual runbook — PR #164.
- **2026-06-20** — VISION.md + VISION.fr.md (one-pager FR/EN) — PR #165.
- **2026-06-20** — v3b series_bias_prior (calibration hiérarchique).
- **2026-06-20** — sigma bascule merged (Brier 0.137 on 62-date backfill).
- **2026-06-10** — Code review pass — 7 findings, all resolved.

---

## Where to read next

- **Vision**: [`docs/VISION.md`](docs/VISION.md), [`ROADMAP.md`](ROADMAP.md).
- **Security audit**: [`contracts/docs/SECURITY-AUDIT-2026-06-21.md`](contracts/docs/SECURITY-AUDIT-2026-06-21.md).
- **Feature engineering**: [`predictor/src/learning/FEATURES.md`](predictor/src/learning/FEATURES.md).
- **Token model**: [`docs/token_model.md`](docs/token_model.md).
- **Dry-run guide**: [`contracts/docs/DRY-RUN-ANVIL.md`](contracts/docs/DRY-RUN-ANVIL.md).
