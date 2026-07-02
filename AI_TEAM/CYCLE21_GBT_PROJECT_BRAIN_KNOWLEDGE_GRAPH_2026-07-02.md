# CYCLE21 — Sprint 6 Priority 1: Project Brain 2.0 — Knowledge Graph Architecture
**Cycle:** 21
**Sprint:** 6
**Priority:** 1
**Date:** 2026-07-02
**Author:** GBT (HCI Chief Architect)
**Status:** SPEC COMPLETE — Ready for Code Implementation

---

## Overview

Project Brain 2.0 is the shift from tables of records to connected construction intelligence.

The system now stores RFIs, photos, punch items, POs, daily reports, schedules, costs, weather alerts, and warranty items. The next step is making the system understand how they relate.

**The goal:**
```
Photo
→ documents punch item
→ located in kitchen
→ tied to drawing A6.2
→ related to RFI-014
→ caused 3-day schedule impact
→ created $4,500 cost exposure
→ assigned to vendor
→ tracked through warranty
```

---

## 1) Knowledge Graph Model

The graph is implemented as a relational edge table in PostgreSQL.

- Each existing table remains the source of truth for its own entity
- The graph stores relationships between entities
- This avoids duplicating business data while allowing cross-table intelligence

### Entity Types

```
project
rfi
submittal
daily_field_report
purchase_order
long_lead_material
project_photo
punch_item
warranty_item
budget_line_item
cpm_activity
cost_forecast
weather_alert
bid_package
plan_document
vendor
change_order
approval
task
room
location
```

Not every entity type needs a table on day one. Some, like `room` or `location`, can begin as typed graph entities and later become formal tables.

---

## 2) PostgreSQL DDL — project_entity_links

```sql
CREATE TABLE IF NOT EXISTS project_entity_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id TEXT NOT NULL,

    source_entity_type TEXT NOT NULL,
    source_entity_id UUID NOT NULL,

    target_entity_type TEXT NOT NULL,
    target_entity_id UUID NOT NULL,

    link_type TEXT NOT NULL,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_project_entity_links_no_self_link CHECK (
        NOT (
            source_entity_type = target_entity_type
            AND source_entity_id = target_entity_id
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_project_entity_links_project_id
    ON project_entity_links(project_id);

CREATE INDEX IF NOT EXISTS idx_project_entity_links_source
    ON project_entity_links(source_entity_type, source_entity_id);

CREATE INDEX IF NOT EXISTS idx_project_entity_links_target
    ON project_entity_links(target_entity_type, target_entity_id);

CREATE INDEX IF NOT EXISTS idx_project_entity_links_type
    ON project_entity_links(link_type);

CREATE INDEX IF NOT EXISTS idx_project_entity_links_project_type
    ON project_entity_links(project_id, link_type);

-- Optional: Prevent duplicate edges
CREATE UNIQUE INDEX IF NOT EXISTS uq_project_entity_links_unique_edge
ON project_entity_links (
    project_id,
    source_entity_type,
    source_entity_id,
    target_entity_type,
    target_entity_id,
    link_type
);
```

---

## 3) Link Type Vocabulary

Use snake_case. Link types describe the relationship direction.

### Photo Links
```
photo_documents_daily_report
photo_documents_rfi
photo_documents_submittal
photo_documents_punch
photo_documents_warranty
photo_documents_material_delivery
photo_documents_safety_issue
photo_documents_quality_issue
photo_shows_progress_on_activity
photo_shows_location
photo_shows_defect
```

### RFI Links
```
rfi_references_plan
rfi_references_spec
rfi_impacts_schedule
rfi_impacts_cost
rfi_created_from_field_issue
rfi_created_from_plan_review
rfi_resolved_by_response
rfi_triggered_change_order
rfi_linked_to_punch
rfi_linked_to_submittal
```

### Submittal Links
```
submittal_references_spec
submittal_required_for_activity
submittal_blocks_procurement
submittal_blocks_installation
submittal_linked_to_bid_package
submittal_linked_to_purchase_order
submittal_resolved_by_review
```

