"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";

export type Level = 1 | 2 | 3;

interface LevelMeta {
  value: Level;
  label: string;
  hint: string;
}

interface Props {
  current: Level;
  labels: {
    aria: string;
    levels: [LevelMeta, LevelMeta, LevelMeta];
  };
}

/**
 * Toggle the depth of detail on /predictor.
 *
 * - Level 1 — public weather card (zero jargon)
 * - Level 2 — informed reader (named components, calibrated explanations)
 * - Level 3 — full registry / expert view (everything in the manifest)
 *
 * Persisted via `?level=` querystring so the choice survives reloads and
 * is shareable / bookmarkable. Uses `<Link>` (prefetch + back-button friendly)
 * rather than imperative router.push.
 */
export function LayerToggle({ current, labels }: Props) {
  const pathname = usePathname();
  const search = useSearchParams();

  function hrefFor(level: Level) {
    const params = new URLSearchParams(search?.toString() ?? "");
    params.set("level", String(level));
    return `${pathname}?${params.toString()}`;
  }

  return (
    <div
      role="group"
      aria-label={labels.aria}
      className="inline-flex flex-col sm:flex-row items-stretch sm:items-center gap-0 text-xs font-mono border border-border rounded overflow-hidden"
    >
      {labels.levels.map((meta, idx) => {
        const isActive = meta.value === current;
        const borderClass =
          idx === 0
            ? ""
            : "sm:border-l border-t sm:border-t-0 border-border";
        return (
          <Link
            key={meta.value}
            href={hrefFor(meta.value) as Route}
            scroll={false}
            aria-pressed={isActive}
            className={`px-3 py-2 transition-colors text-left ${borderClass} ${
              isActive
                ? "bg-accent/20 text-accent"
                : "text-muted hover:text-accent"
            }`}
          >
            <span className="block font-semibold">{meta.label}</span>
            <span className="block text-[10px] opacity-70 mt-0.5">
              {meta.hint}
            </span>
          </Link>
        );
      })}
    </div>
  );
}
