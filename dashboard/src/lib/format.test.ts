import { describe, it, expect } from "vitest";

import { ipfsHttpUrl, isValidRoundHash } from "./format";

/**
 * Revue 2026-06-10 C1 — allowlist de schémas pour ipfsHttpUrl + gateway ipfs.io.
 * L'URI vient de données on-chain (non fiable) : tout schéma hors ipfs://|https://
 * doit retourner "" pour que l'appelant rende du texte (pas d'href -> anti-XSS).
 */
describe("ipfsHttpUrl", () => {
  it("convertit ipfs:// vers le gateway ipfs.io (plus cloudflare)", () => {
    expect(ipfsHttpUrl("ipfs://bafyCID")).toBe("https://ipfs.io/ipfs/bafyCID");
    expect(ipfsHttpUrl("ipfs://bafyCID")).not.toContain("cloudflare-ipfs.com");
  });

  it("laisse passer https:// tel quel", () => {
    expect(ipfsHttpUrl("https://example.com/x")).toBe("https://example.com/x");
  });

  it("rejette les schémas dangereux/non autorisés -> chaîne vide", () => {
    for (const bad of [
      "javascript:alert(1)",
      "data:text/html,<script>alert(1)</script>",
      "http://insecure.example",
      "vbscript:msgbox(1)",
      "  javascript:alert(1)",
      "JAVASCRIPT:alert(1)",
      "file:///etc/passwd",
      "ftp://x",
    ]) {
      expect(ipfsHttpUrl(bad)).toBe("");
    }
  });

  it("retourne '' pour une entrée vide", () => {
    expect(ipfsHttpUrl("")).toBe("");
  });
});

/**
 * Revue 2026-06-10 C3 — validation du hash de round avant tout scan on-chain.
 */
describe("isValidRoundHash", () => {
  it("accepte un hash 0x + 64 hex (casse mixte)", () => {
    expect(isValidRoundHash("0x" + "a".repeat(64))).toBe(true);
    expect(isValidRoundHash("0x" + "AbCdEf".padEnd(64, "0"))).toBe(true);
  });

  it("rejette longueur, préfixe ou caractères invalides", () => {
    expect(isValidRoundHash("0x" + "a".repeat(63))).toBe(false); // trop court
    expect(isValidRoundHash("0x" + "a".repeat(65))).toBe(false); // trop long
    expect(isValidRoundHash("a".repeat(64))).toBe(false); // pas de 0x
    expect(isValidRoundHash("0x" + "z".repeat(64))).toBe(false); // non-hex
    expect(isValidRoundHash("")).toBe(false);
    expect(isValidRoundHash("0xnotahash")).toBe(false);
  });
});
