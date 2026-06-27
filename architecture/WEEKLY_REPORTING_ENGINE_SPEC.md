# Weekly Reporting Engine — Specification
*Sprint 3 | Active | Updated: 2026-06-27*

## Purpose

Automated Friday 4pm reports delivered via ntfy push notification.
Covers per-job status and company-wide summary without manual effort.

## Endpoints

| Endpoint | n8n Trigger | Description |
|----------|-------------|-------------|
| `GET /api/v1/reports/weekly/jobs` | AUTO-WEEKLY-JOB (Friday 16:00) | Per-job reports for all active projects |
| `GET /api/v1/reports/weekly/jobs?project_id={id}` | — | Single project report |
| `GET /api/v1/reports/weekly/company` | AUTO-WEEKLY-COMPANY (Friday 16:30) | Company-wide weekly summary |

## Job Report Contents

Each job report combines:
- `superintendent_today` data for the project
- `pm_weekly` data for the project

Fields: health, project_name, project_code, date_range, week_summary,
tasks, schedule, procurement, budget, rfis, change_orders, priorities.

## Company Report Contents

- `company_health`: aggregate portfolio status
- `projects`: 4-project summary each with job report
- `what_needs_me`: cross-project items for leadership
- `bids_in_flight`: total active bid invitations
- `ai_productivity`: weekly automation metrics

## Automation Schedule

| Workflow | Schedule | Target |
|----------|----------|--------|
| AUTO-SS-MORNING | Mon-Fri 06:00 | SS push notification |
| AUTO-PM-WEEKLY | Monday 07:00 | PM push notification |
| AUTO-WEEKLY-JOB | Friday 16:00 | ntfy + disk write |
| AUTO-WEEKLY-COMPANY | Friday 16:30 | ntfy + disk write |
