import { describe, it, expect } from "vitest";
import { createVerify, generateKeyPairSync } from "node:crypto";

import { appJwt, buildWalletsRow, insertWalletsRow } from "./registry";

describe("buildWalletsRow", () => {
  it("produit le format de ligne EXACT du registre", () => {
    expect(
      buildWalletsRow({ login: "octocat", address: "0xAbC", date: "2026-06-17", signature: "0xsig" }),
    ).toBe("| @octocat | 0xAbC | 2026-06-17 | sig: `0xsig` |");
  });
});

describe("insertWalletsRow", () => {
  const md = [
    "# WALLETS",
    "",
    "## Registry",
    "",
    "| GitHub handle | Ethereum address | Registration date | Notes |",
    "|---|---|---|---|",
    "| @alice | 0x1 | 2026-01-01 | x |",
    "",
    "## Address change",
    "blah",
  ].join("\n");

  it("insère la ligne à la fin de la table sous ## Registry", () => {
    const row = "| @bob | 0x2 | 2026-02-02 | sig: `0x` |";
    const out = insertWalletsRow(md, row);
    const lines = out.split("\n");
    const idxAlice = lines.indexOf("| @alice | 0x1 | 2026-01-01 | x |");
    const idxRow = lines.indexOf(row);
    const idxAddr = lines.indexOf("## Address change");
    expect(idxRow).toBe(idxAlice + 1); // juste après la dernière ligne de table
    expect(idxAddr).toBeGreaterThan(idxRow); // la section suivante reste après
  });

  it("filet de sécurité : append en fin si pas de section Registry", () => {
    const out = insertWalletsRow("# Empty\n", "| @x | 0x | d | sig: `0x` |");
    expect(out.trimEnd().endsWith("| @x | 0x | d | sig: `0x` |")).toBe(true);
  });
});

describe("appJwt", () => {
  it("produit un JWT RS256 signé et vérifiable", () => {
    const { privateKey, publicKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
    const pem = privateKey.export({ type: "pkcs8", format: "pem" }) as string;

    const jwt = appJwt({ appId: "12345", privateKey: pem, now: 1_700_000_000_000 });
    const [h, p, s] = jwt.split(".");
    expect(jwt.split(".")).toHaveLength(3);

    const header = JSON.parse(Buffer.from(h, "base64url").toString("utf8"));
    expect(header).toEqual({ alg: "RS256", typ: "JWT" });

    const payload = JSON.parse(Buffer.from(p, "base64url").toString("utf8"));
    expect(payload.iss).toBe("12345");
    expect(payload.exp - payload.iat).toBe(600);

    const verified = createVerify("RSA-SHA256")
      .update(`${h}.${p}`)
      .verify(publicKey, Buffer.from(s, "base64url"));
    expect(verified).toBe(true);
  });
});
