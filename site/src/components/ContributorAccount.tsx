"use client";

/**
 * ContributorAccount — parcours « compte contributeur » en 4 étapes :
 *   1) Connexion GitHub (OAuth, côté serveur)  → on reçoit le `login` vérifié.
 *   2) Connexion du wallet (EIP-1193) + bon réseau.
 *   3) Signature du message canonique (personal_sign) — le message vient du
 *      serveur (requestNonce), on le signe TEL QUEL, zéro reconstruction locale.
 *   4) Confirmation : lien vers la PR ouverte (ou ligne vérifiée à ratifier).
 *
 * Le composant ne détient AUCUN secret et ne décide rien : toute la vérification
 * est faite par les server actions. Il n'envoie jamais de transaction.
 */

import { useEffect, useState, useTransition } from "react";

import { requestNonce, submitRegistration, type SubmitState } from "@/app/contribuer/actions";
import type { Dictionary } from "@/lib/i18n";

type Eip1193 = {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
  on?: (event: string, handler: (...args: unknown[]) => void) => void;
  removeListener?: (event: string, handler: (...args: unknown[]) => void) => void;
};
declare global {
  interface Window {
    ethereum?: Eip1193;
  }
}

const TARGET_CHAIN_ID = Number(process.env.NEXT_PUBLIC_CHAIN_ID || 421614);
const TARGET_HEX = "0x" + TARGET_CHAIN_ID.toString(16);

