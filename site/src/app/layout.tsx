import type { Metadata, Viewport } from "next";
import { Inter, Fraunces, JetBrains_Mono } from "next/font/google";
import { getLocale } from "@/lib/i18n";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: "swap" });
const fraunces = Fraunces({ subsets: ["latin"], variable: "--font-fraunces", display: "swap", weight: ["400", "500", "600"] });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap", weight: ["400", "500"] });

export const metadata: Metadata = {
  title: "Aratea — Marchés prédictifs météo & mutuelle paramétrique décentralisée",
  description:
    "Projet de recherche open-source : un predictor météo, une couche de règlement on-chain, et à terme une mutuelle paramétrique décentralisée. Construit en public.",
  metadataBase: new URL("https://aratea.vercel.app"),
  openGraph: {
    title: "Aratea — DAO météo + mutuelle paramétrique décentralisée",
    description: "Predictor météo, règlement on-chain, mutuelle paramétrique. Recherche en cours, en public.",
    type: "website",
  },
  icons: { icon: "/favicon.svg", apple: "/favicon.svg" },
};

export const viewport: Viewport = {
  themeColor: "#0a0e13",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = await getLocale();
  return (
    <html lang={locale} className={`${inter.variable} ${fraunces.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
