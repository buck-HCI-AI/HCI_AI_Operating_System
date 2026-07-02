# CYCLE23 — Sprint 6 Priority 3: Client Portal Architecture
**Cycle:** 23
**Sprint:** 6
**Priority:** 3
**Date:** 2026-07-02
**Author:** GBT (HCI Chief Architect)
**Status:** SPEC COMPLETE — Ready for Code Implementation

---

## Overview

HCI builds luxury custom homes. Clients currently have zero visibility into their project.

The Client Portal is not a CRM. It is a curated client experience.

The portal should answer one question:

> "What is happening with my home, what decisions do I need to make, and what is coming next?"

---

## Design Principles

- The portal is curated. It should not expose internal operations.
- Every data point the client sees has been intentionally permitted.
- Client auth is project-scoped: a client can only see their own project.
- Internal costs, vendors, communications, and risks are never exposed.
- Approved photos are curated by HCI before becoming client-visible.
- The experience should feel polished, clear, and confidence-building.

---

## 1) PostgreSQL DDL — client_users

```sql
CREATE TABLE IF NOT EXISTS client_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id TEXT NOT NULL,

    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,

    role TEXT NOT NULL DEFAULT 'owner',
    -- allowed: owner | spouse | representative

    auth_token TEXT NOT NULL,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_client_users_role CHECK (
        role IN ('owner', 'spouse', 'representative')
    ),

    CONSTRAINT uq_client_users_project_email
        UNIQUE (project_id, email)
);

CREATE INDEX IF NOT EXISTS idx_client_users_project_id
    ON client_users(project_id);

CREATE INDEX IF NOT EXISTS idx_client_users_auth_token
    ON client_users(auth_token);

CREATE INDEX IF NOT EXISTS idx_client_users_email
    ON client_users(email);
```

---

## 2) What Clients Can See

The client portal exposes curated project information only.

### Client Dashboard

Clients can see:
```
Project milestone timeline
Approved progress photos (reviewed = true AND client_visible = true)
Current selections status
Pending decisions needing client action
Key dates (estimated completion, next milestone)
Current phase label
Health summary (friendly language, not RED/YELLOW/GREEN codes)
```

### Photos

Only photos where `reviewed = true` are client-visible.

Client-visible photos should be intentionally approved by HCI staff.

Recommended: add `client_visible BOOLEAN DEFAULT FALSE` to `project_photos`.

Phase 1 default: only reviewed photos are visible.

### Selections

- Items the client previously approved or needs to approve
- Due dates for pending items
- Status labels in plain English

### Decisions

- Open decisions requiring client input
- Options with descriptions
- Deadline clearly shown
- Expired decisions surfaced as action items

---

## 3) What Clients Cannot See

Clients must not see:

```
internal costs or budget
subcontractor details
internal risk notes
unapproved photos
draft RFIs
draft submittals
punch items (before formal presentation)
internal schedule recovery notes
approval queue internal workflow
email governance incidents
internal AI team communications
change order details (until shared by HCI)
vendor pricing or bid data
```

The portal is curated. It should not expose internal operations.

---

## 4) PostgreSQL DDL — client_selections

```sql
CREATE TABLE IF NOT EXISTS client_selections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id TEXT NOT NULL,

    category TEXT NOT NULL,
    -- allowed: flooring | cabinets | plumbing | electrical | exterior

    item_description TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'pending',
    -- allowed: pending | approved | rejected | substituted

    deadline DATE,

    notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_client_selections_category CHECK (
        category IN (
            'flooring',
            'cabinets',
            'plumbing',
            'electrical',
            'exterior'
        )
    ),

    CONSTRAINT chk_client_selections_status CHECK (
        status IN (
            'pending',
            'approved',
            'rejected',
            'substituted'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_client_selections_project_id
    ON client_selections(project_id);

CREATE INDEX IF NOT EXISTS idx_client_selections_status
    ON client_selections(status);

CREATE INDEX IF NOT EXISTS idx_client_selections_deadline
    ON client_selections(deadline);
```

---

## 5) PostgreSQL DDL — client_decisions

```sql
CREATE TABLE IF NOT EXISTS client_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    project_id TEXT NOT NULL,

    title TEXT NOT NULL,
    description TEXT NOT NULL,

    options JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Example:
    -- [
    --   {"id": "A", "label": "White Oak", "description": "Wide plank 5 inch"},
    --   {"id": "B", "label": "Walnut", "description": "Select grade 4 inch"}
    -- ]

    deadline DATE,

    status TEXT NOT NULL DEFAULT 'pending',
    -- allowed: pending | decided | expired

    decided_option TEXT,

    decided_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_client_decisions_status CHECK (
        status IN (
            'pending',
            'decided',
            'expired'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_client_decisions_project_id
    ON client_decisions(project_id);

CREATE INDEX IF NOT EXISTS idx_client_decisions_status
    ON client_decisions(status);

CREATE INDEX IF NOT EXISTS idx_client_decisions_deadline
    ON client_decisions(deadline);
```

