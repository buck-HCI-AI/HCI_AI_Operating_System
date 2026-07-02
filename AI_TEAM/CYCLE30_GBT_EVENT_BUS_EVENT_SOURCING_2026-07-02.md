# CYCLE 30 — GBT SPRINT 7 PRIORITY 3
# Event Bus and Event Sourcing Architecture
**HCI AI OS | Hendrickson Construction, Inc.**
**Date:** 2026-07-02
**Cycle:** 30
**Type:** Sprint 7 Priority 3 — Event Bus + Event Sourcing

---

## CHIEF ARCHITECT STATEMENT

> "This architecture makes HCI AI OS extensible: new intelligence services can subscribe to events instead of modifying every router. That is how the platform becomes durable as it grows."

---

## 1) EVENT TYPES CATALOG

### Project Events
```
PROJECT_CREATED
PROJECT_UPDATED
PROJECT_PHASE_CHANGED
PROJECT_COMPLETED
PROJECT_ON_HOLD
```

### Field Events
```
FIELD_REPORT_SUBMITTED
DAILY_LOG_CREATED
WEATHER_LOG_CREATED
CREW_COUNT_RECORDED
SITE_INCIDENT_REPORTED
```

### RFI / Submittal Events
```
RFI_OPENED
RFI_ANSWERED
RFI_CLOSED
RFI_OVERDUE
RFI_SCHEDULE_IMPACT_ADDED
RFI_COST_IMPACT_ADDED
SUBMITTAL_CREATED
SUBMITTAL_UNDER_REVIEW
SUBMITTAL_APPROVED
SUBMITTAL_REJECTED
```

### Procurement Events
```
PURCHASE_ORDER_CREATED
PURCHASE_ORDER_APPROVED
PURCHASE_ORDER_FULFILLED
PURCHASE_ORDER_CANCELLED
LONG_LEAD_MATERIAL_ORDERED
LONG_LEAD_MATERIAL_DELAYED
LONG_LEAD_MATERIAL_DELIVERED
```

### Schedule Events
```
CPM_SCHEDULE_IMPORTED
CRITICAL_PATH_UPDATED
SCHEDULE_VARIANCE_DETECTED
SCHEDULE_RISK_ELEVATED
ACTIVITY_BLOCKED
ACTIVITY_COMPLETED
```

### Cost / Finance Events
```
BUDGET_LINE_CREATED
BUDGET_VARIANCE_EXCEEDED
CHANGE_ORDER_CREATED
CHANGE_ORDER_APPROVED
INVOICE_RECEIVED
INVOICE_APPROVED
PAYMENT_ISSUED
```

### Punch / Warranty Events
```
PUNCH_ITEM_CREATED
PUNCH_ITEM_IN_PROGRESS
PUNCH_ITEM_READY_FOR_INSPECTION
PUNCH_ITEM_CLOSED
PUNCH_ITEM_OVERDUE
WARRANTY_ITEM_CREATED
WARRANTY_EXPIRING_SOON
WARRANTY_CLAIMED
WARRANTY_RESOLVED
```

### Vendor Events
```
VENDOR_CREATED
VENDOR_UPDATED
VENDOR_RISK_FLAGGED
VENDOR_SCORED
VENDOR_INSURANCE_EXPIRING
```

### Client Events
```
CLIENT_SELECTION_MADE
CLIENT_SELECTION_APPROVED
CLIENT_DECISION_OVERDUE
CLIENT_PORTAL_ACCESSED
```

### Photo Events
```
PHOTO_UPLOADED
PHOTO_AI_PROCESSED
PHOTO_LINKED_TO_ENTITY
```

### Executive / AI Events
```
MORNING_BRIEF_GENERATED
EXECUTIVE_KPI_UPDATED
APPROVAL_CREATED
APPROVAL_APPROVED
APPROVAL_DECLINED
AI_DIRECTIVE_ISSUED
AI_DIRECTIVE_ACKNOWLEDGED
AI_DIRECTIVE_COMPLETED
AI_AGENT_HEARTBEAT_STALE
```

---

## 2) DDL

### domain_events table
```sql
CREATE TABLE IF NOT EXISTS domain_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    event_type TEXT NOT NULL,
    aggregate_type TEXT NOT NULL,  -- project, rfi, vendor, photo, etc.
    aggregate_id UUID,
    project_id TEXT,
    
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    actor_id TEXT,  -- user_id or agent_name
    processed_at TIMESTAMPTZ,
    
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_domain_events_type ON domain_events(event_type);
CREATE INDEX IF NOT EXISTS idx_domain_events_aggregate ON domain_events(aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_domain_events_project ON domain_events(project_id);
CREATE INDEX IF NOT EXISTS idx_domain_events_created ON domain_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_domain_events_unprocessed 
    ON domain_events(processed_at) WHERE processed_at IS NULL;
```

