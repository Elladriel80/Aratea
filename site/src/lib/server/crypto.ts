/**
 * Primitives crypto serveur, basées uniquement sur le module `crypto` natif de
 * Node (aucune dépendance ajoutée — plus facile à auditer). Server-only.
 */

import {
  createHmac,
  createHash,
  randomBytes,
  timingSafeEqual,
} from "node:crypto";

/** Encodage base64url (sans padding) d'un Buffer ou d'une chaîne UTF-8. */
export function base64url(input: Buffer | string): string {
  const buf = typeof input === "string" ? Buffer.from(input, "utf8") : input;
  return buf.toString("base64url");
}

/** Décodage base64url → Buffer. */
export function fromBase64url(s: string): Buffer {
  return Buffer.from(s, "base64url");
}

/** Jeton aléatoire URL-safe (par défaut 32 octets ≈ 43 caractères). */
export function randomToken(bytes = 32): string {
  return randomBytes(bytes).toString("base64url");
}

/** SHA-256 d'une chaîne, renvoyé en base64url (utilisé par PKCE S256). */
export function sha256Base64url(input: string): string {
  return createHash("sha256").update(input).digest("base64url");
}

/**
 * Signe une charge utile (`base64url(payload)`) avec HMAC-SHA256 et renvoie
 * `payload.signature`. Format stable utilisé pour tous les cookies signés.
 */
export function hmacSign(payloadB64: string, secret: string): string {
  const sig = createHmac("sha256", secret).update(payloadB64).digest("base64url");
  return `${payloadB64}.${sig}`;
}

/**
 * Vérifie un token `payload.signature` et renvoie la charge utile base64url si
 * la signature est valide, sinon `null`. Comparaison à temps constant pour ne
 * pas fuiter d'information de timing.
 */
export function hmacVerify(token: string, secret: string): string | null {
  const dot = token.lastIndexOf(".");
  if (dot <= 0) return null;
  const payloadB64 = token.slice(0, dot);
  const provided = token.slice(dot + 1);
  const expected = createHmac("sha256", secret).update(payloadB64).digest("base64url");

  const a = Buffer.from(provided);
  const b = Buffer.from(expected);
  if (a.length !== b.length) return null;
  if (!timingSafeEqual(a, b)) return null;
  return payloadB64;
}
