import { getDict } from "@/lib/i18n";
import {
  isDeployed,
  isPremiumPoolDeployed,
  premiumPoolAddress,
  pricingEngineAddress,
  policyRegistryAddress,
  premiumPoolAbi,
} from "@/lib/contracts";
import { publicClient, explorerAddressUrl } from "@/lib/chain";
import { formatUnits } from "viem";

export const dynamic = "force-dynamic";

interface PoolMetrics {
  availableCapital: bigint;
  mcrFloor: bigint;
  totalCapital: bigint;
  isSolvent: boolean;
}

async function fetchPoolMetrics(): Promise<PoolMetrics | null> {
  if (!isPremiumPoolDeployed()) return null;
  try {
    const [available, floor, total, solvent] = await Promise.all([
      publicClient.readContract({ address: premiumPoolAddress, abi: premiumPoolAbi, functionName: "availableCapital" }),
      publicClient.readContract({ address: premiumPoolAddress, abi: premiumPoolAbi, functionName: "mcrFloor" }),
      publicClient.readContract({ address: premiumPoolAddress, abi: premiumPoolAbi, functionName: "totalCapital" }),
      publicClient.readContract({ address: premiumPoolAddress, abi: premiumPoolAbi, functionName: "isSolvent" }),
    ]);
    return { availableCapital: available, mcrFloor: floor, totalCapital: total, isSolvent: solvent };
  } catch {
    return null;
  }
}

function fmt(usdc: bigint): string {
  return Number(formatUnits(usdc, 6)).toLocaleString("fr-FR", { maximumFractionDigits: 2 });
}

