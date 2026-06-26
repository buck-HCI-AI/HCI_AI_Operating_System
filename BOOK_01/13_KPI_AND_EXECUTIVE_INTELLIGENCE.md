# BOOK_01 — Volume 13: KPI and Executive Intelligence

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

---

## What KPI Intelligence Is

KPI Intelligence is the layer that answers Buck's most important questions:

- How is the company performing right now?
- Which projects are at risk?
- Is HCI meeting its bid margin targets?
- Are subcontractors performing as expected?
- Is preconstruction producing competitive bids?

These questions are answered from structured data — not from assembling a report from email.

---

## Two Levels of KPIs

### Company-Level KPIs

These measure HCI as a business across all active projects:

| KPI | Target | Source |
|-----|--------|--------|
| Bid win rate | > 30% | Bid log |
| Bid margin average | ≥ 8% (configurable) | Bid intelligence |
| Total revenue at risk (active projects) | < 15% of backlog | Budget + risk service |
| Change order revenue as % of contract | < 8% | CO log |
| Closeout days past substantial completion | < 45 days avg | Closeout tracker |
| Sub non-compliance rate | 0% (zero tolerance) | Procurement service |
| Project gross margin vs. bid margin | Within 2% avg | Budget vs. actual |
| Project on-time completion rate | > 80% | Schedule tracker |
| Outstanding receivables > 60 days | Alert | Invoice tracker |

### Project-Level KPIs

These measure each active project:

| KPI | Target | Source |
|-----|--------|--------|
| Budget variance by scope line | < 10% any line | Budget service |
| Schedule variance: planned vs. actual | ≤ 7 days on critical path | Schedule service |
| Open RFIs > 14 days | 0 | RFI log |
| Punch items open > 30 days | 0 | Punch list |
| Change orders submitted within 10 days | > 90% | CO log |
| Daily log completion rate | 100% | Log tracker |
| Sub compliance on site | 100% | Compliance tracker |

---

## KPI Data Sources

Every KPI is connected to a specific data source — no manual entry:

| KPI Group | Primary Source |
|-----------|---------------|
| Budget, cost, variance | PostgreSQL `project_budgets`, `cost_postings` |
| Schedule performance | `schedule_intelligence` service |
| Bid performance | `bid_intelligence` service |
| Field operations | `daily_logs` table |
| Change order performance | `change_orders` table |
| RFI performance | `rfis` table |
| Sub compliance | `procurement` service |
| Vendor performance | `vendor_intelligence` service |

---

## Executive Dashboard

The executive dashboard is Buck's real-time view of HCI's operating state. It shows:

**Company snapshot:** Total active contract value | Total bids out | Win rate (last 12 months) | Gross margin trend

**Project cards:** One card per active project — traffic light status (green/yellow/red) on budget, schedule, and compliance

**Alert feed:** Items requiring Buck's attention today — approvals needed, red flags, decisions required, threshold breaches

**Bid pipeline:** Active bid opportunities, proposals in progress, recent awards

**Decision queue:** Decisions awaiting Buck's approval or sign-off

---

## KPI Thresholds and Escalation

All KPI thresholds are configurable in the Operating Rules Engine — not hardcoded:

| Threshold | Default | Escalation Path |
|-----------|---------|-----------------|
| Budget variance yellow | 5% on any scope line | PM notified |
| Budget variance red | 10% on any scope line | PM + Buck notified |
| Schedule variance yellow | 3 days behind | Superintendent + PM notified |
| Schedule variance critical | 7 days on critical path | PM + Buck notified |
| Bid margin below target | < 8% | Buck notified before submission |
| Sub non-compliance | Any | PM + Buck notified immediately |

---

## KPI Intelligence Service

Service path: `03_Source_Code/services/kpi_intelligence/`

- `GET /api/v1/kpis/company` — company-level dashboard
- `GET /api/v1/kpis/project/{id}` — project-level KPI snapshot
- `GET /api/v1/kpis/alerts` — all current threshold breaches
- `GET /api/v1/kpis/trend?metric={name}&period={days}` — trending data
- `POST /api/v1/kpis/threshold` — update a threshold (admin)

---

## Weekly Executive Report

Every Friday, AI assembles the weekly executive report for Buck:

1. Company KPI snapshot vs. last week
2. Active project status (one line per project — budget, schedule, open flags)
3. Alerts from the week requiring Buck's attention
4. Decision queue: items awaiting Buck
5. Bid pipeline status
6. Next week outlook: milestones, deadlines, key decisions expected

Format: brief — one page. AI compiles; Buck reads in 5 minutes.

---

*Standard: `docs/KPI_EXECUTIVE_INTELLIGENCE_STANDARD.md`*  
*Service: `03_Source_Code/services/kpi_intelligence/`*  
*Thresholds configured in: `03_Source_Code/services/operating_rules/`*
