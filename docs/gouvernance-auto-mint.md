<!-- Version française : gouvernance-auto-mint.fr.md -->

# Spec — automatic mint + contest by token-weighted vote (Phase 2)

*v0.5 — 2026-06-19. Status: **implemented** (contracts + tests), **Arbitrum Sepolia testnet only, pre-audit**. See §8 for the actual implementation.*
*Decisions recorded 2026-06-17: **token-weighted** vote (1 token = 1 vote); **no per-wallet cap**. This replaces both the panel AND the 25 % cap of `token_model.md` (§6, §9).*
*Fix 2026-06-19: an alternative is now subject to the **same quorum as the original** (no longer a simple majority); the alternatives queue is **capped** (`MAX_ALTERNATIVES`).*

> ⚠️ **Audit required before mainnet.** Code that mints value, driven by an on-chain vote, is the riskiest category there is. No mainnet deployment without a community audit.

> Goal: make the monthly mint **automatic** (no day-to-day human intervention)
> while still letting token holders **contest** an allocation and impose a
> different distribution by token-weighted vote.

---

## 1. Nominal flow (nobody contests)

1. **D0** — the valuation agent computes the allocation (already automated, off-chain)
   and publishes `valuation_report.md` + the IPFS CID.
2. **D0** — a **keeper** (automated signer, the on-chain counterpart of the predictor
   cron) calls `proposeRound`. This starts the contest window.
3. **During the window** — nothing happens if nobody contests.
4. **End of window, uncontested** — the keeper calls `executeRound` → **automatic
   mint**. Done.

"Full auto" mint by default: the daily human signature disappears, replaced by the
keeper plus the contest window.

---

## 2. Contest → token-weighted vote (recorded rules)

1. A **token holder** contests during the window (`challengeRound`) → this triggers
   a vote.
2. **Token-weighted** vote: 1 token = 1 vote, **no per-wallet cap**. The contested
   round is not executed until the vote is resolved.
3. **Rejection** if: quorum is reached **AND** more than 50 % of votes cast are
   AGAINST (50 % + 1 token of those cast).
4. **If rejected** → **re-proposal** cycle: a new distribution key is proposed and
   resubmitted to a vote under the **same quorum as the original** (quorum reached
   **AND** a "for" majority). Agreement → mint. Refusal → start again. The amount of
   an alternative remains free (we want to be able to correct an under-valuation); it
   is the **quorum** that protects against capture by a large holder at low turnout.
5. **Competing proposals**: several alternatives are possible (at most
   `MAX_ALTERNATIVES` per contest), put to the vote **sequentially by submission
   date**. As soon as one is **accepted**, it is minted and **all the others are
   rejected** automatically.

---

## 3. Reconciliation with `token_model.md`

| Topic | Doc before | Decided |
|---|---|---|
| Who decides a contest | §6: Top X panel, 1 person = 1 vote | **token-weighted vote** (RECORDED — replaces the panel) |
| Weighting | §9: 1 token = 1 vote, 25 %/wallet cap | 1 token = 1 vote, **no cap** (RECORDED — the cap is removed) |
| Quorum | §9: 15 % of circulating supply | **15 %** (proposed default) |
| Majority | §9: 51 % | 50 % + 1 of votes cast |

The §6 panel is replaced. It may optionally be kept as a documented off-chain
fallback, with no on-chain role.

---

## 4. Architecture

- **`RoundRegistry` (already deployable, unchanged)**: propose / challenge / execute /
  cancel state machine. Mints at the end.
- **Keeper** (off-chain, hot key in a CI secret): `ROUND_PROPOSER_ROLE` +
  `ROUND_EXECUTOR_ROLE`. Proposes at D0, executes at the end of the window if
  uncontested.
- **`Governor` contract (new, Phase 2)**: takes over as soon as a round is contested —
  runs the token-weighted vote, manages the sequential queue of competing proposals,
  and executes only the accepted allocation.
- **Anti-vote-buying snapshot**: voting weight is frozen at the **balance at the moment
  of the proposal** (ERC20Votes / checkpoints style). **Critical** — otherwise tokens
  can be borrowed or bought to overturn a vote in progress.

Deploying the token and registry now **is not wasted effort**: the Governor is layered
on top in Phase 2, with no token redeployment.

