> [Lire en français](README.fr.md)

# contracts

Solidity smart contracts for the Aratea protocol. **Phase 1 in progress** — building the on-chain settlement layer for the labor-value mint mechanism described in [`/docs/token_model.md`](../docs/token_model.md).

## Status

Phase 1 — *active*. Milestones M0 through M5. See [`/docs/architecture.md`](../docs/architecture.md) for project-level phasing.

## Phase 1 scope

The on-chain primitives that ratify and execute the monthly mint rounds already produced off-chain (see [`/rounds/`](../rounds/)):

1. **`AugPocToken`** — ERC-20 with `ERC20Permit`, `AccessControl`, and `Pausable`. 18 decimals (Ethereum standard). No fixed supply cap. Four roles: `DEFAULT_ADMIN_ROLE`, `MINTER_ROLE` (RoundRegistry), `PAUSER_ROLE` (Safe), `BURNER_ROLE` (reserved for the future `AraConverter` that will execute the `AUG-POC → ARA` conversion at the Phase 2 DAO launch — see white paper §7.2). Pause blocks user-to-user transfers only; mint and burn remain operational.
2. **`RoundRegistry`** — propose / challenge / execute / cancel lifecycle for monthly mint rounds. Each round is anchored to its IPFS hash (the `valuation_report.md` snapshot from `/rounds/archives/<round-id>/`). No on-chain emission cap — the Aratea token is not designed to be traded, so a per-supply cap to protect a price is not relevant. Quality is guaranteed off-chain by the valuation rubric, the token-weighted vote on individual valuations above 0.01 BTC, the new-entrant cooldown, the slashing mechanism, and the annual audit (white paper §7.7).

Out of scope in Phase 1 (scaffolded, not implemented): on-chain `ARA` governance token + `Governor`, automated NAV oracle, parametric mutual contracts, on-chain Top-X holder voting.

## Layout

```
contracts/
├── src/
│   ├── token/                      # M1 — AugPocToken
│   ├── rounds/                     # M3 — RoundRegistry
│   └── interfaces/                 # IAugPocToken, IRoundRegistry
├── test/
│   ├── unit/                       # ≥ 95% line coverage on business logic
│   ├── fuzz/                       # 10 000 runs default
│   └── invariant/                  # supply / cap / role invariants
├── script/                         # M4 — deployment + Safe calldata generators
├── docs/                           # bilingual FR/EN — architecture, security, deployment, lifecycle
├── foundry.toml
├── slither.config.json
├── remappings.txt
├── .env.example                    # placeholders for Arbitrum Sepolia
└── README.md / README.fr.md
```

## Toolchain

- **Foundry** (forge, cast, anvil) — pinned to stable releases via CI.
- **Solidity 0.8.24**, EVM `paris`, optimizer 200 runs.
- **OpenZeppelin Contracts v5.1.0** for every primitive (ERC20, AccessControl, Pausable, ReentrancyGuard, SafeERC20, ERC20Permit). No hand-rolled re-implementation.
- **`forge-std` v1.9.4** for tests and scripts.
- **Slither 0.10.4** for static analysis (CI fails on `medium`).
- **CI** at `.github/workflows/contracts-ci.yml` — runs on every push / PR touching `contracts/**`.

## Target chain

Arbitrum Sepolia (testnet) in Phase 1. Mainnet deployment is **blocked** until at least one community audit (Code4rena Arena-X, Sherlock Watson, or documented peer review) is complete.

## Build & test

