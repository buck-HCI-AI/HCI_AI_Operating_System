# Architecture Sync Engine
*HCI AI Operating System — Architecture Governance*
*Version: 1.0 | Date: 2026-06-27 | Author: Claude Code*

---

## Purpose

Whenever handbook content changes or implementation changes, the Sync Engine automatically:
- Updates documentation links
- Updates diagrams
- Updates implementation references
- Updates ADR cross-references
- Updates handbook index
- Updates CHANGELOG
- Identifies implementation conflicts
- Notifies Chief Architect of conflicts

---

## Sync Triggers

| Trigger | Source | Action |
|---------|--------|--------|
| New chapter in Drafts/ | n8n file watcher | Validate → Publish pipeline |
| Implementation commit | Post-commit hook or n8n | Review Engine → update affected handbook sections |
| Manual sync call | `POST /architecture-sync/sync` | Full re-sync of all refs |
| Nightly audit | System auditor post-hook | Update platform state table in Master Index |
| ADR created | Claude Code | Update ADR table in Master Index + relevant volume |

---

## Cross-Reference Map

The sync engine maintains a bidirectional map:

```
Handbook Section ←→ Implementation Files
         ←→ ADRs
         ←→ Database Tables
         ←→ n8n Workflows
         ←→ API Endpoints
```

### Current Cross-Reference Table

| Handbook Section | Code Files | DB Tables | Endpoints | ADRs |
|-----------------|-----------|-----------|-----------|------|
| Vol II — Intelligence Model | `base_service.py` | `project_risks_computed` | `/project-brain/*` | ADR-002, ADR-004 |
| Vol III — Project Brain | `services/project_brain/routes.py` | `project_brain_snapshots` | `/project-brain/{id}/*` | ADR-002 |
| Vol IV — Role Intelligence | `routers/superintendent.py`, `routers/pm.py` | `houzz_schedule_items`, `houzz_tasks` | `/superintendent/*`, `/pm/*` | ADR-004 |
| Vol V — Executive Intelligence | `routers/executive.py` | `approval_queue`, `predictions_computed` | `/executive/*`, `/predictive-engine/*` | ADR-003, ADR-005 |
| Vol VI — Intelligence Engine | `services/*/routes.py` | 20+ service tables | `/services/*` | ADR-001 |
| Vol VII — Automation | `workflows/n8n/*.json` | `connector_sync_state` | n/a | ADR-005 |
| Vol VIII — Governance | `tests/`, `migrations/` | `audit_trail` | `/system-auditor/*` | ADR-005 |

---

## Implementation Reference Auto-Update

When a sync runs, the engine scans for "Implementation Reference" sections in handbook chapters and verifies:

1. **Endpoint exists** — `GET /api/v1/services/{service}/*` responds 200
2. **Table exists** — PostgreSQL schema check for referenced tables
3. **Column names match** — Compare handbook schema tables against actual DB columns
4. **Service file exists** — Referenced code paths exist on disk

Any discrepancy → create conflict entry in `CHIEF_ARCHITECT_REVIEW_QUEUE.md`

---

## Diagram Generation

The sync engine generates diagrams from implemented architecture (not from specification):

| Diagram | Source | Output |
|---------|--------|--------|
| API Endpoint Map | `GET /api/v1/services` | `Diagrams/api_endpoint_map.md` |
| Service Dependency Graph | `main.py` service load order | `Diagrams/service_dependencies.md` |
| Data Flow Diagram | Connector → DB → Service chain | `Diagrams/data_flow.md` |
| Health Score Map | System auditor domains | `Diagrams/health_score_map.md` |
| n8n Workflow Registry | n8n API + disk files | `Diagrams/workflow_registry.md` |

Diagrams are ASCII-based markdown (no external tools required).

---

## Conflict Resolution Protocol

```
Conflict Detected
    ↓
1. Create ADR entry in Handbook/ADR/
2. Add to CHIEF_ARCHITECT_REVIEW_QUEUE.md (Section D — Inconsistencies)
3. Add to CHANGELOG.md (conflict entry)
4. Send ntfy: "Architecture conflict detected — Chief Architect review needed"
5. Pause: DO NOT automatically resolve
6. Chief Architect reviews and provides resolution
7. Claude Code implements resolution
8. ADR updated to "Accepted" or "Superseded"
9. CHANGELOG updated with resolution
```

---

## ADR-006: Architecture Sync Service

**Decision:** Build the Architecture Sync Engine as a FastAPI service (`services/architecture_sync/`)
loaded via the standard `_load_svc()` pattern (ADR-001).

**Rationale:** Consistent with all other services; allows sync to be called from n8n, tested
with the standard test framework, and monitored by the System Auditor.

**Consequences:**
- Positive: Sync is API-accessible from anywhere (n8n, Codex, Buck's browser)
- Positive: Standard auditor monitoring applies
- Negative: Sync engine can't access its own service registration (bootstrapping handled in main.py)
