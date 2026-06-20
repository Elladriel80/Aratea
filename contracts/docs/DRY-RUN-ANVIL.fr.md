# Dry-run — fork Anvil local (pré-vol avant testnet)

> Lance la chaîne complète Phase 1 → Phase 2 → Round genesis en local en ~30
> secondes, sans ETH réel ni Ledger. Valide les scripts, le câblage des rôles
> et la logique des contrats de bout en bout avant le vrai broadcast testnet.
>
> Voir `RUNBOOK-DEPLOIEMENT-PHASE1.fr.md` pour la procédure testnet réelle.

---

## Prérequis

- Foundry installé (`forge`, `anvil` dans `~/.foundry/bin/`).
- Lancer depuis `contracts/`.

---

## Étape 1 — Démarrer un nœud Anvil local

```bash
anvil --port 8545
```

Laisser tourner dans un terminal séparé. Comptes par défaut (pré-chargés en
10 000 ETH chacun) :

| Rôle   | Adresse                                      | Clé privée (test uniquement)                                         |
|--------|----------------------------------------------|----------------------------------------------------------------------|
| Admin  | `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266` | `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80` |
| Keeper | `0x70997970C51812dc3A010C7d01b50e0d17dc79C8` | `0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d` |

**Ne jamais utiliser ces clés ailleurs que sur un Anvil local.**

---

## Étape 2 — Déployer la Phase 1 (AugPocToken + RoundRegistry)

```bash
export ADMIN_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

forge script script/DeployArateaPhase1.s.sol:DeployArateaPhase1 \
  --rpc-url http://127.0.0.1:8545 \
  --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
  --sender $ADMIN_ADDRESS \
  --broadcast -vv
```

Relever les adresses déployées affichées par le script :

```
AugPocToken deployed at:    <TOKEN_ADDRESS>
RoundRegistry deployed at:  <REGISTRY_ADDRESS>
```

Valeurs attendues sur Anvil vierge (chaîne 31337, premier déploiement) :

- `TOKEN_ADDRESS`    = `0x5FbDB2315678afecb367f032d93F642f64180aa3`
- `REGISTRY_ADDRESS` = `0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512`

Le script vérifie lui-même le câblage des rôles. Si la dernière ligne affiche
`== Deployment complete ==`, la Phase 1 est correcte.

---

## Étape 3 — Déployer le Governor Phase 2

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

Attendu : `== Phase 2 wiring complete ==`. Adresse MintGovernor sur Anvil
vierge : `0xa513E6E4b8f2a923D98304ec87F64353C4D5C853`.

Changements de rôles appliqués par la Phase 2 :

| Rôle                 | Avant (Phase 1) | Après (Phase 2)          |
|----------------------|-----------------|--------------------------|
| ROUND_PROPOSER_ROLE  | admin           | keeper + governor        |
| ROUND_EXECUTOR_ROLE  | admin           | governor SEUL            |
| ROUND_CANCELLER_ROLE | admin           | admin + governor         |
| ROUND_CHALLENGER_ROLE| (personne)      | governor SEUL            |

---

## Étape 4 — Proposer le Round Genesis

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

Attendu : `Round proposed on-chain.` avec montant `34 039 500` tokens et
fenêtre de challenge de `30` jours.

---

## Checklist pré-vol (avant le vrai broadcast testnet)

Avant de lancer la séquence ci-dessus sur Arbitrum Sepolia, vérifier chaque point :

### Environnement
- [ ] `RPC_ARBITRUM_SEPOLIA` pointe sur un endpoint fonctionnel
- [ ] EOA admin approvisionné en ETH sur Arbitrum Sepolia (≥ 0,01 ETH suffit)
- [ ] EOA keeper approvisionné (pour ProposeGenesisRound + futures propositions)
- [ ] `ETHERSCAN_API_KEY` valide (clé unifiée Etherscan V2 couvre Arbitrum Sepolia)

### Pinata / IPFS
- [ ] `rounds/archives/2026-05-genesis/valuation_report.md` épinglé sur Pinata
- [ ] CID récupéré, `GENESIS_IPFS_URI=ipfs://<CID>/valuation_report.md` renseigné
- [ ] URI résolvable via une gateway publique

### Dry-runs des scripts (à faire AVANT le broadcast réel)
- [ ] Dry-run Anvil local réussi bout en bout (Phase 1 → Phase 2 → Genesis)
- [ ] `forge script ProposeGenesisRound ... --broadcast=false -vv` affiche le bon
      hash, le bon montant (34 039 500 tokens), la bonne fenêtre (30 jours)

### Secrets
- [ ] Aucune clé privée dans `.env` ni commitée (utiliser `--account` keystore ou Ledger)
- [ ] `.env` dans `.gitignore` et non stagé (`git status` propre)
- [ ] JWT Pinata rotaté après le déploiement Phase 1

### Vérification post-déploiement
- [ ] `forge script script/VerifyDeployment.s.sol --rpc-url arbitrum_sepolia -vv`
      passe avec les vraies adresses déployées
- [ ] Contrats vérifiés sur Etherscan (si flag `--verify` utilisé)

### Spécifique Phase 2
- [ ] L'admin a perdu `ROUND_EXECUTOR_ROLE` (plus de chemin de mint direct)
- [ ] Adresse Governor définie dans les secrets CI comme `GOVERNOR_ADDRESS`
- [ ] Clé privée keeper dans les GitHub Secrets comme `KEEPER_PK`

---

## Dry-run validé (2026-06-20)

Séquence exécutée contre Anvil chaîne 31337 :

| Étape              | Résultat |
|--------------------|----------|
| Déploiement Phase 1 | ✅ AugPocToken + RoundRegistry déployés, toutes les assertions OK |
| Déploiement Phase 2 | ✅ MintGovernor déployé, câblage des rôles vérifié |
| Proposition Genesis | ✅ 34 039 500 tokens, fenêtre 30 jours, hash du round loggé |

162 tests passent (unitaires + fuzz + invariants). Couverture : MintGovernor
91,49 % branches, RoundRegistry 100 %.
