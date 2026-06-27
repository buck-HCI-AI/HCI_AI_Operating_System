# Executive Dashboard — Technical Specification
## HCI AI Operating System v2.1

**Authority:** Chief Architect Directive — v2.1 (Item 1)  
**Owner:** Buck Adams  
**Target Sprint:** Sprint 3 (2026-07-07 → 2026-07-21)  
**Design principle:** Mobile-first. One screen. No scrolling for critical info.

---

## Overview

A single-page executive dashboard at `http://localhost:8000/executive`.  
Auto-refreshes every 60 seconds. No login required (internal network only).  
Same data available as JSON at `GET /api/v1/executive/dashboard`.

---

## Screen Layout (Mobile-First)

```
┌─────────────────────────────────────┐
│  HCI AI — Jun 27 · 07:14           │
│  🟢 All Systems Operational         │
├─────────────────────────────────────┤
│  PROJECTS                           │
│  64 Eastwood    🟡 +1d  2 risks    │
│  101 Francis    🟡 +2d  4 risks    │
│  1355 Riverside 🟢  0d  0 risks    │
├─────────────────────────────────────┤
│  AI ACTIVITY                        │
│  Mining Engine  ✅ Ran 03:00       │
│  HouzzMiner     ⏸ Awaiting data   │
│  Browser Claude ● Active            │
├─────────────────────────────────────┤
│  INBOX  ████░░░░  5 decisions       │
│  [EXEC-001] Merge vendors  [→]      │
│  [EXEC-002] Houzz 101F    [→]      │
├─────────────────────────────────────┤
│  RISKS                              │
│  HIGH  0    MED  6    LOW  0       │
├─────────────────────────────────────┤
│  ROI THIS WEEK                      │
│  Hours saved: 29.7h                 │
│  Documents processed: 62            │
├─────────────────────────────────────┤
│  RECOMMENDED NEXT ACTION            │
│  ▶ Approve EXEC-002 (30 seconds)   │
│    Unblocks Houzz intelligence      │
└─────────────────────────────────────┘
```

---

## API Endpoint Spec

### `GET /api/v1/executive/dashboard`

No auth required (internal only — add auth before any external exposure).

**Response:**
```json
{
  "generated_at": "2026-06-27T07:14:00Z",
  "system_health": {
    "status": "healthy",
    "services_up": 7,
    "services_down": 0,
    "alert": null
  },
  "projects": [
    {
      "id": 1,
      "code": "64EW",
      "name": "64 Eastwood",
      "health": "yellow",
      "schedule_variance_days": 1,
      "open_risks": 2,
      "hubspot_deal_id": "331240861419"
    }
  ],
  "ai_activity": {
    "mining_last_run": "2026-06-27T03:00:00Z",
    "mining_status": "completed",
    "houzz_miner": "paused",
    "browser_claude": "active",
    "active_missions": 2,
    "blocked_missions": 2
  },
  "inbox": {
    "total_decisions": 5,
    "oldest_days": 1,
    "items": [
      {
        "id": "EXEC-001",
        "title": "Merge 6 vendor groups",
        "recommendation": "Approve",
        "confidence": "High",
        "deadline": null,
        "approve_url": "http://localhost:8000/api/v1/executive/approve/EXEC-001",
        "reject_url": "http://localhost:8000/api/v1/executive/reject/EXEC-001"
      }
    ]
  },
  "risks": {
    "high": 0,
    "medium": 6,
    "low": 0,
    "total": 6
  },
  "roi": {
    "hours_saved_this_week": 29.7,
    "documents_processed": 62,
    "risks_detected": 31
  },
  "recommended_next_action": {
    "action": "Approve EXEC-002",
    "reason": "Unblocks Houzz intelligence pipeline",
    "estimated_time": "30 seconds",
    "url": "http://localhost:8000/api/v1/executive/approve/EXEC-002"
  }
}
```

### `GET /api/v1/executive/morning-brief`

Condensed 5-item brief for mobile/email:

```json
{
  "date": "2026-06-27",
  "health": "🟢 All systems operational",
  "top_items": [
    "64EW: +1 day behind, 2 risks",
    "101F: +2 days behind, 4 risks — Houzz data pending",
    "1355R: On track",
    "5 decisions in Executive Inbox — EXEC-002 is highest priority",
    "Mining ran at 03:00 — 0 new critical items"
  ],
  "one_action": "Approve EXEC-002 (101 Francis Houzz write) — 30 seconds, unblocks intelligence"
}
```

### `POST /api/v1/executive/approve/{exec_id}`
### `POST /api/v1/executive/reject/{exec_id}`
### `POST /api/v1/executive/defer/{exec_id}`

One-tap approval endpoints. Called from email link or dashboard button.  
Executes approved action immediately (if AUTO/LOW) or queues to Claude Code via EXECUTIVE_INBOX.md (if MEDIUM/OWNER).

---

## Implementation Plan (Sprint 3)

**Week 1:**
1. Build `/api/v1/executive/dashboard` JSON endpoint
2. Build `/api/v1/executive/morning-brief` JSON endpoint
3. Create `03_Source_Code/api/routers/executive.py`
4. Add to main.py (no auth, /executive prefix)

**Week 2:**
5. Build dashboard HTML page (`static/executive/index.html`)
6. Auto-refresh via `setInterval(fetch, 60000)`
7. Mobile CSS: 375px viewport first, expand for desktop
8. n8n workflow: email digest at 07:30 using morning-brief endpoint

**No external dependencies:** All data from FastAPI. Works on local network. No cloud required.

---

## Dashboard Card — Executive Inbox Item

Each inbox item is a card with one action:

```
┌─────────────────────────────────────┐
│ EXEC-001                            │
│ Merge 6 vendor groups               │
│ ─────────────────────────────────── │
│ Recommendation: ✅ APPROVE          │
│ Confidence: High                    │
│ Impact: Cleaner vendor reporting    │
│ Risk: Low — fully reversible        │
│ Deadline: No deadline               │
│ ─────────────────────────────────── │
│  [APPROVE]  [DEFER]  [REJECT]      │
└─────────────────────────────────────┘
```

---

## Email Digest Format (07:30 Daily)

Subject: `HCI AI — Jun 27 · 5 decisions · All systems green`

```
Good morning Buck,

SYSTEM: 🟢 All 7 services operational

PROJECTS:
• 64 Eastwood: 🟡 +1 day · 2 risks
• 101 Francis: 🟡 +2 days · 4 risks  
• 1355 Riverside: 🟢 On schedule

TODAY'S DECISIONS (5):
1. [APPROVE] Merge 6 vendor groups → approve in 1 tap
2. [APPROVE] Write 101 Francis Houzz data → unblocks intelligence
3. [APPROVE] Import Pacific Concrete bid ($185K)
...

ONE ACTION:
Approve EXEC-002 (30 seconds) → Houzz intelligence begins

[OPEN DASHBOARD] [VIEW ALL DECISIONS]

HCI AI Operating System
```

---

*Executive Dashboard Spec | HCI AI Operating System v2.1 | 2026-06-27*
