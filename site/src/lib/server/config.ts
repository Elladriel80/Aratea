/**
 * Configuration serveur du « compte contributeur ».
 *
 * Tout ici est SERVER-ONLY : aucune de ces variables ne doit porter le préfixe
 * `NEXT_PUBLIC_` ni être importée par un composant client. Les secrets ne sont
 * lus qu'à la demande (jamais au moment de l'import), pour que le build passe
 * même sans secrets configurés (ex. CI, preview).
 */

// Dépôt cible du registre. Surchargé par env au besoin ; défaut = dépôt Aratea.
export const REPO = process.env.GH_REPO || "Elladriel80/Aratea";
export const [REPO_OWNER, REPO_NAME] = REPO.split("/");

// Chemin du registre public dans le dépôt.
export const WALLETS_PATH = "rounds/WALLETS.md";

// Scope OAuth : le minimum absolu. On ne lit que le `login` de l'utilisateur.
export const OAUTH_SCOPE = "read:user";

// Durées de vie (courtes par sécurité).
export const SESSION_TTL_MS = 30 * 60 * 1000; // session GitHub vérifiée : 30 min
export const NONCE_TTL_MS = 10 * 60 * 1000; //   nonce de signature : 10 min
export const OAUTH_TX_TTL_MS = 10 * 60 * 1000; // transaction OAuth (state/PKCE) : 10 min

/**
 * Lit une variable d'environnement obligatoire. Lève une erreur claire si elle
 * manque — appelée seulement dans les chemins qui en ont besoin (jamais à
 * l'import), pour ne pas casser le build quand les secrets ne sont pas posés.
 */
export function requireEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Variable d'environnement manquante : ${name}`);
  return v;
}

/** Le secret de signature des cookies de session. */
export function sessionSecret(): string {
  return requireEnv("SESSION_SECRET");
}

/** Les identifiants de l'OAuth App GitHub (server-only). */
export function oauthCredentials(): { clientId: string; clientSecret: string } {
  return {
    clientId: requireEnv("GITHUB_OAUTH_CLIENT_ID"),
    clientSecret: requireEnv("GITHUB_OAUTH_CLIENT_SECRET"),
  };
}

/** True si la GitHub App (écriture du registre par PR) est configurée. */
export function isGithubAppConfigured(): boolean {
  return Boolean(
    process.env.GH_APP_ID &&
      process.env.GH_APP_PRIVATE_KEY &&
      process.env.GH_APP_INSTALLATION_ID,
  );
}

/** Les identifiants de la GitHub App (server-only). */
export function githubAppCredentials(): {
  appId: string;
  privateKey: string;
  installationId: string;
} {
  return {
    appId: requireEnv("GH_APP_ID"),
    // La clé privée PEM peut être stockée avec des "\n" littéraux (Vercel) :
    // on les restaure en vrais retours à la ligne.
    privateKey: requireEnv("GH_APP_PRIVATE_KEY").replace(/\\n/g, "\n"),
    installationId: requireEnv("GH_APP_INSTALLATION_ID"),
  };
}
