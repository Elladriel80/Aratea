import { describe, it, expect } from "vitest";

import nextConfig from "./next.config.js";

/** Revue 2026-06-10 C4 — en-têtes de sécurité sur toutes les routes (dashboard). */
describe("security headers", () => {
  it("expose nosniff / referrer-policy / frame-options sur /:path*", async () => {
    const groups = await nextConfig.headers();
    const rule = groups.find((g) => g.source === "/:path*");
    expect(rule).toBeDefined();
    const byKey = Object.fromEntries(rule.headers.map((h) => [h.key, h.value]));
    expect(byKey["X-Content-Type-Options"]).toBe("nosniff");
    expect(byKey["Referrer-Policy"]).toBe("strict-origin-when-cross-origin");
    expect(byKey["X-Frame-Options"]).toBe("DENY");
    expect(byKey["Content-Security-Policy"]).toContain("frame-ancestors 'none'");
  });
});
