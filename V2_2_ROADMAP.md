# HCI AI Operating System — v2.2 Roadmap
## Executive Operations & Autonomous Coordination

**Authority:** Chief Architect Directive — v2.2 + Notification Service Directive  
**Owner:** Buck Adams  
**Date:** 2026-06-27  
**Mission:** Transition HCI AI OS from coordinated AI tools into a self-managing Construction Operating System.

---

## Design Objective

> "Buck Adams should manage Hendrickson Construction — not manage AI."

1. Buck should be able to leave for hours or days
2. AI agents coordinate themselves
3. Buck receives only executive-level decisions
4. Every manual action is evaluated for automation
5. Mobile is the primary executive interface

---

## v2.2 Objectives

### OBJECTIVE 1 — Executive Operating Cycle (Permanent)

Full lifecycle automation replacing Buck as the daily coordinator.

| Time | Mode | Delivery | Content |
|---|---|---|---|
| 07:00 | Morning Mode | Push + email | Overnight activity, health, risks, decisions |
| Throughout day | Alert Mode | Push only | Owner decisions, critical alerts |
| 19:00 | End-of-Day | Email | Missions complete, ROI, blockers, overnight plan |
| Saturday 08:00 | Weekend Mode | Email | Week summary, deferred items, auto-schedule |
| When away 2d+ | Travel Mode | Single daily email | Critical only |

**Deliverables:**
- `GET /api/v1/executive/eod-brief` — End-of-Day summary endpoint
- `GET /api/v1/executive/weekend-summary` — Weekly summary endpoint
- n8n `AUTO-EOD`: 19:00 daily EOD email
- n8n `AUTO-WEEKEND`: Saturday 08:00 weekend summary email
- n8n `AUTO-NOTIFY`: Urgent alert push via ntfy.sh on HIGH risk / unresolved OWNER item >24h
- Travel mode auto-detection: flag if no approvals >48h, switch to critical-only digest

**Sprint target:** Sprint 4

---

### OBJECTIVE 2 — Executive Dashboard (Continued)

Dashboard spec already built (v2.1). v2.2 refinements:

- All content readable in under 30 seconds on mobile
- Display: Overall Health, Active Projects, Active AI Agents, Mission Progress, Approval Queue, Risks, ROI, Current Recommendation
- Add Mission Progress widget (active/blocked/complete counts from MISSION_QUEUE.md or missions DB table)
- Add Agent Status widget (which agents ran today, last activity)
- `GET /api/v1/executive/eod-brief` feeds end-of-day card
- iOS Shortcut documentation published to `AI_TEAM/IOS_SHORTCUTS.md`

**Sprint target:** Sprint 4

---

### OBJECTIVE 3 — Executive Inbox (Hardened)

Inbox is already the sole work queue. v2.2 requirements:

- Batch approval card: single card with `POST /api/v1/executive/batch-approve` (approve all LOW-confidence items in one tap)
- Card includes full context: Decision, Recommendation, Confidence, Business Impact, Risk, Deadline + Approve/Reject/Defer
- Context links: cards link to detail pages (HubSpot deal, Drive file, project record)
- Auto-escalation: OWNER items unresolved >72h generate an alert via ntfy.sh
- Re-queue: defer adds item back with +7d deadline, generates reminder

**Deliverables:**
- `POST /api/v1/executive/batch-approve` — approve all LOW items
- Auto-escalation n8n workflow: check unresolved >72h, send ntfy push
- Defer logic: update deadline on defer

**Sprint target:** Sprint 4

---

### OBJECTIVE 4 — AI Program Manager (Expanded)

Expand from coordinator document to active operating agent.

**Responsibilities (v2.2):**
- Assign missions to agents (write to MISSION_QUEUE.md via API endpoint)
- Detect idle agents (no activity >2h during active hours)
- Detect blocked work (BLOCKED missions auto-surface in Executive Inbox)
- Resolve agent dependencies (read MISSION_QUEUE, post to EVENT_BUS)
- Schedule recurring work (daily 03:00 mining, 07:00 health check, 19:00 EOD)
- Verify mission completion (check expected outputs exist)
- Recommend next optimizations (weekly list of automation opportunities)
- Escalate only OWNER-level decisions

**Deliverables:**
- `POST /api/v1/missions` — create/update mission
- `GET /api/v1/missions` — list missions with status
- `GET /api/v1/missions/blocked` — blocked missions summary
- Mission DB table (migration 008)
- n8n `AUTO-PM`: daily 06:00 program manager review cycle

**Sprint target:** Sprint 4-5

---

### OBJECTIVE 5 — Continuous Self-Improvement

Detect every manual action → log → estimate ROI → queue for automation.

