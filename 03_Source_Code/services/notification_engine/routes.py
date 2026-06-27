"""
Notification Engine routes — POST /api/v1/services/notifications/send
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from notification_engine.notification_svc import NotificationService

router = APIRouter()


class NotificationPayload(BaseModel):
    title: str
    message: str
    severity: str = "MEDIUM"
    tags: list[str] = []
    action_url: Optional[str] = None
    topic: Optional[str] = None
    actions: Optional[list[dict]] = None


class ApprovalPayload(BaseModel):
    exec_id: str
    title: str
    approve_token: str
    reject_token: str
    defer_token: str
    deadline: Optional[str] = None
    confidence: str = "High"


@router.post("/send")
def send_notification(payload: NotificationPayload):
    return NotificationService.send(
        title=payload.title,
        message=payload.message,
        severity=payload.severity,
        tags=payload.tags,
        action_url=payload.action_url,
        topic=payload.topic,
        actions=payload.actions,
    )


@router.post("/approval-required")
def notify_approval_required(payload: ApprovalPayload):
    """Send actionable Approve/Reject/Defer notification to Buck's phone."""
    return NotificationService.approval_required(
        exec_id=payload.exec_id,
        title=payload.title,
        approve_token=payload.approve_token,
        reject_token=payload.reject_token,
        defer_token=payload.defer_token,
        deadline=payload.deadline,
        confidence=payload.confidence,
    )


@router.post("/morning-brief-push")
def morning_brief_push(
    inbox_count: int,
    health: str = "",
    one_action: Optional[str] = None,
    top_exec_id: Optional[str] = None,
    approve_token: Optional[str] = None,
    reject_token: Optional[str] = None,
    defer_token: Optional[str] = None,
):
    return NotificationService.morning_brief_push(
        inbox_count=inbox_count,
        health=health,
        one_action=one_action,
        top_exec_id=top_exec_id,
        approve_token=approve_token,
        reject_token=reject_token,
        defer_token=defer_token,
    )


@router.post("/alert/inbox/{exec_id}")
def alert_inbox(exec_id: str, title: str, approve_url: str):
    return NotificationService.alert_critical_inbox(exec_id, title, approve_url)


@router.post("/alert/system-down/{service}")
def alert_system_down(service: str):
    return NotificationService.alert_system_down(service)
