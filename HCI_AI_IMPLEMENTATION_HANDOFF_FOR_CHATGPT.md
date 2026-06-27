# HCI AI Operating System — Full Implementation Handoff
**For:** ChatGPT (Chief Architect / Architecture Review Board)
**From:** Claude Code (Lead Implementation Engineer)
**Date:** 2026-06-26
**Repository Branch:** feature/data-architecture-document-storage
**Last Commit:** b4dbed1

---

## 1. What This Is

This is the complete state of the HCI AI Construction Operating System implementation repository. It represents approximately one week of active build work. The system is live, running on a Mac, and actively being used in a 5-day Gate 5 Pilot (2026-06-25 to 2026-07-01) across three real construction projects.

The owner is **Buck Adams**, owner/operator of **Hendrickson Construction Inc (HCI)** — a custom residential general contractor based in Aspen, CO. Buck is building an AI-powered construction operating system to run preconstruction, procurement, field operations, and project intelligence.

---

## 2. Infrastructure (All Running)

| Service | Purpose | URL / Location |
|---|---|---|
| FastAPI | Main application API | http://localhost:8000 |
| MCP Server | AI tool interface (Claude, ChatGPT, Browser Claude) | http://localhost:8080 |
| MCP (public) | ngrok tunnel for external AI access | https://speculate-armband-retinal.ngrok-free.dev/mcp |
| n8n | Workflow automation engine | http://localhost:5678 |
| PostgreSQL | Primary truth store | localhost:5432 — db: hci_os, user: hci_admin |
| Qdrant | Vector memory store | http://localhost:6333 |
| Redis | Cache / temporary state | localhost:6379 |

**Auth:**
- FastAPI: `X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6`
- n8n: key stored in `.env` as `N8N_API_KEY`
- All credentials stored in `/Users/buckadams/HCI_AI_Operating_System/.env` (gitignored)

---

## 3. What's Been Built — The Full Stack

### 3.1 FastAPI Application (427 endpoints)
Located at `03_Source_Code/api/`

**17 Routers:**

| Router | Prefix | What It Does |
|---|---|---|
| health | /api/v1/health | System health check |
| projects | /api/v1/projects | Project CRUD (4 active projects) |
| vendors | /api/v1/vendors | Vendor CRUD (392 vendors) |
| bids | /api/v1/bids | Bid packages and entries |
| sop | /api/v1/sop | SOP registry + 27 SOP execution engines |
| mvp_ops | /api/v1/mvp | Pilot operations + executive report |
| platform | /api/v1/platform | Audit, events, identity, notifications, search |
| memory | /api/v1/memory | Qdrant vector search |
| ingest | /api/v1/ingest | File/batch/path document ingestion |
| search | /api/v1/search | Cross-collection search |
| storage | /api/v1/storage | Object storage buckets |
| ai | /api/v1/ai | Claude agent calls |
| auth | /api/v1/auth | Auth mode + status |
| system | /api/v1/system | System config + collections |
| workflows | /api/v1/workflows | WF trigger + sync |
| documents | /api/v1/documents | Document management |
| vendors | /api/v1/vendors | Vendor management |

**Note:** There are also unversioned duplicate routes (e.g. `/bids/`, `/projects/`) that need to be cleaned up — flagged in DUPLICATE_RISK_REPORT.md.

### 3.2 Intelligence Services (18 services)
Located at `03_Source_Code/services/`

Each service has a `routes.py` (FastAPI router) and a main service class. All inherit from `BaseIntelligenceService` which provides PostgreSQL query helpers, Qdrant vector search, and Claude AI calling.

