import { describe, expect, it } from "vitest";
import { en, fr } from "./i18n";

describe("homepage copy — 12 Sep 2026 truth", () => {
  it("keeps visible word spaces in hero and nav (FR + EN)", () => {
    expect(en.hero.titleA).toContain("Predict the");
    expect(en.hero.titleB).toContain("pool the");
    expect(en.hero.ctaCode).toContain("Explore the");
    expect(en.nav.mission).toContain("the mission");
    expect(fr.hero.titleA).toContain("Prédire le");
    expect(fr.hero.titleB).toContain("mutualiser le");
    expect(fr.hero.ctaCode).toContain("Explorer le");
    expect(fr.nav.mission).toContain("la mission");
  });

  it("does not pretend Phase 1 is the only track or that deploy is still pending", () => {
    expect(en.status.contractsP.toLowerCase()).not.toContain("deployment in progress");
    expect(fr.status.contractsP.toLowerCase()).not.toContain("déploiement");
    expect(fr.status.contractsP).toMatch(/avancée/i);
    expect(en.approach.intro).toMatch(/parallel/i);
    expect(fr.approach.intro).toMatch(/parallèle/i);
    expect(en.roadmap.parallel).toMatch(/parallel/i);
    expect(en.roadmapPage.phases[0].tag).toBe("proof open");
    expect(en.roadmapPage.phases[1].tag).toBe("advanced");
  });

  it("does not frame Kalshi as a money-making strategy", () => {
    expect(en.approach.p1P).toMatch(/not making money/i);
    expect(en.mission.p1).toMatch(/training ground/i);
    expect(fr.mission.p1).toMatch(/terrain d'entraînement/i);
  });
});
