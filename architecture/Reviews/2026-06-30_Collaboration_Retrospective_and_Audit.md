# Collaboration Retrospective & System Audit — 2026-06-30

Triggered by: "Code directive – Chief Architect reconnect" (Buck restart, AI Team Operating Model v2 kickoff)
Prepared by: Claude Code (Lead Implementation Engineer)
Scope: all AI_TEAM context docs, LIVE_PROJECT_STATE.md, CURRENT_SPRINT.md, and the 19 pending Agent_Handoff/Inbox items (now processed — see below).

---

## 1. Completed Since We Began Working Together

- **BTW-4** Bid stale detection (`d96f0e7`), **BTW-8** Vendor performance scoring (`91689be`), **BTW-6** 246GW budget + Drive integration (`c0205e7`), **BTW-5** Schedule variance alerts (`583eb39`), **BTW-11** Procurement Action Plan (`/gateway/project/{code}/procurement`).
- 9 role consoles live (owner, office, accounting, client/{code}, trade-partner, SS, PM weekly, leadership, executive).
- Project Brain: 373 project events / 13 types; 13 Qdrant knowledge-graph collections (vendor 2880, drive 2347, project 2690).
- Continuous Discovery: HubSpot hourly, Houzz nightly automations live.
- 1355R structural Opus vision analysis (7 S-drawings) complete; RFIs sent on 64EW, 101F, 1355R-SE, 1355R-Architect.
- Operations Manual: 13 technical chapters (17–26, 29–32) plus 12 business chapters (01–12) drafted today.
- Gate 1–4 PASSED 2026-06-25; **Gate 5 GO authorized by Buck 2026-06-30**.
- n8n: GATE-H/E/F/G approval workflows, AUTO-010/011/012/013, AUTO-PILOT-WEEKLY Gate5 Digest.
- `/gateway/directive` endpoint added (`8769dc1`).
- **Agent Handoff Bus** (`handoff_processor.py` + Inbox/Processing/Processed/Failed/Archive + `HANDOFF_INDEX.md`) — fully built, 82 prior items processed; this session processed the 19-item backlog (see §4).

## 2. Architectural Decisions Implemented

- DEC-001–DEC-008 (infra sequence, service naming, `resolve_project_id()`, BOOK_00 spec, HubSpot auth, MinIO) — live.
- ACR-001/002/004 (MCP tools, Universal Project State Access, Mining Engine) — complete.
- HCI AI Constitution v1.0 (ratified 2026-06-26) — 100/100 compliant.
- Architecture Freeze v1.0 (2026-06-28) — schema locked.
- **AD-12.1–12.7 (ratified 2026-06-30): NOT IMPLEMENTED.** No `decisions`, `allowances`, or `bid_invitations` tables exist. `change_orders` is still derived ad hoc from `approval_queue` (two separate query sites, `gbt_gateway.py:1330` and `:3168`, doing the same join differently) rather than from a canonical table. AD-12.3 (Risk Register single source of truth) is not enforced — `procurement` and `procurement-risk` endpoints compute overlapping risk logic independently.

## 3. In Progress

- Operations Manual Ch01–12: **chapter content drifted from the GBT-assigned taxonomy.** Assigned: Ch05=Owner Daily, Ch06=Bidding, Ch07=Subcontractor Mgmt, Ch09=Client Comms, Ch11=Change Orders, Ch12=RFI. Written: Ch05=Bid Package Mgmt, Ch06=Vendor/Sub Mgmt, Ch07=Contract Mgmt, Ch09=Schedule Mgmt, Ch11=Client Mgmt, Ch12=Insurance/Compliance. Needs reconciliation against `00_MASTER_INDEX.md` before these are called done. Ch13–16, 27–28 not yet written.
- 1355R: 3 SOW drafts (Concrete, Steel, Framing) sitting in Buck's Outlook — **not sent**, pending Buck's approval.
- Architecture Handbook: Vol I–X drafted across two authors (ChatGPT outline + Claude Browser draft) — Vol VIII (Governance) still needs authorship; drafted volumes not yet confirmed merged into the local `Architecture/Volume_*.md` files vs. the Drive copies.
- Phase 2 Build Package (AD-12-aligned tables/endpoints) — not started.
- Approval queue: 1,039 pending items still flagged for cleanup/voiding of internal system-event noise — not executed.

