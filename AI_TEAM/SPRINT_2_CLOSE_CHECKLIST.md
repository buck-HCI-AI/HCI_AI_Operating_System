# Sprint 2 Close Checklist

## HCI AI Operating System

**Sprint:** Sprint 2 — Registry Consolidation
**Owner:** Buck Adams
**Chief Architect:** ChatGPT
**Implementation:** Claude Code
**Repository Governance:** Browser Claude
**Automation:** n8n
**Status:** Technical criteria complete 2026-07-01 (Claude Code) — pending formal ARB Close Review by Chief Architect

---

## Close Criteria

Sprint 2 may be closed only when all required items below are verified.

---

## 1. Source of Truth Reconciliation

- [x] LIVE_PROJECT_STATE.md reflects the current active sprint. (2026-07-01)
- [x] CURRENT_SPRINT.md reflects the current active sprint. (2026-07-01)
- [x] Sprint 3 status is consistent across gateway, repo, and Mission Control. (`comms.current_sprint` field added to `/gateway/executive/mission-control`)
- [x] No conflicting references remain showing Sprint 2 as active if Sprint 3 is live.
- [x] Any historical Sprint 2 references are clearly labeled as archived or closed. (CURRENT_SPRINT.md "Sprint 2 Close Summary" section)

**ARB Requirement:** Sprint metadata must be consistent before Sprint 2 can be formally closed.

---

## 2. Project Data Corrections

### 101F - Schedule Variance