**Protocol:**
1. Claude Code detects Buck performing a repeated manual task
2. Logs to AUTONOMY_BACKLOG.md (auto-updated, no Buck input needed)
3. Estimates ROI: time saved × frequency
4. Prioritizes by (ROI × feasibility)
5. Queues implementation in next sprint

**Weekly Automation Opportunities Report:**
- Generated every Sunday 19:00 via n8n
- Delivered to Executive Inbox as single card
- Lists top 3 new automation opportunities this week
- Includes cumulative ROI dashboard

**Deliverables:**
- `POST /api/v1/autonomy/opportunity` — log new automation opportunity
- `GET /api/v1/autonomy/report` — weekly report JSON
- n8n `AUTO-WEEKLY-REPORT`: Sunday 19:00 opportunity report
- Auto-update `AUTONOMY_BACKLOG.md` on new opportunity detection

**Sprint target:** Sprint 5

---

### OBJECTIVE 6 — Universal Connector Platform (Hardened)

Houzz is the reference. All future connectors use the same 7-stage pipeline.

```
Connector → Validation → Normalization → Persistence → Event Bus → Mining → Knowledge Graph → Executive Reporting
```

**v2.2 additions:**
- Connector health endpoint: `GET /api/v1/connectors/health` — all connectors with last sync, error rate
- Auto-retry: failed ingestion auto-retries 3× before flagging to Executive Inbox
- Connector SDK: `base_connector.py` — abstract class with 7-stage interface
- Next connectors queued: Procore, Bluebeam, QuickBooks (after Houzz completes)

**Deliverables:**
- `03_Source_Code/services/base_connector.py` — abstract connector SDK
- `GET /api/v1/connectors/health` — connector registry health
- Auto-retry wrapper in ingestion pipeline
- Connector documentation template in CONNECTOR_FRAMEWORK.md

**Sprint target:** Sprint 5

---

### NOTIFICATION SERVICE (2nd BTW Directive)

Build the notification infrastructure to support the Executive Operating Cycle.

**Provider Stack (priority order):**
1. **ntfy.sh** — primary push (free, iOS/Android, self-hostable)
2. **Pushover** — backup push (reliable, paid, no server needed)
3. **Email** — always-on via SendGrid/Gmail SMTP (n8n built-in)
4. **SMS** — Twilio, critical alerts only
5. **Slack** — team channel notifications (future)
6. **Microsoft Teams** — enterprise notifications (future)
7. **Apple Push Notification Service (APNs)** — native iOS (future)

**Policy Engine:**
```
Event severity + context → route to provider(s)
CRITICAL   → ntfy + Pushover + SMS
HIGH       → ntfy + Email
MEDIUM     → Email
LOW        → Weekly digest only
```

**Flow:**
```
Mining/Agent Event → Policy Engine → Executive Inbox → Notification(s)
```

**Deliverables:**
- `03_Source_Code/services/notification_engine/` — notification service
  - `routes.py` — `POST /api/v1/notifications/send`
  - `notification_svc.py` — provider dispatch with policy engine
  - Provider adapters: ntfy, Pushover, email, SMS
- n8n `AUTO-NOTIFY` — upstream trigger for CRITICAL/HIGH events
- `NOTIFICATION_POLICY.md` — policy registry
- ntfy topic: `hci-executive` (Buck subscribes on phone)

**Sprint target:** Sprint 4

---

## Sprint Mapping

| Sprint | Dates | Primary Focus |
|---|---|---|
| Sprint 3 | 2026-07-07 → 2026-07-21 | Executive Dashboard ✅ |
| Sprint 4 | 2026-07-22 → 2026-08-05 | Notification Engine + Operating Cycle + Inbox v2 |
| Sprint 5 | 2026-08-06 → 2026-08-19 | AI Program Manager + Autonomy Backlog + Connector SDK |
| Sprint 6 | 2026-08-20 → 2026-09-03 | Mobile Experience (iOS shortcuts, full mobile UX) |
| Sprint 7 | 2026-09-04 → 2026-09-17 | Self-Improvement Loop + weekly reports |

---

## v2.2 Success Metrics

| Metric | Target |
|---|---|
| Buck's daily touchpoints | ≤ 3 (morning approval, EOD skim, critical alert) |
| Decision time per inbox item | < 30 seconds |
| Autonomous hours per week | ≥ 160h (always-on) |
| Manual tasks automated | +6 new (beyond v2.1 baseline) |
| Notification delivery latency | < 60 seconds from event |
| Agent idle time flagged | < 2h before escalation |

---

*HCI AI Operating System v2.2 | Hendrickson Construction, Inc. | 2026-06-27*  
*Directive: btw.docx (v2.2 Chief Architect) + 2nd BTW.docx (Notification Service)*
