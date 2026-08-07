<!-- Version française : value_engine.fr.md -->

# Aratea valuation engine — fact-only, BTC

*Date: 2026-05-08 — version 0.2, monorepo*

> This document is the canonical version of the valuation engine, hosted in the public Aratea repository. See also `rounds/RUBRIC.md` for the precise operational rules and `rounds/agent/PROMPT.md` for the system prompt.

## 1. Mission

Estimate, in **BTC**, the value of every observable contribution to the project, without any declaration from the contributor. Output: a BTC amount that serves as the numerator of the mint (`tokens = BTC_value / NAV`).

Inviolable constraints:

- **Fact-only.** Single source of information: Git (merged PRs, diffs, commits, reviews, descriptions). No timesheets, no text submissions, no unverifiable claims.
- **Push KO = 0.** Rejected, unmerged or abandoned work → zero value.
- **BTC.** All calculations in BTC or sats. No EUR/USD in the parameters (only as a reference for quarterly recalibration).
- **Open-source rubric and prompt.** Versioned, modifiable by PR + ratification.

## 2. Architecture

Three monthly layers:

### Layer A — Collection (day 1)

Automated GitHub Action. For every wallet registered in `rounds/WALLETS.md`, it aggregates **only**:

- PRs merged in month M-1 (title, body, diff stats, files touched, reviewers, labels, commit messages, issues closed by the PR)
- Reviews given on other people's PRs
- Commits signed directly on `main` (rare)

What is NOT collected:

- Issues opened with no associated merged PR
- Discord, forum or DM discussions
- Declared time tracking
- Self-reports of any kind

Output: `rounds/archives/YYYY-MM/raw.json`.

### Layer B — AI valuation (days 1-2)

