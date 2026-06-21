"use client";

import { useCallback, useEffect, useState } from "react";
import { encodeFunctionData, type Hex } from "viem";

import { publicClient } from "@/lib/chain";
import { BallotState, governorAddress, isGovernorDeployed, mintGovernorAbi, RoundStatus } from "@/lib/contracts";
import { formatTokenAmount, formatUtcDate, shortAddress } from "@/lib/format";

/* ------------------------------------------------------------------ */
/* Wallet helpers (raw EIP-1193 — no wagmi dep)                       */
/* ------------------------------------------------------------------ */

type Eip1193 = {
  request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
  on?: (event: string, handler: (...args: unknown[]) => void) => void;
  removeListener?: (event: string, handler: (...args: unknown[]) => void) => void;
};

declare global {
  interface Window { ethereum?: Eip1193; }
}

const TARGET_CHAIN_ID = Number(process.env.NEXT_PUBLIC_CHAIN_ID || 421614);
const TARGET_HEX = "0x" + TARGET_CHAIN_ID.toString(16);

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

export interface GovernanceRound {
  roundHash: Hex;
  status: number;
  proposedAt: string;   // stringified bigint (seconds)
  challengeWindowDays: number;
}

interface DisputeData {
  snapshot: bigint;
  circulating: bigint;
  quorumVotes: bigint;
  activeBallot: Hex;
  originalDecided: boolean;
  resolved: boolean;
  executed: Hex;
  queue: readonly Hex[];
}

interface BallotData {
  dispute: Hex;
  isOriginal: boolean;
  voteStart: bigint;
  voteEnd: bigint;
  forVotes: bigint;
  againstVotes: bigint;
  state: number;
}

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function windowEndTs(r: GovernanceRound): number {
  return Number(r.proposedAt) + r.challengeWindowDays * 86400;
}

function ballotStateLabel(s: number): string {
  switch (s) {
    case BallotState.Pending: return "En attente";
    case BallotState.Voting: return "Vote ouvert";
    case BallotState.Rejected: return "Rejeté";
    case BallotState.Accepted: return "Accepté";
    default: return "—";
  }
}

/* ------------------------------------------------------------------ */
/* GovernancePanel                                                     */
/* ------------------------------------------------------------------ */

