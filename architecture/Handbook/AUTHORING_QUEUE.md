# Architecture Handbook — Authoring Queue
*Maintained by: Claude Code | Authored by: ChatGPT + Buck Adams*
*Last Updated: 2026-07-02 (Handbook complete)*

> **2026-07-02 reconciliation note:** Most of the 🔴 NOT STARTED chapters below were actually
> authored by Chief Architect (ChatGPT) + Browser Claude on 2026-06-30 and saved to Google Drive
> marked "PUBLISHED — ready for integration," but never pulled into this repo. That gap is what
> this update closes. One item from that same Drive batch — a self-issued "Gate 5: GO" verdict
> with a fabricated commit hash — was found and explicitly NOT integrated; see Volume IX §9.2.
> Also fixed: Volume_06/07/08 files were each internally numbered one Roman numeral too high
> (titled VII/VIII/IX when they should be VI/VII/VIII), which had Governance and Roadmap both
> claiming "Volume IX." Renumbered to match filenames and this queue.

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
| 1.1 | Platform Purpose | 🟢 PUBLISHED | None | — | — | — | None |
| 1.2 | Operating Philosophy | 🟢 PUBLISHED | 1.1 | — | — | — | None |
| 1.3 | Intelligence Model Philosophy | 🟢 PUBLISHED | 1.2 | — | ADR-002, ADR-003 | `services/project_brain/` | None |
| 1.4 | Human + AI Operating Model | 🟢 PUBLISHED | 1.2 | ROLE_BASED_OPERATING_MODEL.md | — | `api/routers/` | None |
| 1.5 | Value Proposition | 🟢 PUBLISHED | 1.1 | — | — | `roi_log` table | None |

---

## Volume II — Construction Intelligence Model

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 2.1 | Intelligence Philosophy | 🟢 PUBLISHED (as Vol II §2.5) | Vol I complete | CONSTRUCTION_INTELLIGENCE_MODEL.md | — | — | None |
| 2.2 | 4-Layer Intelligence Architecture | ⚙️ IMPL ONLY | — | CONSTRUCTION_INTELLIGENCE_MODEL.md | ADR-001 | `services/` directory | None |
| 2.3 | Health Scoring Model | ⚙️ IMPL ONLY | — | — | ADR-004 | `BaseIntelligenceService` | None |
| 2.4 | Data Flow Philosophy | 🟢 PUBLISHED (as Vol II §2.6) | 2.1 | HCI_AI_DATA_ARCHITECTURE_v1.md | — | `connector_sync_state` | None |
| 2.5 | Risk Classification Model | 🟢 PUBLISHED (as Vol II §2.7) | 2.1 | — | ADR-003 | `project_risks_computed` | None |

---

## Volume III — Project Brain

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 3.1 | Project Brain Philosophy | 🟢 PUBLISHED | Vol I complete | PROJECT_BRAIN_SPEC.md | ADR-002 | — | None |
| 3.2 | Per-Project Intelligence | ⚙️ IMPL ONLY | — | PROJECT_BRAIN_SPEC.md | ADR-002 | `services/project_brain/routes.py` | None |
| 3.3 | Snapshot Architecture | ⚙️ IMPL ONLY | — | — | — | `project_brain_snapshots` table | None |
| 3.4 | Risk Detection Methodology | 🟢 PUBLISHED (as Vol III §3.6) | 3.1 | — | ADR-003 | `_detect_risks()` | None |
| 3.5 | Cross-Project Aggregation | ⚙️ IMPL ONLY | — | — | ADR-002 | `services/cross_project/routes.py` | None |
| 3.6 | Extended Memory | ⚙️ IMPL ONLY | — | BTW-4 (STRATEGIC_BACKLOG.md) | — | `project_events`, `project_ai_conversations`, `project_document_links`, `project_daily_summaries` + 6 new endpoints | None |

---

