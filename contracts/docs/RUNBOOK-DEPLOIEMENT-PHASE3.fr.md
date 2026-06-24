# Runbook — déploiement Phase 3 (assurance paramétrique) sur testnet

> Procédure pour déployer la stack Phase 3 sur Arbitrum Sepolia :
> `PricingEngine` + `PremiumPool` + `PolicyRegistry` + `MockWeatherOracle`.
> Résultat : un souscripteur peut payer une prime USDC pour être indemnisé
> automatiquement si la température franchit un seuil le jour cible.
>
> **Prérequis** :
> - Phase 2 opérationnelle (voir `RUNBOOK-REDEPLOIEMENT-COMPLET.fr.md`)
> - Contrat USDC (ERC-20, 6 décimales) disponible sur le réseau cible
> - Gate G2 non requise pour le déploiement testnet ; elle est requise pour
>   activer des vraies polices en production (réduction du `adverse_loading`)
>
> **Gating mainnet** : déploiement testnet possible maintenant.
> Déploiement mainnet avec vraies polices exige :
> 1. Gate G2 confirmée (Brier < marché, p < 0,05)
> 2. 200 000 € de fonds propres de l'association (MCR floor)
> 3. Avis juridique externe + sandbox ACPR

---

## 0. Variables d'environnement

Ajoute dans `.env` :

```bash
# Adresse admin (DEFAULT_ADMIN_ROLE de l'association)
ADMIN_ADDRESS=0x9a94552DCB67F036af6eccc9111b749856ab8EEA   # Ledger EOA

# USDC sur le réseau cible
# Arbitrum Sepolia test USDC (Circle) : déploie un MockERC20 si inexistant
USDC_ADDRESS=0x<adresse_usdc>

# Oracle météo :
# - Testnet : USE_MOCK_ORACLE=true (déploie MockWeatherOracle automatiquement)
# - Mainnet : USE_MOCK_ORACLE=false + ORACLE_ADDRESS=<ReclaimWeatherSource>
USE_MOCK_ORACLE=true
# ORACLE_ADDRESS=0x<oracle_si_USE_MOCK_ORACLE=false>

# Informations post-déploiement (remplir après le broadcast)
# POLICY_REGISTRY_ADDRESS=0x...
# PREMIUM_POOL_ADDRESS=0x...
# PRICING_ENGINE_ADDRESS=0x...
# MOCK_ORACLE_ADDRESS=0x...   (si USE_MOCK_ORACLE=true)
```

---

## 1. Option : déployer un USDC de test

Si aucun USDC n'est disponible sur Arbitrum Sepolia, déploie un `MockERC20` :

```bash
# Déployer un USDC mock (6 décimales) — signer = admin
cast send --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --private-key $ADMIN_PRIVATE_KEY \
  --create \
  $(cast abi-encode "constructor(string,string,uint8)" "Mock USDC" "USDC" 6)
```

Ou utilise le USDC Circle officiel sur Arbitrum Sepolia (si disponible).

---

## 2. Dry-run local (sans broadcast)

```bash
cd contracts
source .env

forge script script/DeployPhase3.s.sol:DeployPhase3 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --sender $ADMIN_ADDRESS \
  -vv
```

La simulation doit afficher :
```
== DeployPhase3 ==
Admin: 0x9a94...
USDC:  0x...
Mock oracle: true
PricingEngine: 0x...
PremiumPool:   0x...
MockWeatherOracle: 0x...
PolicyRegistry: 0x...
== Phase 3 wiring complete ==
```

---

## 3. Broadcast avec Ledger (3 confirmations)

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

**Confirmations Ledger attendues :**

| # | Transaction | Rôle |
|---|---|---|
| 1 | `new PricingEngine(admin)` | Déploiement moteur actuariel |
| 2 | `new PremiumPool(admin, usdc)` | Déploiement réserves |
| 3 | `new MockWeatherOracle()` | Déploiement oracle testnet |
| 4 | `new PolicyRegistry(admin, usdc, engine, pool, oracle)` | Déploiement registre polices |
| 5 | `pool.grantRole(POLICY_REGISTRY_ROLE, policyRegistry)` | Autorisation pool → registry |

**Total : 5 confirmations Ledger.**

---

## 4. Après le broadcast : noter les adresses

Copie les adresses affichées dans `.env` :

```bash
POLICY_REGISTRY_ADDRESS=0x<adresse>
PREMIUM_POOL_ADDRESS=0x<adresse>
PRICING_ENGINE_ADDRESS=0x<adresse>
MOCK_ORACLE_ADDRESS=0x<adresse>   # si testnet
```

