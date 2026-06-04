import type { Metadata } from "next";
import Link from "next/link";
import Nav from "@/components/Nav";
import Reveal from "@/components/Reveal";
import { getDictAndLocale } from "@/lib/i18n";

export const metadata: Metadata = {
  title: "Roadmap — Aratea",
  description: "La trajectoire d'Aratea, enchaînée par jalons techniques : predictor, contrats, DAO, mutuelle paramétrique, couche data DePIN.",
};

export default async function RoadmapPage() {
  const { dict, locale } = await getDictAndLocale();
  const t = dict.roadmapPage;

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
          <h1 className="h1" style={{ fontSize: "clamp(36px, 6vw, 60px)" }}>{t.title}</h1>
          <p className="lede">{t.intro}</p>
        </header>

        <section className="sec" style={{ paddingTop: 0 }}>
          <div className="rm-list">
            {t.phases.map((p, i) => {
              const current = p.tag === "en cours" || p.tag === "current";
              return (
                <Reveal key={i}>
                  <div className="rm-phase">
                    <div className="rm-when">
                      <span>{p.when}</span>
                      <span className={current ? "tag wip" : "tag build"}>{p.tag}</span>
                    </div>
                    <div className="rm-body">
                      <h3>{p.h}</h3>
                      <ul>
                        {p.items.map((it, j) => (
                          <li key={j}>{it}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </Reveal>
              );
            })}
          </div>
          <p className="src-note" style={{ marginTop: 24 }}>{t.note}</p>
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
