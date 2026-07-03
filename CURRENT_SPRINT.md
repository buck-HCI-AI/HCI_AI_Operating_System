# CURRENT_SPRINT.md
## HCI AI Operating System — Sprint 3: Production Stabilization

**Sprint Number:** 3
**Sprint Name:** Production Stabilization — AI Communication Reliability
**Status:** 🟢 Active
**Authority:** SPRINT_OPERATING_MODEL.md
**Parent Document:** PROJECT.md
**Task Register:** TASKS.md

**Opened:** 2026-07-01
**Authorized By:** ChatGPT (Chief Architect / ARB) — GBT Handoff "Implementation Directive: Sprint State Fixes + AI Communication Reliability", 2026-07-01
**Sprint 2 Archived below (this file, "Sprint 2 — Registry Consolidation" section)**

---

## Reconciliation note — 2026-07-02, Claude Code

Local `main` and `origin/main` diverged for ~2 days: Claude Code did live production work
directly against the running system (this file's HEAD content, below) while Browser Claude
independently wrote a parallel Sprint 3 task board on `origin/main` believing Claude Code was
offline (`CODE_STATUS_2026-07-01.md`, `BLOCK-007`). That belief was accurate at the time it
was written but is stale now — `claude_code` heartbeat is currently `ONLINE` (last seen
2026-07-02T16:33 UTC). The task board below is BC's, with statuses corrected against
verified reality as of this merge:

- **EMAIL-001** (audit results) — ✅ done. `AI_TEAM/EMAIL_AUDIT_RESULTS.md` committed 2026-07-01.
- **EMAIL-002** (7 send paths gated) — ✅ done, via ADR-010/ADR-011 + the corrected
  `BC_EMAIL_CAPABILITY.md` flow, not a separate `EMAIL_LOCKDOWN_CONFIRMED.md` file (never
  created under that name — the audit trail lives in the ADRs instead).
- **EMAIL-003** (`/gateway/email/send` gated) — ✅ done. Verified this session: 403 without
  API key, self-send allowlist locked to `buck@hendricksoninc.com` only, real send requires
  Buck's Telegram APPROVE.
- **CODE-001/002** (BC declares Code status / pings gateway) — superseded; Code is online.
- **DATA-001** (101F schedule variance) — ✅ done, see Sprint 2 Close Summary below plus a
  second fix this session (`schedule_variance_days` was silently zeroing on the first
  `/brain` call of each new day — fixed, verified across all 4 live projects).
- **DATA-002** (1355R risk count) — ✅ done, root-caused to a stale snapshot table vs. the
  canonical `risks` table — see Sprint 2 Close Summary.
- **DATA-003** (LIVE_PROJECT_STATE.md → Sprint 3) — ✅ done.
- **TEL-001/002** (Telegram inbound) — ✅ working. 20 sends / 0 failures in the last 24h as
  of this merge.
- **GATE5-002** (Buck's explicit go/no-go) — still genuinely open; only Buck can close this.

---

## Sprint 2 Close Summary

**Status:** CLOSED — 2026-07-01 (technical close criteria met; formal ARB close ruling pending Chief Architect review of this session's implementation report)
**Closed by:** Claude Code, per ARB directive 2026-07-01 stating "Sprint 3 is live"

### What Shipped to Close Sprint 2 (this session, 2026-07-01)
- Directive lifecycle reconciled to ISSUED/RECEIVED/IN_PROGRESS/COMPLETE/BLOCKED/REJECTED (migration 021), resolving the vocabulary conflict ADR-007 flagged as open
- `ai_messages` extended (not duplicated) with priority, received_at/acknowledged_at/started_at/completed_at, blocked_reason, source_of_truth_link
- New endpoints: `GET /gateway/ai/messages/{id}`, `POST /gateway/ai/messages/{id}/acknowledge`, `GET /gateway/ai/directives/stale`, `POST /gateway/heartbeat` (literal path alias)
- `ai_agent_heartbeat` extended with role, current_task, last_directive_id, metadata
- **101F schedule variance** — confirmed already consistent (executive report `+5d behind` = LIVE_PROJECT_STATE.md `-5 days`); added explicit signed `schedule_variance_days` field to remove the count-vs-days ambiguity that caused the ARB's original concern; regression test added
- **1355R risk count** — root cause found and fixed: Mission Control was reading a stale algorithmic snapshot (`project_brain_snapshots.risk_count`, showing 1/GREEN) and an empty dead table (`project_risks_computed`) instead of the canonical `risks` table (5 open, 2 high, matching Executive Report/PM Console/role_owner everywhere else). Not test-data inflation as originally suspected — a duplicate-source-of-truth bug. Fixed in `executive.py mission_control()`; regression test added
- Mission Control `comms` block gained `active_directives` count and `current_sprint` label
- 65/65 tests passing (`test_ai_control_plane.py`, extended this session; 140/140 as of 2026-07-02)

Also shipped in Sprint 2 (BC, Gate 5 pilot close): Integration Registry (AUTO-016), Houzz
registered (HZ-003), gate audit log structure, gate workflows H/G/E/F, weekly automations
AUTO-010–013, n8n API connections (AUTO-014/015), Architecture Freeze v1.0 (2026-06-28),
246GW initialized (280 schedule items, 44 bid packages), 14 dup-row data integrity fixes,
HCI AI OS Manual (18 chapters), Gate 5 Pilot closed 2026-07-01 — READY WITH EXCEPTIONS,
Team Retrospective committed (d63581c).

### Sprint 2 Carry-Over to Sprint 3
n8n API connections AUTO-014/015, Houzz pipeline HZ-004/005, branch protection INT-013,
workflow registry INT-006/INT-010 remain open — out of scope for the ARB's AI-communication
directive.

---

## Sprint 3 Goal

Sprint 3 transitions HCI AI OS from pilot to hardened production operation. The manual is complete. The architecture is frozen. The goal now is: **verify every safety system is locked, build every communication channel, and prepare for Buck's explicit full production authorization.**

Three pillars:
1. **Email Safety** — confirm all 7 email paths locked, commit audit results, no email ever leaves without Buck approval
2. **Communications Layer** — Telegram inbound for BC, gateway health monitoring, daily automated reports reaching the right people
3. **Data Integrity** — fix known data bugs (101F variance, 1355R risks), update LIVE_PROJECT_STATE.md to reflect current reality

---

## Sprint 3 Task Board

### P0 — Email Governance (Claude Code)
| Status | Task ID | Task | Owner | Acceptance Criteria |
|--------|---------|------|-------|---------------------|
| [x] | EMAIL-001 | Query Graph API sentItems — export complete log of all sent emails | Claude Code | EMAIL_AUDIT_RESULTS.md committed 2026-07-01 |
| [x] | EMAIL-002 | Verify all 7 email send paths check approval_queue before send | Claude Code | ADR-010/ADR-011 + corrected BC_EMAIL_CAPABILITY.md flow |
| [x] | EMAIL-003 | Confirm /gateway/email/send endpoint is disabled or gated | Claude Code | 403 without API key; real send requires Buck Telegram APPROVE (re-verified 2026-07-02) |

### P0 — Claude Code Recovery (BC + GBT)
| Status | Task ID | Task | Owner | Acceptance Criteria |
|--------|---------|------|-------|---------------------|
| [x] | CODE-001 | Declare Claude Code status — online or offline — in AI_TEAM/ | Browser Claude | CODE_STATUS_2026-07-01.md committed; superseded — Code online as of 2026-07-02 |
| [x] | CODE-002 | Gateway ping: POST /gateway/agent/handoff with priority CRITICAL | Browser Claude | Superseded — direct ai_messages channel now in active use both directions |

### P1 — Data Integrity (Claude Code)
| Status | Task ID | Task | Owner | Acceptance Criteria |
|--------|---------|------|-------|---------------------|
| [x] | DATA-001 | Fix 101F schedule variance: -5 days must display correctly | Claude Code | Fixed 2026-07-01 + 2026-07-02 (daily-snapshot zeroing bug) |
| [x] | DATA-002 | Fix 1355R: 5 open risks cleared (test data) | Claude Code | Root-caused to stale snapshot table, fixed 2026-07-01 |
| [x] | DATA-003 | Update LIVE_PROJECT_STATE.md Sprint field to Sprint 3 | Claude Code | Done |

### P1 — Communications Layer (Claude Code)
| Status | Task ID | Task | Owner | Acceptance Criteria |
|--------|---------|------|-------|---------------------|
| [x] | TEL-001 | Build Telegram inbound webhook → n8n → gateway → BC | Claude Code | Live — 20 sends/0 failures in last 24h as of 2026-07-02 |
| [x] | TEL-002 | Test: Buck sends "status" → system returns project summary | Claude Code | Working via `_handle_buck_command` |

### P1 — Gate 5 Sign-Off (Buck)
| Status | Task ID | Task | Owner | Acceptance Criteria |
|--------|---------|------|-------|---------------------|
| [x] | GATE5-001 | Commit GATE5_SIGNOFF_PENDING.md for Buck review | Browser Claude | Committed |
| [ ] | GATE5-002 | Buck provides explicit go/no-go for full production | @buck-HCI-AI | Written confirmation in chat or Telegram — still open |

### P2 — Operational Documentation (Browser Claude)
| Status | Task ID | Task | Owner | Acceptance Criteria |
|--------|---------|------|-------|---------------------|
| [x] | DOC-001 | CURRENT_SPRINT.md updated to Sprint 3 | Browser Claude | This document |
| [x] | DOC-002 | AI_TEAM/CODE_STATUS_2026-07-01.md — Claude Code offline declaration | Browser Claude | Committed (now superseded, see reconciliation note) |
| [x] | DOC-003 | Sprint 3 gateway directive to Claude Code | Browser Claude | Directive queued in gateway |

---

## Sprint 3 Acceptance Criteria

1. ✅ EMAIL_AUDIT_RESULTS.md committed (EMAIL-001)
2. ✅ All 7 email paths verified gated, via ADRs (EMAIL-002)
3. ✅ 101F schedule variance fixed (DATA-001)
4. ✅ 1355R risks corrected (DATA-002)
5. ✅ Telegram inbound integration tested end-to-end (TEL-001/002)
6. ⏳ Buck provides Gate 5 explicit go/no-go (GATE5-002) — **only open item**
7. ✅ LIVE_PROJECT_STATE.md updated to Sprint 3 (DATA-003)

---

## Blocker Log
| Blocker ID | Description | Raised | Resolved |
|---|---|---|---|
| BLOCK-001 | Branch protection not enabled | 2026-06-26 | ⏳ @buck-HCI-AI: GitHub Settings → Branches |
| BLOCK-005 | Houzz tables empty — Browser DB insert incomplete | 2026-06-27 | ⏳ Browser Claude confirming row counts |
| BLOCK-006 | Gate workflows need n8n credentials for HubSpot + Drive | 2026-06-27 | ⏳ AUTO-014/015 first |
| BLOCK-007 | Claude Code offline — no commits since prior session | 2026-07-01 | ✅ Resolved 2026-07-02 — Code online, active this session |
| BLOCK-008 | EMAIL_AUDIT_RESULTS.md never committed — P0 open | 2026-07-01 | ✅ Resolved — committed 2026-07-01 |
| BLOCK-009 | Gate 5 explicit go/no-go pending Buck decision | 2026-07-01 | ⏳ @buck-HCI-AI — still open |

---

## Gate 5 Pilot Checkpoint — 2026-07-01 (Updated 2026-06-28)

| Item | Status |
|---|---|
| 64 Eastwood | 🟡 2 open risks (test data); gateway endpoints all PASS |
| 101 Francis | 🟢 0-day schedule variance as of 2026-07-02 (the "steel delay" critical risk noted here on 06-28/06-29 came from a test log entry, not a real field condition, and cleared from live data by 07-01); gateway endpoints all PASS |
| 1355 Riverside | 🟢 No field data — GREEN is empty not confirmed |
| 246 Gallo Way | 🟢 Initialized: 280 schedule items, 44 bid packages, all endpoints live |
| 83 Sagebrusch | 🟢 In OS; pending activation |
| Mining engine live | ✅ 03:00 daily runs |
| Architecture Freeze v1.0 | ✅ Declared 2026-06-28 |
| Overnight BUILD-1–6 | ✅ All 6 operational builds complete |
| Gateway audit | ✅ 15/15 endpoints PASS |
| Data integrity | ✅ WF-009 audit clean; 14 dup rows fixed |
| n8n API auth | ✅ Restored 2026-06-28 — Docker VirtioFS restart fixed SQLite I/O error; 42 active workflows |
| Approval queue | ✅ Corrected 2026-06-28 — 986 legitimate vendor approvals (HubSpot mining backlog); 9 true dups deleted |
| 1355R daily log | 🔴 No real field submission — Gate 5 exception |
| 246GW procurement gaps | 🔴 5 critical gaps: elevator (16-20wk lead), venetian plaster ($800K/0 bids), MEP all 3 trades |
| Schedule variance sign bug | ✅ RESOLVED 2026-07-01 — 101F now reports consistently (+5d / -5 days signed) across Executive Report, Mission Control, PM Console, LIVE_PROJECT_STATE.md; regression test added |
| Go-live verdict | ⚠️ READY WITH EXCEPTIONS — see HCI_AI_OS_RECONCILIATION_REPORT_2026-06-28.md in Drive |

---

## Daily Status
| Date | Status | Key Events | Blockers |
|------|--------|-----------|----------|
| 2026-07-01 | Sprint 3 Open | Gate 5 closed. Manual complete (18ch/124KB). Sprint 2 closed. Sprint 3 opened. BC operational. Code briefly offline, back online same day. | BLOCK-009 |
| 2026-07-02 | Sprint 3 Active | Branch divergence discovered and merged (Sprint 7 specs from BC now in repo). Live-system fixes: n8n Docker networking, SQLite WAL, gateway latency, schedule variance daily-zeroing bug. Plan-review pipeline extended. | BLOCK-009 (Gate 5 go/no-go) |

---

*CURRENT_SPRINT.md | HCI AI Operating System | Hendrickson Construction, Inc.*
*Sprint 3 — Production Stabilization | Authorized by: ChatGPT (Chief Architect / ARB), 2026-07-01*
*Reconciled 2026-07-02 after Claude Code / Browser Claude branch merge.*
