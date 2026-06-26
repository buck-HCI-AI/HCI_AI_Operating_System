# BOOK_00 § 10 — Project Manager Workflow (WF-PM)

**Status:** 🔜 Spec complete — build in Phase 9.3 (after WF-SUPER produces daily log data)

---

## Purpose

The PM Workflow gives Buck a daily structured project controls review for each active project. It pulls intelligence from every service, surfaces what needs attention, and produces a weekly report.

**PM Workflow ≠ Morning Brief.** Morning Brief is a 7 AM digest across all projects. The PM Workflow is a deep per-project review triggered when Buck needs to examine a specific project's health.

---

## Trigger

- `POST /api/v1/workflows/wf-pm/daily-review/{project_number}` — manual per project
- `POST /api/v1/workflows/wf-pm/weekly-report` — automated Friday 4 PM

---

## Daily Review — Inputs

The PM daily review pulls from all active intelligence services:

| Area | Source | Data |
|------|--------|------|
| Project status | Project Brain | Snapshot: scope, status, bid packages, activity |
| Budget | Bid Intelligence | Low bid per package, awarded amount, total exposure |
| Procurement | Procurement Service | Long-lead items due, PO status, open items |
| RFIs / Submittals | risks table + Project Brain | Open RFIs, outstanding submittals (Phase 9.5) |
| Change orders | (future table) | CO log, pending vs. approved |
| Owner communication | HubSpot notes + Project Brain | Recent correspondence, pending decisions |
| Risk | Risk Intelligence | Open risks by severity |
| Schedule | Schedule Intelligence | Variance flags, lookahead, delays |

---

## Daily Review — Outputs

1. **PM Checklist** — structured JSON per project, stored in `workflow_events`
2. **PM Summary Email** — HTML email (optional, on demand)
3. **Project Brain Cache Invalidation** — force refresh of Project Brain on data change
4. **Risk flags** — new risks written to `risks` table if detected by Claude review
5. **Weekly Report contribution** — daily checklist rows accumulate for weekly rollup

---

## Weekly Report — Output Format

```
WEEKLY PROJECT REPORT — {Project Name} — Week of {Date}

SCHEDULE STATUS
  Baseline completion: {date}
  Current forecast: {date}
  Variance: {days}
  Cause: {summary}

BUDGET STATUS
  Contract value: ${amount}
  Committed cost: ${amount}
  Variance: ${amount} ({pct}%)

PROCUREMENT
  On track: {n} items
  At risk: {n} items
  Action needed: {list}

OPEN RISKS
  {risk list by severity}

OWNER ITEMS PENDING
  {list from HubSpot notes}

NEXT WEEK PRIORITIES
  {Claude-generated summary}
```

---

## Architecture

```python
# wf_pm.py (to be built)

class PMWorkflow:
    def daily_review(self, project_number: str) -> dict:
        brain = requests.get(f"/api/v1/services/project-brain/{project_number}").json()
        bids  = requests.get(f"/api/v1/services/bid-intelligence/summary?project_number={project_number}").json()
        proc  = requests.get(f"/api/v1/services/procurement/status?project_number={project_number}").json()
        risks = requests.get(f"/api/v1/services/risk-intelligence/{project_number}").json()
        sched = requests.get(f"/api/v1/services/schedule-intelligence/{project_number}").json()
        
        # Claude synthesizes checklist from all sources
        checklist = BaseIntelligenceService.ask_claude(
            prompt=build_pm_prompt(brain, bids, proc, risks, sched),
            system=PM_SYSTEM_PROMPT
        )
        
        # Log event
        log_workflow_event("wf-pm", project_number, "daily_review", checklist)
        return checklist
```

---

## PM Workflow Output → Project Brain

After each PM review, if the review reveals new information:
- New risks are written to `risks` table
- Project Brain cache is invalidated
- Next Project Brain query reflects current PM assessment

---

## Build Dependencies

- Project Brain ✅ (ready)
- Bid Intelligence ✅ (ready)
- Procurement Service ✅ (ready, no data yet)
- Risk Intelligence ✅ (ready, no data yet)
- Schedule Intelligence ⚠️ (partial — needs WF-SUPER data)
- workflow_events table 🔜 (Phase 8.3)
- WF-SUPER producing daily logs 🔜 (Phase 9.1)
