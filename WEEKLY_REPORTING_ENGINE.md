# Weekly Reporting Engine — Specification
## HCI AI Operating System

**Authority:** Milestone 1 — Operational Intelligence  
**Owner:** Buck Adams (PM & Superintendent, Hendrickson Construction, Inc. — owned by Chris Hendrickson; Owner/operator, HCI-AI)  
**Status:** Spec — Sprint 3 implementation target  

---

## Purpose

Every Friday, automatically generate:
1. One job report per active project (for PM + SS)
2. One company-level executive summary (for Buck + leadership)

Zero manual effort. Reports auto-delivered via email and stored in Drive.

---

## Report 1: Weekly Job Report (per project)

**Trigger:** Friday 16:00 (n8n: AUTO-WEEKLY-JOB)  
**Endpoint:** `GET /api/v1/reports/weekly/jobs?project_id={id}`  
**Output:** Markdown + email  

### Sections

1. **Executive Summary** — 3 bullets: what happened, biggest risk, what's next
2. **Work Completed** — from houzz_daily_logs + houzz_tasks completed this week
3. **Schedule Progress** — variance, items completed, lookahead for next week
4. **Risks and Blockers** — open risks ranked by severity + age
5. **Cost / Budget Changes** — new commitments, budget adjustments, COs this week
6. **Approvals Needed** — pending items requiring owner or PM decision
7. **Client Issues** — open RFIs, unanswered client communications
8. **Vendor Performance** — who showed up, who didn't, any issues
9. **Photos / Documents Added** — count of new files added to Houzz/Drive this week
10. **Next Week Plan** — top 5 priorities auto-derived from schedule + open items
11. **AI Recommendations** — top 2-3 actions AI recommends based on data patterns

### Delivery
- Email to PM + SS assigned to project
- Stored as markdown in `reports/weekly/{project_code}/weekly-{date}.md`
- Summary card added to executive_inbox for Buck review

---

## Report 2: Company-Level Executive Report

**Trigger:** Friday 16:30 (n8n: AUTO-WEEKLY-COMPANY)  
**Endpoint:** `GET /api/v1/reports/weekly/company`  
**Output:** Markdown + email  

### Sections

1. **Status of All Active Jobs** — project card table with health indicators
2. **Projects at Risk** — any RED or YELLOW projects with detail
3. **Schedule Trends** — week-over-week variance movement across portfolio
4. **Cost Trends** — budget exposure changes this week vs prior week
5. **Vendor Trends** — performance patterns, recurring issues
6. **Approval Bottlenecks** — decisions >3 days waiting, by project
7. **Top 5 Decisions Needed** — ranked owner decisions for next week
8. **AI Productivity / ROI** — mining runs, hours saved, documents processed, automations fired
9. **Recommendations for Next Week** — top 3 cross-job recommendations

### Delivery
- Email to Buck + leadership
- Stored as `reports/weekly/company/executive-{date}.md`
- Push notification via ntfy: "Weekly summary ready — N jobs, $Xk exposure, N decisions needed"

---

## API Response Shapes

### Job Report
```json
{
  "project_id": 1,
  "project_code": "101F",
  "week_of": "2026-06-27",
  "health": "YELLOW",
  "executive_summary": ["2 of 4 milestones complete", "$60k cost exposure on electrical", "Award roofing bid next week"],
  "work_completed": [...],
  "schedule": { "variance_days": 2, "completed_items": 12, "next_week": [...] },
  "risks": [...],
  "budget": { "original": 1250000, "current_exposure": 60000, "new_cos": [...] },
  "approvals_needed": [...],
  "client_issues": [...],
  "vendor_performance": [...],
  "files_added": { "count": 8, "photos": 5, "documents": 3 },
  "next_week_priorities": [...],
  "ai_recommendations": [...]
}
```

### Company Report
```json
{
  "week_of": "2026-06-27",
  "company_health": "YELLOW",
  "projects": [...],
  "projects_at_risk": [...],
  "schedule_trends": { "avg_variance": 1.3, "trend": "improving" },
  "cost_trends": { "total_exposure": 60000, "change_vs_prior": -10000 },
  "vendor_trends": [...],
  "approval_bottlenecks": [...],
  "top_5_decisions": [...],
  "ai_roi": { "hours_saved": 12.5, "automations_fired": 47, "documents_processed": 23 },
  "recommendations": [...]
}
```

---

## n8n Workflows Needed

| Workflow | Cron | Action |
|---|---|---|
| AUTO-WEEKLY-JOB | Fri 16:00 | GET /reports/weekly/jobs for each active project → email PM + SS |
| AUTO-WEEKLY-COMPANY | Fri 16:30 | GET /reports/weekly/company → email Buck + push ntfy |
| AUTO-SS-MORNING | Mon-Fri 06:00 | GET /superintendent/{id}/today for each active project → push ntfy |
| AUTO-PM-WEEKLY | Mon 07:00 | GET /pm/{id}/weekly for each active project → push ntfy |
