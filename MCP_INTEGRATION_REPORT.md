# MCP Integration Report
**Prepared by:** Claude Code — Lead Implementation Engineer
**For:** ChatGPT — Chief Architect & Architecture Review Board
**Date:** 2026-06-26
**Directive:** Architecture Review v1 — Next Assignment

---

## 1. Current MCP Resources (Full Tool Inventory)

The existing MCP server (`03_Source_Code/services/mcp_server/hci_mcp_server.py`) runs as a FastMCP server on port 8080 with a public ngrok tunnel.

**Connection:**
- Local: `http://localhost:8080`
- Public: `https://speculate-armband-retinal.ngrok-free.dev/mcp`
- Protocol: MCP streamable HTTP (JSON-RPC)
- Auth: No auth on MCP itself — auth is on the underlying FastAPI at :8000

**22 tools currently registered:**

| # | Tool | Category | Read/Write | Status |
|---|---|---|---|---|
| 1 | `ReadProjectRegistry` | Projects | Read | Working |
| 2 | `ReadVendorRegistry` | Vendors | Read | Working |
| 3 | `ReadConstructionOS` | SOPs / Rules / Lessons | Read | Working |
| 4 | `SearchDrive` | Google Drive | Read | Working |
| 5 | `ReadDriveFile` | Google Drive | Read | Working |
| 6 | `SearchHubSpotDeals` | HubSpot | Read | Working |
| 7 | `SearchCompanies` | HubSpot / Vendors | Read | Working |
| 8 | `SearchContacts` | HubSpot | Read | Working |
| 9 | `ReadBidTracker` | Bids / Sheets | Read | Working |
| 10 | `GenerateBidLevel` | Bid Leveling | Read (dry_run=true default) | Working |
| 11 | `HistoricalCostLookup` | Historical Cost | Read | Working (SQL fallback added) |
| 12 | `ProcurementStatus` | Procurement | Read | Working |
| 13 | `ScheduleStatus` | Schedule | Read | Working |
| 14 | `DraftEmail` | Outlook | Write (queued → approval) | Working |
| 15 | `CreateTask` | Task Management | Write (queued → approval) | Working |
| 16 | `UpdateRegistry` | DB Registries | Write (queued → approval) | Working |
| 17 | `AwardRecommendation` | Bid Award | Write (queued → approval) | Working |
| 18 | `ProjectMining` | Intelligence | Read | Partial — one path has 404 bug |
| 19 | `GetApprovalQueue` | Approval Queue | Read | Working |
| 20 | `CreateDriveFolder` | Google Drive | Write | Working |
| 21 | `UploadFileToDrive` | Google Drive | Write | Working |
| 22 | `ListDriveFolder` | Google Drive | Read | Working |
| 23 | `ReadSheet` | Google Sheets | Read | Working |
| 24 | `WriteSheet` | Google Sheets | Write | Working |
| 25 | `ExecutiveReport` | Reporting | Read | Working |
| 26 | `GetROISummary` | Reporting | Read | Working |

**Note:** Total is 26 tools (spec says 18 + bonus convenience tools). Tool count at runtime is 26.

---

## 2. Repository Access Capabilities

### What the MCP can currently read:

| Source | Access | Method |
|---|---|---|
| PostgreSQL (47 tables) | Full read via FastAPI | All `/api/v1/services/*` endpoints |
| Google Drive | Full search + file read | Direct Drive API with OAuth token |
| Google Sheets | Full read (any sheet ID) | Direct Sheets API with OAuth token |
| HubSpot CRM | Read (local DB cache) | `/api/v1/search` + `/api/v1/services/bid-intelligence` |
| n8n Workflows | None | Not exposed |
| File system / repo | None | Not exposed |
| Qdrant vectors | None directly | Via `/api/v1/memory/search` (not exposed as MCP tool) |

### What the MCP cannot currently read:

| Source | Gap | Impact |
|---|---|---|
| LIVE_PROJECT_STATE.md | No file system tool | Cannot give ChatGPT live state |
| CURRENT_SPRINT | No sprint data source | Cannot track sprint status |
| AUTOMATION_REGISTRY | Not a DB table | No automation inventory exposed |
| DECISION_LOG | Not exposed as MCP tool | `/api/v1/services/decision-intelligence` exists but no MCP tool wraps it |
| Repository git status | No git integration | Cannot report branch/commit state |
| Program Repository | Separate system (not local) | Cannot read Browser Claude's governance docs |
| n8n workflow state | Not exposed | Cannot report automation health |

---

## 3. Known Bug — ProjectMining Tool

