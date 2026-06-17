/**
 * OAuth 2.0 « Sign in with GitHub » — Authorization Code + `state` (anti-CSRF)
 * + PKCE (S256). Scope minimal : `read:user` (on ne lit que le login).
 *
 * Note sur PKCE et GitHub : `state` est la protection CSRF effectivement
 * imposée par GitHub. PKCE (code_challenge/code_verifier) est envoyé en
 * défense en profondeur et par conformité ; GitHub ignore les paramètres
 * inconnus, donc l'ajouter ne casse rien et durcit le flux si/quand GitHub
 * l'applique. Le secret client n'est utilisé QUE côté serveur.
 *
 * Module PUR (helpers + appels réseau, aucune dépendance à next/headers) →
 * testable. Les cookies state/PKCE vivent dans `session.ts`. Server-only.
 */

import { randomToken, sha256Base64url } from "./crypto";
import { OAUTH_SCOPE } from "./config";

const AUTHORIZE_URL = "https://github.com/login/oauth/authorize";
const TOKEN_URL = "https://github.com/login/oauth/access_token";
const USER_URL = "https://api.github.com/user";

/** Données de la transaction OAuth, scellées dans un cookie le temps de l'aller-retour. */
export type OAuthTx = { state: string; codeVerifier: string };

/** code_challenge PKCE = base64url(SHA-256(code_verifier)). Pur → testable. */
export function pkceChallenge(verifier: string): string {
  return sha256Base64url(verifier);
}

/** Construit l'URL d'autorisation GitHub. Pur → testable. */
export function buildAuthorizeUrl(params: {
  clientId: string;
  redirectUri: string;
  state: string;
  codeChallenge: string;
}): string {
  const u = new URL(AUTHORIZE_URL);
  u.searchParams.set("client_id", params.clientId);
  u.searchParams.set("redirect_uri", params.redirectUri);
  u.searchParams.set("scope", OAUTH_SCOPE);
  u.searchParams.set("state", params.state);
  u.searchParams.set("code_challenge", params.codeChallenge);
  u.searchParams.set("code_challenge_method", "S256");
  u.searchParams.set("allow_signup", "false");
  return u.toString();
}

/** Génère une transaction OAuth fraîche (state + code_verifier PKCE). */
export function newOAuthTx(): OAuthTx {
  return { state: randomToken(32), codeVerifier: randomToken(32) };
}

/**
 * Échange le `code` d'autorisation contre un access token. Utilise le secret
 * client (server-only) + le code_verifier PKCE. Lève en cas d'erreur OAuth.
 */
export async function exchangeCodeForToken(args: {
  clientId: string;
  clientSecret: string;
  code: string;
  redirectUri: string;
  codeVerifier: string;
}): Promise<string> {
  const res = await fetch(TOKEN_URL, {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify({
      client_id: args.clientId,
      client_secret: args.clientSecret,
      code: args.code,
      redirect_uri: args.redirectUri,
      code_verifier: args.codeVerifier,
    }),
  });
  const data = (await res.json()) as {
    access_token?: string;
    error?: string;
    error_description?: string;
  };
  if (!data.access_token) {
    throw new Error(`Échange OAuth échoué : ${data.error || res.status}`);
  }
  return data.access_token;
}

/**
 * Récupère le `login` GitHub de l'utilisateur authentifié. C'est la SEULE donnée
 * GitHub qu'on lit, et elle n'est jamais persistée au-delà de la session.
 */
export async function fetchGithubLogin(accessToken: string): Promise<string> {
  const res = await fetch(USER_URL, {
    headers: {
      authorization: `Bearer ${accessToken}`,
      accept: "application/vnd.github+json",
      "user-agent": "aratea-contributor-flow",
    },
  });
  if (!res.ok) throw new Error(`Lecture du profil GitHub échouée : ${res.status}`);
  const data = (await res.json()) as { login?: string };
  if (!data.login) throw new Error("Profil GitHub sans login.");
  return data.login;
}
