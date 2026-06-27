# HCI AI Operating System v2.1 — Operational Autonomy Roadmap
## Phase: Executive Experience + Self-Managing System

**Date:** 2026-06-27  
**Authority:** Chief Architect Directive — v2.1 Planning  
**Owner:** Buck Adams  
**Prerequisite:** v2.0 Phase II complete ✅ (committed 2026-06-27)

> "Reduce Buck's daily interaction to executive decisions only."

---

## What v2.1 Delivers

v2.0 built the coordination layer.  
v2.1 makes it **invisible to Buck**.

| v2.0 | v2.1 |
|---|---|
| Buck reads markdown files | Buck opens one dashboard |
| Buck reads approval queue | Buck gets a card with one tap to approve |
| Buck checks email for updates | System pushes a morning brief to his phone |
| Buck asks "what's the status?" | System proactively sends status |
| Buck coordinates agents via conversation | Agents coordinate autonomously |

---

## Roadmap

### Sprint 3 — Executive Dashboard (Target: 2026-07-07 → 2026-07-21)

**Priority: P1**

| Deliverable | Owner | Notes |
|---|---|---|
| `GET /api/v1/executive/dashboard` endpoint | Claude Code | Live JSON snapshot |
| `GET /api/v1/executive/morning-brief` endpoint | Claude Code | 5-item condensed brief |
| Executive Dashboard HTML (`/executive`) | Claude Code | Auto-refresh, mobile-responsive |
| Email digest at 07:30 daily | n8n | Buck's inbox — compact, actionable |
| Upgrade Executive Inbox to card format | Claude Code | Decision/Recommendation/Impact/Deadline per card |

**Acceptance criteria:** Buck opens `http://localhost:8000/executive` on his phone and sees live status without scrolling.

---

### Sprint 4 — Autonomous Mission Management (Target: 2026-07-21 → 2026-08-04)

**Priority: P1**

| Deliverable | Owner | Notes |
|---|---|---|
| Idle agent detector | n8n + Claude Code | Detects no activity > 4h → assigns next mission |
| Blocked work escalator | n8n | Detects BLOCKED > 24h → moves to Executive Inbox |
| Automatic mission assignment logic | AI_PROGRAM_MANAGER.md v2 | Rules: next OPEN mission by priority |
| Dependency graph | MISSION_QUEUE.md v2 | Mission → depends on → Mission |
| Completion events | Event Bus | Mission COMPLETE → auto-trigger next |
| Post-mission checklist (auto-execute) | `scripts/post_mission.py` | Docs, tests, state update |

**Acceptance criteria:** A mission completes at 03:00. By 07:00 the next mission is assigned and in progress — no Buck action.

---

### Sprint 5 — Universal Connector Expansion (Target: 2026-08-04 → 2026-08-18)

**Priority: P2**

| Connector | Current State | Sprint 5 Target |
|---|---|---|
| Houzz | Reference impl — data pending | Framework-certified post data load |
| HubSpot | Active, non-framework | Aligned to 7-stage pipeline |
| Google Drive | Active, non-framework | Aligned to 7-stage pipeline |
| Microsoft 365 | Active, non-framework | Aligned to 7-stage pipeline |
| QuickBooks | Not started | ACR required before build |
| Procore | Not started | ACR required before build |

**Acceptance criteria:** All 4 active connectors show green on connector health dashboard.

---

### Sprint 6 — Mobile Executive Experience (Target: 2026-08-18 → 2026-09-01)

**Priority: P2** — see `MOBILE_EXECUTIVE_EXPERIENCE.md` for full spec

| Deliverable | Notes |
|---|---|
| Morning Brief push notification | 07:00 daily via ntfy.sh |
| One-tap email approvals | Approve link in email → webhook → executes |
| iOS Shortcut "HCI Brief" | Opens dashboard URL |
| Weekend Summary | Saturday 08:00 condensed weekly review |
| Travel Mode | Simplified output — top 3 items only |

**Acceptance criteria:** Buck approves a vendor merge from his phone while at a job site.

---

### Sprint 7 — Autonomous Improvement Engine (Target: 2026-09-01+)

**Priority: P3** — see `AUTONOMY_BACKLOG.md` for initial opportunities

| Deliverable | Notes |
|---|---|
| Manual task detector | Mining engine detects recurring patterns |
| Automation proposal generator | Drafts ACR for each detected pattern |
| ROI tracker per automation | Time saved per week, per automation |
| Annual architecture self-review | System assesses its own gaps |

**Acceptance criteria:** System identifies a recurring Buck task and presents an automation proposal without being asked.

---

## Success Metrics

| Metric | v2.0 Baseline | v2.1 Target |
|---|---|---|
| Buck's daily interaction | ~15 min | ~5 min |
| Manual agent coordination events | Weekly | Never |
| Approvals requiring laptop | Daily | Phone-optional |
| System uptime without Buck | 1-2 days | 1 week+ |
| Proactive status push | Daily report (pull) | Push notification |

---

## What Stays the Same

- No autonomous production writes
- All OWNER-level gates remain mandatory
- HubSpot: Gate H never bypassed
- Approval queue is the single source of pending items
- Buck retains final authority on all business decisions

---

*HCI AI OS v2.1 Roadmap | Hendrickson Construction, Inc. | 2026-06-27*
