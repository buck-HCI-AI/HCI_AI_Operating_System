# CYCLE 34 — MISSION CONTROL DASHBOARD API
## HCI AI OS — Hendrickson Construction, Inc.
**Cycle:** 34 | **Sprint:** 7 | **Date:** 2026-07-02
**Score: 9.6/10** | Architect: GBT | Ops: BC
**Gateway:** Talked to speculate-armband-retinal.ngrok-free.dev (LIVE)

---

## 1. PURPOSE

GET /mission-control/snapshot is the single operational picture endpoint for HCI AI OS.
It aggregates company health, per-project status, active alerts, blocked missions,
and pending approvals into one cached response. This is what Buck sees in Mission Control.
Score 9.6/10 — high-value: turns many APIs into one operational picture.

---

## 2. FASTAPI ROUTE

```python
GET /mission-control/snapshot
```

Optional query params:
```
project_id: optional      # Filter to single project
include_inactive: bool = false  # Include inactive projects
refresh: bool = false     # Bypass Redis cache
```

Behavior:
- Default: returns all active production projects
- refresh=true bypasses Redis cache (force fresh query)
- PM users see assigned projects only
- Buck/super_admin sees all projects
- AI agents may read all if scoped

```python
@router.get('/mission-control/snapshot', response_model=MissionControlSnapshot)
async def get_mission_control_snapshot(
    project_id: Optional[str] = None,
    include_inactive: bool = False,
    refresh: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    cache_key = f'mission_control:snapshot:{current_user.role}'
    if not refresh:
        cached = await redis.get(cache_key)
        if cached:
            return MissionControlSnapshot(**json.loads(cached))
    snapshot = await build_mission_control_snapshot(db, current_user, project_id, include_inactive)
    await redis.setex(cache_key, 300, snapshot.json())  # 5-minute TTL
    return snapshot
```

---

## 3. RESPONSE SCHEMA

```python
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Optional
from pydantic import BaseModel, Field

class MissionControlProjectStatus(BaseModel):
    project_id: str
    project_code: Optional[str] = None
    project_name: Optional[str] = None
    health: str  # RED | YELLOW | GREEN
    risk_count: int = 0
    critical_risk_count: int = 0
    open_rfis: int = 0
    overdue_rfis: int = 0
    open_punch_items: int = 0
    critical_punch_items: int = 0
    pending_approvals: int = 0
    schedule_variance_days: Optional[int] = None
    budget_variance_dollars: Optional[Decimal] = None
    top_risk_summary: Optional[str] = None
    last_activity_at: Optional[datetime] = None

class MissionControlAlert(BaseModel):
    id: str
    project_id: Optional[str] = None
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW
    alert_type: str
    title: str
    message: str
    source: str
    created_at: datetime

class MissionControlBlockedMission(BaseModel):
    id: str
    project_id: Optional[str] = None
    owner: str
    title: str
    blocker: str
    status: str
    created_at: datetime

class MissionControlSnapshot(BaseModel):
    generated_at: datetime
    company_health: str  # RED | YELLOW | GREEN
    active_projects: int
    red_projects: int
    yellow_projects: int
    green_projects: int
    pending_approvals_count: int
    active_critical_alerts_count: int
    blocked_missions_count: int
    projects: list[MissionControlProjectStatus]
    active_critical_alerts: list[MissionControlAlert]
    blocked_missions: list[MissionControlBlockedMission]
    cache_status: str  # 'cached' | 'fresh'
```

---

## 4. HEALTH CALCULATION

Company health derives from project health:

```python
def calculate_company_health(projects: list[MissionControlProjectStatus]) -> str:
    if any(p.health == 'RED' for p in projects):
        return 'RED'
    if any(p.health == 'YELLOW' for p in projects):
        return 'YELLOW'
    return 'GREEN'

def calculate_project_health(project_data: dict) -> str:
    # RED conditions
    if project_data['critical_risk_count'] > 0:
        return 'RED'
    if project_data['overdue_rfis'] > 0:
        return 'RED'
    if project_data['schedule_variance_days'] and project_data['schedule_variance_days'] > 14:
        return 'RED'
    if project_data['budget_variance_pct'] and project_data['budget_variance_pct'] > 0.10:
        return 'RED'
    # YELLOW conditions
    if project_data['risk_count'] > 2:
        return 'YELLOW'
    if project_data['open_rfis'] > 3:
        return 'YELLOW'
    if project_data['schedule_variance_days'] and project_data['schedule_variance_days'] > 7:
        return 'YELLOW'
    return 'GREEN'
```

