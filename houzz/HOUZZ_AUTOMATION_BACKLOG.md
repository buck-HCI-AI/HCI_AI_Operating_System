# Houzz Automation Backlog
## HCI AI Operating System — Houzz Browser Intelligence Workstream
**Version:** 1.0 | **Created:** 2026-06-26 | **Authority:** SPRINT_OPERATING_MODEL.md  
**Parent Backlog:** PROJECT.md — Automation Backlog  
**All items follow:** SPRINT_OPERATING_MODEL.md sprint document chain

---

## Workstream Summary

The Houzz Browser Intelligence workstream converts Houzz field data into structured executive intelligence without changing superintendent behavior. This backlog defines all implementation tasks needed to bring the full intelligence layer to production.

**Core Principle:** Capture data once in Houzz. Reuse it everywhere in HCI AI.

---

## Sprint Assignments

| Sprint | Theme | Houzz Tasks |
|---|---|---|
| Sprint 1 | System Verification | Manual extraction template, reports folder structure |
| Sprint 2 | Registry Consolidation | n8n trigger automation, project registry integration |
| Sprint 3 | HubSpot & Drive Integration | HubSpot status write (HZ-H1), Drive report filing |
| Sprint 4 | Workflow Certification | End-to-end daily log workflow, PM action items |
| Sprint 5 | MCP Implementation | Schedule intelligence, photo metadata |
| Sprint 6 | Historical Project Mining | Backlog of historical Houzz log extraction |
| Sprint 7 | Executive Dashboards | Portfolio health view, executive brief |
| Sprint 8 | Production Validation | Full pipeline test, scorecard |
| Sprint 9 | Go Live | Production deployment, daily automation live |

---

## Backlog — Sprint 1 (System Verification)

### HZ-001 — Houzz Daily Log Reader (Manual)
**Priority:** 🔴 Critical  
**Sprint:** Sprint 1  
**Label:** `workflow` `n8n`  
**Assigned To:** Browser Claude  
**Description:** Establish the manual Houzz daily log extraction workflow. Browser Claude navigates to each active project's Houzz daily log and extracts structured data using the HCI Data Schema v1.0 defined in HOUZZ_BROWSER_AGENT_STRATEGY.md.

**Acceptance Criteria:**
- [ ] Browser Claude successfully reads a complete Houzz daily log for at least one active project
- [ ] All 10 data categories extracted (or explicitly flagged as missing)
- [ ] Output saved to `reports/houzz/daily/YYYY-MM-DD-[project-slug]-log-extraction.md`
- [ ] Extraction log saved to `reports/houzz/daily/YYYY-MM-DD-extraction-log.md`
- [ ] No write, edit, or submit actions taken in Houzz
- [ ] Passes HOUZZ_READ_ONLY_AUDIT.md compliance checklist

**Dependencies:** Active Houzz session (human-initiated)

---

### HZ-002 — Reports Folder Structure
**Priority:** 🔴 Critical  
**Sprint:** Sprint 1  
**Label:** `workflow` `documentation`  
**Assigned To:** Claude Code  
**Description:** Create the reports/ directory structure for Houzz intelligence outputs.

**Structure to create:**
```
reports/
└── houzz/
    ├── daily/           # Daily log extractions + session logs
    ├── intelligence/    # Processed intelligence reports
    ├── schedule/        # Schedule snapshots and variance reports
    ├── photos/          # Photo metadata extractions
    └── portfolio/       # Cross-project views
```

**Acceptance Criteria:**
- [ ] All directories created with `.gitkeep` placeholder files
- [ ] `reports/houzz/README.md` created explaining folder structure
- [ ] Committed to main via PR

---

### HZ-003 — Houzz Project Registry Entry
**Priority:** 🟡 High  
**Sprint:** Sprint 1  
**Label:** `registry` `workflow`  
**Assigned To:** Claude Code  
**Description:** Add Houzz as a registered integration in the Integration Registry (05_Database/).

**Acceptance Criteria:**
- [ ] Houzz entry added to Integration Registry with: system name, access method, data categories, auth model, gate references
- [ ] Entry notes: no official API, browser-based access
- [ ] Integration Registry updated per schema

---

## Backlog — Sprint 2 (Registry Consolidation)

### HZ-004 — n8n Daily Log Extraction Trigger
**Priority:** 🔴 Critical  
**Sprint:** Sprint 2  
**Label:** `n8n` `workflow`  
**Assigned To:** n8n  
**Description:** Build the n8n workflow that triggers the Houzz daily log extraction sequence at 5:30 PM daily for all active projects.

