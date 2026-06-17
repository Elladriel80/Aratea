import { NextResponse, type NextRequest } from "next/server";

import { oauthCredentials } from "@/lib/server/config";
import { exchangeCodeForToken, fetchGithubLogin } from "@/lib/server/oauth";
import { readAndClearOAuthTx, writeSession } from "@/lib/server/session";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Retour OAuth GitHub : vérifie `state` (anti-CSRF), échange le code (PKCE +
 * secret server-only), lit le `login`, ouvre une session signée courte, et
 * renvoie vers /contribuer à l'étape « wallet ».
 */
export async function GET(req: NextRequest) {
  const origin = req.nextUrl.origin;
  const back = (q: string) => NextResponse.redirect(new URL(`/contribuer?${q}`, origin));

  const params = req.nextUrl.searchParams;
  const code = params.get("code");
  const state = params.get("state");

  // Le state attendu vit dans un cookie signé infalsifiable, lu et détruit ici
  // (usage unique). Toute incohérence = rejet (CSRF / lien rejoué).
  const tx = await readAndClearOAuthTx();
  if (!tx || !code || !state || state !== tx.state) {
    return back("error=oauth_state");
  }

  try {
    const { clientId, clientSecret } = oauthCredentials();
    const redirectUri = new URL("/api/contributor/github/callback", origin).toString();
    const token = await exchangeCodeForToken({
      clientId,
      clientSecret,
      code,
      redirectUri,
      codeVerifier: tx.codeVerifier,
    });
    const login = await fetchGithubLogin(token);
    await writeSession({ login });
    return back("step=wallet");
  } catch {
    return back("error=oauth_failed");
  }
}
