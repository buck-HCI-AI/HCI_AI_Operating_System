# Leadership Dashboard — Specification
## HCI AI Operating System

**Authority:** Milestone 1 — Operational Intelligence  
**Owner:** Chris Hendrickson (Hendrickson Construction) | **HCI-AI Owner / PM & SS:** Buck Adams  
**Status:** Spec — Sprint 3 implementation target  

---

## Purpose

Buck sees every active job clearly in under 60 seconds on his phone.  
One screen. No digging. Green / Yellow / Red. Know exactly which jobs need attention.

---

## Endpoint

```
GET /api/v1/leadership/dashboard
HTML: GET /leadership (mobile-first, existing executive dashboard extended)
```

---

## Dashboard Sections

### 1. Company Health Banner
```
Overall status: GREEN / YELLOW / RED
Active jobs: N
Jobs needing attention: N
Open owner decisions: N
Weekly AI ROI: Xh saved
```

### 2. Project Cards (one per active job)
Each card shows:
```
[STATUS] Project Name — Code
Schedule: +/- X days | Budget: $Xk exposure | Risks: N
Top issue: [most critical item needing attention]
[Approve] [View Details]
```
Color: GREEN = on track | YELLOW = watch | RED = action needed
Sort: RED first, then YELLOW, then GREEN

### 3. Open Owner Decisions
```
Source: executive_inbox WHERE status='pending'
Format: decision card with Approve/Reject/Defer buttons
Max shown: top 5 by deadline, remainder behind "Show All"
```

### 4. Schedule Trends (cross-job)
```
Source: schedule_intelligence across all projects
Chart-friendly data: average_variance_days, jobs_ahead, jobs_behind, jobs_on_track
Trend vs prior week
```

### 5. Budget Exposure (cross-job)
```
Source: houzz_budget + historical_cost across all projects
Total: committed, projected_final, total_exposure
Jobs by exposure (largest first)
```

### 6. AI Productivity
```
Mining runs: today, this week
Documents processed: this week
Decisions automated: this week
Hours saved: this week
Connector syncs: last 24h
```

### 7. What Needs Me? (distilled)
```
Auto-generated top 5 owner actions across all jobs:
Ranked by: deadline urgency × financial impact × days waiting
Format: "101F: Award roofing bid by Friday ($85k) — 2 bids expire"
Actions: tap each → routes to relevant approval or detail
```

---

## API Response Shape

```json
{
  "generated_at": "2026-06-27T07:00:00Z",
  "company_health": "YELLOW",
  "active_projects": 3,
  "projects_needing_attention": 1,
  "open_owner_decisions": 2,
  "weekly_roi_hours": 12.5,
  "projects": [
    {
      "project_id": 1, "code": "101F", "name": "101 Francis",
      "health": "YELLOW",
      "schedule_variance_days": 2, "budget_exposure": 60000,
      "open_risks": 4, "open_decisions": 1,
      "top_issue": "Budget: $60k overrun on electrical scope"
    }
  ],
  "owner_decisions": [...],
  "schedule_trends": { "avg_variance": 1.3, "ahead": 1, "on_track": 1, "behind": 1 },
  "budget_exposure": { "total": 60000, "by_project": [...] },
  "ai_productivity": { "mining_runs_today": 3, "hours_saved_week": 12.5, "decisions_automated": 8 },
  "what_needs_me": [
    "Award roofing bid on 101F — 2 offers expire Friday ($85k decision)",
    "Approve change order CO-003 on 64EW — 32 days unsigned ($28k)",
    "Client check-in needed on 1355R — no contact 9 days"
  ]
}
```

---

## Mobile HTML View

`GET /leadership` — extends existing `/executive` dashboard

Changes from current `/executive`:
- Add project cards with GREEN/YELLOW/RED color coding
- "What Needs Me?" section at top (above everything else)
- Project cards link to `/pm/{project_id}` for drill-down
- 60-second auto-refresh

---

## Health Score Algorithm

Per project, score calculated from:
```python
RED if any:
  - schedule_variance > 7 days
  - budget_overrun > 15%
  - open_decisions_days_waiting > 5
  - critical_path_blocked

YELLOW if any:
  - schedule_variance 3-7 days
  - budget_overrun 5-15%
  - open_decisions_days_waiting 2-5
  - vendor_risk_flagged

GREEN: all else
```

Overall company health = worst individual project health.
