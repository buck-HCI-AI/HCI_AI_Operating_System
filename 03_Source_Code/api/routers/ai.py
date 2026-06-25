"""
AI services scaffold.
Placeholder endpoints for the Agent Layer (Phase 4).
All endpoints return 501 Not Implemented with a roadmap hint.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

ROADMAP = "Agent Layer — Phase 4 directive. See AI_TEAM/06_NEXT_SESSION.md."


class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    project_hint: Optional[str] = None
    agent: str = "executive"


class AgentInfo(BaseModel):
    name: str
    description: str
    status: str
    endpoint: str


PLANNED_AGENTS = [
    AgentInfo(
        name="executive",
        description="Answers questions about projects, vendors, bids, and schedule using full knowledge base",
        status="planned",
        endpoint="/api/v1/ai/query",
    ),
    AgentInfo(
        name="bid-leveler",
        description="Analyzes and levels competing bids, produces award recommendations",
        status="partial — WF-007 in n8n",
        endpoint="/api/v1/ai/bid-leveling",
    ),
    AgentInfo(
        name="document-classifier",
        description="AI-enhanced classifier for project, category, and CSI detection (replaces keyword matching)",
        status="planned — keyword classifier live",
        endpoint="/api/v1/ai/classify",
    ),
    AgentInfo(
        name="morning-brief",
        description="Compiles and sends the daily morning brief email",
        status="live — WF-003",
        endpoint="/workflows/wf003/morning-brief",
    ),
]


@router.get("/agents")
def list_agents():
    """List available and planned AI agents."""
    return {
        "agents": [a.model_dump() for a in PLANNED_AGENTS],
        "note": ROADMAP,
    }


@router.post("/query")
def ai_query(req: QueryRequest):
    """Executive agent query — NOT YET IMPLEMENTED."""
    return {
        "status": "not_implemented",
        "agent": req.agent,
        "query": req.query,
        "message": "Executive Agent (Phase 4). Searches drive_memory + project_memory + vendor_memory.",
        "roadmap": ROADMAP,
        "workaround": "Use POST /api/v1/search for semantic search now.",
    }


@router.post("/classify")
def classify_document(filename: str, content_preview: Optional[str] = None):
    """Classify a document using the keyword classifier (AI upgrade planned)."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ingestion"))
    from classifier import classify
    result = classify(filename, content_preview or "")
    return {
        "filename": filename,
        "classification": result,
        "classifier": "keyword-based v1 (AI upgrade planned for Phase 4)",
    }
