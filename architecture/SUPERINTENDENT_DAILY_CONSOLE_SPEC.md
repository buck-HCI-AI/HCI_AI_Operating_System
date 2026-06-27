# Superintendent Daily Console — Specification
*Sprint 3 | Active | Updated: 2026-06-27*

## Purpose

Single-screen morning briefing for the job superintendent. Answers:
"What do I need to know and do today?" in under 60 seconds.

## API Endpoint

`GET /api/v1/superintendent/{project_id}/today`

Mobile HTML view: `GET /superintendent/{project_id}` (no auth, dark theme)

## Sections Returned

| Section | Data Source | Description |
|---------|-------------|-------------|
| `health` | Computed | GREEN/YELLOW/RED overall status |
| `project_name` | `projects` | Project name and code |
| `date` | System | Today's date + day of week |
| `safety` | Computed | Daily safety topic (10 rotating topics) |
| `tasks` | `houzz_tasks` | Open tasks assigned to project SS |
| `schedule` | `houzz_schedule_items` | Activities due this week |
| `open_decisions` | `executive_inbox` | Pending items requiring decision |
| `procurement` | `bid_packages`, `bid_entries` | Open scope, pending bids |
| `rfis` | `rfis` | Open RFIs by age |
| `submittals` | `submittals` | Pending submittals overdue |

## Safety Topic Rotation

10 topics rotated by day-of-week index from `_SAFETY_TOPICS` list.
New topic revealed each weekday morning.

## Key Business Rules

- Project health RED if critical risks detected
- SS sees only their assigned project's data
- No auth required for HTML mobile view (internal network only)
