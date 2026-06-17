/**
 * Cœur de la vérification : message canonique + récupération de l'adresse
 * signataire (viem). Logique pure et injectable → entièrement testable sans
 * cookies ni HTTP. Server-only (importe viem mais ne touche aucun secret).
 */

import {
  getAddress,
  isAddress,
  recoverMessageAddress,
  type Address,
  type Hex,
} from "viem";

import type { PendingNonce } from "./session";

/**
 * Message canonique signé par le contributeur. DOIT rester STABLE : le
 * ratificateur le reconstruit pour re-vérifier la signature, y compris à la
 * main avec `cast wallet verify --address <A> "<message>" <sig>`.
 *
 *   Aratea wallet registration
 *   GitHub: @<login>
 *   Address: <checksummed address>
 *   Nonce: <nonce>
 *   Date: <YYYY-MM-DD>
 */
export function canonicalMessage(p: {
  login: string;
  address: string;
  nonce: string;
  date: string;
}): string {
  return [
    "Aratea wallet registration",
    `GitHub: @${p.login}`,
    `Address: ${p.address}`,
    `Nonce: ${p.nonce}`,
    `Date: ${p.date}`,
  ].join("\n");
}

/** Valide puis checksumme une adresse fournie par le client. `null` si invalide. */
export function normalizeAddress(raw: string): Address | null {
  if (!isAddress(raw)) return null;
  return getAddress(raw);
}

/** Récupère l'adresse signataire (EIP-191 / personal_sign), checksummée. */
export async function recoverSigner(message: string, signature: Hex): Promise<Address> {
  const addr = await recoverMessageAddress({ message, signature });
  return getAddress(addr);
}

export type CheckResult =
  | {
      ok: true;
      login: string;
      address: Address;
      date: string;
      nonce: string;
      message: string;
    }
  | { ok: false; reason: "no-nonce" | "expired" | "bad-signature" | "address-mismatch" };

/**
 * Vérifie une demande d'enregistrement. TOUT doit passer :
 *  - un nonce est présent (sinon déjà consommé / jamais émis) ;
 *  - le nonce n'est pas expiré ;
 *  - le message reconstruit côté serveur (login de SESSION, jamais saisi) a bien
 *    pour signataire l'adresse revendiquée figée à l'émission du nonce.
 *
 * Le login venant exclusivement de la session, on ne peut pas enregistrer un
 * handle ≠ celui authentifié : le serveur reconstruit le message avec le login
 * de session, donc une signature portant un autre handle ne correspond plus.
 */
export async function checkRegistration(args: {
  login: string;
  pending: PendingNonce | undefined;
  signature: string;
  now: number;
}): Promise<CheckResult> {
  const { login, pending, signature, now } = args;
  if (!pending) return { ok: false, reason: "no-nonce" };
  if (pending.expiresAt <= now) return { ok: false, reason: "expired" };

  const message = canonicalMessage({
    login,
    address: pending.address,
    nonce: pending.nonce,
    date: pending.date,
  });

  let recovered: Address;
  try {
    recovered = await recoverSigner(message, signature as Hex);
  } catch {
    return { ok: false, reason: "bad-signature" };
  }

  if (recovered !== getAddress(pending.address)) {
    return { ok: false, reason: "address-mismatch" };
  }

  return { ok: true, login, address: recovered, date: pending.date, nonce: pending.nonce, message };
}
