# HCI AI System Audit Report v1
**Date:** 2026-06-26 | **Auditor:** Claude Code | **Directive:** HCI_AI_Master_Audit_and_Completion_Directive_v1.pdf
**Status:** Read-only audit complete. No production writes made.

---

## Executive Summary

HCI AI is substantially more built than the audit directive assumed. The API is live with 17 active services, MCP is fully deployed (not architecture-only), bid leveling is production-ready with 22/22 tests passing, and n8n has 9 active workflows. Key gaps are: HubSpot deal IDs not linked to projects, 3 projects missing from DB (349 Draw Drive, 606 Starwood Olson, 843 Cemetery Lane), a duplicate Registry Workbook in Drive, and a duplicate n8n workflow (Bid Receipt Processing v5 running twice).

---

## 1. Infrastructure Status

| Component | Status | Details |
|-----------|--------|---------|
| FastAPI (port 8000) | **GO** | Healthy, 17 services active, launchd managed |
| PostgreSQL (Docker) | **GO** | Healthy, 40 hrs uptime, 4 projects in DB |
| Redis (Docker) | **GO** | Healthy, 40 hrs uptime |
| MinIO (Docker) | **GO** | Healthy, 30 hrs uptime, ports 9000-9001 |
| Qdrant (Docker) | **WARN** | Health check UNHEALTHY but serving 13 collections functionally |
| n8n (Docker) | **GO** | Running 7 days, 15 workflows (9 active) |
| ngrok tunnel | **GO** | speculate-armband-retinal.ngrok-free.dev → port 8000 |
| MCP Server (port 8080) | **GO** | **LIVE — not architecture-only.** 26 tools, launchd managed |
| Mac Mini migration | PENDING | Expected ~Sept 2026 — will replace ngrok with static hosting |

---

## 2. Integration Status

| Integration | Status | Verified Method | Read | Write |
|-------------|--------|----------------|------|-------|
| Google Drive | **GO** | Token refresh + folder read | ✅ | Approval-gated |
| Google Sheets | **GO** | Tab read on all 3 bid trackers | ✅ | Approval-gated |
| HubSpot | **GO** | 392 vendor companies readable | ✅ | Blocked (approval) |
| Outlook / Graph API | **GO** | OAuth credential present in n8n | ✅ | Approval-gated |
| n8n | **GO** | Docker running, 15 workflows found | ✅ | N/A |
| MCP (ngrok) | **GO** | initialize + tools/list + tool call tested | ✅ | Approval-gated |

---

## 3. Project Registry Verification

| ID | Code | Name | Sheet ID | Drive Folder ID | HubSpot Deal ID |
|----|------|------|----------|-----------------|-----------------|
| 1 | 64EW | 64 Eastwood | 1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ | 1ovKLTSyZhmi4RpP5RD6sdhY0oYjwUCJv | **MISSING** |
| 2 | 101F | 101 Francis | 1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE | 1athsij_coRIngqnIe8SSHQbB51_RyZAs | **MISSING** |
| 3 | 1355R | 1355 Riverside | 1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA | 1u4DMaAul951QAZgsp5lAKyQwv2EQNHJt | **MISSING** |
| 4 | ? | Unknown 4th project | MISSING | MISSING | MISSING |

**Projects in audit scope NOT in DB:** 349 Draw Drive, 606 Starwood Olson, 843 Cemetery Lane
**Action required:** Link HubSpot deal IDs; identify 4th project; add missing projects.

---

## 4. Registry Workbook Verification

**File:** HCI_Construction_Operating_System_v2 (Google Sheets)
**CRITICAL:** TWO copies found in Drive with different IDs:
- ID: `1oCjzoab9-5kqprxiig22k_LU7YCWTPkKmcUaQwRdtqA`
- ID: `1n2Gm_x5qVGUA1c61UWdQvAcJsOhCcIlvyQy4ecT3BLA`
**Action required:** Buck must identify which is source of truth and archive the other.

**Tabs found (13):** Dashboard, SOP Registry, Alerts Log, HCI_Project_Registry, HCI_Vendor_Registry, CSI_Reference, HCI_Risk_Registry, HCI_Historical_Cost_Database, Bid_Tracker_Template, Bid_Leveling_Template, Automation_Matrix, n8n_Workflow_Map, Lists

**Row counts:** Not yet read (next pass with Buck approval to verify which workbook is current).

---

## 5. Google Drive Structure

| Folder | Status | Notes |
|--------|--------|-------|
| HCI Master (1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI) | **GO** | 13 items, well organized |
| 00 Executive | **GO** | Present |
| 01 SOPs | **GO** | Present |
| 02 Templates | **GO** | Present |
| 03 Registries | **GO** | 8 items including workbook + vendor list |
| 04 Project Intelligence | **GO** | Present |
| 05 Workflow Docs | **GO** | Present |
| 06 Systems | **GO** | Present |
| Buck AI | **GO** | 30 items: handoffs, directives, cost structures |
| Mining Inbox | **GO** | Present |
| Projects | **WARN** | Only "101 W Francis" found — other project folders missing at this level |
| Projects Folder | **WARN** | Duplicate of "Projects" — one may be legacy |
| _archive | **GO** | Present |

---

## 6. n8n Workflow Inventory

