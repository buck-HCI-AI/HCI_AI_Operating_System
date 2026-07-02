# CYCLE9_GBT_CPM_RESEARCH_SCHEMA — Sprint 4 Foundation Schemas
## Date: 2026-07-01 | Cycle: 9 Part 3 of 3 | Source: GBT Chief Architect

## GBT Chief Architect Review
"Cycle 9 establishes the core persistence layer for Sprint 4:
- plan_documents provides durable storage and status tracking for the Plan Reader pipeline.
- cpm_activities introduces a schedule model capable of supporting true CPM analysis
  with predecessor/successor relationships.
- research_queries creates a governed repository for external research, preserving citations
  and requiring review before information influences project decisions.
- The GET /plans/{plan_id}/summary endpoint exposes processed plan intelligence through
  a clean API without exposing implementation details.
The next architectural step: connect these tables into the Unified Operational State Model
so Mission Control can present plans, schedules, research, approvals, and directives
as related operational objects rather than isolated datasets."

---

## 1. PostgreSQL DDL — cpm_activities

```sql
CREATE TABLE IF NOT EXISTS cpm_activities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  project_id TEXT NOT NULL,
  activity_id TEXT NOT NULL,
  -- activity_id = scheduler-assigned code (e.g. "A1010", "SS-205")
  -- Unique per project
  UNIQUE (project_id, activity_id),

  name TEXT NOT NULL,

  duration_days INTEGER NOT NULL CHECK (duration_days >= 0),

  start_planned DATE,
  end_planned DATE,
  start_actual DATE,
  end_actual DATE,

  float_days INTEGER,
  -- Total float. NULL = not yet calculated.
  -- 0 = critical activity.
  -- Negative = behind critical path.

  is_critical BOOLEAN NOT NULL DEFAULT FALSE,

  predecessors JSONB NOT NULL DEFAULT '[]'::jsonb,
  -- Array of { activity_id: str, relationship: "FS"|"SS"|"FF"|"SF", lag_days: int }

  successors JSONB NOT NULL DEFAULT '[]'::jsonb,
  -- Same schema as predecessors

  status TEXT NOT NULL DEFAULT 'NOT_STARTED',
  -- Values: NOT_STARTED | IN_PROGRESS | COMPLETE | DELAYED | ON_HOLD

  trade TEXT,
  -- e.g. "Concrete", "Framing", "MEP", "Electrical"

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cpm_activities_project_id ON cpm_activities(project_id);
CREATE INDEX IF NOT EXISTS idx_cpm_activities_status ON cpm_activities(status);
CREATE INDEX IF NOT EXISTS idx_cpm_activities_is_critical ON cpm_activities(is_critical);
CREATE INDEX IF NOT EXISTS idx_cpm_activities_activity_id ON cpm_activities(project_id, activity_id);
```

---

## 2. PostgreSQL DDL — research_queries

```sql
CREATE TABLE IF NOT EXISTS research_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  project_id TEXT,
  -- NULL = company-wide research not tied to a specific project

  query_text TEXT NOT NULL,

  query_type TEXT NOT NULL,
  -- Values: MATERIAL_COST | BUILDING_CODE | PRODUCT_SUBSTITUTION
  --         | AHJ_REQUIREMENT | MANUFACTURER_DOCS | GENERAL

  model_used TEXT NOT NULL DEFAULT 'sonar',
  -- sonar (default) or sonar-pro (complex queries only)

  response_text TEXT,
  -- Full Perplexity response

  citations JSONB NOT NULL DEFAULT '[]'::jsonb,
  -- Array of { url: str, title: str, snippet: str }

  status TEXT NOT NULL DEFAULT 'NEEDS_REVIEW',
  -- Values: NEEDS_REVIEW | APPROVED | REJECTED | ARCHIVED
  -- CRITICAL: Never auto-import to Project Brain.
  -- Perplexity answers are EVIDENCE, not project facts, until reviewed.

  reviewed_by TEXT,
  -- User ID or agent name who reviewed

  reviewed_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_research_queries_project_id ON research_queries(project_id);
CREATE INDEX IF NOT EXISTS idx_research_queries_status ON research_queries(status);
CREATE INDEX IF NOT EXISTS idx_research_queries_query_type ON research_queries(query_type);
CREATE INDEX IF NOT EXISTS idx_research_queries_created_at ON research_queries(created_at DESC);
```

---

## 3. FastAPI GET /plans/{plan_id}/summary

```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.plan_documents import PlanDocument
from app.schemas.plan_documents import PlanDocumentOut

router = APIRouter(prefix="/plans", tags=["Plan Reader"])

@router.get("/{plan_id}/summary", response_model=PlanDocumentOut)
def get_plan_summary(
    plan_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Return processed plan intelligence for a given plan_document_id.
    Returns 404 if plan does not exist.
    Returns 202 if plan is still processing.
    """
    plan_doc = db.query(PlanDocument).filter(
        PlanDocument.id == plan_id
    ).first()

    if not plan_doc:
        raise HTTPException(status_code=404, detail="Plan document not found")

    if plan_doc.status in ("UPLOADED", "PROCESSING"):
        raise HTTPException(
            status_code=202,
            detail="Plan is still processing. Check back shortly.",
        )

    return plan_doc
```

---

## 4. Predecessor/Successor JSON Schema

```json
[
  {
    "activity_id": "A1005",
    "relationship": "FS",
    "lag_days": 2
  },
  {
    "activity_id": "A1007",
    "relationship": "SS",
    "lag_days": 0
  }
]
```

Relationship types:
- FS = Finish to Start (most common)
- SS = Start to Start
- FF = Finish to Finish
- SF = Start to Finish

---

## 5. Claude Code Implementation Checklist

- [ ] Run migration: CREATE TABLE cpm_activities
- [ ] Run migration: CREATE TABLE research_queries
- [ ] Create SQLAlchemy model: CpmActivity
- [ ] Create SQLAlchemy model: ResearchQuery
- [ ] Add GET /plans/{plan_id}/summary to plans router
- [ ] Wire plans router into main FastAPI app
- [ ] Test: POST /plans/ingest with valid PDF
- [ ] Test: GET /plans/{id}/summary while PROCESSING -> 202
- [ ] Test: GET /plans/{id}/summary after COMPLETE -> 200
- [ ] Test: GET /plans/{id}/summary unknown id -> 404
- [ ] Test: cpm_activities unique constraint (project_id, activity_id)
- [ ] Test: research_queries status lifecycle (NEEDS_REVIEW -> APPROVED)
- [ ] Commit all with message: feat: Sprint 4 schemas - plan_documents + cpm_activities + research_queries

---

## Cycle 9 Complete

All 3 parts committed:
- Part 1: POST /plans/ingest + plan_documents DDL (commit 478eeeb)
- Part 2: WF-PLAN-001 Gemini n8n workflow + constrained system prompt + JSON schema (commit 8a74fb4)
- Part 3: cpm_activities DDL + research_queries DDL + GET /plans/{id}/summary

Sprint 4 persistence layer is fully specified. Claude Code implements on restart.
