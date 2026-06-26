"""Decision Intelligence Service — FastAPI routes."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from decision_service import DecisionIntelligenceService

router = APIRouter()


class DecisionCreateRequest(BaseModel):
    project_id: Optional[int] = None
    decision_type: str
    decision_date: str
    decision_maker: str
    context: str
    selected_option: str
    rationale: str
    approver: Optional[str] = None
    options_considered: Optional[List[dict]] = None
    risk_accepted: Optional[str] = None
    cost_impact: Optional[float] = None
    schedule_impact: Optional[int] = None
    related_rfi_ids: Optional[List[int]] = None
    related_co_ids: Optional[List[int]] = None


class OutcomeUpdateRequest(BaseModel):
    outcome: str
    outcome_rating: int
    lessons_learned: str = ""


@router.get("")
def info():
    return DecisionIntelligenceService.info()


@router.post("/decisions")
def create_decision(req: DecisionCreateRequest):
    return DecisionIntelligenceService.create_decision(
        req.project_id, req.decision_type, req.decision_date,
        req.decision_maker, req.context, req.selected_option, req.rationale,
        req.approver, req.options_considered, req.risk_accepted,
        req.cost_impact, req.schedule_impact, req.related_rfi_ids, req.related_co_ids
    )


@router.get("/decisions")
def list_decisions(project_id: Optional[int] = None,
                   decision_type: Optional[str] = None,
                   limit: int = 50):
    return {"decisions": DecisionIntelligenceService.get_decisions(
        project_id, decision_type, limit
    )}


@router.patch("/decisions/{decision_id}/outcome")
def update_outcome(decision_id: int, req: OutcomeUpdateRequest):
    return DecisionIntelligenceService.update_outcome(
        decision_id, req.outcome, req.outcome_rating, req.lessons_learned
    )


@router.get("/decisions/search")
def search_decisions(q: str, project_id: Optional[int] = None, limit: int = 8):
    return {"query": q, "results": DecisionIntelligenceService.search(q, project_id, limit)}


@router.get("/decisions/pending-outcomes")
def pending_outcomes():
    return {"pending": DecisionIntelligenceService.pending_outcomes()}
