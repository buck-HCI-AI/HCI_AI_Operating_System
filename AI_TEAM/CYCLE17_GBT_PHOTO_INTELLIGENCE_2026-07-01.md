# CYCLE 17 — Sprint 5 Priority 4: Photo Intelligence
**GBT Cycle:** 17 | **Date:** 2026-07-01 | **Status:** SPEC COMPLETE
**Sprint:** 5 | **Priority:** 4 of 6 | **Depends on:** Cycles 14 (RFI), 15 (Daily Field), 18 (Punch List)

---

## Architecture Overview

Project photos should become searchable, structured construction evidence. They should support:
- daily field reports
- RFIs
- submittals
- punch lists
- safety
- quality
- progress tracking
- warranty history

---

## 1) Storage Architecture

**Primary recommendation: MinIO (self-hosted S3-compatible)**

| Option | Recommendation |
|--------|---------------|
| MinIO (self-hosted) | PRIMARY — S3-compatible, runs on same server as FastAPI, no cloud dependency |
| AWS S3 | SECONDARY — if HCI moves to cloud hosting |
| Local filesystem | FALLBACK — dev/test only, not production |

**File path convention:**
```
{bucket}/projects/{project_id}/photos/{YYYY}/{MM}/{uuid}.{ext}
{bucket}/projects/{project_id}/thumbs/{YYYY}/{MM}/{uuid}_thumb.jpg
```

**MinIO config (environment variables):**
```
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=hci_minio_key
MINIO_SECRET_KEY=hci_minio_secret
MINIO_BUCKET=hci-project-photos
MINIO_SECURE=false
```

---

## 2) PostgreSQL DDL

### project_photos

```sql
CREATE TABLE IF NOT EXISTS project_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    uploader_user_id TEXT NOT NULL,
    taken_at TIMESTAMPTZ,
    location_tag TEXT,
    linked_entity_type TEXT,
    -- allowed: daily_report, rfi, submittal, punch_item
    linked_entity_id UUID,
    storage_path TEXT NOT NULL,
    thumbnail_path TEXT,
    file_size_bytes BIGINT NOT NULL,
    original_filename TEXT NOT NULL,
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    ai_classification JSONB NOT NULL DEFAULT '{}'::jsonb,
    ai_description TEXT,
    ai_flags JSONB NOT NULL DEFAULT '[]'::jsonb,
    reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_project_photos_linked_entity_type CHECK (
        linked_entity_type IS NULL OR linked_entity_type IN ('daily_report', 'rfi', 'submittal', 'punch_item')
    )
);

CREATE INDEX IF NOT EXISTS idx_project_photos_project_id ON project_photos(project_id);
CREATE INDEX IF NOT EXISTS idx_project_photos_linked_entity ON project_photos(linked_entity_type, linked_entity_id);
CREATE INDEX IF NOT EXISTS idx_project_photos_created_at ON project_photos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_photos_reviewed ON project_photos(reviewed);
-- GIN index for JSONB tag search:
CREATE INDEX IF NOT EXISTS idx_project_photos_tags ON project_photos USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_project_photos_ai_flags ON project_photos USING GIN (ai_flags);
```

---

## 3) Gemini Vision Integration

### What to Send

```json
{
  "linked_entity_type": "daily_report",
  "location_tag": "Main level kitchen",
  "photo_context": "Uploaded from daily field report",
  "image": "base64_encoded_image_data"
}
```

### Gemini System Prompt

```
You are the HCI Construction Photo Review Assistant.
You are reviewing a single construction project photo.

You MAY:
- describe what is visible
- classify the photo type
- identify possible safety concerns
- identify possible quality concerns
- identify visible elements (materials, trades, equipment)
- suggest searchable tags

You MUST NOT:
- make definitive code compliance judgments
- identify specific people
- make legal determinations
- calculate quantities or dimensions from photos

If uncertain, use UNKNOWN. Return ONLY valid JSON. No prose.
```

### Required Gemini JSON Output

```json
{
  "classification": {
    "primary_type": "progress",
    "secondary_types": ["material"],
    "confidence": 0.86
  },
  "description": "Photo shows framing work in progress at main level.",
  "visible_elements": ["wood framing", "electrical boxes", "temporary lighting"],
  "suggested_tags": ["framing", "electrical rough-in", "interior"],
  "safety_flags": [
    {
      "flag": "possible_trip_hazard",
      "description": "Loose material appears to be stored in walkway.",
      "severity": "yellow",
      "confidence": 0.62
    }
  ],
  "quality_flags": []
}
```

**Primary type values:** progress, safety, defect, material, milestone, inspection, documentation, unknown
**Safety flag severity:** red (immediate stop-work), yellow (review required), info (note only)

---

## 4) n8n Photo Processing Pipeline

