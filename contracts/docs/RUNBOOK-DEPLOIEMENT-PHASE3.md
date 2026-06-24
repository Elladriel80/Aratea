# Runbook — Phase 3 deployment (parametric insurance) on testnet

> Procedure for deploying the Phase 3 stack on Arbitrum Sepolia:
> `PricingEngine` + `PremiumPool` + `PolicyRegistry` + `MockWeatherOracle`.
> End result: subscribers can pay a USDC premium to receive an automatic payout
> if temperature crosses a threshold on the target date.
>
> **Prerequisites**:
> - Phase 2 operational (see `RUNBOOK-REDEPLOIEMENT-COMPLET.md`)
> - USDC (ERC-20, 6 decimals) available on the target network
> - G2 gate not required for testnet deploy; required for real policies in production
>   (reduces `adverse_loading` from 5% to 2%)
>
> **Mainnet gating**: testnet deployment is possible now.
> Mainnet with real policies requires:
> 1. G2 gate confirmed (Brier < market, p < 0.05)
> 2. 200 000 € in association equity (MCR floor)
> 3. External legal opinion + ACPR sandbox

---

## 0. Environment variables

Add to `.env`:

```bash
# Admin address (association DEFAULT_ADMIN_ROLE)
ADMIN_ADDRESS=0x9a94552DCB67F036af6eccc9111b749856ab8EEA   # Ledger EOA

# USDC on target network
USDC_ADDRESS=0x<usdc_address>

# Oracle strategy:
# - Testnet: USE_MOCK_ORACLE=true (auto-deploys MockWeatherOracle)
# - Mainnet: USE_MOCK_ORACLE=false + ORACLE_ADDRESS=<ReclaimWeatherSource>
USE_MOCK_ORACLE=true

# Fill in after broadcast:
# POLICY_REGISTRY_ADDRESS=0x...
# PREMIUM_POOL_ADDRESS=0x...
# PRICING_ENGINE_ADDRESS=0x...
# MOCK_ORACLE_ADDRESS=0x...
```

---

## 1. Dry-run (no broadcast)

```bash
cd contracts
source .env

forge script script/DeployPhase3.s.sol:DeployPhase3 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --sender $ADMIN_ADDRESS \
  -vv
```

Expected output ends with `== Phase 3 wiring complete ==`.

---

## 2. Broadcast with Ledger (5 confirmations)

```bash
forge script script/DeployPhase3.s.sol:DeployPhase3 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger \
  --sender $ADMIN_ADDRESS \
  --hd-paths "m/44'/60'/0'/0/0" \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  -vv
```

**Ledger confirmations:**

| # | Transaction | Purpose |
|---|---|---|
| 1 | `new PricingEngine(admin)` | Deploy actuarial pricing engine |
| 2 | `new PremiumPool(admin, usdc)` | Deploy USDC reserve pool |
| 3 | `new MockWeatherOracle()` | Deploy testnet oracle |
| 4 | `new PolicyRegistry(admin, usdc, engine, pool, oracle)` | Deploy policy lifecycle contract |
| 5 | `pool.grantRole(POLICY_REGISTRY_ROLE, policyRegistry)` | Wire pool → registry |

**Total: 5 Ledger confirmations.**

---

## 3. Post-deploy: record addresses

Copy the logged addresses into `.env`:

```bash
POLICY_REGISTRY_ADDRESS=0x<address>
PREMIUM_POOL_ADDRESS=0x<address>
PRICING_ENGINE_ADDRESS=0x<address>
MOCK_ORACLE_ADDRESS=0x<address>   # testnet only
```

---

## 4. Grant KEEPER_ROLE on PolicyRegistry

```bash
cast send $POLICY_REGISTRY_ADDRESS \
  "grantRole(bytes32,address)" \
  $(cast keccak "KEEPER_ROLE") \
  $KEEPER_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger --sender $ADMIN_ADDRESS
```

---

## 5. Enable supported weather series

```bash
KXHIGHTSFO=$(cast keccak "KXHIGHTSFO")

cast send $POLICY_REGISTRY_ADDRESS \
  "setSupportedLocation(bytes32,bool)" \
  $KXHIGHTSFO true \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger --sender $ADMIN_ADDRESS
```

Priority series (current predictor coverage):
`KXHIGHTSFO`, `KXLOWTCHI`, `KXLOWTNYC`, `KXLOWTMIA`, `KXLOWTBOS`, `KXLOWTLAX`

---

## 6. Update dashboard

Set Vercel environment variables:

```
NEXT_PUBLIC_POLICY_REGISTRY_ADDRESS=0x<address>
NEXT_PUBLIC_PREMIUM_POOL_ADDRESS=0x<address>
NEXT_PUBLIC_PRICING_ENGINE_ADDRESS=0x<address>
```

---

## 7. End-to-end test (testnet, MockWeatherOracle)

```bash
# 1. Subscribe a policy (subscriber wallet)
cast send $POLICY_REGISTRY_ADDRESS \
  "subscribe(bytes32,uint64,uint256,uint16,uint16)" \
  $KXHIGHTSFO $TARGET_DATE $SUM_ASSURED $THRESHOLD_F_TIMES10 $P_BPS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA --private-key $SUBSCRIBER_PRIVATE_KEY

# 2. Post oracle result (keeper, testnet only)
cast send $MOCK_ORACLE_ADDRESS \
  "postResult(bytes32,uint64,int16)" \
  $KXHIGHTSFO $TARGET_DATE $OBSERVED_TEMP_F_TIMES10 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA --private-key $KEEPER_PRIVATE_KEY

# 3. Settle the policy (keeper, after targetDate)
POLICY_REGISTRY_ADDRESS=$POLICY_REGISTRY_ADDRESS \
POLICY_ID=$POLICY_ID \
forge script script/KeeperSettlePolicy.s.sol \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --private-key $KEEPER_PRIVATE_KEY \
  --broadcast -vv
```

---

## Post-deployment checklist

- [ ] PricingEngine deployed and verified (Arbiscan)
- [ ] PremiumPool deployed, `POLICY_REGISTRY_ROLE` granted to PolicyRegistry
- [ ] PolicyRegistry deployed, `KEEPER_ROLE` granted to keeper
- [ ] Weather series enabled (`setSupportedLocation`)
- [ ] Dashboard Vercel env updated (`NEXT_PUBLIC_*`)
- [ ] End-to-end subscribe → postResult → settlePolicy test passed
- [ ] (Mainnet only) Pool seeded with ≥ 200 000 USDC (MCR floor)
