/**
 * Cookies signés du « compte contributeur » : la session GitHub vérifiée et la
 * transaction OAuth (state/PKCE). Tous httpOnly, signés HMAC, courts.
 *
 * Pourquoi un cookie signé plutôt qu'une base de données ? Le site tourne sur
 * Vercel (serverless, sans état). Un cookie signé HMAC porte le `login` GitHub
 * vérifié + le nonce de signature en cours, sans infra ni stockage tiers, et
 * reste infalsifiable côté client (signé) et illisible par le JS (httpOnly).
 * Le nonce à usage unique est garanti en RETIRANT le nonce de la session une
 * fois consommé (cf. `actions.ts`) : un rejeu ne retrouve aucun nonce actif.
 *
 * Server-only : ne JAMAIS importer ce module depuis un composant client.
 */

import { cookies } from "next/headers";

import { sealData, openData } from "./seal";
import { OAUTH_TX_TTL_MS, SESSION_TTL_MS, sessionSecret } from "./config";
import type { OAuthTx } from "./oauth";

export const SESSION_COOKIE = "aratea-contrib-session";
export const OAUTHTX_COOKIE = "aratea-oauthtx";

/** Nonce de signature en attente, lié à la session et borné dans le temps. */
export type PendingNonce = {
  nonce: string;
  date: string; // YYYY-MM-DD figé à l'émission (évite l'ambiguïté de minuit)
  address: string; // adresse revendiquée, déjà checksummée
  expiresAt: number; // epoch ms
};

/** Contenu de la session : le login GitHub vérifié + un éventuel nonce. */
export type SessionData = {
  login: string;
  pending?: PendingNonce;
};

function cookieOptions(maxAgeMs: number) {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge: Math.floor(maxAgeMs / 1000),
  };
}

// ── Session GitHub vérifiée ────────────────────────────────────────────────

/** Écrit (ou réécrit) la session signée dans le cookie httpOnly. */
export async function writeSession(data: SessionData): Promise<void> {
  const token = sealData(data, sessionSecret(), SESSION_TTL_MS, Date.now());
  const store = await cookies();
  store.set(SESSION_COOKIE, token, cookieOptions(SESSION_TTL_MS));
}

/** Lit la session vérifiée, ou `null` si absente / invalide / expirée. */
export async function readSession(): Promise<SessionData | null> {
  const store = await cookies();
  const token = store.get(SESSION_COOKIE)?.value;
  if (!token) return null;
  return openData<SessionData>(token, sessionSecret(), Date.now());
}

/** Supprime la session (déconnexion / nettoyage). */
export async function clearSession(): Promise<void> {
  const store = await cookies();
  store.delete(SESSION_COOKIE);
}

// ── Transaction OAuth (state + PKCE), scellée le temps de l'aller-retour ─────

/** Scelle la transaction OAuth dans un cookie httpOnly court. */
export async function writeOAuthTx(tx: OAuthTx): Promise<void> {
  const token = sealData(tx, sessionSecret(), OAUTH_TX_TTL_MS, Date.now());
  const store = await cookies();
  store.set(OAUTHTX_COOKIE, token, cookieOptions(OAUTH_TX_TTL_MS));
}

/** Lit puis SUPPRIME la transaction OAuth (usage unique). */
export async function readAndClearOAuthTx(): Promise<OAuthTx | null> {
  const store = await cookies();
  const token = store.get(OAUTHTX_COOKIE)?.value;
  store.delete(OAUTHTX_COOKIE);
  if (!token) return null;
  return openData<OAuthTx>(token, sessionSecret(), Date.now());
}
