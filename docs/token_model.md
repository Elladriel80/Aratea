<!-- Version française : token_model.fr.md -->

# Token model — Aratea POC

*Date: 2026-05-08 — version 0.3, monorepo*

> This document is the canonical version of the token model, hosted in the public Aratea repository. A working copy is kept in the founder's local workspace.

## 1. Founding principle

**One kind of contributor only: labour value.**

Cash is labour already crystallised into monetary form. Code, data and expertise are labour in the process of crystallising. Every contribution converges on the same unit of measure and receives the same treatment.

The AUG-POC token represents a share of the labour value accumulated in the project. No privileged category, no pre-allocation. The cap table emerges from who contributed how much.

## 2. AUG-POC token

- **Standard:** ERC-20 on Arbitrum (target chosen 2026-05-09; Sepolia testnet in Phase 1, mainnet conditional on a community audit).
- **Decimals:** 18 (Ethereum standard). Chosen 2026-05-09 for maximum compatibility with the Web3 ecosystem (DEXes, indexers, wallets). The functional unit of account remains the **sat**: the 1 sat = 1 token convention is imposed by construction at mint on the initial NAV, independently of the ERC-20 contract's decimal count.
- **Unit of account:** BTC. All internal calculations (NAV, hourly rates, valuations) are in BTC or sats.
- **Initial NAV:** **1 sat = 1 token** (atomic, validated 2026-05-08). No mental conversion required — the number of tokens held reads directly as the labour value contributed, in sats.
- **Future convertibility:** an AUG-POC → ARA (Aratea DAO) conversion mechanism is written into the contract from the start. The ratio is voted at 67 % by holders at DAO launch.

## 3. The mint, one unified mechanism

The project accepts only **one type of input** into the valuation engine: an **observable fact**.

- For cash: an on-chain deposit (BTC, or USDC converted at the spot rate of the subscription day). Sent to a "subscription pending" multisig address, not automatically folded into the treasury.
- For labour: a merged PR on the Aratea repository, or a signed commit on main, or a public review on a PR. What is not in Git does not exist.

The AI agent produces the valuation **strictly** from those artefacts (diff, files touched, tests, PR description, commits, reviews). **No declaration, no submission, no self-reported hours.**

Consequences:

- Unmerged, closed or abandoned PR → value = 0.
- "Invisible" work (mentoring over DM, support hours outside the thread) → not captured. An explicit and accepted trade-off.
- To have non-code work counted (community management, RFC, dataset), the output must be committed to the repository (signed digest, doc, curated data).

## 4. Symmetric refusability

Any contribution can be refused by JS (phase 1) or the panel (phase 2+) with written justification, during the challenge window:

- **Refusing a labour contribution**: do not merge the PR → value = 0.
- **Refusing a cash contribution**: return the funds from the "subscription pending" multisig address → no mint.

No contribution is imposed on the project. Legitimate grounds for refusal: conflict of interest, reputational risk, compliance, insufficient quality, strategic coherence.

## 5. Monthly cycle

```
D0   (1st of the month) : automated agent run over the artefacts of month M-1
D0-D1                   : publication of valuation_report.md (PR on the repository)
D1-D7                   : public challenge window
D7                      : ratification (automatic if uncontested AND not refused,
                          panel vote otherwise) → multisig mint
                          Tokens released to the registered wallets
```

## 6. Contest and panel vote

- As long as nobody formally challenges the valuation PR, it is merged at D7 and the mint is executed.
- A **formal contest** is declared by a structured comment on the PR (label `challenge`, signed by a registered wallet).
- When a contest exists at D7, the decision moves to the **Top X holder panel**:
  - X = 5 in phase 1 (≤ 20 contributors), 7 in phase 2 (20-50), 11 in phase 3 (>50).
  - **Each panel member has 1 vote.** No stake weighting. Top X = ranking by AUG-POC token balance at the close of the round.
  - A simple majority (≥ ⌈X/2⌉+1) decides: approve the valuation as it stands, or require a revision (with written instructions, sent back to the agent).

This avoids pure plutocracy while handing the decision to those with the most to lose or gain.

