# Implementation Inventory
Generated: 2026-06-26 | Classification: KEEP / MERGE / ARCHIVE / REVIEW / UNKNOWN

---

## APIs & Routers (FastAPI :8000)

| Path Prefix | Description | Classification |
|---|---|---|
| /api/v1/health | Health check | KEEP |
| /api/v1/projects | Project CRUD | KEEP |
| /api/v1/vendors | Vendor CRUD | KEEP |
| /api/v1/bids | Bid packages & entries | KEEP |
| /api/v1/sop/registry | 27-SOP registry | KEEP |
| /api/v1/sop/04–30 | SOP execution instances | KEEP |
| /api/v1/services/approval-queue | Human-in-loop approval | KEEP |
| /api/v1/services/background-learning | Drive/HubSpot document discovery | KEEP |
| /api/v1/services/bid-intelligence | Bid search + leveling | KEEP |
| /api/v1/services/bid-leveling | AI bid leveling engine | KEEP |
| /api/v1/services/business-process-library | 27 mapped processes | KEEP |
| /api/v1/services/connector-registry | Integration connector tracking | KEEP |
| /api/v1/services/decision-intelligence | Decision logging | KEEP |
| /api/v1/services/document-intelligence | Document classify/ingest/search | KEEP |
| /api/v1/services/historical-cost | Garmisch cost benchmarks (21 records) | KEEP |
| /api/v1/services/kpi-intelligence | KPI snapshots + alerts | KEEP |
| /api/v1/services/lessons-learned | 10 lessons (7 Garmisch) | KEEP |
| /api/v1/services/operating-rules | Operating rule evaluation | KEEP |
| /api/v1/services/procurement | Long-lead + procurement status | KEEP |
| /api/v1/services/project-brain | Per-project AI synthesis | KEEP |
| /api/v1/services/risk-intelligence | Risk flags per project | KEEP |
| /api/v1/services/schedule-intelligence | Schedule variance analysis | KEEP |
| /api/v1/services/vendor-intelligence | Vendor research + scoring | KEEP |
| /api/v1/mvp | MVP exec report + pilot ops | KEEP |
| /api/v1/platform/* | Audit, events, identity, notifications, search | KEEP |
| /api/v1/memory/* | Qdrant vector search | KEEP |
| /api/v1/ingest/* | File/batch/path ingestion | KEEP |
| /api/v1/search | Cross-collection search | KEEP |
| /api/v1/storage/* | Object storage buckets | REVIEW |
| /api/v1/ai/* | Claude agent calls | KEEP |
| /api/v1/auth/* | Auth mode + status | KEEP |
| /api/v1/system/* | System config + collections | KEEP |
| /api/v1/workflows/* | WF trigger + sync | KEEP |
| /bids/, /projects/, /vendors/, etc. | Unversioned duplicate routes | MERGE (redirect to /api/v1/) |

---

## n8n Workflows

| Workflow | Status | Classification |
|---|---|---|
| WF-003 Historical Cost Queue | ACTIVE | KEEP |
| WF-004 Lessons Learned Engine | ACTIVE | KEEP |
| WF-005 SOP Registry Sync | ACTIVE | KEEP |
| WF-006 Executive Alerts | ACTIVE | KEEP |
| WF-007 AI Bid Leveling Engine | ACTIVE | KEEP |
| WF-011 Site Superintendent Daily Briefing | ACTIVE | KEEP |
| Bid Receipt Processing v5 | ACTIVE | KEEP |
| WF-008 Bid Follow-Up Engine | INACTIVE | REVIEW (test before activating) |
| WF-009 New Job Setup | INACTIVE | REVIEW (test before activating) |
| WF-010 Outlook Email Router | INACTIVE | REVIEW (test before activating) |
| ARCHIVED — Bid Leveling (merged) | INACTIVE | ARCHIVE |
| ARCHIVED — Bid Receipt v5 duplicate | INACTIVE | ARCHIVE |
| RETIRED — ChatGPT Chrome Bridge | INACTIVE | ARCHIVE |
| RETIRED — TMP Outlook webhook | INACTIVE | ARCHIVE |
| Inbox Cleanup — Delete Test Emails | INACTIVE | ARCHIVE |

---

## Python Workflows (03_Source_Code/workflows/)

| File | Description | Classification |
|---|---|---|
| wf001_new_project.py | New project setup | KEEP |
| wf002_meeting_intelligence.py | Meeting intel | KEEP |
| wf003_morning_brief.py | Morning brief | KEEP |
| wf004_daily_log.py | Daily log | KEEP |
| wf005_lessons_learned.py | Lessons capture | KEEP |
| wf006_inbox_review.py | Inbox review | KEEP |
| wf_pm.py | PM review workflow | KEEP |
| wf_report.py | Report generation | KEEP |
| wf_superintendent.py | Superintendent workflow | KEEP |
| sync_drive.py | Drive sync | KEEP |
| sync_hubspot.py | HubSpot sync | KEEP |
| sync_houzz.py | Houzz sync | KEEP |
| mine_hubspot.py | HubSpot data mining | KEEP |
| memory_utils.py | Memory utilities | KEEP |

---

## Databases

| Store | Container | Tables/Collections | Classification |
|---|---|---|---|
| PostgreSQL | hci_postgres | 47 tables | KEEP |
| Qdrant | hci_qdrant | hci_* collections (mostly empty — needs indexing) | KEEP |
| Redis | hci_redis | Cache/temp state | KEEP |
| n8n SQLite | n8n container | Workflow state | KEEP |

### PostgreSQL Tables (47)
All KEEP — actively referenced by services. Tables created in schema.sql, seeded via ingestion pipeline or direct inserts.

Key tables with live data:
- `projects` (4 rows — 3 pilot + 83 Sagebrusch)
- `vendors` (392 rows — 258 with CSI)
- `business_processes` (27 rows)
- `lessons_learned` (10 rows)
- `historical_cost_records` (21 rows — Garmisch seed)
- `background_learning_records` (50 rows)
- `operating_rules` (seeded)

---

## Intelligence Services (03_Source_Code/services/)

| Service | Status | Classification |
|---|---|---|
| approval_queue | Active | KEEP |
| background_learning | Active | KEEP |
| bid_intelligence | Active | KEEP |
| bid_leveling | Active | KEEP |
| business_process_library | Active | KEEP |
| connector_registry | Active | KEEP |
| decision_intelligence | Active | KEEP |
| document_intelligence | Active | KEEP |
| historical_cost | Active — SQL fallback added | KEEP |
| kpi_intelligence | Active | KEEP |
| lessons_learned | Active | KEEP |
| mcp_server | Active — hci_mcp_server.py | KEEP |
| operating_rules | Active | KEEP |
| platform/audit | Active | KEEP |
| platform/event_bus | Active | KEEP |
| platform/identity | Active | KEEP |
| platform/notifications | Active | KEEP |
| platform/search_gateway | Active | KEEP |
| procurement | Active | KEEP |
| project_brain | Active | KEEP |
| risk_intelligence | Active | KEEP |
| schedule_intelligence | Active | KEEP |
| sop_execution (SOPs 04–30) | Active — 27 SOPs | KEEP |
| vendor_intelligence | Active | KEEP |

---

## Integrations (03_Source_Code/integrations/)

| Integration | Description | Classification |
|---|---|---|
| google_sheets.py | Sheets read/write via OAuth | KEEP |
| hubspot.py | HubSpot CRM read | KEEP |
| microsoft_graph.py | Outlook/Graph API | KEEP |
| credentials.py | n8n credential decryption | KEEP |

---

## MCP Server

| Item | Detail | Classification |
|---|---|---|
| hci_mcp_server.py | FastMCP standalone on :8080 | KEEP |
| ngrok tunnel | speculate-armband-retinal.ngrok-free.dev/mcp | KEEP |
| Tools: ReadConstructionOS | SOP + rules + lessons + processes | KEEP |
| Tools: GetProjectContext | Project brain query | KEEP |
| Tools: HistoricalCostLookup | Cost search (fixed) | KEEP |
| Tools: LogLessonLearned | Write lesson | KEEP |
| Tools: TriggerSOP | SOP execution trigger | KEEP |
| Tools: QueryVendorIntelligence | Vendor search | KEEP |

---

## Documentation

| File | Description | Classification |
|---|---|---|
| AI_TEAM/00_STATUS.md | System status | MERGE (into LIVE_PROJECT_STATE.md) |
| AI_TEAM/01_ROADMAP.md | Roadmap | MERGE (into Program Repo) |
| AI_TEAM/02_ACTIVE_WORK.md | Active work | MERGE |
| AI_TEAM/03_DECISIONS.md | Decision log | MERGE |
| AI_TEAM/04_ARCHITECTURE.md | Architecture | MERGE |
| AI_TEAM/05_BACKLOG.md | Backlog | MERGE (into Program Repo) |
| AI_TEAM/06_NEXT_SESSION.md | Session handoff | MERGE |
| AI_TEAM/07_BLOCKERS.md | Blockers | MERGE |
| AI_TEAM/08_CHANGELOG.md | Changelog | KEEP (implementation log) |
| AI_TEAM/09_HANDOFF_PROTOCOL.md | Handoff protocol | MERGE |
| CLAUDE.md | Claude Code operating rules | KEEP (implementation layer) |
| 03_Source_Code/CLAUDE.md | Source code rules | KEEP |
| 00_CLAUDE_CODE_MASTER_PROMPT.md | Master prompt | REVIEW |
| README.md | Repo readme | KEEP |
| SESSION_STARTUP/ | Session startup docs | REVIEW |

---

## Scripts & Infrastructure

| Item | Description | Classification |
|---|---|---|
| docker-compose.yml | Full stack orchestration | KEEP |
| infrastructure/docker-compose.storage.yml | Storage services | KEEP |
| infrastructure/docker-compose.yml | Alt compose | REVIEW (may duplicate) |
| infrastructure/setup_mac_mini.sh | Mac mini migration playbook | KEEP |
| 03_Source_Code/ingestion/ | Ingestion pipeline | KEEP |
| 05_Database/postgres/schema.sql | DB DDL | KEEP |
| scripts/ | Utility scripts | REVIEW |

---

## Google Drive Registries

| Registry | Drive ID | Classification |
|---|---|---|
| HCI_Construction_OS_v3 (860 contacts) | (in memory) | KEEP |
| SOP 00 master | (in memory) | KEEP |
| 42-pack SOPs | (in memory) | KEEP |
| SOP 2.0 | (in memory) | KEEP |
| HCI_AI_Registry_Build_v2 Garmisch | Active source | KEEP |
| 03 Registries workbook | Active — sole live copy | KEEP |
| Buck AI folder (archived copy) | Trashed | ARCHIVE |
