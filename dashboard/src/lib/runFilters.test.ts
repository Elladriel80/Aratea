import { describe, it, expect } from "vitest";

import { matchesStatusFilter, statusFilterOptions, STATUS_OPEN } from "./runFilters";

/**
 * Revue 2026-06-10 C5 — le filtre statut doit marcher quelle que soit la locale.
 * value = statut brut (open/resolved), label = libellé localisé.
 */
describe("statusFilterOptions", () => {
  it("garde des values brutes même avec des labels FR localisés", () => {
    const opts = statusFilterOptions({ open: "ouvert", resolved: "résolu" });
    expect(opts).toEqual([
      { value: "open", label: "ouvert" },
      { value: "resolved", label: "résolu" },
    ]);
    // La value n'est JAMAIS le libellé localisé (cause du bug FR).
    expect(opts.map((o) => o.value)).toEqual(["open", "resolved"]);
  });

  it("labels EN coïncident avec les values (pourquoi EN marchait déjà)", () => {
    const opts = statusFilterOptions({ open: "open", resolved: "resolved" });
    expect(opts.map((o) => o.value)).toEqual(opts.map((o) => o.label));
  });
});

describe("matchesStatusFilter", () => {
  it("matche le statut brut sur la value de la chip", () => {
    // La chip FR "ouvert" a pour value "open" -> matche bien un run open.
    const frOpenChipValue = statusFilterOptions({ open: "ouvert", resolved: "résolu" })[0].value;
    expect(frOpenChipValue).toBe(STATUS_OPEN);
    expect(matchesStatusFilter("open", [frOpenChipValue])).toBe(true);
    expect(matchesStatusFilter("resolved", [frOpenChipValue])).toBe(false);
  });

  it("démontre le bug d'origine : filtrer sur le libellé FR ne matchait rien", () => {
    expect(matchesStatusFilter("open", ["ouvert"])).toBe(false);
  });

  it("filtre vide = tout passe", () => {
    expect(matchesStatusFilter("open", [])).toBe(true);
    expect(matchesStatusFilter("resolved", [])).toBe(true);
  });
});
