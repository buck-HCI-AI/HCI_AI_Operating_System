"""Operating Rules Engine — FastAPI routes."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from rules_service import OperatingRulesService

router = APIRouter()


class RuleEvalRequest(BaseModel):
    context: str
    field: str
    value: object
    project_id: Optional[int] = None


class RuleUpdateRequest(BaseModel):
    condition_value: Optional[str] = None
    action: Optional[str] = None
    active: Optional[bool] = None
    change_reason: str
    modified_by: str


class ExceptionRequest(BaseModel):
    rule_code: str
    exception_reason: str
    risk_accepted: str
    mitigation: str
    approver: str
    expires_at: str
    created_by: str
    sop_instance_id: Optional[int] = None
    project_id: Optional[int] = None


@router.get("")
def info():
    return OperatingRulesService.info()


@router.get("/rules")
def list_rules(category: Optional[str] = None, active_only: bool = True):
    return {"rules": OperatingRulesService.list_rules(category, active_only)}


@router.get("/rules/{rule_code}")
def get_rule(rule_code: str):
    rule = OperatingRulesService.get_rule(rule_code)
    if not rule:
        raise HTTPException(404, f"Rule {rule_code} not found")
    return rule


@router.post("/evaluate")
def evaluate_rule(req: RuleEvalRequest):
    result = OperatingRulesService.evaluate_rule(req.context, req.field, req.value)
    return {
        "matched": result.matched,
        "rule_code": result.rule_code,
        "rule_name": result.rule_name,
        "action": result.action,
        "action_target": result.action_target,
        "authority": result.authority,
        "message": result.message,
    }


@router.patch("/rules/{rule_code}")
def update_rule(rule_code: str, req: RuleUpdateRequest):
    return OperatingRulesService.update_rule(
        rule_code, req.condition_value, req.action, req.active,
        req.change_reason, req.modified_by
    )


@router.post("/exception")
def create_exception(req: ExceptionRequest):
    return OperatingRulesService.create_exception(
        req.rule_code, req.exception_reason, req.risk_accepted,
        req.mitigation, req.approver, req.expires_at, req.created_by,
        req.sop_instance_id, req.project_id
    )