---

## 5. Configurer le keeper (KEEPER_ROLE sur PolicyRegistry)

Le keeper est l'EOA qui appelle `settlePolicy()` après l'oracle.
Sur testnet, c'est la même clé que le keeper Phase 2 (CI).

```bash
# Depuis le wallet admin
cast send $POLICY_REGISTRY_ADDRESS \
  "grantRole(bytes32,address)" \
  $(cast keccak "KEEPER_ROLE") \
  $KEEPER_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger --sender $ADMIN_ADDRESS
```

---

## 6. Activer les séries météo supportées

Avant qu'un souscripteur puisse ouvrir une police, la location key doit être activée :

```bash
# locationKey = keccak256 du nom de la série (ex: "KXHIGHTSFO")
KXHIGHTSFO=$(cast keccak "KXHIGHTSFO")

cast send $POLICY_REGISTRY_ADDRESS \
  "setSupportedLocation(bytes32,bool)" \
  $KXHIGHTSFO true \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger --sender $ADMIN_ADDRESS
```

Séries prioritaires (6 séries actuelles du predictor) :
- `KXHIGHTSFO` — San Francisco max
- `KXLOWTCHI`  — Chicago min
- `KXLOWTNYC`  — New York min
- `KXLOWTMIA`  — Miami min
- `KXLOWTBOS`  — Boston min
- `KXLOWTLAX`  — Los Angeles min

---

## 7. Mettre à jour le dashboard

Définis ces variables dans Vercel (env variables du projet) :

```
NEXT_PUBLIC_POLICY_REGISTRY_ADDRESS=0x<adresse>
NEXT_PUBLIC_PREMIUM_POOL_ADDRESS=0x<adresse>
NEXT_PUBLIC_PRICING_ENGINE_ADDRESS=0x<adresse>
```

La page `/insurance` affichera alors l'état du pool en temps réel.

---

## 8. Tester une police end-to-end (testnet, MockWeatherOracle)

```bash
# 1. Minter du USDC de test au souscripteur (si MockERC20)
cast send $USDC_ADDRESS "mint(address,uint256)" $SUBSCRIBER 100000000 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA --private-key $ADMIN_PRIVATE_KEY

# 2. Approuver le transfer USDC vers PolicyRegistry
cast send $USDC_ADDRESS "approve(address,uint256)" $POLICY_REGISTRY_ADDRESS 100000000 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA --private-key $SUBSCRIBER_PRIVATE_KEY

# 3. Calculer la prime (ex: KXHIGHTSFO, demain 15:00 UTC, 100 USDC assuré, seuil 90°F×10=900)
TARGET_DATE=$(date -d "tomorrow 15:00 UTC" +%s)
cast call $POLICY_REGISTRY_ADDRESS \
  "quotePolicy(bytes32,uint64,uint256,uint16,uint16)" \
  $KXHIGHTSFO $TARGET_DATE 100000000 900 7000 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA

# 4. Souscrire la police
cast send $POLICY_REGISTRY_ADDRESS \
  "subscribe(bytes32,uint64,uint256,uint16,uint16)" \
  $KXHIGHTSFO $TARGET_DATE 100000000 900 7000 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA --private-key $SUBSCRIBER_PRIVATE_KEY

# 5. Poster un résultat oracle (testnet uniquement — MockWeatherOracle)
cast send $MOCK_ORACLE_ADDRESS \
  "postResult(bytes32,uint64,int16)" \
  $KXHIGHTSFO $TARGET_DATE 950 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA --private-key $KEEPER_PRIVATE_KEY

# 6. Régler la police (keeper, après targetDate)
POLICY_ID=0x<id_de_la_police_de_l_event_PolicySubscribed>
forge script script/KeeperSettlePolicy.s.sol \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --private-key $KEEPER_PRIVATE_KEY \
  --broadcast \
  -vv
```

---

## Checklist post-déploiement

- [ ] PricingEngine déployé et vérifié (Arbiscan)
- [ ] PremiumPool déployé, POLICY_REGISTRY_ROLE accordé à PolicyRegistry
- [ ] PolicyRegistry déployé, KEEPER_ROLE accordé au keeper
- [ ] Séries météo activées (`setSupportedLocation`)
- [ ] Dashboard Vercel mis à jour (`NEXT_PUBLIC_*`)
- [ ] Test end-to-end subscribe → postResult → settlePolicy réussi
- [ ] (Mainnet uniquement) Pool seedé avec ≥ 200 000 USDC (MCR floor)