### Daily Field Report Links
```
daily_report_documents_activity
daily_report_reports_issue
daily_report_reports_weather_delay
daily_report_reports_safety_incident
daily_report_reports_material_delivery
daily_report_created_rfi
daily_report_created_punch
daily_report_updated_schedule
```

### Punch / Quality Links
```
field_issue_became_punch
punch_documented_by_photo
punch_assigned_to_vendor
punch_related_to_rfi
punch_related_to_submittal
punch_blocks_closeout
punch_resolved_by_vendor
punch_resolved_by_co
punch_created_warranty_item
```

### Procurement Links
```
bid_package_awarded_to_vendor
bid_package_created_purchase_order
purchase_order_for_bid_package
purchase_order_includes_material
material_delayed_activity
material_required_for_activity
material_documented_by_photo
material_impacts_cost_forecast
long_lead_material_blocks_schedule
```

### Schedule Links
```
activity_references_plan
activity_blocked_by_rfi
activity_blocked_by_submittal
activity_blocked_by_material
activity_delayed_by_weather
activity_updated_by_daily_report
activity_impacts_project_health
activity_impacts_cost_forecast
```

### Cost / Finance Links
```
budget_line_impacted_by_rfi
budget_line_impacted_by_purchase_order
budget_line_impacted_by_change_order
cost_forecast_includes_budget_line
cost_forecast_includes_pending_change
rfi_impacts_budget_line
purchase_order_commits_budget_line
```

### Weather Links
```
weather_alert_impacts_activity
weather_alert_documented_by_daily_report
weather_alert_created_schedule_risk
weather_alert_affects_concrete
weather_alert_affects_roofing
weather_alert_affects_excavation
```

### Warranty Links
```
warranty_created_from_punch
warranty_linked_to_vendor
warranty_documented_by_photo
warranty_related_to_material
warranty_claim_created_punch
```

### Governance Links
```
approval_authorizes_action
approval_blocks_action
directive_created_task
directive_implemented_commit
task_resolves_issue
task_blocks_project
```

---

## 4) Pydantic Models

```python
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class EntityLinkCreate(BaseModel):
    project_id: str
    source_entity_type: str
    source_entity_id: UUID
    target_entity_type: str
    target_entity_id: UUID
    link_type: str
    notes: Optional[str] = None

class EntityLinkOut(BaseModel):
    id: UUID
    project_id: str
    source_entity_type: str
    source_entity_id: UUID
    target_entity_type: str
    target_entity_id: UUID
    link_type: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EntityGraphOut(BaseModel):
    entity_type: str
    entity_id: UUID
    project_id: Optional[str] = None
    links: list[EntityLinkOut]
```

---

## 5) SQLAlchemy Model

```python
import uuid

from sqlalchemy import Column, DateTime, Text, CheckConstraint, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

class ProjectEntityLink(Base):
    __tablename__ = "project_entity_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    project_id = Column(Text, nullable=False, index=True)

    source_entity_type = Column(Text, nullable=False)
    source_entity_id = Column(UUID(as_uuid=True), nullable=False)

    target_entity_type = Column(Text, nullable=False)
    target_entity_id = Column(UUID(as_uuid=True), nullable=False)

    link_type = Column(Text, nullable=False, index=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "NOT (source_entity_type = target_entity_type AND source_entity_id = target_entity_id)",
            name="chk_project_entity_links_no_self_link",
        ),
        UniqueConstraint(
            "project_id",
            "source_entity_type",
            "source_entity_id",
            "target_entity_type",
            "target_entity_id",
            "link_type",
            name="uq_project_entity_links_unique_edge",
        ),
    )
```

---

## 6) Graph Query Service

File: `app/services/project_brain_graph_service.py`