export default function GovernancePanel({ rounds }: { rounds: GovernanceRound[] }) {
  const [account, setAccount] = useState<string | null>(null);
  const [chainOk, setChainOk] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [hasWallet, setHasWallet] = useState(true);

  const [disputes, setDisputes] = useState<Record<string, DisputeData>>({});
  const [ballots, setBallots] = useState<Record<string, BallotData>>({});
  const [hasVotedMap, setHasVotedMap] = useState<Record<string, boolean>>({});
  const [challengeReasons, setChallengeReasons] = useState<Record<string, string>>({});
  const [txStatus, setTxStatus] = useState<Record<string, { msg: string; ok: boolean } | null>>({});
  const [nowTs, setNowTs] = useState<number>(Math.floor(Date.now() / 1000));

  // Refresh "now" every 30s for window expiry display
  useEffect(() => {
    const id = setInterval(() => setNowTs(Math.floor(Date.now() / 1000)), 30_000);
    return () => clearInterval(id);
  }, []);

  // Wallet init
  useEffect(() => {
    setHasWallet(typeof window !== "undefined" && !!window.ethereum);
    const eth = window.ethereum;
    if (!eth?.on) return;
    const onAccounts = (...a: unknown[]) => { const accs = a[0] as string[]; setAccount(accs?.[0] ?? null); };
    const onChain = (...a: unknown[]) => setChainOk(parseInt(a[0] as string, 16) === TARGET_CHAIN_ID);
    eth.on("accountsChanged", onAccounts);
    eth.on("chainChanged", onChain);
    return () => { eth.removeListener?.("accountsChanged", onAccounts); eth.removeListener?.("chainChanged", onChain); };
  }, []);

  // Load dispute + ballot state for challenged rounds
  const loadGovernanceState = useCallback(async () => {
    if (!isGovernorDeployed()) return;
    const challengedRounds = rounds.filter(r => r.status === RoundStatus.Challenged);
    const newDisputes: Record<string, DisputeData> = {};
    const newBallots: Record<string, BallotData> = {};

    await Promise.all(challengedRounds.map(async (r) => {
      try {
        // viem returns named object for multi-output named ABI functions
        const d = await publicClient.readContract({
          address: governorAddress,
          abi: mintGovernorAbi,
          functionName: "getDispute",
          args: [r.roundHash],
        }) as unknown as readonly [bigint, bigint, bigint, Hex, boolean, boolean, Hex, readonly Hex[]];
        const dispute: DisputeData = {
          snapshot: d[0], circulating: d[1], quorumVotes: d[2],
          activeBallot: d[3], originalDecided: d[4],
          resolved: d[5], executed: d[6], queue: d[7],
        };
        newDisputes[r.roundHash] = dispute;

        const ZERO_BYTES32 = "0x0000000000000000000000000000000000000000000000000000000000000000";
        if (dispute.activeBallot && dispute.activeBallot !== ZERO_BYTES32) {
          const b = await publicClient.readContract({
            address: governorAddress,
            abi: mintGovernorAbi,
            functionName: "getBallot",
            args: [dispute.activeBallot],
          }) as unknown as readonly [Hex, boolean, bigint, bigint, bigint, bigint, number];
          newBallots[dispute.activeBallot] = {
            dispute: b[0], isOriginal: b[1],
            voteStart: b[2], voteEnd: b[3],
            forVotes: b[4], againstVotes: b[5], state: Number(b[6]),
          };
        }
      } catch { /* not deployed yet or no dispute */ }
    }));

    setDisputes(newDisputes);
    setBallots(newBallots);
  }, [rounds]);

  useEffect(() => { loadGovernanceState(); }, [loadGovernanceState]);

  // Check hasVoted when account changes
  useEffect(() => {
    if (!account || !isGovernorDeployed()) return;
    const newMap: Record<string, boolean> = {};
    Promise.all(
      Object.keys(ballots).map(async (bh) => {
        try {
          const voted = await publicClient.readContract({
            address: governorAddress,
            abi: mintGovernorAbi,
            functionName: "hasVoted",
            args: [bh as Hex, account as `0x${string}`],
          });
          newMap[bh] = voted as boolean;
        } catch { newMap[bh] = false; }
      })
    ).then(() => setHasVotedMap(newMap));
  }, [account, ballots]);

  /* ------------------------------------------------------------------ */
  /* Wallet actions                                                      */
  /* ------------------------------------------------------------------ */

  async function connect() {
    const eth = window.ethereum;
    if (!eth) { setHasWallet(false); return; }
    setConnecting(true);
    try {
      const accounts = (await eth.request({ method: "eth_requestAccounts" })) as string[];
      setAccount(accounts?.[0] ?? null);
      const cid = (await eth.request({ method: "eth_chainId" })) as string;
      setChainOk(parseInt(cid, 16) === TARGET_CHAIN_ID);
    } catch { /* user rejected */ } finally { setConnecting(false); }
  }

  async function switchNet() {
    try {
      await window.ethereum?.request({ method: "wallet_switchEthereumChain", params: [{ chainId: TARGET_HEX }] });
      setChainOk(true);
    } catch { /* not added */ }
  }

  /* ------------------------------------------------------------------ */
  /* Contract writes                                                     */
  /* ------------------------------------------------------------------ */

  async function sendTx(roundKey: Hex, calldata: Hex) {
    const eth = window.ethereum;
    if (!eth || !account) return;
    setTxStatus(s => ({ ...s, [roundKey]: { msg: "Transaction envoyée…", ok: true } }));
    try {
      await eth.request({
        method: "eth_sendTransaction",
        params: [{ from: account, to: governorAddress, data: calldata }],
      });
      setTxStatus(s => ({ ...s, [roundKey]: { msg: "Confirmée ✓ — rafraîchis dans quelques secondes.", ok: true } }));
      setTimeout(() => loadGovernanceState(), 4000);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setTxStatus(s => ({ ...s, [roundKey]: { msg: `Erreur : ${msg.slice(0, 120)}`, ok: false } }));
    }
  }

  function finalize(roundHash: Hex) {
    const data = encodeFunctionData({ abi: mintGovernorAbi, functionName: "finalize", args: [roundHash] });
    sendTx(roundHash, data);
  }

  function challenge(roundHash: Hex) {
    const reason = challengeReasons[roundHash] ?? "";
    const data = encodeFunctionData({ abi: mintGovernorAbi, functionName: "challenge", args: [roundHash, reason] });
    sendTx(roundHash, data);
  }

  function castVote(ballotHash: Hex, support: boolean) {
    const data = encodeFunctionData({ abi: mintGovernorAbi, functionName: "castVote", args: [ballotHash, support] });
    sendTx(ballotHash, data);
  }

  function resolve(ballotHash: Hex) {
    const data = encodeFunctionData({ abi: mintGovernorAbi, functionName: "resolve", args: [ballotHash] });
    sendTx(ballotHash, data);
  }

  /* ------------------------------------------------------------------ */
  /* Render                                                              */
  /* ------------------------------------------------------------------ */

  const activeRounds = rounds.filter(r =>
    r.status === RoundStatus.Proposed || r.status === RoundStatus.Challenged
  );

  return (
    <div className="space-y-6">
      {/* Wallet bar */}
      <div className="flex items-center gap-4 flex-wrap">
        {!hasWallet ? (
          <span className="text-sm text-warn font-mono">Aucun wallet détecté (install MetaMask)</span>
        ) : !account ? (
          <button
            type="button"
            onClick={connect}
            disabled={connecting}
            className="px-3 py-1.5 text-sm font-mono rounded border border-border text-muted hover:text-text hover:border-muted disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {connecting ? "Connexion…" : "Connecter le wallet"}
          </button>
        ) : !chainOk ? (
          <button
            type="button"
            onClick={switchNet}
            className="px-3 py-1.5 text-sm font-mono rounded border border-warn/60 text-warn hover:bg-warn/10"
          >
            Mauvais réseau — passer sur Arbitrum Sepolia
          </button>
        ) : (
          <span className="font-mono text-sm text-ok flex items-center gap-1.5">
            <span className="inline-block w-2 h-2 rounded-full bg-ok" />
            {shortAddress(account)}
          </span>
        )}
        <span className="text-xs text-muted font-mono">Testnet Arbitrum Sepolia — aucune valeur réelle</span>
      </div>

      {/* Round list */}
      {activeRounds.length === 0 ? (
        <div className="rounded-md border border-border bg-panel p-6 font-mono text-muted text-sm">
          Aucun round actif à gouverner. Les rounds apparaissent ici une fois proposés.
        </div>
      ) : (
        <div className="space-y-4">
          {activeRounds.map(r => {
            const winEnd = windowEndTs(r);
            const windowExpired = nowTs >= winEnd;
            const dispute = disputes[r.roundHash];
            const activeBallot = dispute?.activeBallot &&
              dispute.activeBallot !== "0x0000000000000000000000000000000000000000000000000000000000000000"
              ? dispute.activeBallot : null;
            const ballot = activeBallot ? ballots[activeBallot] : null;
            const txSt = txStatus[r.roundHash] ?? (activeBallot ? txStatus[activeBallot] : null);

            return (
              <div key={r.roundHash} className="rounded-md border border-border bg-panel p-5 space-y-3">
                {/* Header */}
                <div className="flex items-center justify-between gap-3 flex-wrap">
                  <div className="font-mono text-sm">
                    <span className="text-accent">{shortAddress(r.roundHash, 6)}</span>
                    <span className="ml-3 text-muted">proposé le {formatUtcDate(BigInt(r.proposedAt))}</span>
                  </div>
                  <span className={`text-xs font-mono px-2 py-0.5 rounded ${
                    r.status === RoundStatus.Challenged
                      ? "bg-warn/10 text-warn border border-warn/40"
                      : windowExpired
                      ? "bg-ok/10 text-ok border border-ok/40"
                      : "bg-border text-muted border border-border"
                  }`}>
                    {r.status === RoundStatus.Challenged ? "Challengé" : windowExpired ? "Finalisable" : "Proposé"}
                  </span>
                </div>

                {/* Proposed round actions */}
                {r.status === RoundStatus.Proposed && (
                  <div className="space-y-2">
                    {windowExpired ? (
                      <div className="space-y-1">
                        <p className="text-xs text-muted font-mono">
                          Fenêtre expirée le {formatUtcDate(BigInt(winEnd))}. N&apos;importe qui peut finaliser.
                        </p>
                        <button
                          type="button"
                          disabled={!account || !chainOk}
                          onClick={() => finalize(r.roundHash)}
                          className="px-3 py-1.5 text-sm font-mono rounded border border-ok/60 text-ok hover:bg-ok/10 disabled:opacity-40 disabled:cursor-not-allowed"
                        >
                          Finaliser (minter les tokens)
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <p className="text-xs text-muted font-mono">
                          Fenêtre de challenge ouverte jusqu&apos;au {formatUtcDate(BigInt(winEnd))}.
                        </p>
                        <div className="flex gap-2 items-center flex-wrap">
                          <input
                            type="text"
                            placeholder="ipfs://... (raison du challenge)"
                            value={challengeReasons[r.roundHash] ?? ""}
                            onChange={e => setChallengeReasons(s => ({ ...s, [r.roundHash]: e.target.value }))}
                            className="flex-1 min-w-[260px] px-2 py-1.5 text-xs font-mono rounded border border-border bg-bg text-text placeholder-muted"
                          />
                          <button
                            type="button"
                            disabled={!account || !chainOk || !(challengeReasons[r.roundHash]?.startsWith("ipfs://"))}
                            onClick={() => challenge(r.roundHash)}
                            className="px-3 py-1.5 text-sm font-mono rounded border border-warn/60 text-warn hover:bg-warn/10 disabled:opacity-40 disabled:cursor-not-allowed"
                          >
                            Challenger
                          </button>
                        </div>
                        <p className="text-xs text-muted font-mono">
                          Requiert d&apos;avoir du pouvoir de vote délégué à la date de proposition.
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Challenged round — dispute + ballot info */}
                {r.status === RoundStatus.Challenged && dispute && (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-2 text-xs font-mono text-muted">
                      <div>Supply circulante : <span className="text-text">{formatTokenAmount(dispute.circulating, 18)} AUG-POC</span></div>
                      <div>Quorum requis : <span className="text-text">{formatTokenAmount(dispute.quorumVotes, 18)} AUG-POC</span></div>
                      <div>Résolu : <span className="text-text">{dispute.resolved ? "Oui" : "Non"}</span></div>
                      {dispute.resolved && <div>Round exécuté : <span className="text-accent">{shortAddress(dispute.executed, 6)}</span></div>}
                    </div>

                    {ballot && (
                      <div className="border border-border rounded p-3 space-y-2">
                        <div className="flex items-center justify-between gap-2 flex-wrap">
                          <span className="text-xs font-mono font-semibold">
                            Ballot actif{ballot.isOriginal ? " (allocation originale)" : " (alternative)"}
                          </span>
                          <span className={`text-xs font-mono px-2 py-0.5 rounded border ${
                            ballot.state === BallotState.Voting
                              ? "border-accent/40 text-accent bg-accent/10"
                              : ballot.state === BallotState.Accepted
                              ? "border-ok/40 text-ok bg-ok/10"
                              : ballot.state === BallotState.Rejected
                              ? "border-warn/40 text-warn bg-warn/10"
                              : "border-border text-muted"
                          }`}>
                            {ballotStateLabel(ballot.state)}
                          </span>
                        </div>

                        <div className="grid grid-cols-3 gap-2 text-xs font-mono text-muted">
                          <div>Pour : <span className="text-ok">{formatTokenAmount(ballot.forVotes, 18)}</span></div>
                          <div>Contre : <span className="text-warn">{formatTokenAmount(ballot.againstVotes, 18)}</span></div>
                          <div>Fin vote : <span className="text-text">{formatUtcDate(ballot.voteEnd)}</span></div>
                        </div>

                        {/* Progress bar */}
                        {(ballot.forVotes + ballot.againstVotes) > 0n && (
                          <div className="w-full h-1.5 bg-border rounded overflow-hidden">
                            <div
                              className="h-full bg-ok"
                              style={{ width: `${Number((ballot.forVotes * 100n) / (ballot.forVotes + ballot.againstVotes))}%` }}
                            />
                          </div>
                        )}

                        {/* Vote actions */}
                        {ballot.state === BallotState.Voting && nowTs < Number(ballot.voteEnd) && (
                          <div className="flex gap-2 items-center flex-wrap pt-1">
                            {hasVotedMap[activeBallot!] ? (
                              <span className="text-xs text-muted font-mono">Déjà voté sur ce ballot.</span>
                            ) : (
                              <>
                                <button
                                  type="button"
                                  disabled={!account || !chainOk}
                                  onClick={() => castVote(activeBallot!, true)}
                                  className="px-3 py-1.5 text-sm font-mono rounded border border-ok/60 text-ok hover:bg-ok/10 disabled:opacity-40 disabled:cursor-not-allowed"
                                >
                                  Voter POUR
                                </button>
                                <button
                                  type="button"
                                  disabled={!account || !chainOk}
                                  onClick={() => castVote(activeBallot!, false)}
                                  className="px-3 py-1.5 text-sm font-mono rounded border border-warn/60 text-warn hover:bg-warn/10 disabled:opacity-40 disabled:cursor-not-allowed"
                                >
                                  Voter CONTRE
                                </button>
                              </>
                            )}
                          </div>
                        )}

                        {/* Resolve action */}
                        {ballot.state === BallotState.Voting && nowTs >= Number(ballot.voteEnd) && (
                          <div className="pt-1 space-y-1">
                            <p className="text-xs text-muted font-mono">
                              Vote terminé. Taler le résultat pour minter (si maintenu) ou ouvrir la re-proposition.
                            </p>
                            <button
                              type="button"
                              disabled={!account || !chainOk}
                              onClick={() => resolve(activeBallot!)}
                              className="px-3 py-1.5 text-sm font-mono rounded border border-accent/60 text-accent hover:bg-accent/10 disabled:opacity-40 disabled:cursor-not-allowed"
                            >
                              Résoudre le ballot
                            </button>
                          </div>
                        )}
                      </div>
                    )}

                    {/* No active ballot, not resolved */}
                    {!activeBallot && !dispute.resolved && dispute.originalDecided && (
                      <p className="text-xs text-muted font-mono">
                        L&apos;allocation originale a été rejetée. En attente d&apos;une alternative (
                        proposer via <code>governor.proposeAlternative()</code>).
                      </p>
                    )}
                  </div>
                )}

                {/* TX status */}
                {txSt && (
                  <p className={`text-xs font-mono ${txSt.ok ? "text-ok" : "text-warn"}`}>
                    {txSt.msg}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Refresh button */}
      {isGovernorDeployed() && (
        <button
          type="button"
          onClick={() => loadGovernanceState()}
          className="text-xs font-mono text-muted hover:text-text border border-border px-3 py-1 rounded"
        >
          Rafraîchir l&apos;état on-chain
        </button>
      )}
    </div>
  );
}
