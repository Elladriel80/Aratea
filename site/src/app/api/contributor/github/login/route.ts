import { NextResponse, type NextRequest } from "next/server";

import { oauthCredentials } from "@/lib/server/config";
import { buildAuthorizeUrl, newOAuthTx, pkceChallenge } from "@/lib/server/oauth";
import { writeOAuthTx } from "@/lib/server/session";
import { checkRateLimit } from "@/lib/server/ratelimit";

// Node runtime (crypto + cookies signés) ; jamais mis en cache.
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Démarre « Sign in with GitHub » : génère state + PKCE, les scelle dans un
 * cookie httpOnly court, puis redirige vers l'écran d'autorisation GitHub.
 */
export async function GET(req: NextRequest) {
  const origin = req.nextUrl.origin;

  // Frein anti-bot par IP (best-effort).
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
  if (!checkRateLimit(`oauth:${ip}`, 10, 60_000).ok) {
    return NextResponse.redirect(new URL("/contribuer?error=rate_limited", origin));
  }

  try {
    const { clientId } = oauthCredentials();
    const redirectUri = new URL("/api/contributor/github/callback", origin).toString();
    const tx = newOAuthTx();
    await writeOAuthTx(tx);
    const url = buildAuthorizeUrl({
      clientId,
      redirectUri,
      state: tx.state,
      codeChallenge: pkceChallenge(tx.codeVerifier),
    });
    return NextResponse.redirect(url);
  } catch {
    // Secrets non configurés (ex. preview sans OAuth App) : message clair.
    return NextResponse.redirect(new URL("/contribuer?error=oauth_unconfigured", origin));
  }
}
