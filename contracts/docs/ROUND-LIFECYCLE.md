> [Lire en français](ROUND-LIFECYCLE.fr.md)

# Round lifecycle — Aratea contracts (Phase 1)

*Version 0.1 — 2026-05-09*

## 1. Round states

```
                ┌────────┐
                │  None  │  (uninitialized hash → no record)
                └───┬────┘
                    │ proposeRound()
                    │ ROUND_PROPOSER_ROLE
                    ▼
                ┌──────────┐
        ┌──────▶│ Proposed │
        │       └────┬─────┘
        │            │
        │            │ challengeRound() (anyone)         ┌──────────┐
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
        │            │ block.timestamp ≥ proposedAt + challengeWindowDays
        │            │ AND status == Proposed
        │            │ executeRound() — ROUND_EXECUTOR_ROLE
        │            │ → mint to beneficiaries (no on-chain cap)
        │            ▼
        │       ┌──────────┐
        └──cancelRound()──│ Executed │ (terminal)
                          └──────────┘
```

## 2. State transitions

| From | Function | Caller | Conditions | To |
|---|---|---|---|---|
| `None` | `proposeRound` | `ROUND_PROPOSER_ROLE` | `roundHash` unique; `beneficiaries.length == amounts.length`; each `amount > 0`; `challengeWindowDays > 0` | `Proposed` |
| `Proposed` | `challengeRound` | anyone | `block.timestamp < proposedAt + challengeWindowDays * 1 days` | `Challenged` |
| `Proposed` | `executeRound` | `ROUND_EXECUTOR_ROLE` | `block.timestamp ≥ proposedAt + challengeWindowDays * 1 days` | `Executed` |
| `Proposed` | `cancelRound` | `ROUND_CANCELLER_ROLE` | always | `Cancelled` |
| `Challenged` | `cancelRound` | `ROUND_CANCELLER_ROLE` | always | `Cancelled` |
| `Challenged` | (none — Safe must `cancelRound` if challenge upheld, otherwise let window expire and `executeRound`) | — | — | — |
| `Executed`, `Cancelled` | (none — terminal) | — | — | — |

## 3. Round struct (target spec for M3)

```solidity
struct Round {
    bytes32 roundHash;          // hash(beneficiaries, amounts, ipfsUri) — unique key
    string  ipfsUri;            // IPFS pointer to /rounds/archives/<round-id>/valuation_report.md snapshot
    uint64  proposedAt;         // block.timestamp at proposeRound
    uint32  challengeWindowDays;// 7 by default; 30 for genesis (per-round override)
    RoundStatus status;
    address[] beneficiaries;
    uint256[] amounts;          // in token base units (wei, 18 decimals)
}
```

`roundHash` is computed off-chain (and verified by anyone) as `keccak256(abi.encode(beneficiaries, amounts, ipfsUri))`. It is the canonical identity of a round.

## 4. Events (target spec for M3)

```solidity
event RoundProposed(
    bytes32 indexed roundHash,
    string ipfsUri,
    uint64 proposedAt,
    uint32 challengeWindowDays,
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

## 5. No on-chain emission cap

`RoundRegistry` enforces no monthly cap and no per-contributor cap. The Aratea token is not designed to be traded on secondary markets, so a per-supply cap to protect a market price is not relevant. Quality is guaranteed off-chain by the valuation rubric, the token-weighted vote on individual valuations above 0.01 BTC, the new-entrant cooldown, the slashing mechanism, and the annual audit (white paper §7.7; statuts art. 32 and art. 31).

The earlier on-chain `MonthlyMintCap` library and its associated state (snapshot at month start, per-month minted accumulator, `MonthlyCapExceeded` custom error) have been removed.

## 6. Genesis round

`2026-05-genesis` (34 039 500 tokens to `@Elladriel80`) ships with `challengeWindowDays = 30` instead of the default 7. The extended window applies to this single round to give the first prospects investors time to review the historical valuation of JS's pre-open-source work; it is the only reason it differs from later rounds.

## 7. Off-chain ↔ on-chain bridge

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
                                              challengeWindowDays
                                          )
```

- The off-chain artefact is the `valuation_report.md` (and the rest of the round folder).
- The hash binds those artefacts to the on-chain record.
- The IPFS URI gives a stable retrieval pointer.
- A challenger can recompute the hash from the published files and verify the on-chain record matches.

## 8. What is intentionally NOT in the lifecycle

- **No automatic conversion of a `Challenged` round into a panel vote.** The vote happens off-chain; the Safe acts on the result. This will move on-chain in Phase 2.
- **No "appeal" path after `Cancelled`.** A cancelled round is terminal. To revive, propose a fresh round with a different `roundHash`.
- **No partial execution.** A round either mints fully to all beneficiaries or reverts.
