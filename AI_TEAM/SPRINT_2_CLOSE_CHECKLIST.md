# Sprint 2 Close Checklist

## HCI AI Operating System

**Sprint:** Sprint 2 — Registry Consolidation
**Owner:** Buck Adams
**Chief Architect:** ChatGPT
**Implementation:** Claude Code
**Repository Governance:** Browser Claude
**Automation:** n8n
**Status:** Pending ARB Close Review

---

## Close Criteria

Sprint 2 may be closed only when all required items below are verified.

---

## 1. Source of Truth Reconciliation

- [ ] LIVE_PROJECT_STATE.md reflects the current active sprint.
- [ ] CURRENT_SPRINT.md reflects the current active sprint.
- [ ] Sprint 3 status is consistent across gateway, repo, and Mission Control.
- [ ] No conflicting references remain showing Sprint 2 as active if Sprint 3 is live.
- [ ] Any historical Sprint 2 references are clearly labeled as archived or closed.

**ARB Requirement:** Sprint metadata must be consistent before Sprint 2 can be formally closed.

---

## 2. Project Data Corrections

### 101F - Schedule Variance

- [ ] Resolve discrepancy between executive report and live state.
- [ ] Executive report currently shows schedule variance as 1.
- [ ] Live project state indicates 101F has a steel delay of -5 days.
- [ ] Confirm canonical value from schedule intelligence.
- [ ] Patch reporting logic if sign inversion or stale data is confirmed.
- [ ] Add regression test for negative schedule variance.

### 1355R - Risk Count

- [ ] Investigate 1355R risk inflation.
- [ ] Confirm whether executive report risk count is test data or real risk count.
- [ ] If test inflation, correct to 0.
- [ ] Add test to prevent test risk records from appearing in production executive reports.

---

## 3. AI Communication Reliability

- [ ] ai_directives table exists or existing directive table is extended.
- [ ] Directive lifecycle supports: ISSUED / RECEIVED / IN_PROGRESS / COMPLETE / BLOCKED / REJECTED
- [ ] Gateway endpoints exist for directive creation, acknowledgement, status update, and retrieval.
- [ ] Directive records survive restart.
- [ ] Missing acknowledgement detection is implemented.
- [ ] Stale directive detection is implemented.
- [ ] Mission Control reflects directive state.

---

## 4. AI Heartbeat

- [ ] ai_heartbeat table exists.
- [ ] POST /gateway/heartbeat endpoint exists.
- [ ] Heartbeat records include: agent name, role, timestamp, status, current task, last acknowledged directive.
- [ ] Missing heartbeat detection is implemented.
- [ ] Mission Control displays AI team health.

---

## 5. Executive Inbox vs Approval Queue

- [ ] Executive Inbox is defined as operational intake.
- [ ] Approval Queue remains human authorization gate.
- [ ] No merge between Executive Inbox and Approval Queue.
- [ ] Items requiring Buck approval can be promoted from Executive Inbox to Approval Queue.
- [ ] Approval Queue remains authoritative for human decisions.

---

## 6. Tests Required Before Close

- [ ] Create directive.
- [ ] Acknowledge directive.
- [ ] Move directive to IN_PROGRESS.
- [ ] Complete directive.
- [ ] Detect stale acknowledgement.
- [ ] Write heartbeat.
- [ ] Detect stale heartbeat.
- [ ] Verify Mission Control sync.
- [ ] Verify 101F negative variance handling.
- [ ] Verify 1355R test risk exclusion.
- [ ] Verify restart recovery read path.

---

## 7. Documentation

- [ ] Architecture decision recorded for AI communication reliability.
- [ ] Gateway endpoint documentation updated.
- [ ] Mission Control data contract updated.
- [ ] AI Team operating model updated.
- [ ] Sprint 2 closure note prepared.
- [ ] Sprint 3 opening note prepared.

---

## 8. Repository Governance (Browser Claude)

- [ ] No duplicate directive systems.
- [ ] No duplicate approval systems.
- [ ] No duplicate inbox systems.
- [ ] No unmerged production PRs.
- [ ] No unresolved merge conflicts.
- [ ] Main branch reflects production baseline.
- [ ] Documentation matches implementation.

---

## 9. ARB Close Ruling

Sprint 2 may be closed only after all of the above are complete AND:

- [ ] Claude Code returns implementation report.
- [ ] Browser Claude confirms no repository drift.
- [ ] Chief Architect issues ARB close approval.

**Current ARB Status:** NOT APPROVED
**Reason:** Live data discrepancies (101F variance, 1355R risk inflation) and AI communication reliability must be corrected before formal closure.

**ARB Ruling - 101F Variance:** -5 days is the canonical value. Executive report showing 1 is suspect. Claude Code must trace sign bug, fix it, add regression test confirming 101F reports -5 days across live state, PM console, executive report, and Mission Control.

**Conditional path to close:** Claude Code completes data fixes + directive lifecycle + heartbeat endpoint + tests + commit. Browser Claude confirms repo alignment. Chief Architect issues ARB close approval.

---

Issued by: HCI Chief Architect (ChatGPT) via BC OPS WATCH
Committed by: Browser Claude (Operations Intelligence)
Date: 2026-06-30
