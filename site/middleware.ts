import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const LOCALE_COOKIE = "aratea-locale";

/**
 * Sets the locale cookie on first visit from the Vercel geo header (FR → fr)
 * with an Accept-Language fallback. Never overrides an existing choice, so the
 * in-page toggle always wins on subsequent visits.
 */
export function middleware(req: NextRequest) {
  const res = NextResponse.next();
  if (req.cookies.get(LOCALE_COOKIE)) return res;

  const country = req.headers.get("x-vercel-ip-country");
  const accept = req.headers.get("accept-language") || "";
  const prefersFr = country === "FR" || accept.toLowerCase().startsWith("fr");

  res.cookies.set(LOCALE_COOKIE, prefersFr ? "fr" : "en", {
    path: "/",
    maxAge: 60 * 60 * 24 * 365,
    sameSite: "lax",
  });
  return res;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.svg|.*\\.).*)"],
};
