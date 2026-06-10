/**
 * Read all rounds known to the registry by scanning the four lifecycle events
 * (RoundProposed / Challenged / Executed / Cancelled) from `deployBlock` to
 * the current head. Folds them into one record per roundHash with the latest
 * status. Pure read-only — never broadcasts.
 */

import { unstable_cache } from "next/cache";
import { type Address, type Hex } from "viem";

import { publicClient } from "./chain";
import { deployBlock, registryAddress, roundRegistryAbi, RoundStatus } from "./contracts";

export interface RoundSummary {
  roundHash: Hex;
  ipfsUri: string;
  proposedAt: bigint;
  challengeWindowDays: number;
  status: RoundStatus;
  beneficiaries: readonly Address[];
  amounts: readonly bigint[];
  totalAmount: bigint;
  /** Block number of the most recent on-chain event for this round. */
  lastEventBlock: bigint;
}

/**
 * Internal RPC scan (4 full-range getContractEvents). Wrapped by the cached
 * `fetchAllRounds` below — do not call directly from pages.
 */
async function _scanAllRounds(): Promise<RoundSummary[]> {
  const proposedLogs = await publicClient.getContractEvents({
    address: registryAddress,
    abi: roundRegistryAbi,
    eventName: "RoundProposed",
    fromBlock: deployBlock,
    toBlock: "latest",
  });

  const challengedLogs = await publicClient.getContractEvents({
    address: registryAddress,
    abi: roundRegistryAbi,
    eventName: "RoundChallenged",
    fromBlock: deployBlock,
    toBlock: "latest",
  });

  const executedLogs = await publicClient.getContractEvents({
    address: registryAddress,
    abi: roundRegistryAbi,
    eventName: "RoundExecuted",
    fromBlock: deployBlock,
    toBlock: "latest",
  });

  const cancelledLogs = await publicClient.getContractEvents({
    address: registryAddress,
    abi: roundRegistryAbi,
    eventName: "RoundCancelled",
    fromBlock: deployBlock,
    toBlock: "latest",
  });

  const rounds = new Map<Hex, RoundSummary>();

  for (const log of proposedLogs) {
    if (!log.args.roundHash) continue;
    const ben = (log.args.beneficiaries ?? []) as readonly Address[];
    const amts = (log.args.amounts ?? []) as readonly bigint[];
    const total = amts.reduce((acc, a) => acc + a, 0n);
    rounds.set(log.args.roundHash, {
      roundHash: log.args.roundHash,
      ipfsUri: log.args.ipfsUri ?? "",
      proposedAt: log.args.proposedAt ?? 0n,
      challengeWindowDays: Number(log.args.challengeWindowDays ?? 0),
      status: RoundStatus.Proposed,
      beneficiaries: ben,
      amounts: amts,
      totalAmount: total,
      lastEventBlock: log.blockNumber ?? 0n,
    });
  }

  // Apply later events in chronological order so the final status is correct.
  const laterEvents = [
    ...challengedLogs.map((l) => ({ log: l, status: RoundStatus.Challenged })),
    ...executedLogs.map((l) => ({ log: l, status: RoundStatus.Executed })),
    ...cancelledLogs.map((l) => ({ log: l, status: RoundStatus.Cancelled })),
  ].sort((a, b) => Number((a.log.blockNumber ?? 0n) - (b.log.blockNumber ?? 0n)));

  for (const { log, status } of laterEvents) {
    const hash = (log.args as { roundHash?: Hex }).roundHash;
    if (!hash) continue;
    const existing = rounds.get(hash);
    if (!existing) continue;
    existing.status = status;
    existing.lastEventBlock = log.blockNumber ?? existing.lastEventBlock;
  }

  return Array.from(rounds.values()).sort((a, b) => Number(b.proposedAt - a.proposedAt));
}

/**
 * JSON-serializable mirror of RoundSummary: every bigint is a decimal string.
 * Next's Data Cache (unstable_cache) can't serialize BigInt, so the cached
 * scan stores this shape and `fetchAllRounds` revives it (revue 2026-06-10 C3).
 */
type SerializableRound = Omit<
  RoundSummary,
  "proposedAt" | "amounts" | "totalAmount" | "lastEventBlock"
> & {
  proposedAt: string;
  amounts: readonly string[];
  totalAmount: string;
  lastEventBlock: string;
};

/**
 * Cached RPC scan. The 4 full-range eth_getLogs are the shortest path to a
 * dashboard outage (RPC quota) — every page render did them uncached. We cache
 * the result for 60 s (revue C3); bigints are stringified for the Data Cache.
 */
const _fetchAllRoundsCached = unstable_cache(
  async (): Promise<SerializableRound[]> => {
    const rounds = await _scanAllRounds();
    return rounds.map((r) => ({
      ...r,
      proposedAt: r.proposedAt.toString(),
      amounts: r.amounts.map((a) => a.toString()),
      totalAmount: r.totalAmount.toString(),
      lastEventBlock: r.lastEventBlock.toString(),
    }));
  },
  ["aratea:all-rounds"],
  { revalidate: 60 },
);

/**
 * Fetch every round committed to the registry, sorted by proposedAt descending
 * (most recent first). Backed by a 60 s cache so concurrent requests share one
 * RPC scan. Best-effort: any round whose Proposed event we can't decode is
 * silently skipped.
 */
export async function fetchAllRounds(): Promise<RoundSummary[]> {
  const cached = await _fetchAllRoundsCached();
  return cached.map((r) => ({
    ...r,
    proposedAt: BigInt(r.proposedAt),
    amounts: r.amounts.map((a) => BigInt(a)),
    totalAmount: BigInt(r.totalAmount),
    lastEventBlock: BigInt(r.lastEventBlock),
  }));
}

/**
 * Compute when the challenge window of a round closes.
 */
export function windowEnd(round: RoundSummary): bigint {
  return round.proposedAt + BigInt(round.challengeWindowDays) * 86_400n;
}
