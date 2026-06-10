/**
 * Formatting helpers for the dashboard. Pure functions, no side effects.
 */

import { formatUnits } from "viem";

/** Token amount in wei → human-readable string, with thousand separators. */
export function formatTokenAmount(wei: bigint, decimals = 18, maxFractionDigits = 4): string {
  const raw = formatUnits(wei, decimals);
  const [intPart, fracPart] = raw.split(".");
  const intFormatted = Number(intPart).toLocaleString("en-US");
  if (!fracPart || fracPart === "0") return intFormatted;
  const trimmed = fracPart.replace(/0+$/, "").slice(0, maxFractionDigits);
  return trimmed ? `${intFormatted}.${trimmed}` : intFormatted;
}

/** Percentage of total, formatted with at most 2 fraction digits. */
export function formatPercent(numerator: bigint, denominator: bigint): string {
  if (denominator === 0n) return "—";
  const bps = Number((numerator * 10_000n) / denominator);
  return `${(bps / 100).toFixed(2)}%`;
}

/** Shorten a 0x-prefixed hex string to `0xabcd…1234`. */
export function shortAddress(addr: string, chars = 4): string {
  if (!addr || addr.length < 10) return addr;
  return `${addr.slice(0, 2 + chars)}…${addr.slice(-chars)}`;
}

/** Unix seconds → ISO date string in UTC. */
export function formatUtcDate(unixSeconds: bigint | number): string {
  const ms = Number(unixSeconds) * 1000;
  const d = new Date(ms);
  return d.toISOString().replace("T", " ").slice(0, 19) + " UTC";
}

/** Human-readable countdown to a target unix timestamp. */
export function formatCountdown(targetUnixSeconds: bigint | number, nowSeconds: number): string {
  const target = Number(targetUnixSeconds);
  const remaining = target - nowSeconds;
  if (remaining <= 0) return "expired";
  const days = Math.floor(remaining / 86_400);
  const hours = Math.floor((remaining % 86_400) / 3600);
  const mins = Math.floor((remaining % 3600) / 60);
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${mins}m`;
  return `${mins}m`;
}

/**
 * Convert an `ipfs://` URI to a public HTTP gateway URL, or pass through an
 * `https://` URL. ANY other scheme (`javascript:`, `data:`, `http:`, `vbscript:`,
 * …) returns `""` so the caller renders plain text instead of a clickable href.
 *
 * The URI comes from on-chain round data and is therefore untrusted: rendering it
 * directly in an `href` allowed `javascript:`-style XSS (revue 2026-06-10 C1).
 * The `ipfs.io` gateway replaces the decommissioned `cloudflare-ipfs.com`.
 */
export function ipfsHttpUrl(ipfsUri: string): string {
  if (!ipfsUri) return "";
  if (ipfsUri.startsWith("ipfs://")) {
    const cid = ipfsUri.slice("ipfs://".length);
    return `https://ipfs.io/ipfs/${cid}`;
  }
  if (ipfsUri.startsWith("https://")) {
    return ipfsUri;
  }
  return "";
}