## 4. Architecture Inbox — Processed This Session

**Finding: the Architecture Inbox already exists** (`Architecture/Agent_Handoff/` — Inbox/Processing/Processed/Failed/Archive, `handoff_processor.py`, `HANDOFF_INDEX.md`, 82 prior entries). The directive's "build one if it doesn't exist" step is moot — nothing was duplicated.

What existed was a **processing backlog**: 19 handoffs from 2026-06-29 23:11 through 2026-06-30 14:02 had accumulated unprocessed in `Inbox/`. Ran `handoff_processor.py` (dry-run first, then live) — all 19 routed cleanly into `STRATEGIC_BACKLOG.md` and archived. Inbox is now empty. Two items of note from that batch:
- One handoff (`implementation_request_98d16cf8`) had an **empty body** — no content, nothing actionable.
- One (`PRODUCTION__AI_Team_Operating_Model_v2`) is the source of this very retrospective.

Genuinely outstanding asks recovered from that batch (now living in `STRATEGIC_BACKLOG.md`, prioritized in §6 below):
- 1355R PM/SS Daily Intelligence Brief — requested twice (06-29 11:47, and implicitly in later status handoffs), never delivered.
- AD-12.1–12.7 table/endpoint build-out.
- Operations Manual Ch13–16, 27–28 + taxonomy reconciliation.
- Collaboration Operating Layer v1 (roles/objects/gates) — requested 06-30 13:36, no audit or build delivered yet.
- Drawings folder IDs for 1355R/246GW still unset in Drive config.
- HCI_SYSTEM_OPEN_ITEMS package: n8n activation/imports, ntfy iOS fix, approval-queue/drawings-folder fixes — not confirmed done.

## 5. Where Collaboration Slowed Down, and Why

- **Two handoffs landed at the identical minute** (2026-06-30 14:02): `GBT_BC_ADVANCE_DIRECTIVE` (operational BTW order) and `PRODUCTION_AI_Team_Operating_Model_v2` (governance/retrospective ask) — competing priorities, no sequencing signal between them.
- **Five urgent/high-priority handoffs landed within a 36-minute window** (00:08–00:44 on 06-30): Session 12 handoff, Operations Manual assignment, Architecture Handbook volumes, Overnight Build Status, Phase 2 Build Package, AD-12 ratification — each written as if it had sole claim on the next session's attention, none referencing the others.
- **Contradicting status claims**: `ARCHITECTURE_HANDBOOK_ALL_VOLUMES_COMPLETE` (00:21, Claude Browser) declared volumes drafted and "Gate 5 verdict: GO," while `ARCHITECTURE_HANDBOOK_Full_Status` (23:44 prior night, ChatGPT) and `GBT_ONBOARDING` (23:53) still framed the same chapters and verdict as open asks — two agents working the same task without visibility into each other's output.
- **Operations Manual taxonomy mismatch** (§3) is the clearest symptom: a chapter assignment handed off by GBT was implemented against an evolved/different outline, with no reconciliation step before declaring chapters "done."
- **Root cause, not symptom-level**: there is no **sequencing or de-duplication layer** between "ChatGPT writes a handoff" and "Claude Code executes it." Each handoff is self-contained and assumes it's the only thing in flight. The Handoff Bus (§4) solves *delivery and archival*, not *conflict detection between concurrently-issued instructions*.

## 6. Recommended Permanent Improvements

