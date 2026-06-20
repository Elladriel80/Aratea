# Aratea — Vision & One-Pager

> v0.1 — June 2026

---

## The Problem

Traditional parametric insurance and prediction markets rely on centralized
oracles, opaque valuations, and siloed data. Policyholders cannot verify that
a payout formula is correct, data providers cannot be rewarded fairly for
their measurements, and the "house" always controls the rules.

---

## What Aratea Builds

Aratea is a **decentralized mutualist insurance protocol** combining three
interconnected layers:

### 1 — Prediction Engine

An AI-assisted signal that estimates the probability of a parametric trigger
(temperature, weather event…) before the on-chain market closes. The signal
is trained on historical observation data, validated on a held-out set with a
rigorous sign-test, and only promoted when it demonstrably beats the consensus
market price. Prediction logic runs off-chain and is open source; settlement
runs on-chain and is trustless.

Current status: Logistic Regression ensemble trained on 61 historical dates.
Holdout Brier score 0.137 vs market 0.134. Active research to close the gap.

### 2 — Mutualist DAO

A token-weighted governance layer where contributors earn `AUG-POC` tokens for
verifiable work (correct predictions, quality data, code review…). The token
has no speculative mint schedule: every token is backed by validated work at
Net Asset Value. Mint is controlled by a `RoundRegistry` contract; rounds are
proposed monthly, open to a 7-day challenge window, and require a token-weighted
super-majority to cancel. Once the Brier edge is confirmed, the protocol can pay
out parametric claims directly from the mutual fund, governed on-chain.

### 3 — DePIN Data Layer (Phase 4)

Decentralized physical infrastructure nodes (weather stations, IoT sensors)
rewarded in `AUG-POC` for supplying verifiable observation data. This creates a
data market that is transparent, auditable, and resistant to single-provider
failure — the opposite of a centralized oracle.

---

## Token Model

- **One token, one mechanic**: work → validated contribution → mint at NAV.
- **No pre-mine, no VC allocation**: every `AUG-POC` token in circulation
  represents a verified contribution logged on-chain.
- **Bounded supply via governance**: the mutual fund determines monthly mint
  amounts through the valuation rubric; token holders can reject any round they
  deem over-valued.
- **Radical transparency**: coverage ratio (commitments / capital) is visible
  on-chain at all times.

---

## Phases

| Phase | Goal | Status |
|-------|------|--------|
| 1 — Kalshi POC | Prove a predictive edge on a real prediction market | In progress |
| 2 — DAO Token | Deploy token + governance on-chain (Arbitrum Sepolia) | Contracts ready, testnet pending |
| 3 — Parametric Mutual | First on-chain insurance product backed by the prediction signal | Planned |
| 4 — DePIN Data Layer | Decentralized weather data infrastructure | Planned |

---

## Current Traction

- **162 passing tests** (unit + fuzz + invariant) across `AugPocToken`,
  `RoundRegistry`, and `MintGovernor`. 91% branch coverage on governance.
- **Security**: Slither CI (fail on medium), Gitleaks secret scanning, SHA-pinned
  GitHub Actions, gated oracle writes (KEEPER_ROLE).
- **Prediction**: 61 historical dates in the training set. Feature set v3
  (`p_consensus`, `forecast_spread`, `days_ahead`) in production.
- **Open source**: Apache-2.0. Contributions via standard PR workflow.

---

## For Contributors

The project is designed for builders who care about verifiable systems. We
welcome contributions in:

- **Smart contracts** (Solidity / Foundry): settlement layer, governance, slashing.
- **Prediction research** (Python): feature engineering, calibration, backtesting.
- **Data infrastructure**: IPFS pipelines, on-chain oracle feeds.
- **Documentation**: bilingual FR/EN, protocol specifications.

See `CONTRIBUTING.md` and `STATUS.md` for the current state of each component.

---

## Contact

Project repository: https://github.com/Elladriel80/Aratea  
License: Apache-2.0
