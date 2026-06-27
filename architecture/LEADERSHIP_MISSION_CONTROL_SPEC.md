# Leadership Mission Control — Specification
*Phase 2, Priority 4 | Active | Updated: 2026-06-27*

## Purpose

Full-portfolio executive view. Answers: "How is the company doing right now?"
in under 60 seconds from any device.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/leadership/dashboard` | Sprint 3 summary dashboard |
| `GET /api/v1/executive/mission-control` | Phase 2 full intelligence view |
| `GET /api/v1/services/cross-project/company-snapshot` | Cross-project deep dive |
| `GET /executive/` | Mobile HTML dashboard |

## Mission Control Response (11 sections)

| Section | Contents |
|---------|----------|
| `company_health` | Portfolio RED/YELLOW/GREEN aggregate |
| `portfolio` | Per-project health + risk counts from `project_brain_snapshots` |
| `ai_missions` | Active/blocked/open/completed mission counts |
| `ai_productivity` | Hours saved, docs processed, errors caught (last 30 days) |
| `pending_approvals` | Count + top 5 items from `approval_queue` |
| `critical_alerts` | HIGH-risk predictions from `predictions_computed` |
| `top_risks` | Critical/high risks from `project_risks_computed` |
| `top_opportunities` | Top ROI automation opportunities |
| `weekly_trends` | 7-day health history from `project_brain_snapshots` |
| `kpi_dashboard` | Latest KPI values from `kpi_snapshots` |
| `procurement_pulse` | Open/awarded package totals across all projects |

## Leadership Dashboard (Sprint 3)

`GET /api/v1/leadership/dashboard` returns:
- `company_health`: overall status
- `projects`: 4-project summary with health, open decisions, risk flags
- `what_needs_me`: prioritized list of items requiring Buck's attention
- `bids_in_flight`: total outstanding bid invitations
- `ai_productivity`: AI automation metrics (6 categories)

## Mobile HTML View

`GET /executive/` — dark theme, auto-refreshes every 60s,
approval action buttons, mission control data feed.
