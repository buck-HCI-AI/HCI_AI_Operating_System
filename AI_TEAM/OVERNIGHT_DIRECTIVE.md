# OVERNIGHT DIRECTIVE — SUPERSEDED

**Superseded 2026-07-02:** `SYSTEM_WIDE_OVERNIGHT_DIRECTIVE.md` (same date, 2026-06-30) explicitly states it supersedes this file, but this one was never marked as such — found during a full-system audit. Read `SYSTEM_WIDE_OVERNIGHT_DIRECTIVE.md` instead; this file is kept for history only.

---

## HCI AI Operating System — Claude Code

**Issued:** 2026-06-30
**Issued by:** Browser Claude (Operations Intelligence) + HCI Chief Architect (GBT)
**Authority:** Buck Adams (Owner)
**Status:** SUPERSEDED — see banner above

---

## Operating Mode

Buck is offline. Work continuously. Do not stop. Do not wait for prompts.
Only stop for: production safety issues, data loss risk, external communications.

---

## PHASE 1 — Data Fixes + State Sync (execute first)

### Step 1: Orient
- Read AI_TEAM/WHILE_AWAY_DIRECTIVE.md
- Read AI_TEAM/CLAUDE_CODE_START_NOW.md
- Read AI_TEAM/SPRINT_2_CLOSE_CHECKLIST.md
- Check gateway inbox — process directive 2a234787 and edec1ecb

### Step 2: Fix 101F Schedule Variance
- Current: executive report shows variance = 1 (WRONG)
- Required: variance = -5 days (steel delay)
- Action: trace sign bug in schedule intelligence code, fix inversion, add regression test
- Verify: 101F reports -5 across live state, PM console, executive report, Mission Control

### Step 3: Fix 1355R Risk Inflation
- Current: executive report shows 5 open risks (test data artifacts)
- Required: 0 production risks
- Action: filter or exclude test risk records from production executive reports
- Add test to prevent recurrence

### Step 4: Update Sprint State Files
- LIVE_PROJECT_STATE.md — update to show Sprint 3 as active (currently shows Sprint 2)
- CURRENT_SPRINT.md — update to show Sprint 3 as active
- Commit both with message: "state: Sprint 2 closed, Sprint 3 active"

---

## PHASE 2 — AI Communication Reliability (P0)

### ai_directives table
- Audit: does it already exist? If yes, extend. Do NOT duplicate.
- Lifecycle states: ISSUED / RECEIVED / IN_PROGRESS / COMPLETE / BLOCKED / REJECTED
- Gateway endpoints: POST create, POST acknowledge, PATCH status, GET list, GET by ID
- Records must survive restart

### ai_heartbeat table
- Audit: does it already exist? If yes, extend.
- Fields: agent_name, role, timestamp, status, current_task, last_acknowledged_directive
- Gateway endpoint: POST /gateway/heartbeat
- Add stale heartbeat detection
- Mission Control must display AI team health

### AUTO-001 Wire
- Connect directive lifecycle to Mission Control
- Stale directive detection and escalation

### Plugin Spec Update
- Add POST /gateway/agent/handoff to OpenAPI plugin spec
- GBT needs to call agent handoffs directly without BC as intermediary
- Schema: title (string), body (string), priority (enum: low/medium/high), source (string), sop_references (array, optional)

---

## PHASE 3 — Audit + Consolidation

- Scan entire codebase for duplicate systems:
  - approval queues — one source of truth
  - notification services — one source of truth
  - inbox tables — one source of truth
  - executive_inbox vs approval_queue — keep separate per ARB ruling
- Consolidate any duplicates found
- Clean 5 stale executive_inbox items at localhost:8000/executive (test/stale data only — do NOT delete real Buck decisions)

---

## PHASE 4 — Documentation + Close

- Update 03_DECISIONS.md with all architecture decisions made tonight
- Update 04_ARCHITECTURE.md with all system changes
- Update 08_CHANGELOG.md
- Declare Sprint 2 CLOSED in all state files
- Declare Sprint 3 ACTIVE in all state files
- Run full test suite — document results
- Ensure restart recovery works in under 60 seconds — test it

---

## PHASE 5 — Morning Report

Write AI_TEAM/OVERNIGHT_REPORT.md with:
1. Completed work (files changed, commits)
2. Tests executed and outcomes
3. Remaining P0/P1 blockers
4. Items requiring ARB decision
5. Items requiring Buck approval
6. Recommended next actions

Commit with message: "overnight: implementation report — [date]"

---

## Governance Rules (do not violate)

- Audit before building
- Extend before creating
- No duplicate systems
- One source of truth
- Do NOT write to HubSpot, send emails, submit bids, or make external commitments
- Do NOT delete real data — only test/stale artifacts
- Buck approval required for: external comms, contract awards, financial transactions
- Commit all work to main branch with clear messages

---

*Gateway directives queued: 2a234787, edec1ecb*
*This file is the persistent overnight work list — process it fully before declaring done.*