---

## 6) Client Auth Model

### MVP Auth

Use bearer token from `client_users.auth_token`:

```http
Authorization: Bearer <client_auth_token>
```

Gateway verifies:
```
client_users.auth_token = provided token
client_users.active = true
```

Returns: `ClientUser` object including project_id scope.

### Dependency

```python
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.client_users import ClientUser

def get_current_client_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> ClientUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.split(" ", 1)[1]

    client = (
        db.query(ClientUser)
        .filter(ClientUser.auth_token == token, ClientUser.active == True)
        .first()
    )

    if not client:
        raise HTTPException(status_code=401, detail="Invalid or inactive token")

    return client

def assert_client_project_access(client: ClientUser, project_id: str) -> None:
    if client.project_id != project_id:
        raise HTTPException(status_code=403, detail="Access denied")
```

### Future: Phase 2 Auth Options
- Magic link email (no password)
- SMS verification
- OAuth (Google)

Phase 1: bearer token is sufficient for controlled client access.

---

## 7) FastAPI Endpoints

Router: `app/api/routers/client_portal.py`

```python
router = APIRouter(prefix="/client", tags=["Client Portal"])
```

### GET /client/project/{id}/dashboard

```python
@router.get("/project/{project_id}/dashboard")
def get_client_dashboard(
    project_id: str,
    db: Session = Depends(get_db),
    client: ClientUser = Depends(get_current_client_user),
):
    assert_client_project_access(client, project_id)

    project = get_client_safe_project_summary(project_id, db)
    milestones = get_client_visible_milestones(project_id, db)
    recent_photos = get_client_visible_photos(project_id, db, limit=6)
    pending_selections = (
        db.query(ClientSelection)
        .filter(
            ClientSelection.project_id == project_id,
            ClientSelection.status == "pending",
        )
        .order_by(ClientSelection.deadline.asc().nullslast())
        .all()
    )
    pending_decisions = (
        db.query(ClientDecision)
        .filter(
            ClientDecision.project_id == project_id,
            ClientDecision.status == "pending",
        )
        .order_by(ClientDecision.deadline.asc().nullslast())
        .all()
    )

    return {
        "project": project,
        "milestones": milestones,
        "recent_photos": recent_photos,
        "pending_selections": pending_selections,
        "pending_decisions": pending_decisions,
    }
```

### GET /client/project/{id}/photos

```python
@router.get("/project/{project_id}/photos")
def get_client_photos(
    project_id: str,
    db: Session = Depends(get_db),
    client: ClientUser = Depends(get_current_client_user),
):
    assert_client_project_access(client, project_id)
    return get_client_visible_photos(project_id, db)
```

### GET /client/selections/{id}

```python
@router.get("/selections/{selection_id}")
def get_client_selection(
    selection_id: UUID,
    db: Session = Depends(get_db),
    client: ClientUser = Depends(get_current_client_user),
):
    selection = db.query(ClientSelection).filter(ClientSelection.id == selection_id).first()
    if not selection:
        raise HTTPException(status_code=404, detail="Selection not found")
    assert_client_project_access(client, selection.project_id)
    return selection
```

### POST /client/decisions/{id}/respond

```python
@router.post("/decisions/{decision_id}/respond")
def respond_to_client_decision(
    decision_id: UUID,
    payload: ClientDecisionRespond,
    db: Session = Depends(get_db),
    client: ClientUser = Depends(get_current_client_user),
):
    decision = db.query(ClientDecision).filter(ClientDecision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    assert_client_project_access(client, decision.project_id)

    if decision.status != "pending":
        raise HTTPException(status_code=400, detail="Decision is not pending")

    valid_option_ids = {str(option.get("id")) for option in decision.options if option.get("id") is not None}
    if payload.selected_option not in valid_option_ids:
        raise HTTPException(status_code=400, detail="Invalid option selected")

    decision.decided_option = payload.selected_option
    decision.decided_at = datetime.now(timezone.utc)
    decision.status = "decided"

    # Future: create Project Brain link + notify PM/Mission Control

    db.commit()
    db.refresh(decision)
    return decision
```

---

## 8) SQLAlchemy Models

