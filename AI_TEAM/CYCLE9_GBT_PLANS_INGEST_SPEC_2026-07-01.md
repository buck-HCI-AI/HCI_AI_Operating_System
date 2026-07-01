# CYCLE9_GBT_PLANS_INGEST_SPEC
## Date: 2026-07-01 | Cycle: 9 Part 1 of 3 | Source: GBT Chief Architect

## Request
FastAPI POST /plans/ingest endpoint spec + PostgreSQL DDL for plan_documents table.
For Claude Code to implement immediately.

---

## 1. PostgreSQL DDL

```sql
CREATE TABLE IF NOT EXISTS plan_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id TEXT NOT NULL,
  filename TEXT NOT NULL,
  upload_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status TEXT NOT NULL DEFAULT 'UPLOADED',
  gemini_summary TEXT,
  sheet_count INTEGER,
  revision_number TEXT,
  flagged_rfis JSONB NOT NULL DEFAULT '[]'::jsonb,
  processing_errors TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_plan_documents_project_id ON plan_documents(project_id);
CREATE INDEX IF NOT EXISTS idx_plan_documents_status ON plan_documents(status);
```

## 2. Pydantic Models

```python
from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class PlanIngestResponse(BaseModel):
    id: UUID
    project_id: str
    filename: str
    upload_ts: datetime
    status: str
    message: str

class PlanDocumentOut(BaseModel):
    id: UUID
    project_id: str
    filename: str
    upload_ts: datetime
    status: str
    gemini_summary: Optional[str] = None
    sheet_count: Optional[int] = None
    revision_number: Optional[str] = None
    flagged_rfis: list[dict[str, Any]] = Field(default_factory=list)
    processing_errors: Optional[str] = None
```

## 3. FastAPI Endpoint (POST /plans/ingest)

```python
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.plan_documents import PlanDocument
from app.schemas.plan_documents import PlanIngestResponse
from app.services.plan_processing import process_plan_document

router = APIRouter(prefix="/plans", tags=["Plan Reader"])
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"application/pdf"}

@router.post("/ingest", response_model=PlanIngestResponse, status_code=202)
async def ingest_plan_document(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not project_id.strip():
        raise HTTPException(status_code=422, detail="project_id is required")
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    filename = Path(file.filename or "").name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File extension must be .pdf")
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="PDF exceeds 50MB limit")
    try:
        plan_doc = PlanDocument(project_id=project_id.strip(), filename=filename, status="UPLOADED")
        db.add(plan_doc)
        db.commit()
        db.refresh(plan_doc)
        storage_path = "/tmp/hci_plan_uploads/" + str(plan_doc.id) + "_" + filename
        Path("/tmp/hci_plan_uploads").mkdir(parents=True, exist_ok=True)
        with open(storage_path, "wb") as f:
            f.write(content)
        background_tasks.add_task(process_plan_document, plan_document_id=str(plan_doc.id), storage_path=storage_path)
        return PlanIngestResponse(id=plan_doc.id, project_id=plan_doc.project_id,
            filename=plan_doc.filename, upload_ts=plan_doc.upload_ts,
            status=plan_doc.status, message="Plan uploaded successfully. Processing started.")
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to ingest: " + str(exc))
```

## 4. SQLAlchemy Model (plan_documents)

```python
import uuid
from sqlalchemy import Column, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class PlanDocument(Base):
    __tablename__ = "plan_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(Text, nullable=False, index=True)
    filename = Column(Text, nullable=False)
    upload_ts = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    status = Column(Text, nullable=False, default="UPLOADED", index=True)
    gemini_summary = Column(Text, nullable=True)
    sheet_count = Column(Integer, nullable=True)
    revision_number = Column(Text, nullable=True)
    flagged_rfis = Column(JSONB, nullable=False, server_default="[]")
    processing_errors = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
```

## 5. Background Processing Stub

```python
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.plan_documents import PlanDocument

def process_plan_document(plan_document_id: str, storage_path: str) -> None:
    db: Session = SessionLocal()
    try:
        plan_doc = db.query(PlanDocument).filter(PlanDocument.id == plan_document_id).first()
        if not plan_doc: return
        plan_doc.status = "PROCESSING"
        db.commit()
        # TODO: 1. Validate PDF 2. Count sheets 3. Extract title block
        # 4. Send to Gemini 5. Extract RFIs 6. Store Project Brain refs
        plan_doc.status = "COMPLETE"
        db.commit()
    except Exception as exc:
        plan_doc.status = "FAILED"
        plan_doc.processing_errors = str(exc)
        db.commit()
    finally:
        db.close()
```

## 6. Error Handling Contract

400 - Non-PDF upload, empty file, file > 50MB, invalid extension
422 - Missing project_id, missing file, invalid form payload
500 - Database failure, file write failure, unexpected ingestion failure

---

## GBT Ruling
Ready for Claude Code to implement as first Plan Reader ingestion endpoint.

## Cycle Status
- Part 1 COMPLETE: /plans/ingest spec + plan_documents DDL
- Part 2 PENDING: Gemini n8n workflow spec (what nodes, what prompt, what output)
- Part 3 PENDING: research_queries table + CPM scheduling schema