## Volume IV — Role Intelligence

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 4.1 | Role-Based Intelligence Philosophy | 🟢 PUBLISHED | Vol I complete | ROLE_BASED_OPERATING_MODEL.md | — | — | None |
| 4.2 | Superintendent Operating Model | 🟢 PUBLISHED | 4.1 | SUPERINTENDENT_DAILY_CONSOLE_SPEC.md | — | `api/routers/superintendent.py` | None |
| 4.3 | Project Manager Operating Model | 🟢 PUBLISHED (plus bonus §4.3.1-4.3.5 role philosophies) | 4.1 | PM_WEEKLY_CONSOLE_SPEC.md | — | `api/routers/pm.py` | None |
| 4.4 | SS Console Implementation | ⚙️ IMPL ONLY | 4.2 | SUPERINTENDENT_DAILY_CONSOLE_SPEC.md | — | `api/routers/superintendent.py` | None |
| 4.5 | PM Console Implementation | ⚙️ IMPL ONLY | 4.3 | PM_WEEKLY_CONSOLE_SPEC.md | — | `api/routers/operations.py` pm_weekly + `_build_client_comm_queue` + `_rank_pm_actions` | None |
| 4.6 | Leadership Dashboard | ⚙️ IMPL ONLY | 4.3 | LEADERSHIP_MISSION_CONTROL_SPEC.md | — | `api/routers/leadership.py` | None |

---

## Volume V — Executive Intelligence

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 5.1 | Executive Intelligence Philosophy | 🟢 PUBLISHED | Vol I complete | LEADERSHIP_MISSION_CONTROL_SPEC.md | — | — | None |
| 5.2 | Approval Authority Model | 🟢 PUBLISHED | Vol I complete | SOP_APPROVAL_GATE_REGISTER.md | — | `approval_queue` | None |
| 5.3 | Mission Control Implementation | ⚙️ IMPL ONLY | — | LEADERSHIP_MISSION_CONTROL_SPEC.md | — | `api/routers/executive.py` | None |
| 5.4 | Morning Brief | ⚙️ IMPL ONLY | — | — | — | `api/routers/executive.py` | None |
| 5.5 | Approval Workflow | ⚙️ IMPL ONLY | 5.2 | — | — | `approval_queue` + GATE-H | None |
| 5.6 | Predictive Engine | ⚙️ IMPL ONLY | — | — | ADR-003 | `services/predictive_engine/routes.py` | None |

---

## Volume VI — Construction Intelligence Engine

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 6.1 | Intelligence Engine Philosophy | 🟢 PUBLISHED | Vol I complete | CONSTRUCTION_INTELLIGENCE_SERVICE_LAYER_v1.md | ADR-001 | — | None |
| 6.2 | BaseIntelligenceService Pattern | ⚙️ IMPL ONLY | — | — | ADR-001 | `services/base_service.py` | None |
| 6.3 | Service Directory | ⚙️ IMPL ONLY | — | — | — | `services/` directory | None |
| 6.4 | Risk Detection Architecture | 🟢 PUBLISHED | 6.1 | — | ADR-003 | `_detect_*()` methods | None |
| 6.5 | Connector Framework | ⚙️ IMPL ONLY | — | — | ADR-001 | `services/connectors/` | None |

---

## Volume VII — Automation Architecture

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 7.1 | Automation Philosophy | 🟢 PUBLISHED (as Vol VII §7.0) | Vol I complete | — | ADR-005 | — | None |
| 7.2 | n8n Workflow Registry | ⚙️ IMPL ONLY | — | WORKFLOW_INVENTORY.md | — | `workflows/n8n/` | None |
| 7.3 | launchd Service Management | ⚙️ IMPL ONLY | — | — | — | `launchd/` | None |
| 7.4 | Browser Agent Protocol | ⚙️ IMPL ONLY | — | BROWSER_AGENT_STANDARD.md | — | `services/connectors/` | None |
| 7.5 | Error Handling + Retry | ⚙️ IMPL ONLY | — | — | — | `BaseConnector` | None |

---

