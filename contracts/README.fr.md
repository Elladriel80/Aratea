> [Read in English](README.md)

# contracts

Smart contracts Solidity du protocole Aratea. **Phase 1 en cours** — construction de la couche de règlement on-chain pour la mécanique de mint valeur-travail décrite dans [`/docs/token_model.md`](../docs/token_model.md).

## Statut

Phase 1 — *active*. Jalons M0 à M5. Voir [`/docs/architecture.md`](../docs/architecture.md) pour le phasage projet global.

## Périmètre Phase 1

Les primitives on-chain qui ratifient et exécutent les rounds mensuels déjà produits off-chain (voir [`/rounds/`](../rounds/)) :

1. **`AugPocToken`** — ERC-20 avec `ERC20Permit`, `AccessControl` et `Pausable`. 18 décimales (standard Ethereum). Pas de cap de supply fixe. Quatre rôles : `DEFAULT_ADMIN_ROLE`, `MINTER_ROLE` (RoundRegistry), `PAUSER_ROLE` (Safe), `BURNER_ROLE` (réservé au futur `AraConverter` qui exécutera la conversion `AUG-POC → ARA` au lancement DAO en Phase 2 — cf. white paper §7.2). La pause bloque uniquement les transferts d'utilisateur à utilisateur ; mint et burn restent opérationnels.
2. **`RoundRegistry`** — cycle de vie propose / challenge / execute / cancel des rounds mensuels de mint. Chaque round est ancré à son hash IPFS (le snapshot du `valuation_report.md` dans `/rounds/archives/<round-id>/`). Pas de cap d'émission on-chain — le token Aratea n'a pas vocation à être tradé, donc un cap référencé au supply pour protéger un prix est sans objet. La qualité est garantie off-chain par le rubric de valuation, le vote pondéré des holders sur toute valuation individuelle > 0,01 BTC, le cooldown nouveaux entrants, le slashing et l'audit annuel (white paper §7.7).

Hors périmètre Phase 1 (scaffoldé, pas implémenté) : token de gouvernance `ARA` + `Governor`, oracle NAV automatisé, contrats paramétriques de mutuelle, vote on-chain des Top-X holders.

## Arborescence

```
contracts/
├── src/
│   ├── token/                      # M1 — AugPocToken
│   ├── rounds/                     # M3 — RoundRegistry
│   └── interfaces/                 # IAugPocToken, IRoundRegistry
├── test/
│   ├── unit/                       # ≥ 95 % de couverture sur la logique métier
│   ├── fuzz/                       # 10 000 runs par défaut
│   └── invariant/                  # invariants supply / cap / rôles
├── script/                         # M4 — scripts de déploiement + générateurs de calldata Safe
├── docs/                           # bilingue FR/EN — architecture, sécurité, déploiement, cycle de vie
├── foundry.toml
├── slither.config.json
├── remappings.txt
├── .env.example                    # placeholders pour Arbitrum Sepolia
└── README.md / README.fr.md
```

## Stack

- **Foundry** (forge, cast, anvil) — versions stables pinées via CI.
- **Solidity 0.8.24**, EVM `paris`, optimiseur 200 runs.
- **OpenZeppelin Contracts v5.1.0** pour chaque primitive (ERC20, AccessControl, Pausable, ReentrancyGuard, SafeERC20, ERC20Permit). Aucune réimplémentation maison.
- **`forge-std` v1.9.4** pour les tests et scripts.
- **Slither 0.10.4** pour l'analyse statique (la CI échoue à partir du niveau `medium`).
- **CI** dans `.github/workflows/contracts-ci.yml` — tourne à chaque push / PR qui touche à `contracts/**`.

## Chain cible

Arbitrum Sepolia (testnet) en Phase 1. Le déploiement mainnet est **bloqué** tant qu'au moins un audit communautaire (Code4rena Arena-X, Sherlock Watson, ou peer review documentée) n'est pas réalisé.

## Build & tests

> Foundry doit être installé localement. Voir [getfoundry.sh](https://book.getfoundry.sh/getting-started/installation).

```bash
# depuis contracts/
forge install --no-commit foundry-rs/forge-std@v1.9.4 OpenZeppelin/openzeppelin-contracts@v5.1.0
forge build
forge test -vvv
forge coverage --report summary
```

La CI exécute les mêmes commandes sur chaque PR — l'install local n'est nécessaire que pour le développement.

## Modèle de sécurité (version courte)

- Tous les rôles privilégiés (`MINTER_ROLE`, `PAUSER_ROLE`, `ROUND_PROPOSER_ROLE`, `ROUND_EXECUTOR_ROLE`) sont détenus par un multisig Safe sur Arbitrum Sepolia. **Jamais une EOA.**
- Pas d'upgradeabilité au démarrage. Les bug fixes sont déployés en tant que nouveaux contracts + migration.
- Pattern Checks-Effects-Interactions strict, `ReentrancyGuard` sur toutes les surfaces de transfert externe, `SafeERC20` pour toutes les interactions ERC20.
- Tests obligatoires à trois niveaux : unit (≥ 95 % de couverture), fuzz (10 000 runs), invariants sur les propriétés critiques (`token.totalSupply()` égal à la somme des montants exécutés ; pas de mint sans fenêtre de challenge expirée ; `MINTER_ROLE` détenu uniquement par le Safe).

Threat model complet dans [`docs/SECURITY.fr.md`](docs/SECURITY.fr.md).

## Cycle de vie d'un round (Phase 1)

```
   ┌────────────────────┐
   │ Agent IA off-chain │  ───►  /rounds/archives/<round-id>/valuation_report.md
   │ produit le rapport │
   └─────────┬──────────┘
             │ founder ratifie + pin IPFS
             ▼
   ┌────────────────────┐
   │ Safe.proposeRound  │  ───►  RoundRegistry.proposeRound()
   │  (calldata)        │        émet l'event RoundProposed
   └─────────┬──────────┘
             │
             ▼
   ┌────────────────────┐         ┌─────────────────────┐
   │ Fenêtre challenge  │  ───►   │  challengeRound()    │  (n'importe qui)
   │ (7 j / 30 j genesis)│         │  → status Challenged │
   └─────────┬──────────┘         └─────────┬───────────┘
             │ fenêtre expirée + status == Proposed
             ▼                               │ Safe revoit le vote panel off-chain
   ┌────────────────────┐                    ▼
   │ Safe.executeRound  │              ┌─────────────────────┐
   │  → mint aux bens   │              │ Safe.cancelRound() │
   │  (pas de cap on-chain)│            └─────────────────────┘
   └────────────────────┘
```

Détail dans [`docs/ROUND-LIFECYCLE.fr.md`](docs/ROUND-LIFECYCLE.fr.md).

## Roadmap (jalons)

| Jalon | Périmètre | Statut |
|---|---|---|
| **M0** | Scaffold Foundry, CI, threat model, doc bilingue | ✅ fait |
| **M1** | `AugPocToken` (ERC20 + Permit + AccessControl + Pausable + 4 rôles) | ✅ fait |
| **M2** | ~~Bibliothèque `MonthlyMintCap`~~ — retirée 2026-05-17 (pas de cap on-chain, cf. §7.7) | — |
| **M3** | `RoundRegistry` (propose / challenge / execute / cancel) | ✅ fait |
| **M4** | Scripts de déploiement Arbitrum Sepolia + helpers opérationnels | ✅ fait |
| **M5** | Dashboard read-only (Next.js + viem) | en attente |

## Licence

Apache 2.0 — voir [/LICENSE](../LICENSE).
