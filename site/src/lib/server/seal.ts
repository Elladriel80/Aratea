/**
 * Scellage générique d'une donnée dans un token signé `payload.signature` avec
 * expiration absolue. Pur (aucune I/O, aucun secret en dur) → testable. Base
 * commune des cookies signés (session + transaction OAuth). Server-only.
 */

import { base64url, fromBase64url, hmacSign, hmacVerify } from "./crypto";

type Envelope<T> = { d: T; exp: number };

/** Scelle `data` avec une expiration `now + ttlMs`. */
export function sealData<T>(data: T, secret: string, ttlMs: number, now: number): string {
  const env: Envelope<T> = { d: data, exp: now + ttlMs };
  return hmacSign(base64url(JSON.stringify(env)), secret);
}

/** Ouvre un token scellé : renvoie la donnée si valide ET non expirée, sinon `null`. */
export function openData<T>(token: string, secret: string, now: number): T | null {
  const payloadB64 = hmacVerify(token, secret);
  if (!payloadB64) return null;
  try {
    const env = JSON.parse(fromBase64url(payloadB64).toString("utf8")) as Envelope<T>;
    if (typeof env?.exp !== "number" || env.exp <= now) return null;
    return env.d;
  } catch {
    return null;
  }
}
