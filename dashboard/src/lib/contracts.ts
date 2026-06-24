/**
 * Contract addresses (from env) and TypeScript-native ABIs for the read-only
 * surface the dashboard consumes. We hand-write the ABIs (rather than dump the
 * full Foundry artefacts) so they stay tight, fully typed by viem, and free of
 * irrelevant constructor / write functions.
 */

import { type Address } from "viem";

const ZERO = "0x0000000000000000000000000000000000000000";
const TOKEN_ADDRESS_RAW    = process.env.NEXT_PUBLIC_TOKEN_ADDRESS as `0x${string}` | undefined;
const REGISTRY_ADDRESS_RAW = process.env.NEXT_PUBLIC_REGISTRY_ADDRESS as `0x${string}` | undefined;
const GOVERNOR_ADDRESS_RAW = process.env.NEXT_PUBLIC_GOVERNOR_ADDRESS as `0x${string}` | undefined;

// Phase 3 — parametric insurance contracts
const POLICY_REGISTRY_ADDRESS_RAW = process.env.NEXT_PUBLIC_POLICY_REGISTRY_ADDRESS as `0x${string}` | undefined;
const PREMIUM_POOL_ADDRESS_RAW    = process.env.NEXT_PUBLIC_PREMIUM_POOL_ADDRESS    as `0x${string}` | undefined;
const PRICING_ENGINE_ADDRESS_RAW  = process.env.NEXT_PUBLIC_PRICING_ENGINE_ADDRESS  as `0x${string}` | undefined;

export const tokenAddress:         Address = (TOKEN_ADDRESS_RAW    || ZERO) as Address;
export const registryAddress:      Address = (REGISTRY_ADDRESS_RAW || ZERO) as Address;
export const governorAddress:      Address = (GOVERNOR_ADDRESS_RAW || ZERO) as Address;
export const policyRegistryAddress: Address = (POLICY_REGISTRY_ADDRESS_RAW || ZERO) as Address;
export const premiumPoolAddress:    Address = (PREMIUM_POOL_ADDRESS_RAW    || ZERO) as Address;
export const pricingEngineAddress:  Address = (PRICING_ENGINE_ADDRESS_RAW  || ZERO) as Address;

export const deployBlock: bigint = BigInt(process.env.NEXT_PUBLIC_DEPLOY_BLOCK || "0");

export function isDeployed(): boolean {
  return tokenAddress.toLowerCase() !== ZERO && registryAddress.toLowerCase() !== ZERO;
}

export function isGovernorDeployed(): boolean {
  return governorAddress.toLowerCase() !== ZERO;
}

export function isPremiumPoolDeployed(): boolean {
  return premiumPoolAddress.toLowerCase() !== ZERO;
}

/* ------------------------------------------------------------------ */
/* AugPocToken — read-only surface                                    */
/* ------------------------------------------------------------------ */

export const augPocTokenAbi = [
  {
    type: "function",
    name: "name",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "string" }],
  },
  {
    type: "function",
    name: "symbol",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "string" }],
  },
  {
    type: "function",
    name: "decimals",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint8" }],
  },
  {
    type: "function",
    name: "totalSupply",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "paused",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "bool" }],
  },
  {
    type: "function",
    name: "MINTER_ROLE",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "bytes32" }],
  },
  {
    type: "function",
    name: "PAUSER_ROLE",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "bytes32" }],
  },
  {
    type: "function",
    name: "BURNER_ROLE",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "bytes32" }],
  },
  {
    type: "function",
    name: "hasRole",
    stateMutability: "view",
    inputs: [
      { name: "role", type: "bytes32" },
      { name: "account", type: "address" },
    ],
    outputs: [{ type: "bool" }],
  },
] as const;

/* ------------------------------------------------------------------ */
/* RoundRegistry — read-only surface                                  */
/* ------------------------------------------------------------------ */