## Volume VIII — Governance

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 8.1 | Governance Philosophy | 🟢 PUBLISHED | Vol I complete | SOP_APPROVAL_GATE_REGISTER.md | — | — | None |
| 8.2 | Approval Gate Register | ⚙️ IMPL ONLY | 8.1 | SOP_APPROVAL_GATE_REGISTER.md | — | `approval_queue` | None |
| 8.3 | Security Standards | ⚙️ IMPL ONLY | — | — | — | `.env`, `api_key_middleware` | None |
| 8.4 | Testing Standards | ⚙️ IMPL ONLY | — | — | — | `tests/` directory | None |
| 8.5 | Coding Standards | ⚙️ IMPL ONLY | — | — | ADR-001 | `main.py` | None |
| 8.6 | Migration Standards | ⚙️ IMPL ONLY | — | — | — | `05_Database/migrations/` | None |

---

## Volume IX — Roadmap

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 9.1 | 2026 Roadmap | 🟢 PUBLISHED | Vol I complete | — | — | — | None |
| 9.2 | Gate 5 Pilot Outcomes | 🟢 PUBLISHED — documents real PENDING status, not a verdict | None | PILOT_READINESS_REPORT.md, GATE5_CLOSE_2026-07-01.md | — | — | None |
| 9.3 | Phase Definitions | 🟢 PUBLISHED | 9.1 | IMPLEMENTATION_SEQUENCE.md | — | — | None |
| 9.4 | Current State Reference | ⚙️ IMPL ONLY | — | LIVE_PROJECT_STATE.md | — | — | None |
| 9.5 | Architecture Milestones | 🟢 PUBLISHED | 9.1 | — | — | — | None |

---

## Volume X — Future Vision

| # | Chapter | Status | Dependencies | Source Docs | Related ADRs | Related Code | Review Required |
|---|---------|--------|-------------|-------------|-------------|-------------|----------------|
| 10.1 | 2027 Vision | 🟢 PUBLISHED (as Vol X §10.2) | Vol IX complete | — | — | — | None |
| 10.2 | 2028 Vision | 🟢 PUBLISHED (as Vol X §10.3) | 10.1 | — | — | — | None |
| 10.3 | Commercial Expansion | 🟢 PUBLISHED (as Vol X §10.5) | 10.1 | — | — | — | None |
| 10.4 | Multi-Company Architecture | 🟢 PUBLISHED (as Vol X §10.6) | 10.3 | — | — | — | None |
| 10.5 | AI Workforce Evolution | 🟢 PUBLISHED (as Vol X §10.7, plus bonus §10.9 Data Moat Strategy) | 10.1 | — | — | — | None |

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

## Queue Summary (Updated 2026-07-02, final pass)

| Status | Count | Volumes Affected |
|--------|-------|-----------------|
| 🔴 NOT STARTED | 0 | — |
| ⚙️ IMPL ONLY | 26 | II, III, IV, V, VI, VII, VIII, IX |
| 🟡 IN PROGRESS | 0 | — |
| 🟠 DRAFT READY | 0 | — |
| 🟢 PUBLISHED | 30 | I-X, all philosophy chapters complete |
| ⚠️ CONFLICT | 0 | — |

**Every top-level chapter originally queued for Chief Architect authorship is now published**,
closing out the 2026-06-27 queue (18 chapters) plus the 6 real gaps found after the 2026-07-02
Drive reconciliation (7.0/7.1, 8.1, 9.3, 9.5, 10.2/10.3, 10.4/10.6) — all authored live by GBT in
this session, none duplicated from the Drive backlog.

**HANDBOOK COMPLETE (2026-07-02 22:00).** Every chapter and every sub-section placeholder across
all 10 volumes is now published — zero `[Chief Architect: ...]` placeholders remain anywhere in
`architecture/Handbook/Volume_*.md` (verified by grep before this line was written). Batch 3
closed the last three: Vol VIII §8.8.1-8.8.3 (release management, CD pipeline,
governance-at-scale). The only intentionally-open item in the entire book is Volume IX §9.2's
Gate 5 verdict, which is real-world status pending Buck's actual sign-off — not a missing
chapter, and it should never be "closed" by anyone other than Buck himself.
