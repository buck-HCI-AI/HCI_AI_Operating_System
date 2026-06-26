# BOOK_00 § 11 — Superintendent Workflow (WF-SUPER)

**Status:** 🔜 Spec complete — build in Phase 9.1. Absorbs WF-004 Daily Log.

---

## Purpose

The Superintendent Workflow is the field execution interface. It captures what happened on site every day, feeds that data into Schedule Intelligence and Project Brain, and surfaces field risks before they become schedule problems.

**This is the highest-priority new workflow.** Without daily log data, Schedule Intelligence, Risk Intelligence, and PM reporting are all running on empty.

---

## Trigger

- `POST /api/v1/workflows/wf-super/daily-log` — field submission (same URL as old WF-004, backward compatible)
- On-demand via mobile form (future) or API call

---

## Input: Daily Log Fields

```json
{
  "project_number": "64EW",
  "log_date": "2026-06-25",
  "weather": "Sunny, 72°F",
  "temp_high": 72,
  "temp_low": 48,
  "crew_on_site": [
    {"trade": "Concrete", "company": "High-Con", "count": 4},
    {"trade": "General", "company": "HCI", "count": 2}
  ],
  "work_performed": "Poured footings on north side, set formwork for stem walls",
  "deliveries": ["Rebar delivery — Meadow Valley Steel"],
  "inspections": ["Footing inspection passed — City of Aspen"],
  "quality_notes": "Minor honeycomb on NE corner footing — patched",
  "safety_notes": "All crew helmets and vests confirmed",
  "subcontractor_progress": "High-Con 60% complete on footings vs 50% planned",
  "constraints": ["Crane not available until Thursday"],
  "lookahead": "Stem wall pour Thursday, framing starts Monday",
  "field_risks": ["Crane delay may push framing start 2 days"],
  "issues": "",
  "photos_count": 12,
  "logged_by": "Buck Adams"
}
```

---

## Database Changes (Phase 9.1)

Extend `daily_logs` table:

```sql
ALTER TABLE daily_logs
  ADD COLUMN manpower        JSONB,
  ADD COLUMN deliveries      JSONB,
  ADD COLUMN inspections     JSONB,
  ADD COLUMN quality_notes   TEXT,
  ADD COLUMN safety_notes    TEXT,
  ADD COLUMN subcontractor_progress TEXT,
  ADD COLUMN constraints     JSONB,
  ADD COLUMN lookahead       TEXT,
  ADD COLUMN field_risks     JSONB,
  ADD COLUMN logged_by       TEXT;
```

---

## Processing Pipeline

On daily log submission:

```
1. SAVE → daily_logs table (Postgres)
2. EMBED → Qdrant project_memory (vectorize work_performed + issues + field_risks)
3. ANALYZE → Schedule Intelligence: compare to scheduled activities (Phase 9.2)
4. FLAG RISKS → if constraints or field_risks present → write to risks table
5. INVALIDATE → Project Brain cache for this project
6. LOG EVENT → workflow_events table
7. RETURN → confirmation with any auto-detected risks or schedule flags
```

---

## Output

```json
{
  "log_id": 47,
  "project": "64 Eastwood",
  "date": "2026-06-25",
  "saved": true,
  "schedule_analysis": {
    "planned_activities": ["Footings 100%"],
    "actual_progress": "Footings 60%",
    "variance": "40% behind — may impact stem wall pour date",
    "flags": ["SCHEDULE RISK: Crane delay may push framing 2 days"]
  },
  "risks_written": 1,
  "project_brain_cache": "invalidated"
}
```

---

## Backward Compatibility

`POST /api/v1/workflows/wf004/daily-log` will call WF-SUPER internally. WF-004 Python file will become a thin wrapper. No external callers need to change URLs.

---

## Mobile Input (Future Phase 10)

A simple web form at `http://localhost:8000/field` (or ngrok URL) served by FastAPI static files. Fields map directly to the JSON above. Photos upload to MinIO `hci-photos`. No native app required — mobile browser only.

---

## Build Dependencies

- daily_logs table ✅ (exists, needs new columns)
- workflow_events table 🔜 (Phase 8.3)
- risks table ✅ (exists)
- Schedule Intelligence Service ✅ (partial — will receive data after this)
- Project Brain ✅ (cache invalidation works)