**Acceptance Criteria:**
- [ ] n8n workflow `houzz-daily-log-reader` created and documented in 04_Workflows/
- [ ] Workflow triggers at 5:30 PM daily
- [ ] Checks active project list from registry
- [ ] Triggers Browser Claude extraction for each active project
- [ ] Retries up to 3 times if log not yet submitted
- [ ] Logs trigger result to extraction log
- [ ] Sends alert if log not available by 6:30 PM

---

### HZ-005 — Houzz-to-HCI-AI Project Health Engine
**Priority:** 🔴 Critical  
**Sprint:** Sprint 2  
**Label:** `workflow` `registry`  
**Assigned To:** ChatGPT + n8n  
**Description:** Build the intelligence analysis pipeline that takes structured Houzz extraction data and produces the 7 intelligence artifacts: executive summary, PM action items, schedule impact, procurement impact, risk alerts, lessons learned candidates, tomorrow's priorities.

**Acceptance Criteria:**
- [ ] ChatGPT prompt templates created for each of the 7 artifacts
- [ ] n8n workflow passes extraction data to ChatGPT and receives outputs
- [ ] All 7 artifacts committed to `reports/houzz/intelligence/`
- [ ] Report format matches HOUZZ_DAILY_LOG_WORKFLOW.md Phase 4 specification
- [ ] Health signal (Green/Yellow/Red) computed and attached to each report
- [ ] End-to-end test: extraction → analysis → report in < 30 min

---

## Backlog — Sprint 3 (HubSpot & Drive Integration)

### HZ-006 — HubSpot Project Status Write (Gate HZ-H1)
**Priority:** 🟡 High  
**Sprint:** Sprint 3  
**Label:** `hubspot` `workflow`  
**Assigned To:** n8n  
**Description:** Implement Gate HZ-H1 — the approval workflow for writing Houzz-derived project health signals to HubSpot deal records.

**Acceptance Criteria:**
- [ ] n8n workflow prepares HubSpot write payload from daily intelligence report
- [ ] Approval request routed to human owner with full context
- [ ] On approval: HubSpot deal updated via Gate H process
- [ ] Gate log written to `reports/gates/gate-HZ-H1-log.md`
- [ ] Batch approval option supported (multiple projects in one review)

---

### HZ-007 — Drive Daily Intelligence Filing
**Priority:** 🟡 High  
**Sprint:** Sprint 3  
**Label:** `drive` `workflow`  
**Assigned To:** n8n  
**Description:** Automatically file each day's intelligence report to the correct project folder in Google Drive (AI working folder — no gate required).

**Acceptance Criteria:**
- [ ] n8n workflow identifies correct Drive project folder by project name/ID
- [ ] Intelligence report filed as: `YYYY-MM-DD-[project]-daily-intelligence.md`
- [ ] Filed to: `HCI AI Working / Projects / [Project Name] / Daily Intelligence /`
- [ ] Filing logged with timestamp

---

## Backlog — Sprint 4 (Workflow Certification)

### HZ-008 — Daily Executive Brief from Houzz
**Priority:** 🔴 Critical  
**Sprint:** Sprint 4  
**Label:** `workflow` `n8n`  
**Assigned To:** ChatGPT + n8n  
**Description:** Produce a single daily executive brief that aggregates all active project intelligence into a portfolio-level summary for the human owner.

