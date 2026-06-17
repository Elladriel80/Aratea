# Spec — mint automatique + contestation par vote token-weighted (Phase 2)

*v0.4 — 2026-06-17. Statut : **implémenté** (contrats + tests), **testnet Arbitrum Sepolia uniquement, pré-audit**. Voir §8 pour l'implémentation réelle.*
*Décisions actées 2026-06-17 : vote **token-weighted** (1 token = 1 voix) ; **aucun plafond par wallet**. Remplace le panel ET le cap 25 % du `token_model.md` (§6, §9).*

> ⚠️ **Audit requis avant mainnet.** Du code qui mint de la valeur, piloté par un vote on-chain, est la catégorie la plus risquée. Aucun déploiement mainnet sans audit communautaire.

> Objectif : rendre le mint mensuel **automatique** (sans intervention humaine au
> quotidien), tout en laissant les détenteurs de tokens **contester** une
> allocation et imposer une répartition différente par vote token-weighted.

---

## 1. Flux nominal (personne ne conteste)

1. **J0** — l'agent de valuation calcule l'allocation (déjà automatisé, off-chain)
   et publie le `valuation_report.md` + CID IPFS.
2. **J0** — un **keeper** (signataire automatisé, pendant on-chain du cron
   predictor) appelle `proposeRound`. Démarre la fenêtre de contestation.
3. **Pendant la fenêtre** — rien si personne ne conteste.
4. **Fin de fenêtre, non contesté** — le keeper appelle `executeRound` → **mint
   automatique**. Fini.

Mint « full auto » par défaut : la signature humaine quotidienne disparaît,
remplacée par le keeper + la fenêtre de contestation.

---

## 2. Contestation → vote token-weighted (règles actées)

1. Un **détenteur de tokens** conteste pendant la fenêtre (`challengeRound`) →
   déclenche un vote.
2. Vote **token-weighted** : 1 token = 1 voix, **aucun plafond par wallet**. Le
   round contesté n'est pas exécuté tant que le vote n'est pas résolu.
3. **Rejet** si : quorum atteint **ET** > 50 % des voix exprimées votent CONTRE
   (50 % + 1 token des exprimés).
4. **Si rejeté** → cycle de **re-proposition** : une nouvelle clé de répartition
   est proposée, resoumise au vote à la majorité des voix exprimées. Accord →
   mint. Refus → on recommence.
5. **Propositions concurrentes** : plusieurs alternatives possibles, mises au vote
   **séquentiellement par date de soumission**. Dès qu'une est **acceptée**, elle
   est mintée et **toutes les autres rejetées** automatiquement.

---

## 3. Réconciliation avec `token_model.md`

| Sujet | Doc avant | Décidé | 
|---|---|---|
| Qui tranche une contestation | §6 : panel Top X, 1 personne = 1 voix | **vote token-weighted** (ACTÉ — remplace le panel) |
| Pondération | §9 : 1 token = 1 vote, cap 25 %/wallet | 1 token = 1 vote, **aucun plafond** (ACTÉ — on retire le cap) |
| Quorum | §9 : 15 % du supply circulant | **15 %** (défaut proposé) |
| Majorité | §9 : 51 % | 50 % + 1 des exprimés |

Le panel §6 est remplacé. À conserver éventuellement comme simple fallback
hors-chaîne documenté, sans rôle on-chain.

---

## 4. Architecture

- **`RoundRegistry` (déjà déployable, inchangé)** : machine à états propose /
  challenge / execute / cancel. Mint au final.
- **Keeper** (off-chain, clé chaude en secret CI) : `ROUND_PROPOSER_ROLE` +
  `ROUND_EXECUTOR_ROLE`. Propose à J0, exécute en fin de fenêtre si non contesté.
- **Contrat `Governor` (nouveau, Phase 2)** : prend la main dès qu'un round est
  contesté — tient le vote token-weighted, gère la file séquentielle des
  propositions concurrentes, n'exécute que l'allocation acceptée.
