<!-- Version française : architecture.fr.md -->

# Aratea — architecture overview

*Date: 2026-05-08 — version 0.1*

## Vision

Aratea is a decentralised protocol for **parametric weather mutual cover**, powered by a community-built predictive engine. Three pillars:

1. **Predictive engine**: meta-ensemble of AI weather models plus crowdsourced data. Open-source, contribution-driven, measured against Kalshi during the POC phase.
2. **Mutual DAO**: tokenised risk-sharing pool in the vein of Nexus Mutual. Members supply collateral; parametric payouts are triggered by weather oracles.
3. **DePIN data layer**: physical stations rewarded in token. Improves local resolution and reduces dependence on government feeds.

> **Legal clarification** — Aratea is not a regulated insurer. The term "mutual" here means a **decentralised discretionary mutual**: members pool capital, claim execution is parametric and automatic (on-chain oracle), and there is no insurer's contractual undertaking. See white paper section 4.

The three pillars reinforce one another: better prediction → better pricing → more contracts sold → more stakers attracted → funding for more DePIN sensors → better prediction.

## Phases

### Phase 1 — Kalshi POC *(in progress)*

Goal: demonstrate that the predictive engine has a measurable edge. No final product, no smart contract, no risk pool. The go/no-go criterion is strictly quantitative: the AI ensemble must beat the best single model and beat climatology over N>50 forward-tested events (with no data leakage).

Code: `predictor/`. Entirely off-chain. The Kalshi trading bankroll funds what comes next.

### Phase 2 — Aratea DAO (token + governance)

Starts once Phase 1 is validated. Goals:

- Deploy the AUG-POC ERC-20 on Base/Arbitrum/Optimism (chain to be decided).
- Activate the mint module through the existing monthly rounds (already tested off-chain).
- Put Top-X holder panel governance in place.
- Convert AUG-POC into ARA (the final DAO token) by a ≥ 67 % vote.

Code: `contracts/token/`, `contracts/rounds/`, `contracts/governance/`.

### Phase 3 — Parametric mutual

Starts once the DAO is operational and the predictor is proven live. Goals:

- Risk-sharing pool: members deposit USDC/BTC and earn the premiums of contracts sold through NAV appreciation.
- Pricing: the (off-chain) predictive engine emits contract prices, signed and posted on-chain.
- Resolution: Chainlink Custom on top of NOAA/NWS feeds (and our own DePIN feed once available).
- Initial categories: extreme temperature, cumulative rainfall, wind events.

**Bounded cover promise and radical transparency.** The mutual undertakes to indemnify every eligible parametric claim *within the limit of the pool's available capital*, as established on-chain at settlement. If several active undertakings trigger simultaneously beyond the available *Free Capital*, indemnification is executed pro rata. The ratio of active undertakings to total mobilisable capital is readable on-chain continuously, and is enforceable by the subscriber as of right (see article 4 bis of the articles of association).

This mechanism is the exact inverse of the classical insurance model, whose opacity was identified as a central factor in the 2008 collapse of AIG (≈ USD 440 billion in notional CDS written through AIG Financial Products without matching capitalisation; US federal rescue ≈ USD 182 billion). By making the undertakings/capital ratio visible in real time, the architecture makes opacity of that nature structurally impossible.

Code: `contracts/mutual/`, `predictor/oracle/` (price signing), resolution pipeline in `predictor/scripts/`.

### Phase 4 — DePIN data layer

Physical stations (partnership with WeatherXM or an own network, to be decided). Rewards in ARA token based on:

- Station availability (uptime).
- Data quality (consistency with neighbours, model-based validation, no manual outliers).
- Geographic density (bonus for under-covered areas).

The rounds module values these contributions like any other (non-code) work.

## Cross-cutting components

### Token economic model

See [`token_model.md`](token_model.md) — a single token, labour value as the unifying principle, mint at NAV, symmetric refusability between cash and labour contributions, Top-X holder governance.

### Valuation engine

See [`value_engine.md`](value_engine.md) — fact-only AI agent running on Git artefacts, public and versioned rubric and rate table, 7-day challenge window, ratification by the Top-X holder panel in case of contest.

### Weather oracles

Phase 3+. Target architecture:

1. Primary source: NOAA / NWS for US markets (Kalshi-compatible resolutions).
2. Secondary source: ECMWF / Météo-France / DWD for upcoming European markets.
3. Cross-validation: our own DePIN stations for high-frequency local resolution.

The current `predictor/src/kalshi/resolution.py` module serves as the prototype: precise station ↔ market mapping rules, rounding handling, Trace conventions. It will be reused and extended for the on-chain oracle.

### Data stack

- Forecasts: Open-Meteo (free, multi-model) for the POC. Aurora/Pangu/FourCastNet/GenCast via HuggingFace + cloud GPU in Phase A.2.
- Historical: ERA5 via Open-Meteo.
- Kalshi markets: public REST API (read). Write API integration once the DAO is active, if we expand to other prediction markets.
- Crowdsourced: to be integrated (PWS, Twitter, traffic cams).

## Open decisions

- **Deployment chain**: Base / Arbitrum / Optimism. Criteria: gas, DeFi/risk-pool ecosystem, custody options.
- **Bankroll stablecoin**: USDC, EURC, multi-stable. Impact: Kalshi conversion fees (USD only).
- **Kalshi POC custody**: JS personal account, intermediate US LLC structure, foundation. Determines the upstream legal structure.
- **Smart contract toolchain**: Foundry selected, to be recorded in `contracts/README.md`.
- **Wallet registry**: signed file in Phase 1 (`rounds/WALLETS.md`), on-chain registry from Phase 2.

## See also

- Token model (§7.7 Guardrails) → [`token_model.md`](token_model.md)
- Valuation engine (§7 Operational guardrails) → [`value_engine.md`](value_engine.md)
- **Draft articles of association, FR** (art. 4 bis "Limite des engagements de couverture et principe de transparence radicale" + art. 32 "Moteur de valuation et émission de tokens") → [`../../statuts-aratea-v0-projet-2026-05-16.md`](../../statuts-aratea-v0-projet-2026-05-16.md)
- **Draft Articles of Association EN** → [`../../statuts-aratea-v0-projet-2026-05-16-EN.md`](../../statuts-aratea-v0-projet-2026-05-16-EN.md)