### domain_event_consumers table (tracks consumer progress)
```sql
CREATE TABLE IF NOT EXISTS domain_event_consumers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    consumer_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    last_processed_event_id UUID REFERENCES domain_events(event_id),
    
    status TEXT NOT NULL DEFAULT 'active',
    -- active | paused | errored
    
    processed_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_domain_event_consumer UNIQUE (consumer_name, event_type)
);
```

### domain_event_dead_letters table
```sql
CREATE TABLE IF NOT EXISTS domain_event_dead_letters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    event_id UUID REFERENCES domain_events(event_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    consumer_name TEXT NOT NULL,
    
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_message TEXT NOT NULL,
    
    attempts INTEGER NOT NULL DEFAULT 0,
    
    status TEXT NOT NULL DEFAULT 'open',
    -- open | retried | resolved | ignored
    
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_domain_event_consumer_dead 
        UNIQUE (event_id, consumer_name)
);
```

---

## 3) EVENT BUS RECOMMENDATION: PostgreSQL + Redis Streams (Phase Approach)

### Phase 1 (Sprint 7): PostgreSQL LISTEN/NOTIFY
**Why:** No new infrastructure. Works with existing PostgreSQL. Sufficient for <1000 events/day.

```sql
-- Trigger on domain_events insert
CREATE OR REPLACE FUNCTION notify_event_consumers()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('hci_domain_events', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER domain_events_notify
    AFTER INSERT ON domain_events
    FOR EACH ROW EXECUTE FUNCTION notify_event_consumers();
```

### Phase 2 (Sprint 8+): Redis Streams
**Why:** When event volume grows, Redis Streams provides consumer groups, acknowledgment, and replay.

```
XADD hci:domain_events * event_id <uuid> event_type <type> aggregate_id <id>
```

Consumer groups:
```
project_brain_consumer
mission_control_consumer
predictive_consumer
vendor_consumer
executive_consumer
notification_consumer
```

Each consumer group tracks delivery independently.

---

## 4) EVENT CONSUMERS

### Project Brain Consumer
Subscribes to: ALL events
Actions:
- For each event: extract entities from payload
- Create project_entity_links for explicit relationships
- Update entity last_activity timestamp
- No AI inference in Phase 1

### Mission Control Consumer
Subscribes to:
```
RFI_OPENED, RFI_OVERDUE, SCHEDULE_RISK_ELEVATED
BUDGET_VARIANCE_EXCEEDED, PUNCH_ITEM_OVERDUE
VENDOR_RISK_FLAGGED, AI_AGENT_HEARTBEAT_STALE
```
Actions:
- Create mission control alert
- Update project risk summary
- Refresh portfolio dashboard

### Predictive Intelligence Consumer
Subscribes to:
```
LONG_LEAD_MATERIAL_ORDERED
LONG_LEAD_MATERIAL_DELAYED
RFI_OVERDUE
WEATHER_ALERT_CREATED
VENDOR_RISK_FLAGGED
FIELD_REPORT_SUBMITTED
SCHEDULE_VARIANCE_DETECTED
```
Actions:
- Refresh schedule risk predictions for affected project
- Update top risks
- Trigger Morning Brief inclusion if risk threshold exceeded

### Vendor Intelligence Consumer
Subscribes to:
```
PURCHASE_ORDER_FULFILLED
PUNCH_ITEM_CLOSED
WARRANTY_CLAIMED
RFI_ANSWERED
VENDOR_UPDATED
```
Actions:
- Recalculate vendor performance score
- Update vendor risk flags

### Executive Consumer
Subscribes to:
```
MORNING_BRIEF_GENERATED
EXECUTIVE_KPI_UPDATED
```
Actions:
- Update KPI snapshots
- Refresh portfolio summary
- Include urgent events in Buck brief

### Notification Consumer
Subscribes to:
```
PUNCH_ITEM_OVERDUE
RFI_OVERDUE
AI_AGENT_HEARTBEAT_STALE
BUDGET_VARIANCE_EXCEEDED
SCHEDULE_RISK_ELEVATED
CLIENT_DECISION_OVERDUE
```
Actions:
- Telegram alert (via /gateway/telegram/send when available)
- Mission Control alert
- Approval notification to appropriate role