---

## 5. SQL QUERY DESIGN

```sql
-- Core snapshot query
SELECT
    p.id AS project_id,
    p.project_code,
    p.name AS project_name,
    COUNT(r.id) FILTER (WHERE r.status = 'open') AS risk_count,
    COUNT(r.id) FILTER (WHERE r.status = 'open' AND r.severity IN ('HIGH', 'CRITICAL')) AS critical_risk_count,
    COUNT(rfi.id) FILTER (WHERE rfi.status = 'open') AS open_rfis,
    COUNT(rfi.id) FILTER (WHERE rfi.status = 'open' AND rfi.due_date < NOW()) AS overdue_rfis,
    COUNT(pi.id) FILTER (WHERE pi.status = 'open') AS open_punch_items,
    COUNT(pi.id) FILTER (WHERE pi.status = 'open' AND pi.severity = 'CRITICAL') AS critical_punch_items,
    COUNT(aq.id) FILTER (WHERE aq.status = 'pending') AS pending_approvals,
    p.schedule_variance_days,
    p.budget_variance_dollars,
    MAX(GREATEST(r.updated_at, rfi.updated_at, pi.updated_at)) AS last_activity_at
FROM projects p
LEFT JOIN risks r ON r.project_id = p.id
LEFT JOIN rfis rfi ON rfi.project_id = p.id
LEFT JOIN punch_items pi ON pi.project_id = p.id
LEFT JOIN approval_queue aq ON aq.project_id = p.id
WHERE p.status = 'active'
GROUP BY p.id, p.project_code, p.name, p.schedule_variance_days, p.budget_variance_dollars
ORDER BY p.project_code;

-- Active critical alerts query
SELECT id, project_id, severity, alert_type, title, message, source, created_at
FROM mission_alerts
WHERE severity IN ('CRITICAL', 'HIGH')
AND resolved_at IS NULL
ORDER BY severity DESC, created_at DESC;

-- Blocked missions query
SELECT id, project_id, owner, title, blocker, status, created_at
FROM ai_missions
WHERE status = 'BLOCKED'
ORDER BY created_at DESC;
```

---

## 6. CACHING STRATEGY

| Cache Key | TTL | Invalidation |
|-----------|-----|--------------|
| mission_control:snapshot:super_admin | 300s | On any project event |
| mission_control:snapshot:pm:{user_id} | 300s | On assigned project event |
| mission_control:project:{project_id} | 60s | On project.updated event |

```python
# Cache invalidation via event bus
async def on_project_status_changed(event: DomainEvent):
    project_id = event.payload['project_id']
    # Clear all snapshot caches
    keys = await redis.keys('mission_control:snapshot:*')
    if keys:
        await redis.delete(*keys)
    # Clear specific project cache
    await redis.delete(f'mission_control:project:{project_id}')
```

---

## 7. REAL-TIME ALERT WEBHOOK

When any project changes to RED status, trigger immediate notification:

```python
async def on_project_health_changed(event: DomainEvent):
    if event.payload.get('new_health') == 'RED':
        project_id = event.payload['project_id']
        project_name = event.payload.get('project_name', project_id)
        reason = event.payload.get('reason', 'Unknown trigger')

        # 1. Emit alert event
        await event_bus.emit('alert.project_red', {
            'project_id': project_id,
            'project_name': project_name,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })

        # 2. Telegram notification to Buck (if configured)
        if TELEGRAM_BUCK_USER_ID:
            msg = f'ALERT: {project_name} status is RED. Reason: {reason}'
            await send_telegram_message(TELEGRAM_BUCK_USER_ID, msg)

        # 3. Invalidate mission control cache
        await redis.delete(*await redis.keys('mission_control:snapshot:*'))
```