export const roundRegistryAbi = [
  {
    type: "function",
    name: "statusOf",
    stateMutability: "view",
    inputs: [{ name: "roundHash", type: "bytes32" }],
    outputs: [{ type: "uint8" }],
  },
  {
    type: "function",
    name: "getRound",
    stateMutability: "view",
    inputs: [{ name: "roundHash", type: "bytes32" }],
    outputs: [
      { name: "ipfsUri", type: "string" },
      { name: "proposedAt", type: "uint64" },
      { name: "challengeWindowDays", type: "uint32" },
      { name: "status", type: "uint8" },
    ],
  },
  {
    type: "function",
    name: "getRoundBeneficiaries",
    stateMutability: "view",
    inputs: [{ name: "roundHash", type: "bytes32" }],
    outputs: [{ type: "address[]" }],
  },
  {
    type: "function",
    name: "getRoundAmounts",
    stateMutability: "view",
    inputs: [{ name: "roundHash", type: "bytes32" }],
    outputs: [{ type: "uint256[]" }],
  },
  {
    type: "function",
    name: "windowEndOf",
    stateMutability: "view",
    inputs: [{ name: "roundHash", type: "bytes32" }],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "token",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "address" }],
  },
  /* Events the dashboard subscribes to */
  {
    type: "event",
    name: "RoundProposed",
    inputs: [
      { name: "roundHash", type: "bytes32", indexed: true },
      { name: "ipfsUri", type: "string", indexed: false },
      { name: "proposedAt", type: "uint64", indexed: false },
      { name: "challengeWindowDays", type: "uint32", indexed: false },
      { name: "beneficiaries", type: "address[]", indexed: false },
      { name: "amounts", type: "uint256[]", indexed: false },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "RoundChallenged",
    inputs: [
      { name: "roundHash", type: "bytes32", indexed: true },
      { name: "challenger", type: "address", indexed: true },
      { name: "reasonIpfsUri", type: "string", indexed: false },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "RoundExecuted",
    inputs: [
      { name: "roundHash", type: "bytes32", indexed: true },
      { name: "executedAt", type: "uint64", indexed: false },
      { name: "totalMinted", type: "uint256", indexed: false },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "RoundCancelled",
    inputs: [
      { name: "roundHash", type: "bytes32", indexed: true },
      { name: "canceller", type: "address", indexed: true },
      { name: "reasonIpfsUri", type: "string", indexed: false },
    ],
    anonymous: false,
  },
] as const;

/* ------------------------------------------------------------------ */
/* Round status enum (matches IRoundRegistry.RoundStatus)             */
/* ------------------------------------------------------------------ */

export enum RoundStatus {
  None = 0,
  Proposed = 1,
  Challenged = 2,
  Executed = 3,
  Cancelled = 4,
}

export const roundStatusLabel: Record<RoundStatus, string> = {
  [RoundStatus.None]: "None",
  [RoundStatus.Proposed]: "Proposed",
  [RoundStatus.Challenged]: "Challenged",
  [RoundStatus.Executed]: "Executed",
  [RoundStatus.Cancelled]: "Cancelled",
};

/* ------------------------------------------------------------------ */
/* MintGovernor — governance surface (Phase 2)                        */
/* ------------------------------------------------------------------ */

export enum BallotState {
  None = 0,
  Pending = 1,
  Voting = 2,
  Rejected = 3,
  Accepted = 4,
}

export const mintGovernorAbi = [
  /* Views */
  {
    type: "function",
    name: "getDispute",
    stateMutability: "view",
    inputs: [{ name: "originalRound", type: "bytes32" }],
    outputs: [
      { name: "snapshot", type: "uint64" },
      { name: "circulating", type: "uint256" },
      { name: "quorumVotes", type: "uint256" },
      { name: "activeBallot", type: "bytes32" },
      { name: "originalDecided", type: "bool" },
      { name: "resolved", type: "bool" },
      { name: "executed", type: "bytes32" },
      { name: "queue", type: "bytes32[]" },
    ],
  },
  {
    type: "function",
    name: "getBallot",
    stateMutability: "view",
    inputs: [{ name: "ballotRound", type: "bytes32" }],
    outputs: [
      { name: "dispute", type: "bytes32" },
      { name: "isOriginal", type: "bool" },
      { name: "voteStart", type: "uint64" },
      { name: "voteEnd", type: "uint64" },
      { name: "forVotes", type: "uint256" },
      { name: "againstVotes", type: "uint256" },
      { name: "state", type: "uint8" },
    ],
  },
  {
    type: "function",
    name: "hasVoted",
    stateMutability: "view",
    inputs: [
      { name: "ballotRound", type: "bytes32" },
      { name: "voter", type: "address" },
    ],
    outputs: [{ type: "bool" }],
  },
  {
    type: "function",
    name: "quorumBps",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint16" }],
  },
  {
    type: "function",
    name: "voteDurationDays",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint32" }],
  },
  /* Writes */
  {
    type: "function",
    name: "finalize",
    stateMutability: "nonpayable",
    inputs: [{ name: "roundHash", type: "bytes32" }],
    outputs: [],
  },
  {
    type: "function",
    name: "challenge",
    stateMutability: "nonpayable",
    inputs: [
      { name: "roundHash", type: "bytes32" },
      { name: "reasonIpfsUri", type: "string" },
    ],
    outputs: [],
  },
  {
    type: "function",
    name: "castVote",
    stateMutability: "nonpayable",
    inputs: [
      { name: "ballotRound", type: "bytes32" },
      { name: "support", type: "bool" },
    ],
    outputs: [],
  },
  {
    type: "function",
    name: "resolve",
    stateMutability: "nonpayable",
    inputs: [{ name: "ballotRound", type: "bytes32" }],
    outputs: [],
  },
  /* Events */
  {
    type: "event",
    name: "RoundFinalized",
    inputs: [{ name: "roundHash", type: "bytes32", indexed: true }],
    anonymous: false,
  },
  {
    type: "event",
    name: "DisputeOpened",
    inputs: [
      { name: "originalRound", type: "bytes32", indexed: true },
      { name: "challenger", type: "address", indexed: true },
      { name: "snapshot", type: "uint64", indexed: false },
      { name: "quorumVotes", type: "uint256", indexed: false },
      { name: "voteEnd", type: "uint64", indexed: false },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "VoteCast",
    inputs: [
      { name: "ballotRound", type: "bytes32", indexed: true },
      { name: "voter", type: "address", indexed: true },
      { name: "support", type: "bool", indexed: false },
      { name: "weight", type: "uint256", indexed: false },
    ],
    anonymous: false,
  },
  {
    type: "event",
    name: "DisputeResolved",
    inputs: [
      { name: "originalRound", type: "bytes32", indexed: true },
      { name: "executedRound", type: "bytes32", indexed: true },
    ],
    anonymous: false,
  },
] as const;

/* ------------------------------------------------------------------ */
/* PremiumPool — read-only surface (Phase 3)                          */
/* ------------------------------------------------------------------ */

export const premiumPoolAbi = [
  {
    type: "function",
    name: "availableCapital",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "totalCapital",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "totalReserved",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "mcrFloor",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "isSolvent",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "bool" }],
  },
  {
    type: "function",
    name: "annualPremiumsCollected",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
  {
    type: "function",
    name: "MCR_FLOOR_USDC",
    stateMutability: "view",
    inputs: [],
    outputs: [{ type: "uint256" }],
  },
] as const;