**Workflow:** WF-PHOTO-001
**Trigger:** POST /photos/upload fires background task OR scheduled scan of unprocessed photos

```sql
-- Scheduled scan query for unprocessed photos:
SELECT * FROM project_photos WHERE ai_classification = '{}'::jsonb ORDER BY created_at ASC LIMIT 25;
```

**Workflow Nodes (10):**
1. Trigger / Queue — receives photo_id from upload hook or scheduled scan
2. Get photo metadata from Gateway — GET /photos/id/{photo_id}
3. Fetch image from MinIO — retrieve binary content
4. Create thumbnail — resize to 400px max dimension, save to thumb path
5. Send image + context to Gemini Vision — base64 encode + send with system prompt
6. Validate JSON response — check required fields, handle UNKNOWN values
7. Update project_photos — PATCH ai_classification, ai_description, ai_flags, tags
8. If RED safety flag → create Mission Control alert
9. If linked to daily_report → update report photo summary
10. Complete — log processing time

---

## 5) FastAPI Endpoints (app/api/routers/photos.py)

```python
from pathlib import Path
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.project_photos import ProjectPhoto
from app.schemas.project_photos import PhotoOut, PhotoTagsUpdate
from app.services.photo_storage import save_photo_to_minio
from app.services.photo_processing import process_photo_async

router = APIRouter(prefix="/photos", tags=["Photo Intelligence"])

MAX_PHOTO_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/heic", "image/webp"}
VALID_ENTITY_TYPES = {"daily_report", "rfi", "submittal", "punch_item"}


@router.post("/upload", response_model=PhotoOut, status_code=201)
async def upload_photo(
    background_tasks: BackgroundTasks,
    project_id: str = Form(...),
    uploader_user_id: str = Form(...),
    file: UploadFile = File(...),
    taken_at: Optional[datetime] = Form(default=None),
    location_tag: Optional[str] = Form(default=None),
    linked_entity_type: Optional[str] = Form(default=None),
    linked_entity_id: Optional[UUID] = Form(default=None),
    notes: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, HEIC, WEBP allowed")
    filename = Path(file.filename or "").name
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > MAX_PHOTO_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Photo exceeds 25MB limit")
    if linked_entity_type and linked_entity_type not in VALID_ENTITY_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid linked_entity_type: {linked_entity_type}")
    try:
        storage_result = save_photo_to_minio(
            project_id=project_id, filename=filename,
            content=content, content_type=file.content_type,
        )
        photo = ProjectPhoto(
            project_id=project_id,
            uploader_user_id=uploader_user_id,
            taken_at=taken_at,
            location_tag=location_tag,
            linked_entity_type=linked_entity_type,
            linked_entity_id=linked_entity_id,
            storage_path=storage_result["storage_path"],
            file_size_bytes=len(content),
            original_filename=filename,
            notes=notes,
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        background_tasks.add_task(process_photo_async, photo.id)
        return photo
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(exc)}")


@router.get("/project/{project_id}", response_model=List[PhotoOut])
def get_project_photos(
    project_id: str,
    entity_type: Optional[str] = None,
    reviewed: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ProjectPhoto).filter(ProjectPhoto.project_id == project_id)
    if entity_type:
        query = query.filter(ProjectPhoto.linked_entity_type == entity_type)
    if reviewed is not None:
        query = query.filter(ProjectPhoto.reviewed == reviewed)
    return query.order_by(ProjectPhoto.created_at.desc()).all()


@router.get("/id/{photo_id}", response_model=PhotoOut)
def get_photo(photo_id: UUID, db: Session = Depends(get_db)):
    photo = db.query(ProjectPhoto).filter(ProjectPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.patch("/id/{photo_id}/tags", response_model=PhotoOut)
def update_photo_tags(photo_id: UUID, payload: PhotoTagsUpdate, db: Session = Depends(get_db)):
    photo = db.query(ProjectPhoto).filter(ProjectPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    photo.tags = payload.tags
    if payload.reviewed is not None:
        photo.reviewed = payload.reviewed
    if payload.notes is not None:
        photo.notes = payload.notes
    try:
        db.commit()
        db.refresh(photo)
        return photo
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update photo: {str(exc)}")
```

---

## 6) Endpoint Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /photos/upload | Upload photo (multipart), trigger async AI processing |
| GET | /photos/project/{project_id} | List photos for project (filter by entity_type, reviewed) |
| GET | /photos/id/{photo_id} | Get single photo by ID |
| PATCH | /photos/id/{photo_id}/tags | Update tags, reviewed flag, notes |

> Route note: GET /photos/id/{id} and GET /photos/project/{project_id} avoids routing collision. Consistent with Cycle 15 pattern.

---

## 7) Pydantic Schemas (app/schemas/project_photos.py)

