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


@router.post("/send")
def send_notification(payload: NotificationPayload):
    return NotificationService.send(
        title=payload.title,
        message=payload.message,
        severity=payload.severity,
        tags=payload.tags,
        action_url=payload.action_url,
        topic=payload.topic,
    )


@router.post("/morning-brief-push")
def morning_brief_push(inbox_count: int, health: str = "🟢", one_action: Optional[str] = None):
    return NotificationService.morning_brief_push(inbox_count, health, one_action)


@router.post("/alert/inbox/{exec_id}")
def alert_inbox(exec_id: str, title: str, approve_url: str):
    return NotificationService.alert_critical_inbox(exec_id, title, approve_url)


@router.post("/alert/system-down/{service}")
def alert_system_down(service: str):
    return NotificationService.alert_system_down(service)