| Service | API Prefix | Purpose | Data State |
|---|---|---|---|
| approval_queue | /services/approval-queue | Human-in-loop approval gate for all writes | Active |
| background_learning | /services/background-learning | Discovers docs from Drive/HubSpot/Houzz, queues for AI analysis | 50 records |
| bid_intelligence | /services/bid-intelligence | Bid search, summary, leveling queries | Active |
| bid_leveling | /services/bid-leveling | AI-powered bid comparison + scope leveling | Active |
| business_process_library | /services/business-process-library | 27 processes mapped from SOPs | 27 rows |
| connector_registry | /services/connector-registry | Tracks all integration connectors | Active |
| decision_intelligence | /services/decision-intelligence | Logs decisions + tracks outcomes | Active |
| document_intelligence | /services/document-intelligence | Classify, ingest, search documents | Active |
| historical_cost | /services/historical-cost | Cost benchmarks from past projects | 21 rows (Garmisch) |
| kpi_intelligence | /services/kpi-intelligence | KPI snapshots + alert triggers | Active |
| lessons_learned | /services/lessons-learned | Captures + searches lessons | 10 rows |
| operating_rules | /services/operating-rules | Evaluates actions against HCI rules | Seeded |
| procurement | /services/procurement | Long-lead + procurement status | Active |
| project_brain | /services/project-brain | Per-project AI synthesis layer | Active |
| risk_intelligence | /services/risk-intelligence | Risk flags per project | Active |
| schedule_intelligence | /services/schedule-intelligence | Schedule variance analysis | Active |
| vendor_intelligence | /services/vendor-intelligence | Vendor research + scoring | 392 vendors |
| mcp_server | (standalone :8080) | FastMCP tool server for AI access | Live |

### 3.3 SOP Execution Engine (27 SOPs fully implemented)
Located at `03_Source_Code/services/sop_execution/`

Each SOP has three files: `sop_XX_agent.py` (Claude AI agent), `sop_XX_service.py` (business logic), `sop_XX_templates.py` (output templates). All SOPs have full API routes at `/api/v1/sop/XX/`.

| SOP | Name | Phase |
|---|---|---|
| 04 | Plan Review | Preconstruction |
| 05 | Construction Narrative | Preconstruction |
| 06 | Missing Information / Risk Log | Preconstruction |
| 07 | ROM Budget | Estimating |
| 08 | Historical Cost Database | Estimating |
| 09 | Budget Review | Estimating |
| 10 | Allowances / Alternates / Exclusions | Preconstruction |
| 11 | Bid Package Assembly | Preconstruction/Bidding |
| 12 | Subcontractor CRM | Preconstruction/Bidding |
| 13 | Bid Distribution | Bidding |
| 14 | Bid Follow-Up | Bidding |
| 15 | Bid Leveling | Bidding/Buyout |
| 16 | Buyout | Buyout |
| 17 | Project Schedule | Preconstruction/Setup |
| 18 | Long-Lead Procurement | Preconstruction/Setup |
| 19 | Subcontract Agreement | Buyout/Contract Execution |
| 20 | Contract Setup | Setup |
| 21 | Compliance | Setup |
| 22 | COI / W-9 / Lien Waiver | Setup |
| 23 | Project Startup | Setup/Field |
| 24 | Superintendent Daily Dashboard | Field Execution |
| 25 | Daily Log | Field Execution |
| 26 | Field Coordination | Field Execution |
| 27 | Quality Control | Field Execution |
| 28 | QC Detail Card | Field Execution |
| 29 | Safety | Field Execution |
| 30 | Inspection | Field Execution |

Each SOP has its own approval gate, AI draft step, human confirmation step, and handoff to the next SOP. The full chain from SOP-04 (Plan Review) through SOP-30 (Inspection) represents HCI's complete construction workflow.

### 3.4 Platform Services (5 cross-cutting services)
Located at `03_Source_Code/services/platform/`

| Service | Purpose |
|---|---|
| audit | Full audit trail for every action |
| event_bus | Pub/sub event system for service coordination |
| identity | User/role/permission management |
| notifications | Alert delivery to Buck and team |
| search_gateway | Unified search across all data domains |

### 3.5 Integrations (4 external systems)
Located at `03_Source_Code/integrations/`

| Integration | File | What It Does |
|---|---|---|
| Google Drive | google_sheets.py | Read/write Sheets via OAuth; read Drive files |
| HubSpot CRM | hubspot.py | Read deals, contacts, companies, notes, tasks |
| Microsoft Graph | microsoft_graph.py | Read Outlook inbox, calendar, email routing |
| n8n Credentials | credentials.py | Decrypt n8n credential store for API tokens |

### 3.6 Python Workflow Files
Located at `03_Source_Code/workflows/`

