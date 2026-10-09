<!-- Version française : contributor-starter-issues.fr.md -->

# Contributor starter issues

This file catalogues real, small tasks suitable for opening as GitHub issues with
the `good-first-issue` label. They are intentionally scoped to one module and
require no private credentials, wallet access, or production deployment rights.

Aratea is bilingual EN/FR. Following the repository-wide convention, the base
filename is the English version and the `.fr.md` suffix is the French mirror.
Several tasks below exist precisely to close gaps in that mirroring.

**Before starting**, read [`../CONTRIBUTING.md`](../CONTRIBUTING.md). Two points
matter more than the rest: Aratea runs **no third-party bounty platform**, and
contributions are compensated through the project's own monthly minting rounds
based on Git-visible evidence only.

---

## Status of this catalogue

*Last revised: 2026-08-10.*

The five original entries of this file (predictor README alignment, dashboard env
table, static site preview, wallet registration example, docs index) have all been
consumed and are considered closed. The docs index in particular now exists at
[`README.md`](README.md).

The catalogue below is the current batch, opened 2026-08-07.

| Issue | Task | Module | State |
|---|---|---|---|
| #197 | `CONTRIBUTING.fr.md` parity | root | open |
| #198 | `rounds/WALLETS.fr.md` | `rounds/` | open |
| #199 | `site/README.fr.md` | `site/` | open |
| #200 | `predictor/docs/` index | `predictor/` | **reserved for @AlbertSong1024 until ~2026-08-21** |
| #201 | Phase 1 runbook, English version | `contracts/` | open — **not labelled `good-first-issue`** |
| #202 | `docs/bounty-mechanism.fr.md` | `docs/` | proposed, not yet opened |
| #203 | Tailwind CSS 4 migration | `dashboard/` | proposed, not yet opened — **not a first issue** |

A reserved issue means a contributor has publicly claimed it with an announced
window. If the window lapses without a PR, the issue reopens to the next taker.

---

## 1. Bring `CONTRIBUTING.fr.md` to parity with `CONTRIBUTING.md` *(#197)*

**Module:** repository root

**Why it is real:** `CONTRIBUTING.md` (EN) and `CONTRIBUTING.fr.md` (FR) have
drifted. The English version carries sections the French one does not — notably
the "No third-party bounty platforms" policy, the per-module local setup blocks,
and the pre-commit hygiene section. A French-speaking contributor reading only
the mirror gets an incomplete picture of the rules that bind them.

**Likely files:**

- `CONTRIBUTING.fr.md`

**Acceptance criteria:**

- Every section heading present in `CONTRIBUTING.md` has a counterpart in
  `CONTRIBUTING.fr.md`, in the same order.
- The bounty-platform policy is translated in full — it is a rule, not a
  courtesy, and a partial translation weakens it.
- Command blocks are copied verbatim; only prose is translated.
- Cross-links point to the French mirror where one exists (`README.fr.md`,
  `rounds/RUBRIC.md`…), and to the base file where none does.
- The PR states that no rule was changed, only translated.

---

## 2. Write `rounds/WALLETS.fr.md` *(#198)*

**Module:** `rounds/`

**Why it is real:** `rounds/WALLETS.md` defines the wallet registration table and
the signature procedure — step 2 of participating in the project. It exists in
English only. Registering a wallet is a prerequisite for any compensation, so a
translation gap here is a direct barrier to entry for French-speaking
contributors.

**Likely files:**

- `rounds/WALLETS.fr.md` (new)
- `rounds/WALLETS.md` — add the `<!-- Version française : WALLETS.fr.md -->`
  header comment only

**Acceptance criteria:**

- The signed-message shape is reproduced **exactly**, character for character —
  a mistranslated signature payload produces an invalid signature.
- Placeholder addresses only. No real contributor row is added or duplicated.
- The registry table itself is not duplicated in the mirror; the French file
  links to the canonical table in `WALLETS.md`.
- Both files cross-link to each other.

---

## 3. Write `site/README.fr.md` *(#199)*

**Module:** `site/`

**Why it is real:** `site/README.md` covers deployment, editing, and local
preview of the single-file static page. No French mirror exists.

**Likely files:**

- `site/README.fr.md` (new)
- `site/README.md` — header comment only

**Acceptance criteria:**

- All preview and deployment commands are reproduced verbatim.
- The text preserves the statement that no build step is required.
- `site/index.html` is not modified.

---

## 4. Add an index to `predictor/docs/` *(#200 — reserved)*

**Module:** `predictor/`

**Why it is real:** `predictor/docs/` accumulates feature notes, split reports,
and session briefs with no entry point. A reader looking for how the feature sets
are defined, or for the temporal-split rationale, has to open files one by one.
[`docs/README.md`](README.md) did the same job for the top-level docs folder and
is the model to follow.

