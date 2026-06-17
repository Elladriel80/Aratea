"use server";

/**
 * Server actions du « compte contributeur ». Toute la vérification se fait ici,
 * côté serveur — le client ne fait que connecter le wallet et signer.
 *
 *  - requestNonce(address)   : exige une session GitHub valide ; émet un nonce
 *    à usage unique lié à la session + TTL court ; renvoie le message canonique
 *    EXACT à signer (pas de reconstruction côté client → zéro dérive).
 *  - submitRegistration(sig) : re-vérifie tout (session, nonce, signature,
 *    adresse), CONSOMME le nonce, puis ouvre une PR (ou renvoie la ligne
 *    vérifiée pour ratification manuelle si la GitHub App n'est pas configurée).
 */

import { headers } from "next/headers";

import { randomToken } from "@/lib/server/crypto";
import {
  NONCE_TTL_MS,
  REPO,
  WALLETS_PATH,
  isGithubAppConfigured,
} from "@/lib/server/config";
import { checkRateLimit } from "@/lib/server/ratelimit";
import { buildWalletsRow, openRegistrationPr } from "@/lib/server/registry";
import { readSession, writeSession, type PendingNonce } from "@/lib/server/session";
import { canonicalMessage, checkRegistration, normalizeAddress } from "@/lib/server/verify";

export type NonceState =
  | {
      status: "ok";
      login: string;
      address: string;
      nonce: string;
      date: string;
      message: string;
    }
  | { status: "error"; reason: string };

export type SubmitState =
  | { status: "ok"; prUrl: string | null; manual?: { row: string; editUrl: string } }
  | { status: "error"; reason: string };

async function clientIp(): Promise<string> {
  const h = await headers();
  return h.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
}

/** Émet un nonce de signature et renvoie le message canonique à signer. */
export async function requestNonce(addressRaw: string): Promise<NonceState> {
  const session = await readSession();
  if (!session) return { status: "error", reason: "no-session" };

  // Frein anti-abus : par session ET par IP.
  const ip = await clientIp();
  if (!checkRateLimit(`nonce:${session.login}`, 8, 60_000).ok) {
    return { status: "error", reason: "rate-limited" };
  }
  if (!checkRateLimit(`nonce-ip:${ip}`, 20, 60_000).ok) {
    return { status: "error", reason: "rate-limited" };
  }

  const address = normalizeAddress(addressRaw);
  if (!address) return { status: "error", reason: "bad-address" };

  const nonce = randomToken(24);
  const date = new Date().toISOString().slice(0, 10);
  const pending: PendingNonce = {
    nonce,
    date,
    address,
    expiresAt: Date.now() + NONCE_TTL_MS,
  };
  await writeSession({ login: session.login, pending });

  const message = canonicalMessage({ login: session.login, address, nonce, date });
  return { status: "ok", login: session.login, address, nonce, date, message };
}

/** Vérifie la signature, consomme le nonce, ouvre la PR (ou fallback manuel). */
export async function submitRegistration(input: {
  signature: string;
  website?: string;
}): Promise<SubmitState> {
  // Honeypot : seul un bot remplit ce champ caché → faux succès silencieux.
  if (input.website && input.website.trim()) {
    return { status: "ok", prUrl: null };
  }

  const session = await readSession();
  if (!session) return { status: "error", reason: "no-session" };

  const ip = await clientIp();
  if (!checkRateLimit(`submit:${session.login}`, 8, 60_000).ok) {
    return { status: "error", reason: "rate-limited" };
  }
  if (!checkRateLimit(`submit-ip:${ip}`, 20, 60_000).ok) {
    return { status: "error", reason: "rate-limited" };
  }

  const result = await checkRegistration({
    login: session.login,
    pending: session.pending,
    signature: input.signature,
    now: Date.now(),
  });

  // Usage unique : on retire le nonce de la session AVANT toute action externe.
  // Un rejeu (même signature) ne retrouvera aucun nonce actif → rejet.
  await writeSession({ login: session.login });

  if (!result.ok) return { status: "error", reason: result.reason };

  const row = buildWalletsRow({
    login: result.login,
    address: result.address,
    date: result.date,
    signature: input.signature,
  });

  // Sans GitHub App (dev local / preview) : on ne fabrique aucun droit
  // d'écriture — on renvoie la ligne vérifiée + un lien d'édition pour une
  // ratification manuelle. Le flux reste démontrable de bout en bout.
  if (!isGithubAppConfigured()) {
    const editUrl = `https://github.com/${REPO}/edit/main/${WALLETS_PATH}`;
    return { status: "ok", prUrl: null, manual: { row, editUrl } };
  }

  try {
    const { prUrl } = await openRegistrationPr({
      login: result.login,
      address: result.address,
      date: result.date,
      signature: input.signature,
      message: result.message,
    });
    return { status: "ok", prUrl };
  } catch {
    return { status: "error", reason: "pr-failed" };
  }
}