**Acceptance Criteria:**
- [ ] Executive brief compiled from all active project intelligence reports
- [ ] Brief includes: portfolio health summary (# Green/Yellow/Red), top risks, top PM actions, schedule highlights
- [ ] Delivered to human owner by 7:00 PM daily
- [ ] Committed to `reports/houzz/portfolio/YYYY-MM-DD-executive-brief.md`
- [ ] Length: 1 page equivalent (< 500 words)

---

### HZ-009 — PM Action Item Extractor
**Priority:** 🟡 High  
**Sprint:** Sprint 4  
**Label:** `workflow`  
**Assigned To:** ChatGPT + n8n  
**Description:** Extract and aggregate PM action items across all active projects into a single prioritized PM action list, delivered with the daily brief.

**Acceptance Criteria:**
- [ ] PM action items extracted from each project's daily intelligence
- [ ] Cross-project action list ranked by urgency
- [ ] Each action includes: project, action, urgency, contact needed
- [ ] Delivered with daily executive brief
- [ ] Committed to `reports/houzz/portfolio/YYYY-MM-DD-pm-actions.md`

---

## Backlog — Sprint 5 (MCP Implementation)

### HZ-010 — Houzz Schedule Reader
**Priority:** 🟡 High  
**Sprint:** Sprint 5  
**Label:** `workflow` `mcp`  
**Assigned To:** Browser Claude  
**Description:** Extend Browser Agent to extract Houzz schedule data: activity list, planned vs. actual dates, percent complete, and schedule variance.

**Acceptance Criteria:**
- [ ] Browser Claude reads Houzz schedule view for each active project
- [ ] Extracts: activity name, planned start/finish, actual start/finish, % complete, status
- [ ] Calculates variance (days ahead/behind) per activity
- [ ] Identifies critical path activities at risk
- [ ] Output saved to `reports/houzz/schedule/YYYY-MM-DD-[project]-schedule.md`
- [ ] Schedule intelligence integrated into daily executive brief

---

### HZ-011 — Houzz Photo Intelligence Extractor
**Priority:** 🟢 Medium  
**Sprint:** Sprint 5  
**Label:** `workflow` `mcp`  
**Assigned To:** Browser Claude + ChatGPT  
**Description:** Extract photo metadata from Houzz (count, captions, timestamps, work area) and pass to vision AI for content analysis.

**Acceptance Criteria:**
- [ ] Browser Claude navigates to project photos and reads metadata for all photos taken today
- [ ] Extracts: filename, timestamp, caption, work area (from caption or log context)
- [ ] Passes metadata to ChatGPT for content classification
- [ ] Photo summary included in daily intelligence report
- [ ] Output saved to `reports/houzz/photos/YYYY-MM-DD-[project]-photos.md`
- [ ] Read-only: no photo upload, deletion, or annotation

---

## Backlog — Sprint 8 (Production Validation)

### HZ-012 — Superintendent Daily Log Draft Assistant
**Priority:** 🟢 Medium  
**Sprint:** Sprint 8  
**Label:** `workflow` `n8n`  
**Assigned To:** ChatGPT + n8n  
**Description:** Build the advisory draft assistant that pre-populates a morning Houzz log draft for the superintendent based on yesterday's open issues, today's planned schedule, expected deliveries, and weather forecast. Superintendent always controls submission.

**Acceptance Criteria:**
- [ ] Morning draft (5:30 AM) generated from: yesterday's open issues, planned schedule activities, procurement schedule, weather forecast API
- [ ] Draft formatted as Houzz daily log structure (ready to copy into Houzz)
- [ ] Draft clearly marked "AI DRAFT — SUPERINTENDENT REVIEW REQUIRED"
- [ ] Delivered to superintendent via designated internal channel
- [ ] AI never submits or prefills the Houzz form directly
- [ ] Gate E applies if any client-visible content is included

---

## Backlog — Sprint 9 (Go Live)

### HZ-013 — Full Houzz Intelligence Pipeline — Production
**Priority:** 🔴 Critical  
**Sprint:** Sprint 9  
**Label:** `production` `workflow`  
**Assigned To:** n8n + all agents  
**Description:** Full end-to-end Houzz intelligence pipeline running in production: extraction → analysis → reporting → HubSpot update → Drive filing → executive brief → PM actions, delivered daily by 7:00 PM.

**Acceptance Criteria:**
- [ ] Production readiness scorecard passing for all Houzz components
- [ ] All HZ gates tested and operational
- [ ] 5 consecutive days of successful daily extraction and reporting
- [ ] Executive brief delivered on time 5 consecutive days
- [ ] Human owner approves go-live
- [ ] All workflows documented in 04_Workflows/

---

## Task ID Reference

| ID | Task Name | Sprint | Priority |
|---|---|---|---|
| HZ-001 | Houzz Daily Log Reader (Manual) | Sprint 1 | 🔴 Critical |
| HZ-002 | Reports Folder Structure | Sprint 1 | 🔴 Critical |
| HZ-003 | Houzz Project Registry Entry | Sprint 1 | 🟡 High |
| HZ-004 | n8n Daily Log Extraction Trigger | Sprint 2 | 🔴 Critical |
| HZ-005 | Houzz-to-HCI-AI Project Health Engine | Sprint 2 | 🔴 Critical |
| HZ-006 | HubSpot Project Status Write (Gate HZ-H1) | Sprint 3 | 🟡 High |
| HZ-007 | Drive Daily Intelligence Filing | Sprint 3 | 🟡 High |
| HZ-008 | Daily Executive Brief from Houzz | Sprint 4 | 🔴 Critical |
| HZ-009 | PM Action Item Extractor | Sprint 4 | 🟡 High |
| HZ-010 | Houzz Schedule Reader | Sprint 5 | 🟡 High |
| HZ-011 | Houzz Photo Intelligence Extractor | Sprint 5 | 🟢 Medium |
| HZ-012 | Superintendent Daily Log Draft Assistant | Sprint 8 | 🟢 Medium |
| HZ-013 | Full Houzz Intelligence Pipeline — Production | Sprint 9 | 🔴 Critical |

---

*Governed by SPRINT_OPERATING_MODEL.md + HCI_AI_CONSTITUTION.md | Houzz Browser Intelligence Workstream | Hendrickson Construction, Inc.*
