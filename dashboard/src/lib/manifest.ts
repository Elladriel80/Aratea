/**
 * Types + formatting helpers for `public/predictor_manifest.json`. Pure
 * module — no runtime deps. The build-time loader that touches `node:fs`
 * lives in `manifest.server.ts`; this file is safe to import from client
 * components.
 */

export type FeatureStatus = "experimental" | "active" | "dropped" | "retired";
export type Verdict = "MARKET" | "ENSEMBLE" | "LEARNED" | "TIE";

export interface FeatureHistoryEntry {
  run_ts: string | null;
  feature_set: string | null;
  brier_delta: number | null;
  status: "active" | "dropped" | null;
}

export interface FeatureRecord {
  name: string;
  hypothesis: string;
  source: string;
  date_added: string;
  current_status: FeatureStatus | string;
  current_brier_delta: number | null;
  current_brier_delta_raw: string;
  history: FeatureHistoryEntry[];
}

export interface RunRecord {
  ts: string;
  feature_set: string;
  feature_names: string[];
  n_train: number | null;
  n_test: number | null;
  train_date_range: [string, string] | null;
  test_date_range: [string, string] | null;
  brier_train: number | null;
  brier_test: number | null;
  brier_kalshi_mid_test: number | null;
  log_loss_train: number | null;
  log_loss_test: number | null;
  log_loss_kalshi_mid_test: number | null;
  gap_vs_kalshi_mid: number | null;
  verdict: Verdict | string;
  notes: string;
}

export interface PaperBetsSummary {
  n_open: number;
  n_resolved: number;
  pnl_usd_cumulative: number;
  phase_1_counter: string;
}

/**
 * Hybrid effective sample size (CONVENTION §6.bis). Reports N_live, the strict
 * point-in-time backtest count, the NAIVE-excluded count, and the resulting
 * `N_effective = N_live + α · N_backtest_strict`. Used for *secondary*
 * decisions only — the Phase 1 go/no-go gate stays strictly on N_live.
 */
export interface HybridSample {
  alpha_backtest: number;
  n_live: number;
  n_backtest_strict: number;
  n_backtest_naive_excluded: number;
  n_effective: number;
  phase_1_target: number;
  phase_1_progress_live_only: string;
  convention_ref: string;
  note: string;
}

/** Aggregate counters on the backtest ledger (no per-record detail). */
export interface BacktestSummary {
  n_total: number;
  n_strict_point_in_time: number;
  n_naive_excluded: number;
  by_mode: Record<string, number>;
}

export interface BacktestModel {
  name: string;
  role: string | null;
  method: string | null;
  p_yes: number | null;
  brier: number | null;
  log_loss: number | null;
  won: boolean | null;
  point_in_time: boolean | null;
  /** When true, this model was scored with the *current* forecast as a stand-in
   *  for the as-of forecast (NAIVE replay). Excluded from N_backtest_strict. */
  naive_uses_current_forecast: boolean | null;
}

export interface BacktestResolution {
  status: "open" | "resolved" | string;
  outcome: "yes" | "no" | null;
  winning_bin_ticker: string | null;
}

/**
 * One backtest replay record (`schema_version: "2-backtest"`). Structurally
 * closer to `LiveRunRecord` than to the sklearn training `RunRecord`: it has
 * one `models[]` slot per replayed component on a given Kalshi event, plus
 * an `as_of_date` / `target_date` pair captured by the replay harness.
 */
export interface BacktestRunRecord {
  run_id: string;
  schema_version: string;
  type: string;
  mode: string;
  ts_replay_utc: string | null;
  as_of_date: string;
  target_date: string;
  horizon_days: number | null;
  event_ticker: string;
  event_title: string;
  series: string;
  target_market_ticker: string;
  models: BacktestModel[];
  resolution: BacktestResolution;
}

export type LiveRunRole = "champion" | "challenger" | "baseline";

export interface LiveRunModel {
  name: string;
  role: LiveRunRole | string | null;
  method: string | null;
  p_yes: number | null;
  brier: number | null;
  won: boolean | null;
  pnl_usd: number | null;
  pnl_type: "actual" | "theoretical" | string | null;
}

export interface LiveRunPosition {
  side: "YES" | "NO" | string | null;
  n_contracts: number | null;
  entry_price: number | null;
  size_usd: number | null;
  entry_price_yes_cents: number | null;
  entry_price_no_cents: number | null;
}

export interface LiveRunResolution {
  status: "open" | "resolved" | string;
  outcome: "yes" | "no" | null;
  observed_range_f: [number, number] | null;
  winning_bin_ticker: string | null;
  ts_utc: string | null;
  champion_pnl_usd: number | null;
  champion_won: boolean | null;
}

export interface LiveRunRecord {
  run_id: string;
  schema_version: number;
  ts_utc: string | null;
  event_ticker: string;
  event_title: string;
  target_market_ticker: string;
  champion_name: string;
  kalshi_mid_at_entry: number | null;
  position: LiveRunPosition;
  models: LiveRunModel[];
  resolution: LiveRunResolution;
}

export interface PredictorManifest {
  generated_at: string;
  schema_version: number;
  features: FeatureRecord[];
  runs: RunRecord[];
  live_runs?: LiveRunRecord[];
  live_runs_total?: number;
  backtest_runs?: BacktestRunRecord[];
  backtest_runs_total?: number;
  backtest_summary?: BacktestSummary;
  hybrid_sample?: HybridSample;
  paper_bets_summary: PaperBetsSummary;
  kalshi_mid_reference: number | null;
  max_runs_in_manifest?: number;
}

/** Format a `YYYYMMDDTHHMMSSZ` stamp as `2026-05-11 13:08 UTC`. */
export function formatRunTimestamp(ts: string | null | undefined): string {
  if (!ts) return "—";
  const m = ts.match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})Z$/);
  if (!m) return ts;
  const [, y, mo, d, h, mi] = m;
  return `${y}-${mo}-${d} ${h}:${mi} UTC`;
}

/** Format a Brier score (4 fraction digits). */
export function formatBrier(b: number | null | undefined): string {
  if (b === null || b === undefined || Number.isNaN(b)) return "—";
  return b.toFixed(4);
}

/** Format a signed delta with explicit sign. Used for gap vs kalshi_mid. */
export function formatDelta(d: number | null | undefined, digits = 4): string {
  if (d === null || d === undefined || Number.isNaN(d)) return "—";
  const sign = d > 0 ? "+" : d < 0 ? "−" : "±";
  return `${sign}${Math.abs(d).toFixed(digits)}`;
}

/** Extract the Kalshi series prefix from a ticker like `KXLOWTNYC-26MAY11` → `KXLOWTNYC`. */
export function seriesFromEventTicker(ticker: string): string {
  const idx = ticker.indexOf("-");
  return idx === -1 ? ticker : ticker.slice(0, idx);
}

/** True iff any model in this backtest run was scored in NAIVE mode (current
 *  forecast substituted for as-of forecast). NAIVE records are excluded from
 *  N_backtest_strict in CONVENTION §6.bis. */
export function isBacktestRunNaive(run: BacktestRunRecord): boolean {
  return run.models.some((m) => m.naive_uses_current_forecast === true);
}
