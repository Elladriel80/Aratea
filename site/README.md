# Aratea — site (landing)

Public landing for Aratea, rebuilt as a **Next.js (App Router)** app so the page
can do real dynamic things instead of shipping a frozen HTML snapshot. Same
stack as `../dashboard` (Next 15 · React 19 · TypeScript · Tailwind · viem) so
patterns and versions stay aligned.

## Dynamic features

- **Live predictor data** — fetches the dashboard's canonical
  `predictor_manifest.json` (ISR, hourly revalidate) and renders resolved /
  open paper bets + paper P&L. Update the predictor → the landing follows, no
  edits here. Source: `src/lib/manifest.ts`.
- **Live on-chain state** — reads the `AUG-POC` token (supply, pause state) via
  viem + a public Arbitrum Sepolia RPC. Shows a "testnet pending" state while
  contract addresses are zero. Source: `src/lib/chain.ts`, `src/lib/contracts.ts`.
- **Wallet connect** — minimal EIP-1193 connect (no wagmi): reads the address,
  detects the wrong network and offers to switch to Arbitrum Sepolia. Prepares
  future governance interactions. Source: `src/components/WalletButton.tsx`.
- **Contributor form** — a React 19 server action posts to a Discord webhook
  when `CONTRIB_DISCORD_WEBHOOK` is set; otherwise it no-ops gracefully.
  Source: `src/app/actions.ts`, `src/components/ContributeForm.tsx`.
- **Bilingual FR/EN** — cookie-based locale set by `middleware.ts` from the
  Vercel geo header (FR → fr) with Accept-Language fallback; the in-page toggle
  overrides it. No third-party geo-IP. Source: `src/lib/i18n.ts`.
- **Motion** — scroll-reveal, animated hero chart, atmospheric gradients, all
  gated behind `prefers-reduced-motion`.

## Run

```bash
npm install
npm run dev      # http://localhost:3000
```

```bash
npm run build && npm run start   # production
npm run typecheck                # tsc --noEmit
```

## Environment

Copy `.env.example` → `.env.local`. All `NEXT_PUBLIC_*` are browser-exposed; the
Discord webhook is server-only.

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_MANIFEST_URL` | Predictor manifest source (defaults to the live dashboard). |
| `NEXT_PUBLIC_RPC_URL` / `NEXT_PUBLIC_CHAIN_ID` | On-chain reads (Arbitrum Sepolia = 421614). |
| `NEXT_PUBLIC_TOKEN_ADDRESS` / `NEXT_PUBLIC_REGISTRY_ADDRESS` | Contract addresses (zero until testnet deploy). |
| `NEXT_PUBLIC_EXPLORER_URL` | Block explorer base. |
| `CONTRIB_DISCORD_WEBHOOK` | **Server-only.** Where the contributor form posts. Empty = disabled. |
| `GITHUB_OAUTH_CLIENT_ID` / `GITHUB_OAUTH_CLIENT_SECRET` | **Server-only.** OAuth App for the contributor account (scope `read:user`). |
| `SESSION_SECRET` | **Server-only.** HMAC secret signing session + OAuth-tx cookies. |
| `GH_APP_ID` / `GH_APP_PRIVATE_KEY` / `GH_APP_INSTALLATION_ID` | **Server-only.** GitHub App that opens the registry PR. Unset = manual-ratification fallback. |
| `GH_REPO` | Registry repo `owner/name` (default `Elladriel80/Aratea`). |

## Contributor account — `/contribuer`

*(EN)* A self-service page where a contributor links their **GitHub handle** to
an **Ethereum address** in a **proven, non-spoofable** way, then submits that
link to the registry (`rounds/WALLETS.md`).

*(FR)* Une page self-service où un contributeur lie son **handle GitHub** à une
**adresse Ethereum** de façon **prouvée et non usurpable**, puis soumet ce lien
au registre (`rounds/WALLETS.md`).

### Flow / Flux

1. **Sign in with GitHub** — OAuth 2.0 (Authorization Code + `state` + PKCE),
   scope `read:user` only. The verified `login` is stored in a short, signed,
   httpOnly session cookie. *(OAuth GitHub ; seul le login vérifié est lu.)*
2. **Connect wallet** — EIP-1193, Arbitrum Sepolia (chain 421614).
3. **Sign** — the server issues a single-use, session-bound **nonce** (10-min
   TTL) and returns the **canonical message**; the client `personal_sign`s it
   verbatim. *(Le serveur émet un nonce à usage unique ; le client signe le
   message canonique tel quel.)*
4. **Submit** — the server re-verifies everything
   (`recoverMessageAddress` = claimed address, exact canonical message, nonce
   valid & bound to session), **consumes the nonce**, and opens a **PR**.

Canonical message (must stay stable — the ratifier reconstructs it):

```
Aratea wallet registration
GitHub: @<login>
Address: <checksummed address>
Nonce: <nonce>
Date: <YYYY-MM-DD>
```

Manual check: `cast wallet verify --address <A> "<message>" <sig>` → `true`.

### Registry write — least privilege, ratified

*(EN)* The server has **no direct write access** to `main`. It opens a PR via a
**GitHub App installed on this repo only**, with exactly **`Contents: write` +
`Pull requests: write`**. The PR targets a dedicated branch `registry/<login>`;
a human (the ratifier) re-verifies the signature and **merges manually**. No
auto-merge. If the App is not configured (local dev / preview), the flow returns
the verified row + an edit link for manual ratification instead.

*(FR)* Le serveur n'a **aucun droit d'écriture direct** sur `main` : il ouvre une
PR via une **GitHub App limitée à ce dépôt** (2 permissions), sur la branche
`registry/<login>` ; un humain re-vérifie la signature et **merge à la main**
(jamais de merge auto). Sans App configurée, le flux renvoie la ligne vérifiée +
un lien d'édition pour ratification manuelle.

### Setup

**OAuth App** (Settings → Developer settings → OAuth Apps):
- Authorization callback URL: `<origin>/api/contributor/github/callback`
  (e.g. `http://localhost:3000/...` in dev).
