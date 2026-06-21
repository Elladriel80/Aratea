# Status

*Last updated: 2026-06-21*

Snapshot of where Aratea actually stands across its three live tracks
(predictor, contracts, dashboard) and the infrastructure around them.
Every numeric claim below has a source file in this repo — paths are
quoted inline so anything can be verified without trusting this page.

For the phased plan that frames these tracks, see [`ROADMAP.md`](ROADMAP.md).

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

### Latest learning loop results (2026-06-21)

62 dates, chronological split TRAIN 38 / VALID 12 / HOLDOUT 12:

| Config | HOLDOUT Brier | vs Kalshi mid |
|---|---|---|
| v3 baseline (C=0.1) | 0.1369 | +0.0029 above market |
| v3b (series_bias_prior, global) | 0.1170 | −0.0003 (minor leakage) |
| **v3fa (series_bias_fa, TRAIN-only)** | **0.1173** | **= market (tie, clean)** |

**Key finding:** Series-specific bias correction (per-series mean overestimation)
brings the model from +0.0029 above market (v3) to exact parity (v3fa). Bias
priors are structurally stable: TRAIN-only vs full-dataset estimates differ ≤ 0.011.
Next lever: more dates via daily pipeline or new structural feature.

NO-GO hypotheses tested (62-date dataset):
`GBM depth=2`, `consensus×spread`, `is_hightemp (p=0.117)`, `month_sin/cos (p=0.102, 3 months)`,
`p_consensus×series_bias_fa (p=0.912)`, `days_ahead×series_bias_fa (p=0.633)`.

**Current verdict:** model at exact market parity (0.1173 = 0.1173) with 12 HOLDOUT dates.
Edge detection requires more data. **Next lever:** expand Kalshi universe to 10-12 series
(code supports 20+ via `src/kalshi/resolution.py`) — see TODO-HUMAIN.md section B39.

### Feature sets

| Key | Features | Holdout | Status |
|---|---|---|---|
| `v3` | p_consensus, forecast_spread, days_ahead | 0.1369 | Committed champion |
| `v3b` | v3 + series_bias_prior (global lookup) | 0.1170 | Experimental |
| **`v3fa`** | **v3 + series_bias_fa (TRAIN-only)** | **0.1173 = market** | **Best clean result** |
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
| **M5** | Testnet Arbitrum Sepolia — live deploy | 🟡 blocked (human: install Foundry + run forge deploy) |
| **M6** | Governance UI `/governance` — wallet + on-chain vote | ✅ done (PR #166) |

### Test coverage (as of 2026-06-21)

| Contract | Line | Branch | Function |
|---|---|---|---|
| `AugPocToken` | 100% | 100% | 100% |
| `RoundRegistry` | 100% | 100% | 100% |
| `MintGovernor` | 100% | 91.49% | 100% |
| **Full suite** | — | — | **162 tests** |

### Security (internal audit 2026-06-21)

Full report: [`contracts/docs/SECURITY-AUDIT-2026-06-21.md`](contracts/docs/SECURITY-AUDIT-2026-06-21.md) (~620 SLOC, 7 findings).

**Testnet: GO. Mainnet: NO-GO** (requires external audit + Safe multisig + Timelock + REG-1/GOV-1 fixes).

Key open items for mainnet: GOV-1 (param changes no Timelock), REG-1 (ROUND_EXECUTOR_ROLE scope post-Phase2), TOK-2 (admin EOA → Safe).

### Deployment state

- **Dry-run:** validated on `forge anvil` — Phase 1 + Phase 2 + ProposeGenesisRound — see [`contracts/docs/DRY-RUN-ANVIL.md`](contracts/docs/DRY-RUN-ANVIL.md).
- **Testnet (Arbitrum Sepolia):** not yet deployed.
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
