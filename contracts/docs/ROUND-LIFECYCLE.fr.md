> [Read in English](ROUND-LIFECYCLE.md)

# Cycle de vie d'un round — contracts Aratea (Phase 1)

*Version 0.1 — 2026-05-09*

## 1. États d'un round

```
                ┌────────┐
                │  None  │  (hash non initialisé → pas d'enregistrement)
                └───┬────┘
                    │ proposeRound()
                    │ ROUND_PROPOSER_ROLE
                    ▼
                ┌──────────┐
        ┌──────▶│ Proposed │
        │       └────┬─────┘
        │            │
        │            │ challengeRound() (n'importe qui)   ┌──────────┐
        │            ├────────────────────────────────▶ │Challenged│
        │            │                                    └────┬─────┘
        │            │                                         │
        │            │                                         │ cancelRound()
        │            │                                         │ ADMIN_ROLE
        │            │                                         ▼
        │            │                                   ┌──────────┐
        │            │                                   │Cancelled │ (terminal)
        │            │                                   └──────────┘
        │            │
        │            │ block.timestamp ≥ proposedAt + challengeWindow
        │            │ ET status == Proposed
        │            │ executeRound() — ROUND_EXECUTOR_ROLE
        │            │ → mint vers les bénéficiaires (pas de cap on-chain)
        │            ▼
        │       ┌──────────┐
        └──cancelRound()──│ Executed │ (terminal)
                          └──────────┘
```

## 2. Transitions d'état

| Depuis | Fonction | Appelant | Conditions | Vers |
|---|---|---|---|---|
| `None` | `proposeRound` | `ROUND_PROPOSER_ROLE` | `roundHash` unique ; `beneficiaries.length == amounts.length` ; chaque `amount > 0` ; `challengeWindow > 0` | `Proposed` |
| `Proposed` | `challengeRound` | n'importe qui | `block.timestamp < proposedAt + challengeWindow` | `Challenged` |
| `Proposed` | `executeRound` | `ROUND_EXECUTOR_ROLE` | `block.timestamp ≥ proposedAt + challengeWindow` | `Executed` |
| `Proposed` | `cancelRound` | `ROUND_CANCELLER_ROLE` | toujours | `Cancelled` |
| `Challenged` | `cancelRound` | `ROUND_CANCELLER_ROLE` | toujours | `Cancelled` |
| `Challenged` | (aucune — le Safe doit `cancelRound` si le challenge est validé, sinon laisser la fenêtre expirer et `executeRound`) | — | — | — |
| `Executed`, `Cancelled` | (aucune — terminal) | — | — | — |

## 3. Struct Round (spec cible pour M3)

```solidity
struct Round {
    bytes32 roundHash;          // hash(beneficiaries, amounts, ipfsUri) — clé unique
    string  ipfsUri;            // pointeur IPFS vers le snapshot de /rounds/archives/<round-id>/valuation_report.md
    uint64  proposedAt;         // block.timestamp au proposeRound
    uint32  challengeWindow; // en secondes ; testnet : 300 s ; mainnet genesis : 2 592 000 s (30 j)
    RoundStatus status;
    address[] beneficiaries;
    uint256[] amounts;          // en unités de base du token (wei, 18 décimales)
}
```

`roundHash` est calculé off-chain (et vérifiable par n'importe qui) comme `keccak256(abi.encode(beneficiaries, amounts, ipfsUri))`. C'est l'identité canonique d'un round.

## 4. Events (spec cible pour M3)

```solidity
event RoundProposed(
    bytes32 indexed roundHash,
    string ipfsUri,
    uint64 proposedAt,
    uint32 challengeWindow,
    address[] beneficiaries,
    uint256[] amounts
);

event RoundChallenged(
    bytes32 indexed roundHash,
    address indexed challenger,
    string reasonIpfsUri
);

event RoundExecuted(
    bytes32 indexed roundHash,
    uint64 executedAt,
    uint256 totalMinted
);

event RoundCancelled(
    bytes32 indexed roundHash,
    address indexed canceller,
    string reasonIpfsUri
);
```

## 5. Pas de cap d'émission on-chain

`RoundRegistry` n'applique aucun cap mensuel ni cap par apporteur. Le token Aratea n'a pas vocation à être tradé sur marché secondaire, donc un cap référencé au supply pour protéger un prix est sans objet. La qualité est garantie off-chain par le rubric de valuation, le vote pondéré des holders sur toute valuation individuelle > 0,01 BTC, le cooldown nouveaux entrants, le slashing et l'audit annuel (white paper §7.7 ; statuts art. 32 et art. 31).

L'ancienne bibliothèque on-chain `MonthlyMintCap` et l'état associé (snapshot au début du mois, accumulateur des mints par mois, custom error `MonthlyCapExceeded`) ont été retirés.

## 6. Round genesis

`2026-05-genesis` (34 039 500 tokens à `@Elladriel80`) part avec `challengeWindow = 30` au lieu du 7 par défaut. La fenêtre étendue s'applique à ce seul round pour laisser le temps aux premiers prospects investisseurs d'examiner la valuation historique du travail pré-open-source de JS ; c'est la seule raison qu'elle diffère des rounds suivants.

## 7. Pont off-chain ↔ on-chain

```
/rounds/archives/<round-id>/         ──pin──▶  IPFS (Pinata)
                                                  │
                                                  │  CID = bafy...
                                                  ▼
                                          contract.proposeRound(
                                              roundHash,
                                              [beneficiaries...],
                                              [amounts...],
                                              "ipfs://bafy...",
                                              challengeWindow
                                          )
```

- L'artefact off-chain est le `valuation_report.md` (et le reste du dossier du round).
- Le hash lie ces artefacts à l'enregistrement on-chain.
- L'URI IPFS donne un pointeur de récupération stable.
- Un challenger peut recalculer le hash depuis les fichiers publiés et vérifier que l'enregistrement on-chain correspond.

## 8. Ce qui n'est intentionnellement PAS dans le cycle de vie

- **Pas de conversion automatique d'un round `Challenged` en vote panel.** Le vote a lieu off-chain ; le Safe agit sur le résultat. Cela passera on-chain en Phase 2.
- **Pas de chemin d'"appel" après `Cancelled`.** Un round cancelled est terminal. Pour le ressusciter, proposer un nouveau round avec un `roundHash` différent.
- **Pas d'exécution partielle.** Un round mint complètement à tous les bénéficiaires ou revert.