function SolvencyBar({ available, floor }: { available: bigint; floor: bigint }) {
  const ratio = floor === 0n ? 200 : Math.min(Number((available * 200n) / floor), 200);
  const pct = Math.min(ratio, 100);
  const color = ratio >= 150 ? "bg-success" : ratio >= 100 ? "bg-warn" : "bg-error";
  return (
    <div className="w-full bg-border rounded h-2 mt-1">
      <div className={`h-2 rounded ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export default async function InsurancePage() {
  const dict = await getDict();

  if (!isDeployed()) {
    return (
      <div className="rounded-md border border-warn/40 bg-warn/10 p-6 font-mono">
        <h1 className="text-xl mb-2 text-warn">{dict.common.not_deployed_title}</h1>
        <p className="text-sm text-muted">{dict.common.not_deployed_body}</p>
      </div>
    );
  }

  const pool = await fetchPoolMetrics();
  const ratio = pool && pool.mcrFloor > 0n
    ? Number((pool.availableCapital * 100n) / pool.mcrFloor)
    : null;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-mono font-semibold mb-2">
          Assurance paramétrique — Phase 3
        </h1>
        <p className="text-sm text-muted max-w-2xl">
          Polices météo automatiques : payer une prime pour être indemnisé si la
          température franchit un seuil le jour cible. Pas d&apos;expertise ni de
          déclaration — le règlement est déclenché automatiquement par l&apos;oracle
          on-chain (Reclaim Protocol).
        </p>
      </div>

      {/* Pool status */}
      {!isPremiumPoolDeployed() ? (
        <div className="rounded-md border border-warn/40 bg-warn/10 p-4 font-mono text-sm">
          <p className="text-warn font-semibold mb-1">PremiumPool non déployé</p>
          <p className="text-muted">
            Lance <code>DeployPhase3.s.sol</code> et définis{" "}
            <code>NEXT_PUBLIC_PREMIUM_POOL_ADDRESS</code> pour voir l&apos;état de la réserve.
          </p>
        </div>
      ) : pool ? (
        <section className="space-y-4">
          <h2 className="text-lg font-mono font-semibold">Réserves de l&apos;association</h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-md border border-border p-4">
              <p className="text-xs text-muted mb-1">Capital disponible</p>
              <p className="text-xl font-mono font-semibold">{fmt(pool.availableCapital)}</p>
              <p className="text-xs text-muted">USDC</p>
            </div>
            <div className="rounded-md border border-border p-4">
              <p className="text-xs text-muted mb-1">Plancher MCR</p>
              <p className="text-xl font-mono font-semibold">{fmt(pool.mcrFloor)}</p>
              <p className="text-xs text-muted">USDC (Art. R334-6 CA)</p>
            </div>
            <div className="rounded-md border border-border p-4">
              <p className="text-xs text-muted mb-1">Capital total</p>
              <p className="text-xl font-mono font-semibold">{fmt(pool.totalCapital)}</p>
              <p className="text-xs text-muted">USDC (dispo + réservé)</p>
            </div>
            <div className="rounded-md border border-border p-4">
              <p className="text-xs text-muted mb-1">Ratio solvabilité</p>
              <p className={`text-xl font-mono font-semibold ${pool.isSolvent ? "text-success" : "text-error"}`}>
                {ratio !== null ? `${ratio}%` : "—"}
              </p>
              <p className="text-xs text-muted">{pool.isSolvent ? "solvable" : "sous plancher MCR"}</p>
              {ratio !== null && pool.mcrFloor > 0n && (
                <SolvencyBar available={pool.availableCapital} floor={pool.mcrFloor} />
              )}
            </div>
          </div>
        </section>
      ) : (
        <p className="text-sm text-muted">Impossible de lire les données du pool.</p>
      )}

      {/* Contrats */}
      <section className="space-y-2">
        <h2 className="text-lg font-mono font-semibold">Contrats Phase 3</h2>
        <div className="font-mono text-sm space-y-1">
          {[
            { label: "PolicyRegistry", address: policyRegistryAddress },
            { label: "PremiumPool", address: premiumPoolAddress },
            { label: "PricingEngine", address: pricingEngineAddress },
          ].map(({ label, address }) => (
            address.toLowerCase() !== "0x0000000000000000000000000000000000000000" ? (
              <div key={label} className="flex gap-3 items-center">
                <span className="text-muted w-36">{label}</span>
                <a
                  href={explorerAddressUrl(address)}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="text-accent hover:underline truncate"
                >
                  {address}
                </a>
              </div>
            ) : (
              <div key={label} className="flex gap-3 items-center">
                <span className="text-muted w-36">{label}</span>
                <span className="text-muted text-xs">non déployé</span>
              </div>
            )
          ))}
        </div>
      </section>

      {/* Comment souscrire */}
      <section className="rounded-md border border-border p-6 space-y-3">
        <h2 className="text-lg font-mono font-semibold">Comment souscrire une police</h2>
        <ol className="text-sm space-y-2 text-muted list-decimal list-inside">
          <li>
            Obtenir une estimation de prime via{" "}
            <code className="text-text">PolicyRegistry.quotePolicy(locationKey, targetDate, sumAssured, threshold, pBps)</code>.
          </li>
          <li>
            Approuver le transfer USDC :{" "}
            <code className="text-text">usdc.approve(policyRegistryAddress, premium)</code>.
          </li>
          <li>
            Souscrire :{" "}
            <code className="text-text">PolicyRegistry.subscribe(locationKey, targetDate, sumAssured, threshold, pBps)</code>.
          </li>
          <li>
            Le keeper règle la police après la date cible si l&apos;oracle a posté un résultat.
            Payout automatique si <code className="text-text">observedTempF &ge; threshold</code>.
          </li>
        </ol>
        <p className="text-xs text-muted mt-2">
          Seuils disponibles : KXHIGHTSFO (San Francisco max), KXLOWTCHI (Chicago min),
          KXLOWTNYC (New York min), KXLOWTMIA (Miami min), et plus (voir{" "}
          <code>predictor/scripts/resolution.py</code>).
        </p>
      </section>
    </div>
  );
}