function short(addr: string): string {
  return addr.length < 10 ? addr : `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

export default function ContributorAccount({
  t,
  initialLogin,
  initialError,
}: {
  t: Dictionary["account"];
  initialLogin: string | null;
  initialError: string | null;
}) {
  const login = initialLogin;

  // Wallet
  const [hasWallet, setHasWallet] = useState(true);
  const [address, setAddress] = useState<string | null>(null);
  const [chainOk, setChainOk] = useState(true);

  // Flux de signature
  function errMsg(reason: string | null): string {
    if (!reason) return "";
    const map = t.errors as Record<string, string>;
    return map[reason] ?? t.errors.generic;
  }

  const [message, setMessage] = useState<string | null>(null);
  const [result, setResult] = useState<SubmitState | null>(null);
  // L'erreur initiale vient d'un code (?error=…) côté URL : on la traduit aussi.
  const [error, setError] = useState<string | null>(initialError ? errMsg(initialError) : null);
  const [copied, setCopied] = useState(false);
  const [honeypot, setHoneypot] = useState("");
  const [pending, startTransition] = useTransition();
  const [signing, setSigning] = useState(false);

  useEffect(() => {
    setHasWallet(typeof window !== "undefined" && !!window.ethereum);
    const eth = window.ethereum;
    if (!eth?.on) return;
    const onAccounts = (...a: unknown[]) => {
      const accs = a[0] as string[];
      setAddress(accs?.[0] ?? null);
      // Changer de compte invalide le message déjà préparé (lié à l'adresse).
      setMessage(null);
      setResult(null);
    };
    const onChain = (...a: unknown[]) =>
      setChainOk(parseInt(a[0] as string, 16) === TARGET_CHAIN_ID);
    eth.on("accountsChanged", onAccounts);
    eth.on("chainChanged", onChain);
    return () => {
      eth.removeListener?.("accountsChanged", onAccounts);
      eth.removeListener?.("chainChanged", onChain);
    };
  }, []);

  async function connectWallet() {
    const eth = window.ethereum;
    if (!eth) {
      setHasWallet(false);
      return;
    }
    try {
      const accs = (await eth.request({ method: "eth_requestAccounts" })) as string[];
      setAddress(accs?.[0] ?? null);
      const cid = (await eth.request({ method: "eth_chainId" })) as string;
      setChainOk(parseInt(cid, 16) === TARGET_CHAIN_ID);
    } catch {
      /* refusé par l'utilisateur */
    }
  }

  async function switchNet() {
    const eth = window.ethereum;
    if (!eth) return;
    try {
      await eth.request({ method: "wallet_switchEthereumChain", params: [{ chainId: TARGET_HEX }] });
      setChainOk(true);
    } catch {
      /* réseau non ajouté / refusé */
    }
  }

  function prepareMessage() {
    if (!address) return;
    setError(null);
    setResult(null);
    startTransition(async () => {
      const res = await requestNonce(address);
      if (res.status === "ok") setMessage(res.message);
      else setError(errMsg(res.reason));
    });
  }

  async function signAndSubmit() {
    const eth = window.ethereum;
    if (!eth || !address || !message) return;
    setError(null);
    setSigning(true);
    try {
      const signature = (await eth.request({
        method: "personal_sign",
        params: [message, address],
      })) as string;
      startTransition(async () => {
        const res = await submitRegistration({ signature, website: honeypot });
        setResult(res);
        if (res.status === "error") setError(errMsg(res.reason));
        else setMessage(null);
      });
    } catch {
      setError(errMsg("bad-signature"));
    } finally {
      setSigning(false);
    }
  }

  function reset() {
    setMessage(null);
    setResult(null);
    setError(null);
  }

  const step1Done = !!login;
  const step2Done = step1Done && !!address && chainOk;
  const done = result?.status === "ok";

  function stepClass(active: boolean, complete: boolean): string {
    return `acct-step${complete ? " is-done" : active ? " is-active" : " is-locked"}`;
  }

  return (
    <div className="acct">
      <p className="acct-nofunds" role="note">{t.noFunds}</p>

      {error && (
        <p className="acct-err" role="alert">{error}</p>
      )}

      {/* Honeypot anti-bot (hors écran, non focusable). */}
      <input
        type="text"
        name="website"
        tabIndex={-1}
        autoComplete="off"
        aria-hidden="true"
        value={honeypot}
        onChange={(e) => setHoneypot(e.target.value)}
        style={{ position: "absolute", left: "-9999px", width: 1, height: 1, opacity: 0 }}
      />

      {/* Étape 1 — GitHub */}
      <section className={stepClass(!step1Done, step1Done)} aria-labelledby="acct-s1">
        <div className="acct-num">1</div>
        <div className="acct-body">
          <h3 id="acct-s1">{t.s1}</h3>
          {step1Done ? (
            <p className="acct-ok" role="status">{t.s1done} <strong>@{login}</strong></p>
          ) : (
            <a className="btn btn-primary" href="/api/contributor/github/login">{t.s1cta}</a>
          )}
        </div>
      </section>

      {/* Étape 2 — Wallet */}
      <section className={stepClass(step1Done && !step2Done, step2Done)} aria-labelledby="acct-s2">
        <div className="acct-num">2</div>
        <div className="acct-body">
          <h3 id="acct-s2">{t.s2}</h3>
          {!step1Done ? (
            <p className="acct-muted">{t.s2locked}</p>
          ) : !hasWallet ? (
            <p className="acct-muted">{t.noWallet}</p>
          ) : !address ? (
            <button type="button" className="btn btn-primary" onClick={connectWallet}>{t.s2cta}</button>
          ) : !chainOk ? (
            <button type="button" className="btn btn-ghost warn" onClick={switchNet}>{t.s2switch}</button>
          ) : (
            <p className="acct-ok" role="status">{t.s2connected} — <code>{short(address)}</code></p>
          )}
        </div>
      </section>

      {/* Étape 3 — Signature */}
      <section className={stepClass(step2Done && !done, done)} aria-labelledby="acct-s3">
        <div className="acct-num">3</div>
        <div className="acct-body">
          <h3 id="acct-s3">{t.s3}</h3>
          {!step2Done ? (
            <p className="acct-muted">{t.s3locked}</p>
          ) : !message ? (
            <button type="button" className="btn btn-primary" onClick={prepareMessage} disabled={pending}>
              {pending ? "…" : t.s3get}
            </button>
          ) : (
            <>
              <p className="acct-msglabel">{t.s3msg}</p>
              <pre className="acct-msg"><code>{message}</code></pre>
              <button type="button" className="btn btn-primary" onClick={signAndSubmit} disabled={signing || pending}>
                {signing || pending ? t.s3signing : t.s3sign}
              </button>
            </>
          )}
        </div>
      </section>

      {/* Étape 4 — Confirmation */}
      {done && result?.status === "ok" && (
        <section className="acct-step is-done" aria-labelledby="acct-s4">
          <div className="acct-num">✓</div>
          <div className="acct-body">
            <h3 id="acct-s4">{t.s4}</h3>
            {result.prUrl ? (
              <div role="status">
                <p className="acct-ok">{t.successPr}</p>
                <a className="btn btn-primary" href={result.prUrl} target="_blank" rel="noopener noreferrer">{t.viewPr}</a>
              </div>
            ) : result.manual ? (
              <div role="status">
                <p className="acct-ok">{t.manualTitle}</p>
                <p className="acct-muted">{t.manualIntro}</p>
                <p className="acct-msglabel">{t.manualRow}</p>
                <pre className="acct-msg"><code>{result.manual.row}</code></pre>
                <div className="acct-cta">
                  <button
                    type="button"
                    className="btn btn-ghost"
                    onClick={() => {
                      navigator.clipboard?.writeText(result.manual!.row);
                      setCopied(true);
                      setTimeout(() => setCopied(false), 2000);
                    }}
                  >
                    {copied ? t.copied : t.copy}
                  </button>
                  <a className="btn btn-primary" href={result.manual.editUrl} target="_blank" rel="noopener noreferrer">{t.manualOpen}</a>
                </div>
              </div>
            ) : (
              // Honeypot / faux succès silencieux : rien à afficher d'actionnable.
              <p className="acct-ok" role="status">✓</p>
            )}
            <button type="button" className="acct-reset" onClick={reset}>{t.reset}</button>
          </div>
        </section>
      )}
    </div>
  );
}