- **Snapshot anti-achat-de-vote** : le poids de vote est figé sur le **solde à
  l'instant de la proposition** (type ERC20Votes / checkpoints). **Critique** —
  sinon on emprunte/achète des tokens pour renverser un vote en cours.

Déployer token + registry maintenant **n'est pas du gâchis** : le Governor
s'ajoute par-dessus en Phase 2, sans redéployer le token.

---

## 5. Paramètres — défauts proposés (à valider ou ajuster)

| Paramètre | Défaut proposé | Note |
|---|---|---|
| Quorum | **15 %** du supply circulant | cohérent §9 ; en-dessous = round validé tel quel |
| Durée du vote / proposition | **7 jours** | aligné sur la cadence mensuelle |
| Fenêtre de contestation (rounds mensuels) | **7 jours** | genesis = 30 j (inchangé) |
| Plafond par wallet | **aucun** (ACTÉ) | plutocratie assumée : le plus gros solde pèse le plus |
| Qui peut proposer une alternative | **tout holder ≥ 1 % du supply** | évite le spam de propositions |
| « Supply circulant » | total minté − treasury | base du quorum |
| Quorum non atteint | **round validé tel quel** | = traité comme « non contesté » |
| Coupe-circuit | `CANCELLER_ROLE` gardé par JS (Ledger/Safe) | frein d'urgence hors-vote |

---

## 6. Sécurité, phasage, audit

