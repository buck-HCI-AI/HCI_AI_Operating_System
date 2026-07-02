# CYCLE 41 — Superintendent Morning Brief
**GBT Cycle:** 41
**Sprint:** 8
**Priority:** P1 — Field Operations
**Status:** SPEC — Pending Code + n8n Implementation
**Date:** 2026-07-02
**Author:** Browser Claude (BC)

---

## Problem Statement

Superintendents arrive on site at 7:00 AM. They need a complete project brief in hand BEFORE they walk the job — not after. Currently there is no automated morning brief. Supers must manually query Field GPT or wait for a human to pull status.

This is Sprint 8’s flagship field feature: automated 06:30 MT generation of a mobile-ready brief for each active project.

---

## ADR-S8-003: Field-First Design (existing)
Every Sprint 8 feature is evaluated from the superintendent’s perspective first. The morning brief IS the superintendent’s perspective.

---

## What the Brief Must Contain

Generated at **06:30 MT daily** for each active project. Ready before 7:00 AM site arrival.

### Section 1: Weather
- Today’s forecast (temp, precip, wind)
- Any weather-related work restrictions (concrete pours, crane ops, roofing)
- Source: OpenWeatherMap API (already integrated per CYCLE12)

### Section 2: Schedule Status
- Current gate/phase
- Activities due today
- Any activities overdue or at risk
- Schedule variance in days
- Source: /gateway/project/{code}/brain schedule data

### Section 3: Open RFIs
- Any RFIs with responses due today or overdue
- Blocking RFIs flagged RED
- Source: /gateway/project/{code}/rfis (CYCLE39)

### Section 4: Critical Risks
- High/critical severity risks only
- Any new risks since yesterday
- Source: /gateway/project/{code}/brain risk data

### Section 5: Crew & Subcontractor Notes
- Any subs scheduled today
- Any confirmed no-shows or delays from yesterday
- Source: project brain / field reports

### Section 6: Pending Decisions
- Decisions requiring superintendent input today
- Source: /gateway/project/{code}/brain decisions data

### Section 7: Buck’s Priorities
- Any Buck-flagged priorities for the day
- Source: ai_messages targeted at superintendent role

---

## Delivery Mechanism

### Primary: Telegram
- Send via existing Telegram bot to superintendent’s chat
- Format: plain text, mobile-readable, no markdown tables
- Max length: 4096 chars (Telegram limit) — truncate gracefully

### Secondary: Field GPT
- Field GPT can also call GET /gateway/project/{code}/morning-brief on demand
- Supers can ask: "Give me the morning brief for 101F"

---

## Endpoint Required

### GET /gateway/project/{code}/morning-brief
Returns the pre-generated morning brief for today.

**Response shape:**
```json
{
  "project_code": "101F",
  "generated_at": "2026-07-02T06:30:00MT",
  "brief": {
    "weather": {
      "summary": "Sunny, 78F, winds 8mph SW. No restrictions.",
      "restrictions": []
    },
    "schedule": {
      "current_gate": "GATE2",
      "variance_days": 5,
      "due_today": ["TS02b Steel column erection"],
      "overdue": ["TS02a Steel delivery — 5 days late"]
    },
    "open_rfis": [
      {"id": "RFI-001", "subject": "Axis B framing", "due": "2026-07-05", "status": "open"}
    ],
    "critical_risks": [
      {"description": "Steel supplier delay", "severity": "critical", "days_impact": 5}
    ],
    "pending_decisions": [],
    "buck_priorities": []
  }
}
```

---

## n8n Workflow: WF-BRIEF-001

**Trigger:** Cron — 06:30 MT daily (12:30 UTC)
**Steps:**
1. Get list of active projects from /gateway/portfolio/summary
2. For each project: call /gateway/project/{code}/brain + weather API
3. Assemble brief per template above
4. Store brief in DB (morning_briefs table)
5. Send via Telegram to project superintendent
6. Log delivery status

**Failure handling:**
- If gateway unreachable: send fallback Telegram alert to Buck
- If Telegram fails: log to n8n execution history
- Never silent-fail — always notify

---

## Database Table

```sql
CREATE TABLE morning_briefs (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  brief_date DATE NOT NULL,
  generated_at TIMESTAMPTZ DEFAULT NOW(),
  weather_summary TEXT,
  schedule_summary JSONB,
  open_rfis JSONB,
  critical_risks JSONB,
  pending_decisions JSONB,
  full_text TEXT,
  telegram_sent BOOLEAN DEFAULT FALSE,
  telegram_sent_at TIMESTAMPTZ,
  UNIQUE(project_id, brief_date)
);
```

---

## Success Criteria

- [ ] Brief generated at 06:30 MT for all active projects
- [ ] Delivered via Telegram before 07:00 MT
- [ ] Field GPT can return brief on demand: "morning brief for 101F"
- [ ] Brief readable on mobile (469px) — ADR-S8-003 compliant
- [ ] Weather restrictions flagged when applicable
- [ ] Blocking RFIs highlighted
- [ ] 109/109 existing tests still pass
- [ ] Failure alert sent to Buck if generation fails

---

## Implementation Order

1. Create morning_briefs table (migration)
2. Build GET /gateway/project/{code}/morning-brief endpoint
3. Build WF-BRIEF-001 n8n cron workflow
4. Test with 101F: manually trigger, verify Telegram delivery
5. Add `getMorningBrief` to HCI Field GPT Actions schema

---

## Directive Reference

- Related: CYCLE37_SPRINT8_PREVIEW.md (P1 item), CYCLE12 (weather), CYCLE39 (RFIs)
- ADR: ADR-S8-003 (Field-First Design)
- n8n workflow: WF-BRIEF-001
- Code channel: Post completion to ai_messages
- Superintendents on site: 07:00 MT. Brief must be ready BEFORE that.

---

*Generated by Browser Claude — 2026-07-02 — Per never-stop directive*
