# Security audit — 2026-06-21

> Internal security pass (suite du handoff 2026-05-11). Périmètre : **contrats
> Phase 1 + Phase 2** (AugPocToken · RoundRegistry · MintGovernor) + infra CI.
> This document is the audit artefact required for the external-audit scope and
> for the mainnet go/no-go gate.

---

## 1. Methodology

Static code review of the three production contracts (≈ 620 SLOC total) plus the
CI pipeline and the deployment scripts. Tests (162 passing, 100 % line coverage on
MintGovernor, 100 % on RoundRegistry) were treated as supporting evidence. Slither
was not run locally (no local Foundry/Python env); the CI pipeline adds `slither`
as a recommended follow-up (see INFRA-1 below).

Review performed against commit references at the time of the 2026-06-20 dry-run
(B21) and Phase-2 merge (B2/B20).

Severity scale: **C = Critical** (immediate fund loss) · **H = High** (fund loss
or governance capture under realistic conditions) · **M = Medium** (exploit
requires specific conditions or yields limited impact) · **I = Informational**
(best-practice improvement, no direct vulnerability).

---

## 2. Findings

### 2.1 AugPocToken

| ID | Severity | Title | Status |
|----|----------|-------|--------|
| TOK-1 | I | Pas d'émission cap on-chain | Accepted — by design |
| TOK-2 | I | Admin key = EOA acceptable testnet, DOIT être Safe mainnet | Residual risk — see §4 |
| TOK-3 | I | `BURNER_ROLE` non accordé au déploiement | ✅ Correct by design |

**TOK-1 — Pas d'émission cap on-chain**

Le contrat ne plafonne pas le total supply. Intention documentée : la qualité est
garantie hors-chaîne par le rubric + vote token-weighted + cooldown + audit annuel.
*Risque résiduel* : si la gouvernance off-chain échoue (key compromise, collusion),
des mints infinis sont techniquement possibles. Atténuation : MINTER_ROLE détenu
uniquement par RoundRegistry ; executeRound() nécessite ROUND_EXECUTOR_ROLE (Phase
2 = MintGovernor seul) ; audit annuel prévu. Accepté comme design intentionnel.

**TOK-2 — Admin key custody**

Le natspec avertit explicitement que `admin` DOIT être un Safe multisig M ≥ 2 sur
mainnet. Sur testnet, un EOA est acceptable. Ce n'est pas un bug mais une prérequis
procédural : si l'admin key EOA est compromise, toutes les permissions peuvent être
redistribuées. → Inclus dans la checklist go/no-go mainnet (§4).

**TOK-3 — BURNER_ROLE**

Non accordé au déploiement et réservé au futur contrat AraConverter (Phase 2 DAO).
Design correct : le risque de burn non autorisé est techniquement nul avant ce
déploiement.

---

### 2.2 RoundRegistry

| ID | Severity | Title | Status |
|----|----------|-------|--------|
| REG-1 | M | ROUND_EXECUTOR_ROLE ne doit plus être détenu que par le Governor (Phase 2) | Mitigated by design, to enforce at deploy |
| REG-2 | I | Pas de borne supérieure sur `beneficiaries[]` | Low risk, accepted |
| REG-3 | I | `ipfsUri` non validé on-chain | Out of threat model |

**REG-1 — ROUND_EXECUTOR_ROLE (Severity: Medium)**

`executeRound()` accepte les rounds aux statuts `Proposed` AND `Challenged`. Si
ROUND_EXECUTOR_ROLE est accordé à plusieurs adresses (EOA admin + MintGovernor),
l'EOA admin pourrait exécuter un round `Challenged` pendant qu'un vote est en cours
dans le Governor, court-circuitant le mécanisme de contestation.

*Impact* : exécution forcée d'une allocation rejetée par les holders.
*Atténuation actuelle* : le runbook de déploiement (RUNBOOK-DEPLOIEMENT-PHASE2)
prévoit de RÉVOQUER ROUND_EXECUTOR_ROLE à l'admin et de l'attribuer UNIQUEMENT au
MintGovernor. Cette procédure DOIT être suivie à la lettre au déploiement testnet et
mainnet. Le risque de l'EOA n'existe que dans la fenêtre entre la Phase 1 et la
Phase 2 (actuellement : jamais déployé en testnet).
*Recommandation* : ajouter un test de déploiement qui vérifie que
`!registry.hasRole(ROUND_EXECUTOR_ROLE, admin)` après le rewiring Phase 2.

