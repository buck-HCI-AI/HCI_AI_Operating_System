# ADR-021 — 275SS Bid Package Provenance Report

**Date:** 2026-07-11
**Status:** Investigation complete, evidence-backed, decision pending Buck
**Driver:** Chief Architect directive (Telegram msg 1526, relayed by Buck):
"Do not assume. Do not delete. Produce an evidence-backed provenance report"
before any cleanup, answering "Can we prove, with evidence, exactly who or
what created these rows?" — not "did the system probably do this?"

## The finding under investigation

`bid_packages` rows for two projects, both created in a single-instant batch
with no `hubspot_deal_id` and no `drive_bids` row, flagged by the
`unbacked_bulk_bid_packages` drift-check detector:
- **574J (574 Johnson Drive):** 9 packages, created 2026-06-28 16:03:06 UTC
- **275SS (275 Sunnyside Lane):** 14 packages, created 2026-06-28 16:04:04 UTC

## Method

`gateway_request_log` (every logged API call) had zero entries in the
creation window — ruling out any application/gateway code path as the
direct cause. Git history had no commits that day touching this data.
Neither of those sources could explain the rows, so the investigation went
to the one remaining source: **Postgres's own error log** (`docker logs
hci_postgres`). Postgres logs the full failing SQL text (`STATEMENT:`) for
any statement that errors, even with `log_statement=none` (confirmed via
`SHOW log_statement` — off) and `log_connections=off` (confirmed — no
session/client identity is recoverable, only statement text and timestamps).

## Outcome A confirmed for 574J — exact SQL recovered

A failed statement at 2026-06-28 16:02:56.975 UTC (wrong column name
`csi_code` vs. actual `csi_division`) recovered this **exact, deliberately
commented script**, immediately preceding the successful insert 10 seconds
later:

```sql
-- Import 574 Johnson Drive 2026 market bids as vendor pricing intelligence
-- These are real Aspen subcontractor bids from June 2026 = current market rates
-- Import as bid_entries against the 574J reference project (id=17)

-- First need bid packages for this project — insert package stubs
INSERT INTO bid_packages (project_id, package_name, csi_code, status) VALUES
(17, 'Excavation', '02', 'received'),
(17, 'Concrete', '03', 'received'),
(17, 'Structural Steel + Railings', '05', 'received'),
(17, 'Rough Carpentry', '06A', 'received'),
(17, 'Framing Material', '06B', 'received'),
(17, 'Roofing', '07', 'received'),
(17, 'Insulation', '07A', 'received'),
(17, 'HVAC', '15', 'received'),
(17, 'Windows Supply', '08', 'received')
RETURNING id, package_name;
```

This is unambiguous: a deliberately authored, well-commented import script,
explicitly stating its purpose ("real Aspen subcontractor bids... current
market rates") and its two-step plan (package stubs, then `bid_entries`).
The 9 package names match exactly the 9 real 574J packages found in the
database. This directly corroborates the `source='drive_mine_574_johnson_
bid_tracker'` tag already found on the associated `bid_entries` (real vendor
names, dollar amounts, multi-bid comparison notes — see ADR-019/checkpoint).
**Verdict: Outcome A. Human-or-agent-directed authorized maintenance/import
process, executed via direct SQL, not a platform defect.**

## 275SS — high-confidence Outcome A, not identically provable

No error was logged for the 275SS insert (it succeeded on the first try),
and Postgres does not log successful statements — so the exact SQL text
cannot be recovered the same way. What the evidence does show:
- Created 58 seconds after the 574J success, in the same short, densely
  active window (16:02:56–16:12:28 UTC) of hand-run SQL against this
  database — the same window contains multiple other deliberately-commented
  scripts and several `DELETE`/schema-correction statements consistent with
  one operator (or one agent session) actively working through several
  projects' data in sequence.
- The 14 package names and CSI division codes (`01, 02, 02B, 04-09, 13, 15,
  16, ALL`) are coherent, correctly-formed, real CSI divisions matching a
  genuine luxury-residential scope breakdown (Main House sub-divided by CSI
  division, plus site sections for Pool & Spa, Tennis Court, Barn) — not
  garbled or nonsensical, which is what accidental/hallucinated fabrication
  typically looks like (compare to the real 246GW incident, which produced
  19 fake "awarded" packages with names that were literal document-title
  fragments and attached fabricated dollar amounts).
- Unlike 246GW's fabrication, these rows have **zero dollar figures**
  attached anywhere — all `status='not_started'`, no `awarded_amount`, no
  `bid_entries` at all. Whatever created them stopped at "define the
  package taxonomy" and never proceeded to award or price anything.
- A separate, confirmed-legitimate mining operation that same day
  (`source='drive_mine_2026-06-28'`) did reference real 275 Sunnyside cost
  data elsewhere in the system (a lessons-learned entry citing "$138,829"
  HVAC controls "Seen at 275 Sunnyside"), confirming 275SS was a real,
  active subject of legitimate data work that day, not an untouched project
  that suddenly had fabricated financial claims attached to it.

**Verdict: high-confidence Outcome A** (same operator/session, same style,
zero financial fabrication, immediately adjacent to proven-legitimate work)
**but not provable to the same documentary standard as 574J**, because
Postgres's own logging configuration doesn't retain successful statements.
This gap is itself worth fixing (see below) so this exact investigation is
never this hard again.

## What this is not

This is not the 246GW pattern. 246GW's incident involved 19 packages marked
`awarded` with fabricated dollar amounts feeding executive reports as if
real contracts existed, sitting undetected for 11 days. 275SS's rows carry
no dollar figures, no awarded status, and no downstream report has ever
presented them as real financial commitments — the drift-check caught this
one before it could.

## Recommendation (decision is Buck's, not made here)

Given the evidence points to legitimate-but-incomplete scaffolding rather
than fabrication: **complete the work, don't delete it.** Run the same
Drive-mining process already proven for 574J against 275 Sunnyside's real
bid tracker (if one exists in their Shared Drive — read-only access per the
monitored-project directive) to attach real `bid_entries` to these package
stubs, or explicitly mark them `not_started` and leave them as an honest,
empty scope breakdown if no real bid data exists yet to mine. Either
resolution requires Buck's confirmation before acting, per the standing
monitored-project write-scope rule.

## Platform gap this investigation exposed

`bid_packages` (and most operational tables) has no `created_by`/`source`
column and Postgres itself isn't configured to log successful statements
(`log_statement=none`) or connections (`log_connections=off`). This
investigation only succeeded because of a lucky coincidence — a typo that
happened to error and get logged. A future incident without a matching typo
would leave this exact question permanently unanswerable. Recommend (not yet
built, needs Buck's sign-off given performance/disk tradeoffs): either add a
lightweight `created_by`/`source` column convention to financially-sensitive
tables going forward, or enable `log_statement=mod` (log all data-modifying
statements) if disk usage allows. Filing as a known gap here rather than
silently fixing Postgres config unilaterally, since it has real resource
tradeoffs.
