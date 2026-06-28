# BOOK_00 § 13 — Reporting and Dashboards

**Status:** ✅ LIVE — Built 2026-06-26/28. Executive reporting via GBT Gateway (/gateway/executive/report and /gateway/executive/mission-control). n8n workflows: AUTO-WEEKLY-EXEC, AUTO-PM-WEEKLY, AUTO-DAILY-PROJECT-SUMMARY, AUTO-WEEKLY-JOB, AUTO-WEEKLY-COMPANY all active. Weekly email reports running Friday 16:00. Morning brief 07:00 daily.

---

## Report Types

| Report | Frequency | Audience | Trigger |
|--------|-----------|----------|---------|
| Daily Field Report | Daily | Buck, Super | WF-SUPER completion |
| Weekly PM Report | Weekly (Friday) | Buck, PM | WF-PM Friday trigger |
| Schedule Variance Report | On detection | Buck, PM, Owner | schedule_variance write |
| Procurement Risk Report | Weekly | Buck, PM | Monday AM |
| Executive Project Health | Weekly | Buck | Friday PM |
| Owner Summary | On request | Owner | Manual trigger |

---

## Data Sources for All Reports

All reports pull exclusively from the API layer:

| Data | Source |
|------|--------|
| Project overview | `GET /api/v1/services/project-brain/{project}` |
| Bid status | `GET /api/v1/services/bid-intelligence/summary` |
| Schedule | `GET /api/v1/services/schedule-intelligence/{project}` + schedule_variance table |
| Procurement | `GET /api/v1/services/procurement/status` |
| Risks | `GET /api/v1/services/risk-intelligence/{project}` |
| Workflow events | `workflow_events` table |
| Historical | `GET /api/v1/services/historical-cost/bid-vs-actual/{project}` |

**Rule:** Reports do not query PostgreSQL directly. They consume Intelligence Service endpoints.

---

## Daily Field Report

**Trigger:** Automatic after WF-SUPER daily log submission  
**Delivery:** Saved to MinIO `hci-reports/daily/` + email draft in Outlook

```
DAILY FIELD REPORT — 64 Eastwood — June 25, 2026

CREW ON SITE
  High-Con Concrete: 4
  HCI: 2

WORK PERFORMED
  Poured footings on north side, set formwork for stem walls.

DELIVERIES
  Rebar — Meadow Valley Steel

INSPECTIONS
  ✅ Footing inspection passed — City of Aspen

CONSTRAINTS / RISKS
  ⚠️ Crane not available until Thursday — may delay stem wall pour

SCHEDULE STATUS
  Footings: 60% complete (50% planned) — slightly ahead
  Stem walls: Start date at risk (crane)

TOMORROW LOOKAHEAD
  Stem wall pour Thursday; framing starts Monday
```

---

## Weekly PM Report

**Trigger:** Friday 4 PM (launchd)  
**Delivery:** Email to buck@ahmaspen.com + MinIO archive

Aggregates 5 daily PM reviews into:
- Schedule variance summary
- Budget exposure (low bids vs. budget)
- Procurement at-risk items
- Open risks requiring decision
- Owner communication actions pending
- Next week priorities (Claude-synthesized)

---

## Schedule Variance Report

**Trigger:** Immediate on detection by Schedule Intelligence  
**Delivery:** Appended to next Morning Brief + optional email alert

Format: see BOOK_00 § 12.

---

## Executive Project Health Report

**Trigger:** Friday PM (automated)  
**Audience:** Buck (owner view)

Single-page HTML showing all active projects:

| Project | Schedule | Budget | Procurement | Risk | Action |
|---------|----------|--------|-------------|------|--------|
| 64 Eastwood | ⚠️ | ✅ | — | Med | Crane decision |
| 101 Francis | ✅ | ✅ | — | Low | — |
| 1355 Riverside | — | ✅ | — | Low | — |

---

## Owner-Facing Summary

**Trigger:** Manual (`POST /api/v1/workflows/wf-report/owner-summary/{project}`)  
**Audience:** Property owner  
**Format:** Clean, professional HTML — no internal cost data, no vendor names, no risk details unless pre-approved

Focuses on: schedule milestone status, upcoming events, decisions needed from owner, next steps.

---

## Dashboard (Phase 10.2)

**Tech:** HTML + vanilla JS, served as FastAPI static files  
**URL:** `http://localhost:8000/dashboard` (or ngrok)

No new backend required — the dashboard is a read-only UI over existing API endpoints.

```
┌────────────────────────────────────────────┐
│  HCI Dashboard    [Project selector ▼]     │
├────────────────────────────────────────────┤
│  64 Eastwood — Exterior & Site             │
│  Status: Active | Bids: 35 packages        │
│                                            │
│  BID COVERAGE        RISK LEVEL            │
│  ████████░░ 62%      ⚠️ Medium             │
│                                            │
│  RECENT ACTIVITY                           │
│  Jun 25 - Footing pour, inspection passed  │
│  Jun 24 - High-Con concrete bid received   │
│                                            │
│  ASK PROJECT BRAIN                         │
│  [What is the framing budget?        ] Ask │
│  Answer: No framing bid received yet...    │
└────────────────────────────────────────────┘
```

**Serves:** Buck's daily project view. Not a public-facing tool.
