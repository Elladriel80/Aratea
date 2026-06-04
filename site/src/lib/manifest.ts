/**
 * Live predictor data. The deployed dashboard serves the canonical manifest at
 * /predictor_manifest.json — we fetch it here with ISR so the landing stays in
 * sync automatically without ever re-editing the site.
 */

export interface PaperBetsSummary {
  n_open: number;
  n_resolved: number;
  pnl_usd_cumulative: number;
  phase_1_counter: string;
}

export interface RunRecord {
  ts: string;
  feature_set: string;
  brier_test: number | null;
  brier_kalshi_mid_test: number | null;
  gap_vs_kalshi_mid: number | null;
  verdict: string;
}

export interface PredictorManifest {
  generated_at: string;
  schema_version: number;
  paper_bets_summary?: PaperBetsSummary;
  runs?: RunRecord[];
}

const MANIFEST_URL =
  process.env.NEXT_PUBLIC_MANIFEST_URL ||
  "https://aratea-app.vercel.app/predictor_manifest.json";

export async function fetchManifest(): Promise<PredictorManifest | null> {
  try {
    const res = await fetch(MANIFEST_URL, {
      // Revalidate hourly: live but cache-friendly.
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return (await res.json()) as PredictorManifest;
  } catch {
    return null;
  }
}
