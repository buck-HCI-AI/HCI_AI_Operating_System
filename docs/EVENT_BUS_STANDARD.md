# Event Bus Standard
**Version:** 1.0 | **Date:** 2026-06-26

---

## Overview

The HCI AI Event Bus is a synchronous publish/subscribe system backed by PostgreSQL. All domain events are persisted with correlation IDs. No external message broker is required at current scale.

## Standard Event Types

| Event Type | Source | Trigger |
|---|---|---|
| `sop.status_changed` | Any SOP service | Every status transition |
| `sop.gate_approved` | ApprovalEngine | Gate record created |
| `sop.work_stopped` | StopConditionChecker | SC-01 through SC-07 triggered |
| `sop.ai_drafted` | Any SOP agent | AI draft complete |
| `sop.handed_off` | Any SOP service | Handed Off status transition |
| `sop.exception_created` | ApprovalEngine | Bypass exception logged |
| `sop.gate.approval_required` | SOP services | Approval gate reached |
| `workflow.triggered` | Workflow Engine | Workflow started |
| `workflow.completed` | Workflow Engine | Workflow finished |
| `workflow.failed` | Workflow Engine | Workflow error |
| `notification.sent` | NotificationService | Notification created |
| `notification.read` | NotificationService | Notification read |

## Event Payload Standard

Every event must include:

```json
{
  "event_type": "sop.status_changed",
  "source_service": "sop_15",
  "entity_type": "sop_instance",
  "entity_id": 42,
  "project_id": 1,
  "actor": "Buck Adams",
  "correlation_id": "uuid-v4",
  "payload": {
    "from_status": "Internal Review",
    "to_status": "Approval Required"
  }
}
```

## Correlation IDs

Every event receives a UUID correlation ID. Pass `correlation_id` when publishing related events to link them across services. Example: a status change event and its resulting notification should share a correlation ID.

## Auto-Emission from SOP Layer

`BaseSOP.transition_status()` automatically emits `sop.status_changed` to the Event Bus on every status transition. No additional code needed in SOP services.

## Subscribing to Events

```python
from event_bus.event_bus_service import subscribe, SOP_STATUS_CHANGED

def on_status_changed(event: dict):
    if event["payload"].get("to_status") == "Approval Required":
        # create notification
        pass

subscribe(SOP_STATUS_CHANGED, on_status_changed)
```

## API

```
POST /api/v1/platform/events/publish          — publish event
GET  /api/v1/platform/events                  — query events (filter by type/entity/project)
GET  /api/v1/platform/events/sop/{id}         — all events for a SOP instance
```

## Database

Table: `platform_events`

| Column | Type | Notes |
|---|---|---|
| `event_type` | varchar | Dotted namespace: `sop.status_changed` |
| `source_service` | varchar | Originating service: `sop_15` |
| `entity_type` | varchar | `sop_instance`, `project`, `workflow` |
| `entity_id` | int | FK to the entity |
| `project_id` | int | FK to projects |
| `correlation_id` | uuid | Auto-generated; link related events |
| `retry_count` | int | Incremented on handler retry |
| `status` | varchar | `published`, `failed` |
| `payload` | jsonb | Event-specific data |
| `actor` | varchar | Who triggered the event |
| `published_at` | timestamptz | When published |