- Copy Client ID/secret into `GITHUB_OAUTH_CLIENT_ID` / `GITHUB_OAUTH_CLIENT_SECRET`.
- `SESSION_SECRET`: a long random value (`openssl rand -base64 48`).

**GitHub App** (for the PR write path):
- Install **on this repo only**. Repository permissions = **Contents: write**
  and **Pull requests: write** — nothing else.
- Set `GH_APP_ID`, `GH_APP_INSTALLATION_ID`, and `GH_APP_PRIVATE_KEY` (PEM; on
  Vercel paste with literal `\n` between lines).

All of the above are **server-only** — never prefixed `NEXT_PUBLIC_`, never
committed (`.env*.local` is gitignored).

### Tests

```bash
npm run test       # vitest (signature OK/falsified, single-use nonce, handle≠session, PKCE, registry row…)
npm run typecheck  # strict
```

### Threat model (menace → mitigation)

- Handle spoofing → handle comes from OAuth, never a typed field.
- Signature replay → server single-use nonce + TTL + session-bound; message includes the nonce.
- OAuth CSRF → `state` (+ PKCE) verified; both in a signed, single-use cookie.
- Session theft → cookies httpOnly/Secure/SameSite=Lax, signed (HMAC), short TTL.
- Secret leak → no secret client-side; none committed; signatures never logged.
- Bots → per-IP + per-session rate limit; hidden honeypot field.
- Escalation → GitHub App: minimum permissions, single repo, no auto-merge.
- Phishing → the exact message is shown before signing; message-only, never a transaction.

## Deploy (Vercel) — migration note

The previous landing was a **static** site (Vercel Root Directory `site/`, no
build command). This version is a Next.js app, so reconfigure the `aratea`
Vercel project once:

1. Framework preset: **Next.js** (remove the "no build command" / static config).
2. Root Directory: `site/`.
3. Add the env vars above in the project UI.

Every push to `main` then redeploys as Next.js. The companion read-only
dashboard stays in `../dashboard/` ([aratea-app.vercel.app](https://aratea-app.vercel.app/)).

## Structure

```
src/
  app/             layout, globals.css, page.tsx (landing), actions.ts (server action)
    contribuer/    contributor-account page + actions.ts (requestNonce, submitRegistration)
    api/contributor/github/{login,callback}/  OAuth route handlers
  components/      Nav, WalletButton, LocaleToggle, Reveal, ContributeForm, ContributorAccount
  lib/             i18n, chain, contracts, manifest, links, format
    server/        SERVER-ONLY: config, crypto, seal, session, oauth, verify, registry, ratelimit (+ *.test.ts)
middleware.ts      locale cookie
```

Everything under `lib/server/` is server-only (Node `crypto` + viem, no new
deps) and must never be imported from a client component.

No content lives in markup: all copy comes from `src/lib/i18n.ts` (FR + EN
typed dictionaries). Edit there and both languages stay in sync.
