# Runbook — déploiement Phase 2 (MintGovernor) sur testnet

> Procédure pour déployer le `MintGovernor` **sur Arbitrum Sepolia**, en
> s'appuyant sur les contrats Phase 1 déjà déployés (`AugPocToken` +
> `RoundRegistry`). Résultat : le mint mensuel est entièrement automatisé
> (keeper propose → fenêtre → anyone finalise → mint), avec contestation
> token-weighted si un holder challenge.
>
> **Prérequis** : Phase 1 déployée et vérifiée (voir
> `RUNBOOK-DEPLOIEMENT-PHASE1.fr.md`). Les adresses `TOKEN_ADDRESS` et
> `REGISTRY_ADDRESS` doivent être dans `.env`.

---

## 0. Avant de commencer

### Variables nécessaires dans `.env`

```
ADMIN_ADDRESS=0x9a94552DCB67F036af6eccc9111b749856ab8EEA   # clé Ledger, DEFAULT_ADMIN_ROLE
TOKEN_ADDRESS=0x56a754632f19996649E78818BcD8ee388D2871Ee    # de la Phase 1
REGISTRY_ADDRESS=0xA2324C2E467a6F38032586C1d650BBcC13F11F3F  # de la Phase 1
ETHERSCAN_API_KEY=<ta_clé>
RPC_ARBITRUM_SEPOLIA=https://sepolia-rollup.arbitrum.io/rpc
```

### KEEPER_ADDRESS (TODO humain avant le broadcast)

Le keeper est la clé chaude de CI (variable `KEEPER_PRIVATE_KEY` dans les
GitHub Secrets). Pour trouver son adresse :

```bash
cast wallet address --private-key $KEEPER_PRIVATE_KEY
```

Ajoute la ligne suivante dans `.env` avant le broadcast :

```
KEEPER_ADDRESS=0x<adresse_du_keeper>
```

> Si tu n'as pas encore généré la clé keeper, génères-en une avec
> `cast wallet new` et stocke la clé privée dans GitHub Secrets sous le nom
> `KEEPER_PRIVATE_KEY`. Le keeper n'a besoin que de `ROUND_PROPOSER_ROLE`
> (pas admin, pas de minter direct).

### Paramètres de gouvernance (optionnels — valeurs par défaut bonnes pour testnet)

```
GOVERNOR_QUORUM_BPS=1500            # 15 % de la supply circulante = quorum
GOVERNOR_PROPOSAL_THRESHOLD_BPS=100 # 1 % = seuil pour proposer une alternative
GOVERNOR_VOTE_DURATION_DAYS=7       # 7 jours de vote (fenêtre minimale)
```

---

## 1. Dry-run local (fork Anvil) — validation pré-vol

Le dry-run complet Phase 1 → Phase 2 → Genesis Round a déjà été validé
le 2026-06-20 (voir `DRY-RUN-ANVIL.md`). Pour valider spécifiquement Phase 2
avant de broadcaster, utilise le mode **simulation Foundry** (sans `--broadcast`) :

```bash
cd contracts
source .env
export KEEPER_ADDRESS=0x<ton_keeper>

# Simulation (lit l'état de la chaîne, pas de tx envoyée)
forge script script/DeployPhase2Governor.s.sol:DeployPhase2Governor \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --sender $ADMIN_ADDRESS \
  -vv
```

Le script doit terminer par `== Phase 2 wiring complete ==` sans revert.
S'il lève une erreur, le problème est dans la topologie de rôles Phase 1 —
relancer `forge script VerifyDeployment.s.sol` pour diagnostiquer.

---

## 2. Broadcast Phase 2 — commande exacte Ledger

```bash
cd contracts
source .env
export KEEPER_ADDRESS=0x<adresse_du_keeper>   # TODO: remplir avant de lancer

forge script script/DeployPhase2Governor.s.sol:DeployPhase2Governor \
  --rpc-url $RPC_ARBITRUM_SEPOLIA \
  --ledger \
  --sender $ADMIN_ADDRESS \
  --hd-paths "m/44'/60'/0'/0/0" \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  -vv
```

**Nombre de confirmations Ledger attendues : jusqu'à 8**

