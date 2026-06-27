# Houzz Read-Only Audit
## HCI AI Operating System — Houzz Browser Intelligence Workstream
**Version:** 1.0 | **Created:** 2026-06-26 | **Authority:** HCI_AI_CONSTITUTION.md + AUTOMATION_GOVERNANCE.md  
**Workstream:** Houzz Browser Intelligence  
**Operating Mode:** READ-ONLY — No write, submit, edit, delete, message, or schedule actions permitted

---

## Purpose

This document defines the scope, boundaries, data inventory, and read-only operating rules for the Houzz Browser Intelligence Layer. It is the governing audit document for all Browser Agent interactions with Houzz on behalf of Hendrickson Construction, Inc.

**Core Principle:** Capture data once in Houzz. Reuse it everywhere in HCI AI.

---

## Constitutional Compliance

This workstream operates under:
- **HCI_AI_CONSTITUTION.md** — Article III, Section 3.1 (Reads are fully autonomous)
- **AUTOMATION_GOVERNANCE.md** — Part 1.1 (Reads, summaries, validation: no approval required)
- **APPROVAL_GATES.md** — Gate E (client comms), Gate H (CRM writes), Gate D (destructive)
- **AI_TEAM_CHARTER.md** — Browser Claude role (read + report only in external systems)

**Absolute Prohibition:** The Browser Agent operating in Houzz MUST NEVER:
- Submit or edit daily logs
- Send messages to clients or project contacts
- Modify schedules or tasks
- Delete photos, logs, or any records
- Change project status, milestones, or budget
- Approve or decline RFIs, submittals, or change orders
- Take any action that creates, modifies, or removes data in Houzz

---

## Houzz Platform Overview (HCI Field Execution)

Houzz Pro (formerly Ivy) serves as the primary field execution platform for Hendrickson Construction, Inc. superintendents and project managers. It provides:

### Data Categories Available for Read

| Data Category | Houzz Module | Read Priority | HCI AI Value |
|---|---|---|---|
| **Daily Logs** | Project → Logs | 🔴 Critical | Labor tracking, work completed, issues flagged |
| **Photos** | Project → Photos | 🔴 Critical | Visual progress documentation, condition records |
| **Weather Logs** | Daily Log → Weather | 🟡 High | Schedule impact analysis, delay justification |
| **Schedule** | Project → Schedule | 🟡 High | Activity status, lookahead, delay detection |
| **Client Communications** | Messages | 🟠 Medium | Client sentiment, open items, approval tracking |
| **Project Updates** | Project → Updates | 🟠 Medium | Milestone tracking, narrative progress |
| **Labor Entries** | Daily Log → Labor | 🟡 High | Crew productivity, cost tracking |
| **Material Deliveries** | Daily Log → Deliveries | 🟡 High | Procurement tracking, just-in-time verification |
| **Subcontractor Activity** | Daily Log → Subs | 🟡 High | Sub performance, schedule compliance |
| **Budget/Cost Tracking** | Financials | 🟢 Low | Cost-to-complete awareness (read-only summary) |
| **Selections** | Selections | 🟢 Low | Client decision status |
| **To-Do Items** | Tasks | 🟢 Low | Open action items |

---

## Browser Agent Access Method

### Access Type
- **Method:** Browser-based navigation (no API assumed)
- **Agent:** Browser Claude operating in Houzz web interface
- **Authentication:** Human owner credentials via existing Houzz session
- **Session:** Read-only; agent does not store credentials

### Navigation Paths (Standard Houzz Pro)

| Data Target | Navigation Path |
|---|---|
| Project List | Dashboard → Projects |
| Daily Log | Project → Logs → [Date] |
| Photos | Project → Photos → [Filter by date] |
| Weather | Daily Log → Weather section |
| Schedule | Project → Schedule |
| Labor | Daily Log → Labor section |
| Deliveries | Daily Log → Materials/Deliveries |
| Client Messages | Project → Messages |
| Project Summary | Project → Overview |

---

## Data Extraction Rules

### Rule 1 — Read, Never Touch
The Browser Agent navigates to each Houzz page, reads and extracts visible text and data, then exits. No clicks on edit, submit, send, delete, or schedule buttons are permitted.

### Rule 2 — Structured Extraction
All extracted data must be converted to structured format before passing to HCI AI for analysis:
- Daily logs → structured JSON or markdown table
- Photos → filename, timestamp, caption, project association
- Weather → date, conditions, high/low temp, precipitation
- Schedule → activity name, planned start/finish, actual status, variance
- Labor → crew name, trade, hours, area of work

### Rule 3 — No Personal Data Beyond Work Context
The Browser Agent does not extract or store personal contact information, private messages, or financial data beyond project-level cost summaries.

### Rule 4 — Daily Extraction Window
Standard extraction occurs once per day after the superintendent closes out the daily log (typically end-of-day). No real-time monitoring or continuous scraping.

### Rule 5 — Audit Log Required
Every Browser Agent Houzz session must be logged with:
- Timestamp of session start and end
- Projects accessed
- Data categories read
- Extraction success/failure per category
- Any anomalies detected

### Rule 6 — No Write-Back Without Gate
Any data derived from Houzz extraction that is to be written to HubSpot, Drive, or any other system must pass through the applicable approval gate before execution.

---

## Data Inventory by Project Type

### Active Construction Project (Standard Daily Read)
- Daily log narrative (text)
- Labor headcount and hours by trade
- Subcontractor presence
- Materials delivered (name, quantity, vendor)
- Work areas active today
- Weather at project site
- Safety observations/incidents
- Open issues or RFIs noted in log
- Photos taken today (count, captions)
- Schedule activities in progress or completed

### Project Startup / Mobilization
- Site access confirmation
- Permit posting status
- Subcontractor mobilization
- Utility locates and protection measures
- Initial schedule baseline read

### Project Closeout
- Punch list items and completion status
- Final inspection scheduling
- As-built documentation completeness
- Certificate of substantial completion
- Client walkthrough scheduling

---

## Houzz Intelligence Gaps (Known Limitations)

| Limitation | Impact | Mitigation |
|---|---|---|
| No official API | Cannot automate server-to-server reads | Browser Agent reads via web UI |
| Session authentication required | Cannot run unattended without login | Human initiates session; agent reads |
| Photo content not machine-readable from thumbnails | Cannot auto-analyze photo content at thumbnail level | Navigate to full-size photos; use vision AI |
| Daily log must be submitted by super before read | Extraction depends on superintendent completing log | Morning extraction reads previous day's closed log |
| Schedule data may require PDF/export for full detail | Web view may be limited | Read visible schedule + flag for export if needed |
| Client messages may be sensitive | Privacy consideration | Read project-level summaries only; full messages require human approval to act on |

---

## Compliance Checklist

- [x] Workstream operates read-only
- [x] No write, edit, delete, message, or schedule actions defined
- [x] All data extraction follows AUTOMATION_GOVERNANCE.md Part 1.1
- [x] Write-back to any system requires applicable approval gate
- [x] Client communications require Gate E before any action
- [x] Session audit logging required for every access
- [x] Governed by HCI_AI_CONSTITUTION.md

---

*Governed by HCI_AI_CONSTITUTION.md | Houzz Browser Intelligence Workstream | Hendrickson Construction, Inc.*