---

## 5) DEAD LETTER QUEUE RULES

- After 3 consumer failures: event moves to domain_event_dead_letters
- Dead letters appear in Mission Control dashboard
- Buck does not need routine dead letter notifications unless they affect production state
- Dead letter resolution options: retry, resolve, ignore

---

## 6) EVENT EMISSION SERVICE

Recommended file: `app/services/event_bus.py`

```python
from sqlalchemy.orm import Session
from app.models.domain_events import DomainEvent

def emit_event(
    db: Session,
    event_type: str,
    aggregate_type: str,
    aggregate_id=None,
    project_id: str | None = None,
    payload: dict | None = None,
    actor_id: str | None = None,
    version: int = 1,
):
    event = DomainEvent(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        project_id=project_id,
        payload=payload or {},
        actor_id=actor_id,
        version=version,
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Phase 2: publish to Redis Stream
    # XADD hci:domain_events * event_id <id> event_type <type>
    
    return event
```

**Rule:** Every router should emit after successful commit.

### Example Usage in Router
```python
# In /photos router after successful photo upload:
await emit_event(
    db=db,
    event_type="PHOTO_UPLOADED",
    aggregate_type="photo",
    aggregate_id=photo.id,
    project_id=photo.project_id,
    payload={"filename": photo.filename, "entity_type": photo.entity_type},
    actor_id=str(principal.user_id)
)
```

---

## 7) /events ROUTER

### Endpoints
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /events | Emit domain event | ai_agent, super_admin |
| GET | /events | Query event history | super_admin, ai_agent |
| GET | /events/{event_id} | Get single event | super_admin, ai_agent |
| GET | /events/dead-letters | View dead letters | super_admin |
| POST | /events/dead-letters/{id}/retry | Retry dead letter | super_admin |
| POST | /events/dead-letters/{id}/resolve | Resolve dead letter | super_admin |

### Pydantic Schemas
```python
class DomainEventCreate(BaseModel):
    event_type: str
    aggregate_type: str
    aggregate_id: Optional[UUID] = None
    project_id: Optional[str] = None
    payload: dict[str, Any] = {}
    actor_id: Optional[str] = None
    version: int = 1

class DomainEventOut(BaseModel):
    event_id: UUID
    event_type: str
    aggregate_id: Optional[UUID] = None
    aggregate_type: str
    project_id: Optional[str] = None
    payload: dict[str, Any]
    actor_id: Optional[str] = None
    processed_at: Optional[datetime] = None
    version: int
    created_at: datetime
```

---

## 8) EVENT-TO-GRAPH EXAMPLE

When `RFI_OPENED` fires:

Payload:
```json
{
    "rfi_id": "uuid",
    "project_id": "HCI-2024-001",
    "discipline": "structural",
    "cpm_activity_reference": "act-234"
}
```

Project Brain Consumer creates:
```
rfi -> cpm_activity
link_type = rfi_impacts_schedule
```

Predictive Consumer refreshes:
```
GET /predict/schedule/{project_id}
```

Mission Control Consumer updates project risk summary.

---

## 9) TEST GATES

Claude Code should add tests for:
1. Emit event creates `domain_events` row
2. Event has valid event type
3. Query by project returns project events only
4. Query by aggregate returns aggregate history
5. Unauthorized user cannot emit events
6. AI agent with API key can emit scoped event
7. Event consumer marks event processed
8. Failed consumer writes dead letter after retry limit
9. PHOTO_UPLOADED creates Project Brain link
10. RFI_OPENED updates Mission Control hook
11. SCHEDULE_RISK_ELEVATED appears in executive analytics
12. Dead letters appear in Mission Control

---

## 10) DEFINITION OF DONE

Event Bus Phase 1 is complete when:
- `domain_events`, `domain_event_consumers`, and `domain_event_dead_letters` tables exist
- `/events` emit/query endpoints exist
- Core routers emit domain events after successful writes
- Project Brain consumes events to create graph links
- Mission Control consumes events to refresh project summaries
- Dead letter handling exists
- Tests pass

---

*Cycle 30 complete. Event Bus + Event Sourcing spec committed.*
*Sprint 7 Priority 3 done.*
*Next: CYCLE 31 — QuickBooks Integration (requires Buck authorization)*
*OR: CYCLE 31 — Sprint 7 Retrospective to close Sprint 7 spec phase*
