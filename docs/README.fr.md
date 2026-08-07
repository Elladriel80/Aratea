<!-- English version: README.md -->

# Documentation Aratea

Index des documents canoniques de `docs/`. Chaque entrée pointe vers le
fichier et en résume l'objet en une ligne. Les descriptions se limitent
strictement à ce que dit le document lui-même — aucune affirmation
nouvelle n'est introduite ici.

Le projet Aratea est bilingue FR/EN. Selon la convention du dépôt, le nom
de fichier de base est la version anglaise et le suffixe `.fr.md` désigne
le miroir français. Quand une seule langue existe, la colonne `Lang` le
précise. La version anglaise de cet index est en [README.md](README.md).

## Architecture produit

| Document | Lang | Objet |
|---|---|---|
| [architecture.fr.md](architecture.fr.md) / [architecture.md](architecture.md) | FR/EN | Vision Aratea (mutuelle paramétrique décentralisée + moteur prédictif + couche de données DePIN), boucle de renforcement entre les trois piliers, plan de phases. |
| [VISION.fr.md](VISION.fr.md) / [VISION.md](VISION.md) | FR/EN | Énoncé long de ce à quoi sert le projet et de l'ordre dans lequel il compte y arriver. |

## Économie du token

| Document | Lang | Objet |
|---|---|---|
| [token_model.fr.md](token_model.fr.md) / [token_model.md](token_model.md) | FR/EN | Spécification du token AUG-POC : ERC-20 sur Arbitrum, convention NAV 1 sat = 1 token, comptabilisation valeur-travail sans catégorie d'apporteur privilégiée. |

## Valuation

| Document | Lang | Objet |
|---|---|---|
| [value_engine.fr.md](value_engine.fr.md) / [value_engine.md](value_engine.md) | FR/EN | Moteur de valuation fact-only en BTC, alimenté uniquement par les artefacts visibles dans Git ; le rubric opérationnel vit dans [`../rounds/RUBRIC.fr.md`](../rounds/RUBRIC.fr.md). |

## Gouvernance

| Document | Lang | Objet |
|---|---|---|
| [gouvernance-auto-mint.fr.md](gouvernance-auto-mint.fr.md) / [gouvernance-auto-mint.md](gouvernance-auto-mint.md) | FR/EN | Spec Phase 2 du mint automatique et de sa voie de contestation : rounds pilotés par keeper, vote token-weighted, file séquentielle d'alternatives ; implémenté sur Arbitrum Sepolia, pré-audit. |

## Sécurité

| Document | Lang | Objet |
|---|---|---|
| [SECURITY-audit-2026-05-11-handoff.md](SECURITY-audit-2026-05-11-handoff.md) | FR | Handoff de l'audit du 2026-05-11 : ce qui a été corrigé dans le code et les rotations manuelles restantes. |
| [SECURITY-rotation-procedure.md](SECURITY-rotation-procedure.md) | EN | Runbook pour les rotations de credentials routinières (90 jours) et déclenchées sur incident. |
| [SECURITY-rotation-log.md](SECURITY-rotation-log.md) | EN | Journal append-only de chaque rotation de secret (noms de credentials uniquement, jamais les valeurs). |
| [../contracts/docs/SECURITY-AUDIT-2026-06-21.md](../contracts/docs/SECURITY-AUDIT-2026-06-21.md) | FR/EN | Passe de sécurité interne du 2026-06-21 : constats AugPocToken · RoundRegistry · MintGovernor, checklist go/no-go mainnet, périmètre de l'audit externe. |

## Onboarding contributeurs

| Document | Lang | Objet |
|---|---|---|
| [contributor-starter-issues.md](contributor-starter-issues.md) | EN | Catalogue de tâches réelles et bornées, exploitables comme tickets `good-first-issue`. |
| [bounty-mechanism.md](bounty-mechanism.md) | EN | Placeholder décrivant le mécanisme de bounty *futur* (Phase 2) — précise explicitement qu'Aratea **ne** lance actuellement **pas** de programme de bounty cash. |

## Documents racine liés

- [../README.md](../README.md) — point d'entrée projet (EN).
- [../README.fr.md](../README.fr.md) — point d'entrée projet (FR).
- [../ROADMAP.md](../ROADMAP.md) — phases courantes et jalons.
- [../STATUS.md](../STATUS.md) — état live de chaque chantier.
- [../CONTRIBUTING.md](../CONTRIBUTING.md) / [../CONTRIBUTING.fr.md](../CONTRIBUTING.fr.md) — règles de contribution.