| Workflow | Status | Category |
|----------|--------|----------|
| Bid Receipt Processing v5 | **ACTIVE** | GO - Production |
| Bid Receipt Processing v5 | **INACTIVE** | **DUPLICATE — same name, different ID. Investigate.** |
| WF-007 AI Bid Leveling Engine | **ACTIVE** | GO - Production |
| WF-003 Historical Cost Queue | **ACTIVE** | GO - Production |
| WF-004 Lessons Learned Engine | **ACTIVE** | GO - Production |
| WF-005 SOP Registry Sync | **ACTIVE** | GO - Production |
| WF-006 Executive Alerts | **ACTIVE** | GO - Production |
| WF-011 Site Superintendent Daily Briefing | **ACTIVE** | GO - Production |
| ChatGPT Chrome Bridge | **ACTIVE** | REVIEW — unclear purpose, verify still needed |
| TMP-cl-84994d | **ACTIVE** | REVIEW — temp workflow name, verify or retire |
| WF-008 Bid Follow-Up Engine | **INACTIVE** | Staging Only |
| WF-009 New Job Setup | **INACTIVE** | Staging Only |
| WF-010 Outlook Email Router | **INACTIVE** | Staging Only |
| ARCHIVED — Bid Leveling (merged into WF-007) | **INACTIVE** | RETIRE |
| Inbox Cleanup — Delete Test Emails | **INACTIVE** | RETIRE (dangerous if activated) |

**n8n API access:** API key not configured in .env — workflows cannot be queried via REST API. Must use Docker exec or n8n UI.

---

## 7. API Service Endpoint Status

| Service | Endpoint | Status | Data |
|---------|----------|--------|------|
| Executive Report | GET /api/v1/mvp/exec-report | **GO** | 3 projects, 6 risks |
| Bid Leveling | /api/v1/services/bid-leveling/* | **GO** | 3 projects, all divisions |
| Risk Intelligence | /api/v1/services/risk-intelligence/* | **GO** | Active |
| Procurement | /api/v1/services/procurement/* | **GO** | Active |
| Lessons Learned | /api/v1/services/lessons-learned/* | **GO** | 0 rows (empty) |
| Operating Rules | /api/v1/services/operating-rules/* | **GO** | 12 rules |
| Vendor Intelligence | /api/v1/services/vendor-intelligence/* | **GO** | 392 vendors |
| Approval Queue | /api/v1/services/approval-queue/* | **GO** | 9 pending items |
| Schedule Intelligence | /api/v1/services/schedule-intelligence/* | **GO** | Active |
| Historical Cost | /api/v1/services/historical-cost/search | **GO** | path /lookup 404, /search works |
| Background Learning | /api/v1/services/background-learning/ | **GO** | path /candidates 404 |
| KPI Intelligence | /api/v1/services/kpi-intelligence/ | **GO** | path /kpis 404 |
| Business Process Library | /api/v1/services/business-process-library/* | **GO** | 0 rows (empty) |
| Connector Registry | /api/v1/services/connector-registry/* | **GO** | 18 connectors, all read-only |
| SOP | /api/v1/sop/* | **NO-GO** | All paths 404 — route missing from main.py or wrong prefix |
| MCP Proxy | /mcp/ → port 8080 | **GO** | 26 tools via ngrok |

---

## 8. MCP Status (Correction for GBT)

GBT's directive stated MCP as "Architecture only — confirm not deployed." This is incorrect.

**MCP is FULLY DEPLOYED:**
- Server: FastMCP running via launchd, port 8080
- Proxy: /mcp/ route on main API (port 8000) → proxied via ngrok
- URL: https://speculate-armband-retinal.ngrok-free.dev/mcp/
- Auth: X-API-Key header
- Tools: 26 tools (18 spec + 8 convenience)
- Write tools: ALL approval-gated (DraftEmail, AwardRecommendation, UpdateRegistry require queue approval)
- Tested: initialize ✅, tools/list ✅, ExecutiveReport tool call ✅, ReadBidTracker tool call ✅

---

## 9. Duplicates Found

| Item | Duplicate Type | Recommendation |
|------|---------------|----------------|
| HCI_Construction_Operating_System_v2 | Two Google Sheets with same name, different IDs | Buck identifies source of truth; archive other |
| Bid Receipt Processing v5 (n8n) | Two workflows, same name, one ON one OFF | Investigate; deactivate/delete the OFF copy |
| "Projects" + "Projects Folder" in HCI Master | Two Drive folders with similar purpose | Confirm which is canonical; archive other |
| ARCHIVED — Bid Leveling (n8n) | Superseded by WF-007 | Retire |

---

## 10. Go/No-Go Summary

| Area | Status |
|------|--------|
| Core API + Infrastructure | **GO** |
| Google Drive + Sheets | **GO** |
| HubSpot (read) | **GO** |
| Bid Leveling Service | **GO** (22/22 tests pass) |
| MCP Server | **GO** (live, tested) |
| n8n (active workflows) | **GO** (with duplicate caveat) |
| SOP endpoint | **NO-GO** (path broken) |
| Project Registry (HubSpot IDs) | **NO-GO** (missing deal IDs) |
| Projects 349DD, 606SO, 843CL | **NO-GO** (not in system) |
| Registry Workbook (duplicate) | **NO-GO** (must resolve) |
| Lessons Learned (data) | **NO-GO** (0 rows) |
| Business Process Library (data) | **NO-GO** (0 rows) |
| WF-008/009/010 | **STAGING ONLY** |
| HubSpot write-back | **BLOCKED** (by design, approval gate) |

---

*Audit conducted 2026-06-26. No writes made. All data read-only. Next action: Buck reviews this report and approves completion backlog.*
