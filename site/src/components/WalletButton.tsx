"use client";

import { useEffect, useState } from "react";
import { shortAddress } from "@/lib/format";

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

export default function WalletButton({
  labels,
}: {
  labels: { connect: string; connecting: string; wrongNet: string; switch: string; disconnect: string; noWallet: string };
}) {
  const [address, setAddress] = useState<string | null>(null);
  const [chainOk, setChainOk] = useState(true);
  const [busy, setBusy] = useState(false);
  const [hasWallet, setHasWallet] = useState(true);

  useEffect(() => {
    setHasWallet(typeof window !== "undefined" && !!window.ethereum);
    const eth = window.ethereum;
    if (!eth?.on) return;
    const onAccounts = (...a: unknown[]) => {
      const accs = a[0] as string[];
      setAddress(accs?.[0] ?? null);
    };
    const onChain = (...a: unknown[]) => setChainOk(parseInt(a[0] as string, 16) === TARGET_CHAIN_ID);
    eth.on("accountsChanged", onAccounts);
    eth.on("chainChanged", onChain);
    return () => {
      eth.removeListener?.("accountsChanged", onAccounts);
      eth.removeListener?.("chainChanged", onChain);
    };
  }, []);

  async function connect() {
    const eth = window.ethereum;
    if (!eth) {
      setHasWallet(false);
      return;
    }
    setBusy(true);
    try {
      const accounts = (await eth.request({ method: "eth_requestAccounts" })) as string[];
      setAddress(accounts?.[0] ?? null);
      const cid = (await eth.request({ method: "eth_chainId" })) as string;
      setChainOk(parseInt(cid, 16) === TARGET_CHAIN_ID);
    } catch {
      /* user rejected */
    } finally {
      setBusy(false);
    }
  }

  async function switchNet() {
    const eth = window.ethereum;
    if (!eth) return;
    try {
      await eth.request({ method: "wallet_switchEthereumChain", params: [{ chainId: TARGET_HEX }] });
      setChainOk(true);
    } catch {
      /* chain not added / rejected */
    }
  }

  if (!hasWallet) {
    return <span className="wallet-pill wallet-muted" title={labels.noWallet}>{labels.noWallet}</span>;
  }

  if (address && !chainOk) {
    return (
      <button type="button" className="btn-wallet warn" onClick={switchNet}>
        {labels.switch}
      </button>
    );
  }

  if (address) {
    return (
      <button type="button" className="btn-wallet ok" onClick={() => setAddress(null)} title={labels.disconnect}>
        <span className="wdot" /> {shortAddress(address)}
      </button>
    );
  }

  return (
    <button type="button" className="btn-wallet" onClick={connect} disabled={busy}>
      {busy ? labels.connecting : labels.connect}
    </button>
  );
}