### Get All Direct Links (Bidirectional)
```python
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.project_entity_links import ProjectEntityLink

def get_entity_links(
    entity_type: str,
    entity_id: UUID,
    db: Session,
) -> list[ProjectEntityLink]:
    return (
        db.query(ProjectEntityLink)
        .filter(
            (
                (ProjectEntityLink.source_entity_type == entity_type)
                & (ProjectEntityLink.source_entity_id == entity_id)
            )
            |
            (
                (ProjectEntityLink.target_entity_type == entity_type)
                & (ProjectEntityLink.target_entity_id == entity_id)
            )
        )
        .order_by(ProjectEntityLink.created_at.desc())
        .all()
    )

def create_entity_link(payload, db: Session) -> ProjectEntityLink:
    link = ProjectEntityLink(
        project_id=payload.project_id,
        source_entity_type=payload.source_entity_type,
        source_entity_id=payload.source_entity_id,
        target_entity_type=payload.target_entity_type,
        target_entity_id=payload.target_entity_id,
        link_type=payload.link_type,
        notes=payload.notes,
    )

    db.add(link)

    try:
        db.commit()
        db.refresh(link)
        return link

    except IntegrityError:
        db.rollback()
        raise ValueError("Entity link already exists")
```

---

## 7) FastAPI Endpoints

Router: `app/api/routers/project_brain_graph.py`

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.project_brain_graph import (
    EntityLinkCreate,
    EntityLinkOut,
    EntityGraphOut,
)
from app.services.project_brain_graph_service import (
    create_entity_link,
    get_entity_links,
)

router = APIRouter(prefix="/brain", tags=["Project Brain Graph"])

@router.post("/links", response_model=EntityLinkOut, status_code=201)
def create_project_entity_link(
    payload: EntityLinkCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_entity_link(payload, db)

    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create entity link: {str(exc)}",
        )

@router.get(
    "/entity/{entity_type}/{entity_id}/links",
    response_model=EntityGraphOut,
)
def get_project_entity_links(
    entity_type: str,
    entity_id: UUID,
    db: Session = Depends(get_db),
):
    links = get_entity_links(
        entity_type=entity_type,
        entity_id=entity_id,
        db=db,
    )

    project_id = links[0].project_id if links else None

    return EntityGraphOut(
        entity_type=entity_type,
        entity_id=entity_id,
        project_id=project_id,
        links=links,
    )
```

---

## 8) Automatic Link Creation Rules

Graph links should be created automatically when normal workflows happen.

### Photo Upload
When a photo is uploaded with `linked_entity_type` and `linked_entity_id`:
- `photo_documents_punch`
- `photo_documents_rfi`
- `photo_documents_daily_report`

### Daily Field Report Submission
- `daily_report_documents_activity` for each activity listed
- `daily_report_created_rfi` if report spawns RFI
- `daily_report_created_punch` if report spawns punch item
- `field_issue_became_punch` for issues converted to punch

### RFI Creation
- `rfi_references_plan` if RFI references plan document
- `rfi_impacts_schedule` if RFI has schedule impact
- `rfi_impacts_cost` if RFI has cost impact

### Submittal Creation
- `submittal_linked_to_bid_package` if linked to bid package
- `submittal_required_for_activity` if associated with CPM activity

### Procurement
- `purchase_order_for_bid_package` + `bid_package_created_purchase_order` when PO linked to bid package
- `material_required_for_activity` when long-lead material links to CPM activity
- `material_delayed_activity` if delivery is late

### Weather
- `weather_alert_impacts_activity` when alert affects CPM activity
- `activity_delayed_by_weather` reciprocal

### Punch / Warranty
- `punch_documented_by_photo` when photos linked to punch
- `warranty_created_from_punch` when warranty created from punch item

---

## 9) Mission Control Project Intelligence Summary

```json
{
  "project_id": "101F",
  "project_brain": {
    "connected_entities": 482,
    "open_risk_chains": [
      {
        "severity": "RED",
        "summary": "Window delivery delay impacts critical path and budget forecast.",
        "chain": [
          { "entity_type": "long_lead_material", "label": "Marvin Windows" },
          { "link_type": "material_delayed_activity" },
          { "entity_type": "cpm_activity", "label": "Window Install" },
          { "link_type": "activity_impacts_cost_forecast" },
          { "entity_type": "cost_forecast", "label": "July Forecast" }
        ]
      }
    ],
    "unlinked_entities": {
      "photos": 12,
      "rfis": 2,
      "punch_items": 5
    },
    "top_connected_risks": [
      {
        "entity_type": "rfi",
        "entity_id": "uuid",
        "summary": "RFI-014 has linked cost and schedule impacts.",
        "links_count": 6
      }
    ]
  }
}
```

---

## 10) Graph Intelligence Queries

### Find Unlinked Photos
```sql
SELECT p.*
FROM project_photos p
LEFT JOIN project_entity_links l
    ON l.source_entity_type = 'project_photo'
    AND l.source_entity_id = p.id