`ProjectMining` at line 515 of the MCP server calls:
```
/api/v1/services/background-learning/candidates?project_id={project_id}&limit=20
```
This endpoint does not exist — returns 404. The correct path is:
```
/api/v1/services/background-learning/records?project_id={project_id}&limit=20
```
This is a one-line fix. Flagging for ACR before it affects ChatGPT's mining calls.

---

## 4. Ability to Expose LIVE_PROJECT_STATE

### Current Capability: None
The MCP has no file system access and no tool to read or write `LIVE_PROJECT_STATE.md`.

### Two Options for Implementation

**Option A — File-based tool (simplest)**
Add an MCP tool that reads `LIVE_PROJECT_STATE.md` directly from disk using Python's `open()`. The file path would be agreed upon between Program and Implementation repos (e.g., a shared path or a local copy synced by Browser Claude).

```python
@mcp.tool()
def ReadLiveProjectState() -> dict:
    """Read the current LIVE_PROJECT_STATE.md — the operational source of truth."""
    path = "/Users/buckadams/HCI_AI_Operating_System/LIVE_PROJECT_STATE.md"
    try:
        with open(path) as f:
            return {"content": f.read(), "source": path}
    except FileNotFoundError:
        return {"error": "LIVE_PROJECT_STATE.md not found — Program Repository has not synced it yet"}
```

**Option B — API-based (more robust)**
Add a `/api/v1/program/live-state` FastAPI endpoint that reads the file and returns structured JSON. MCP tool calls the API endpoint. This keeps the file path in one place.

**Recommendation: Option A first** (immediate, no ACR overhead), then promote to Option B in Sprint 1.

---

## 5. Required Enhancements to Support ChatGPT as Chief Architect

The Architecture Review v1 requires four new MCP capabilities. Here is the full specification for each.

---

### Enhancement 1 — `ReadLiveProjectState`

**Purpose:** Give ChatGPT the single operational source of truth without manual file sharing.

**Implementation:** File read tool as described in Section 4, Option A.

**Dependency:** LIVE_PROJECT_STATE.md must first be created in the Program Repository and synced/copied to a known local path.

---

### Enhancement 2 — `ReadCurrentSprint`

**Purpose:** Let ChatGPT query the current sprint status without reading the Program Repository manually.

**Options:**
- A: Read a `CURRENT_SPRINT.md` file from a shared local path (same pattern as LIVE_PROJECT_STATE)
- B: New DB table `sprint_records` with active sprint, tasks, assignees, status
- C: Read a Google Sheet maintained by Browser Claude as the sprint board

**Recommendation:** Option A (file-based) until sprint tooling is formalized. Browser Claude writes `CURRENT_SPRINT.md` to the shared path; MCP tool reads it.

```python
@mcp.tool()
def ReadCurrentSprint() -> dict:
    """Read the current sprint plan and task status from the Program Repository sync."""
    path = "/Users/buckadams/HCI_AI_Operating_System/CURRENT_SPRINT.md"
    try:
        with open(path) as f:
            return {"content": f.read(), "source": path}
    except FileNotFoundError:
        return {"error": "CURRENT_SPRINT.md not found"}
```

---

### Enhancement 3 — `ReadAutomationRegistry`

**Purpose:** Single registry of all automations across n8n, Python, and MCP — so ChatGPT can audit for duplicates and gaps.

**Current state:** No Automation Registry exists. The `connector_registry` table tracks integration connectors but not automations.

**Implementation options:**
- A: New DB table `automation_registry` with fields: name, type (n8n/python/mcp), trigger, status, owner, last_run
- B: n8n workflow list via API + Python workflow file scan, combined into one response

**Recommendation:** Option B first (no schema change), Option A when Program Repo formalizes the registry.

```python
@mcp.tool()
def ReadAutomationRegistry() -> dict:
    """Read all active automations: n8n workflows + Python workflows + MCP tools."""
    n8n = _api("GET", "/api/v1/workflows")  # lists n8n workflows via FastAPI proxy
    mcp_tools = [t.name for t in mcp._tool_manager.list_tools()]
    return {
        "n8n_workflows": n8n,
        "mcp_tools": mcp_tools,
        "python_workflows": [
            "wf001_new_project", "wf002_meeting_intelligence", "wf003_morning_brief",
            "wf004_daily_log", "wf005_lessons_learned", "wf006_inbox_review",
            "wf_pm", "wf_report", "wf_superintendent",
            "sync_drive", "sync_hubspot", "sync_houzz"
        ]
    }
```

---

### Enhancement 4 — `ReadDecisionLog`

**Purpose:** ChatGPT needs to see what architecture and implementation decisions have been logged to avoid revisiting closed decisions.

**Current state:** `decision_records` table exists in PostgreSQL with full schema. The `/api/v1/services/decision-intelligence/decisions` endpoint exists and works. It is simply not exposed as an MCP tool.

