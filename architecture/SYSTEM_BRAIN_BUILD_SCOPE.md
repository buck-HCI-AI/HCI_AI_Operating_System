# System Brain — Build Scope
**Continuous Remember → Check → Heal → Learn loop**
Requested by Buck 2026-07-20 ("build a brain for the system to remember and keep learning and healing from"). Task #177. Grounded in ADR-016 (continuous drift detection & self-heal), which already established the principle; this unifies and automates it.

## The problem this solves
Issues keep surfacing **live** (during Buck's review) that the system should have caught first: 101F bids mis-classified into wrong divisions, a schedule built from one duplicated source, insulation bids filed flat, an apostrophe duplicating folders 18×, vendor emails auto-hidden in subfolders. Root cause: our self-testing validated that the pipeline **runs and reproduces**, never that its **output is semantically correct**. And when a human catches a new failure, turning it into a permanent guard is manual and often skipped.

## What already exists (the pieces)
| Faculty | Today | Gap |
|---|---|---|
| **Remember** | `memory/*.md` + `MEMORY.md` index; `SESSION_CHECKPOINT.md` | Not connected to the checks — the system doesn't verify past fixes still hold |
| **Check** | `GET /gateway/admin/drift-check` (Mon 07:00 + on-demand): dead connectors, stale creds, n8n failure rate, dupes, GBT sprint-claim drift | Only *mechanical* checks. No *semantic/correctness* checks (right divisions? clean source? matches canonical?) |
| **Heal** | `POST /gateway/admin/self-heal` (container/infra only: n8n restart) | Doesn't touch data-quality; no promotion path from finding → fix |
| **Learn** | Manual: I add a check when Buck catches something | Not automated; findings don't accumulate into permanent guards |

## The build — 4 phases

### Phase 1 — Semantic/correctness checks (the "correct first time" layer)
Add to `drift-check` the classes we've actually hit (task #176):
- Bids in non-real divisions (e.g. Division "00" on 574 Johnson) or divisions not in ANY recognized HCI scheme (must know all schemes — CANONICAL_DIVISION_TREE, real HCI 28/33, Sunnyside CSI — so it doesn't false-flag 1355R's real Div 13/28).
- Catch-all divisions: many distinct vendors spanning clearly-different sub-scopes with no sub-package split.
- Duplicate vendor folders / duplicate `is_latest` bids (same vendor+file).
- Single-source / duplicated mined estimates (distinct-title vs row-count gap — the schedule bug).
- Job structure ≠ canonical (missing sibling folders, flat filing).

### Phase 2 — Learning log + auto-promotion
- A `learning_log` table: every finding, its fix, the check that (should) catch it, status.
- **Auto-promotion:** when a new failure pattern is recorded, generate/register a corresponding drift-check so it's guarded **forever** — automating ADR-016's "turn every catch into a check" instead of relying on me to remember.
- Cross-reference to `memory/*.md` so a documented lesson has a live check backing it.

### Phase 3 — Extend self-heal to safe data fixes
- Auto-fix the unambiguous, reversible classes (trash duplicate folders, re-file a bid whose division is provably wrong per a single scheme, refresh a stale pointer). Everything ambiguous → route to the approval queue / flag Buck. Never auto-touch monitored-job source-of-truth Drive files (standing rule).

### Phase 4 — Continuous loop + reporting
- Run the full remember→check→heal cycle on a schedule (already Mon 07:00) **plus event-driven** (after any ingestion/leveling run).
- One concise Telegram digest: what was checked, what self-healed, what needs Buck — evidence-backed, deduped (no noise).

## Guardrails (unchanged standing rules)
- Never auto-write/delete monitored-job Drive files; never hard-delete without asking; HubSpot is being phased out (don't build on it); emails all go to inbox (no auto-routing).

## System-wide coverage (Buck 2026-07-20: "include the book and other parts of the system")
The brain is **not** scoped to bid data — it spans the whole HCI OS. The `drift-check` "check" faculty already covers many system parts; the brain unifies them under one remember→check→heal→learn loop and adds the missing ones:

| System part | In the brain as | Status |
|---|---|---|
| **The Book** — Architecture Handbook (volumes) + Operating Book (CH01–07) | *Remember* (canonical knowledge) + *Check* (Book stays in-sync with real code/config; numbering integrity; un-integrated authored content). Wire in `AUTO-BOOK-REFRESH` + the existing handbook-numbering / unintegrated-Drive-content checks; add a drift check for "code/config changed but the Book that documents it didn't." | partial — extend |
| **SOPs / business processes** (`business_processes` BP-XX, `sop_approval_gates`) | *Check*: every built feature traces to a governing SOP (CLAUDE.md "SOP alignment check"); flag orphaned features + missing SOPs. | new |
| **n8n workflows** | *Check* (failure rate, dead branches — already in drift-check) + *Heal* (container restart — already in self-heal). | done |
| **Connectors** (Drive/Houzz; HubSpot phasing out) | *Check*: never-synced / stale connectors (already in drift-check). | done |
| **Schedule / Houzz, RFI pipeline, budgets/ROM** | *Check*: semantic correctness (dates, durations vs multi-job norms, RFI freshness, carry vs bids). | extend |
| **Agents** (GBT/CA, BC) | *Check*: heartbeat/staleness, sprint-claim drift, unacked coordination docs (already in drift-check). | done |
| **Bid data** | *Check*: classification/dedup/catch-all (Phase 1, done). | done |
| **Memory** (`memory/*.md`) | *Remember* — every check cross-references a lesson; a documented fix has a live check backing it. | Phase 2 |

**Principle:** anything the system *knows* (the Book, SOPs, memory) is what it checks *against*; anything it *does* (workflows, ingestion, leveling, scheduling) is what it checks *for correctness*. The learning log + auto-promotion apply to ALL of it, not just bids.

## Sequencing
Build **after** 64EW/101F finish (Buck's call). Phase 1 (bid semantic checks) + Phase 2 (learning log) are done. Next: extend the check layer across the Book + SOPs + schedule/RFI/budget (this section), then Phase 3 self-heal + Phase 4 continuous loop. Each phase/target is independently shippable.
