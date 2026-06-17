/**
 * Écriture du registre par PR, en moindre privilège.
 *
 * Choix retenu (le plus sûr) : le serveur n'a AUCUN droit d'écriture direct sur
 * `main`. Il ouvre une PR via une GitHub App installée sur ce seul dépôt, avec
 * exactement deux permissions (`contents:write` + `pull_requests:write`). La PR
 * cible une branche dédiée `registry/<login>` ; un humain (le ratificateur)
 * re-vérifie la signature puis merge. Aucun merge automatique.
 *
 * Les helpers purs (ligne WALLETS, insertion, JWT) sont testables ; la partie
 * réseau est isolée dans {@link openRegistrationPr}. Server-only.
 */

import { createSign } from "node:crypto";

import { base64url, randomToken } from "./crypto";
import {
  REPO_OWNER,
  REPO_NAME,
  WALLETS_PATH,
  githubAppCredentials,
} from "./config";

const API = "https://api.github.com";

/** Ligne ajoutée au registre. Format STABLE attendu par le ratificateur. */
export function buildWalletsRow(args: {
  login: string;
  address: string;
  date: string;
  signature: string;
}): string {
  return `| @${args.login} | ${args.address} | ${args.date} | sig: \`${args.signature}\` |`;
}

/**
 * Insère `row` à la fin de la table sous le titre « ## Registry ». Pur →
 * testable. Si la section/table est introuvable, ajoute la ligne en fin de
 * fichier (filet de sécurité).
 */
