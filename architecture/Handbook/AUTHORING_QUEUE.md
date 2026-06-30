# Architecture Handbook — Authoring Queue
*Maintained by: Claude Code | Authored by: ChatGPT + Buck Adams*
*Last Updated: 2026-06-27*

Each chapter is a work item. Claude Code updates status as implementations change.
Chief Architect resolves authoring items.

---

## Queue Key

| Status | Meaning |
|--------|---------|
| 🔴 NOT STARTED | Chief Architect has not authored this section |
| 🟡 IN PROGRESS | Chief Architect is drafting |
| 🟠 DRAFT READY | Draft in Drafts/ awaiting validation + publish |
| 🟢 PUBLISHED | Validated, versioned, in Published/ |
| ⚙️ IMPL ONLY | Implementation reference only (Claude Code) — no CA authorship needed |
| ⚠️ CONFLICT | Implementation diverged from architecture — ADR needed |

---

## Volume I — Executive Vision

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 1.A | HCI AI Organization | 🟢 PUBLISHED | None | One thing I think we almost missed.docx | — | — | None |
| 1.B | Design Principles | 🟢 PUBLISHED | 1.A | One thing I think we almost missed.docx | — | — | None |
| 1.C | Maturity Model | 🟢 PUBLISHED | 1.A | One thing I think we almost missed.docx | ADR-004 | — | None |
| 1.D | North Star | 🟢 PUBLISHED | 1.A | One thing I think we almost missed.docx | — | — | None |
| 1.1 | Platform Purpose | 🔴 NOT STARTED | None | — | — | — | Chief Architect |
| 1.2 | Operating Philosophy | 🔴 NOT STARTED | 1.1 | — | — | — | Chief Architect |
| 1.3 | Intelligence Model Philosophy | 🔴 NOT STARTED | 1.2 | — | ADR-002, ADR-003 | `services/project_brain/` | Chief Architect |
| 1.4 | Human + AI Operating Model | 🔴 NOT STARTED | 1.2 | ROLE_BASED_OPERATING_MODEL.md | — | `api/routers/` | Chief Architect |
| 1.5 | Value Proposition | 🔴 NOT STARTED | 1.1 | — | — | `roi_log` table | Chief Architect |

---

## Volume II — Construction Intelligence Model

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 2.1 | Intelligence Philosophy | 🔴 NOT STARTED | Vol I complete | CONSTRUCTION_INTELLIGENCE_MODEL.md | — | — | Chief Architect |
| 2.2 | 4-Layer Intelligence Architecture | ⚙️ IMPL ONLY | — | CONSTRUCTION_INTELLIGENCE_MODEL.md | ADR-001 | `services/` directory | None |
| 2.3 | Health Scoring Model | ⚙️ IMPL ONLY | — | — | ADR-004 | `BaseIntelligenceService` | None |
| 2.4 | Data Flow Philosophy | 🔴 NOT STARTED | 2.1 | HCI_AI_DATA_ARCHITECTURE_v1.md | — | `connector_sync_state` | Chief Architect |
| 2.5 | Risk Classification Model | 🔴 NOT STARTED | 2.1 | — | ADR-003 | `project_risks_computed` | Chief Architect |

---

## Volume III — Project Brain

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 3.1 | Project Brain Philosophy | 🔴 NOT STARTED | Vol I complete | PROJECT_BRAIN_SPEC.md | ADR-002 | — | Chief Architect |
| 3.2 | Per-Project Intelligence | ⚙️ IMPL ONLY | — | PROJECT_BRAIN_SPEC.md | ADR-002 | `services/project_brain/routes.py` | None |
| 3.3 | Snapshot Architecture | ⚙️ IMPL ONLY | — | — | — | `project_brain_snapshots` table | None |
| 3.4 | Risk Detection Methodology | 🔴 NOT STARTED | 3.1 | — | ADR-003 | `_detect_risks()` | Chief Architect |
| 3.5 | Cross-Project Aggregation | ⚙️ IMPL ONLY | — | — | ADR-002 | `services/cross_project/routes.py` | None |
| 3.6 | Extended Memory | ⚙️ IMPL ONLY | — | BTW-4 (STRATEGIC_BACKLOG.md) | — | `project_events`, `project_ai_conversations`, `project_document_links`, `project_daily_summaries` + 6 new endpoints | None |

---

