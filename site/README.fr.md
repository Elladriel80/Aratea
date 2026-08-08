# Aratea — site (landing)

> [Read in English](README.md)

Page d'accueil publique pour Aratea, reconstruite en tant qu'application **Next.js (App Router)** pour permettre à la page de faire des choses dynamiques réelles au lieu d'envoyer un instantané HTML figé. Même stack que `../dashboard` (Next 15 · React 19 · TypeScript · Tailwind · viem) pour que les patterns et versions restent alignés.

## Fonctionnalités dynamiques

- **Données prédictives en direct** — récupère le `predictor_manifest.json` canonique du dashboard (ISR, revalidation horaire) et rend les paris papier résolus/ouverts + P&L papier. Mettez à jour le prédicteur → la page d'accueil suit, sans modifications ici. Source : `src/lib/manifest.ts`.
- **État on-chain en direct** — lit le token `AUG-POC` (supply, état de pause) via viem + un RPC public Arbitrum Sepolia. Affiche un état « testnet en attente » tant que les adresses de contrats sont zéro. Source : `src/lib/chain.ts`, `src/lib/contracts.ts`.
- **Connexion wallet** — connexion EIP-1193 minimale (sans wagmi) : lit l'adresse, détecte le mauvais réseau et propose de passer à Arbitrum Sepolia. Prépare les futures interactions de gouvernance. Source : `src/components/WalletButton.tsx`.
- **Formulaire contributeur** — une action serveur React 19 publie sur un webhook Discord lorsque `CONTRIB_DISCORD_WEBHOOK` est défini ; sinon, elle ne fait rien gracieusement. Source : `src/app/actions.ts`, `src/components/ContributeForm.tsx`.
- **Bilingue FR/EN** — locale basée sur le cookie définie par `middleware.ts` à partir de l'en-tête geo Vercel (FR → fr) avec fallback Accept-Language ; le basculement dans la page le remplace. Pas de geo-IP tiers. Source : `src/lib/i18n.ts`.
- **Animation** — révélation au défilement, graphique animé du héros, dégradés atmosphériques, tous filtrés par `prefers-reduced-motion`.

## Exécution

```bash
npm install
npm run dev      # http://localhost:3000
```

```bash
npm run build && npm run start   # production
npm run typecheck                # tsc --noEmit
```

## Environnement

Copiez `.env.example` → `.env.local`. Tous les `NEXT_PUBLIC_*` sont exposés au navigateur ; le webhook Discord est uniquement côté serveur.