| # | Transaction | Rôle |
|---|-------------|------|
| 1 | `new MintGovernor(...)` | déploie le gouverneur |
| 2 | `grantRole(ROUND_PROPOSER_ROLE, keeper)` | keeper peut proposer |
| 3 | `grantRole(ROUND_PROPOSER_ROLE, governor)` | governor peut re-proposer des alternatives |
| 4 | `grantRole(ROUND_EXECUTOR_ROLE, governor)` | seul le governor peut minter |
| 5 | `grantRole(ROUND_CANCELLER_ROLE, governor)` | governor peut annuler les alternatives supercédées |
| 6 | `grantRole(ROUND_CHALLENGER_ROLE, governor)` | porte d'entrée unique pour les challenges |
| 7 | `revokeRole(ROUND_EXECUTOR_ROLE, admin)` | supprime le chemin mint direct de l'admin |
| 8 | `revokeRole(ROUND_PROPOSER_ROLE, admin)` | l'admin ne propose plus directement |

Le script vérifie le câblage en interne (fonction `_assertWiring`) — il reverte
si l'une des assertions échoue.

**Topologie des rôles après Phase 2**

| Rôle | Phase 1 | Phase 2 |
|------|---------|---------|
| DEFAULT_ADMIN_ROLE | admin | admin (inchangé) |
| ROUND_PROPOSER_ROLE | admin | keeper + governor |
| ROUND_EXECUTOR_ROLE | admin | **governor UNIQUEMENT** |
| ROUND_CANCELLER_ROLE | admin | admin + governor |
| ROUND_CHALLENGER_ROLE | — | **governor UNIQUEMENT** |
| MINTER_ROLE (token) | registry | registry (inchangé) |

---

## 3. Après le broadcast

### 3.1 Relever l'adresse du MintGovernor

La sortie du script affiche :

```
MintGovernor deployed at: 0x<GOVERNOR_ADDRESS>
```

Ajoute dans `.env` :

```
GOVERNOR_ADDRESS=0x<GOVERNOR_ADDRESS>
```

Et mets à jour les secrets CI et les variables d'environnement Vercel :

- GitHub Secrets : `GOVERNOR_ADDRESS`
- Vercel (dashboard) : `NEXT_PUBLIC_GOVERNOR_ADDRESS=0x<GOVERNOR_ADDRESS>`

### 3.2 Vérification indépendante

```bash
# Vérifie que le governor a bien les 4 rôles opérationnels
cast call $REGISTRY_ADDRESS "hasRole(bytes32,address)(bool)" \
  $(cast keccak "ROUND_PROPOSER_ROLE") $GOVERNOR_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → true

cast call $REGISTRY_ADDRESS "hasRole(bytes32,address)(bool)" \
  $(cast keccak "ROUND_EXECUTOR_ROLE") $ADMIN_ADDRESS \
  --rpc-url $RPC_ARBITRUM_SEPOLIA
# → false  (l'admin n'a PLUS l'executor après Phase 2)
```

### 3.3 Configurer le keeper en CI

Dans `.github/workflows/aratea-keeper.yml`, la variable `GOVERNOR_ADDRESS`
doit être passée aux scripts keeper (KeeperProposeRound + KeeperFinalize) :

```yaml
env:
  GOVERNOR_ADDRESS: ${{ secrets.GOVERNOR_ADDRESS }}
  REGISTRY_ADDRESS: ${{ secrets.REGISTRY_ADDRESS }}
  TOKEN_ADDRESS: ${{ secrets.TOKEN_ADDRESS }}
```

---

## 4. Checklist pré-vol

- [ ] `KEEPER_ADDRESS` dérivé de `KEEPER_PRIVATE_KEY` et ajouté dans `.env`
- [ ] `TOKEN_ADDRESS` et `REGISTRY_ADDRESS` Phase 1 vérifiés dans `.env`
- [ ] Simulation dry-run (étape 1) passe sans revert
- [ ] Ledger connecté, déverrouillé, application Ethereum ouverte
- [ ] Arbiscan API key valide (`ETHERSCAN_API_KEY` dans `.env`)
- [ ] Wallet admin (`ADMIN_ADDRESS`) a assez d'ETH testnet pour les 8 txs

---

## 5. Flux opérationnel post-Phase 2

Une fois le MintGovernor déployé, le cycle mensuel automatisé fonctionne
sans intervention humaine :

```
[J0]  Keeper → KeeperProposeRound.s.sol → round proposé, fenêtre 7 jours
[J7+] Anyone → governor.finalize(roundHash) → mint automatique (si non challengé)

Chemin contesté :
  Token holder → governor.challenge(roundHash, reasonIpfsUri)
  → vote ouvert 7 jours (poids gelés au snapshot de la proposition)
  → Anyone → governor.resolve(ballotRound) → mint si maintenu, sinon re-proposition
```

Voir `docs/ROUND-LIFECYCLE.md` pour le cycle de vie complet.
