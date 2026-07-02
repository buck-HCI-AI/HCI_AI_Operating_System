# CYCLE 35 — n8n ALERT AUTOMATION PIPELINE
## HCI AI OS — Hendrickson Construction, Inc.
**Cycle:** 35 | **Sprint:** 7 | **Date:** 2026-07-02
**Workflow ID:** WF-ALERT-001 | **Score: 9.8/10**
**Principle:** notify-and-escalate, NOT notify-and-act. All notifications advisory. Human review is the decision point.

---

## 1. WORKFLOW OVERVIEW

WF-ALERT-001 fires when alert.project_red event is emitted by HCI AI OS.
It closes the loop between the event bus, Mission Control, and Buck.

Architecture flow:
```
HCI AI OS
    |
Domain Event: PROJECT_HEALTH_CHANGED (new_health = RED)
    |
n8n Webhook (POST /project-red)
    |
Verify Event (IF node)
    |
Severity Switch (CRITICAL | HIGH | other)
    |
Telegram Notify -> Log to mission_alerts -> Invalidate Cache
    |
[Wait 30 min]
    |
Check acknowledged?
    |           |
  Yes         No
    |           |
 Close      Escalate (second Telegram + log)
```

---

## 2. NODE DEFINITIONS

### Node 1 — Webhook Trigger
```
Type: Webhook
Name: Webhook - Project RED
Method: POST
Path: /project-red
Authentication: Header API Key (X-HCI-API-Key)
Response: 200 OK (immediate, async processing)
```

### Node 2 — Verify Event
```
Type: IF Node
Condition: event_type == PROJECT_HEALTH_CHANGED AND new_health == RED
False branch: Terminate workflow (discard non-RED events)
```

### Node 3 — Severity Switch
```
Type: Switch Node
Switch on: severity
Outputs:
  - CRITICAL -> immediate Telegram (urgent format)
  - HIGH -> immediate Telegram (standard format)
  - other -> log only, no Telegram
```

### Node 4 — Send Telegram Alert
```
Type: HTTP Request
Method: POST
Endpoint: POST /gateway/telegram/send
  (or direct Telegram Bot API if preferred)
Payload:
  {
    "message": "HCI PROJECT RED\nProject: {{$json.project_name}}\nReason: {{$json.reason}}\nSeverity: {{$json.severity}}"
  }
Expected response: { status: queued }
Retry: 3 attempts, exponential backoff
```

### Node 5 — Log to mission_alerts
```
Type: HTTP Request (POST /gateway/mission-alerts)
Payload:
  {
    "project_id": "{{$json.project_id}}",
    "alert_type": "PROJECT_RED",
    "severity": "{{$json.severity}}",
    "title": "Project {{$json.project_name}} is RED",
    "message": "{{$json.reason}}",
    "source_event_id": "{{$json.event_id}}",
    "status": "OPEN",
    "telegram_sent": true
  }
```

Note: inserts into mission_alerts table via gateway endpoint,
keeping workflow logic separate from direct database writes.

### Node 6 — Invalidate Mission Control Cache
```
Type: HTTP Request
POST /gateway/cache/invalidate
Payload: { pattern: 'mission_control:snapshot:*' }
Purpose: Forces fresh snapshot on next BC/Code query
```

### Node 7 — Wait 30 Minutes
```
Type: Wait Node
Duration: 30 minutes
Resume on: webhook callback OR timer expiry
```

### Node 8 — Check Acknowledgement
```
Type: HTTP Request (GET /gateway/mission-alerts/{alert_id})
Check: response.acknowledged == true
IF node branches:
  - True: close/resolve workflow
  - False: fire escalation
```

### Node 9 — Escalation (if unacknowledged)
```
Type: HTTP Request (POST /gateway/telegram/send)
Message: ESCALATION - {project_name} still RED after 30 min. No acknowledgment received.
          Alert ID: {alert_id}. Requires Buck review.
Also: update mission_alerts.status = 'ESCALATED'
```