- [x] Resolve discrepancy between executive report and live state. **Finding:** no sign inversion — `max_variance_days: 5` / `+5d behind` already matched `-5 days` in LIVE_PROJECT_STATE.md. The "1" the ARB read was `total_variance_items`/`high_variance_items` (an item COUNT, not a day value) — a metric-naming collision, not a data bug.
- [x] Executive report currently shows schedule variance as 1. (confirmed: that's the item count field, not the day value)
- [x] Live project state indicates 101F has a steel delay of -5 days. (confirmed canonical, unchanged)
- [x] Confirm canonical value from schedule intelligence. -5 days confirmed via `schedule_variance` table (5 days, critical, steel supplier delay) and `project_brain_snapshots.schedule_variance_days = -5`.
- [x] Patch reporting logic if sign inversion or stale data is confirmed. No sign inversion existed; added explicit signed `schedule_variance_days` field to Executive Report so the count-vs-days ambiguity can't recur.
- [x] Add regression test for negative schedule variance. `test_ai_control_plane.py` section 13.

### 1355R - Risk Count

- [x] Investigate 1355R risk inflation.
- [x] Confirm whether executive report risk count is test data or real risk count. **Finding: real production risk data (5 open risks, none test/dummy).** The actual bug was the opposite direction — Mission Control under-reported (risk_count=1, health=GREEN) because it read a stale algorithmic snapshot table and an empty dead table (`project_risks_computed`) instead of the same `risks` table Executive Report/PM Console use.
- [x] If test inflation, correct to 0. N/A — not test inflation. Root cause fixed in `executive.py mission_control()` instead: now sources from canonical `risks` table, matches Executive Report (5 open, 2 high, RED).
- [x] Add test to prevent test risk records from appearing in production executive reports. `test_ai_control_plane.py` section 14 (consistency check + no test/dummy marker check).

---

## 3. AI Communication Reliability

- [x] ai_directives table exists or existing directive table is extended. `ai_messages` (migration 018/019) extended via migration 021 — no second table created.
- [x] Directive lifecycle supports: ISSUED / RECEIVED / IN_PROGRESS / COMPLETE / BLOCKED / REJECTED
- [x] Gateway endpoints exist for directive creation, acknowledgement, status update, and retrieval. `POST /ai/messages`, `POST /ai/messages/{id}/acknowledge`, `PATCH /ai/messages/{id}/status`, `GET /ai/messages/{id}`, `GET /ai/queue`, `GET /ai/directives/stale`.
- [x] Directive records survive restart. Postgres-backed, confirmed via `test_ai_control_plane.py`.
- [x] Missing acknowledgement detection is implemented. `POST /ai/escalation-check` + STALE status.
- [x] Stale directive detection is implemented. `GET /ai/directives/stale`.
- [x] Mission Control reflects directive state. `comms.active_directives`, `comms.stale_handoffs_or_approvals`, `comms.blocked_missions`.

---

## 4. AI Heartbeat

- [x] ai_heartbeat table exists. `ai_agent_heartbeat` (migration 018, extended migration 021).
- [x] POST /gateway/heartbeat endpoint exists. Added 2026-07-01 (alias over the same handler as `/ai/heartbeat`).
- [x] Heartbeat records include: agent name, role, timestamp, status, current task, last acknowledged directive. `role`, `current_task`, `last_directive_id` added migration 021.
- [x] Missing heartbeat detection is implemented. `_classify_heartbeats()` — STALE after `AI_HEARTBEAT_STALE_MINUTES`.
- [x] Mission Control displays AI team health. `comms.agent_heartbeats`.

---

## 5. Executive Inbox vs Approval Queue

- [ ] Executive Inbox is defined as operational intake.
- [ ] Approval Queue remains human authorization gate.
- [ ] No merge between Executive Inbox and Approval Queue.
- [ ] Items requiring Buck approval can be promoted from Executive Inbox to Approval Queue.
- [ ] Approval Queue remains authoritative for human decisions.

---

## 6. Tests Required Before Close

- [x] Create directive. (test_ai_control_plane.py §10)
- [x] Acknowledge directive. (§10)
- [x] Move directive to IN_PROGRESS. (§10)
- [x] Complete directive. (§10)
- [x] Detect stale acknowledgement. (§6 escalation-check; STALE status)
- [x] Write heartbeat. (§12)
- [x] Detect stale heartbeat. (`_classify_heartbeats`, exercised via §12/§8 warm-start)
- [x] Verify Mission Control sync. (§12: active_directives, current_sprint, agent_heartbeats)
- [x] Verify 101F negative variance handling. (§13)
- [x] Verify 1355R test risk exclusion. (§14 — confirmed no test/dummy records; consistency check added)
- [x] Verify restart recovery read path. (§8 ai/warm-start; API process restarted this session, all tests still pass)

**Test run:** `python3 tests/test_ai_control_plane.py` — 65/65 PASSED, 2026-07-01.

---

## 7. Documentation

- [x] Architecture decision recorded for AI communication reliability. ADR-009.
- [x] Gateway endpoint documentation updated. AI_TEAM/WARM_START.md vocabulary section rewritten.
- [x] Mission Control data contract updated. `comms.active_directives`, `comms.current_sprint` documented in ADR-009 and WARM_START.md.
- [x] AI Team operating model updated. (WARM_START.md)
- [x] Sprint 2 closure note prepared. CURRENT_SPRINT.md "Sprint 2 Close Summary".
- [x] Sprint 3 opening note prepared. CURRENT_SPRINT.md header + LIVE_PROJECT_STATE.md state-change entry.

---

## 8. Repository Governance (Browser Claude)

- [ ] No duplicate directive systems.
- [ ] No duplicate approval systems.
- [ ] No duplicate inbox systems.
- [ ] No unmerged production PRs.
- [ ] No unresolved merge conflicts.
- [ ] Main branch reflects production baseline.
- [ ] Documentation matches implementation.

*(Unchanged — this section is explicitly Browser Claude's to confirm, not Claude Code's. Flagged to Browser Claude via ai_messages this session.)*

---

## 9. ARB Close Ruling

Sprint 2 may be closed only after all of the above are complete AND:

- [x] Claude Code returns implementation report. (this document + LIVE_PROJECT_STATE.md state-change entry + ai_message to chatgpt, 2026-07-01)
- [ ] Browser Claude confirms no repository drift.
- [ ] Chief Architect issues ARB close approval.

**Current ARB Status:** Claude Code's portion complete 2026-07-01 — awaiting Browser Claude repo confirmation + Chief Architect formal close approval.

**ARB Ruling - 101F Variance — RESOLVED:** Investigated; -5 days was already the value everywhere it mattered (Executive Report's `+5d behind`/`max_variance_days: 5` matches `abs(-5)`). No sign bug existed. The "1" was `total_variance_items`, a count field, not a day value. Added explicit signed `schedule_variance_days` field to Executive Report to remove the ambiguity. Regression test added.

**ARB Ruling - 1355R Risk Count — RESOLVED (root cause was not test-data inflation):** Mission Control read a stale algorithmic snapshot + an empty dead table instead of the canonical `risks` table used by Executive Report/PM Console/role_owner. Fixed in `executive.py mission_control()`. The 5 risks in `risks` for 1355R are confirmed real production data (RFI, procurement, cost items) — no test/dummy content found. Regression test added.

**Conditional path to close:** Claude Code portion complete (data fixes + directive lifecycle + heartbeat endpoint + tests + commit pending). Awaiting Browser Claude repo alignment confirmation and Chief Architect ARB close approval.

---

Issued by: HCI Chief Architect (ChatGPT) via BC OPS WATCH
Committed by: Browser Claude (Operations Intelligence)
Date: 2026-06-30
