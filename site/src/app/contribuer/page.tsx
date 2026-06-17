import type { Metadata } from "next";
import Link from "next/link";

import Nav from "@/components/Nav";
import ContributorAccount from "@/components/ContributorAccount";
import { getDictAndLocale } from "@/lib/i18n";
import { readSession } from "@/lib/server/session";

export const metadata: Metadata = {
  title: "Compte contributeur — Aratea",
  description:
    "Lie ton compte GitHub à ton adresse Ethereum, de façon prouvée, pour devenir éligible au mint des tokens contributeurs.",
};

export default async function ContribuerPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string; step?: string }>;
}) {
  const { dict, locale } = await getDictAndLocale();
  const t = dict.account;
  const [session, sp] = await Promise.all([readSession(), searchParams]);

  return (
    <>
      <div className="aurora" aria-hidden="true">
        <span className="a1" />
        <span className="a2" />
        <span className="a3" />
      </div>
      <div className="grain" aria-hidden="true" />

      <Nav locale={locale} nav={dict.nav} wallet={dict.wallet} />

      <main className="wrap">
        <header className="hero" style={{ paddingBottom: 20 }}>
          <Link className="rm-back" href="/">← {t.back}</Link>
          <div className="sec-label" style={{ marginTop: 18 }}>{t.eyebrow}</div>
          <h1 className="h1" style={{ fontSize: "clamp(34px, 6vw, 56px)" }}>{t.title}</h1>
          <p className="lede">{t.intro}</p>
        </header>

        <section className="sec" style={{ paddingTop: 0 }}>
          <ContributorAccount
            t={t}
            initialLogin={session?.login ?? null}
            initialError={sp?.error ?? null}
          />
        </section>

        <footer>
          <div className="foot-grid">
            <p className="foot-note">{dict.footer.note}</p>
            <div className="foot-meta">
              <div>© 2026 Aratea</div>
              <div>{dict.footer.meta}</div>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
