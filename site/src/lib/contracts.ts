import { type Address } from "viem";

const TOKEN_RAW = process.env.NEXT_PUBLIC_TOKEN_ADDRESS as `0x${string}` | undefined;
const REGISTRY_RAW = process.env.NEXT_PUBLIC_REGISTRY_ADDRESS as `0x${string}` | undefined;
const ZERO = "0x0000000000000000000000000000000000000000";

export const tokenAddress: Address = (TOKEN_RAW || ZERO) as Address;
export const registryAddress: Address = (REGISTRY_RAW || ZERO) as Address;

export function isDeployed(): boolean {
  return (
    tokenAddress.toLowerCase() !== ZERO &&
    registryAddress.toLowerCase() !== ZERO
  );
}

/** AugPocToken — minimal read-only surface the landing needs. */
export const augPocTokenAbi = [
  { type: "function", name: "name", stateMutability: "view", inputs: [], outputs: [{ type: "string" }] },
  { type: "function", name: "symbol", stateMutability: "view", inputs: [], outputs: [{ type: "string" }] },
  { type: "function", name: "decimals", stateMutability: "view", inputs: [], outputs: [{ type: "uint8" }] },
  { type: "function", name: "totalSupply", stateMutability: "view", inputs: [], outputs: [{ type: "uint256" }] },
  { type: "function", name: "paused", stateMutability: "view", inputs: [], outputs: [{ type: "bool" }] },
] as const;
