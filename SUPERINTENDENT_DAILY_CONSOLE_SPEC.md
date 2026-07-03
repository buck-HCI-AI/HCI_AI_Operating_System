# Superintendent Daily Console — Specification
## HCI AI Operating System

**Authority:** Job Operations Intelligence Layer Directive  
**Owner:** Buck Adams (PM & Superintendent, Hendrickson Construction, Inc. — owned by Chris Hendrickson; Owner/operator, HCI-AI)  
**Status:** Spec — ready for Sprint 3 implementation  

---

## Purpose

The SS console answers one question every morning: **What do I need to do today on this job?**

Delivered as:
- API response at `GET /api/v1/superintendent/{project_id}/today`
- Push notification at 06:00 via ntfy
- Email summary at 06:15
- Mobile-first HTML page at `/superintendent/{project_id}`

---

## Console Sections

### 1. Today's Schedule
```
Source: houzz_schedule_items WHERE due_date = TODAY
Fields: task_name, assigned_to, start_time, end_time, status
Alert: items with status='behind' or past due_date
```

### 2. Open Tasks
```
Source: houzz_tasks WHERE status != 'complete' AND due_date <= TODAY + 3
Fields: title, assigned_to, due_date, priority, blocking_item
Sort: overdue first, then by due_date
```

### 3. Required Inspections
```
Source: houzz_tasks WHERE task_type ILIKE '%inspection%' AND due_date = TODAY
Fields: inspection_type, time, required_by, pass_conditions
Alert: no inspection record → flag as needs scheduling
```

### 4. Trade / Vendor Arrivals
```
Source: houzz_schedule_items + houzz_vendors + houzz_subcontractors
Filter: expected_date = TODAY
Fields: trade_name, company, contact_phone, scope, mobilization_notes
```

### 5. Weather Risks
```
Source: weather API (future integration — OpenWeatherMap or NWS)
Project location → forecast for next 48h
Alert triggers: rain >0.25in, wind >25mph, temp <32F or >95F
```

### 6. Open Blockers
```
Source: houzz_tasks WHERE status='blocked' + executive_inbox WHERE project relates
Fields: blocker_description, blocking_since, escalation_path
Actions: tap to escalate to PM (routes to executive_inbox)
```

### 7. Daily Log Draft
```
Source: yesterday's houzz_daily_logs + today's schedule
Pre-fill: work completed (from yesterday log), planned work (from today schedule)
Draft delivered as editable text — SS fills in actual work, weather, issues
Goal: 80% of the log pre-written by AI, SS reviews and submits
```

### 8. Photos Needed
```
Source: houzz_tasks WHERE requires_photo=true + inspection items
Fields: what to photograph, why, where to upload
Reminder: unphoto'd inspection items flagged RED
```

### 9. Safety Reminders
```
Source: project_brain.safety_plan + houzz_tasks WHERE category='safety'
Daily: toolbox talk topic (rotating), active safety holds
Weekly: safety inspection due dates
```

### 10. Issues to Escalate to PM
```
Source: Automated detection rules:
  - Schedule items >2 days behind
  - Budget line items >10% over
  - Blocked tasks >48h unresolved
  - RFIs open >5 business days
  - Vendor no-show (scheduled but no arrival log)
Format: pre-drafted escalation message for SS to review and send (Gate E)
```

---

## API Response Shape

```json
{
  "project_id": 1,
  "project_code": "101F",
  "project_name": "101 Francis",
  "date": "2026-06-27",
  "generated_at": "2026-06-27T06:00:00Z",
  "health": "YELLOW",
  "schedule": { "items_today": 4, "overdue": 1, "items": [...] },
  "tasks": { "open_count": 7, "overdue_count": 2, "items": [...] },
  "inspections": { "required_today": 1, "items": [...] },
  "vendor_arrivals": { "expected_count": 3, "items": [...] },
  "weather_risk": { "level": "LOW|MEDIUM|HIGH", "forecast": "...", "alerts": [] },
  "blockers": { "count": 1, "items": [...] },
  "daily_log_draft": { "work_completed": "...", "planned_work": "...", "issues": "" },
  "photos_needed": { "count": 2, "items": [...] },
  "safety": { "toolbox_topic": "...", "active_holds": [] },
  "escalate_to_pm": { "count": 0, "items": [] }
}
```

---

## Mobile HTML View

Route: `GET /superintendent/{project_id}` (HTML response)

Layout:
- Card-based, scrollable
- Color-coded: 🟢 on-track / 🟡 watch / 🔴 action-needed
- Each section collapsible
- "Escalate to PM" button → fires Gate E with pre-drafted message
- "Mark Complete" on tasks → updates houzz_tasks (dry_run=false when authorized)

---

## Automation

```
n8n: AUTO-SS-MORNING (new workflow)
Cron: 06:00 daily, all active projects
For each project:
  1. GET /superintendent/{project_id}/today
  2. Format push message (top 3 items)
  3. Send ntfy push: "101F today: 4 tasks, 1 overdue, 1 inspection"
  4. Email summary to assigned SS (n8n Gmail node)
```

---

## Implementation Notes

- All reads — no writes without approval (daily log draft is read-only until SS confirms)
- Escalate to PM goes through Gate E (GATE-E-client-comms) — SS reviews before sending
- Photo reminders link to Houzz mobile app (deep link format: `houzz://project/{id}`)
- Weather integration is a future add-on — stub in response with `"source": "pending"`
