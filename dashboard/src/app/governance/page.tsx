import GovernancePanel, { type GovernanceRound } from "@/components/GovernancePanel";
import { isDeployed, isGovernorDeployed, RoundStatus } from "@/lib/contracts";
import { getDict } from "@/lib/i18n";
import { fetchAllRounds } from "@/lib/rounds";

export const dynamic = "force-dynamic";

export default async function GovernancePage() {
  const dict = await getDict();

  if (!isDeployed()) {
    return (
      <div className="rounded-md border border-warn/40 bg-warn/10 p-6 font-mono">
        <h1 className="text-xl mb-2 text-warn">{dict.common.not_deployed_title}</h1>
        <p className="text-sm text-muted">{dict.common.not_deployed_body}</p>
      </div>
    );
  }

  // Fetch all rounds; filter to active ones (Proposed + Challenged)
  const allRounds = await fetchAllRounds();
  const activeRounds: GovernanceRound[] = allRounds
    .filter(r => r.status === RoundStatus.Proposed || r.status === RoundStatus.Challenged)
    .map(r => ({
      roundHash: r.roundHash,
      status: r.status,
      proposedAt: r.proposedAt.toString(),
      challengeWindowDays: r.challengeWindowDays,
    }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-mono font-semibold mb-2">
          Gouvernance DAO
        </h1>
        <p className="text-sm text-muted max-w-2xl">
          Proposer, challenger et voter sur les rounds de mint mensuel. Le flux
          nominal : keeper propose → fenêtre de challenge → finalisation automatique.
          En cas de contestation : vote token-weighted, résolution, puis mint ou
          re-proposition.
        </p>

        {!isGovernorDeployed() && (
          <div className="mt-4 rounded-md border border-warn/40 bg-warn/10 p-4 font-mono text-sm">
            <p className="text-warn font-semibold mb-1">MintGovernor non déployé</p>
            <p className="text-muted">
              Lance <code>DeployPhase2Governor.s.sol</code> et définis{" "}
              <code>NEXT_PUBLIC_GOVERNOR_ADDRESS</code> pour activer les actions de gouvernance.
              Voir <code>contracts/docs/RUNBOOK-DEPLOIEMENT-PHASE2.fr.md</code>.
            </p>
          </div>
        )}
      </div>

      <GovernancePanel rounds={activeRounds} />
    </div>
  );
}