**Likely files:**

- `predictor/docs/README.md` (new)

**Acceptance criteria:**

- Every file at the top level of `predictor/docs/` is linked with a one-line
  purpose.
- Documents are grouped by theme (features, validation methodology, session
  reports) rather than listed flat.
- **No new claim is introduced.** Each one-liner is restricted to what the linked
  document itself states — this is an index, not a summary, and the distinction
  matters because several of these documents record results that have since been
  superseded.
- Superseded documents are marked as such where the file itself says so, and
  left unannotated otherwise.

> **Reserved** for @AlbertSong1024 until approximately 2026-08-21, announced
> publicly on 2026-08-07.

---

## 5. English version of the Phase 1 deployment runbook *(#201)*

**Module:** `contracts/`

> ⚠️ **Deliberately not labelled `good-first-issue`.** This document describes a
> procedure executed with real keys on a live chain. A translation error here has
> consequences a documentation mistake normally does not. Listed in this
> catalogue because it is well-scoped, but it wants a contributor who has already
> merged something in this repository.

**Why it is real:** the Phase 1 deployment runbook exists in French only, while
the contracts documentation is otherwise the most read-by-outsiders part of the
repository — it is what an auditor or an external reviewer opens first. The
convention makes English the base filename, so the current state inverts the
repository standard.

**Likely files:**

- The English base-name counterpart of the existing French runbook under
  `contracts/docs/`

**Acceptance criteria:**

- Every command, address placeholder, and Ledger confirmation count is
  reproduced exactly. A runbook that diverges from the original in a single
  parameter is worse than no runbook.
- Warnings and blocking preconditions keep their prominence — they are the part
  that prevents a mistake on a live chain.
- The French original gains a header comment pointing to the English base file.
- The PR states that no procedure was changed, only translated.

---

## 6. Write `docs/bounty-mechanism.fr.md` *(#202 — proposed)*

**Module:** `docs/`

**Why it is real:** [`bounty-mechanism.md`](bounty-mechanism.md) states that
Aratea does **not** currently run a cash bounty program, and describes what a
Phase 2 mechanism might look like. It exists in English only. This is the
document that answers "will I be paid, and how" — arguably the single most
consequential page for a prospective contributor to misunderstand.

**Likely files:**

- `docs/bounty-mechanism.fr.md` (new)
- `docs/README.md` and `docs/README.fr.md` — update the `Lang` column for this
  row from `EN` to `EN/FR`

**Acceptance criteria:**

- The negative statement — no active cash bounty program, no third-party
  platform — is translated without hedging or softening.
- The Phase 2 mechanism is clearly marked as prospective, not committed.
- Both index files are updated in the same PR.

---

## 7. Migrate the dashboard to Tailwind CSS 4 *(#203 — proposed)*

**Module:** `dashboard/`

> ⚠️ **Not a `good-first-issue`.** Listed here because it is well-scoped and
> independently verifiable, but it is a genuine migration and should carry a
> `help-wanted` label rather than `good-first-issue`.

**Why it is real:** the dashboard is pinned to `tailwindcss` 3.4.16. Tailwind 4
is a rewrite: new engine, configuration moved from `tailwind.config.js` into CSS
via `@theme`, and PostCSS repackaged as `@tailwindcss/postcss`. A dependabot PR
proposing the bump alone would break the build, which is why the automated PR was
closed in favour of a tracked migration.

There is no security pressure here — Tailwind 3 has no known advisory. This is
maintenance, and it can wait for someone who wants it.

**Likely files:**

- `dashboard/package.json`
- `dashboard/postcss.config.*`
- `dashboard/tailwind.config.*` (removed or reduced)
- the global stylesheet, which receives the `@theme` block
- any component relying on a renamed or removed utility class

**Acceptance criteria:**

- `npm run typecheck` and `npm run build` both pass.
- Every page renders without visual regression: `/`, `/rounds`, `/round/[hash]`,
  `/predictor`, `/governance`, `/insurance`. Before/after screenshots of each in
  the PR.
- The PR lists every utility class renamed by the migration, so the diff can be
  reviewed without re-deriving the mapping.
- No change to application logic — this is a styling-layer migration only.

---

## Proposing a new starter issue

An entry belongs here when all four hold:

1. **It is real.** The gap is verifiable in the repository today, and the entry
   says how to verify it.
2. **It is scoped.** One module, one problem, reviewable in a single sitting.
3. **It needs no privilege.** No secret, no wallet, no deploy right, no
   production access.
4. **It has acceptance criteria a reviewer can check** without re-doing the work.

Entries that fail (1) are the ones that rot: this catalogue previously listed
five tasks that had been completed months earlier, which wastes the time of
exactly the contributors it was meant to attract. **When an issue is closed,
strike its entry here in the same PR.**
