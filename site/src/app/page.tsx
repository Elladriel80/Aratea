import { formatUnits } from "viem";
import Link from "next/link";

import Nav from "@/components/Nav";
import Reveal from "@/components/Reveal";
import { getDictAndLocale } from "@/lib/i18n";
import { fetchManifest } from "@/lib/manifest";
import { publicClient } from "@/lib/chain";
import { tokenAddress, augPocTokenAbi, isDeployed } from "@/lib/contracts";
import { LINKS } from "@/lib/links";
import { formatInt, formatUsd, formatDate } from "@/lib/format";

type OnChain = { supply: bigint; decimals: number; paused: boolean };

async function readOnChain(): Promise<OnChain | null> {
  if (!isDeployed()) return null;
  try {
    const [supply, decimals, paused] = await Promise.all([
      publicClient.readContract({ address: tokenAddress, abi: augPocTokenAbi, functionName: "totalSupply" }),
      publicClient.readContract({ address: tokenAddress, abi: augPocTokenAbi, functionName: "decimals" }),
      publicClient.readContract({ address: tokenAddress, abi: augPocTokenAbi, functionName: "paused" }),
    ]);
    return { supply: supply as bigint, decimals: Number(decimals), paused: paused as boolean };
  } catch {
    return null;
  }
}

