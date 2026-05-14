import type { Route } from "next";
import Link from "next/link";

import { getDict } from "@/lib/i18n";
import type { LiveRunRecord } from "@/lib/manifest";

interface Props {
  /** Most recent live paper-trade run, or null if none exist yet. */
  run: LiveRunRecord | null;
  /** Href that takes the reader from "what" to "why" — points to level 2. */
  whyHref: string;
}

/* -------------------------------------------------------------------------- */
/*  Pure formatting helpers (no React, no i18n)                               */
/* -------------------------------------------------------------------------- */

function fmtPct(p: number | null | undefined, digits = 0): string {
  if (p === null || p === undefined || Number.isNaN(p)) return "—";
  return `${(p * 100).toFixed(digits)}%`;
}

function fmtPctPoints(p: number, digits = 0): string {
  return `${(p * 100).toFixed(digits)} pts`;
}

type UnitKind = "temp_f" | "in" | "mph" | "count" | "raw";

const KIND_MAP: Record<
  string,
  { icon: string; en: string; fr: string; unit: UnitKind; varKey: string }
> = {
  LOWT: { icon: "❄️", en: "Daily low temperature", fr: "Température minimale", unit: "temp_f", varKey: "lowt" },
  HIGHT: { icon: "🌡️", en: "Daily high temperature", fr: "Température maximale", unit: "temp_f", varKey: "hight" },
  HIGH: { icon: "🌡️", en: "Daily high temperature", fr: "Température maximale", unit: "temp_f", varKey: "hight" },
  TEMP: { icon: "🌡️", en: "Temperature", fr: "Température", unit: "temp_f", varKey: "temp" },
  RAIN: { icon: "🌧️", en: "Rainfall", fr: "Pluie", unit: "in", varKey: "rain" },
  PRCP: { icon: "🌧️", en: "Precipitation", fr: "Précipitations", unit: "in", varKey: "rain" },
  SNOW: { icon: "🌨️", en: "Snowfall", fr: "Chute de neige", unit: "in", varKey: "snow" },
  WIND: { icon: "💨", en: "Wind speed", fr: "Vitesse du vent", unit: "mph", varKey: "wind" },
  HURR: { icon: "🌀", en: "Hurricane count", fr: "Nombre d’ouragans", unit: "count", varKey: "hurr" },
};

const LOCATION_MAP: Record<string, { en: string; fr: string }> = {
  NYC: { en: "New York City", fr: "New York" },
  LAX: { en: "Los Angeles", fr: "Los Angeles" },
  BOS: { en: "Boston", fr: "Boston" },
  SFO: { en: "San Francisco", fr: "San Francisco" },
  MIA: { en: "Miami", fr: "Miami" },
  DEN: { en: "Denver", fr: "Denver" },
  ATL: { en: "Atlanta", fr: "Atlanta" },
  ORD: { en: "Chicago", fr: "Chicago" },
  DCA: { en: "Washington DC", fr: "Washington DC" },
  PHL: { en: "Philadelphia", fr: "Philadelphie" },
  SEA: { en: "Seattle", fr: "Seattle" },
  HOU: { en: "Houston", fr: "Houston" },
};

/** Extract the numeric threshold from a Kalshi bin code like "B52.5" → "52.5". */
function parseBinThreshold(bin: string): string | null {
  const m = bin.match(/^B(-?\d+(?:\.\d+)?)/);
  return m ? m[1] : null;
}

const MONTH_MAP: Record<string, { en: string; fr: string }> = {
  JAN: { en: "Jan", fr: "janv." },
  FEB: { en: "Feb", fr: "févr." },
  MAR: { en: "Mar", fr: "mars" },
  APR: { en: "Apr", fr: "avr." },
  MAY: { en: "May", fr: "mai" },
  JUN: { en: "Jun", fr: "juin" },
  JUL: { en: "Jul", fr: "juil." },
  AUG: { en: "Aug", fr: "août" },
  SEP: { en: "Sep", fr: "sept." },
  OCT: { en: "Oct", fr: "oct." },
  NOV: { en: "Nov", fr: "nov." },
  DEC: { en: "Dec", fr: "déc." },
};

interface ParsedEvent {
  icon: string;
  kindLabel: string;
  kindKey: string;
  unit: UnitKind;
  locCode: string;
  locLabel: string;
  dateLabel: string;
}

/**
 * Try to decode a Kalshi event ticker like `KXLOWTNYC-26MAY11` into a
 * human-readable shape: icon, what's being measured, where, and when.
 * Falls back to the original event_title if the regex doesn't match.
 */
