# Dry-run — local Anvil fork (pre-flight for testnet)

> Run the full Phase 1 → Phase 2 → Genesis Round deployment chain locally in
> ~30 seconds, with no real ETH and no Ledger. Validates scripts, role wiring,
> and contract logic end-to-end before the real testnet broadcast.
>
> See `RUNBOOK-DEPLOIEMENT-PHASE1.fr.md` for the actual testnet procedure.

---

## Prerequisites

- Foundry installed (`forge`, `anvil` in `~/.foundry/bin/`).
- Run from `contracts/`.

---

## Step 1 — Start a local Anvil node

```bash
anvil --port 8545
```

Leave it running in a separate terminal. Default accounts (all pre-funded with
10 000 ETH):

| Role   | Address                                      | Private key (test-only)                                              |
|--------|----------------------------------------------|----------------------------------------------------------------------|
| Admin  | `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` | `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80` |
| Keeper | `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` | `0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d` |

**Never use these keys anywhere but on a local Anvil node.**

---

## Step 2 — Deploy Phase 1 (AugPocToken + RoundRegistry)

```bash
export ADMIN_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

forge script script/DeployArateaPhase1.s.sol:DeployArateaPhase1 \
  --rpc-url http://127.0.0.1:8545 \
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
  --sender $ADMIN_ADDRESS \
  --broadcast -vv
```

Note the deployed addresses printed by the script:

```
AugPocToken deployed at:    <TOKEN_ADDRESS>
RoundRegistry deployed at:  <REGISTRY_ADDRESS>
```

Expected on a fresh Anvil (chain 31337, first deployment):

- `TOKEN_ADDRESS`    = `0x5FbDB2315678afecb367f032d93F642f64180aa3`
- `REGISTRY_ADDRESS` = `0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512`

The script asserts role wiring internally. If the final line reads
`== Deployment complete ==`, Phase 1 is correct.

---

## Step 3 — Deploy Phase 2 Governor

```bash
export TOKEN_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
export REGISTRY_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
export KEEPER_ADDRESS=0x70997970C51812dc3A010C7d01b50e0d17dc79C8

forge script script/DeployPhase2Governor.s.sol:DeployPhase2Governor \
  --rpc-url http://127.0.0.1:8545 \
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
  --sender $ADMIN_ADDRESS \
  --broadcast -vv
```

Expected: `== Phase 2 wiring complete ==`. The MintGovernor address on a fresh
Anvil is `0xa513E6E4b8f2a923D98304ec87F64353C4D5C853`.

Role changes applied by Phase 2:

| Role                 | Before (Phase 1) | After (Phase 2)          |
|----------------------|------------------|--------------------------|
| ROUND_PROPOSER_ROLE  | admin            | keeper + governor        |
| ROUND_EXECUTOR_ROLE  | admin            | governor ONLY            |
| ROUND_CANCELLER_ROLE | admin            | admin + governor         |
| ROUND_CHALLENGER_ROLE| (nobody)         | governor ONLY            |

---

## Step 4 — Propose Genesis Round

```bash
export PROPOSER_ADDRESS=0x70997970C51812dc3A010C7d01b50e0d17dc79C8
export GENESIS_BENEFICIARY=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
export GENESIS_IPFS_URI=ipfs://bafybeianvilsectest000000000000000000000000
export BROADCAST=true

forge script script/ProposeGenesisRound.s.sol:ProposeGenesisRound \
  --rpc-url http://127.0.0.1:8545 \
  --private-key 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d \
  --sender $PROPOSER_ADDRESS \
  --broadcast -vv
```

Expected: `Round proposed on-chain.` with amount `34 039 500` tokens and
challenge window `30` days.

---

## Pre-flight checklist (before real testnet broadcast)

Before running the above sequence against Arbitrum Sepolia, verify each item:

### Environment
- [ ] `RPC_ARBITRUM_SEPOLIA` points to a working endpoint (Alchemy/Infura/public)
- [ ] Admin EOA funded with ETH on Arbitrum Sepolia (≥ 0.01 ETH covers all txs)
- [ ] Keeper EOA funded with ETH (for ProposeGenesisRound + future keepers calls)
- [ ] `ETHERSCAN_API_KEY` valid (Etherscan V2 unified key covers Arbitrum Sepolia)

### Pinata / IPFS
- [ ] `rounds/archives/2026-05-genesis/valuation_report.md` pinned on Pinata
- [ ] CID retrieved and `GENESIS_IPFS_URI=ipfs://<CID>/valuation_report.md` set
- [ ] URI resolves via a public gateway

### Script dry-runs (do these BEFORE the real broadcast)
- [ ] Local Anvil dry-run passes end-to-end (Phase 1 → Phase 2 → Genesis)
- [ ] `forge script ProposeGenesisRound ... --broadcast=false -vv` prints correct
      hash, amount (34 039 500 tokens), window (30 days)

### Secrets
- [ ] No private keys in `.env` or committed to git (use `--account` keystore or Ledger)
- [ ] `.env` is in `.gitignore` and not staged (`git status` shows clean)
- [ ] Pinata JWT rotated after Phase 1 deploy (CI uses `aratea-ci-*` keys only)

### Post-deploy verification
- [ ] `forge script script/VerifyDeployment.s.sol --rpc-url arbitrum_sepolia -vv`
      passes with the real deployed addresses
- [ ] Etherscan shows contracts verified (if `--verify` flag was used)

### Phase 2 specific
- [ ] Admin lost `ROUND_EXECUTOR_ROLE` (no direct mint path after Phase 2)
- [ ] Governor address set as `GOVERNOR_ADDRESS` in CI secrets for keeper scripts
- [ ] Keeper private key stored in GitHub Secrets as `KEEPER_PK`

---

## Validated dry-run (2026-06-20)

Sequence run against Anvil chain 31337:

| Step               | Result |
|--------------------|--------|
| Deploy Phase 1     | ✅ AugPocToken + RoundRegistry deployed, all assertions pass |
| Deploy Phase 2     | ✅ MintGovernor deployed, role wiring verified |
| Propose Genesis    | ✅ 34 039 500 tokens, 30-day window, round hash logged |

All 162 tests (unit + fuzz + invariant) pass. Coverage: MintGovernor 91.49%
branches, RoundRegistry 100%.
