# Integration Sequence
**HCI AI Operating System — Build Sequence Reference**
**Version:** 2.0 | **Last Updated:** 2026-06-26

---

## Sequence Overview

```
Phase 1   Infrastructure (Postgres, Redis, MinIO, Qdrant, Docker)      ✅ COMPLETE
Phase 2   Integrations (HubSpot, Drive, Outlook, Graph API)            ✅ COMPLETE
Phase 3   API Layer (FastAPI, all core routers)                        ✅ COMPLETE
Phase 4   Intelligence Services (9 services)                           ✅ COMPLETE
Phase 5   Workflow Engine (18 workflows, n8n, launchd)                 ✅ COMPLETE
Phase 6   Reporting + Dashboard                                        ✅ COMPLETE
Phase 7   Production Hardening (auth, backup, monitor, launchd)        ✅ COMPLETE
Phase 8   QA + Validation Gates (5 gates, UAT, pilot)                  ✅ COMPLETE
Phase 9   BOOK_01 Operating Manual (19 volumes)                        ✅ COMPLETE
Phase 10  SOP Execution Layer — Phases A–H (27 SOPs)                  ✅ COMPLETE
Phase 11  Platform Integration Layer (5 shared capabilities)           ✅ COMPLETE
Phase 12  Gate 5 Pilot (101 Francis / 64 Eastwood / 1355 Riverside)   🔄 IN PROGRESS
```

---

## Phase 10: SOP Execution Layer

All 27 SOPs follow the 4-layer pattern: Templates → Agent → Service → Router

| Phase | SOPs | Description |
|---|---|---|
| A+B | all | Documentation: conversion inventory, status matrix, gate register |
| C | 11, 15 | Pilot build (Bid Package + Bid Leveling) |
| D | 11, 15 | Testing: 29 tests, 28 PASS, 1 CONDITIONAL |
| E | 10, 13, 14, 16 | Chain expansion |
| F | 04–09 | Preconstruction backfill |
| G | 12, 19 | Close loop (Sub CRM + Subcontract Agreement) |
| H | 17, 18, 20–30 | Field execution (Schedule → Safety → Inspection) |

**SOP chain:** 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 19 → 17 → 18 → 20 → 21 → 22 → 23 → [24 / 25 / 26 / 27 / 28 / 29 / 30]

---

## Phase 11: Platform Integration Layer

### Build Order (dependency-first)

```
Step 1: DB schema (05_Database/platform_schema.sql)
         └─ platform_users, platform_permissions,
            platform_events, platform_notifications, platform_audit_log

Step 2: Identity Service
         └─ services/platform/identity/identity_service.py
         └─ 12 roles seeded, 42+ permissions

Step 3: Event Bus
         └─ services/platform/event_bus/event_bus_service.py
         └─ BaseSOP._emit() wired in shared/base_sop.py

Step 4: Notification Center
         └─ services/platform/notifications/notification_service.py
         └─ 17 notification types, escalation thresholds

Step 5: Audit Trail
         └─ services/platform/audit/audit_service.py
         └─ Unifies sop_workflow_events + workflow_events + platform_audit_log

Step 6: Search Gateway
         └─ services/platform/search_gateway/search_gateway_service.py
         └─ Intent routing → Postgres + Qdrant; confidence + citations

Step 7: API Router
         └─ api/routers/platform.py (33 endpoints)
         └─ Registered in api/main.py

Step 8: Tests
         └─ tests/test_platform_integration.py (39 tests: 39 PASS)
```

### Integration Points (Platform → SOP Layer)

- `BaseSOP.transition_status()` → `EventBus.publish("sop.status_changed")`
- Event Bus → Notification Center (subscribe on approval_required events)
- Notification Center → Audit Trail (log notification creates)
- Search Gateway → Qdrant (`services.vector.search()`)
- Search Gateway → `decision_records` table (`find_decisions()`)

---

## Phase 12: Gate 5 Pilot

**Scope:** 101 Francis, 64 Eastwood, 1355 Riverside  
**Duration:** 2026-06-25 → 2026-07-01 (5 days)  
**Go-live authorization:** Pending Buck sign-off after pilot review

---

## File Map

| Layer | Key Files |
|---|---|
| DB schema | `05_Database/platform_schema.sql` |
| Identity | `services/platform/identity/identity_service.py` |
| Event Bus | `services/platform/event_bus/event_bus_service.py` |
| Notifications | `services/platform/notifications/notification_service.py` |
| Audit | `services/platform/audit/audit_service.py` |
| Search | `services/platform/search_gateway/search_gateway_service.py` |
| API Router | `api/routers/platform.py` |
| Tests | `tests/test_platform_integration.py` |
| SOP auto-emit | `services/sop_execution/shared/base_sop.py` (see `_emit()`) |
