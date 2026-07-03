# Job Operations Intelligence Layer
## HCI AI Operating System

**Authority:** Future Directive — future .docx (Buck Adams, 2026-06-27)  
**Status:** Planning — implementation begins after Sprint 2 close  
**Owner:** Chris Hendrickson (Hendrickson Construction) | **HCI-AI Owner / PM & SS:** Buck Adams  

---

## Mission

> Make every active job easier to run for Superintendents, PMs, and HCI leadership.

Every active job generates hundreds of data points per day across Houzz, HubSpot, Drive, email, bids, and schedules. Today those are siloed. The Job Operations Intelligence Layer aggregates them into three role-specific consoles — so each person sees exactly what they need, nothing they don't.

---

## Primary Users

| Role | Primary Need | Frequency |
|---|---|---|
| Superintendent | What do I do today? | Daily — every morning |
| Project Manager | What do I manage this week? | Weekly — Monday morning |
| Owner / Leadership | Which jobs need my attention? | Daily — anytime, phone |

---

## Deliverables

| Document | Purpose |
|---|---|
| [SUPERINTENDENT_DAILY_CONSOLE_SPEC.md](SUPERINTENDENT_DAILY_CONSOLE_SPEC.md) | SS morning brief spec + API design |
| [PM_WEEKLY_CONSOLE_SPEC.md](PM_WEEKLY_CONSOLE_SPEC.md) | PM weekly console spec + API design |
| [LEADERSHIP_DASHBOARD_SPEC.md](LEADERSHIP_DASHBOARD_SPEC.md) | Cross-job leadership view spec |
| [WEEKLY_REPORTING_ENGINE.md](WEEKLY_REPORTING_ENGINE.md) | Automated report generation spec |
| [ROADMAP_JOB_OPERATIONS_LAYER.md](ROADMAP_JOB_OPERATIONS_LAYER.md) | Sprint-by-sprint implementation plan |

---

## API Surface (Role-Based Views)

```
GET /api/v1/superintendent/{project_id}/today     — SS morning brief
GET /api/v1/pm/{project_id}/weekly                — PM weekly console
GET /api/v1/leadership/dashboard                   — Cross-job leadership view
GET /api/v1/reports/weekly/jobs                    — All job reports (Friday)
GET /api/v1/reports/weekly/company                 — Company-level summary (Friday)
```

---

## Data Sources

All intelligence aggregated from existing services — no new data stores required:

| Source | Data | Status |
|---|---|---|
| Houzz | Daily logs, schedule, tasks, budget, files, photos | Connector built ✅ |
| HubSpot | Contacts, deals, activities, comms history | Connector built ✅ |
| Google Drive | Documents, SOPs, reports, photos | Connector needed ⏳ |
| Outlook/email | Client comms, RFI threads, vendor emails | Connector needed ⏳ |
| Bid Leveling | Bid status, award decisions, cost exposure | Service live ✅ |
| Approval Queue | Open decisions, pending authorizations | Service live ✅ |
| Schedule Intelligence | Variance, critical path, lookahead | Service live ✅ |
| Vendor Registry | Vendor contacts, performance, POs | Service live ✅ |
| Historical Cost | Budget vs actual, cost trends | Service live ✅ |
| Project Brain | Project metadata, milestones, risks | Service live ✅ |

---

## Automation Rules

### Daily (runs automatically — no approval needed)
- 06:00 — Generate SS morning brief per active job
- 06:00 — Detect schedule blockers and surface in console
- 06:00 — Draft daily log template with yesterday's activity pre-filled
- 06:00 — Flag weather risks (integration needed: weather API)
- 06:15 — Push SS brief to ntfy + email

### Weekly (runs automatically — no approval needed)
- Friday 16:00 — Generate PM weekly job report per active project
- Friday 16:30 — Generate leadership company-level summary
- Friday 17:00 — Push weekly reports to ntfy + email
- Monday 07:00 — Update project health scores (existing AUTO-010)

---

## Governance

| Action | Approval Required |
|---|---|
| Generate reports, summaries, drafts | No — runs automatically |
| Update dashboard / health scores | No — runs automatically |
| Send client communications | Yes — Gate E (GATE-E-client-comms workflow) |
| Approve budgets / bids / awards | Yes — Gate F (GATE-F-financial workflow) |
| Issue change orders | Yes — approval_queue + ntfy |
| Update HubSpot records | Yes — Gate H (GATE-H-hubspot-write workflow) |

---

## Success Criteria

- Superintendents know what to do today without opening Houzz, Drive, or email
- PMs can manage every project from one screen per week
- Leadership sees all job status in under 60 seconds on phone
- Buck can review all jobs from his phone in under 5 minutes
- All Friday reports generated automatically — zero manual effort

---

*Job Operations Intelligence Layer | HCI AI Operating System | Hendrickson Construction, Inc.*  
*Directive: future .docx 2026-06-27 | Planning complete — awaiting Sprint 3 authorization*