---

## 5. Parameters — proposed defaults (to validate or adjust)

| Parameter | Proposed default | Note |
|---|---|---|
| Quorum | **15 %** of circulating supply | consistent with §9; below it the round is approved as it stands |
| Vote / proposal duration | **7 days** | aligned on the monthly cadence |
| Contest window (monthly rounds) | **7 days** | genesis = 30 d (unchanged) |
| Per-wallet cap | **none** (RECORDED) | plutocracy accepted: the largest balance weighs the most |
| Who may propose an alternative | **any holder ≥ 1 % of supply** | prevents proposal spam |
| "Circulating supply" | total minted − treasury | quorum base |
| Quorum not reached | **round approved as it stands** | treated as "uncontested" |
| Circuit breaker | `CANCELLER_ROLE` held by JS (Ledger/Safe) | emergency brake outside the vote |

---

## 6. Security, phasing, audit

- Scope is **Phase 2 DAO** (issues #1, #49, #51, #52, #53). Not Phase 1.
- An on-chain vote that controls a mint is the riskiest category → **no mainnet without
  a community audit** (existing guardrail).
- Path: (1) spec validated → (2) Governor + tests/fuzz/invariants → (3) Arbitrum Sepolia
  testnet → (4) audit → (5) mainnet.

---

## 7. Genesis does not need this module (decoupling)

At genesis there is **a single holder** (JS): the vote is trivial (100 % his). The first
mint therefore does NOT depend on the Governor. Two options:

- **A** — bootstrap genesis now (deploy + propose + execute) → tokens on-chain today;
  the Governor is added afterwards, nothing lost.
- **B** — design the whole module first, deploy once.

---

## 8. Implementation (2026-06-17)

### Contracts

- **`contracts/src/governance/MintGovernor.sol`** (new) — carries the vote, the sequential
  queue of competing proposals, quorum/thresholds, and permissionless finalisation. It
  executes only the accepted allocation, through the registry.
- **`contracts/src/token/AugPocToken.sol`** — extended with OpenZeppelin **`ERC20Votes`**
  (checkpoints) and a **timestamp clock** (ERC-6372 `mode=timestamp`). Roles and pause
  unchanged.
- **`contracts/src/rounds/RoundRegistry.sol`** — **one change only**: `challengeRound` is
  gated by a new `ROUND_CHALLENGER_ROLE` (see deviations). It remains the source of the mint.

### Role topology (wired by `script/DeployPhase2Governor.s.sol`)

| Role (registry) | Holder | Power |
|---|---|---|
| `DEFAULT_ADMIN_ROLE` | **Admin** (cold key, Ledger/Safe, outside CI) | manages roles |
| `ROUND_PROPOSER_ROLE` | **Keeper** (hot CI key) **+ Governor** | propose a round / an alternative |
| `ROUND_EXECUTOR_ROLE` | **Governor only** | mint (admin revoked) |
| `ROUND_CANCELLER_ROLE` | **Admin + Governor** | circuit breaker / cancel defeated alternatives |
| `ROUND_CHALLENGER_ROLE` | **Governor only** | single point of entry for contests |
| `MINTER_ROLE` (token) | **Registry only** | unchanged (Phase 1) |

The keeper holds **only** `ROUND_PROPOSER_ROLE` (propose + permissionless finalisation);
never a role that mints outside the rules or that changes roles.

### Parameters (defaults, configurable by the Governor's admin)

| Parameter | Default | Notes |
|---|---|---|
| `quorumBps` | **1500** (15 %) | of circulating supply at the snapshot; `ceilDiv` (rounding unfavourable to the attacker) |
| `voteDurationDays` | **7** | a vote never ends before the contest window closes |
| `proposalThresholdBps` | **100** (1 %) | minimum weight to submit an alternative |
| `treasury` | `address(0)` | if set, excluded from circulating supply — **must self-delegate** (otherwise the quorum subtraction is inaccurate) |
| `MAX_ALTERNATIVES` | **16** (constant) | maximum number of **alternatives** per contest (the original is not counted); anti-spam / anti-gas-DoS bound |

Rejection of the original = **quorum reached** (`cast ≥ quorum`) **AND** `against > for`
(strictly > 50 %; integers, no division). Quorum not reached → round approved as it stands.
An alternative is accepted = **same quorum as the original** (`cast ≥ quorum`) **AND**
`for > against`. An alternative below quorum is rejected (no mint) and we move to the next one.

**Queue cap (`MAX_ALTERNATIVES = 16`).** With no bound, a holder above the threshold could
spam `proposeAlternative` until the resolution loops (`_activateNextPending` /
`_executeWinner`, which walk the whole queue) exceed the *block gas limit* — the contest would
stay frozen. `proposeAlternative` reverts (`TooManyAlternatives`) beyond 16 alternatives. The
fix chosen is the simplest one; a "one active alternative per proposer" bound remains a
possible complementary defence if needed.

**Known limitations (documented, pre-audit).**

- *Original rejected with no alternative filed*: the round stays `Challenged` indefinitely.
  Cleanup only through the admin `CANCELLER_ROLE` (`cancelRound`) — a **manual** procedure
  accepted at this stage; a permissionless `cancelRejectedOriginal` (the Governor already
  holds `CANCELLER`) can be exposed later if the need is confirmed.
- *Treasury excluded from circulating supply*: `setTreasury` does **not** enforce treasury
  self-delegation. For the quorum subtraction to be exact, the treasury **must self-delegate**
  (`ERC20Votes` checkpoints) — to be verified when wiring the deployment.

### Deviations from the design (justified)

1. **`challengeRound` becomes role-gated (`ROUND_CHALLENGER_ROLE` → Governor).** A contest must
   trigger a vote; but a `Challenged` round can no longer be finalised permissionlessly. If
   anyone could flip a round into `Challenged` directly, they would freeze it with no vote to
   resolve it (DoS). The Governor becomes the single point of entry: its `challenge()` stays open
   to every holder. Non-regression tests updated.
2. **Snapshot = OpenZeppelin `ERC20Votes` (checkpoints), not a home-made snapshot.** More
   auditable. Consequence: a holder must **delegate** (often to themselves) for their balance to
   count as voting weight, and a treasury excluded from circulating supply must self-delegate.
   Inherent supply bound: `2^208 − 1` (≈ 4.1e62 wei), far above any realistic supply.
3. **The Governor also holds `ROUND_PROPOSER_ROLE`** (on top of `EXECUTOR`/`CANCELLER`/`CHALLENGER`):
   required to register re-proposal alternatives in the registry. Each alternative is registered
   and then **auto-challenged** (`Challenged`) so that it is never executable by permissionless
   finalisation — only the Governor's vote can mint it.

### Keeper + CI

- Foundry scripts: `KeeperProposeRound.s.sol` (D0) and `KeeperFinalize.s.sol` (end of window).
- Workflow `.github/workflows/aratea-keeper.yml`: monthly cron (finalises the current round if
  uncontested) + `workflow_dispatch` (manual propose/finalise). Keeper key in a **CI secret**,
  scoped to propose/finalise. Admin key (deployment/roles) **outside CI**.

### Tests

`forge test` (134 tests): unit + **fuzz** (quorum/majority rule, anti-vote-buying) +
**invariants** (supply only increases through executed rounds; the Governor is never admin;
keeper at least privilege). Coverage added for the 2026-06-19 fix: an alternative below quorum
is **not** accepted, an alternative at quorum is accepted (+ cancellation of its siblings), and
exceeding `MAX_ALTERNATIVES` reverts. **Slither** reports no `medium+` finding.

### End-to-end testnet scenario

1. (Prerequisite) Phase 1 deployed: `DeployArateaPhase1` (token + registry, admin = cold key).
2. `DeployPhase2Governor` (admin broadcast): deploys the Governor, wires the roles, revokes the
   admin's EXECUTOR.
3. Fill in the CI secrets/vars (keeper, RPC, addresses).
4. **Nominal**: keeper `proposeRound` (D0) → after the window, `finalize` (keeper or anyone) → mint.
5. **Contested**: a holder calls `challenge` → 7-day vote → `resolve`: upheld → mint; rejected →
   `proposeAlternative` (holder ≥ 1 %) → vote → the first accepted alternative is minted, the
   others cancelled.
