# Browser Agent Directive — Houzz Monitoring Project Extraction
## HCI AI Operating System
**Issued:** 2026-06-30  
**Updated:** 2026-06-30 (Round 2 — monitoring projects only)  
**Issued By:** Claude Code  
**Authorized By:** Buck Adams (HCI-AI Owner; PM & Superintendent at Hendrickson Construction)  
**Priority:** HIGH

---

## CONTEXT (READ THIS FIRST)

A prior BC extraction (2026-06-28) covered 101 Francis and 1355 Riverside — those are done.  
**This extraction targets the MONITORING projects** — completed or near-complete jobs with years of rich data (daily logs, photos, budgets, change orders). These are the most valuable projects for the AI system.

---

## TARGET PROJECTS — IN PRIORITY ORDER

| Priority | Project Name | What to look for |
|----------|-------------|-----------------|
| 1 | **275 Sunnyside** (or "275 Sunnyside Lane") | Rich: daily logs, budget, COs, photos |
| 2 | **574 Johnson** (or "574 Johnson Drive") | Rich: daily logs, budget, COs |
| 3 | **606 Starwood** (or "606 Starwood Olson") | Rich: daily logs, COs |
| 4 | **813 McSkimming** (or "807 McSkimming" or "McSkimming Spitzley") | Rich: full project data |
| 5 | Any other completed/monitoring projects you see | Get what you can |

**Skip or do minimal extraction on:** 64 Eastwood (not in Houzz), 101 Francis (done), 1355 Riverside (done, empty in Houzz).

**READ ONLY — no edits, no messages, no submits, no writes to Houzz.**

---

## STEP 1 — List all projects in Houzz Pro

Go to the Houzz Pro dashboard → Projects. List every project you see. Note each project name and status.

---

## STEP 2 — For each project, extract ALL of the following

Priority order for each project:

### A. Daily Logs (most valuable)
- Every daily log entry: date, weather, temperature, crew count
- Work summary / what was done today
- Observations, issues, safety notes
- Material deliveries noted
- Sub activity noted
- Photos attached (note URLs, count, and descriptions)

### B. Schedule
- All schedule items with: title, start date, end date, status (Not Started / In Progress / Complete)
- Completion percentage if shown
- Any flagged or delayed items

### C. Change Orders
- CO number, title, description, amount ($), status (pending/approved/rejected), date

### D. Budget / Financials (if visible)
- Budget line items by trade/category
- Budget vs. actual or committed amounts
- Any cost codes visible

### E. Time Entries / Labor
- Date, crew member, hours, trade/role
- Total hours per week if summarized

### F. Selections (finish selections)
- Item name, category (tile/fixture/flooring/etc.)
- Brand, model, status (pending/approved/ordered/delivered)

### G. Tasks / Open Items
- Task description, assigned to, due date, status

### H. Team / Subs on project
- Company name, role (GC/framing/electrical/etc.), contact name

---

## STEP 3 — Save the extracted data

**Option A — Write to DB via API (preferred):**
POST structured JSON to: `http://localhost:8000/gateway/field/daily-report`

For daily logs:
```
POST http://localhost:8000/gateway/field/daily-report
{
  "project_code": "64EW",  // or whichever project
  "date": "2026-06-29",
  "weather": "Partly cloudy, 72F",
  "crew_size": 12,
  "work_summary": "...",
  "observations": [...],
  "issues": [...],
  "source": "houzz_extraction"
}
```

**Option B — Write structured markdown files:**
Save to: `/Users/buckadams/HCI_AI_Operating_System/reports/houzz/{project_name}/`
File naming: `YYYY-MM-DD-daily-log.md`, `schedule.md`, `change-orders.md`, etc.

**Option C — Write directly to DB via docker:**
```bash
docker exec -i hci_postgres psql -U hci_admin -d hci_os
```
Then INSERT into `houzz_daily_logs`, `houzz_change_orders`, `project_schedule_items`, etc.

---

## STEP 4 — Completion report

When done with each project, note:
- Project name
- Date range of daily logs extracted (e.g., "Jan 2025 — Jun 2026")
- Counts: X daily logs, Y schedule items, Z change orders, N photos documented
- Any data that wasn't accessible or was empty

Write completion summary to:
`/Users/buckadams/HCI_AI_Operating_System/AI_TEAM/HOUZZ_EXTRACTION_COMPLETION_REPORT.md`

---

## DB table mapping (where to write each data type)

| Data Type | Table | Key Columns |
|-----------|-------|-------------|
| Daily logs | `houzz_daily_logs` | project_id, log_date, content, weather, crew_size, author |
| Schedule items | `project_schedule_items` | project_id (text), title, start_date, end_date, status, task_type |
| Change orders | `houzz_change_orders` | houzz_project_id, co_number, title, amount, status, submitted_date |
| Budget | `houzz_budget` | project_id, category, budgeted_amount, actual_amount |
| Selections | `houzz_selections` | project_id, item_name, category, brand, status |
| Tasks | `houzz_tasks` | project_id, title, assigned_to, due_date, status |
| Team members | `houzz_team_members` | project_id, name, role, company |
| Time entries | `houzz_time_entries` | project_id, entry_date, worker_name, hours, trade |

**Project ID mapping (our DB ID → Houzz project name):**
| Our project_code | Our DB id | Houzz project name (approximate) |
|-----------------|-----------|----------------------------------|
| 64EW | 1 | 64 Eastwood |
| 101F | 2 | 101 Francis |
| 1355R | 3 | 1355 Riverside |
| 246GW | 8 | 246 Gallo Way / Chaparral |
| 275SS | 16 | 275 Sunnyside |
| 574J | 17 | 574 Johnson |
| 606SW | 25 | 606 Starwood |
| 813MS | 14 | 813 McSkimming |

---

## READ-ONLY RULES (ABSOLUTE)

- NO editing any record in Houzz
- NO submitting any form
- NO sending any message
- NO clicking approve/reject/send
- NO deleting anything
- READ AND EXTRACT ONLY

---

*Authorized by Buck Adams — PM & Superintendent, Hendrickson Construction, Inc. / Owner, HCI-AI*
