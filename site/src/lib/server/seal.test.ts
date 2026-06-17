import { describe, it, expect } from "vitest";

import { sealData, openData } from "./seal";

/** Cookies signés : round-trip, détection de falsification, expiration. */
const SECRET = "test-session-secret";

describe("sealData / openData", () => {
  it("round-trip une donnée valide non expirée", () => {
    const token = sealData({ login: "octocat", n: 1 }, SECRET, 1000, 0);
    expect(openData<{ login: string; n: number }>(token, SECRET, 500)).toEqual({ login: "octocat", n: 1 });
  });

  it("renvoie null une fois expiré", () => {
    const token = sealData({ login: "octocat" }, SECRET, 1000, 0);
    expect(openData(token, SECRET, 1000)).toBeNull(); // exp atteint
    expect(openData(token, SECRET, 5000)).toBeNull();
  });

  it("renvoie null si la signature est falsifiée", () => {
    const token = sealData({ login: "octocat" }, SECRET, 1000, 0);
    const tampered = token.slice(0, -1) + (token.endsWith("A") ? "B" : "A");
    expect(openData(tampered, SECRET, 0)).toBeNull();
  });

  it("renvoie null si le payload est falsifié", () => {
    const token = sealData({ login: "octocat" }, SECRET, 1000, 0);
    const sig = token.slice(token.lastIndexOf(".") + 1);
    expect(openData(`AAAA.${sig}`, SECRET, 0)).toBeNull();
  });

  it("renvoie null avec un mauvais secret", () => {
    const token = sealData({ login: "octocat" }, SECRET, 1000, 0);
    expect(openData(token, "wrong-secret", 0)).toBeNull();
  });
});
