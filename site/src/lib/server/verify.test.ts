import { describe, it, expect } from "vitest";
import { getAddress } from "viem";
import { privateKeyToAccount } from "viem/accounts";

import { canonicalMessage, checkRegistration, normalizeAddress } from "./verify";

/**
 * Cœur sécurité du « compte contributeur » : message canonique stable +
 * vérification de signature. On signe avec une vraie clé de test (viem), sans
 * wallet. Couvre : signature OK + falsifiée, nonce usage-unique, handle≠session.
 */

// Clé de test bien connue (compte Hardhat #0). Jamais de vraie clé ici.
const account = privateKeyToAccount(
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
);
const other = privateKeyToAccount(
  "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
);

const LOGIN = "octocat";
const NONCE = "test-nonce-123";
const DATE = "2026-06-17";
const NOW = 1_000_000;
const ADDR = getAddress(account.address);

function pending(over: Record<string, unknown> = {}) {
  return { nonce: NONCE, date: DATE, address: ADDR, expiresAt: NOW + 600_000, ...over };
}

function signFor(login: string, address: string): Promise<`0x${string}`> {
  const message = canonicalMessage({ login, address, nonce: NONCE, date: DATE });
  return account.signMessage({ message });
}

describe("canonicalMessage", () => {
  it("a un format STABLE (le ratificateur le reconstruit)", () => {
    expect(
      canonicalMessage({ login: "octocat", address: "0xABC", nonce: "n", date: "2026-06-17" }),
    ).toBe(
      "Aratea wallet registration\nGitHub: @octocat\nAddress: 0xABC\nNonce: n\nDate: 2026-06-17",
    );
  });
});

describe("normalizeAddress", () => {
  it("checksumme une adresse valide", () => {
    expect(normalizeAddress(account.address.toLowerCase())).toBe(ADDR);
  });
  it("renvoie null sur adresse invalide", () => {
    expect(normalizeAddress("0xnope")).toBeNull();
    expect(normalizeAddress("octocat")).toBeNull();
  });
});

describe("checkRegistration", () => {
  it("accepte une signature valide de l'adresse revendiquée", async () => {
    const sig = await signFor(LOGIN, ADDR);
    const res = await checkRegistration({ login: LOGIN, pending: pending(), signature: sig, now: NOW });
    expect(res.ok).toBe(true);
    if (res.ok) {
      expect(res.address).toBe(ADDR);
      expect(res.login).toBe(LOGIN);
      expect(res.nonce).toBe(NONCE);
    }
  });

  it("rejette une signature falsifiée", async () => {
    const sig = await signFor(LOGIN, ADDR);
    const tampered = (sig.slice(0, -1) + (sig.endsWith("0") ? "1" : "0")) as `0x${string}`;
    const res = await checkRegistration({ login: LOGIN, pending: pending(), signature: tampered, now: NOW });
    expect(res.ok).toBe(false);
  });

  it("garantit l'usage unique du nonce (2e usage rejeté)", async () => {
    const sig = await signFor(LOGIN, ADDR);
    const first = await checkRegistration({ login: LOGIN, pending: pending(), signature: sig, now: NOW });
    expect(first.ok).toBe(true);
    // Le serveur consomme le nonce après succès → plus de pending pour un rejeu.
    const second = await checkRegistration({ login: LOGIN, pending: undefined, signature: sig, now: NOW });
    expect(second).toEqual({ ok: false, reason: "no-nonce" });
  });

  it("rejette un nonce expiré", async () => {
    const sig = await signFor(LOGIN, ADDR);
    const res = await checkRegistration({
      login: LOGIN,
      pending: pending({ expiresAt: NOW - 1 }),
      signature: sig,
      now: NOW,
    });
    expect(res).toEqual({ ok: false, reason: "expired" });
  });

  it("rejette un handle ≠ session (login vient de la session, pas du message signé)", async () => {
    // L'attaquant signe un message portant un AUTRE handle…
    const sig = await signFor("evil-handle", ADDR);
    // …mais le serveur reconstruit avec le login de SESSION → l'adresse ne correspond plus.
    const res = await checkRegistration({ login: LOGIN, pending: pending(), signature: sig, now: NOW });
    expect(res.ok).toBe(false);
    if (!res.ok) expect(res.reason).toBe("address-mismatch");
  });

  it("rejette si la signature provient d'une autre adresse que celle revendiquée", async () => {
    const sig = await signFor(LOGIN, ADDR); // signée par `account`
    const res = await checkRegistration({
      login: LOGIN,
      pending: pending({ address: getAddress(other.address) }), // revendique `other`
      signature: sig,
      now: NOW,
    });
    expect(res.ok).toBe(false);
    if (!res.ok) expect(res.reason).toBe("address-mismatch");
  });
});
