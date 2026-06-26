"""
HCI AI Platform Integration Layer — API Router
Exposes Identity, Event Bus, Notifications, Audit Trail, and Unified Search.
All endpoints: /api/v1/platform/...
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services", "platform"))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/platform", tags=["platform"])

# ── Lazy imports — platform services resolve their own sys.path ───────────────

def _identity():
    from identity.identity_service import IdentityService
    return IdentityService

def _events():
    from event_bus.event_bus_service import EventBus
    return EventBus

def _notifs():
    from notifications.notification_service import NotificationService
    return NotificationService

def _audit():
    from audit.audit_service import AuditTrail
    return AuditTrail

def _search():
    from search_gateway.search_gateway_service import SearchGateway
    return SearchGateway


# ──────────────────────────────────────────────────────────────────────────────
# Platform overview
# ──────────────────────────────────────────────────────────────────────────────

@router.get("")
def platform_overview():
    """Platform Integration Layer status overview."""
    return {
        "status": "active",
        "capabilities": {
            "identity":      "/api/v1/platform/identity",
            "events":        "/api/v1/platform/events",
            "notifications": "/api/v1/platform/notifications",
            "audit":         "/api/v1/platform/audit",
            "search":        "/api/v1/platform/search",
        },
        "version": "1.0",
    }


# ──────────────────────────────────────────────────────────────────────────────
# Identity & Permissions
# ──────────────────────────────────────────────────────────────────────────────

class UpsertUserRequest(BaseModel):
    actor_name: str
    role: str
    email: Optional[str] = None

@router.get("/identity/users")
def list_users(role: Optional[str] = None):
    """List all platform users, optionally filtered by role."""
    try:
        return {"users": _identity().list_users(role=role)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/identity/users/{actor_name}")
def get_user(actor_name: str):
    """Get identity record for an actor."""
    try:
        u = _identity().get_actor(actor_name)
        if not u:
            return {
                "actor_name": actor_name,
                "role": _identity().get_role(actor_name),
                "permissions": _identity().get_permissions(actor_name),
                "source": "default_fallback",
            }
        u["permissions"] = _identity().get_permissions(actor_name)
        return u
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/identity/users/{actor_name}/permissions")
def get_permissions(actor_name: str):
    """List all permissions for an actor."""
    try:
        return {
            "actor_name":  actor_name,
            "role":        _identity().get_role(actor_name),
            "permissions": _identity().get_permissions(actor_name),
            "authority_level": _identity().role_level(actor_name),
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/identity/users/{actor_name}/can/{permission}")
def check_permission(actor_name: str, permission: str):
    """Check if actor has a specific permission."""
    try:
        return {
            "actor_name": actor_name,
            "permission": permission,
            "allowed":    _identity().can(actor_name, permission),
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/identity/users")
def upsert_user(req: UpsertUserRequest):
    """Create or update a platform user."""
    try:
        return _identity().upsert_user(req.actor_name, req.role, req.email)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/identity/roles")
def list_roles():
    """List all defined roles with permission counts."""
    try:
        return {"roles": _identity().list_roles()}
    except Exception as e:
        raise HTTPException(500, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Event Bus
# ──────────────────────────────────────────────────────────────────────────────

class PublishEventRequest(BaseModel):
    event_type: str
    source_service: Optional[str] = ""
    entity_type: Optional[str] = ""
    entity_id: Optional[int] = None
    project_id: Optional[int] = None
    payload: Optional[dict] = None
    actor: Optional[str] = "system"

@router.post("/events/publish")
def publish_event(req: PublishEventRequest):
    """Publish a domain event to the platform event bus."""
    try:
        eid = _events().publish(
            event_type=req.event_type,
            source_service=req.source_service or "",
            entity_type=req.entity_type or "",
            entity_id=req.entity_id,
            project_id=req.project_id,
            payload=req.payload,
            actor=req.actor or "system",
        )
        return {"event_id": eid, "event_type": req.event_type, "status": "published"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/events")
def get_events(
    event_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    project_id: Optional[int] = None,
    limit: int = Query(50, le=200),
):
    """Query platform events with filters."""
    try:
        return {
            "events": _events().get_events(
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                project_id=project_id,
                limit=limit,
            )
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/events/sop/{sop_instance_id}")
def get_sop_events(sop_instance_id: int):
    """Get all events for a specific SOP instance."""
    try:
        return {"sop_instance_id": sop_instance_id, "events": _events().get_sop_events(sop_instance_id)}
    except Exception as e:
        raise HTTPException(500, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Notification Center
# ──────────────────────────────────────────────────────────────────────────────

class CreateNotificationRequest(BaseModel):
    recipient: str
    notification_type: str
    title: str
    body: Optional[str] = ""
    entity_type: Optional[str] = ""
    entity_id: Optional[int] = None
    project_id: Optional[int] = None
    action_url: Optional[str] = ""

@router.post("/notifications")
def create_notification(req: CreateNotificationRequest):
    """Create a notification for a recipient."""
    try:
        nid = _notifs().create(
            recipient=req.recipient,
            notification_type=req.notification_type,
            title=req.title,
            body=req.body or "",
            entity_type=req.entity_type or "",
            entity_id=req.entity_id,
            project_id=req.project_id,
            action_url=req.action_url or "",
        )
        return {"notification_id": nid, "status": "created"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/notifications/{recipient}")
def get_notifications(
    recipient: str,
    unread_only: bool = False,
    notification_type: Optional[str] = None,
    limit: int = Query(50, le=200),
):
    """Get notifications for a recipient."""
    try:
        notifs = _notifs().get_notifications(recipient, unread_only, notification_type, limit)
        return {
            "recipient": recipient,
            "count": len(notifs),
            "unread_count": _notifs().unread_count(recipient),
            "notifications": notifs,
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/notifications/{notification_id}/read")
def mark_read(notification_id: int, actor: str = ""):
    """Mark a notification as read."""
    try:
        ok = _notifs().mark_read(notification_id, actor)
        return {"notification_id": notification_id, "marked_read": ok}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/notifications/{recipient}/read-all")
def mark_all_read(recipient: str):
    """Mark all notifications for a recipient as read."""
    try:
        count = _notifs().mark_all_read(recipient)
        return {"recipient": recipient, "marked_read_count": count}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/notifications")
def get_all_unread_summary():
    """Summary of unread notification counts per recipient."""
    try:
        return {"unread_by_recipient": _notifs().get_all_unread()}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/notifications/escalate")
def run_escalation(escalate_to: str = "Buck Adams"):
    """Escalate all overdue unacknowledged notifications past their threshold."""
    try:
        escalated = _notifs().escalate_overdue(escalate_to)
        return {"escalated_count": len(escalated), "escalated": escalated}
    except Exception as e:
        raise HTTPException(500, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Audit Trail
# ──────────────────────────────────────────────────────────────────────────────

class AuditLogRequest(BaseModel):
    source: str
    event_type: str
    actor: Optional[str] = "system"
    entity_type: Optional[str] = ""
    entity_id: Optional[int] = None
    project_id: Optional[int] = None
    summary: Optional[str] = ""
    payload: Optional[dict] = None

@router.post("/audit")
def write_audit(req: AuditLogRequest):
    """Write an audit record to the platform audit log."""
    try:
        aid = _audit().log(
            source=req.source,
            event_type=req.event_type,
            actor=req.actor or "system",
            entity_type=req.entity_type or "",
            entity_id=req.entity_id,
            project_id=req.project_id,
            summary=req.summary or "",
            payload=req.payload,
        )
        return {"audit_id": aid, "status": "logged"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/audit")
def query_audit(
    source: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    project_id: Optional[int] = None,
    actor: Optional[str] = None,
    event_type: Optional[str] = None,
    since_hours: Optional[int] = None,
    limit: int = Query(100, le=500),
):
    """Query the platform audit log with filters."""
    try:
        records = _audit().query(
            source=source, entity_type=entity_type, entity_id=entity_id,
            project_id=project_id, actor=actor, event_type=event_type,
            since_hours=since_hours, limit=limit,
        )
        return {"count": len(records), "records": records}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/audit/sop/{sop_instance_id}")
def get_sop_audit(sop_instance_id: int):
    """Full audit trail for a SOP instance (workflow events + platform log)."""
    try:
        return _audit().get_full_sop_trail(sop_instance_id)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/audit/project/{project_id}/timeline")
def get_project_timeline(project_id: int, since_hours: int = 168):
    """Unified project timeline: SOPs + workflows + platform events."""
    try:
        return _audit().get_project_timeline(project_id, since_hours)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/audit/summary")
def audit_summary(project_id: Optional[int] = None):
    """Count of audit events by source in the last 24 hours."""
    try:
        return {"summary": _audit().summary(project_id)}
    except Exception as e:
        raise HTTPException(500, str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Unified Search Gateway
# ──────────────────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    sources: Optional[List[str]] = None
    project_filter: Optional[str] = None
    limit: int = 10
    score_threshold: float = 0.3

@router.post("/search")
def unified_search(req: SearchRequest):
    """
    Unified cross-source search.

    Auto-detects query intent and searches Postgres (vendors, projects, SOPs, bids, risks)
    and Qdrant (semantic: documents, lessons learned, historical costs).

    Optional: specify `sources` list to restrict: ["vendors", "projects", "sops",
    "bids", "risks", "qdrant_documents", "qdrant_lessons", "qdrant_costs"]
    """
    try:
        return _search().search(
            query=req.query,
            sources=req.sources,
            project_filter=req.project_filter,
            limit=req.limit,
            score_threshold=req.score_threshold,
        )
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search/vendors")
def search_vendors(q: str, limit: int = Query(10, le=50)):
    """Quick vendor search by name, trade, or contact."""
    try:
        return {"query": q, "results": _search().find_vendor(q, limit)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search/sops")
def search_sops(project: str = "", sop_number: str = "", limit: int = Query(10, le=50)):
    """Find SOP instances by project name or SOP number."""
    try:
        return {"results": _search().find_sop(project, sop_number, limit)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search/lessons")
def search_lessons(topic: str, limit: int = Query(5, le=20)):
    """Semantic search through lessons learned knowledge base."""
    try:
        return {"topic": topic, "results": _search().find_lessons_learned(topic, limit)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search/decisions")
def search_decisions(topic: str, limit: int = Query(5, le=20)):
    """Search past decision records for related decisions."""
    try:
        return {"topic": topic, "results": _search().find_decisions(topic, limit)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/search/full")
def full_search(req: SearchRequest):
    """Full search including related decisions and lessons learned."""
    try:
        return _search().search_with_decisions(req.query, req.limit)
    except Exception as e:
        raise HTTPException(500, str(e))
