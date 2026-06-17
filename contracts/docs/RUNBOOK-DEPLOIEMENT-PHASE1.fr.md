# Runbook — déploiement Phase 1 + premier mint (round genesis)

> Procédure opérateur pour le testnet **Arbitrum Sepolia**. Aucune valeur réelle
> en jeu. Le code (token + registry + scripts) est prêt et couvert par la CI
> `contracts-ci` ; ce document n'enchaîne que des commandes, il n'y a rien à coder.
>
> Le mint genesis se fait en **trois temps** : `deploy` → `propose` →
> (**fenêtre de challenge 30 jours**) → `execute`. Les jetons ne sont mintés
> qu'à l'étape `execute`, après expiration de la fenêtre.

---

## 0. Prérequis humains (à faire une fois, ~15 min)

Ces trois éléments ne peuvent pas être automatisés — ce sont des comptes externes :

1. **Pinata (IPFS)** — compte gratuit sur pinata.cloud. Épingler le fichier
   `rounds/archives/2026-05-genesis/valuation_report.md`, récupérer le CID, d'où
   l'URI `ipfs://<CID>/valuation_report.md`.
2. **ETH testnet** sur Arbitrum Sepolia, envoyé sur ton EOA admin
   (`0x9a94...8EEA`). Faucet : faucet.quicknode.com/arbitrum/sepolia, ou bridge
   depuis Sepolia via bridge.arbitrum.io. Quelques centimes suffisent (gas).
3. **Clé API Etherscan V2** (gratuite, etherscan.io) — la clé unifiée couvre
   Arbitrum Sepolia (chain id 421614), pas besoin d'une clé Arbiscan séparée.

---

## 1. Préparer l'environnement

Depuis `contracts/` :

```
cp .env.example .env
```

Remplir dans `.env` (le reste est rempli au fur et à mesure) :

- `RPC_ARBITRUM_SEPOLIA` — endpoint public par défaut OK, ou Alchemy/Infura.
- `ADMIN_ADDRESS` — ton EOA admin (reçoit DEFAULT_ADMIN_ROLE + broadcast le deploy).
- `ETHERSCAN_API_KEY` et `ARBISCAN_API_KEY` — **mets la même clé Etherscan V2 dans
  les deux** (le flag `--etherscan-api-key` lit la 1re, `foundry.toml [etherscan]`
  lit la 2de).

`forge` charge `.env` automatiquement : les variables sont lues par les scripts
(`vm.envAddress`, etc.) sans `source` manuel.

**Signataire.** Les scripts ne lisent jamais de clé privée : tu la fournis en
flag CLI. Deux options :
- Ledger : `--ledger --hd-paths "m/44'/60'/0'/0/0"`.
- EOA MetaMask : importe la clé une fois dans un keystore Foundry chiffré —
  `cast wallet import aratea-deployer --interactive` — puis utilise
  `--account aratea-deployer` (évite d'écrire la clé en clair).

**Shell.** Les commandes ci-dessous utilisent l'alias RPC `arbitrum_sepolia`
(résolu par `foundry.toml` depuis `.env`), donc aucune expansion `$VAR` n'est
nécessaire. Lance-les depuis le dossier `contracts/`.

---

## 2. Déployer le token + le registry

```
forge script script/DeployArateaPhase1.s.sol:DeployArateaPhase1 \
  --rpc-url arbitrum_sepolia \
  --account aratea-deployer \
  --sender <ADMIN_ADDRESS> \
  --broadcast --verify -vv
```

(Ledger : remplacer `--account aratea-deployer` par
`--ledger --hd-paths "m/44'/60'/0'/0/0"`.)

Le script déploie, câble les rôles (MINTER_ROLE → registry, PAUSER/PROPOSER/
EXECUTOR/CANCELLER → admin, BURNER → personne) et **vérifie le câblage**.
Relever dans la sortie :
- `AugPocToken deployed at:` → mettre dans `.env` comme `TOKEN_ADDRESS`.
- `RoundRegistry deployed at:` → mettre dans `.env` comme `REGISTRY_ADDRESS`.

Contrôle indépendant (lecture seule, pas de signer) :

```
forge script script/VerifyDeployment.s.sol --rpc-url arbitrum_sepolia -vv
```

---

## 3. Proposer le round genesis

Renseigner d'abord dans `.env` : `GENESIS_BENEFICIARY` (ton EOA),
`GENESIS_IPFS_URI` (l'URI Pinata de l'étape 0), `PROPOSER_ADDRESS` (= ton EOA).

**Dry-run d'abord** (laisse `BROADCAST=false` dans `.env`) : ça imprime le
hash du round et la calldata, sans rien envoyer. Vérifie le montant affiché :
**34 039 500 AUG-POC**, fenêtre **30 jours**.

```
forge script script/ProposeGenesisRound.s.sol:ProposeGenesisRound \
  --rpc-url arbitrum_sepolia -vv
```

Puis pour de vrai : mettre `BROADCAST=true` dans `.env` et ajouter `--broadcast`
+ le signer :

```
forge script script/ProposeGenesisRound.s.sol:ProposeGenesisRound \
  --rpc-url arbitrum_sepolia \
  --account aratea-deployer --sender <PROPOSER_ADDRESS> \
  --broadcast -vv
```

**Relever le `Round hash` imprimé** → le mettre dans `.env` comme `ROUND_HASH`.
C'est lui qui identifie le round à l'étape execute.

---

## 4. Attendre la fenêtre de challenge (30 jours)

Rien à faire. Pendant 30 jours, quiconque détecte une erreur de valorisation
peut challenger le round on-chain. Pour le genesis (solo, testnet), c'est une
formalité — mais la fenêtre est codée en dur, donc `execute` échouera tant
qu'elle n'est pas expirée (`ExecuteRound: challenge window not expired yet`).

---

## 5. Exécuter le round → premier mint

Après expiration (laisser `ROUND_HASH` et `BROADCAST=true` dans `.env`,
renseigner `EXECUTOR_ADDRESS` = ton EOA) :

```
forge script script/ExecuteRound.s.sol:ExecuteRound \
  --rpc-url arbitrum_sepolia \
  --account aratea-deployer --sender <EXECUTOR_ADDRESS> \
  --broadcast -vv
```

Cela mint **34 039 500 AUG-POC** vers le bénéficiaire. C'est le premier mining
de tokens du projet — M5 est franchi.

---

## 6. Après le mint

- Renseigner côté Vercel (projet dashboard `aratea-app`) :
  `NEXT_PUBLIC_TOKEN_ADDRESS` et `NEXT_PUBLIC_REGISTRY_ADDRESS` → la carte
  on-chain passe de « testnet à venir » aux données réelles.
- Le dashboard `/rounds` et `/round/<hash>` affichent alors le round genesis.

---

## En cas de pépin

- `challenge window not expired yet` → normal avant J+30.
- `round already exists with this hash` → le round est déjà proposé (relancer
  directement l'étape execute, pas propose).
- Annuler un round mal formé avant exécution : `script/CancelRound.s.sol`
  (rôle CANCELLER, `REASON_IPFS_URI` requis).

> Avant le vrai broadcast de l'étape 3, fais-moi voir la sortie du dry-run :
> on revérifie ensemble le hash, le montant et l'URI IPFS.
