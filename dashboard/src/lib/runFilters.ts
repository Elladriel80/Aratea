/**
 * Pure helpers for the predictor run filters (revue 2026-06-10 C5).
 *
 * The status chips must carry a RAW value (`open` / `resolved`) matched against
 * `run.resolution.status`, with a separate localized label. Sending the
 * localized label as the value broke the filter in FR locale ("ouvert" never
 * matched "open" -> empty tables).
 */
import type { FilterOption } from "@/components/FilterBar";

/** Raw status values used both in the URL param and in `resolution.status`. */
export const STATUS_OPEN = "open";
export const STATUS_RESOLVED = "resolved";

/** Build the status filter chips: raw value + localized label. */
export function statusFilterOptions(labels: {
  open: string;
  resolved: string;
}): FilterOption[] {
  return [
    { value: STATUS_OPEN, label: labels.open },
    { value: STATUS_RESOLVED, label: labels.resolved },
  ];
}

/** True iff a run's raw status passes the selected status filter values. */
export function matchesStatusFilter(rawStatus: string, selected: string[]): boolean {
  return selected.length === 0 || selected.includes(rawStatus);
}