The agent receives `raw.json` + `RUBRIC.md` + `HOURLY_RATES.md` + project state (`docs/architecture.md` + the round's `docs/state.md` if present).

For each observable artefact, it computes:

```
BTC_value = estimated_hours × BTC_rate_per_hour × quality_adj × impact_adj
```

- **estimated_hours**: the time a professional would take to produce the same output, inferred from the diff and the context. Never asked of the contributor.
- **BTC_rate_per_hour**: according to the profile required by the nature of the output, from a public versioned table (`rounds/HOURLY_RATES.md`).
- **quality_adj** ∈ [0.5 ; 1.3]. Read off the artefacts: tests present, CI green, reviewers, code cleanliness.
- **impact_adj** ∈ [0.8 ; 1.5]. Read off the role of the module touched and roadmap progress.

The profile is a **variable** (market rate → BTC, recalibrated quarterly). The **deliverable** determines the value (a junior who produces senior-grade work is paid the senior rate for that deliverable, and vice versa).

Output: `rounds/archives/YYYY-MM/valuation_report.md` (PR opened on the aratea repository).

### Layer C — Challenge & ratification (days 1-7)

A **7-day** window. A structured comment (label `challenge`, signed by a wallet in the registry) can contest a specific point of the valuation.

At D+7:

- **No formal challenge** → the PR is merged by GitHub Action. Multisig mint executed.
- **At least one formal challenge** → the decision goes to the **Top X holders panel, 1 vote each**. X = 5 in phase 1. Simple majority. Panel deadline: 72 h. The panel either approves the valuation as it stands or requests a specific revision with written instructions. After revision, a new PR opens a restricted 72 h window.

## 3. The profile as a market variable

The rates in `HOURLY_RATES.md` are **variables** tied to the freelance market, expressed in BTC at a point in time. Quarterly recalibration:

- Source: average Paris day rates (Malt, Comet, Crème de la Crème) per profile.
- EUR/BTC conversion at the quarter's average spot.
- If drift exceeds 25 % against current values → token-weighted vote (51 %) to adjust.

The rubric does not *pick* a profile per individual. It picks the profile **according to the output produced**: an ML pipeline optimisation PR → ML/data profile, regardless of who wrote it. A docs PR → tech writer profile.

## 4. The rubric — summary

Full detail in `rounds/RUBRIC.md`. In brief:

1. **Estimated hours**: inferred from the diff (LoC adjusted for complexity, files touched, refactor vs greenfield, presence of tests).
2. **Profile**: determined by the nature of the module and the output.
3. **Quality** ∈ [0.5 ; 1.3]: tests, docs, CI, approving reviewers, technical debt.
4. **Impact** ∈ [0.8 ; 1.5]: core vs peripheral, does it unblock a milestone, is a measurable metric improved.

Hard bounds, no exceptional bonus.

## 5. The cash case

Outside the rubric on the valuation side (1 sat = 1 sat, no estimation), but **subject to ratification like any other contribution**.

- BTC contribution: sent to the current round's `subscription-pending` multisig address. If accepted at D+7, minted at NAV. If refused by JS (phase 1) or the panel (phase 2+) with written justification, the funds are returned.
- USDC or EURC contribution: converted into sats at the spot rate of the subscription day, same pending + ratification mechanism.

Cash appears in the monthly report **without a valuation** (gross amount + sender address), for the ratifier's visibility. Refusal is possible on strategic, reputational, conflict-of-interest or compliance grounds.

## 6. Genesis — retroactive valuation

The agent runs over **the repository's entire Git history** (commits, PRs, code delivered before the project was opened). Split into documented logical phases.

For the genesis round:

- Challenge window **extended to 30 days** (vs the standard 7).
- Explicit notification to the first prospective investors **before they invest**.
- No "founder" bonus.

See the dry run in `rounds/archives/2026-05-genesis/` for the first iteration.

## 7. Operational guardrails

The Aratea token is not intended to be traded on a secondary market — it represents a pro-rata share of the NAV and a governance right. Issuance caps traditionally exist to protect a market price; that logic does not apply here. The guardrails below concern process quality (validation, fraud, audit), not issuance velocity. No global monthly cap and no per-contributor cap is imposed.

- **Automatic token-weighted vote** for large valuations: any contributor valued above 0.01 BTC in a round goes to a weighted holder vote, even with no contest.
- **Newcomer cooldown**: first merged contribution must be more than 30 days old before mint eligibility.
- **Slashing**: 6-month clawback where fraud is established by a 67 % vote.
- **Annual audit**: rubric, rate table and past valuations reviewed at the holder assembly.

## 8. Evolution of the system

- **Phase 1 (≤ 20 contributors)**: 5-holder panel. Ratification by GitHub Action if uncontested, panel otherwise.
- **Phase 2 (20-50)**: 7-holder panel. Possible addition of an automated peer-feedback module (cross-signals from PR reviews, still fact-based).
- **Phase 3 (DAO live, > 50)**: 11-holder panel. Token-weighted vote on parameters. Quarterly retroactive rounds.

## 9. Honest risks

1. **Invisible, unrewarded coordination.** Mitigation: encourage signed public digests. If it is not in Git, it is not valued.
2. **Gaming the diff.** The rubric penalises technical debt and "modest/low" impact adjustments. The panel remains the ultimate authority.
3. **BTC volatility.** Offset by quarterly recalibration.
4. **A polarised Top X panel.** Mitigation: vote transparency, annual review.
5. **AI under-estimation for certain categories.** Annual audit against real freelance rates.

## 10. Current implementation

Phase 1 MVP on GitHub Actions + a Safe multisig. No custom smart contract yet. See `rounds/scripts/` for the skeleton of the collection GitHub Action, `rounds/agent/PROMPT.md` for the system prompt, and `contracts/README.md` for the roadmap of the contracts to come.

## 11. See also

- Overall project architecture → [`architecture.md`](architecture.md)
- Token model (§7.7 Guardrails) → [`token_model.md`](token_model.md)
- **Draft articles of association, FR** (art. 4 bis transparency + art. 32 valuation engine + art. 31 slashing) → [`../../statuts-aratea-v0-projet-2026-05-16.md`](../../statuts-aratea-v0-projet-2026-05-16.md)
- **Draft Articles of Association EN** → [`../../statuts-aratea-v0-projet-2026-05-16-EN.md`](../../statuts-aratea-v0-projet-2026-05-16-EN.md)