| File | WF | Purpose |
|---|---|---|
| wf001_new_project.py | WF-001 | New project setup in HubSpot + DB + Drive |
| wf002_meeting_intelligence.py | WF-002 | Meeting notes → action items → AI summary |
| wf003_morning_brief.py | WF-003 | Morning briefing email to Buck |
| wf004_daily_log.py | WF-004 | Daily log capture from field |
| wf005_lessons_learned.py | WF-005 | Lessons learned capture + storage |
| wf006_inbox_review.py | WF-006 | Inbox triage + routing |
| wf_pm.py | WF-PM | PM daily review + weekly report |
| wf_report.py | WF-RPT | Executive health, schedule alerts, owner summary |
| wf_superintendent.py | WF-SUPER | Superintendent daily log |
| sync_drive.py | — | Drive sync to background_learning pipeline |
| sync_hubspot.py | — | HubSpot sync to local DB |
| sync_houzz.py | — | Houzz project sync (DO NOT MODIFY — pending architecture review) |
| mine_hubspot.py | — | Deep HubSpot data mining |
| memory_utils.py | — | Qdrant memory utilities |

### 3.7 Ingestion Pipeline
Located at `03_Source_Code/ingestion/`

| File | Purpose |
|---|---|
| ingest.py | Main ingestion orchestrator |
| classifier.py | Document type classification |
| extractor.py | Text extraction from PDFs, DOCX, etc. |
| ingest_memory.py | Qdrant vector indexing |
| seed_postgres.py | DB seeding from source data |
| create_collections.py | Qdrant collection setup |
| run_ingestion.py | CLI entry point |

---

## 4. Database — 47 Tables

All in PostgreSQL container `hci_postgres`, database `hci_os`.

### Core Business Tables
| Table | Rows | Description |
|---|---|---|
| projects | 4 | 64 Eastwood, 101 Francis, 1355 Riverside, 83 Sagebrusch |
| vendors | 392 | 258 with CSI divisions assigned |
| bid_packages | — | Bid packages per project |
| bid_entries | — | Individual vendor bids |
| meetings | — | Meeting records |
| rfis | — | RFI log |
| submittals | — | Submittal tracking |
| risks | — | Risk register |
| long_lead_items | — | Long-lead procurement items |
| procurement_items | — | Procurement tracking |
| daily_logs | — | Field daily logs |
| schedule_variance | — | Schedule variance records |

### Intelligence Tables
| Table | Rows | Description |
|---|---|---|
| business_processes | 27 | All 27 SOPs mapped as business processes |
| lessons_learned | 10 | 3 gate test + 7 Garmisch mined |
| historical_cost_records | 21 | 17 CSI division + 4 vendor proposals from 655 S Garmisch |
| decision_records | — | Decision log |
| kpi_snapshots | — | KPI history |
| operating_rules | seeded | HCI operating rules |
| operating_rule_exceptions | — | Rule exception log |
| background_learning_records | 50 | Document discovery pipeline |
| approval_queue | — | Pending human approvals |

### SOP Execution Tables
| Table | Description |
|---|---|
| sop_instances | Running SOP instances |
| sop_inputs | Inputs to each SOP run |
| sop_outputs | Outputs from each SOP run |
| sop_approval_gates | Approval gate state per instance |
| sop_exceptions | SOP exception log |
| sop_kpi_records | KPI captured per SOP run |
| sop_stop_events | Stop conditions triggered |
| sop_workflow_events | SOP lifecycle events |

### Platform Tables
| Table | Description |
|---|---|
| platform_audit_log | Full action audit trail |
| platform_events | Event bus records |
| platform_notifications | Notification queue |
| platform_permissions | Role permission matrix |
| platform_users | System users / AI actors |

### HubSpot Sync Tables (local cache)
| Table | Description |
|---|---|
| hubspot_deals | Deal records synced from HubSpot |
| hubspot_contacts | Contact records |
| hubspot_companies | Company records |
| hubspot_notes | Note records |
| hubspot_tasks | Task records |
| hubspot_engagements | Engagement records |

### Other Tables
| Table | Description |
|---|---|
| houzz_projects | Houzz project sync (DO NOT MODIFY) |
| houzz_daily_logs | Houzz daily log sync |
| houzz_schedule_items | Houzz schedule items |
| connector_registry | Integration connector registry |
| drive_sync_log | Drive sync history |
| roi_log | ROI tracking |