WHERE p.project_id = :project_id
AND l.id IS NULL;
```

### Find RFIs with Schedule or Cost Impact
```sql
SELECT r.*
FROM rfis r
JOIN project_entity_links l
    ON l.source_entity_type = 'rfi'
    AND l.source_entity_id = r.id
WHERE r.project_id = :project_id
AND l.link_type IN ('rfi_impacts_schedule', 'rfi_impacts_cost');
```

---

## 11) Recursive Graph Traversal — Phase 2

```sql
WITH RECURSIVE graph_walk AS (
    SELECT
        id, project_id,
        source_entity_type, source_entity_id,
        target_entity_type, target_entity_id,
        link_type,
        1 AS depth
    FROM project_entity_links
    WHERE source_entity_type = :entity_type
      AND source_entity_id = :entity_id

    UNION ALL

    SELECT
        l.id, l.project_id,
        l.source_entity_type, l.source_entity_id,
        l.target_entity_type, l.target_entity_id,
        l.link_type,
        gw.depth + 1
    FROM project_entity_links l
    JOIN graph_walk gw
        ON l.source_entity_type = gw.target_entity_type
        AND l.source_entity_id = gw.target_entity_id
    WHERE gw.depth < 3
)
SELECT *
FROM graph_walk;
```

**Do not implement recursive traversal until direct links are stable.**

---

## 12) Integration With Existing Tables

No existing table needs to be redesigned.

Add graph link creation hooks to existing create/update flows:
- `/photos/upload`
- `/rfis`
- `/field-reports`
- `/procurement/long-lead`
- `/weather/check-conditions`
- `/punch`
- `/warranty`
- `/submittals`
- `/finance/budget-line`

Each hook creates links only when entity IDs are explicit. Do not infer uncertain links without marking them as AI-suggested.

---

## 13) AI-Suggested Links — Future Extension

```sql
ALTER TABLE project_entity_links
    ADD COLUMN IF NOT EXISTS confidence NUMERIC(5,2),
    ADD COLUMN IF NOT EXISTS created_by TEXT NOT NULL DEFAULT 'system',
    ADD COLUMN IF NOT EXISTS review_status TEXT NOT NULL DEFAULT 'approved';
```

Future statuses: `suggested`, `approved`, `rejected`

---

## 14) Tests Required

Claude Code should add tests for:
1. Create entity link
2. Reject duplicate link (409)
3. Reject self-link (constraint violation)
4. Get links where entity is source
5. Get links where entity is target (bidirectional)
6. Photo upload creates photo-to-entity link
7. RFI with linked plan creates graph link
8. Long-lead material linked to CPM creates graph link
9. Weather alert linked to CPM creates graph link
10. Mission Control summary counts linked entities
11. Unlinked photos query works
12. Graph service handles entity with no links

---

## 15) Definition of Done

Project Brain 2.0 Phase 1 is complete when:
- [ ] `project_entity_links` table exists
- [ ] Link vocabulary is documented
- [ ] `/brain/links` endpoint creates links
- [ ] `/brain/entity/{entity_type}/{entity_id}/links` returns connected entities
- [ ] Existing workflows create graph links for explicit relationships
- [ ] Mission Control shows connected intelligence summary
- [ ] Unlinked entity counts are visible
- [ ] Tests pass

---

## GBT Chief Architect Assessment

> "This is the strongest architectural move for Sprint 6 because it turns HCI AI OS from a set of construction modules into a connected construction intelligence system."

**Sprint 6 Priority Order (from Cycle 20 Retrospective):**
1. Project Brain 2.0 (Knowledge Graph) — THIS CYCLE
2. Vendor Intelligence Engine
3. Client Portal
4. Mobile Field Experience
5. Predictive Intelligence
6. Executive Analytics

---

*Spec committed by Browser Claude — Operations Intelligence*
*GBT Cycle 21 complete — Sprint 6 Priority 1 spec delivered*
