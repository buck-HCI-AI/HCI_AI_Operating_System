# BOOK_01 — Volume 07: Daily Logs and Field Reporting

**Version:** 1.0 | **Date:** 2026-06-25

---

## Why the Daily Log Is the Most Important Document on the Job

The daily log is HCI's contemporaneous record of what happened on the job site. In a dispute, claim, or delay analysis, the daily log is the first document produced. A log that says "general construction" is worth nothing. A log that says "Crew of 6 (4 HCI, 2 Miller Electric) placed 32 CY of concrete at Grid E.3-F.6, Level 2 deck. Pour was delayed 2 hours by rain starting at 10 AM. Pour resumed at 12 PM. Inspector from AHJ on site at 2 PM for final pre-pour inspection — passed. Work complete by 4:30 PM." is worth everything.

The system makes detailed logging easy — not harder.

---

## How the Daily Log System Works

**Submission:** The Superintendent submits the daily log via `~/Desktop/HCI_Daily_Log.command`. The script prompts for each required field, then submits via the WF-SUPER API endpoint.

**AI processing:** After submission, AI:
1. Checks the log against the 3-week look-ahead — were planned activities completed?
2. Extracts delays, flags, and risks
3. Checks crew count against budget manpower curve
4. Adds the log to the project record for Project Brain Q&A
5. Generates a summary for the PM's daily digest

**PM review:** PM reviews the AI summary and confirms or adds context. Anomalies escalate to Buck.

---

## Daily Log Workflow (WF-SUPER)

```
Superintendent submits via CLI
  → API validates required fields (project_id, date, weather, work description)
  → Records stored in PostgreSQL (daily_logs table)
  → AI processes log and generates summary
  → Summary delivered to PM by end of day
  → Summary included in next morning's brief
  → Log indexed in Project Brain for Q&A
```

---

## What AI Extracts From Each Log

| Extracted Item | Where It Goes |
|---------------|--------------|
| Crew count and composition | Manpower tracking; budget comparison |
| Delays: cause, duration, scope | Delay log; schedule impact analysis |
| Inspections and results | Inspection log; quality control record |
| Materials received | Procurement tracker |
| Risk and issue flags | Risk log |
| Look-ahead status | Schedule adherence metric |
| Work described by scope/area | Progress tracking; percent complete |

---

## Morning Brief

The morning brief is auto-delivered every day at 7 AM to all active project users. It contains:

| Section | Content |
|---------|---------|
| Weather | Today's forecast: temp, conditions, precipitation chance |
| Schedule | Top 3 priority activities from look-ahead |
| Open flags | Issues flagged in prior day's log or by AI overnight |
| Budget | Any new variances > 5% since last brief |
| Open RFIs/submittals | Due or overdue items |
| Crew | Expected on-site complement based on current commitments |
| Safety | Any outstanding safety items |

---

## Field Reporting Cadence

| Report | Frequency | Author | AI Role | Delivered To |
|--------|-----------|--------|---------|-------------|
| Daily log | Daily | Superintendent | Processes and summarizes | PM, Project Record |
| Daily brief | Daily | AI (auto) | Generates from data | All project users |
| Look-ahead | Weekly (Monday) | Superintendent | Cross-checks schedule | PM |
| Weekly status | Weekly (Friday) | PM (AI draft) | Drafts from data | Buck, Client |
| Monthly report | Monthly | PM + Buck | AI compiles data | Owner/Client as required |

---

## Data Quality Controls

Log submissions are validated at input:
- `project_id` must match an active project
- `date` must be a working day (system flags holiday/weekend submission for review)
- `weather` is required
- `work_description` minimum 50 characters (enforces specificity)
- Duplicate submission for same project + date requires override

A log that fails validation is returned with specific error messages — not silently accepted with empty fields.

---

## Field Reporting KPIs

| KPI | Target |
|-----|--------|
| Daily log submission rate | 100% of working days per active project |
| Logs submitted by 6 PM | > 95% |
| Logs with specific work description (> 50 chars) | 100% (enforced) |
| PM daily digest reviewed | Same day as submission |
| Morning brief delivered by 7 AM | 100% (automated) |

---

*WF-SUPER workflow: `03_Source_Code/api/routers/wf_super.py`*  
*Daily log table: `daily_logs` in PostgreSQL*  
*Submission command: `~/Desktop/HCI_Daily_Log.command`*