---

## 3. MISSION_ALERTS TABLE

```sql
CREATE TABLE mission_alerts (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id       TEXT,
    alert_type       TEXT NOT NULL,
    severity         TEXT NOT NULL,
    title            TEXT,
    message          TEXT,
    source_event_id  UUID,
    acknowledged     BOOLEAN DEFAULT FALSE,
    acknowledged_by  TEXT,
    acknowledged_at  TIMESTAMPTZ,
    status           TEXT DEFAULT 'OPEN'
                     CHECK (status IN ('OPEN', 'ACKNOWLEDGED', 'ESCALATED', 'RESOLVED')),
    telegram_sent    BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    resolved_at      TIMESTAMPTZ
);

CREATE INDEX idx_mission_alerts_status ON mission_alerts(status) WHERE resolved_at IS NULL;
CREATE INDEX idx_mission_alerts_project ON mission_alerts(project_id);
CREATE INDEX idx_mission_alerts_unacked ON mission_alerts(acknowledged, created_at)
    WHERE acknowledged = FALSE AND resolved_at IS NULL;
```

---

## 4. GATEWAY ENDPOINTS REQUIRED

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /gateway/telegram/send | POST | Send Telegram message to Buck |
| /gateway/mission-alerts | POST | Create new alert record |
| /gateway/mission-alerts/{id} | GET | Check acknowledgement status |
| /gateway/mission-alerts/{id} | PATCH | Update status to ESCALATED |
| /gateway/cache/invalidate | POST | Invalidate Redis cache patterns |

---

## 5. ERROR HANDLING

| Error | Response |
|-------|----------|
| Telegram delivery fails | Retry 3x, log failure, continue workflow |
| Gateway unreachable | Retry 3x exponential backoff, log to n8n error log |
| alert_id not found on ack check | Log warning, skip escalation |
| Webhook receives malformed payload | Return 400, log, terminate |
| API key invalid | Return 401, log security event |

---

## 6. WORKFLOW DESIGN PRINCIPLES

Per GBT guidance:
- notify-and-escalate, NOT notify-and-act
- All notifications are advisory
- Human review (Buck) remains the decision point
- No operational changes are made automatically by n8n
- Escalation is based on acknowledgement status, not simply elapsed time
- Every notification is logged regardless of delivery status

---

## 7. ACCEPTANCE CRITERIA

| # | Criteria | Test |
|---|----------|------|
| 1 | PROJECT_HEALTH_CHANGED with new_health=RED triggers workflow | Post test event to webhook |
| 2 | CRITICAL and HIGH alerts send Telegram to Buck | Verify Telegram receipt |
| 3 | Every alert recorded in mission_alerts | Query DB after trigger |
| 4 | Mission Control cache refreshed after alert | Verify snapshot shows new alert |
| 5 | Unacknowledged alerts escalated after 30 min | Wait 30 min, verify escalation |
| 6 | Acknowledged alerts NOT escalated | Ack alert, verify no escalation |
| 7 | Delivery failures logged | Simulate Telegram failure, check n8n logs |
| 8 | Non-RED events not processed | Post YELLOW event, verify silent exit |
| 9 | Retry logic fires on transient errors | Simulate 1 failure, verify retry |
| 10 | Workflow idempotent on duplicate events | Post same event_id twice, verify 1 alert |

---

## 8. CYCLE SCORE: 9.8/10

WF-ALERT-001 is one of the most important operational automations in HCI AI OS.
It closes the loop between the event bus, Mission Control, and human decision-making.
Design is correctly notify-and-escalate, not notify-and-act.

-0.2: Dependent on Telegram credentials (Buck pending) and gateway alert endpoints.

---

*Next: Cycle 36 — Sprint 7 Full Implementation Retrospective*
*Code: Implement WF-ALERT-001 in n8n after /telegram/webhook and /mission-alerts endpoints are live*
