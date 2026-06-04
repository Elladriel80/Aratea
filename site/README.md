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
  app/         layout, globals.css, page.tsx (landing), actions.ts (server action)
  components/  Nav, WalletButton, LocaleToggle, Reveal, ContributeForm
  lib/         i18n, chain, contracts, manifest, links, format
middleware.ts  locale cookie
```

No content lives in markup: all copy comes from `src/lib/i18n.ts` (FR + EN
typed dictionaries). Edit there and both languages stay in sync.