export function insertWalletsRow(markdown: string, row: string): string {
  const lines = markdown.split("\n");
  const headingIdx = lines.findIndex((l) => /^##\s+Registry\b/i.test(l));

  if (headingIdx !== -1) {
    // Repère la 1re ligne de table après le titre, puis la dernière ligne
    // contiguë de cette table.
    let start = -1;
    for (let i = headingIdx + 1; i < lines.length; i++) {
      if (lines[i].trimStart().startsWith("|")) {
        start = i;
        break;
      }
      // Stop si on atteint la section suivante avant toute table.
      if (/^##\s+/.test(lines[i])) break;
    }
    if (start !== -1) {
      let end = start;
      while (end + 1 < lines.length && lines[end + 1].trimStart().startsWith("|")) {
        end++;
      }
      lines.splice(end + 1, 0, row);
      return lines.join("\n");
    }
  }

  // Filet de sécurité : append en fin de fichier.
  const sep = markdown.endsWith("\n") ? "" : "\n";
  return `${markdown}${sep}${row}\n`;
}

/**
 * JWT d'app GitHub (RS256), signé avec la clé privée de l'App via le `crypto`
 * natif de Node (pas de dépendance JWT). `now` injectable pour les tests.
 */
export function appJwt(args: { appId: string; privateKey: string; now: number }): string {
  const iat = Math.floor(args.now / 1000) - 60; // tolérance d'horloge
  const exp = iat + 600; // 10 min (max autorisé par GitHub)
  const headerB64 = base64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const payloadB64 = base64url(JSON.stringify({ iat, exp, iss: args.appId }));
  const signingInput = `${headerB64}.${payloadB64}`;
  const sig = createSign("RSA-SHA256").update(signingInput).sign(args.privateKey).toString("base64url");
  return `${signingInput}.${sig}`;
}

// ── Appels REST GitHub ─────────────────────────────────────────────────────

function ghHeaders(token: string): Record<string, string> {
  return {
    authorization: `Bearer ${token}`,
    accept: "application/vnd.github+json",
    "x-github-api-version": "2022-11-28",
    "user-agent": "aratea-contributor-flow",
  };
}

async function ghJson<T>(res: Response, step: string): Promise<T> {
  if (!res.ok) {
    // On ne logge jamais de secret ; uniquement l'étape et le status.
    throw new Error(`GitHub API ${step} → ${res.status}`);
  }
  return (await res.json()) as T;
}

/**
 * Ouvre une PR ajoutant la ligne vérifiée au registre. Renvoie l'URL de la PR.
 * Aucune écriture sur `main` : tout passe par une branche + PR à ratifier.
 */
export async function openRegistrationPr(args: {
  login: string;
  address: string;
  date: string;
  signature: string;
  message: string;
}): Promise<{ prUrl: string }> {
  const { appId, privateKey, installationId } = githubAppCredentials();

  // 1) JWT d'app → token d'installation (durée de vie courte, scope = ce dépôt).
  const jwt = appJwt({ appId, privateKey, now: Date.now() });
  const tokRes = await fetch(`${API}/app/installations/${installationId}/access_tokens`, {
    method: "POST",
    headers: ghHeaders(jwt),
  });
  const { token } = await ghJson<{ token: string }>(tokRes, "installation token");

  // 2) Branche par défaut + son sha de tête.
  const repo = await ghJson<{ default_branch: string }>(
    await fetch(`${API}/repos/${REPO_OWNER}/${REPO_NAME}`, { headers: ghHeaders(token) }),
    "get repo",
  );
  const base = repo.default_branch;
  const baseRef = await ghJson<{ object: { sha: string } }>(
    await fetch(`${API}/repos/${REPO_OWNER}/${REPO_NAME}/git/ref/heads/${base}`, {
      headers: ghHeaders(token),
    }),
    "get base ref",
  );
  const baseSha = baseRef.object.sha;

  // 3) Crée la branche dédiée (suffixe unique si elle existe déjà).
  let branch = `registry/${args.login}`;
  let created = await fetch(`${API}/repos/${REPO_OWNER}/${REPO_NAME}/git/refs`, {
    method: "POST",
    headers: ghHeaders(token),
    body: JSON.stringify({ ref: `refs/heads/${branch}`, sha: baseSha }),
  });
  if (created.status === 422) {
    branch = `registry/${args.login}-${randomToken(4)}`;
    created = await fetch(`${API}/repos/${REPO_OWNER}/${REPO_NAME}/git/refs`, {
      method: "POST",
      headers: ghHeaders(token),
      body: JSON.stringify({ ref: `refs/heads/${branch}`, sha: baseSha }),
    });
  }
  if (!created.ok) throw new Error(`GitHub API create branch → ${created.status}`);

  // 4) Lit le registre sur la branche, insère la ligne, ré-écrit.
  const file = await ghJson<{ content: string; sha: string }>(
    await fetch(
      `${API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${WALLETS_PATH}?ref=${branch}`,
      { headers: ghHeaders(token) },
    ),
    "get file",
  );
  const current = Buffer.from(file.content, "base64").toString("utf8");
  const updated = insertWalletsRow(current, buildWalletsRow(args));

  const putRes = await fetch(`${API}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${WALLETS_PATH}`, {
    method: "PUT",
    headers: ghHeaders(token),
    body: JSON.stringify({
      message: `registry: add @${args.login}`,
      content: Buffer.from(updated, "utf8").toString("base64"),
      sha: file.sha,
      branch,
    }),
  });
  if (!putRes.ok) throw new Error(`GitHub API put file → ${putRes.status}`);

  // 5) Ouvre la PR (jamais de merge auto : un humain ratifie).
  const prBody = [
    "Enregistrement contributeur vérifié automatiquement (OAuth GitHub + signature wallet).",
    "",
    "**Le ratificateur doit re-vérifier la signature avant de merger :**",
    "```",
    `cast wallet verify --address ${args.address} "${args.message}" ${args.signature}`,
    "```",
    "(doit renvoyer `true`)",
    "",
    "_Aucune écriture directe sur `main` : merge manuel après vérification._",
  ].join("\n");

  const pr = await ghJson<{ html_url: string }>(
    await fetch(`${API}/repos/${REPO_OWNER}/${REPO_NAME}/pulls`, {
      method: "POST",
      headers: ghHeaders(token),
      body: JSON.stringify({
        title: `registry: add @${args.login}`,
        head: branch,
        base,
        body: prBody,
      }),
    }),
    "create pr",
  );

  return { prUrl: pr.html_url };
}
