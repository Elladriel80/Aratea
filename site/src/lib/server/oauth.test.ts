import { describe, it, expect } from "vitest";

import { buildAuthorizeUrl, pkceChallenge } from "./oauth";

/** PKCE + URL d'autorisation (scope minimal, S256). */
describe("pkceChallenge", () => {
  it("respecte le vecteur de test RFC 7636 (S256)", () => {
    // Annexe B de la RFC 7636.
    expect(pkceChallenge("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk")).toBe(
      "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM",
    );
  });
});

describe("buildAuthorizeUrl", () => {
  it("cible GitHub avec scope read:user, state, PKCE S256", () => {
    const url = buildAuthorizeUrl({
      clientId: "cid",
      redirectUri: "https://app.test/api/contributor/github/callback",
      state: "st4te",
      codeChallenge: "chall",
    });
    const u = new URL(url);
    expect(u.origin + u.pathname).toBe("https://github.com/login/oauth/authorize");
    expect(u.searchParams.get("client_id")).toBe("cid");
    expect(u.searchParams.get("redirect_uri")).toBe("https://app.test/api/contributor/github/callback");
    expect(u.searchParams.get("scope")).toBe("read:user");
    expect(u.searchParams.get("state")).toBe("st4te");
    expect(u.searchParams.get("code_challenge")).toBe("chall");
    expect(u.searchParams.get("code_challenge_method")).toBe("S256");
  });
});