```python
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class PhotoOut(BaseModel):
    id: UUID
    project_id: str
    uploader_user_id: str
    taken_at: Optional[datetime] = None
    location_tag: Optional[str] = None
    linked_entity_type: Optional[str] = None
    linked_entity_id: Optional[UUID] = None
    storage_path: str
    thumbnail_path: Optional[str] = None
    file_size_bytes: int
    original_filename: str
    tags: List[Any] = Field(default_factory=list)
    ai_classification: dict[str, Any] = Field(default_factory=dict)
    ai_description: Optional[str] = None
    ai_flags: List[Any] = Field(default_factory=list)
    reviewed: bool
    notes: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class PhotoTagsUpdate(BaseModel):
    tags: List[str] = Field(default_factory=list)
    reviewed: Optional[bool] = None
    notes: Optional[str] = None
```

---

## 8) SQLAlchemy Model (app/models/project_photos.py)

```python
import uuid
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from app.database import Base

class ProjectPhoto(Base):
    __tablename__ = "project_photos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(Text, nullable=False, index=True)
    uploader_user_id = Column(Text, nullable=False)
    taken_at = Column(DateTime(timezone=True), nullable=True)
    location_tag = Column(Text, nullable=True)
    linked_entity_type = Column(Text, nullable=True)
    linked_entity_id = Column(UUID(as_uuid=True), nullable=True)
    storage_path = Column(Text, nullable=False)
    thumbnail_path = Column(Text, nullable=True)
    file_size_bytes = Column(BigInteger, nullable=False)
    original_filename = Column(Text, nullable=False)
    tags = Column(JSONB, nullable=False, default=list)
    ai_classification = Column(JSONB, nullable=False, default=dict)
    ai_description = Column(Text, nullable=True)
    ai_flags = Column(JSONB, nullable=False, default=list)
    reviewed = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        CheckConstraint(
            "linked_entity_type IS NULL OR linked_entity_type IN ('daily_report','rfi','submittal','punch_item')",
            name="chk_project_photos_linked_entity_type",
        ),
    )
```

---

## 9) Linking Photos to Construction Records

**Daily Field Reports:** `linked_entity_type="daily_report"`, `linked_entity_id=report.id`. Phase 2: update daily_field_reports JSONB to include photo_ids array.

**RFIs:** `linked_entity_type="rfi"`, `linked_entity_id=rfi.id`. Photos provide visual evidence for RFI questions and responses.

**Submittals:** `linked_entity_type="submittal"`, `linked_entity_id=submittal.id`. Shop drawing approval evidence.

**Punch Items:** `linked_entity_type="punch_item"`, `linked_entity_id=punch_item.id`. Punch list architecture in Cycle 18 — link type reserved now.

**Mission Control Photo Intelligence Output:**
```json
{
  "project_id": "101F",
  "photo_intelligence": {
    "photos_uploaded_today": 34,
    "unreviewed_ai_flags": 5,
    "red_safety_flags": 1,
    "quality_flags": 3,
    "linked_daily_report_photos": 22,
    "linked_rfi_photos": 4
  }
}
```

---

## 10) Test Cases

| # | Test | Expected |
|---|------|----------|
| 1 | Upload valid JPEG photo | 201, photo created, background task queued |
| 2 | Upload invalid file type (PDF) | 400 |
| 3 | Upload photo exceeding 25MB | 400 |
| 4 | Upload with invalid linked_entity_type | 400 |
| 5 | Upload with empty file | 400 |
| 6 | GET /photos/project/{project_id} | 200 list ordered by created_at desc |
| 7 | GET /photos/project with entity_type filter | Only matching entity type returned |
| 8 | GET /photos/id/{photo_id} | 200 single photo |
| 9 | GET /photos/id non-existent | 404 |
| 10 | PATCH tags update | 200, tags and reviewed updated |
| 11 | AI processing: Gemini JSON validation | Valid JSON stored in ai_classification |
| 12 | Red safety flag creates Mission Control alert hook | Alert created |

---

## 11) Router Registration

In app/main.py:
```python
from app.api.routers import photos
app.include_router(photos.router)
```

---

## Definition of Done

Photo Intelligence Phase 1 complete when:
- [ ] MinIO/S3-compatible storage is configured
- [ ] project_photos table exists
- [ ] Photos upload through FastAPI (multipart)
- [ ] Metadata stored in PostgreSQL
- [ ] Thumbnails generated or reserved
- [ ] Gemini Vision classifies, describes, tags, and flags photos
- [ ] Photos link to daily_field_reports, RFIs, submittals, punch_items
- [ ] Mission Control surfaces photo safety/quality flags
- [ ] WF-PHOTO-001 n8n pipeline documented
- [ ] 12 test cases pass

---

*Spec generated by GBT Cycle 17 | BC Operations Intelligence | 2026-07-01*
