# PM Weekly Console — Specification
*Sprint 3 | Active | Updated: 2026-06-27*

## Purpose

Single weekly operational view for the Project Manager. Answers:
"What needs my attention this week?" covering budget, procurement, RFIs, and priorities.

## API Endpoint

`GET /api/v1/pm/{project_id}/weekly`

Mobile HTML view: `GET /pm/{project_id}` (no auth, dark theme)

## Sections Returned

| Section | Data Source | Description |
|---------|-------------|-------------|
| `health` | Computed | GREEN/YELLOW/RED |
| `budget` | `houzz_budget` | Budgeted vs actual vs committed |
| `rfis` | `rfis` | Open RFIs + overdue |
| `submittals` | `submittals` | Pending approval with deadlines |
| `change_orders` | `houzz_change_orders` | Unsigned COs + $ value |
| `procurement` | `bid_packages`, `bid_entries` | Packages status, bids outstanding |
| `open_decisions` | `executive_inbox` | Decisions blocking progress |
| `next_week_priorities` | Computed | Auto-generated top 5 actions |

## Procurement Metrics

- `packages`: total bid packages for project
- `open_packages`: not yet awarded
- `bids_out`: bid invitations sent, awaiting response
- `avg_bid_response_days`: average time to first bid

## Priority Generation

Auto-generated from most critical open items across all sections:
1. Unsigned COs > $25K
2. Overdue submittals
3. Stale RFIs (>14 days)
4. Pending decisions
5. Open bid packages near deadline
