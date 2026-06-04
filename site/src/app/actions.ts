"use server";

export type ContribState = { status: "idle" | "ok" | "error"; message: string };

/**
 * Contributor form handler. Posts to a Discord webhook when configured
 * (server-only env CONTRIB_DISCORD_WEBHOOK). With no webhook set it logs and
 * returns success, so the form stays demoable without leaking a secret.
 */
export async function submitContributor(
  _prev: ContribState,
  formData: FormData,
): Promise<ContribState> {
  const name = String(formData.get("name") || "").trim();
  const skill = String(formData.get("skill") || "").trim();
  const email = String(formData.get("email") || "").trim();
  const message = String(formData.get("message") || "").trim();

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
    });
    if (!res.ok) return { status: "error", message: "send" };
    return { status: "ok", message: "" };
  } catch {
    return { status: "error", message: "send" };
  }
}