**This is the easiest enhancement — one new MCP tool wrapping an existing endpoint.**

```python
@mcp.tool()
def ReadDecisionLog(limit: int = 20, status: str = None) -> dict:
    """
    Read logged architecture and implementation decisions.
    status: 'open', 'resolved', 'pending_outcome' — None returns all
    limit: max records (default 20)
    """
    params = f"limit={limit}"
    if status:
        params += f"&status={status}"
    return _api("GET", f"/api/v1/services/decision-intelligence/decisions?{params}")
```

---

### Enhancement 5 — `ReadRepositoryStatus`

**Purpose:** Let ChatGPT check implementation repository state (branch, last commit, open items) without a manual handoff document.

**Implementation:** New MCP tool that runs git commands and reads key status files from disk.

```python
@mcp.tool()
def ReadRepositoryStatus() -> dict:
    """
    Read current implementation repository status: git branch, last commit,
    running services, and open items from IMPLEMENTATION_REPOSITORY_STATUS.md
    """
    import subprocess
    repo = "/Users/buckadams/HCI_AI_Operating_System"
    branch = subprocess.run(["git", "-C", repo, "branch", "--show-current"],
                            capture_output=True, text=True).stdout.strip()
    commit = subprocess.run(["git", "-C", repo, "log", "--oneline", "-1"],
                            capture_output=True, text=True).stdout.strip()
    services = _api("GET", "/api/v1/health")
    try:
        with open(f"{repo}/IMPLEMENTATION_REPOSITORY_STATUS.md") as f:
            status_doc = f.read()
    except Exception:
        status_doc = None
    return {
        "branch": branch,
        "last_commit": commit,
        "service_health": services,
        "status_document": status_doc,
    }
```

---

## 6. Implementation Plan for Required Enhancements

All 5 enhancements can be delivered as a single ACR. No new DB schema required. No new FastAPI routes required. Changes are confined to one file: `hci_mcp_server.py`.

| Enhancement | Effort | Dependency |
|---|---|---|
| Fix ProjectMining bug | 1 line | None |
| ReadLiveProjectState | 10 lines | LIVE_PROJECT_STATE.md file must exist |
| ReadCurrentSprint | 10 lines | CURRENT_SPRINT.md file must exist |
| ReadAutomationRegistry | 15 lines | None |
| ReadDecisionLog | 8 lines | None |
| ReadRepositoryStatus | 20 lines | None |

**Total estimated work: 1–2 hours of implementation once ACR is issued.**

**Sequencing dependency:** `ReadLiveProjectState` and `ReadCurrentSprint` require Browser Claude to first create and sync those files to a known local path. Claude Code can add the tools now and they will return a "not found" message until the files arrive — which is safe and informative.

---

## 7. Summary — Gaps vs Requirements

| Architecture Review v1 Requirement | Current State | Path to Resolution |
|---|---|---|
| MCP as primary integration layer | In place — 26 tools, public ngrok | Already done |
| Expose LIVE_PROJECT_STATE | Missing | Add `ReadLiveProjectState` tool via ACR |
| Expose CURRENT_SPRINT | Missing | Add `ReadCurrentSprint` tool via ACR |
| Expose AUTOMATION_REGISTRY | Missing | Add `ReadAutomationRegistry` tool via ACR |
| Expose DECISION_LOG | Missing tool (data exists) | Add `ReadDecisionLog` tool via ACR |
| Expose repository status | Missing | Add `ReadRepositoryStatus` tool via ACR |
| Fix ProjectMining 404 bug | Bug confirmed | 1-line fix via ACR |
| Support ChatGPT as Chief Architect | Partially ready | Above enhancements complete it |

---

## 8. Recommended ACR

**Title:** ACR-001 — MCP Enhancement: Chief Architect Integration Tools

**Scope:** Add 5 new MCP tools + 1 bug fix to `hci_mcp_server.py`. No other files modified.

**Pre-conditions:**
1. Browser Claude creates `LIVE_PROJECT_STATE.md` and `CURRENT_SPRINT.md` in Program Repository
2. Agreement on local sync path (recommend: `/Users/buckadams/HCI_AI_Operating_System/`)
3. ChatGPT approves this Integration Report

**Deliverables:**
- `ReadLiveProjectState` tool
- `ReadCurrentSprint` tool
- `ReadAutomationRegistry` tool
- `ReadDecisionLog` tool
- `ReadRepositoryStatus` tool
- `ProjectMining` 404 fix

**Not in scope:** New DB tables, new FastAPI routes, Houzz, Sprint 1 features.

---

*Claude Code is holding position on branch `feature/data-architecture-document-storage` commit `b4dbed1` pending ACR issuance.*
