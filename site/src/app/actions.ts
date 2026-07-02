"use server";

import { headers } from "next/headers";

import { checkRateLimit } from "@/lib/server/ratelimit";

export type ContribState = { status: "idle" | "ok" | "error"; message: string };

// Caps serveur anti-abus (revue 2026-06-10 C2). Les maxLength du formulaire sont
// client-only et contournables (curl/bot) ; on tronque côté serveur AVANT de
// construire le payload Discord.
const MAX_NAME = 80;
const MAX_SKILL = 80;
const MAX_EMAIL = 120;
const MAX_MESSAGE = 600;

const cap = (s: string, max: number): string => (s.length > max ? s.slice(0, max) : s);

/**
 * Contributor form handler. Posts to a Discord webhook when configured
 * (server-only env CONTRIB_DISCORD_WEBHOOK). With no webhook set it logs and
 * returns success, so the form stays demoable without leaking a secret.
 */
export async function submitContributor(
  _prev: ContribState,
  formData: FormData,
): Promise<ContribState> {
  // Honeypot : champ caché que seuls les bots remplissent. Non vide -> on
  // rejette SILENCIEUSEMENT (faux succès) pour ne pas révéler le filtre.
  const honeypot = String(formData.get("website") || "").trim();
  if (honeypot) return { status: "ok", message: "" };

  // Frein anti-abus par IP (revue 2026-07-02 M1) : le honeypot seul est
  // contournable par un bot qui omet le champ ; même limiteur best-effort que
  // /contribuer (fenêtre fixe en mémoire). 5 envois/min par IP suffisent
  // largement pour un humain.
  const h = await headers();
  const ip = h.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
  if (!checkRateLimit(`contrib-form:${ip}`, 5, 60_000).ok) {
    return { status: "error", message: "send" };
  }

  const name = cap(String(formData.get("name") || "").trim(), MAX_NAME);
  const skill = cap(String(formData.get("skill") || "").trim(), MAX_SKILL);
  const email = cap(String(formData.get("email") || "").trim(), MAX_EMAIL);
  const message = cap(String(formData.get("message") || "").trim(), MAX_MESSAGE);

  if (!name || !skill) return { status: "error", message: "needName" };

  const webhook = process.env.CONTRIB_DISCORD_WEBHOOK;
  const payload = {
    content: [
      "**New contributor interest**",
      `• Name: ${name}`,
      `• Skill: ${skill}`,
      `• Email: ${email || "—"}`,
      `• Message: ${message || "—"}`,
    ].join("\n"),
    // Neutralise toute mention @everyone/@here/<@user>/<@&role> injectée via les
    // champs : Discord ne notifiera personne (revue C2).
    allowed_mentions: { parse: [] as string[] },
  };

  if (!webhook) {
    console.log("[contrib] (no webhook configured)", payload.content);
    return { status: "ok", message: "" };
  }

  try {
    const res = await fetch(webhook, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
      // Ne bloque pas la server action si Discord est lent (revue 2026-07-02 F4).
      signal: AbortSignal.timeout(5_000),
    });
    if (!res.ok) return { status: "error", message: "send" };
    return { status: "ok", message: "" };
  } catch {
    return { status: "error", message: "send" };
  }
}
