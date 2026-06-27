# HCI AI Construction Operating System
# Architecture Handbook
**Constitutional Reference Document**
*Chief Architects: ChatGPT + Buck Adams (Hendrickson Construction)*
*Implementation Support: Claude Code*
*Last Synchronized: 2026-06-27*

---

> **Handbook Authority**
> This handbook is authored and owned by the Chief Architect (ChatGPT) and Buck Adams.
> Claude Code maintains synchronization between this document and the live implementation.
> All operational philosophy, design decisions, and vision content require Chief Architect approval.

---

## Table of Contents

| Volume | Title | Status |
|--------|-------|--------|
| [Volume I](Volume_01_Executive_Vision.md) | Executive Vision | ⚠️ Awaiting Chief Architect |
| [Volume II](Volume_02_Construction_Intelligence_Model.md) | Construction Intelligence Model | 🟡 Stub + Implementation refs |
| [Volume III](Volume_03_Project_Brain.md) | Project Brain | 🟡 Stub + Implementation refs |
| [Volume IV](Volume_04_Superintendent_Intelligence.md) | Superintendent Intelligence | 🟡 Stub + Implementation refs |
| [Volume V](Volume_05_Project_Manager_Intelligence.md) | Project Manager Intelligence | 🟡 Stub + Implementation refs |
| [Volume VI](Volume_06_Executive_Mission_Control.md) | Executive Mission Control | 🟡 Stub + Implementation refs |
| [Volume VII](Volume_07_Construction_Intelligence_Engine.md) | Construction Intelligence Engine | 🟡 Stub + Implementation refs |
| [Volume VIII](Volume_08_Automation_Architecture.md) | Automation Architecture | 🟡 Stub + Implementation refs |
| [Volume IX](Volume_09_Governance.md) | Governance | 🟡 Stub + Implementation refs |
| [Volume X](Volume_10_Future_Vision.md) | Future Vision | ⚠️ Awaiting Chief Architect |

---

## Platform at a Glance

**HCI AI Operating System** transforms raw construction data into role-based intelligence for
Hendrickson Construction's Superintendents, Project Managers, and Leadership.

### Current Implementation State (2026-06-27)

| Layer | Component | Status | Key Endpoint |
|-------|-----------|--------|-------------|
| API | FastAPI v1 | ✅ Live | `http://localhost:8000` |
| Project Brain | Intelligence + Health + Risks | ✅ Live | `/api/v1/services/project-brain/{id}/intelligence` |
| Predictive Engine | 7 risk predictions + confidence | ✅ Live | `/api/v1/services/predictive-engine/{id}/predictions` |
| Cross-Project | Portfolio health + alerts | ✅ Live | `/api/v1/services/cross-project/health-matrix` |
| Operations | SS Console + PM Console + Leadership | ✅ Live | `/api/v1/superintendent/{id}/today` |
| System Auditor | 8-domain nightly self-eval | ✅ Live | `/api/v1/services/system-auditor/run` |
| Mission Control | Executive portfolio view | ✅ Live | `/api/v1/executive/mission-control` |
| n8n Automation | 32 workflows | ✅ Live | `http://localhost:5678` |
| Database | PostgreSQL — 73 tables | ✅ Live | `hci_os` |

### Projects Under Management

| ID | Code | Project Name | Status |
|----|------|-------------|--------|
| 1 | 64EW | 64 Eastwood | Active |
| 2 | 101F | 101 Francis | Active |
| 3 | 1355R | 1355 Riverside | Active |
| 4 | 83SB | 83 Sagebrusch | Active |

---

## Architecture Decision Records

See [ADRs/](ADRs/) for all recorded architectural decisions.

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](ADRs/ADR-001-fastapi-service-pattern.md) | FastAPI service registration pattern | Accepted |
| [ADR-002](ADRs/ADR-002-project-brain-per-project.md) | Per-project intelligence model | Accepted |
| [ADR-003](ADRs/ADR-003-predictive-engine-confidence.md) | Evidence-based predictions with confidence | Accepted |
| [ADR-004](ADRs/ADR-004-health-scoring-algorithm.md) | RED/YELLOW/GREEN health scoring | Accepted |
| [ADR-005](ADRs/ADR-005-system-auditor-nightly.md) | Autonomous nightly system auditor | Accepted |

---

## Conflict Log

*Claude Code flags any conflict between implementation and architecture here for Chief Architect review.*

| Date | Conflict | Status |
|------|----------|--------|
| — | No conflicts detected | — |

---

## Synchronization Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-27 | Initial workspace created, all volumes stubbed, 5 ADRs generated | Claude Code |
| 2026-06-27 | Sprint 3+4 implementation cross-referenced | Claude Code |
| 2026-06-27 | Phase 2 Priority 3-4 (Predictive Engine, Mission Control) cross-referenced | Claude Code |
| 2026-06-27 | Phase 3 (System Auditor) cross-referenced | Claude Code |
