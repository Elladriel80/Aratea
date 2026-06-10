"use client";

import { useActionState } from "react";
import { submitContributor, type ContribState } from "@/app/actions";
import type { Dictionary } from "@/lib/i18n";

const initial: ContribState = { status: "idle", message: "" };

export default function ContributeForm({ t }: { t: Dictionary["contribute"] }) {
  const [state, action, pending] = useActionState(submitContributor, initial);

  return (
    <form action={action} className="contrib-form">
      {/* Honeypot anti-bot (revue 2026-06-10 C2) : hors écran, non focusable, non
          autocomplété. Un humain ne le voit pas ; un bot qui le remplit est rejeté
          silencieusement côté serveur. */}
      <input
        type="text"
        name="website"
        tabIndex={-1}
        autoComplete="off"
        aria-hidden="true"
        style={{ position: "absolute", left: "-9999px", width: 1, height: 1, opacity: 0 }}
      />
      <div className="cf-row">
        <input name="name" required placeholder={t.name} aria-label={t.name} maxLength={80} />
        <input name="email" type="email" placeholder={t.email} aria-label={t.email} maxLength={120} />
      </div>
      <input name="skill" required placeholder={t.skill} aria-label={t.skill} maxLength={80} />
      <textarea name="message" placeholder={t.message} aria-label={t.message} rows={3} maxLength={600} />
      <button type="submit" className="btn btn-primary" disabled={pending}>
        {pending ? t.sending : t.submit} <span className="arr">→</span>
      </button>
      {state.status === "ok" && <p className="cf-msg ok" role="status">{t.ok}</p>}
      {state.status === "error" && <p className="cf-msg err" role="alert">{state.message === "needName" ? t.needName : t.err}</p>}
    </form>
  );
}