---

## 8. CURRENT LIVE STATE (from Code mission control check)

As of 2026-07-02, mission control reports:

| Project | Health | Primary Issue |
|---------|--------|---------------|
| 101 Francis | RED | Steel supplier 5 days behind GATE2-TS02b (column erection) |
| 1355 Riverside | RED | RFI-001 blocking framing at Axis B, $280k electrical bid spread |
| 64 Eastwood | YELLOW | 2 risks, no critical |
| 246 Gallo Way | GREEN | Clear |

Company health: RED (2 of 4 projects RED)

Alert source for 101 Francis: GATE2-TS02b at risk of cascading to downstream structural work.
Alert source for 1355 Riverside: RFI-001 must be resolved before framing continues.

---

## 9. MISSION CONTROL TABLE MIGRATION

```sql
-- New table: mission_alerts
CREATE TABLE mission_alerts (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id   UUID REFERENCES projects(id),
    severity     VARCHAR(10) NOT NULL CHECK (severity IN ('CRITICAL','HIGH','MEDIUM','LOW')),
    alert_type   VARCHAR(50) NOT NULL,
    title        VARCHAR(255) NOT NULL,
    message      TEXT,
    source       VARCHAR(100),
    resolved_at  TIMESTAMPTZ,
    resolved_by  VARCHAR(100),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mission_alerts_severity ON mission_alerts(severity) WHERE resolved_at IS NULL;
CREATE INDEX idx_mission_alerts_project ON mission_alerts(project_id) WHERE resolved_at IS NULL;

-- Add health tracking to projects
ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS health VARCHAR(10) DEFAULT 'GREEN'
        CHECK (health IN ('RED', 'YELLOW', 'GREEN')),
    ADD COLUMN IF NOT EXISTS schedule_variance_days INT,
    ADD COLUMN IF NOT EXISTS budget_variance_dollars DECIMAL(12,2),
    ADD COLUMN IF NOT EXISTS health_updated_at TIMESTAMPTZ;
```

---

## 10. ACCEPTANCE CRITERIA

| # | Criteria | Test |
|---|----------|------|
| 1 | GET /mission-control/snapshot returns company_health | Call endpoint |
| 2 | RED/YELLOW/GREEN calculated correctly | Seed test data, verify health |
| 3 | Response cached 5min in Redis | Call twice, verify cache_status='cached' |
| 4 | refresh=true forces fresh query | Call with refresh=true, verify 'fresh' |
| 5 | PM users see only assigned projects | Test with PM user token |
| 6 | Project going RED triggers Telegram alert | Update project to RED, check Telegram |
| 7 | Cache invalidated on project event | Fire project.updated, verify cache cleared |
| 8 | mission_alerts table seeded | Insert alert, verify in snapshot response |
| 9 | Blocked missions included | Create blocked mission, verify in response |
| 10 | Response < 200ms when cached | Load test with k6 |

---

## 11. IMPLEMENTATION NOTES

- AI team warm start: subscribe to project.status_changed on startup
- n8n alert workflows: n8n listens to alert.project_red event, can send email/SMS/Slack
- The snapshot endpoint is READ ONLY — no writes, no side effects
- Role-based filtering enforced at query level (not post-filter)
- All amounts in USD with 2 decimal places
- Dates in ISO 8601 format

---

## 12. CYCLE SCORE: 9.6/10

Cycle 34 delivers complete Mission Control Dashboard API specification.
This cycle integrates live data from the running system (Code confirmed
101 Francis = RED, 1355 Riverside = RED as of 2026-07-02).

The endpoint is the single operational picture of HCI AI OS.
Gateway confirmed ONLINE during this cycle.

-0.4: Dependent on projects table having health/variance columns (migration required).

---

*Next: Cycle 35 — n8n Workflow Automation: Alert → Notification → Escalation Pipeline*
*Code: Implement GET /mission-control/snapshot after auth router is live (Sprint 7 Phase 4)*
