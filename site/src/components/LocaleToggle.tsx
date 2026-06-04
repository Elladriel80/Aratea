"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";
import type { Locale } from "@/lib/i18n";

export default function LocaleToggle({ locale }: { locale: Locale }) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  function set(next: Locale) {
    if (next === locale) return;
    document.cookie = `aratea-locale=${next}; path=/; max-age=${60 * 60 * 24 * 365}; samesite=lax`;
    startTransition(() => router.refresh());
  }

  return (
    <div className="lang-toggle" role="group" aria-label="Language" data-pending={pending}>
      <button type="button" className={locale === "fr" ? "active" : ""} onClick={() => set("fr")} aria-pressed={locale === "fr"}>
        FR
      </button>
      <button type="button" className={locale === "en" ? "active" : ""} onClick={() => set("en")} aria-pressed={locale === "en"}>
        EN
      </button>
    </div>
  );
}