- Scope **Phase 2 DAO** (issues #1, #49, #51, #52, #53). Pas Phase 1.
- Vote on-chain qui contrôle un mint = catégorie la plus risquée → **pas de
  mainnet sans audit communautaire** (garde-fou existant).
- Chemin : (1) spec validée → (2) Governor + tests/fuzz/invariants → (3) testnet
  Arbitrum Sepolia → (4) audit → (5) mainnet.

---

## 7. Le genesis n'a pas besoin de ce module (découplage)

Au genesis, **un seul holder** (JS) : le vote est trivial (100 % à lui). Le
premier mint ne dépend donc PAS du Governor. Deux options :

- **A** — bootstrapper le genesis maintenant (deploy + propose + execute) →
  tokens on-chain aujourd'hui ; le Governor s'ajoute après, rien de perdu.
- **B** — designer tout le module d'abord, déployer une seule fois.

---

## 8. Implémentation (2026-06-17)

### Contrats
- **`contracts/src/governance/MintGovernor.sol`** (nouveau) — porte le vote, la file
  séquentielle des propositions concurrentes, le quorum/seuils, et la finalisation
  permissionless. N'exécute que l'allocation acceptée, via le registry.
- **`contracts/src/token/AugPocToken.sol`** — étendu avec OpenZeppelin **`ERC20Votes`**
  (checkpoints), **horloge timestamp** (ERC-6372 `mode=timestamp`). Rôles/pause inchangés.
- **`contracts/src/rounds/RoundRegistry.sol`** — **une seule modif** : `challengeRound`
  est gardé par un nouveau `ROUND_CHALLENGER_ROLE` (cf. déviations). Reste la source du mint.

### Topologie des rôles (câblée par `script/DeployPhase2Governor.s.sol`)
| Rôle (registry) | Détenteur | Pouvoir |
|---|---|---|
| `DEFAULT_ADMIN_ROLE` | **Admin** (clé froide, Ledger/Safe, hors-CI) | gère les rôles |
| `ROUND_PROPOSER_ROLE` | **Keeper** (clé chaude CI) **+ Governor** | proposer un round / une alternative |
| `ROUND_EXECUTOR_ROLE` | **Governor seul** | mint (admin révoqué) |
| `ROUND_CANCELLER_ROLE` | **Admin + Governor** | coupe-circuit / annuler les alternatives battues |
| `ROUND_CHALLENGER_ROLE` | **Governor seul** | guichet unique de contestation |
| `MINTER_ROLE` (token) | **Registry seul** | inchangé (Phase 1) |

Le keeper ne détient **que** `ROUND_PROPOSER_ROLE` (proposer + finaliser le permissionless) ;
jamais de rôle qui mint hors-règles ni qui change les rôles.

### Paramètres (défauts, configurables par l'admin du Governor)
| Paramètre | Défaut | Notes |
|---|---|---|
| `quorumBps` | **1500** (15 %) | du supply circulant au snapshot ; `ceilDiv` (arrondi défavorable à l'attaquant) |
| `voteDurationDays` | **7** | un vote ne finit jamais avant la clôture de la fenêtre de contestation |
| `proposalThresholdBps` | **100** (1 %) | poids minimal pour soumettre une alternative |
| `treasury` | `address(0)` | si défini, exclu du circulant — **doit s'auto-déléguer** |

Rejet de l'original = **quorum atteint** (`exprimés ≥ quorum`) **ET** `contre > pour` (strictement
> 50 % ; entiers, sans division). Quorum non atteint → round validé tel quel. Alternative acceptée
= **majorité simple** des exprimés (`pour > contre`).

### Déviations vs design (justifiées)
1. **`challengeRound` passe en rôle-gated (`ROUND_CHALLENGER_ROLE` → Governor).** Une
   contestation doit déclencher un vote ; or un round `Challenged` n'est plus finalisable par le
   permissionless. Si n'importe qui pouvait flipper un round en `Challenged` directement, il le
   gèlerait sans vote pour le résoudre (DoS). Le Governor devient le guichet unique : son
   `challenge()` reste ouvert à tout détenteur. Tests de non-régression mis à jour.
2. **Snapshot = OpenZeppelin `ERC20Votes` (checkpoints), pas un snapshot maison.** Plus auditable.
   Conséquence : un détenteur doit **déléguer** (souvent à lui-même) pour que son solde compte
   comme poids de vote, et la treasury exclue du circulant doit s'auto-déléguer. Borne de supply
   inhérente : `2^208 − 1` (≈ 4,1e62 wei), très au-dessus de tout supply réaliste.
3. **Le Governor détient aussi `ROUND_PROPOSER_ROLE`** (en plus d'`EXECUTOR`/`CANCELLER`/`CHALLENGER`) :
   nécessaire pour enregistrer les alternatives de re-proposition dans le registry. Chaque
   alternative est enregistrée puis **auto-contestée** (`Challenged`) pour qu'elle ne soit jamais
   exécutable par la finalisation permissionless — seul le vote du Governor peut la minter.

### Keeper + CI
- Scripts Foundry : `KeeperProposeRound.s.sol` (J0) et `KeeperFinalize.s.sol` (fin de fenêtre).
- Workflow `.github/workflows/aratea-keeper.yml` : cron mensuel (finalise le round courant si non
  contesté) + `workflow_dispatch` (propose/finalise manuels). Clé keeper en **secret CI**, périmètre
  proposer/finaliser. Clé admin (déploiement/rôles) **hors-CI**.

### Tests
`forge test` (131 tests) : unitaires + **fuzz** (règle quorum/majorité, anti-achat-de-vote) +
**invariants** (le supply n'augmente que par des rounds exécutés ; le Governor n'est jamais admin ;
keeper en moindre privilège). **Slither** sans alerte `medium+`.

### Scénario end-to-end testnet
1. (Pré-requis) Phase 1 déployée : `DeployArateaPhase1` (token + registry, admin = clé froide).
2. `DeployPhase2Governor` (broadcast admin) : déploie le Governor, câble les rôles, révoque l'EXECUTOR de l'admin.
3. Renseigner les secrets/vars CI (keeper, RPC, adresses).
4. **Nominal** : keeper `proposeRound` (J0) → après la fenêtre, `finalize` (keeper ou quiconque) → mint.
5. **Contesté** : un détenteur `challenge` → vote 7 j → `resolve` : validé/maintenu → mint ; rejeté →
   `proposeAlternative` (holder ≥ 1 %) → vote → la 1re alternative acceptée est mintée, les autres annulées.