export default async function Home() {
  const { dict, locale } = await getDictAndLocale();
  const [manifest, onchain] = await Promise.all([fetchManifest(), readOnChain()]);
  const pbs = manifest?.paper_bets_summary;
  const resolved = pbs?.n_resolved ?? 115;

  const linkItems = [
    { lk: "community", v: dict.links.community, href: LINKS.discord, ext: true },
    { lk: "code", v: dict.links.code, href: LINKS.github, ext: true },
    { lk: "state", v: dict.links.state, href: LINKS.dashboard, ext: true },
    { lk: "trajectory", v: dict.links.trajectory, href: LINKS.roadmap[locale], ext: true },
    { lk: "whitepaper", v: dict.links.whitepaper, href: LINKS.notion[locale], ext: true },
  ];

  return (
    <>
      <div className="aurora" aria-hidden="true">
        <span className="a1" />
        <span className="a2" />
        <span className="a3" />
      </div>
      <div className="grain" aria-hidden="true" />

      <Nav locale={locale} nav={dict.nav} wallet={dict.wallet} />
      <span id="top" />

      <main className="wrap">
        {/* HERO */}
        <header className="hero">
          <Reveal className="eyebrow">
            <span className="dot" />
            {dict.hero.eyebrow}
          </Reveal>
          <Reveal delay={60}>
            <h1 className="h1">
              {dict.hero.titleA}
              <br />
              <span className="grad">{dict.hero.titleB}</span>
            </h1>
          </Reveal>
          <Reveal delay={120}>
            <p className="lede">{dict.hero.lede}</p>
          </Reveal>
          <Reveal delay={180} className="cta-row">
            <a className="btn btn-primary" href={LINKS.github} target="_blank" rel="noopener noreferrer">
              {dict.hero.ctaCode} <span className="arr">→</span>
            </a>
            <a className="btn btn-ghost" href={LINKS.dashboard} target="_blank" rel="noopener noreferrer">
              {dict.hero.ctaDashboard}
            </a>
          </Reveal>

          <Reveal delay={240} className="hero-chart">
            <div className="hc-head">
              <span className="hc-title">{dict.hero.chartTitle}</span>
              <span className="hc-legend">
                <span><i style={{ background: "#5eead4" }} />{dict.hero.chartModel}</span>
                <span><i style={{ background: "#56b6f7" }} />{dict.hero.chartMarket}</span>
              </span>
            </div>
            <svg viewBox="0 0 1000 240" preserveAspectRatio="none" width="100%" height="160" role="img" aria-label="Brier score trajectory">
              <line x1="0" y1="60" x2="1000" y2="60" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="120" x2="1000" y2="120" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="180" x2="1000" y2="180" stroke="rgba(255,255,255,0.05)" />
              <path
                className="draw"
                d="M0,70 C150,60 250,150 400,120 C550,95 650,140 800,110 C880,95 950,120 1000,108"
                fill="none"
                stroke="#56b6f7"
                strokeWidth="2.5"
                strokeLinecap="round"
                style={{ transitionDelay: "0.2s" }}
              />
              <path
                className="draw"
                d="M0,150 C150,120 250,170 400,135 C550,108 650,150 800,118 C880,104 950,124 1000,112"
                fill="none"
                stroke="#5eead4"
                strokeWidth="3"
                strokeLinecap="round"
              />
            </svg>
            <p className="hc-note">{dict.hero.chartNote}</p>
          </Reveal>
        </header>

        {/* MISSION */}
        <section id="mission" className="sec">
          <Reveal>
            <div className="sec-label">{dict.mission.label}</div>
            <h2 className="sec-title">{dict.mission.title}</h2>
            <div className="prose-block">
              <p className="lead">{dict.mission.lead}</p>
              <p>{dict.mission.p1}</p>
              <p>{dict.mission.p2}</p>
            </div>
            <div className="principles">
              {dict.mission.principles.map((p, i) => (
                <div className="principle" key={i}>
                  <h4>{p.h}</h4>
                  <p>{p.d}</p>
                </div>
              ))}
            </div>
          </Reveal>
        </section>

        {/* CONTEXT */}
        <section id="context" className="sec">
          <Reveal>
            <div className="sec-label">{dict.context.label}</div>
            <h2 className="sec-title">{dict.context.title}</h2>
            <p className="sec-intro">{dict.context.intro}</p>
            <div className="figures">
              {dict.context.figures.map((f, i) => (
                <div className="figure" key={i}>
                  <div className="fig-num">{f.value}</div>
                  <div className="fig-lbl">{f.label}</div>
                </div>
              ))}
            </div>
            <p className="src-note">{dict.context.source}</p>
          </Reveal>
        </section>

        {/* WHY DECENTRALIZED */}
        <section id="why" className="sec">
          <Reveal>
            <div className="sec-label">{dict.why.label}</div>
            <h2 className="sec-title">{dict.why.title}</h2>
            <div className="principles">
              {dict.why.points.map((p, i) => (
                <div className="principle" key={i}>
                  <h4>{p.h}</h4>
                  <p>{p.d}</p>
                </div>
              ))}
            </div>
          </Reveal>
        </section>

        {/* PROJECT + STATS */}
        <section id="project" className="sec">
          <Reveal>
            <div className="sec-label">{dict.project.label}</div>
            <h2 className="sec-title">{dict.project.title}</h2>
            <p className="sec-intro">{dict.project.intro}</p>
            <div className="stats">
              <div className="stat"><div className="num">{formatInt(resolved, locale)}</div><div className="lbl">{dict.stats.resolved}</div></div>
              <div className="stat"><div className="num">0 $</div><div className="lbl">{dict.stats.atRisk}</div></div>
              <div className="stat"><div className="num">3</div><div className="lbl">{dict.stats.models}</div></div>
              <div className="stat"><div className="num">100%</div><div className="lbl">{dict.stats.openSource}</div></div>
            </div>
          </Reveal>
        </section>

        {/* LIVE DATA */}
        <section id="live" className="sec">
          <Reveal>
            <div className="sec-label">{dict.live.label}</div>
            <h2 className="sec-title">{dict.live.title}</h2>
            <div className="live-grid">
              <div className="live-card">
                <div className="lc-head">
                  <span className="lc-title">{dict.live.predictorCard}</span>
                  <span className="tag wip">{dict.live.phase}</span>
                </div>
                {pbs ? (
                  <>
                    <div className="kv"><span className="k">{dict.live.resolved}</span><span className="v">{formatInt(pbs.n_resolved, locale)}</span></div>
                    <div className="kv"><span className="k">{dict.live.open}</span><span className="v">{formatInt(pbs.n_open, locale)}</span></div>
                    <div className="kv"><span className="k">{dict.live.pnl}</span><span className="v small">{formatUsd(pbs.pnl_usd_cumulative, locale)}</span></div>
                  </>
                ) : (
                  <p className="live-empty">{dict.live.unavailable}</p>
                )}
              </div>

              <div className="live-card">
                <div className="lc-head">
                  <span className="lc-title">{dict.live.onchainCard}</span>
                  <span className={onchain ? "tag live" : "tag build"}>{onchain ? "AUG-POC" : "testnet"}</span>
                </div>
                {onchain ? (
                  <>
                    <div className="kv"><span className="k">{dict.live.supply}</span><span className="v">{formatInt(Number(formatUnits(onchain.supply, onchain.decimals)), locale)}</span></div>
                    <div className="kv"><span className="k">{dict.live.state}</span><span className="v small">{onchain.paused ? dict.live.paused : dict.live.active}</span></div>
                  </>
                ) : (
                  <p className="live-empty">{dict.live.notDeployed}</p>
                )}
              </div>
            </div>
            <p className="live-foot">
              {dict.live.source}:{" "}
              <a href={LINKS.dashboard} target="_blank" rel="noopener noreferrer">dashboard</a>
              {manifest?.generated_at ? ` · ${dict.live.updated} ${formatDate(manifest.generated_at, locale)}` : ""}
            </p>
          </Reveal>
        </section>

        {/* STATUS */}
        <section id="status" className="sec">
          <Reveal>
            <div className="sec-label">{dict.status.label}</div>
            <h2 className="sec-title">{dict.status.title}</h2>
            <div className="grid grid-3">
              <div className="card"><span className="tag wip">{dict.status.predictorTag}</span><h3>{dict.status.predictorH}</h3><p>{dict.status.predictorP}</p></div>
              <div className="card"><span className="tag build">{dict.status.contractsTag}</span><h3>{dict.status.contractsH}</h3><p>{dict.status.contractsP}</p></div>
              <div className="card"><span className="tag live">{dict.status.dashboardTag}</span><h3>{dict.status.dashboardH}</h3><p>{dict.status.dashboardP}</p></div>
            </div>
          </Reveal>
        </section>

        {/* APPROACH */}
        <section id="approach" className="sec">
          <Reveal>
            <div className="sec-label">{dict.approach.label}</div>
            <h2 className="sec-title">{dict.approach.title}</h2>
            <p className="sec-intro">{dict.approach.intro}</p>
            <div className="pillars">
              <div className="pillar"><div className="step">01</div><h3>{dict.approach.p1H}</h3><p>{dict.approach.p1P}</p></div>
              <div className="pillar"><div className="step">02</div><h3>{dict.approach.p2H}</h3><p>{dict.approach.p2P}</p></div>
              <div className="pillar"><div className="step">03</div><h3>{dict.approach.p3H}<span className="badge">{dict.approach.soon}</span></h3><p>{dict.approach.p3P}</p></div>
            </div>
          </Reveal>
        </section>

        {/* ROADMAP */}
        <section id="roadmap" className="sec">
          <Reveal>
            <div className="sec-label">{dict.roadmap.label}</div>
            <h2 className="sec-title">{dict.roadmap.title}</h2>
            <div className="timeline">
              <div className="phase is-current"><div className="when">Phase 1</div><div className="what"><h4>{dict.roadmap.p1H}<span className="pill">{dict.roadmap.current}</span></h4><p>{dict.roadmap.p1P}</p></div></div>
              <div className="phase"><div className="when">Phase 2</div><div className="what"><h4>{dict.roadmap.p2H}</h4><p>{dict.roadmap.p2P}</p></div></div>
              <div className="phase"><div className="when">Phase 3</div><div className="what"><h4>{dict.roadmap.p3H}</h4><p>{dict.roadmap.p3P}</p></div></div>
              <div className="phase"><div className="when">Phase 4</div><div className="what"><h4>{dict.roadmap.p4H}</h4><p>{dict.roadmap.p4P}</p></div></div>
            </div>
            <Link className="btn btn-ghost" href="/roadmap" style={{ marginTop: 26 }}>
              {dict.roadmap.cta} <span className="arr">→</span>
            </Link>
          </Reveal>
        </section>

        {/* FAQ */}
        <section id="faq" className="sec">
          <Reveal>
            <div className="sec-label">{dict.faq.label}</div>
            <h2 className="sec-title">{dict.faq.title}</h2>
            <div className="faq">
              {dict.faq.items.map((it, i) => (
                <details className="qa" key={i}>
                  <summary>{it.q}</summary>
                  <p>{it.a}</p>
                </details>
              ))}
            </div>
          </Reveal>
        </section>

        {/* CONTRIBUTE */}
        <section id="contribute" className="sec">
          <Reveal>
            <div className="band">
              <h2>{dict.contribute.title}</h2>
              <p>{dict.contribute.intro}</p>
              <div className="roles-title">{dict.contribute.rolesTitle}</div>
              <div className="roles">
                {dict.contribute.roles.map((r, i) => (
                  <div className="role" key={i}>
                    <h4>{r.h}</h4>
                    <p>{r.d}</p>
                  </div>
                ))}
              </div>
              <p className="closing">{dict.contribute.closing}</p>
              <div className="band-cta">
                <Link className="btn btn-primary band-account" href="/contribuer">{dict.contribute.account} <span className="arr">→</span></Link>
              </div>
            </div>
            <div className="links">
              {linkItems.map((l) => (
                <a key={l.lk} className="link-card" href={l.href} target="_blank" rel="noopener noreferrer">
                  <span className="lk">{`// ${l.lk}`}</span>
                  <span className="lv">{l.v}</span>
                </a>
              ))}
            </div>
          </Reveal>
        </section>

        <footer>
          <div className="foot-grid">
            <p className="foot-note">{dict.footer.note}</p>
            <div className="foot-meta">
              <div>© 2026 Aratea</div>
              <div>{dict.footer.meta}</div>
              <div>{dict.footer.updated} 2026-06-04</div>
            </div>
          </div>
        </footer>
      </main>
    </>
  );
}
