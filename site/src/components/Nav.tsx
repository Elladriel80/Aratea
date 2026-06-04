"use client";

import { useEffect, useState } from "react";
import LocaleToggle from "./LocaleToggle";
import WalletButton from "./WalletButton";
import type { Dictionary, Locale } from "@/lib/i18n";

export default function Nav({
  locale,
  nav,
  wallet,
}: {
  locale: Locale;
  nav: Dictionary["nav"];
  wallet: Dictionary["wallet"];
}) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav className={scrolled ? "nav nav-scrolled" : "nav"}>
      <a className="brand" href="#top" aria-label="Aratea">
        <span className="mark">A</span>
        <span className="name">Aratea</span>
      </a>
      <div className="nav-right">
        <div className="nav-links">
          <a href="#mission">{nav.mission}</a>
          <a href="#status">{nav.status}</a>
          <a href="#approach">{nav.approach}</a>
          <a href="#contribute">{nav.contribute}</a>
        </div>
        <WalletButton labels={wallet} />
        <LocaleToggle locale={locale} />
      </div>
    </nav>
  );
}