function parseEvent(
  eventTicker: string,
  eventTitle: string,
  locale: "en" | "fr",
): ParsedEvent {
  // KX{KIND}{LOC}-{YY}{MMM}{DD}
  const re = /^KX([A-Z]+?)([A-Z]{3,4})-(\d{2})([A-Z]{3})(\d{2})$/;
  const m = eventTicker.match(re);

  if (!m) {
    return {
      icon: "🌤️",
      kindLabel: eventTitle,
      kindKey: "",
      unit: "raw",
      locCode: "",
      locLabel: "",
      dateLabel: "",
    };
  }

  // The kind/loc split is ambiguous from a regex alone — KIND_MAP entries are
  // listed longest-first below to avoid `HIGH` shadowing `HIGHT`.
  const head = m[1] + m[2];
  let kind = "";
  let loc = "";
  const candidates = ["HIGHT", "LOWT", "TEMP", "RAIN", "PRCP", "SNOW", "WIND", "HURR", "HIGH"];
  for (const c of candidates) {
    if (head.startsWith(c)) {
      kind = c;
      loc = head.slice(c.length);
      break;
    }
  }
  if (!kind) {
    kind = m[1];
    loc = m[2];
  }

  const meta = KIND_MAP[kind];
  const yy = m[3];
  const mmm = m[4];
  const dd = m[5];
  const monthMeta = MONTH_MAP[mmm];

  const dateLabel = monthMeta
    ? locale === "fr"
      ? `${parseInt(dd, 10)} ${monthMeta.fr} 20${yy}`
      : `${monthMeta.en} ${parseInt(dd, 10)}, 20${yy}`
    : `${dd} ${mmm} 20${yy}`;

  const locMeta = LOCATION_MAP[loc];
  return {
    icon: meta?.icon ?? "🌤️",
    kindLabel: meta ? (locale === "fr" ? meta.fr : meta.en) : kind,
    kindKey: meta?.varKey ?? "",
    unit: meta?.unit ?? "raw",
    locCode: loc,
    locLabel: locMeta ? (locale === "fr" ? locMeta.fr : locMeta.en) : loc,
    dateLabel,
  };
}

interface ConfidenceBucket {
  label: string;
  hint: string;
  tone: string;
  bars: 1 | 2 | 3;
}

/**
 * Map "how decisive is the model on this single event" to a Low/Medium/High
 * bucket. Distance from 50% is the simplest honest proxy: a 92% bet is
 * intuitively more "confident" than a 53% bet, regardless of edge vs. market.
 */
function computeConfidence(
  pYes: number,
  labels: {
    confidence_low: string;
    confidence_medium: string;
    confidence_high: string;
    confidence_low_hint: string;
    confidence_medium_hint: string;
    confidence_high_hint: string;
  },
): ConfidenceBucket {
  const decisiveness = Math.abs(pYes - 0.5) * 2; // 0 → 1
  if (decisiveness >= 0.7) {
    return {
      label: labels.confidence_high,
      hint: labels.confidence_high_hint,
      tone: "text-ok border-ok/40 bg-ok/10",
      bars: 3,
    };
  }
  if (decisiveness >= 0.3) {
    return {
      label: labels.confidence_medium,
      hint: labels.confidence_medium_hint,
      tone: "text-accent border-accent/40 bg-accent/10",
      bars: 2,
    };
  }
  return {
    label: labels.confidence_low,
    hint: labels.confidence_low_hint,
    tone: "text-warn border-warn/40 bg-warn/10",
    bars: 1,
  };
}

/* -------------------------------------------------------------------------- */
/*  Component                                                                 */
/* -------------------------------------------------------------------------- */

