> [Lire en français](RUNBOOK-DEPLOIEMENT-PHASE2.fr.md)

# Runbook — Phase 2 deployment (MintGovernor) on testnet

> Step-by-step procedure to deploy `MintGovernor` on **Arbitrum Sepolia**,
> on top of already-deployed Phase 1 contracts (`AugPocToken` +
> `RoundRegistry`). Result: the monthly mint flow is fully automated
> (keeper proposes → window → anyone finalises → mint), with token-weighted
> contestation if a holder challenges.
>
> **Prerequisite**: Phase 1 deployed and verified (see `DEPLOYMENT.md`).
> `TOKEN_ADDRESS` and `REGISTRY_ADDRESS` must be in `.env`.

---

## 0. Before you start

### Required `.env` variables

```
ADMIN_ADDRESS=0x9a94552DCB67F036af6eccc9111b749856ab8EEA   # Ledger key, DEFAULT_ADMIN_ROLE
TOKEN_ADDRESS=0x56a754632f19996649E78818BcD8ee388D2871Ee    # from Phase 1
REGISTRY_ADDRESS=0xA2324C2E467a6F38032586C1d650BBcC13F11F3F  # from Phase 1
ETHERSCAN_API_KEY=<your_key>
RPC_ARBITRUM_SEPOLIA=https://sepolia-rollup.arbitrum.io/rpc
```

### KEEPER_ADDRESS (human TODO before broadcast)

The keeper is the CI hot key (stored as `KEEPER_PRIVATE_KEY` in GitHub Secrets).
To find its address:

```bash
cast wallet address --private-key $KEEPER_PRIVATE_KEY
```

Add to `.env` before broadcasting:

```
KEEPER_ADDRESS=0x<keeper_address>
```

> If you haven't generated the keeper key yet, create one with `cast wallet new`
> and store the private key in GitHub Secrets as `KEEPER_PRIVATE_KEY`. The keeper
> only needs `ROUND_PROPOSER_ROLE` (no admin, no direct minter).

### Governance parameters (optional — defaults are good for testnet)

```
GOVERNOR_QUORUM_BPS=1500            # 15% of circulating supply = quorum
GOVERNOR_PROPOSAL_THRESHOLD_BPS=100 # 1% = threshold to submit an alternative
GOVERNOR_VOTE_DURATION_DAYS=7       # 7-day vote window (minimum)
```

---

## 1. Local dry-run (Foundry simulation) — pre-flight check

The full Phase 1 → Phase 2 → Genesis Round dry-run was already validated
on 2026-06-20 (see `DRY-RUN-ANVIL.md`). To validate Phase 2 specifically
before broadcasting, use **Foundry simulation mode** (without `--broadcast`):

```bash
cd contracts
source .env
export KEEPER_ADDRESS=0x<your_keeper>

# Simulation (reads chain state, no tx sent)
forge script script/DeployPhase2Governor.s.sol:DeployPhase2Governor \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --sender $ADMIN_ADDRESS \
  -vv
```

The script should end with `== Phase 2 wiring complete ==` without reverting.
If it reverts, the problem is in the Phase 1 role topology — run
`forge script VerifyDeployment.s.sol` to diagnose.

---

## 2. Broadcast Phase 2 — exact Ledger command

```bash
cd contracts
source .env
export KEEPER_ADDRESS=0x<keeper_address>   # TODO: fill in before running

forge script script/DeployPhase2Governor.s.sol:DeployPhase2Governor \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger \
  --sender $ADMIN_ADDRESS \
  --hd-paths "m/44'/60'/0'/0/0" \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  -vv
```

**Expected Ledger confirmations: up to 8**

| # | Transaction | Role |
|---|-------------|------|
| 1 | `new MintGovernor(...)` | deploys the governor |
| 2 | `grantRole(ROUND_PROPOSER_ROLE, keeper)` | keeper can propose |
| 3 | `grantRole(ROUND_PROPOSER_ROLE, governor)` | governor can re-propose alternatives |
| 4 | `grantRole(ROUND_EXECUTOR_ROLE, governor)` | only governor can mint |
| 5 | `grantRole(ROUND_CANCELLER_ROLE, governor)` | governor can cancel superseded alternatives |
| 6 | `grantRole(ROUND_CHALLENGER_ROLE, governor)` | single challenge front-door |
| 7 | `revokeRole(ROUND_EXECUTOR_ROLE, admin)` | removes admin's direct mint path |
| 8 | `revokeRole(ROUND_PROPOSER_ROLE, admin)` | admin no longer proposes directly |

