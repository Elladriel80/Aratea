# Runbook — full-stack redeploy (Phase 1 → Genesis → Phase 2)

> **Context (blocker DEPLOY-1)**: the registry deployed in May 2026
> (`0xA2324C2E467a6F38032586C1d650BBcC13F11F3F`) was built from a code version
> that predates the addition of `ROUND_CHALLENGER_ROLE`. The `DeployPhase2Governor`
> script tries to read this constant from the deployed registry and reverts. The
> old Phase 1 contracts are therefore **incompatible** with the current Phase 2.
> **Solution: full redeploy from scratch** on the current code.
>
> Dry-run validated end-to-end on 2026-06-21 (test `FullStackRedeployTest`,
> 7/7 assertions green — see `test/unit/FullStackRedeployTest.t.sol`).
>
> **Testnet one-session mode (2026-06-23)**: the challenge window is now configurable
> in seconds via `CHALLENGE_WINDOW_SECONDS`. Testnet value: **300 s** (5 min) →
> Phase 1 → Genesis (propose) → wait 5 min → Execute → Phase 2 in a **single session**.
> Mainnet: keep 2 592 000 s (30 days). The contract enforces `[60 s ; 365 d]`.
> `FullStackRedeployTest` updated with `GENESIS_WINDOW_SEC = 300`.

---

## 0. Before you start

### Update `.env` (remove old addresses)

```bash
# ── OLD Phase 1 addresses (obsolete — do NOT use) ──
# OLD_TOKEN_ADDRESS=0x56a754632f19996649E78818BcD8ee388D2871Ee
# OLD_REGISTRY_ADDRESS=0xA2324C2E467a6F38032586C1d650BBcC13F11F3F

# ── Keep these ──
ADMIN_ADDRESS=0x9a94552DCB67F036af6eccc9111b749856ab8EEA
RPC_ARBITRUM_SEPOLIA=https://sepolia-rollup.arbitrum.io/rpc
ETHERSCAN_API_KEY=<your_key>

# ── Genesis (unchanged — same valuation report) ──
GENESIS_BENEFICIARY=0x9a94552DCB67F036af6eccc9111b749856ab8EEA
PROPOSER_ADDRESS=0x9a94552DCB67F036af6eccc9111b749856ab8EEA
GENESIS_IPFS_URI=ipfs://bafybeih5jb2vk577w57uw62m4j7opyke4poryrphscydhzmd3htvm2ug7u

# ── Challenge window (NEW — in seconds) ──
# Testnet one-session (5 min):
CHALLENGE_WINDOW_SECONDS=300
# Mainnet (30 days): comment the line above and uncomment:
# CHALLENGE_WINDOW_SECONDS=2592000

# TOKEN_ADDRESS and REGISTRY_ADDRESS will be added after step 1.
```

### KEEPER_ADDRESS (TODO before step 3)

```bash
cast wallet address --private-key $KEEPER_PRIVATE_KEY
# Add to .env: KEEPER_ADDRESS=0x<result>
```

---

## 1. Step 1 — Deploy Phase 1 (new token + new registry)

**7 Ledger confirmations**

| # | Transaction |
|---|-------------|
| 1 | `new AugPocToken(admin)` |
| 2 | `new RoundRegistry(admin, token)` |
| 3 | `token.grantRole(MINTER_ROLE, registry)` |
| 4 | `token.grantRole(PAUSER_ROLE, admin)` |
| 5 | `registry.grantRole(ROUND_PROPOSER_ROLE, admin)` |
| 6 | `registry.grantRole(ROUND_EXECUTOR_ROLE, admin)` |
| 7 | `registry.grantRole(ROUND_CANCELLER_ROLE, admin)` |

```bash
cd contracts
source .env

forge script script/DeployArateaPhase1.s.sol:DeployArateaPhase1 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger \
  --sender $ADMIN_ADDRESS \
  --hd-paths "m/44'/60'/0'/0/0" \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  -vv
```

**After broadcast**, add to `.env`:

```bash
TOKEN_ADDRESS=0x<new_address>     # "AugPocToken deployed at: ..."
REGISTRY_ADDRESS=0x<new_address>  # "RoundRegistry deployed at: ..."
```

**Quick sanity check — confirms current code with ROUND_CHALLENGER_ROLE:**

```bash
cast call $REGISTRY_ADDRESS "ROUND_CHALLENGER_ROLE()(bytes32)" \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → 0x... (non-zero — proves it's the new code)
```

---

## 2. Step 2 — Propose genesis round on the NEW registry

**1 Ledger confirmation**

| # | Transaction |
|---|-------------|
| 8 | `registry.proposeRound(hash, [ELLADRIEL], [34_039_500e18], ipfsUri, CHALLENGE_WINDOW_SECONDS)` |

```bash
source .env   # TOKEN_ADDRESS, REGISTRY_ADDRESS + CHALLENGE_WINDOW_SECONDS now set

BROADCAST=true forge script script/ProposeGenesisRound.s.sol:ProposeGenesisRound \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger \
  --sender $PROPOSER_ADDRESS \
  --hd-paths "m/44'/60'/0'/0/0" \
  --broadcast \
  -vv
```

Output will show `Challenge window (seconds): 300` (testnet) or `2592000` (mainnet).

**Note the `roundHash`** printed in the output — needed for step 2b.

---

## ⏳ Wait for the challenge window

| Mode | Wait | Env var |
|------|------|---------|
| **Testnet one-session** | **300 seconds (5 min)** | `CHALLENGE_WINDOW_SECONDS=300` |
| Mainnet / production | 30 days (2 592 000 s) | `CHALLENGE_WINDOW_SECONDS=2592000` |

