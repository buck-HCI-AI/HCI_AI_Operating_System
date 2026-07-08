# ADR-017 — Live-Project Write Scope Guard

**Date:** 2026-07-08
**Status:** Accepted, implemented
**Related:** ADR-016 (continuous drift detection & self-heal)

## Context

Buck's standing rule: only the 4 live projects (64EW, 101F, 1355R, 246GW) may
ever be written to or have automation run against them. Every other project
(`status IN ('monitoring','reference')`) is read-only — monitor and report,
never write.

On 2026-07-08, an audit found 120 `houzz_daily_logs` rows written to 6
reference-status projects (1762R, 212CL, 349DD, 370G, 655G, 825CL) in the
prior ~18 hours, plus 4 `project_sqft_benchmarks` rows on 813MS/655G/212CL/675M
from an earlier session. Buck flagged this as a hard violation ("THAT CAN'T
HAPPEN EVER") and ordered a system-wide audit and fix.

### Root cause

Two distinct causes, not one:

1. **Real code gap**: `POST /api/v1/services/connectors/{name}/ingest`
   (`services/connectors/routes.py`) had no awareness of `projects.status`
   at all. Any caller with a valid Houzz `project_id` could persist to any
   project regardless of live/monitoring/reference — nothing in the code
   stopped a write to a non-live project except the caller choosing not to.
   The Houzz daily-log rows were written this way, by Claude Code, acting on
   Buck's own earlier-in-session request to mine historical/closed jobs for
   the brain ("I will also try and get historical jobs that are closed to
   mine as well soon — that should really help the brain, is that correct
   thinking?" → confirmed). That request was real, but the system had no
   mechanism to make the resulting write deliberate and logged rather than
   just another unguarded POST.

2. **Manual direct-SQL write**: the 4 `project_sqft_benchmarks` rows came
   from an ad-hoc `INSERT` run directly against the DB in a prior session,
   not through any service/API code path. No code defect produced this —
   it's a process gap (an agent with direct DB access choosing to write to
   a non-live project without checking status first), not a bug to patch.

Verified during this audit: `bid_packages`/`risks` deletions and all Drive
bid-folder writes this session touched only live projects (64EW, 101F,
1355R, 246GW). `background_learning_service.py`'s cross-project discovery
scan is explicitly `mode: "read_only"`. `bid_leveling_service.get_all_configured_projects()`
already correctly filters `WHERE status IN ('active','pilot')`.

## Decision

Add a project-scope guard to the one proven automatable write path
(`BaseConnector.ingest()` in `services/connectors/base_connector.py`),
fail-closed by default:

- Before any non-dry-run persist, resolve every project reference in the
  payload to `projects.status`.
- If any resolved project is not `active`/`pilot`, OR the reference can't be
  resolved at all, block the entire batch with HTTP 403 and no writes
  applied — nothing partially commits.
- The 403 response explains exactly which project(s) were blocked and how
  to proceed intentionally: resend with `allow_non_live: true` and a
  required `override_reason`.
- An explicit override still writes, but every override is logged to
  `notification_log` (`event_type='non_live_project_write_override'`) with
  the reason — so historical-mining writes Buck actually wants stay
  possible, but are now a deliberate, auditable action instead of an
  invisible default.
- `HouzzConnector._project_scope_check()` implements the resolution
  (`houzz_project_id` → `houzz_projects.name` → `projects.status`); the
  `projects` entity type itself is exempt since that's how the mapping
  bootstraps in the first place.

Verified live: a `daily_logs` write against 212 Cleveland (reference status)
was blocked with 0 rows written; the same payload with `allow_non_live` +
`override_reason` wrote 1 row and logged the override to `notification_log`.

### What this does NOT fix

Direct DB/SQL access (Bash + psycopg2, available to Claude Code per
CLAUDE.md's local-command auto-approval) and direct Google Drive API calls
bypass this guard entirely by construction — there is no code chokepoint for
either. Closing that gap is a discipline rule, not a code fix: before any
manual write (SQL or Drive) to a specific project, check `projects.status`
first, and treat anything outside `active`/`pilot` as requiring Buck's
explicit per-write authorization, not a standing "historical mining is fine"
assumption from earlier in a conversation.

## Consequences

- Every non-live-project write through the connector ingest endpoint is now
  either blocked or explicitly, auditably overridden — never silent again.
- HubSpot connector has no scope check yet (`_project_scope_check` defaults
  to a no-op in the base class) — its entity records don't currently carry a
  resolvable project reference the way Houzz's do. Add one if/when HubSpot
  writes start being project-scoped.
- The 120 historical Houzz log rows and 4 sqft-benchmark rows already
  written were left in place pending Buck's explicit direction — not
  reverted unilaterally, since some of that data was written at his own
  prior request in the same session.