> Foundry must be installed locally. See [getfoundry.sh](https://book.getfoundry.sh/getting-started/installation).

```bash
# from contracts/
forge install --no-commit foundry-rs/forge-std@v1.9.4 OpenZeppelin/openzeppelin-contracts@v5.1.0
forge build
forge test -vvv
forge coverage --report summary
```

CI runs the same commands on every PR — local install is only needed for development.

## Security model (short version)

- All privileged roles (`MINTER_ROLE`, `PAUSER_ROLE`, `ROUND_PROPOSER_ROLE`, `ROUND_EXECUTOR_ROLE`) are held by a Safe multisig on Arbitrum Sepolia. **Never an EOA.**
- No upgradeability initially. Bug fixes ship as new deployments + migration.
- Strict Checks-Effects-Interactions, `ReentrancyGuard` on every external transfer surface, `SafeERC20` for all ERC20 interactions.
- Required tests at three levels: unit (≥ 95 % coverage), fuzz (10 000 runs), invariants on critical properties (`token.totalSupply()` equals the sum of executed round amounts; no mint without expired challenge window; `MINTER_ROLE` held only by the Safe).

Full threat model in [`docs/SECURITY.md`](docs/SECURITY.md).

## Lifecycle of a round (Phase 1)

```
   ┌────────────────────┐
   │  Off-chain agent   │  ───►  /rounds/archives/<round-id>/valuation_report.md
   │  produces report   │
   └─────────┬──────────┘
             │ founder ratifies + pins to IPFS
             ▼
   ┌────────────────────┐
   │ Safe.proposeRound  │  ───►  RoundRegistry.proposeRound()
   │  (calldata)        │        emits RoundProposed event
   └─────────┬──────────┘
             │
             ▼
   ┌────────────────────┐         ┌─────────────────────┐
   │ Challenge window   │  ───►   │  challengeRound()    │  (anyone)
   │ (7 d / 30 d genesis)│         │  → status Challenged │
   └─────────┬──────────┘         └─────────┬───────────┘
             │ window expires + status == Proposed
             ▼                               │ Safe reviews off-chain panel vote
   ┌────────────────────┐                    ▼
   │ Safe.executeRound  │              ┌─────────────────────┐
   │  → mint to bens    │              │ Safe.cancelRound() │
   │  (no on-chain cap) │              └─────────────────────┘
   └────────────────────┘
```

Detail in [`docs/ROUND-LIFECYCLE.md`](docs/ROUND-LIFECYCLE.md).

## Phase 2 — automatic mint + token-weighted contestation

> Testnet / pre-audit. Full spec and decisions: [`/docs/gouvernance-auto-mint.fr.md`](../docs/gouvernance-auto-mint.fr.md).

A `MintGovernor` sits **on top of the unchanged `RoundRegistry`** (still the sole minter) to make the monthly mint automatic yet contestable:

- **Nominal**: a keeper (proposer only) proposes a round at J0; after the challenge window, anyone calls `MintGovernor.finalize` → the Governor (sole executor) mints. No daily human signature.
- **Contested**: a token holder calls `MintGovernor.challenge` → a token-weighted vote opens. **Vote weight is frozen at the round's `proposedAt`** via `ERC20Votes` checkpoints (timestamp clock) — tokens bought after the proposal carry no weight. The original is rejected iff **quorum reached (15% of circulating) AND `against > for`**; otherwise it mints. On rejection, holders ≥ 1% submit alternatives, voted **sequentially** at simple majority; the first accepted mints and cancels the rest.

Role topology (least privilege): keeper = `ROUND_PROPOSER_ROLE` only (hot key, in CI); Governor = `PROPOSER`+`EXECUTOR`+`CANCELLER`+`CHALLENGER`; admin = `DEFAULT_ADMIN` + `CANCELLER` circuit-breaker (cold key, out of CI, EXECUTOR revoked). `MINTER_ROLE` stays with the registry. Wired by `script/DeployPhase2Governor.s.sol`.

Minimal registry change: `challengeRound` is now gated by a new `ROUND_CHALLENGER_ROLE` (held by the Governor) so a stake-free direct challenge cannot freeze a round with no vote to resolve it. See the spec §8 for the full deviation list.

Keeper operations: `script/KeeperProposeRound.s.sol` + `script/KeeperFinalize.s.sol`, driven by the scheduled `.github/workflows/aratea-keeper.yml` (keeper key as a CI secret; admin key never in CI).

## Roadmap (milestones)

| Milestone | Scope | Status |
|---|---|---|
| **M0** | Foundry scaffold, CI, threat model, bilingual doc | ✅ done |
| **M1** | `AugPocToken` (ERC20 + Permit + AccessControl + Pausable + 4 roles) | ✅ done |
| **M2** | ~~`MonthlyMintCap` library~~ — removed 2026-05-17 (no on-chain cap, see §7.7) | — |
| **M3** | `RoundRegistry` (propose / challenge / execute / cancel) | ✅ done |
| **M4** | Deployment scripts on Arbitrum Sepolia + operational helpers | ✅ done |
| **M5** | Read-only dashboard (Next.js + viem) | pending |
| **M6** | Phase 2 — `MintGovernor` (auto-mint + token-weighted vote) + keeper | ✅ done (testnet, pre-audit) |

## License

Apache 2.0 — see [/LICENSE](../LICENSE).
