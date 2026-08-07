<!-- Version française : README.fr.md -->

# Aratea documentation

Index of the canonical documents under `docs/`. Each entry links the file
and summarises its purpose in one line. Purposes are restricted to what
the linked document itself states — no new claims are introduced here.

The Aratea project is bilingual EN/FR. Following the repository-wide
convention, the base filename is the English version and the `.fr.md`
suffix is the French mirror. Where only one language exists, the `Lang`
column says so. The French mirror of this index is at
[README.fr.md](README.fr.md).

## Product architecture

| Document | Lang | Purpose |
|---|---|---|
| [architecture.md](architecture.md) / [architecture.fr.md](architecture.fr.md) | EN/FR | Aratea vision (decentralized parametric mutual + predictive engine + DePIN data layer), three-pillar reinforcement loop, and phase plan. |
| [VISION.md](VISION.md) / [VISION.fr.md](VISION.fr.md) | EN/FR | Long-form statement of what the project is for and the order in which it intends to get there. |

## Token economics

| Document | Lang | Purpose |
|---|---|---|
| [token_model.md](token_model.md) / [token_model.fr.md](token_model.fr.md) | EN/FR | Specification of the AUG-POC token: ERC-20 on Arbitrum, NAV convention 1 sat = 1 token, labor-value accounting with no privileged contributor category. |

## Valuation

| Document | Lang | Purpose |
|---|---|---|
| [value_engine.md](value_engine.md) / [value_engine.fr.md](value_engine.fr.md) | EN/FR | Fact-only BTC valuation engine, fed exclusively by Git-visible artefacts; the operational rubric lives at [`../rounds/RUBRIC.md`](../rounds/RUBRIC.md). |

## Governance

| Document | Lang | Purpose |
|---|---|---|
| [gouvernance-auto-mint.md](gouvernance-auto-mint.md) / [gouvernance-auto-mint.fr.md](gouvernance-auto-mint.fr.md) | EN/FR | Phase 2 spec for the automatic mint and its contest path: keeper-driven rounds, token-weighted vote, sequential alternatives queue; implemented on Arbitrum Sepolia, pre-audit. |

## Security

| Document | Lang | Purpose |
|---|---|---|
| [SECURITY-audit-2026-05-11-handoff.md](SECURITY-audit-2026-05-11-handoff.md) | FR | Action handoff from the 2026-05-11 audit: what was fixed in-code and what manual rotations remain. |
| [SECURITY-rotation-procedure.md](SECURITY-rotation-procedure.md) | EN | Runbook for routine (90-day) and incident-driven credential rotations. |
| [SECURITY-rotation-log.md](SECURITY-rotation-log.md) | EN | Append-only paper trail of every secret rotation (credential names only, never values). |
| [../contracts/docs/SECURITY-AUDIT-2026-06-21.md](../contracts/docs/SECURITY-AUDIT-2026-06-21.md) | FR/EN | Internal security pass 2026-06-21: AugPocToken · RoundRegistry · MintGovernor findings, mainnet go/no-go checklist, external audit scope. |

## Contributor onboarding

| Document | Lang | Purpose |
|---|---|---|
| [contributor-starter-issues.md](contributor-starter-issues.md) | EN | Catalogue of scoped, real tasks suitable for opening as `good-first-issue` tickets. |
| [bounty-mechanism.md](bounty-mechanism.md) | EN | Placeholder describing the *future* (Phase 2) bounty mechanism — explicitly states that Aratea does **not** currently run a cash bounty program. |

## Related top-level documents

- [../README.md](../README.md) — project entry point (EN).
- [../README.fr.md](../README.fr.md) — project entry point (FR).
- [../ROADMAP.md](../ROADMAP.md) — current phases and milestones.
- [../STATUS.md](../STATUS.md) — live state of each track.
- [../CONTRIBUTING.md](../CONTRIBUTING.md) / [../CONTRIBUTING.fr.md](../CONTRIBUTING.fr.md) — contribution rules.
