"""Platform Event Bus Service.

Synchronous publish/subscribe for HCI AI domain events.
Events are persisted to platform_events and dispatched to registered handlers.
Includes correlation IDs for cross-service tracing and retry tracking.
No external broker required at current scale.
"""
from __future__ import annotations
import os, sys, uuid, json
from typing import Callable

_here = os.path.dirname(os.path.abspath(__file__))
_src = os.path.abspath(os.path.join(_here, "..", "..", ".."))
sys.path.insert(0, _src)
sys.path.insert(0, os.path.join(_src, "api"))

import services.db as db

# ── Event type registry ───────────────────────────────────────────────────────
# Standard event types emitted by the HCI AI platform
SOP_STATUS_CHANGED    = "sop.status_changed"
SOP_GATE_APPROVED     = "sop.gate_approved"
SOP_WORK_STOPPED      = "sop.work_stopped"
SOP_AI_DRAFTED        = "sop.ai_drafted"
SOP_HANDED_OFF        = "sop.handed_off"
SOP_EXCEPTION_CREATED = "sop.exception_created"

WORKFLOW_TRIGGERED    = "workflow.triggered"
WORKFLOW_COMPLETED    = "workflow.completed"
WORKFLOW_FAILED       = "workflow.failed"

NOTIFICATION_SENT     = "notification.sent"
NOTIFICATION_READ     = "notification.read"

IDENTITY_USER_CREATED = "identity.user_created"
IDENTITY_USER_UPDATED = "identity.user_updated"

# ── Handler registry ──────────────────────────────────────────────────────────
# Handlers are registered at import time; called synchronously on publish
_handlers: dict[str, list[Callable[[dict], None]]] = {}


def subscribe(event_type: str, handler: Callable[[dict], None]) -> None:
    """Register a handler for an event type. Wildcards not supported."""
    _handlers.setdefault(event_type, []).append(handler)


def _persist(event: dict) -> int | None:
    """Write event to platform_events. Returns new event id."""
    try:
        row = db.execute_returning("""
            INSERT INTO platform_events
                (event_type, source_service, entity_type, entity_id, project_id,
                 payload, actor, correlation_id, status)
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s::uuid, %s)
            RETURNING id, correlation_id::text
        """, (
            event.get("event_type"),
            event.get("source_service"),
            event.get("entity_type"),
            event.get("entity_id"),
            event.get("project_id"),
            json.dumps(event.get("payload") or {}),
            event.get("actor"),
            event.get("correlation_id") or str(uuid.uuid4()),
            "published",
        ))
        return row["id"] if row else None
    except Exception:
        return None


class EventBus:
    """Synchronous publish/subscribe event bus."""

    @staticmethod
    def publish(
        event_type: str,
        source_service: str = "",
        entity_type: str = "",
        entity_id: int | None = None,
        project_id: int | None = None,
        payload: dict | None = None,
        actor: str = "system",
        correlation_id: str | None = None,
    ) -> int | None:
        """Publish a domain event. Persists to DB and calls registered handlers.

        correlation_id: pass an existing UUID to link related events across services.
                        Auto-generated if not supplied.
        """
        cid = correlation_id or str(uuid.uuid4())
        event = {
            "event_type":     event_type,
            "source_service": source_service,
            "entity_type":    entity_type,
            "entity_id":      entity_id,
            "project_id":     project_id,
            "payload":        payload or {},
            "actor":          actor,
            "correlation_id": cid,
        }
        event_id = _persist(event)
        event["id"] = event_id

        for handler in _handlers.get(event_type, []):
            try:
                handler(event)
            except Exception:
                pass  # handler failures never kill the caller

        return event_id

    @staticmethod
    def get_events(
        event_type: str | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        project_id: int | None = None,
        limit: int = 50,
    ) -> list[dict]:
        conditions = ["1=1"]
        params: list = []
        if event_type:
            conditions.append("event_type = %s")
            params.append(event_type)
        if entity_type:
            conditions.append("entity_type = %s")
            params.append(entity_type)
        if entity_id is not None:
            conditions.append("entity_id = %s")
            params.append(entity_id)
        if project_id is not None:
            conditions.append("project_id = %s")
            params.append(project_id)
        params.append(limit)
        try:
            rows = db.query(f"""
                SELECT * FROM platform_events
                WHERE {' AND '.join(conditions)}
                ORDER BY published_at DESC
                LIMIT %s
            """, params)
            return [dict(r) for r in rows]
        except Exception:
            return []

    @staticmethod
    def get_sop_events(sop_instance_id: int) -> list[dict]:
        return EventBus.get_events(entity_type="sop_instance", entity_id=sop_instance_id)