## Volume IV — Role Intelligence

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 4.1 | Role-Based Intelligence Philosophy | 🔴 NOT STARTED | Vol I complete | ROLE_BASED_OPERATING_MODEL.md | — | — | Chief Architect |
| 4.2 | Superintendent Operating Model | 🔴 NOT STARTED | 4.1 | SUPERINTENDENT_DAILY_CONSOLE_SPEC.md | — | `api/routers/superintendent.py` | Chief Architect |
| 4.3 | Project Manager Operating Model | 🔴 NOT STARTED | 4.1 | PM_WEEKLY_CONSOLE_SPEC.md | — | `api/routers/pm.py` | Chief Architect |
| 4.4 | SS Console Implementation | ⚙️ IMPL ONLY | 4.2 | SUPERINTENDENT_DAILY_CONSOLE_SPEC.md | — | `api/routers/superintendent.py` | None |
| 4.5 | PM Console Implementation | ⚙️ IMPL ONLY | 4.3 | PM_WEEKLY_CONSOLE_SPEC.md | — | `api/routers/operations.py` pm_weekly + `_build_client_comm_queue` + `_rank_pm_actions` | None |
| 4.6 | Leadership Dashboard | ⚙️ IMPL ONLY | 4.3 | LEADERSHIP_MISSION_CONTROL_SPEC.md | — | `api/routers/leadership.py` | None |

---

## Volume V — Executive Intelligence

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 5.1 | Executive Intelligence Philosophy | 🔴 NOT STARTED | Vol I complete | LEADERSHIP_MISSION_CONTROL_SPEC.md | — | — | Chief Architect |
| 5.2 | Approval Authority Model | 🔴 NOT STARTED | Vol I complete | SOP_APPROVAL_GATE_REGISTER.md | — | `approval_queue` | Chief Architect |
| 5.3 | Mission Control Implementation | ⚙️ IMPL ONLY | — | LEADERSHIP_MISSION_CONTROL_SPEC.md | — | `api/routers/executive.py` | None |
| 5.4 | Morning Brief | ⚙️ IMPL ONLY | — | — | — | `api/routers/executive.py` | None |
| 5.5 | Approval Workflow | ⚙️ IMPL ONLY | 5.2 | — | — | `approval_queue` + GATE-H | None |
| 5.6 | Predictive Engine | ⚙️ IMPL ONLY | — | — | ADR-003 | `services/predictive_engine/routes.py` | None |

---

## Volume VI — Construction Intelligence Engine

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 6.1 | Intelligence Engine Philosophy | 🔴 NOT STARTED | Vol I complete | CONSTRUCTION_INTELLIGENCE_SERVICE_LAYER_v1.md | ADR-001 | — | Chief Architect |
| 6.2 | BaseIntelligenceService Pattern | ⚙️ IMPL ONLY | — | — | ADR-001 | `services/base_service.py` | None |
| 6.3 | Service Directory | ⚙️ IMPL ONLY | — | — | — | `services/` directory | None |
| 6.4 | Risk Detection Architecture | 🔴 NOT STARTED | 6.1 | — | ADR-003 | `_detect_*()` methods | Chief Architect |
| 6.5 | Connector Framework | ⚙️ IMPL ONLY | — | — | ADR-001 | `services/connectors/` | None |

---

## Volume VII — Automation Architecture

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 7.1 | Automation Philosophy | 🔴 NOT STARTED | Vol I complete | — | ADR-005 | — | Chief Architect |
| 7.2 | n8n Workflow Registry | ⚙️ IMPL ONLY | — | WORKFLOW_INVENTORY.md | — | `workflows/n8n/` | None |
| 7.3 | launchd Service Management | ⚙️ IMPL ONLY | — | — | — | `launchd/` | None |
| 7.4 | Browser Agent Protocol | ⚙️ IMPL ONLY | — | BROWSER_AGENT_STANDARD.md | — | `services/connectors/` | None |
| 7.5 | Error Handling + Retry | ⚙️ IMPL ONLY | — | — | — | `BaseConnector` | None |

---

## Volume VIII — Governance

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 8.1 | Governance Philosophy | 🔴 NOT STARTED | Vol I complete | SOP_APPROVAL_GATE_REGISTER.md | — | — | Chief Architect |
| 8.2 | Approval Gate Register | ⚙️ IMPL ONLY | 8.1 | SOP_APPROVAL_GATE_REGISTER.md | — | `approval_queue` | None |
| 8.3 | Security Standards | ⚙️ IMPL ONLY | — | — | — | `.env`, `api_key_middleware` | None |
| 8.4 | Testing Standards | ⚙️ IMPL ONLY | — | — | — | `tests/` directory | None |
| 8.5 | Coding Standards | ⚙️ IMPL ONLY | — | — | ADR-001 | `main.py` | None |
| 8.6 | Migration Standards | ⚙️ IMPL ONLY | — | — | — | `05_Database/migrations/` | None |