Check window expiry:
```bash
cast call $REGISTRY_ADDRESS "windowEndOf(bytes32)(uint256)" $ROUND_HASH \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
```

---

## 2b. Step 2b — Execute genesis round (after window expires)

**1 Ledger confirmation**

| # | Transaction |
|---|-------------|
| 9 | `registry.executeRound(roundHash)` |

```bash
source .env
export ROUND_HASH=0x<round_hash_from_step_2>
export EXECUTOR_ADDRESS=$ADMIN_ADDRESS

BROADCAST=true forge script script/ExecuteRound.s.sol:ExecuteRound \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger \
  --sender $EXECUTOR_ADDRESS \
  --hd-paths "m/44'/60'/0'/0/0" \
  --broadcast \
  -vv
```

**Verify:**

```bash
cast call $TOKEN_ADDRESS "balanceOf(address)(uint256)" $GENESIS_BENEFICIARY \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → 34039500000000000000000000 (34,039,500 tokens in wei)
```

> **Important**: step 2b MUST run **before** step 3 (Phase 2).
> In Phase 2, `ROUND_EXECUTOR_ROLE` is revoked from the admin — the admin can
> no longer execute directly. Sequence: propose → wait → execute → THEN Phase 2.

---

## 3. Step 3 — Deploy Phase 2 (MintGovernor + role rewiring)

**8 Ledger confirmations**

| # | Transaction |
|---|-------------|
| 10 | `new MintGovernor(...)` |
| 11 | `registry.grantRole(ROUND_PROPOSER_ROLE, keeper)` |
| 12 | `registry.grantRole(ROUND_PROPOSER_ROLE, governor)` |
| 13 | `registry.grantRole(ROUND_EXECUTOR_ROLE, governor)` |
| 14 | `registry.grantRole(ROUND_CANCELLER_ROLE, governor)` |
| 15 | `registry.grantRole(ROUND_CHALLENGER_ROLE, governor)` |
| 16 | `registry.revokeRole(ROUND_EXECUTOR_ROLE, admin)` |
| 17 | `registry.revokeRole(ROUND_PROPOSER_ROLE, admin)` |

```bash
source .env
export KEEPER_ADDRESS=0x<keeper_address>   # TODO: fill before running

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

**After broadcast**, add to `.env` and update CI/Vercel:

```bash
GOVERNOR_ADDRESS=0x<new_address>
# GitHub Secret: GOVERNOR_ADDRESS
# Vercel: NEXT_PUBLIC_GOVERNOR_ADDRESS=0x<GOVERNOR_ADDRESS>
```

---

## 4. Final verification (Phase 2)

```bash
source .env
export GOVERNOR_ADDRESS=0x<GOVERNOR_ADDRESS>

forge script script/VerifyDeploymentPhase2.s.sol:VerifyDeploymentPhase2 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA -vv
# Expected: "== All Phase 2 assertions passed =="

# REG-1 confirmed: admin lost EXECUTOR
cast call $REGISTRY_ADDRESS "hasRole(bytes32,address)(bool)" \
  $(cast keccak "ROUND_EXECUTOR_ROLE") $ADMIN_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → false

# Governor holds CHALLENGER_ROLE (the root cause of the redeploy)
cast call $REGISTRY_ADDRESS "hasRole(bytes32,address)(bool)" \
  $(cast keccak "ROUND_CHALLENGER_ROLE") $GOVERNOR_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → true
```

---

## 5. Summary — total Ledger confirmations

| Session | When | Confirmations |
|---------|------|---------------|
| Step 1 — Phase 1 | Now | **7** |
| Step 2 — Propose Genesis | Now (same session) | **1** |
| Step 2b — Execute Genesis | After window (5 min testnet / 30 d mainnet) | **1** |
| Step 3 — Phase 2 | Right after 2b (same session on testnet) | **8** |
| **Total** | | **17** |

> **Testnet one-session**: with `CHALLENGE_WINDOW_SECONDS=300`, steps 1 → 2 → 2b → 3
> complete in a **single session** (~35 min Ledger + 5 min wait).
> Mainnet: plan 4 separate sessions (D, D, D+30, D+30).

---

## 6. Pre-flight checklist

- [ ] Old TOKEN/REGISTRY addresses commented out or removed from `.env`
- [ ] `ETHERSCAN_API_KEY` valid in `.env`
- [ ] `KEEPER_ADDRESS` derived from `KEEPER_PRIVATE_KEY` and added to `.env` (step 3)
- [ ] Local dry-run confirmed: `forge test --match-contract FullStackRedeployTest -vv` → 7/7 PASS (300 s window)
- [ ] `CHALLENGE_WINDOW_SECONDS` set in `.env` (300 testnet, 2592000 mainnet)
- [ ] Ledger connected, unlocked, Ethereum app open
- [ ] Admin wallet has enough testnet ETH for 17 txs (est. ~0.05 ETH)

---

## 7. Documented risk — DEPLOY-1 (deployment versioning ≠ code)

This scenario illustrates a structural risk: **a deployed contract may be older
than the current code**. If the code evolves after a deployment (new role, new
function), scripts that depend on the new code fail against the old deployed version.

**Mitigation**: always verify compatibility between the current code and the
deployed addresses before attempting a layered deployment (Phase 2, upgrade).
The command `cast call $REGISTRY "ROUND_CHALLENGER_ROLE()(bytes32)"` is the
minimal check to run before any Phase 2 attempt.

See also `SECURITY-AUDIT-2026-06-21.md` finding `DEPLOY-1`.