---

## 5. MCP Server — The AI Access Layer

**File:** `03_Source_Code/services/mcp_server/hci_mcp_server.py`
**Running at:** http://localhost:8080 (FastMCP standalone)
**Public URL:** https://speculate-armband-retinal.ngrok-free.dev/mcp

The MCP server is how ALL external AI systems should talk to the HCI OS. It wraps the FastAPI and presents clean tools.

### Available MCP Tools

| Tool | What It Does |
|---|---|
| `ReadConstructionOS` | Reads SOPs, operating rules, lessons learned, business processes. Category param: `sops`, `operating_rules`, `lessons_learned`, `business_processes`, `all` |
| `GetProjectContext` | Full project brain query — bids, vendors, schedule, risks for any project number |
| `HistoricalCostLookup` | Searches historical cost records by trade/CSI division/project type |
| `LogLessonLearned` | Writes a new lesson learned to the DB (goes through approval queue) |
| `TriggerSOP` | Starts an SOP instance for a given project |
| `QueryVendorIntelligence` | Searches vendor database by trade, CSI division, or name |

**Connection method for ChatGPT:**
The ngrok URL above is the public MCP endpoint. ChatGPT can connect to it as a custom tool/plugin using the `/mcp` path. The server speaks the MCP protocol (JSON-RPC over HTTP).

---

## 6. Active Projects (Gate 5 Pilot)

| ID | Project | HubSpot Deal ID | Drive Folder | Outlook Folder |
|---|---|---|---|---|
| 1 | 64 Eastwood | 331240861419 | Linked | 64 Eastwood |
| 2 | 101 Francis | 321401932527 | Linked | 101 Francis |
| 3 | 1355 Riverside | 321351275210 | Linked | 1355 Riverside |
| 4 | 83 Sagebrusch | None (TBD) | None | HCI Admin |

---

## 7. n8n Workflows (15 total)

| ID | Name | Status | Trigger |
|---|---|---|---|
| WF-003 | Historical Cost Queue | ACTIVE | Manual |
| WF-004 | Lessons Learned Engine | ACTIVE | Manual |
| WF-005 | SOP Registry Sync | ACTIVE | Schedule |
| WF-006 | Executive Alerts | ACTIVE | Schedule |
| WF-007 | AI Bid Leveling Engine | ACTIVE | Webhook |
| WF-011 | Site Superintendent Daily Briefing | ACTIVE | Schedule |
| Bid Receipt v5 | Bid intake processing | ACTIVE | Email/webhook |
| WF-008 | Bid Follow-Up Engine | INACTIVE | Not tested |
| WF-009 | New Job Setup | INACTIVE | Not tested |
| WF-010 | Outlook Email Router | INACTIVE | Not tested |
| ARCHIVED x3 | Superseded workflows | INACTIVE | — |
| Inbox Cleanup | Delete test emails | INACTIVE | — |

---

## 8. Data Sources Mined

### 655 South Garmisch (completed custom residential project — NOT in active projects DB)
This was the first project used to seed the historical cost and lessons learned databases.

**7 lessons learned captured:**
- Cost Control: Cost-code tracking as benchmark format
- Site Work: Shoring/underpinning as major cost driver ($1.23M budget)
- Environmental: Mine tailing removal as discrete cost code ($32K)
- General Conditions: Noise fencing overrun at 107.31% of budget
- Procurement: Casework 14-16 week lead time risk
- Mechanical: MEP incomplete drawings = CO exposure
- Drywall: Sequence depends on window/door installation

**21 historical cost records:** 17 CSI division summaries + 4 vendor proposals (TJ Concrete, Climate Control Company, NuVision Drywall, Cabinet estimate)

### HCI Vendor Registry (392 vendors)
Sourced from existing HCI contacts. 258 vendors (65.8%) have CSI divisions assigned via name pattern matching. Remainder are non-construction entities (banks, law firms, government, architects).

### 27 SOPs
Sourced from HCI's SOP library (SOP 00 master + 42-pack + SOP 2.0). Registered in the API and mapped to business processes.

---

## 9. Key API Endpoints to Know