| Variable | But |
|---|---|
| `NEXT_PUBLIC_MANIFEST_URL` | Source du manifeste du prédicteur (par défaut le dashboard en direct). |
| `NEXT_PUBLIC_RPC_URL` / `NEXT_PUBLIC_CHAIN_ID` | Lectures on-chain (Arbitrum Sepolia = 421614). |
| `NEXT_PUBLIC_TOKEN_ADDRESS` / `NEXT_PUBLIC_REGISTRY_ADDRESS` | Adresses des contrats (zéro jusqu'au déploiement testnet). |
| `NEXT_PUBLIC_EXPLORER_URL` | Base de l'explorateur de blocs. |
| `CONTRIB_DISCORD_WEBHOOK` | **Uniquement serveur.** Où le formulaire contributeur publie. Vide = désactivé. |
| `GITHUB_OAUTH_CLIENT_ID` / `GITHUB_OAUTH_CLIENT_SECRET` | **Uniquement serveur.** App OAuth pour le compte contributeur (portée `read:user`). |
| `SESSION_SECRET` | **Uniquement serveur.** Secret HMAC pour signer les cookies de session + OAuth-tx. |
| `GH_APP_ID` / `GH_APP_PRIVATE_KEY` / `GH_APP_INSTALLATION_ID` | **Uniquement serveur.** GitHub App qui ouvre le PR du registre. Non défini = fallback de ratification manuelle. |
| `GH_REPO` | Registre `owner/name` (défaut `Elladriel80/Aratea`). |

## Compte contributeur — `/contribuer`

Une page self-service où un contributeur lie son **handle GitHub** à une **adresse Ethereum** de façon **prouvée et non usurpable**, puis soumet ce lien au registre (`rounds/WALLETS.md`).

### Flux

1. **Connexion avec GitHub** — OAuth 2.0 (Authorization Code + `state` + PKCE), portée `read:user` seulement. Le `login` vérifié est stocké dans un cookie de session court, signé, httpOnly.
2. **Connexion wallet** — EIP-1193, Arbitrum Sepolia (chaîne 421614).
3. **Signature** — le serveur émet un **nonce à usage unique** lié à la session (TTL 10 min) et retourne le **message canonique** ; le client le signe tel quel avec `personal_sign`.
4. **Soumission** — le serveur reverifie tout (`recoverMessageAddress` = adresse revendiquée, message canonique exact, nonce valide et lié à la session), **consomme le nonce**, et ouvre un **PR**.

Message canonique (doit rester stable — le ratificateur le reconstruit) :

```
Aratea wallet registration
GitHub: @<login>
Address: <checksummed address>
Nonce: <nonce>
Date: <YYYY-MM-DD>
```

Vérification manuelle : `cast wallet verify --address <A> "<message>" <sig>` → `true`.

### Écriture du registre — privilège minimal, ratifié

Le serveur n'a **aucun droit d'écriture direct** sur `main`. Il ouvre une PR via une **GitHub App limitée à ce dépôt**, avec exactement **`Contents: write` + `Pull requests: write`**. La PR cible une branche dédiée `registry/<login>` ; un humain (le ratificateur) reverifie la signature et **merge à la main**. Pas de merge automatique. Si l'App n'est pas configurée (dev local / aperçu), le flux renvoie la ligne vérifiée + un lien d'édition pour ratification manuelle à la place.

### Configuration

**App OAuth** (Settings → Developer settings → OAuth Apps) :
- URL de rappel d'autorisation : `<origin>/api/contributor/github/callback` (par ex. `http://localhost:3000/...` en dev).
- Copiez l'ID client/secret dans `GITHUB_OAUTH_CLIENT_ID` / `GITHUB_OAUTH_CLIENT_SECRET`.
- `SESSION_SECRET` : une longue valeur aléatoire (`openssl rand -base64 48`).

**GitHub App** (pour le chemin d'écriture PR) :
- Installez **sur ce dépôt uniquement**. Permissions du dépôt = **Contents: write** et **Pull requests: write** — rien d'autre.
- Définissez `GH_APP_ID`, `GH_APP_INSTALLATION_ID` et `GH_APP_PRIVATE_KEY` (PEM ; sur Vercel, collez avec des `\\n` littéraux entre les lignes).

Tout ce qui précède est **uniquement serveur** — jamais préfixé `NEXT_PUBLIC_`, jamais commité (`.env*.local` est dans .gitignore).

### Tests

```bash
npm run test       # vitest (signature OK/falsifiée, nonce à usage unique, handle≠session, PKCE, ligne de registre…)
npm run typecheck  # strict
```

### Modèle de menace (menace → mitigation)

- Usurpation de handle → handle vient de OAuth, jamais d'un champ tapé.
- Rejeu de signature → nonce à usage unique côté serveur + TTL + lié à la session ; le message inclut le nonce.
- CSRF OAuth → `state` (+ PKCE) vérifié ; les deux dans un cookie signé, à usage unique.
- Vol de session → cookies httpOnly/Secure/SameSite=Lax, signés (HMAC), TTL court.
- Fuite de secret → aucun secret côté client ; aucun commité ; les signatures ne sont jamais journalisées.
- Bots → limite de débit par IP + par session ; champ honeypot caché.
- Escalade → GitHub App : permissions minimales, dépôt unique, pas de merge automatique.
- Phishing → le message exact est affiché avant la signature ; message seulement, jamais une transaction.

## Déploiement (Vercel) — note de migration

Le précédent landing était un site **statique** (Vercel Root Directory `site/`, pas de commande de build). Cette version est une application Next.js, donc reconfigurez le projet Vercel `aratea` une fois :

1. Preset framework : **Next.js** (supprimez la config « no build command » / static).
2. Root Directory : `site/`.
3. Ajoutez les variables d'environnement ci-dessus dans l'interface du projet.

Chaque push vers `main` redéploie alors en Next.js. Le dashboard compagnon en lecture seule reste dans `../dashboard/` ([aratea-app.vercel.app](https://aratea-app.vercel.app/)).

## Structure

```
src/
  app/             layout, globals.css, page.tsx (landing), actions.ts (action serveur)
    contribuer/    page compte contributeur + actions.ts (requestNonce, submitRegistration)
    api/contributor/github/{login,callback}/  gestionnaires de route OAuth
  components/      Nav, WalletButton, LocaleToggle, Reveal, ContributeForm, ContributorAccount
  lib/             i18n, chain, contracts, manifest, links, format
    server/        UNIQUEMENT SERVEUR : config, crypto, seal, session, oauth, verify, registry, ratelimit (+ *.test.ts)
middleware.ts      cookie de locale
```

Tout sous `lib/server/` est uniquement serveur (Node `crypto` + viem, pas de nouvelles dépendances) et ne doit jamais être importé depuis un composant client.

Aucun contenu ne vit dans le balisage : tout le texte vient de `src/lib/i18n.ts` (dictionnaires typés FR + EN). Modifiez là et les deux langues restent synchronisées.
