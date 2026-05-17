> [Lire en français](ARCHITECTURE.fr.md)

# Architecture — Aratea contracts (Phase 1)

*Version 0.1 — 2026-05-09*

## 1. Goal

Build the smallest possible on-chain layer that ratifies and executes the monthly labor-value mint rounds already produced off-chain in [`/rounds/`](../../rounds/). Everything that does **not** need to be on-chain stays off-chain.

## 2. What lives on-chain in Phase 1

Two primitives:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   AugPocToken          (ERC20 + AccessControl + Pausable)       │
│        ▲                                                        │
│        │ MINTER_ROLE                                            │
│        │                                                        │
│   RoundRegistry        (propose / challenge / execute / cancel) │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

- **`AugPocToken`** is a vanilla OZ ERC-20 with `AccessControl`, `Pausable`, and `ERC20Permit`. 18 decimals. No fixed `cap`. The only minter role is granted to `RoundRegistry` (so that `executeRound()` can call `token.mint(...)`).
- **`RoundRegistry`** stores `Round` structs and exposes the four lifecycle functions. It holds no funds and enforces no on-chain emission cap. The Aratea token is not designed to be traded on secondary markets, so a per-supply cap to protect a price is not relevant. Emission quality is guaranteed off-chain by the valuation rubric, the token-weighted vote on individual valuations above 0.01 BTC, the new-entrant cooldown, the slashing mechanism, and the annual audit (white paper §7.7; statuts art. 32 and art. 31).

## 3. What stays off-chain in Phase 1

- **The valuation agent** — runs monthly, reads Git artifacts, produces `valuation_report.md`.
- **The challenge process** — challenges are filed on-chain (event), but the **resolution** of a contested round (Top-X holder vote) stays off-chain in Phase 1. The Safe acts on the human result via `cancelRound` or `executeRound`.
- **The NAV calculation** — read from treasury + mark-to-market positions, computed off-chain monthly. Phase 2+ will add an oracle.
- **IPFS pinning** — `RoundRegistry` only stores the IPFS URI string. The actual file hosting is done by Pinata (or any CID-compatible service).

## 4. Trust assumptions

| Trust placed in | Why it's acceptable in Phase 1 | Plan to reduce trust |
|---|---|---|
| Safe multisig signers | Small trusted set (founder + 1-2 advisors) | Phase 2: rotate to a community-elected signer set or Governor contract. |
| Off-chain agent ratification | Founder discretion is documented in [`/rounds/RUBRIC.md`](../../rounds/RUBRIC.md); challenge window is open to anyone | Phase 2: Top-X holder vote on-chain. |
| IPFS pinning availability | Multiple pins (Pinata + IPFS public gateway + content addressed) | Multiple pinning providers; Filecoin redundancy long-term. |
| Token role wiring at deploy | Verified by deploy script + post-deploy invariant test | Phase 2: deploy via deterministic CREATE2 + reproducible build proof. |

## 5. Why Foundry

- Native fuzz + invariant testing without plugins.
- Faster compile/test loop than Hardhat.
- Standard for security-conscious solo devs and audit firms (Code4rena, Spearbit, Trail of Bits).
- `forge fmt` removes style debate and is enforced in CI.

## 6. Why Arbitrum (Sepolia in Phase 1)

- Mature L2, low fees, broad DeFi liquidity if Phase 3 mutualization pool is launched there.
- Eligible for Arbitrum Foundation grants (STIP/LTIPP) accessible to a solo dev.
- Solid tooling (Stylus optional, Nitro consensus, Arbiscan, official bridge).
- Fallback: nothing in Phase 1 makes the contracts Arbitrum-specific — same bytecode runs on Optimism, Base, or any EVM L2 if the chain decision changes later.

## 7. Why no upgradeability

- Reduces the attack surface to "deployment + roles", which is fully covered by tests + invariants.
- Avoids the proxy / implementation slot complexity that has been the source of multiple high-profile incidents (storage layout bugs, init re-entry, admin slot collisions).
- Bug fixes ship as a new deployment + a documented migration. The cost is one extra Safe transaction; the benefit is no upgrade trapdoor that an attacker could ever exploit.
- If at some milestone we conclude a contract truly must be upgradeable, the prompt requires explicit founder approval, UUPS pattern, and a `TimelockController` of at least 48 h. Phase 1 does not need it.

## 8. What the contract code does *not* do

- **Does not compute the NAV.** NAV is off-chain.
- **Does not value contributions.** That is the agent's job. The contract trusts the `(beneficiary, amount)` pairs supplied at `proposeRound`.
- **Does not cap emission.** No `MAX_MONTHLY_MINT` or `MAX_CONTRIBUTOR_SHARE` constants. Emission quality is an off-chain process gate.
- **Does not gate transfers.** `AugPocToken` is a freely transferable ERC-20. No KYC, no allowlist, no transfer fee.
- **Does not adjudicate challenges.** It records the existence of a challenge (event) and lets the Safe resolve via `cancelRound` or letting the window expire.

## 9. Pointers

- Round lifecycle in detail → [`ROUND-LIFECYCLE.md`](ROUND-LIFECYCLE.md)
- Threat model → [`SECURITY.md`](SECURITY.md)
- Deployment flow → [`DEPLOYMENT.md`](DEPLOYMENT.md)
- Token economic model → [`/docs/token_model.md`](../../docs/token_model.md)
- Project-level architecture → [`/docs/architecture.md`](../../docs/architecture.md)