The script verifies wiring internally (`_assertWiring`) — it reverts if any
assertion fails.

**Role topology after Phase 2**

| Role | Phase 1 | Phase 2 |
|------|---------|---------|
| DEFAULT_ADMIN_ROLE | admin | admin (unchanged) |
| ROUND_PROPOSER_ROLE | admin | keeper + governor |
| ROUND_EXECUTOR_ROLE | admin | **governor ONLY** |
| ROUND_CANCELLER_ROLE | admin | admin + governor |
| ROUND_CHALLENGER_ROLE | — | **governor ONLY** |
| MINTER_ROLE (token) | registry | registry (unchanged) |

---

## 3. After the broadcast

### 3.1 Note the MintGovernor address

The script prints:

```
MintGovernor deployed at: 0x<GOVERNOR_ADDRESS>
```

Add to `.env`:

```
GOVERNOR_ADDRESS=0x<GOVERNOR_ADDRESS>
```

Update CI secrets and Vercel environment variables:

- GitHub Secrets: `GOVERNOR_ADDRESS`
- Vercel (dashboard): `NEXT_PUBLIC_GOVERNOR_ADDRESS=0x<GOVERNOR_ADDRESS>`

### 3.2 Independent verification

Run the dedicated Phase 2 verification script (comprehensive — all 11 wiring properties):

```bash
cd contracts
source .env
export GOVERNOR_ADDRESS=0x<GOVERNOR_ADDRESS>

forge script script/VerifyDeploymentPhase2.s.sol:VerifyDeploymentPhase2 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA -vv
```

Expected output: `== All Phase 2 assertions passed ==` + `REG-1 CONFIRMED: admin does NOT hold ROUND_EXECUTOR_ROLE`.

For quick spot checks with `cast`:

```bash
# Governor has EXECUTOR
cast call $REGISTRY_ADDRESS "hasRole(bytes32,address)(bool)" \
  $(cast keccak "ROUND_EXECUTOR_ROLE") $GOVERNOR_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → true

# Admin does NOT have EXECUTOR (REG-1)
cast call $REGISTRY_ADDRESS "hasRole(bytes32,address)(bool)" \
  $(cast keccak "ROUND_EXECUTOR_ROLE") $ADMIN_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → false
```

### 3.3 Configure keeper in CI

In `.github/workflows/aratea-keeper.yml`, `GOVERNOR_ADDRESS` must be passed
to keeper scripts (KeeperProposeRound + KeeperFinalize):

```yaml
env:
  GOVERNOR_ADDRESS: ${{ secrets.GOVERNOR_ADDRESS }}
  REGISTRY_ADDRESS: ${{ secrets.REGISTRY_ADDRESS }}
  TOKEN_ADDRESS: ${{ secrets.TOKEN_ADDRESS }}
```

---

## 4. Pre-flight checklist

- [ ] `KEEPER_ADDRESS` derived from `KEEPER_PRIVATE_KEY` and added to `.env`
- [ ] Phase 1 `TOKEN_ADDRESS` and `REGISTRY_ADDRESS` verified in `.env`
- [ ] Dry-run simulation (step 1) passes without revert
- [ ] Ledger connected, unlocked, Ethereum app open
- [ ] Arbiscan API key valid (`ETHERSCAN_API_KEY` in `.env`)
- [ ] Admin wallet (`ADMIN_ADDRESS`) has enough testnet ETH for 8 txs

---

## 5. Post-Phase-2 operational flow

Once MintGovernor is deployed, the monthly cycle runs without human intervention:

```
[D0]  Keeper → KeeperProposeRound.s.sol → round proposed, 7-day window
[D7+] Anyone → governor.finalize(roundHash) → automatic mint (if uncontested)

Contested path:
  Token holder → governor.challenge(roundHash, reasonIpfsUri)
  → 7-day token-weighted vote (weights frozen at proposal snapshot)
  → Anyone → governor.resolve(ballotRound) → mint if upheld, re-proposition if rejected
```

See `docs/ROUND-LIFECYCLE.md` for the full lifecycle.
