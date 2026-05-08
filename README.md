> [Lire en français](README.fr.md)

# augure-rounds

Token issuance mechanics for the **AUG-POC** token, based on the labor value brought to the Augure project.

> Augure is an open-source project building decentralized weather prediction markets and parametric insurance. Its current POC phase validates a predictive edge on Kalshi markets.

## Principle

Every contribution to the project — cash, code, data, design, research — is the same substance: **labor value**. This repository operates the engine that:

1. **Collects** monthly contributions of every registered participant, **strictly from observable Git artifacts** (merged PRs, diffs, commits, reviews). No self-reports, no claimed hours, no narrative submissions.
2. **Estimates** their value in **BTC** equivalent ("how much would the market have paid for this exact output?"), via an AI agent following a public rubric.
3. **Opens a 7-day public challenge window** on the published valuation report.
4. **Releases** the AUG-POC tokens at the end of the window, minted at `valued_BTC / NAV_per_token`.

Cash follows the same path: a BTC deposit (or USDC at spot) is treated as labor value already crystallized.

## Hard rules

- **Fact-only.** Source of truth: Git. Anything not committed does not exist for valuation.
- **Push KO = 0.** Rejected, closed-without-merge or abandoned PRs have zero value.
- **BTC unit.** Hourly rates, NAV, valuations, mint amounts — all in BTC or sats.
- **No category privilege.** A cash investor is treated identically to a code contributor: a labor unit valued and minted.

## Reference documents

- **[`RUBRIC.md`](RUBRIC.md)** — valuation procedure followed by the AI agent.
- **[`HOURLY_RATES.md`](HOURLY_RATES.md)** — per-profile rate sheet (in sats/hour).
- **[`agent/PROMPT.md`](agent/PROMPT.md)** — system prompt of the valuation agent.
- **[`WALLETS.md`](WALLETS.md)** — public registry of contributor wallets.
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — how to participate.

## Monthly cycle

| Day | Action |
|---|---|
| 1 | Automated snapshot of all merged contributions of month M-1 |
| 1-2 | AI agent produces `valuation_report.md` (PR opened) |
| 1-7 | Public challenge window (formal challenges via signed comment) |
| 7 | Auto-merge if no challenge → multisig mint. If challenged → Top-X holder panel decides |

## Contested valuations — the holder panel

If a formal challenge is filed during the window, the decision passes to the **Top X token holders, each with one vote** (not weighted by stake). Simple majority decides.

| Phase | Contributors | X |
|---|---|---|
| 1 | ≤ 20 | 5 |
| 2 | 20-50 | 7 |
| 3 | > 50 | 11 |

The panel either ratifies the AI's valuation as-is, or sends it back with written instructions for revision.

## Guardrails

- Monthly cap: ≤ 10 % of circulating supply minted per window.
- Per-contributor cap: ≤ 30 % of monthly mint.
- Valuations > 0.01 BTC in a round trigger an automatic panel vote even without challenge.
- New entrant cooldown: first merged PR must be > 30 days old before mint eligibility.
- Slashing: clawback over 6 months on fraud established by 67 % vote.

## Status

Phase 1 (4-week MVP):
- [ ] RUBRIC.md, HOURLY_RATES.md, PROMPT.md (initial drafts shipped)
- [ ] GitHub collection script
- [ ] Multisig Safe on Base
- [ ] Genesis round (retroactive valuation of pre-open-source work)
- [ ] First live round

## License

Code and documents under [Apache 2.0](LICENSE).
