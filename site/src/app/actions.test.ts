import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

import { submitContributor, type ContribState } from "./actions";

/**
 * Revue 2026-06-10 C2 — durcissement du formulaire contributeur côté serveur :
 * troncature (name/skill <= 80, message <= 600), allowed_mentions: {parse: []},
 * honeypot caché rejeté silencieusement.
 */

const IDLE: ContribState = { status: "idle", message: "" };
const WEBHOOK = "https://discord.test/webhook";

function fd(fields: Record<string, string>): FormData {
  const f = new FormData();
  for (const [k, v] of Object.entries(fields)) f.set(k, v);
  return f;
}

let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  process.env.CONTRIB_DISCORD_WEBHOOK = WEBHOOK;
  fetchMock = vi.fn(async () => new Response(null, { status: 204 }));
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
  delete process.env.CONTRIB_DISCORD_WEBHOOK;
});

function lastPayload() {
  expect(fetchMock).toHaveBeenCalledTimes(1);
  const [, init] = fetchMock.mock.calls[0];
  return JSON.parse((init as RequestInit).body as string);
}

describe("submitContributor", () => {
  it("tronque name/skill à 80 et message à 600 côté serveur", async () => {
    const res = await submitContributor(IDLE, fd({
      name: "n".repeat(200),
      skill: "s".repeat(200),
      email: "a@b.co",
      message: "m".repeat(2000),
    }));
    expect(res.status).toBe("ok");

    const payload = lastPayload();
    expect(payload.content).toContain(`Name: ${"n".repeat(80)}\n`);
    expect(payload.content).not.toContain("n".repeat(81));
    expect(payload.content).toContain(`Skill: ${"s".repeat(80)}`);
    expect(payload.content).not.toContain("s".repeat(81));
    expect(payload.content).toContain("m".repeat(600));
    expect(payload.content).not.toContain("m".repeat(601));
  });

  it("ajoute allowed_mentions: { parse: [] } au payload Discord", async () => {
    await submitContributor(IDLE, fd({ name: "Alice", skill: "Solidity" }));
    const payload = lastPayload();
    expect(payload.allowed_mentions).toEqual({ parse: [] });
  });

  it("rejette silencieusement quand le honeypot est rempli (faux succès, pas d'envoi)", async () => {
    const res = await submitContributor(IDLE, fd({
      name: "Bot",
      skill: "spam",
      website: "http://spam.example", // honeypot
    }));
    expect(res.status).toBe("ok");
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("exige name et skill (erreur sinon)", async () => {
    const res = await submitContributor(IDLE, fd({ name: "", skill: "" }));
    expect(res.status).toBe("error");
    expect(res.message).toBe("needName");
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