export async function PublicWeatherCard({ run, whyHref }: Props) {
  const dict = await getDict();
  const t = dict.predictor.public;
  const layers = dict.predictor.layers;

  if (!run) {
    return (
      <div className="rounded-xl border border-border bg-panel p-8 text-center text-muted font-mono text-sm">
        {t.no_run}
      </div>
    );
  }

  const champion = run.models.find((m) => m.role === "champion") ?? run.models[0];
  const pAratea = champion?.p_yes ?? null;
  const pMarket = run.kalshi_mid_at_entry ?? null;
  const side = (run.position.side ?? "").toUpperCase();

  // Detect current locale from the dictionary itself: the FR dict's predictor
  // title contains "apprentissage". Avoids needing a second cookie read here.
  const currentLocale: "en" | "fr" = dict.predictor.title.includes("apprentissage")
    ? "fr"
    : "en";

  const event = parseEvent(run.event_ticker, run.event_title, currentLocale);
  const bin = run.target_market_ticker.split("-").slice(2).join("-") || "";

  // Build the dynamic question: variable + location + date + threshold (with
  // its proper unit). Falls back to raw event_title + bin if anything is
  // missing — better to show the truth than a broken sentence.
  const threshold = parseBinThreshold(bin);
  const unitFormatter =
    event.unit === "temp_f"
      ? t.threshold_unit_temp_f
      : event.unit === "in"
        ? t.threshold_unit_in
        : event.unit === "mph"
          ? t.threshold_unit_mph
          : event.unit === "count"
            ? t.threshold_unit_count
            : t.threshold_unit_raw;
  const variableLabel =
    event.kindKey === "lowt"
      ? t.var_lowt
      : event.kindKey === "hight"
        ? t.var_hight
        : event.kindKey === "temp"
          ? t.var_temp
          : event.kindKey === "rain"
            ? t.var_rain
            : event.kindKey === "snow"
              ? t.var_snow
              : event.kindKey === "wind"
                ? t.var_wind
                : event.kindKey === "hurr"
                  ? t.var_hurr
                  : "";

  const dynamicQuestion =
    threshold && variableLabel && event.locLabel && event.dateLabel
      ? t.question_template(
          variableLabel,
          event.locLabel,
          event.dateLabel,
          unitFormatter(threshold),
        )
      : null;

  // Edge framing: by how many percentage points does Aratea differ from the market?
  const edgeFraction =
    pAratea !== null && pMarket !== null ? pAratea - pMarket : null;
  let edgeSentence: string;
  if (edgeFraction === null) {
    edgeSentence = "—";
  } else if (Math.abs(edgeFraction) < 0.01) {
    edgeSentence = t.agrees;
  } else if (edgeFraction > 0) {
    edgeSentence = t.disagrees_higher(fmtPctPoints(edgeFraction, 1));
  } else {
    edgeSentence = t.disagrees_lower(fmtPctPoints(-edgeFraction, 1));
  }

  // Resolution badge
  let statusBadge: { text: string; tone: string };
  if (run.resolution.status === "open" || run.resolution.outcome === null) {
    statusBadge = {
      text: t.window_open,
      tone: "border-warn/40 bg-warn/10 text-warn",
    };
  } else if (run.resolution.champion_won) {
    statusBadge = {
      text: t.window_resolved_won,
      tone: "border-ok/40 bg-ok/10 text-ok",
    };
  } else {
    statusBadge = {
      text: t.window_resolved_lost,
      tone: "border-err/40 bg-err/10 text-err",
    };
  }

  const confidence =
    pAratea !== null
      ? computeConfidence(pAratea, t)
      : null;

  return (
    <section
      aria-labelledby="public-card-heading"
      className="rounded-xl border border-border bg-panel/60 backdrop-blur-sm overflow-hidden"
    >
      {/* HEADER — event identity in plain words */}
      <header className="px-6 pt-6 pb-3 flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-4">
          <div className="text-5xl leading-none" aria-hidden="true">
            {event.icon}
          </div>
          <div>
            <h2
              id="public-card-heading"
              className="text-xs uppercase tracking-wider text-muted font-mono"
            >
              {t.heading}
            </h2>
            <p className="text-xl font-semibold text-text mt-1">
              {event.kindLabel}
              {event.locCode ? <> · {event.locCode}</> : null}
            </p>
            <p className="text-sm text-muted">
              {event.dateLabel}
              {bin ? <span className="opacity-60"> · {bin}</span> : null}
            </p>
          </div>
        </div>
        <span
          className={`inline-block self-start rounded-md border px-3 py-1 text-[11px] font-mono ${statusBadge.tone}`}
        >
          {statusBadge.text}
        </span>
      </header>

      {/* QUESTION — built dynamically with the threshold + unit, so the % has
          its own context. Falls back to the raw Kalshi title if a piece is
          missing. */}
      <div className="px-6 pb-3">
        <div className="rounded-md border border-border/60 bg-bg/40 px-3 py-2">
          <div className="text-[10px] uppercase tracking-wider text-muted font-mono">
            {t.question_label}
          </div>
          <p className="text-sm text-text/90 mt-1 leading-snug">
            {dynamicQuestion ?? (
              <>
                {run.event_title}
                {bin ? (
                  <span className="text-muted font-mono"> · {bin}</span>
                ) : null}
              </>
            )}
          </p>
          {dynamicQuestion ? (
            <p className="text-[10px] text-muted/60 font-mono mt-1">
              <code>{run.target_market_ticker}</code>
            </p>
          ) : null}
        </div>
      </div>

      {/* BIG NUMBER — probability gauge, weather-app style */}
      <div className="px-6 py-6 grid grid-cols-1 md:grid-cols-3 gap-6 items-center border-t border-border/40">
        <div className="md:col-span-1 text-center md:text-left">
          <div className="text-[10px] uppercase tracking-wider text-muted leading-tight">
            {t.probability_caption}
          </div>
          <div className="text-6xl font-bold text-accent leading-tight mt-1">
            {fmtPct(pAratea)}
          </div>
          <div
            className={`mt-2 inline-block rounded-md border px-2 py-0.5 text-[11px] font-mono ${
              side === "YES"
                ? "border-ok/40 bg-ok/10 text-ok"
                : side === "NO"
                  ? "border-err/40 bg-err/10 text-err"
                  : "border-border bg-bg text-muted"
            }`}
          >
            {side === "YES"
              ? t.side_yes
              : side === "NO"
                ? t.side_no
                : "—"}
          </div>
          {champion ? (
            <p className="mt-3 text-[10px] text-muted/80 font-mono leading-snug">
              {t.champion_caption(champion.name)}
            </p>
          ) : null}
        </div>

        <div className="md:col-span-2 space-y-4">
          {/* Edge sentence — the only thing the quidam should remember */}
          <p className="text-base text-text leading-snug">{edgeSentence}.</p>

          {/* Two-bar comparison: Aratea vs Market */}
          <ProbabilityRow
            label={t.aratea_says}
            pct={pAratea}
            tone="bg-accent"
          />
          <ProbabilityRow
            label={t.market_says}
            pct={pMarket}
            tone="bg-warn"
          />

          {/* Confidence */}
          {confidence ? (
            <div
              className={`rounded-md border px-3 py-2 text-xs font-mono ${confidence.tone}`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="uppercase tracking-wider opacity-80">
                  {t.confidence_label}
                </span>
                <span className="flex items-center gap-1">
                  <span className="font-semibold">{confidence.label}</span>
                  <ConfidenceBars bars={confidence.bars} />
                </span>
              </div>
              <p className="mt-1 opacity-80">{confidence.hint}</p>
            </div>
          ) : null}
        </div>
      </div>

      {/* FOOTER — explainers + escape hatch toward level 2 */}
      <footer className="px-6 py-4 border-t border-border/40 bg-bg/40 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex flex-col gap-2 max-w-2xl">
          <details className="text-xs text-muted font-mono">
            <summary className="cursor-pointer text-text/80 hover:text-accent">
              {t.explainer_title}
            </summary>
            <p className="mt-2 leading-relaxed">{t.explainer_body}</p>
          </details>
          {champion ? (
            <details className="text-xs text-muted font-mono">
              <summary className="cursor-pointer text-text/80 hover:text-accent">
                {t.champion_explainer_title}
              </summary>
              <p className="mt-2 leading-relaxed">{t.champion_explainer}</p>
            </details>
          ) : null}
        </div>
        <Link
          href={whyHref as Route}
          className="self-start sm:self-auto inline-block rounded-md border border-accent/40 bg-accent/10 px-3 py-2 text-xs font-mono text-accent hover:bg-accent/20"
        >
          {layers.cta_why}
        </Link>
      </footer>
    </section>
  );
}

function ProbabilityRow({
  label,
  pct,
  tone,
}: {
  label: string;
  pct: number | null;
  tone: string;
}) {
  const w = pct === null ? 0 : Math.max(0, Math.min(1, pct)) * 100;
  return (
    <div>
      <div className="flex items-center justify-between text-[11px] font-mono mb-1">
        <span className="uppercase tracking-wider text-muted">{label}</span>
        <span className="text-text font-semibold">
          {pct === null ? "—" : `${(pct * 100).toFixed(1)}%`}
        </span>
      </div>
      <div
        className="h-2 rounded-full bg-bg/80 border border-border overflow-hidden"
        role="progressbar"
        aria-valuenow={pct === null ? undefined : Math.round(w)}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className={`h-full ${tone} transition-all`}
          style={{ width: `${w}%` }}
        />
      </div>
    </div>
  );
}

function ConfidenceBars({ bars }: { bars: 1 | 2 | 3 }) {
  return (
    <span className="inline-flex items-end gap-0.5 ml-1" aria-hidden="true">
      {[1, 2, 3].map((i) => (
        <span
          key={i}
          className={`block w-1 ${
            i === 1 ? "h-2" : i === 2 ? "h-3" : "h-4"
          } rounded-sm ${i <= bars ? "bg-current" : "bg-current opacity-25"}`}
        />
      ))}
    </span>
  );
}
