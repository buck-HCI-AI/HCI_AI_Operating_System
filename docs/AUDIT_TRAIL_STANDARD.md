# Audit Trail Standard
**Version:** 1.0 | **Date:** 2026-06-26

---

## Overview

The HCI AI Audit Trail provides immutable, queryable records of who did what, when, why, and with what approval — across all services. Three source tables are unified: `sop_workflow_events`, `workflow_events`, and `platform_audit_log`.

## What Gets Audited

Every SOP status transition, approval, stop condition, exception, and bypass is automatically logged. Workflow engine start/complete/fail events are logged at the workflow layer. Any service can write to `platform_audit_log` directly via `AuditTrail.log()`.

## Record Structure

Every audit record includes:

| Field | Type | Meaning |
|---|---|---|
| `source` | varchar | `sop`, `workflow`, `platform`, or service name |
| `event_type` | varchar | What happened (e.g., `sop.status_changed`) |
| `actor` | varchar | Who caused the event |
| `entity_type` | varchar | What was affected (`sop_instance`, `project`, etc.) |
| `entity_id` | int | Primary key of affected entity |
| `project_id` | int | Related project |
| `summary` | text | Human-readable description |
| `payload` | jsonb | Full context (status, notes, approver, amounts) |
| `correlation_id` | uuid | Links related events across services |
| `confidence` | numeric | For AI-generated records (0.0–1.0) |
| `created_at` | timestamptz | Immutable write timestamp |

## Querying

```python
from audit.audit_service import AuditTrail

# All events for a SOP instance (3-source unified)
trail = AuditTrail.get_full_sop_trail(sop_instance_id=42)

# Project timeline (all SOPs + workflows + platform events)
timeline = AuditTrail.get_project_timeline(project_id=1, since_hours=168)

# Filter by actor, event type, and timeframe
records = AuditTrail.query(actor="Buck Adams", event_type="sop.gate_approved", since_hours=24)

# 24-hour activity summary by source
summary = AuditTrail.summary()
```

## Immutability

Records in all three audit tables have no UPDATE or DELETE paths via the audit service API. Correctional entries are new records with a reference to the original.

## API

```
POST /api/v1/platform/audit                           — write audit record
GET  /api/v1/platform/audit                           — query (source/entity/project/actor/type/hours)
GET  /api/v1/platform/audit/sop/{id}                  — full 3-source trail for a SOP instance
GET  /api/v1/platform/audit/project/{id}/timeline     — unified project timeline
GET  /api/v1/platform/audit/summary                   — event counts by source in last 24h
```

## Compliance

Audit records satisfy the HCI "who/what/when/why/approvals" requirement from the Master Constitution. Every approval gate, exception bypass, and status transition is captured with actor attribution and correlation ID for cross-event tracing.