---

## Volume IX — Roadmap

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 9.1 | 2026 Roadmap | 🔴 NOT STARTED | Vol I complete | — | — | — | Chief Architect |
| 9.2 | Gate 5 Pilot Outcomes | 🔴 NOT STARTED | None | PILOT_READINESS_REPORT.md | — | — | Chief Architect |
| 9.3 | Phase Definitions | 🔴 NOT STARTED | 9.1 | IMPLEMENTATION_SEQUENCE.md | — | — | Chief Architect |
| 9.4 | Current State Reference | ⚙️ IMPL ONLY | — | LIVE_PROJECT_STATE.md | — | — | None |
| 9.5 | Architecture Milestones | 🔴 NOT STARTED | 9.1 | — | — | — | Chief Architect |

---

## Volume X — Future Vision

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 10.1 | 2027 Vision | 🔴 NOT STARTED | Vol IX complete | — | — | — | Chief Architect |
| 10.2 | 2028 Vision | 🔴 NOT STARTED | 10.1 | — | — | — | Chief Architect |
| 10.3 | Commercial Expansion | 🔴 NOT STARTED | 10.1 | — | — | — | Chief Architect |
| 10.4 | Multi-Company Architecture | 🔴 NOT STARTED | 10.3 | — | — | — | Chief Architect |
| 10.5 | AI Workforce Evolution | 🔴 NOT STARTED | 10.1 | — | — | — | Chief Architect |

---

## Implementation Additions (2026-06-29) — AUTHORING_QUEUE Updates

| Volume | Chapter | New Status | Change |
|--------|---------|-----------|--------|
| III | 3.2 Extended Memory | ⚙️ IMPL ONLY ✅ | BTW-4: /gateway/project/{code}/timeline (373 events), /documents, /memory — all live |
| III | 3.3.2 Events | ⚙️ IMPL ONLY ✅ | project_events table populated (13 types, 373 records) |
| III | 3.3.4 Knowledge Graph | ⚙️ IMPL ONLY ✅ | BTW-9: /api/v1/services/knowledge-graph/ live; Qdrant 13 collections populated |
| IV | 4.9-4.11 (NEW) | ⚙️ IMPL ONLY ✅ | BTW-5: 5 new role consoles (Owner/Office/Accounting/Client/Trade Partner) live at /gateway/role/* |
| VII | 7.2 n8n Registry | ⚙️ IMPL ONLY ✅ | Updated: 55/63 active workflows (was 32); 21 workflows documented in Volume VII |
| IX | 9.4 Current State | ⚙️ IMPL ONLY ✅ | Updated: all BTW complete, Phase 4 complete, Gate 5 verdict due July 1 |

---

## Queue Summary (Updated 2026-06-29)

| Status | Count | Volumes Affected |
|--------|-------|-----------------|
| 🔴 NOT STARTED | 18 | I, II, III, IV, V, VI, IX, X |
| ⚙️ IMPL ONLY | 26 | II, III, IV, V, VI, VII, VIII, IX |
| 🟡 IN PROGRESS | 0 | — |
| 🟠 DRAFT READY | 0 | — |
| 🟢 PUBLISHED | 4 | I.A, I.B, I.C, I.D |
| ⚠️ CONFLICT | 0 | — |

**Chief Architect authoring priority order (most urgent first):**
1. Volume I (1.1-1.5) — Platform Purpose, Operating Philosophy, Intelligence Model Philosophy, Human+AI Model, Value Proposition
2. Volume IX (9.1-9.2) — 2026 Roadmap + Gate 5 verdict (due July 1, 2026)
3. Volume IV (4.1-4.3) — Role philosophy for 9 live consoles
4. Volume V (5.1-5.2) — Executive philosophy + approval authority model
5. Volume II (2.1, 2.4, 2.5) — Intelligence and data flow philosophy
6. Volume III (3.1, 3.4) — Project Brain philosophy + risk detection methodology
7. Volume VI (6.1, 6.4) — Intelligence engine philosophy + risk architecture
8. Volume VIII (8.1) — Governance philosophy
9. Volume X (10.1-10.5) — Future vision (2027-2028)

**Total chapters needing GBT authorship: 18 chapters across 8 volumes**
**Full handbook completion ETA: depends on GBT authoring velocity**
