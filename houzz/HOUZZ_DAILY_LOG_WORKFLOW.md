# Houzz Daily Log Workflow
## HCI AI Operating System — Houzz Browser Intelligence Workstream
**Version:** 1.0 | **Created:** 2026-06-26 | **Authority:** HOUZZ_READ_ONLY_AUDIT.md + HCI_AI_CONSTITUTION.md  
**Core Principle:** Superintendent uses Houzz normally. HCI AI reads, extracts, and elevates the intelligence.

---

## Overview

This document defines the end-to-end daily workflow for extracting intelligence from Houzz daily logs and converting them into executive summaries, PM action items, risk alerts, and tomorrow's priorities for Hendrickson Construction, Inc.

The superintendent never changes their behavior. Houzz remains their system. HCI AI listens.

---

## Workflow Participants

| Role | Agent | Action |
|---|---|---|
| Field Execution | Superintendent | Completes daily log in Houzz (unchanged behavior) |
| Data Extraction | Browser Claude | Reads completed Houzz log (read-only) |
| Intelligence Engine | ChatGPT | Analyzes extracted data, generates outputs |
| Orchestration | n8n | Triggers extraction, routes outputs, sends alerts |
| Delivery | Claude Code | Commits structured outputs to repository |
| Review | Human Owner / PM | Reviews summaries, approves any write-back actions |

---

## Step-by-Step Daily Workflow

### Phase 1 — Field Execution (Superintendent, No Change Required)

**Time:** During workday  
**Actor:** Superintendent  
**System:** Houzz Pro

The superintendent completes their Houzz daily log as normal, capturing:
- [ ] Work completed today (narrative)
- [ ] Labor: crew members, trade, hours worked
- [ ] Subcontractors on site (name, trade, headcount)
- [ ] Materials received (item, quantity, vendor, PO reference)
- [ ] Equipment on site
- [ ] Weather conditions (auto-populated or manual)
- [ ] Safety observations
- [ ] Open issues, delays, or problems encountered
- [ ] Photos taken with captions
- [ ] Schedule activities in progress or completed

**Daily log submitted by:** End of day (target: 5:00 PM or earlier)

---

### Phase 2 — Trigger (n8n, Automated)

**Time:** 5:30 PM daily (or on-demand)  
**Actor:** n8n  
**Action:** Trigger Browser Agent extraction sequence

n8n workflow: `houzz-daily-log-reader`
1. Check if current date's daily log is available for each active project
2. If log submitted: trigger Browser Claude extraction
3. If log not yet submitted: wait 30 min, retry up to 3 times
4. If log still not submitted after 6:30 PM: log warning, flag project in status report

---

### Phase 3 — Browser Agent Extraction (Browser Claude, Read-Only)

**Time:** 5:30–6:00 PM daily  
**Actor:** Browser Claude  
**System:** Houzz Pro (browser, read-only)  
**Output:** Structured extraction file

For each active project:

**3.1 Navigate to project daily log**
- Go to Project → Logs → [Today's Date]
- Confirm log is in "submitted" or "completed" state
- Do NOT click edit, approve, or any action button

**3.2 Extract all visible data into structured format:**

```
Daily Log Extraction — [Project Name] — [YYYY-MM-DD]

NARRATIVE:
[Full text of daily log narrative]

LABOR:
- [Name/Trade]: [Hours] hrs — [Area of work]

SUBCONTRACTORS:
- [Company] ([Trade]): [Headcount] workers — [Area]

MATERIALS RECEIVED:
- [Item]: [Qty] [Unit] from [Vendor] — PO: [Reference]

EQUIPMENT:
- [Equipment type]: [Location/use]

WEATHER:
- Conditions: [Description]
- Temperature: [High]/[Low]
- Precipitation: [None/Amount]
- Impact on work: [Yes/No — describe if yes]

SAFETY:
- Incidents: [None / Description]
- Observations: [Text]

OPEN ISSUES:
- [Issue 1 description]
- [Issue 2 description]

PHOTOS:
- Count: [N] photos
- Captions: [List]

SCHEDULE ACTIVITIES:
- In progress: [Activity name] — [% complete]
- Completed today: [Activity name]
- Not started (was planned): [Activity name]

EXTRACTION METADATA:
- Extracted at: [timestamp]
- Agent: Browser Claude
- Project: [name]
- Log status at time of read: [Submitted/Draft]
```

**3.3 Save extraction to repository:**
`reports/houzz/daily/[YYYY-MM-DD]-[project-slug]-log-extraction.md`

---

### Phase 4 — Intelligence Generation (ChatGPT)

**Time:** 6:00–6:30 PM  
**Actor:** ChatGPT  
**Input:** Structured extraction from Phase 3  
**Outputs:** 7 intelligence artifacts

**4.1 Executive Summary**
A 5–7 sentence narrative suitable for a project owner or executive. Covers: work accomplished, crew deployment, weather, key issues, and overall project health signal (Green / Yellow / Red).

**4.2 PM Action Items**
A numbered list of specific, actionable items the PM needs to address tomorrow. Each item includes: what, why, urgency, and who to contact.

**4.3 Schedule Impact Analysis**
- Activities completed vs. planned (ahead/behind/on track)
- Activities not started that were planned (delay flag)
- Estimated schedule variance in days
- Risk to milestone dates

**4.4 Procurement / Delivery Impact**
- Materials received vs. expected
- Missing or late deliveries
- Items to expedite for tomorrow or upcoming days
- Recommended purchase order follow-ups

**4.5 Risk Alert Log**
- Safety incidents or near-misses
- Quality concerns noted in log
- Subcontractor non-performance flags
- Weather-related delay qualification language
- Open RFIs or design conflicts blocking work

**4.6 Lessons Learned Candidates**
Items from today's log that could inform future project planning, estimating, or superintendent guidance.

**4.7 Tomorrow's Priorities**
A ranked list of 3–5 priorities for the superintendent and PM to align on at the next morning huddle.

---

### Phase 5 — Output Delivery (n8n + Claude Code)

**Time:** 6:30–7:00 PM  
**Actor:** n8n (routing) + Claude Code (commits)

**5.1 Commit intelligence artifacts to repository:**
`reports/houzz/intelligence/[YYYY-MM-DD]-[project-slug]-daily-intelligence.md`

**5.2 Route executive summary to designated channel** (internal notification — no client comms):
- PM notification (internal)
- Human owner alert if Red flag detected

**5.3 Log completion:**
`reports/houzz/daily/[YYYY-MM-DD]-extraction-log.md`

---

### Phase 6 — Human Review & Approval Gating

**Actor:** Human Owner / PM  
**Time:** Evening or next morning

PM reviews the daily intelligence report. Any actions that require write-back to external systems go through the appropriate approval gate:

| Proposed Action | Gate Required |
|---|---|
| Update HubSpot deal with project status | Gate H |
| Send update to client | Gate E |
| Create procurement PO | Gate F |
| Archive or delete any Houzz record | Gate D |
| Write schedule update back to Houzz | Gate E (if client-visible) |
| No write-back required | No gate — report only |

---

## Output File Structure

```
reports/
└── houzz/
    ├── daily/
    │   ├── YYYY-MM-DD-[project-slug]-log-extraction.md
    │   └── YYYY-MM-DD-extraction-log.md
    └── intelligence/
        └── YYYY-MM-DD-[project-slug]-daily-intelligence.md
```

---

## Quality Standards

| Output | Standard |
|---|---|
| Extraction completeness | All 10 data categories captured or flagged as missing |
| Executive summary | 5–7 sentences, jargon-free, owner-ready |
| PM action items | Specific, actionable, prioritized |
| Risk alerts | Identified within 30 min of extraction |
| Delivery time | Complete intelligence package by 7:00 PM daily |

---

## Failure Handling

| Scenario | Response |
|---|---|
| Superintendent log not submitted by 6:30 PM | Flag in extraction log; run next morning on previous day's log |
| Browser navigation fails | Log error; retry once; alert human owner if still failing |
| Houzz session expired | Halt; alert human owner to refresh session |
| Extraction incomplete (missing sections) | Deliver partial intelligence with clearly flagged missing sections |
| ChatGPT analysis fails | Deliver raw extraction with flag for human review |

---

*Governed by HCI_AI_CONSTITUTION.md | Houzz Browser Intelligence Workstream | Hendrickson Construction, Inc.*
