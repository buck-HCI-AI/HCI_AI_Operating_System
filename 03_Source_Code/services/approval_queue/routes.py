import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from approval_queue_service import ApprovalQueueService

router = APIRouter()


class EnqueueRequest(BaseModel):
    workflow: str
    action_type: str
    target_system: str
    target_id: str
    target_description: str
    proposed_payload: dict
    reason: str
    project_id: Optional[int] = None
    actor: Optional[str] = "system"
    priority: Optional[str] = "normal"
    source_data: Optional[dict] = None
    rollback_path: Optional[str] = None


class ApproveRequest(BaseModel):
    approved_by: Optional[str] = "Buck Adams"


class RejectRequest(BaseModel):
    rejected_by: Optional[str] = "Buck Adams"
    reason: Optional[str] = ""


@router.get("")
def service_info():
    return {"service": "approval-queue", "description": "All proposed write actions pending Buck approval"}


@router.get("/summary")
def get_summary():
    return ApprovalQueueService.summary()


@router.post("/enqueue")
def enqueue(req: EnqueueRequest):
    return ApprovalQueueService.enqueue(
        workflow=req.workflow, action_type=req.action_type,
        target_system=req.target_system, target_id=req.target_id,
        target_description=req.target_description,
        proposed_payload=req.proposed_payload, reason=req.reason,
        project_id=req.project_id, actor=req.actor or "system",
        priority=req.priority or "normal", source_data=req.source_data,
        rollback_path=req.rollback_path,
    )


@router.get("/pending")
def get_pending(project_id: Optional[int] = None, workflow: Optional[str] = None,
                limit: int = Query(50, le=200)):
    return {"items": ApprovalQueueService.get_queue("pending", project_id, workflow, limit)}


@router.get("/items")
def get_items(status: Optional[str] = None, project_id: Optional[int] = None,
              limit: int = Query(50, le=200)):
    return {"items": ApprovalQueueService.get_queue(status, project_id, limit=limit)}


@router.get("/items/{queue_id}")
def get_item(queue_id: int):
    result = ApprovalQueueService.get_item(queue_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/items/{queue_id}/approve")
def approve(queue_id: int, req: ApproveRequest):
    result = ApprovalQueueService.approve(queue_id, req.approved_by or "Buck Adams")
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/items/{queue_id}/reject")
def reject(queue_id: int, req: RejectRequest):
    result = ApprovalQueueService.reject(queue_id, req.rejected_by or "Buck Adams", req.reason or "")
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@router.post("/items/{queue_id}/execute")
def execute(queue_id: int, actor: str = "system"):
    """Mark an approved action as executed. Caller must have already applied the actual change."""
    result = ApprovalQueueService.mark_executed(queue_id, actor)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result
