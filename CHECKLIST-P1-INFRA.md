# Checklist P1 infra — brancher dashboard + keeper (testnet)

*Généré 2026-07-03. Valeurs vérifiées contre `contracts/.env` et les artefacts de broadcast.*
*Toutes les actions ci-dessous sont réservées à JS (saisie de secrets dans des dashboards).*

Statut amont : CI verte sur `main` (`5b7c6b1`), Phase 2 live on-chain, M5 clos. Il ne reste
que ce branchement d'infra. ~15 min au total.

---

## Bloc A — Vercel (projet dashboard)

Vercel → projet Aratea (dashboard) → **Settings → Environment Variables**.
Portée : Production (+ Preview si tu veux). Toutes en `NEXT_PUBLIC_` = publiques, aucune n'est un secret.

```
NEXT_PUBLIC_TOKEN_ADDRESS=0x0d8b96f84d3a8fe9d4b28b703c89d34c810fb6ec
NEXT_PUBLIC_REGISTRY_ADDRESS=0xbb25c0adf2fc9e0ae2dc47882f3b314e53e4570c
NEXT_PUBLIC_GOVERNOR_ADDRESS=0x3126edc0baaaac75802aea086a0cb713fa7ad598
NEXT_PUBLIC_DEPLOY_BLOCK=280209573
```

- Sans `GOVERNOR` → la page `/governance` affiche « MintGovernor not deployed ».
- `DEPLOY_BLOCK=280209573` = bloc de déploiement Phase 1 (token+registry). Facultatif mais
  recommandé : sans lui le scan d'events part de 0 et crame le quota RPC free-tier.
- `NEXT_PUBLIC_RPC_URL`, `NEXT_PUBLIC_CHAIN_ID` (421614), `NEXT_PUBLIC_EXPLORER_URL` : garder
  les défauts publics déjà dans `.env.example` sauf si tu passes sur un RPC dédié (cf. Décision 1).
- **Après ajout : redéployer** (Vercel ne réinjecte les env vars qu'au build suivant).

> Le projet **site** (landing, distinct du dashboard) lit les mêmes adresses. Si tu veux que la
> landing affiche les chiffres token en live, réplique `TOKEN`/`REGISTRY` dans son projet Vercel.
> Non bloquant pour le dashboard.

---

## Bloc B — GitHub → Settings → Secrets → Actions

Repo `Elladriel80/Aratea`. Ce sont de **vrais secrets**.

```
KEEPER_PRIVATE_KEY   → clé privée de l'EOA keeper 0xcE4900f254c6DDE560DdB76751f6882c7D418598   (cf. Décision 2)
RPC_ARBITRUM_SEPOLIA → URL RPC Arbitrum Sepolia                                                 (cf. Décision 1)
```

Rappel sécurité (déjà cadré dans l'en-tête de `aratea-keeper.yml`) : cette clé ne porte que
`ROUND_PROPOSER_ROLE`. Elle peut proposer/finaliser un round, rien d'autre — pas de mint hors règles,
pas de changement de rôle. La clé admin (froide) reste hors CI.

---

## Bloc C — GitHub → Settings → Variables → Actions

Non secrètes (adresses + hash publics).

```
ARATEA_REGISTRY_ADDRESS=0xbb25c0adf2fc9e0ae2dc47882f3b314e53e4570c
ARATEA_GOVERNOR_ADDRESS=0x3126edc0baaaac75802aea086a0cb713fa7ad598
ARATEA_ROUND_HASH=0x0f68dc33e21cd265c83d8c9842d1dd5647671a857ee6e5669119e012f6674026
```

Sans B + C, `aratea-keeper.yml` no-op proprement (garde `KEEPER_PRIVATE_KEY not set → skipping`).

---

## Décisions humaines (à trancher par toi — je ne peux pas décider à ta place)

**Décision 1 — Fournisseur RPC.**
Le public `https://sepolia-rollup.arbitrum.io/rpc` marche pour les lectures dashboard, mais pour le
keeper (broadcast de tx signées, 1×/mois) un endpoint dédié Alchemy/Infura est plus fiable
(rate-limit, pas de coupure). Recommandé : Alchemy free-tier, clé dédiée keeper.
→ La même URL peut servir Bloc A (`NEXT_PUBLIC_RPC_URL`) et Bloc B (`RPC_ARBITRUM_SEPOLIA`),
mais **attention** : celle du Bloc A finit dans le bundle browser (publique). Ne mets pas une URL
Alchemy contenant une clé sensible côté `NEXT_PUBLIC_`. Idéal : RPC public côté dashboard, RPC dédié
côté keeper.

**Décision 2 — Clé privée keeper.**
Tu es le seul à détenir la clé de `0xcE4900…`. Je ne la manipule pas. Si tu ne l'as plus sous la
main, il faut re-dériver/re-générer une EOA et lui re-`grantRole(ROUND_PROPOSER_ROLE)` sur le
registry (via l'admin Ledger).

---

## Vérification après coup

1. **Dashboard** : ouvrir `/governance` → ne doit plus afficher « not deployed » ; les figures token
   s'affichent.
2. **Keeper** : GitHub → Actions → `aratea-keeper` → *Run workflow* (dispatch) avec `action=finalize`
   sans round_hash → doit logger « nothing to finalize / skipping » proprement (preuve que les secrets
   sont lus). Le vrai cycle tourne au cron du 1er du mois 09:00 UTC.
3. Me signaler ici, je clos le P1 dans le suivi et je mets à jour `TODO-HUMAIN.md`.