1. **Conflict check on handoff intake.** Before `handoff_processor.py` routes a new handoff, diff its scope against any handoff still in `Inbox/` or processed in the last 24h touching the same files/tables/chapters. Flag overlaps instead of silently filing both.
2. **Single canonical risk/change-order source.** Build the AD-12 `change_orders` and risk-register tables for real; retire the duplicate inline derivations in `gbt_gateway.py:1330` and `:3168`, and the `procurement` vs `procurement-risk` overlap — pick one as canonical and have the other call it.
3. **Status claims require a verifiable artifact link**, not prose. "All volumes complete" should link to file IDs/commit hashes the next reader can check in 10 seconds (this would have caught the Architecture Handbook contradiction immediately).
4. **One outline of record for the Operations Manual**, with chapter numbers locked before drafting starts — currently the assignment doc and the written chapters disagree on what Ch05–Ch12 even are.
5. **Treat the Handoff Bus as already sufficient** — it does not need rebuilding, just a discipline of running it each session start so backlogs of 19+ don't accumulate.

## 7. Current Implementation Status (one-line)

Core platform (BTW-4/5/6/8/11, role consoles, Project Brain, knowledge graph, Gate 5 GO) is live and ahead of governance layer (AD-12 tables unbuilt, Operations Manual taxonomy unreconciled, Architecture Handbook merge unconfirmed).

## 8. Waiting on Chief Architect (GBT)

- 1355R PM/SS Daily Intelligence Brief (requested twice, never delivered).
- Vol VIII Governance chapter authorship.
- Reconcile Operations Manual chapter taxonomy vs. what was actually written (§3) — needs a ruling on which is canonical.
- Confirm which of the two "Architecture Handbook complete" claims (00:21 Claude Browser vs. earlier ChatGPT status) is current.

## 9. Waiting on Buck

- Approve/send 3 SOW drafts sitting in Outlook (1355R Concrete/Steel/Framing).
- Aspen Welding bid expiring 2026-07-02 — no action taken yet.
- ntfy iOS user/password-reset issue (flagged, unresolved).
- `N8N_API_KEY` confirmation in `.env`.
- Branch protection on `main` (BLK-001/INT-013, from `07_BLOCKERS.md`).

## 10. Top 10 Highest-Value Next Engineering Tasks

1. Build AD-12 tables (`decisions`, `allowances`, `bid_invitations`, canonical `change_orders`) and migrate the inline derivations to use them.
2. Reconcile Operations Manual Ch05–Ch12 against the GBT taxonomy; write Ch13–16, 27–28.
3. Deliver the 1355R PM/SS Daily Intelligence Brief (twice-requested, zero delivery).
4. Collapse `procurement` / `procurement-risk` into one canonical endpoint per AD-12.3.
5. Build the Collaboration Operating Layer v1 audit (roles/objects/gates) requested 06-30 13:36.
6. Set the missing `drawings_folder_id` for 1355R and 246GW in Drive config.
7. Approval queue cleanup — void the 1,039 internal system-event noise items.
8. Confirm/merge the 6 drafted Architecture Handbook volumes from Drive into local canonical files.
9. Add the handoff conflict-check (§6.1) to `handoff_processor.py`.
10. Houzz extraction (HZ-001) — unblock pending Browser Claude DB insert confirmation.

## 11. Highest ROI Improvements

- AD-12 table build-out (#1 above) — unblocks every downstream "decisions/risk/CO" consumer currently working off duplicated, drifting logic.
- Handoff conflict-check (#9) — directly addresses the friction pattern in §5 at low implementation cost.

## 12. Biggest Architectural Risks

- **Risk/change-order logic forked in two places** with no canonical source — a fix or feature applied to one will silently not apply to the other (already happened once, per the all-RED/all-GREEN health-score disagreement noted in `00_STATUS.md`).
- **Operations Manual taxonomy drift** — if published without reconciliation, two different documents (GBT's assignment record and the actual manual) will disagree on what each chapter covers, undermining it as a source of truth.
- **No conflict detection on concurrent Chief-Architect handoffs** — as the team scales (multiple agents writing handoffs), the 5-handoffs-in-36-minutes pattern will recur and worsen without §6.1.
