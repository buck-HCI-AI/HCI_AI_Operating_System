# Notification Center Standard
**Version:** 1.0 | **Date:** 2026-06-26

---

## Overview

Centralized notification service for all HCI AI workflow events. Supports in-system delivery with acknowledgement and escalation.

## Notification Types

| Type | Who Gets It | Escalation Threshold |
|---|---|---|
| `approval_required` | Approver + Buck | 4 hours |
| `work_stopped` | Actor + Buck | 2 hours |
| `safety_hazard` | Super + Buck | 1 hour |
| `qa_failure` | PM | 4 hours |
| `rfi_open` | PM | 24 hours |
| `submittal_due` | PM | 24 hours |
| `bid_deadline` | PM | 8 hours |
| `procurement_delay` | PM | — |
| `schedule_impact` | PM | — |
| `bid_received` | PM | — |
| `ai_draft_ready` | PM/Actor | — |
| `handoff_ready` | Next actor | — |
| `workflow_exception` | PM + Buck | — |
| `exception_created` | Buck | — |
| `info` | Specified recipient | — |

## Escalation

Notifications above their threshold that are unacknowledged escalate to Buck Adams (or a specified actor). Call `POST /api/v1/platform/notifications/escalate` to run escalation check. Escalated notifications are tagged `escalation_level=1`.

## Construction-Specific Notifiers

```python
from notifications.notification_service import NotificationService

# Procurement delay
NotificationService.notify_procurement_delay("Steel Beams", "Alpine Steel", delay_weeks=3, project_id=1)

# RFI overdue
NotificationService.notify_rfi_open("RFI-042", "Beam connection detail", days_open=6, project_id=1)

# Schedule impact
NotificationService.notify_schedule_impact("Concrete Pour", variance_days=4, project_id=1)

# Bid received
NotificationService.notify_bid_received("Electrical", "Durgin Electric", 145000, project_id=1)

# QA failure
NotificationService.notify_qa_failure("Waterproofing membrane check", "CRITICAL", sop_instance_id=42)

# Safety hazard
NotificationService.notify_safety_hazard("SAF-003", "Fall risk at roof edge", "CRITICAL", project_id=1)
```

## Acknowledgement

Recipients call `POST /api/v1/platform/notifications/{id}/read` to acknowledge. Bulk: `POST /api/v1/platform/notifications/{recipient}/read-all`.

## API

```
POST /api/v1/platform/notifications                     — create notification
GET  /api/v1/platform/notifications/{recipient}         — get notifications (filter: unread_only, type)
POST /api/v1/platform/notifications/{id}/read           — mark read (acknowledge)
POST /api/v1/platform/notifications/{recipient}/read-all— mark all read
GET  /api/v1/platform/notifications                     — unread counts per recipient
POST /api/v1/platform/notifications/escalate            — run escalation pass
```

## Database

Table: `platform_notifications`

| Column | Purpose |
|---|---|
| `recipient` | Actor name |
| `notification_type` | Notification category |
| `title` | Short display text |
| `body` | Full description |
| `entity_type` / `entity_id` | What the notification is about |
| `project_id` | Related project |
| `action_url` | Deep link to resolve the notification |
| `is_read` / `read_at` | Acknowledgement tracking |
| `email_sent` | Whether email delivery was triggered |
| `escalation_level` | 0=new, 1=escalated |
| `escalated_to` | Who it was escalated to |