## 7. NAV calculation (in BTC)

```
NAV_BTC = treasury_BTC_balance
        + (Kalshi_positions_USD × USD/BTC_spot)
        + pending_settlement_receivables_BTC
        - operational_liabilities_BTC

NAV_per_token = NAV_BTC / circulating_supply
```

Delivered work does NOT enter the NAV (anti-circularity).

**Consequence — dilution of cash investors:** when labour is minted at the current NAV, supply increases while the numerator (cash + positions) does not move immediately. The bet: the code delivered creates future Kalshi P&L that will bring the NAV back above.

**Guardrails:**

The AUG-POC token is not intended to be traded on a secondary market — it represents a pro-rata share of the NAV and a governance right. Issuance caps traditionally exist to protect a market price; that logic does not apply here. The guardrails below concern **process quality** (validation, fraud, audit), not issuance velocity. No global monthly cap and no per-contributor cap is imposed: the mintable share is determined entirely by the weighted valuation of actual contributions.

- **Automatic token-weighted vote**: any individual valuation above 0.01 BTC goes to a weighted holder vote before minting, even without a contest (terms in §6 and §9).
- **Newcomer cooldown**: first merged contribution must be more than 30 days old before mint eligibility.
- **Slashing**: tokens are clawback-able for 6 months where fraud is established by a 67 % vote.
- **Annual audit** of the rubric and past rounds, at the holder assembly.

## 8. Subscription / Redemption

- **Monthly subscription window** (1st of the month). Cash contributions (BTC or USDC) and labour contributions (PRs merged in month M-1) are handled in the same round.
- **Every contribution is refusable** (see §4).
- **Quarterly redemption window**, 30-day notice, 20 % gate per window, 2 % penalty before 12 months.
- **NAV calculation**: signed by a 2-of-3 multisig (JS + 1 advisor + 1 representative holder). Published monthly.

## 9. General governance

Distinct from the anti-contest panel:

- **1 token = 1 vote**, capped at 25 % per wallet, on parametric matters (rubric, rates, dilution cap, DAO conversion, slashing).
- Thresholds: 51 % ordinary, 67 % major parametric, quorum 15 % of circulating supply.

## 10. Accepted trade-offs

1. **Cap table volatility.** Nobody knows what it will look like in 6 months. Coherent for anyone who believes what matters is the proportional share of value actually accumulated, not a "guaranteed" percentage.
2. **Potential dilution of cash investors.** To be stated plainly in the term sheet.
3. **Non-Git work is invisible.** Accepted. To have such work counted, the output must be committed.
4. **BTC volatility.** Hourly rates are stable in BTC but move in EUR/USD. Recalibration mechanism by vote if drift exceeds 25 % in a quarter.
5. **The Top X holder panel can polarise.** Mitigation: X grows with the community; panel votes are public and logged.
6. **Not attractive to large traditional VCs.** A philosophical choice. The project looks for investors aligned on labour value.

## 11. Genesis

At launch, two things happen simultaneously in the same window:

1. **Retroactive valuation of JS's work on kalshi-poc** (folded into `predictor/`). The agent runs over the whole Git history and produces a phase-by-phase valuation. **Challenge window extended to 30 days**, open to the first prospective investors before they invest.
2. **First cash investors** (if any). BTC or USDC contribution, minted at the initial NAV of 1 sat = 1 token.

See the dry run in `rounds/archives/2026-05-genesis/` for the engine's first iteration over the pre-open-source history.

## 12. See also

- Overall project architecture → [`architecture.md`](architecture.md)
- Valuation engine → [`value_engine.md`](value_engine.md)
- **Draft articles of association, FR** (art. 4 bis "Limite des engagements de couverture et principe de transparence radicale" + art. 32 "Moteur de valuation et émission de tokens" + art. 31 *Slashing*) → [`../../statuts-aratea-v0-projet-2026-05-16.md`](../../statuts-aratea-v0-projet-2026-05-16.md)
- **Draft Articles of Association EN** → [`../../statuts-aratea-v0-projet-2026-05-16-EN.md`](../../statuts-aratea-v0-projet-2026-05-16-EN.md)
