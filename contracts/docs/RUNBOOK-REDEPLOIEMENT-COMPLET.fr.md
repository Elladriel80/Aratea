# Runbook — redéploiement complet (Phase 1 → Genesis → Phase 2)

> **Contexte (bloqueur DEPLOY-1)** : le registry déployé en mai 2026
> (`0xA2324C2E467a6F38032586C1d650BBcC13F11F3F`) a été produit à partir d'une
> version de code antérieure à l'ajout de `ROUND_CHALLENGER_ROLE`. Le script
> `DeployPhase2Governor` tente de lire cette constante sur le registry déployé et
> reverte. Les anciens contrats Phase 1 sont donc **incompatibles** avec la Phase 2
> actuelle. **Solution : redéploiement complet depuis zéro** sur le code courant.
>
> Dry-run validé de bout en bout le 2026-06-21 (test `FullStackRedeployTest`,
> 7/7 assertions vertes — voir `test/unit/FullStackRedeployTest.t.sol`).

---

## 0. Avant de commencer

### Mettre à jour `.env` (supprimer les anciennes adresses)

```bash
# ── ANCIENNES adresses Phase 1 (obsolètes — NE PLUS UTILISER) ──
# OLD_TOKEN_ADDRESS=0x56a754632f19996649E78818BcD8ee388D2871Ee
# OLD_REGISTRY_ADDRESS=0xA2324C2E467a6F38032586C1d650BBcC13F11F3F

# ── Variables à garder ──
ADMIN_ADDRESS=0x9a94552DCB67F036af6eccc9111b749856ab8EEA
RPC_ARBITRUM_SEPOLIA=https://sepolia-rollup.arbitrum.io/rpc
ETHERSCAN_API_KEY=<ta_clé>

# ── Genesis (identiques — même rapport de valorisation) ──
GENESIS_BENEFICIARY=0x9a94552DCB67F036af6eccc9111b749856ab8EEA
PROPOSER_ADDRESS=0x9a94552DCB67F036af6eccc9111b749856ab8EEA
GENESIS_IPFS_URI=ipfs://bafybeih5jb2vk577w57uw62m4j7opyke4poryrphscydhzmd3htvm2ug7u

# ── Les nouvelles adresses TOKEN_ADDRESS et REGISTRY_ADDRESS seront ajoutées
#    après l'étape 1 (noter la sortie de la commande forge). ──
```

### KEEPER_ADDRESS (TODO avant l'étape 3)

```bash
cast wallet address --private-key $KEEPER_PRIVATE_KEY
# Ajouter dans .env : KEEPER_ADDRESS=0x<résultat>
```

---

## 1. Étape 1 — Déployer Phase 1 (nouveau token + nouveau registry)

**7 confirmations Ledger**

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

**Après le broadcast**, noter et ajouter dans `.env` :

```bash
# Sortie : "AugPocToken deployed at:   0x..."
TOKEN_ADDRESS=0x<nouvelle_adresse>
# Sortie : "RoundRegistry deployed at:  0x..."
REGISTRY_ADDRESS=0x<nouvelle_adresse>
```

**Vérification rapide :**

```bash
# Le nouveau registry doit avoir ROUND_CHALLENGER_ROLE
cast call $REGISTRY_ADDRESS "ROUND_CHALLENGER_ROLE()(bytes32)" \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → 0x... (non nul — prouve que c'est le bon code)
```

---

## 2. Étape 2 — Proposer le round genesis sur le NOUVEAU registry

**1 confirmation Ledger**

| # | Transaction |
|---|-------------|
| 8 | `registry.proposeRound(hash, [ELLADRIEL], [34 039 500 * 1e18], ipfsUri, 30)` |

```bash
source .env   # TOKEN_ADDRESS et REGISTRY_ADDRESS maintenant à jour

BROADCAST=true forge script script/ProposeGenesisRound.s.sol:ProposeGenesisRound \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger \
  --sender $PROPOSER_ADDRESS \
  --hd-paths "m/44'/60'/0'/0/0" \
  --broadcast \
  -vv
```

**Relever le `roundHash`** affiché dans la sortie — nécessaire à l'étape 2b.

---

## ⏳ Attendre 30 jours (fenêtre de challenge genesis)

La fenêtre de challenge expire 30 jours après la proposition. Aucun challenger
n'est attendu ; si un challenge est déposé, le panneau off-chain statue et, s'il est
rejeté, l'exécution se poursuit à la fin de la fenêtre.

---

## 2b. Étape 2b — Exécuter le round genesis (après 30 jours)

**1 confirmation Ledger**

| # | Transaction |
|---|-------------|
| 9 | `registry.executeRound(roundHash)` |