```python
class ClientUser(Base):
    __tablename__ = "client_users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(Text, nullable=False, index=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, index=True)
    phone = Column(Text, nullable=True)
    role = Column(Text, nullable=False, default="owner")
    auth_token = Column(Text, nullable=False, index=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        UniqueConstraint("project_id", "email", name="uq_client_users_project_email"),
        CheckConstraint("role IN ('owner','spouse','representative')", name="chk_client_users_role"),
    )

class ClientSelection(Base):
    __tablename__ = "client_selections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(Text, nullable=False, index=True)
    category = Column(Text, nullable=False)
    item_description = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="pending")
    deadline = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        CheckConstraint("category IN ('flooring','cabinets','plumbing','electrical','exterior')", name="chk_client_selections_category"),
        CheckConstraint("status IN ('pending','approved','rejected','substituted')", name="chk_client_selections_status"),
    )

class ClientDecision(Base):
    __tablename__ = "client_decisions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(Text, nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    options = Column(JSONB, nullable=False, default=list)
    deadline = Column(Date, nullable=True)
    status = Column(Text, nullable=False, default="pending")
    decided_option = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    __table_args__ = (
        CheckConstraint("status IN ('pending','decided','expired')", name="chk_client_decisions_status"),
    )
```

---

## 9) Data Isolation Rules

| Data Type | Visible to Client |
|-----------|-------------------|
| Milestones | Yes — if assigned to project and client-facing |
| Approved Photos | Yes — reviewed = true |
| Selections | Yes — if assigned to project |
| Decisions | Yes — if pending/decided for client action |
| Costs | Never in Phase 1 |
| Vendors | Never in Phase 1 |
| Internal RFIs/Submittals | Never |
| Punch Items | Never (before formal presentation) |

---

## 10) Service Functions

File: `app/services/client_portal_service.py`

```python
def get_client_safe_project_summary(project_id: str, db: Session) -> dict:
    # Returns: project_name, current_phase, estimated_completion
    # Does NOT return: internal costs, risks, AI notes
    ...

def get_client_visible_milestones(project_id: str, db: Session) -> list:
    # Returns milestones marked client_facing = true
    ...

def get_client_visible_photos(project_id: str, db: Session, limit: int = 50) -> list:
    # Returns photos where reviewed = true
    # Ordered by taken_at DESC
    ...
```

---

## 11) Business Rules

### Selection Status Rules

- `pending` — HCI has entered it, awaiting client acknowledgment or selection
- `approved` — client has confirmed
- `rejected` — client has declined, alternative needed
- `substituted` — HCI has provided an alternative after rejection

### Decision Deadline Rules

If `deadline < today` and status is `pending`:
- Mark as `expired`
- Notify PM
- Surface in Mission Control
- Do not auto-select an option

n8n workflow: WF-CLIENT-001 Client Decision Deadline Monitor (daily at 07:00)

---

## 12) Mission Control Internal Output

Mission Control should surface pending client actions for PM attention:

```json
{
  "project_id": "101F",
  "client_portal": {
    "pending_decisions": 2,
    "pending_selections": 4,
    "expired_decisions": 1,
    "selections_due_this_week": 2,
    "last_client_login": "2026-06-28T14:32:00Z"
  }
}
```

---

## 13) Client Dashboard Output Example

```json
{
  "project_id": "101F",
  "project_name": "101 Francis",
  "current_phase": "Interior Construction",
  "health_summary": "Your project is active. The next major milestone is Framing Complete on August 15.",
  "estimated_completion": "2026-11-15",
  "next_milestone": {
    "label": "Framing Complete",
    "planned_date": "2026-08-15",
    "status": "upcoming"
  },
  "milestones": [
    { "label": "Demolition Complete", "planned_date": "2026-07-01", "status": "complete" },
    { "label": "Framing Complete", "planned_date": "2026-08-15", "status": "upcoming" }
  ],
  "recent_photos": [],
  "pending_selections": [],
  "pending_decisions": [],
  "key_dates": [
    { "label": "Estimated Completion", "date": "2026-11-15" },
    { "label": "Next Milestone", "date": "2026-08-15" }
  ]
}
```

---

## 14) Tests Required

Claude Code should implement tests for:
1. Create client user
2. Reject duplicate project/email combination
3. Authenticate with valid bearer token
4. Reject expired or invalid token
5. Assert client cannot access other project
6. Client dashboard returns only approved photos
7. Client dashboard does not return costs or vendors
8. Create selection
9. Update selection status
10. Create decision with JSONB options
11. Client responds with valid option
12. Reject invalid option ID
13. Expired decision auto-marked by WF-CLIENT-001
14. Mission Control surfaces pending client actions

---

## 15) Definition of Done

Client Portal Phase 1 is complete when:
- [ ] `client_users`, `client_selections`, and `client_decisions` tables exist
- [ ] Client auth is enforced
- [ ] Client dashboard returns only curated project information
- [ ] Approved/client-visible photos are available
- [ ] Client selections are visible
- [ ] Client decisions can be responded to
- [ ] Internal costs, vendors, risks, and communications are not exposed
- [ ] Mission Control can see pending client actions
- [ ] Tests pass

---

## GBT Chief Architect Assessment

> "The client portal should make owners feel informed and cared for without exposing internal operations. That is the right luxury-home experience: clear, curated, polished, and controlled."

---

*Spec committed by Browser Claude — Operations Intelligence*
*GBT Cycle 23 complete — Sprint 6 Priority 3 spec delivered*
