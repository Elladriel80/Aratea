import { describe, it, expect, beforeEach } from "vitest";

import { checkRateLimit, resetRateLimits } from "./ratelimit";

describe("checkRateLimit (fenêtre fixe)", () => {
  beforeEach(resetRateLimits);

  it("laisse passer jusqu'à la limite puis bloque dans la fenêtre", () => {
    expect(checkRateLimit("k", 2, 1000, 0).ok).toBe(true);
    expect(checkRateLimit("k", 2, 1000, 0).ok).toBe(true);
    expect(checkRateLimit("k", 2, 1000, 0).ok).toBe(false);
  });

  it("réinitialise après la fenêtre", () => {
    expect(checkRateLimit("k2", 1, 1000, 0).ok).toBe(true);
    expect(checkRateLimit("k2", 1, 1000, 500).ok).toBe(false);
    expect(checkRateLimit("k2", 1, 1000, 1001).ok).toBe(true);
  });

  it("isole les clés (IP vs session)", () => {
    expect(checkRateLimit("a", 1, 1000, 0).ok).toBe(true);
    expect(checkRateLimit("b", 1, 1000, 0).ok).toBe(true);
    expect(checkRateLimit("a", 1, 1000, 0).ok).toBe(false);
  });
});