```
GET  /api/v1/health                                    — system health
GET  /api/v1/mvp/status                                — pilot status dashboard
GET  /api/v1/mvp/exec-report                           — executive report
GET  /api/v1/sop/registry                              — all 27 SOPs
GET  /api/v1/services                                  — all 18 services
GET  /api/v1/services/historical-cost/benchmarks       — cost benchmarks
GET  /api/v1/services/historical-cost/search?q=        — cost search
GET  /api/v1/services/lessons-learned/lessons          — lessons library
GET  /api/v1/services/business-process-library/processes — 27 processes
GET  /api/v1/services/vendor-intelligence/vendors      — vendor list
GET  /api/v1/services/background-learning/summary      — discovery pipeline
GET  /api/v1/services/approval-queue/pending           — items needing approval
GET  /api/v1/projects/                                 — active projects
GET  /api/v1/services/project-brain/{project_number}   — per-project AI synthesis
```

---

## 10. AI Team Operating Rules (Non-Negotiable)

These rules are hardcoded into the system and enforced by the approval queue:

1. **HubSpot writes require Buck approval** — never auto-update
2. **Drive writes use dry-run log first** — no silent writes
3. **No external commitments** — AI cannot issue awards, contracts, or client-facing comms
4. **No production go-live without validation evidence**
5. **All write actions logged in audit trail**
6. **Human approval required for:** awards, budgets over threshold, contracts, change orders

---

## 11. What's NOT Done Yet (Open Items)

| Item | Priority | Notes |
|---|---|---|
| WF-008/009/010 staging test | P1 | Before pilot closes 2026-07-01 |
| HubSpot connected inbox | P1 | Buck action — HubSpot Settings > Email |
| ChatGPT workspace GPT | P1 | Buck action |
| 83 Sagebrusch HubSpot deal | P1 | Buck to confirm if active job |
| Qdrant vector indexing | P2 | DB content not yet indexed; search falls back to SQL |
| Houzz reconciliation | BLOCKED | Pending architecture review |
| Unversioned API route cleanup | P2 | Claude Code can execute on ACR |
| Drive Registry orphan cleanup | P2 | 3 extra HCI_Project_Registry copies |

---

## 12. File Structure Overview

```
/Users/buckadams/HCI_AI_Operating_System/
├── docker-compose.yml              ← live stack (run from here)
├── CLAUDE.md                       ← Claude Code operating rules
├── .env                            ← all credentials (gitignored)
├── IMPLEMENTATION_REPOSITORY_STATUS.md
├── IMPLEMENTATION_INVENTORY.md
├── DUPLICATE_RISK_REPORT.md
├── INTEGRATION_RECOMMENDATIONS.md
├── LIVE_PROJECT_STATE_INPUT.md
├── 03_Source_Code/
│   ├── api/                        ← FastAPI app (main.py + routers/)
│   ├── services/                   ← 18 intelligence services + platform
│   ├── integrations/               ← Drive, HubSpot, Outlook, n8n creds
│   ├── ingestion/                  ← document ingestion pipeline
│   ├── workflows/                  ← Python workflow files (WF-001–006)
│   └── tests/                      ← test suite (48/48 passing)
├── 05_Database/postgres/schema.sql ← full DB DDL
├── AI_TEAM/                        ← coordination docs (to be deprecated)
├── HCI_AI_Audit_20260626/          ← audit output files
└── infrastructure/                 ← alternate compose files + setup scripts
```

---

## 13. How to Connect ChatGPT to the Live System

**Option A — MCP Protocol (recommended)**
Connect to: `https://speculate-armband-retinal.ngrok-free.dev/mcp`
This gives ChatGPT access to all 6 MCP tools listed in Section 5.

**Option B — Direct API calls**
Base URL: `http://localhost:8000` (local only — not accessible externally without tunnel)
Header: `X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6`

**Option C — Read this document**
This document alone gives ChatGPT full context to conduct the architecture review without a live connection.

---

## 14. Current Hold Status

Per directive received 2026-06-26:
- Branch: `feature/data-architecture-document-storage`
- Commit: `b4dbed1`
- Status: **HOLDING — awaiting Architecture Review v1**
- No new features, no Sprint 1, no Houzz, no n8n additions, no refactors
- Ready to execute Architecture Change Requests (ACRs) when issued