**REG-2 — Boucle de mint illimitée**

`executeRound()` itère sur `r.beneficiaries[]` sans borne supérieure. Un round avec
1 000+ bénéficiaires pourrait OOG. En pratique, les rounds sont générés off-chain
par l'agent qui valide leur taille. Risque réel très faible. Mentionné pour mémoire.

**REG-3 — ipfsUri non validé**

L'URI IPFS est une `string` quelconque. Seul le `roundHash =
keccak256(abi.encode(beneficiaries, amounts, ipfsUri))` est vérifié. Un
ROUND_PROPOSER_ROLE malveillant pourrait mettre une URI vide ou malformée. En dehors
du modèle de menace (le proposer est le keeper de confiance). Noté pour l'audit
externe.

---

### 2.3 MintGovernor

| ID | Severity | Title | Status |
|----|----------|-------|--------|
| GOV-1 | H | Param changes (quorum, treasury) sans Timelock | Risk for mainnet |
| GOV-2 | M | Dispute bloqué si executeRound() revert | ✅ Mitigated — `forceResolveStuck()` added |
| GOV-3 | I | Double check `AlreadyDisputed` redondant | Harmless |
| GOV-4 | I | `proposeAlternative` : rollback sur duplicate altHash | Safe by design |

**GOV-1 — Param changes sans Timelock (Severity: High sur mainnet)**

`setQuorumBps`, `setProposalThresholdBps`, `setVoteDurationDays`, `setTreasury` sont
appelables immédiatement par `DEFAULT_ADMIN_ROLE`. Un admin malveillant (ou une key
compromise) peut :

- Baisser `quorumBps` à 1 bps → quorum quasi-jamais atteint → toutes les
  contestations validées automatiquement.
- Changer `treasury = address(0)` → circulating supply gonflé → quorum plus difficile.
- Passer `voteDurationDays = 1` → vote express impossible à surveiller.
- Changer ces paramètres DANS la même transaction qu'un vote pour manipuler son
  résultat.

*Impact* : governance capture par l'admin key sur mainnet.
*Atténuation actuelle* : aucune (testnet, pas d'argent réel).
*Recommandation mainnet* : déployer un `TimelockController` OpenZeppelin (delay ≥ 7
jours) et transférer `DEFAULT_ADMIN_ROLE` du Governor au Timelock. L'admin EOA
devient proposer du Timelock ; la communauté peut annuler en 7 jours.

**GOV-2 — Dispute bloqué sans mécanisme d'urgence (Severity: Medium) — ✅ FIXED**

Si `_executeWinner()` est appelé mais que `registry.executeRound(winner)` revert
(ex. : MintGovernor n'a plus ROUND_EXECUTOR_ROLE, ou un bug de registre), la
transaction revert intégralement et le dispute reste bloqué pour toujours (`resolved
= false`, pas d'`activeBallot`). Aucun chemin de sortie.

*Impact* : un dispute contesté et résolu ne peut plus être exécuté ni clos. Les
tokens ne sont pas mintés. Le round reste en attente indéfiniment.
*Fix* : `forceResolveStuck(bytes32 originalRound)` ajouté dans MintGovernor.sol
(section EMERGENCY). Marque `resolved = true`, efface `activeBallot` et marque
le ballot `Rejected` si un vote était encore ouvert. Protégé par `DEFAULT_ADMIN_ROLE`.
Émet `DisputeForceResolved`. 5 tests unitaires ajoutés (B40).

**GOV-3 — Double check AlreadyDisputed**

`challenge()` ligne ~240 : `if (_disputes[roundHash].snapshot != 0) revert
AlreadyDisputed();` est atteint uniquement si `status == Proposed` (ligne ~236 revert
avant sinon). La guard est redondante mais inoffensive — bonne défense en profondeur.

**GOV-4 — proposeAlternative : rollback sur duplicate**

Si `altHash` existe déjà (même hash de contenu), `registry.proposeRound()` revert
et toute la transaction est annulée, y compris les effets préalables sur `d.queue` et
`_ballots`. Safe par design (Checks-Effects-Interactions + revert atomique). OK.

---

### 2.4 Infrastructure CI

| ID | Severity | Title | Status |
|----|----------|-------|--------|
| INFRA-1 | I | Slither absent de la CI | ✅ Done — `static-analysis` job in contracts-ci.yml |
| INFRA-2 | ✅ | SHA pinning GitHub Actions | Done (B16) |
| INFRA-3 | ✅ | Gitleaks secret scan | Done (B19) |
| INFRA-4 | ✅ | persist-credentials:false + BOT_PAT isolé | Done (B17) |

**INFRA-1 — Slither intégré en CI ✅ DONE**

Le job `static-analysis` dans `contracts-ci.yml` exécute `crytic/slither-action@v0.4.0`
(SHA pinned) avec `slither.config.json` (filtre `lib/,test/,script/`, `fail_on: medium`).
Tourne sur chaque push/PR modifiant `contracts/**`.

---

### 2.5 Déploiement — risque de versioning

| ID | Severity | Title | Status |
|----|----------|-------|--------|
| DEPLOY-1 | M | Contrat déployé antérieur au code courant | ✅ Documenté + runbook correctif |

**DEPLOY-1 — Versioning déploiement ≠ code (Severity: Medium)**

Détecté le 2026-06-21 : le `RoundRegistry` déployé en mai 2026 sur Arbitrum Sepolia
(`0xA2324C2E467a6F38032586C1d650BBcC13F11F3F`) a été compilé à partir d'une révision
de code antérieure à l'ajout de `ROUND_CHALLENGER_ROLE`. Le code courant de
`DeployPhase2Governor` appelle `registry.ROUND_CHALLENGER_ROLE()` pour câbler le
rôle — cette fonction est absente du contrat déployé → revert systématique.

*Impact* : `DeployPhase2Governor` est inopérant contre les contrats Phase 1 existants.
Il est impossible d'activer la Phase 2 sans redéployer Phase 1.

*Mitigation* : runbook de redéploiement complet rédigé et dry-run validé
(`FullStackRedeployTest`, 7/7 assertions vertes, 2026-06-21). Tâche backlog B43.
Commande de diagnostic rapide avant toute Phase 2 :

```bash
cast call $REGISTRY "ROUND_CHALLENGER_ROLE()(bytes32)" --rpc-url $RPC_ARBITRUM_SEPOLIA
# → 0x0000000000000000000000000000000000000000000000000000000000000000
#   = ancienne version (BLOQUER Phase 2)
# → 0x<hash non nul>
#   = code courant (Phase 2 possible)
```

*Apprentissage général* : avant toute déploiement de couche (Phase 2, upgrade),
vérifier systématiquement que les fonctions requises par le script existent
sur le contrat déployé. Ajouter cette vérification dans la checklist pré-vol.

---

## 3. Éléments déjà résolus (revue 2026-06-10 + ce cycle)

| ID revue précédente | Titre | Résolu |
|--------------------|-------|--------|
| S-1 | VerifyDeployment : nom token aligné | ✅ `Augure POC Token` |
| O-1 | submitMeasurement permissionless | ✅ `onlyRole(KEEPER_ROLE)` |
| R-1 | Griefing slot unique challenge | ✅ Phase 2 `ROUND_CHALLENGER_ROLE` |
| CI/SHA | Pin SHA GitHub Actions | ✅ tous les workflows |
| BOT_PAT | persist-credentials:false | ✅ daily-trading.yml |
| C2 | Dédup gate G1 par market_ticker | ✅ backtest.py + aggregate |
| Gitleaks | Scan secrets CI | ✅ security-scan.yml (B19) |
| Couverture tests | MintGovernor + RoundRegistry | ✅ 100 % lignes (B20) |

---

## 4. Checklist Go / No-Go

### ✅ GO — Testnet (Arbitrum Sepolia)

Toutes ces conditions sont remplies :

- [x] 182+ tests passent, couverture 100 % lignes sur MintGovernor + RoundRegistry
- [x] Dry-run forge complet validé (DRY-RUN-ANVIL.md + FullStackRedeployTest 7/7)
- [x] Runbook redéploiement complet bilingue rédigé (RUNBOOK-REDEPLOIEMENT-COMPLET)
- [x] SHA pinning des Actions CI
- [x] Gitleaks CI actif
- [x] Secrets rotés (D2)
- [x] Page gouvernance UI opérationnelle (B32)

### ❌ NO-GO — Mainnet / Argent réel

Conditions non encore remplies :

- [ ] **Audit externe par un cabinet spécialisé** (Cantina, Trail of Bits, Code4rena)
      — OBLIGATOIRE avant toute migration d'argent réel
- [ ] **DEFAULT_ADMIN_ROLE transféré à un Safe multisig M ≥ 2** (TOK-2)
      sur AugPocToken ET MintGovernor
- [ ] **TimelockController** avec delay ≥ 7 jours pour les param changes du
      Governor (GOV-1)
- [x] **ROUND_EXECUTOR_ROLE** : test post-rewiring Phase 2 ajouté (REG-1 — B41 :
      `DeployArateaPhase2.t.sol::test_Phase2_AdminLosesExecutorRole`). À vérifier
      on-chain après le broadcast Ledger (B6).
- [x] **Mécanisme d'urgence** `forceResolveStuck()` ajouté au MintGovernor (GOV-2) — B40
- [x] **Slither CI** intégré et sortie propre (INFRA-1) — `contracts-ci.yml` job `static-analysis`
- [ ] **Supply cap ou garde-fous d'émission** : décision DAO documentée et
      archivée on-chain

---

## 5. Périmètre recommandé pour l'audit externe

> À utiliser comme cahier des charges dans la candidature Gitcoin DeSci (B28) et
> pour tout contact avec un auditeur.

**Contrats en périmètre (SLOC ≈ 620 hors libs) :**

| Fichier | SLOC | Points critiques |
|---------|------|-----------------|
| `src/token/AugPocToken.sol` | ~133 | Pause sémantique, clock ERC-6372, MINTER_ROLE |
| `src/rounds/RoundRegistry.sol` | ~231 | Lifecycle state machine, mint loop, CHALLENGER_ROLE |
| `src/governance/MintGovernor.sol` | ~576 | Vote-weight snapshot, quorum math, param changes, dispute queue |
| Scripts de déploiement | ~100 | Séquence de rewiring des rôles Phase 1 → Phase 2 |

**Questions prioritaires pour l'auditeur :**

1. Peut-on manipuler le quorum ou les poids de vote dans MintGovernor via vote-buying,
   flash loans, ou replay d'ancien checkpoint ?
2. Existe-t-il un chemin vers `executeRound()` qui contourne le vote quand un dispute
   est ouvert (GOV-1/REG-1 interaction) ?
3. Les param changes admin (GOV-1) peuvent-ils être exploités dans une seule
   transaction pour changer l'issue d'un vote en cours ?
4. La boucle `_activateNextPending` est-elle bornée en gaz sur la longueur `queue`
   (MAX_ALTERNATIVES = 16, invariant vérifié) ?
5. Y a-t-il des conditions où `_circulatingAt` retourne 0 et le quorum devient
   `Math.ceilDiv(0, BPS_DENOMINATOR) = 0`, rendant tout vote automatiquement valide ?

**Budget recommandé :** 10 000 – 20 000 $ (3–5 jours·ingénieur auditeur). Source
potentielle : Grant DeSci (B28, R2).

---

## 6. Slither — commandes à lancer manuellement (si Foundry installé)

```bash
cd contracts
pip install slither-analyzer crytic-compile
slither . --json slither.json --checklist --exclude-dependencies
```

Filtres connus à appliquer (`--filter-paths`) :
- `lib/forge-std`
- `lib/openzeppelin-contracts`

---

*Rédigé par l'agent orchestrateur Aratea — 2026-06-21. Passe interne, non
substituable à un audit externe indépendant.*