```bash
source .env
export ROUND_HASH=0x<le_round_hash_de_l_etape_2>
export EXECUTOR_ADDRESS=$ADMIN_ADDRESS

# Vérifier que la fenêtre est expirée (doit retourner la tx sans erreur)
BROADCAST=true forge script script/ExecuteRound.s.sol:ExecuteRound \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger \
  --sender $EXECUTOR_ADDRESS \
  --hd-paths "m/44'/60'/0'/0/0" \
  --broadcast \
  -vv
```

**Vérification :**

```bash
cast call $TOKEN_ADDRESS "balanceOf(address)(uint256)" $GENESIS_BENEFICIARY \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → 34039500000000000000000000 (= 34 039 500 tokens en wei)
```

> **Important** : l'étape 2b DOIT être exécutée **avant** l'étape 3 (Phase 2).
> En Phase 2, `ROUND_EXECUTOR_ROLE` est révoqué à l'admin — l'admin ne peut
> plus exécuter directement. C'est pourquoi la séquence est :
> propose → wait → execute → PUIS Phase 2.

---

## 3. Étape 3 — Déployer Phase 2 (MintGovernor + recâblage des rôles)

**8 confirmations Ledger**

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
export KEEPER_ADDRESS=0x<adresse_keeper>   # TODO : remplir avant de lancer

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

**Après le broadcast**, noter et ajouter dans `.env` :

```bash
GOVERNOR_ADDRESS=0x<nouvelle_adresse>
```

Mettre à jour les secrets CI et Vercel :
- GitHub Secret : `GOVERNOR_ADDRESS`
- Vercel : `NEXT_PUBLIC_GOVERNOR_ADDRESS=0x<GOVERNOR_ADDRESS>`

---

## 4. Vérification finale (Phase 2)

```bash
source .env
export GOVERNOR_ADDRESS=0x<GOVERNOR_ADDRESS>

# Script de vérification complet (11 assertions)
forge script script/VerifyDeploymentPhase2.s.sol:VerifyDeploymentPhase2 \
  --rpc-url $RPC_ARBITRUM_SEPOLIA -vv
# Attendu : "== All Phase 2 assertions passed =="

# REG-1 confirmé : admin n'a plus EXECUTOR
cast call $REGISTRY_ADDRESS "hasRole(bytes32,address)(bool)" \
  $(cast keccak "ROUND_EXECUTOR_ROLE") $ADMIN_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → false

# Governor tient bien CHALLENGER_ROLE (la raison du redéploiement)
cast call $REGISTRY_ADDRESS "hasRole(bytes32,address)(bool)" \
  $(cast keccak "ROUND_CHALLENGER_ROLE") $GOVERNOR_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → true
```

---

## 5. Récapitulatif — nombre total de confirmations Ledger

| Session | Quand | Confirmations |
|---------|-------|---------------|
| Étape 1 — Phase 1 | Maintenant | **7** |
| Étape 2 — Propose Genesis | Maintenant | **1** |
| Étape 2b — Execute Genesis | J+30 (après la fenêtre) | **1** |
| Étape 3 — Phase 2 | J+30 (après execute) | **8** |
| **Total** | | **17** |

---

## 6. Checklist pré-vol

- [ ] Anciennes adresses TOKEN/REGISTRY commentées ou retirées du `.env`
- [ ] `ETHERSCAN_API_KEY` valide dans `.env`
- [ ] `KEEPER_ADDRESS` dérivé de `KEEPER_PRIVATE_KEY` et ajouté dans `.env` (pour étape 3)
- [ ] Dry-run local confirmé : `forge test --match-contract FullStackRedeployTest -vv` → 7/7 PASS
- [ ] Ledger connecté, déverrouillé, application Ethereum ouverte
- [ ] Wallet admin a assez d'ETH testnet pour les 17 txs (estim. ~0,05 ETH)

---

## 7. Risque documenté — DEPLOY-1 (versioning déploiement ≠ code)

Ce scénario illustre un risque structurel : **un contrat déployé peut être
antérieur au code courant**. Si le code évolue après un déploiement (ajout d'un
rôle, d'une fonction), les scripts qui dépendent du nouveau code échouent contre
l'ancienne version déployée.

**Mitigation** : toujours vérifier la compatibilité entre le code courant et les
adresses déployées avant un déploiement de couche supplémentaire (Phase 2, upgrade).
La commande `cast call $REGISTRY "ROUND_CHALLENGER_ROLE()(bytes32)"` est le test
minimal à faire avant toute tentative de Phase 2.

Voir aussi `SECURITY-AUDIT-2026-06-21.md` finding `DEPLOY-1`.
