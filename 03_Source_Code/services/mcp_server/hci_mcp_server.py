"""
HCI AI MCP Server — Full Specification Implementation
Exposes all 18 tools from the HCI AI MCP Master Engineering Specification v1.0.

Mounted on main FastAPI app at /mcp (accessible via ngrok).
Also runs standalone on port 8080 for local MCP clients.

ChatGPT connection:
  URL:  https://speculate-armband-retinal.ngrok-free.dev/mcp
  Auth: X-API-Key header → value from HCI_API_KEY in .env
"""
import sys, os, json, ssl, urllib.parse, urllib.request, urllib.error, argparse, base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bid_leveling"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "approval_queue"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

import certifi
from mcp.server.fastmcp import FastMCP

HCI_API  = "http://localhost:8000"
HCI_KEY  = os.environ["HCI_API_KEY"]
SSL_CTX  = ssl.create_default_context(cafile=certifi.where())

mcp = FastMCP(
    "HCI AI Operating System",
    instructions=(
        "You are connected to the HCI AI Operating System for Hendrickson Construction. "
        "You have full access to: bid tracking (all 3 projects, all divisions), vendor registry, "
        "HubSpot (companies, contacts, deals), Google Drive (search, read, create, upload), "
        "Google Sheets (read/write), project intelligence, SOPs, historical cost database, "
        "procurement status, schedule status, and the approval queue.\n\n"
        "APPROVAL RULES — automatic (no approval needed): search, read, summaries, analysis, "
        "recommendations. ALWAYS requires approval: awards, budgets, contracts, client emails, "
        "change orders, registry writes, CRM updates.\n\n"
        "Always start with ReadProjectRegistry or GetProjectBidData to get context before "
        "making recommendations. Default dry_run=true for all workflow runs."
    ),
)


def _api(method: str, path: str, body: dict = None) -> dict:
    url  = f"{HCI_API}{path}"
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(
        url, data=data, method=method,
        headers={"X-API-Key": HCI_KEY, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode()[:500]}
    except Exception as e:
        return {"error": str(e)}


# ── 1. ReadProjectRegistry ─────────────────────────────────────────────────────

@mcp.tool()
def ReadProjectRegistry(project_id: int = None, project_code: str = None) -> dict:
    """
    Read full project context from the HCI Construction OS registry.
    Returns: project info, recent bids, HubSpot deals, daily logs, schedule variance, open risks.
    project_id: 1=64 Eastwood, 2=101 Francis, 3=1355 Riverside
    project_code: '64EW', '101F', or '1355R'
    If neither provided, returns list of all projects.
    """
    if project_code:
        return _api("POST", f"/api/v1/mvp/projects/{project_code}/init", {})
    if project_id:
        code_map = {1: "64EW", 2: "101F", 3: "1355R"}
        code = code_map.get(project_id)
        if code:
            return _api("POST", f"/api/v1/mvp/projects/{code}/init", {})
    return _api("GET", "/api/v1/projects")


# ── 2. ReadVendorRegistry ──────────────────────────────────────────────────────

@mcp.tool()
def ReadVendorRegistry(search: str = None, csi_division: str = None,
                        limit: int = 50) -> dict:
    """
    Read the HCI Vendor Registry. Search by name, trade, or filter by CSI division.
    Returns vendor records including trade, contact info, performance data, and HubSpot IDs.
    search: keyword to search vendor names/trades (e.g. 'electrical', 'concrete')
    csi_division: filter by CSI division number e.g. '16' for electrical
    limit: max results (default 50)
    """
    if search:
        return _api("GET", f"/api/v1/search?q={urllib.parse.quote(search)}&type=vendor&limit={limit}")
    params = f"limit={limit}"
    if csi_division:
        params += f"&csi_division={csi_division}"
    return _api("GET", f"/api/v1/vendors?{params}")


# ── 3. ReadConstructionOS ──────────────────────────────────────────────────────

@mcp.tool()
def ReadConstructionOS(category: str = "all") -> dict:
    """
    Read the HCI Construction Operating System — SOPs, operating rules, lessons learned,
    business processes, and KPI standards.
    category: 'sops' | 'operating_rules' | 'lessons_learned' | 'business_processes' | 'all'
    """
    if category == "sops" or category == "all":
        sops = _api("GET", "/api/v1/sop/registry")
    else:
        sops = {}
    if category == "operating_rules" or category == "all":
        rules = _api("GET", "/api/v1/services/operating-rules/rules")
    else:
        rules = {}
    if category == "lessons_learned" or category == "all":
        lessons = _api("GET", "/api/v1/services/lessons-learned/lessons?limit=50")
    else:
        lessons = {}
    if category == "business_processes" or category == "all":
        processes = _api("GET", "/api/v1/services/business-process-library/processes?limit=50")
    else:
        processes = {}
    return {
        "sops":               sops    if category in ("sops",             "all") else None,
        "operating_rules":    rules   if category in ("operating_rules",   "all") else None,
        "lessons_learned":    lessons if category in ("lessons_learned",    "all") else None,
        "business_processes": processes if category in ("business_processes","all") else None,
    }


# ── 4. SearchDrive ─────────────────────────────────────────────────────────────

@mcp.tool()
def SearchDrive(query: str, folder_id: str = None, file_type: str = None) -> dict:
    """
    Search Google Drive for files by name/keyword.
    query: search string (e.g. 'bid leveling', 'structural drawings', 'schedule')
    folder_id: restrict search to a specific folder (optional)
    file_type: filter by type — 'pdf', 'xlsx', 'folder', 'doc', 'drawing' (optional)
    Known folder IDs:
      HCI Master: 1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI
      64 Eastwood: 1ovKLTSyZhmi4RpP5RD6sdhY0oYjwUCJv
      101 Francis: 1athsij_coRIngqnIe8SSHQbB51_RyZAs
      1355 Riverside: 1u4DMaAul951QAZgsp5lAKyQwv2EQNHJt
    """
    from credentials import get_google_token
    token = get_google_token("drive")

    q_parts = [f"name contains '{query}' or fullText contains '{query}'"]
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")
    if file_type:
        mime_map = {
            "pdf":    "application/pdf",
            "xlsx":   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "folder": "application/vnd.google-apps.folder",
            "doc":    "application/vnd.google-apps.document",
            "sheet":  "application/vnd.google-apps.spreadsheet",
        }
        if file_type in mime_map:
            q_parts.append(f"mimeType='{mime_map[file_type]}'")

    q_parts.append("trashed=false")
    params = urllib.parse.urlencode({
        "q":       " and ".join(q_parts),
        "fields":  "files(id,name,mimeType,modifiedTime,size,parents,webViewLink)",
        "pageSize": 30,
    })
    url = f"https://www.googleapis.com/drive/v3/files?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            data = json.loads(r.read())
            return {"files": data.get("files", []), "count": len(data.get("files", []))}
    except Exception as e:
        return {"error": str(e)}


# ── 5. ReadDriveFile ───────────────────────────────────────────────────────────

@mcp.tool()
def ReadDriveFile(file_id: str, as_text: bool = True) -> dict:
    """
    Read file content from Google Drive.
    file_id: the Drive file ID.
    as_text: if True, returns text content (for text, CSV, exported Google Docs).
             if False, returns base64-encoded binary content (for xlsx, pdf, etc.)
    Google Docs/Sheets are exported as text/plain or csv automatically.
    """
    from credentials import get_google_token
    token = get_google_token("drive")

    # First get metadata to determine mime type
    meta_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=name,mimeType,size"
    meta_req = urllib.request.Request(meta_url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(meta_req, context=SSL_CTX) as r:
            meta = json.loads(r.read())
    except Exception as e:
        return {"error": f"Metadata error: {e}"}

    mime = meta.get("mimeType", "")
    name = meta.get("name", "")

    # Google Workspace files need export
    export_map = {
        "application/vnd.google-apps.document":     ("text/plain",               ".txt"),
        "application/vnd.google-apps.spreadsheet":  ("text/csv",                 ".csv"),
        "application/vnd.google-apps.presentation": ("text/plain",               ".txt"),
    }
    if mime in export_map:
        export_mime, _ = export_map[mime]
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType={urllib.parse.quote(export_mime)}"
    else:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            content = r.read()
        if as_text:
            try:
                text = content.decode("utf-8", errors="replace")
                return {"file_id": file_id, "name": name, "mime_type": mime,
                        "content": text[:50000], "truncated": len(text) > 50000}
            except Exception:
                return {"file_id": file_id, "name": name, "mime_type": mime,
                        "content_b64": base64.b64encode(content[:100000]).decode(),
                        "note": "binary file — returned as base64"}
        else:
            return {"file_id": file_id, "name": name, "mime_type": mime,
                    "content_b64": base64.b64encode(content[:200000]).decode()}
    except Exception as e:
        return {"error": str(e)}


# ── 6. SearchHubSpotDeals ──────────────────────────────────────────────────────

@mcp.tool()
def SearchHubSpotDeals(search: str = None, project_name: str = None,
                        stage: str = None, limit: int = 50) -> dict:
    """
    Search HubSpot deals from the HCI local database.
    search: keyword to search deal names (e.g. '101 Francis', 'electrical', 'Division 16')
    project_name: filter by project (e.g. '101 Francis', '1355 Riverside')
    stage: filter by stage name (partial match)
    limit: max results (default 50)
    """
    params = f"limit={limit}"
    if search:
        params += f"&search={urllib.parse.quote(search)}"
    return _api("GET", f"/api/v1/services/bid-intelligence/deals?{params}")


# ── 7. SearchCompanies ─────────────────────────────────────────────────────────

@mcp.tool()
def SearchCompanies(search: str = None, trade: str = None, limit: int = 50) -> dict:
    """
    Search HubSpot companies (vendors/subcontractors) from the HCI database.
    search: keyword to search company names or descriptions
    trade: filter by trade/CSI division (e.g. 'electrical', 'concrete', 'mechanical')
    limit: max results (default 50)
    """
    q = search or trade or ""
    if q:
        return _api("GET", f"/api/v1/search?q={urllib.parse.quote(q)}&type=company&limit={limit}")
    return _api("GET", f"/api/v1/vendors?limit={limit}")


# ── 8. SearchContacts ──────────────────────────────────────────────────────────

@mcp.tool()
def SearchContacts(search: str = None, company: str = None, limit: int = 50) -> dict:
    """
    Search HubSpot contacts (subcontractor reps, vendors, owners) from the HCI database.
    search: name or email keyword
    company: filter by company name
    limit: max results (default 50)
    """
    q = search or company or ""
    if q:
        return _api("GET", f"/api/v1/search?q={urllib.parse.quote(q)}&type=contact&limit={limit}")
    return _api("GET", f"/api/v1/search?q=&type=contact&limit={limit}")


# ── 9. ReadBidTracker ──────────────────────────────────────────────────────────

@mcp.tool()
def ReadBidTracker(project_id: int) -> dict:
    """
    Read the complete bid tracking data for a project directly from Google Sheets.
    Returns bid_tracking (all vendors/bids by division), division_summary (leveling status,
    risk, recommendations), and package_detail (per-trade breakdown).
    project_id: 1=64 Eastwood, 2=101 Francis, 3=1355 Riverside
    """
    return _api("GET", f"/api/v1/services/bid-leveling/projects/{project_id}/data")


# ── 10. GenerateBidLevel ───────────────────────────────────────────────────────

@mcp.tool()
def GenerateBidLevel(project_id: int, dry_run: bool = True,
                      divisions: list = None) -> dict:
    """
    Generate bid leveling analysis and Excel files for a project.
    dry_run=True (default): analyze all divisions and return what would be generated — no writes.
    dry_run=False: generate per-division Excel files and queue Drive uploads for Buck's approval.
    divisions: optional list of CSI division numbers to process, e.g. ['15', '16']. None = all.
    project_id: 1=64 Eastwood, 2=101 Francis, 3=1355 Riverside
    """
    body = {"dry_run": dry_run}
    if divisions:
        body["divisions"] = divisions
    return _api("POST", f"/api/v1/services/bid-leveling/projects/{project_id}/run", body)


# ── 11. HistoricalCostLookup ───────────────────────────────────────────────────

@mcp.tool()
def HistoricalCostLookup(trade: str = None, csi_division: str = None,
                          project_type: str = None) -> dict:
    """
    Look up historical cost data from the HCI Historical Cost Database.
    trade: trade description (e.g. 'framing', 'electrical', 'mechanical')
    csi_division: CSI division number (e.g. '06', '15', '16')
    project_type: filter by project type (e.g. 'residential', 'commercial')
    Returns cost benchmarks and historical project data.
    """
    terms = [t for t in [trade, csi_division, project_type] if t]
    q = urllib.parse.quote(" ".join(terms)) if terms else "construction"
    return _api("GET", f"/api/v1/services/historical-cost/search?q={q}")


# ── 12. ProcurementStatus ──────────────────────────────────────────────────────

@mcp.tool()
def ProcurementStatus(project_id: int = None) -> dict:
    """
    Get procurement status for a project or all projects.
    Returns open procurement items, long-lead status, package awards, and pending decisions.
    project_id: 1=64 Eastwood, 2=101 Francis, 3=1355 Riverside. None = all projects.
    """
    if project_id:
        return _api("GET", f"/api/v1/services/procurement/status?project_id={project_id}")
    return _api("GET", "/api/v1/services/procurement/status")


# ── 13. ScheduleStatus ────────────────────────────────────────────────────────

@mcp.tool()
def ScheduleStatus(project_code: str = None) -> dict:
    """
    Get schedule status and variance intelligence for a project.
    Returns variance analysis, decision points, risk level, and recommended notifications.
    project_code: '64EW', '101F', or '1355R'. If None, returns executive report for all.
    """
    if project_code:
        return _api("GET", f"/api/v1/mvp/projects/{project_code}/schedule-status")
    return _api("GET", "/api/v1/mvp/exec-report")


# ── 14. DraftEmail ────────────────────────────────────────────────────────────

@mcp.tool()
def DraftEmail(to: str, subject: str, body: str, project_id: int = None,
                cc: str = None) -> dict:
    """
    APPROVAL REQUIRED — Drafts an email and queues it for Buck's review before sending.
    The email will NOT be sent automatically. Buck must review and approve in the queue.
    to: recipient email address(es)
    subject: email subject
    body: email body text
    project_id: associated project (optional)
    cc: CC email addresses (optional)
    """
    return _api("POST", "/api/v1/services/approval-queue/enqueue", {
        "workflow":     "draft_email",
        "action_type":  "send_email",
        "target_system": "outlook",
        "target_id":    to,
        "target_description": f"Email to {to}: {subject}",
        "proposed_payload": {
            "to": to, "cc": cc, "subject": subject, "body": body,
        },
        "reason": f"GBT drafted email: {subject}",
        "project_id": project_id,
        "rollback_path": "Delete draft — email was never sent",
    })


# ── 15. CreateTask ────────────────────────────────────────────────────────────

@mcp.tool()
def CreateTask(title: str, description: str, project_id: int = None,
                priority: str = "normal", assigned_to: str = "Buck Adams") -> dict:
    """
    Creates a task and queues it for Buck's awareness and action.
    Tasks are logged in the approval queue as informational items.
    title: task title
    description: what needs to be done and why
    project_id: associated project (optional)
    priority: 'low', 'normal', 'high', 'urgent'
    assigned_to: who should action this (default: Buck Adams)
    """
    return _api("POST", "/api/v1/services/approval-queue/enqueue", {
        "workflow":     "create_task",
        "action_type":  "task",
        "target_system": "hci_os",
        "target_id":    title,
        "target_description": f"Task: {title}",
        "proposed_payload": {
            "title": title, "description": description,
            "assigned_to": assigned_to, "priority": priority,
        },
        "reason": description,
        "project_id": project_id,
        "priority": priority,
        "rollback_path": "Remove task from queue",
    })


# ── 16. UpdateRegistry (approval required) ────────────────────────────────────

@mcp.tool()
def UpdateRegistry(registry_type: str, record_id: str, updates: dict,
                    project_id: int = None, reason: str = "") -> dict:
    """
    APPROVAL REQUIRED — Queues a registry update for Buck's review before execution.
    The update will NOT be applied until Buck approves.
    registry_type: 'vendor', 'project', 'historical_cost', 'lessons_learned', 'procurement', 'bid_tracker'
    record_id: ID or identifier of the record to update
    updates: dict of field → new_value changes
    reason: why this update is needed
    """
    return _api("POST", "/api/v1/services/approval-queue/enqueue", {
        "workflow":     "update_registry",
        "action_type":  "registry_write",
        "target_system": registry_type,
        "target_id":    str(record_id),
        "target_description": f"Update {registry_type} record {record_id}",
        "proposed_payload": {"registry": registry_type, "record_id": record_id, "updates": updates},
        "reason": reason or f"GBT requested update to {registry_type} record {record_id}",
        "project_id": project_id,
        "rollback_path": f"Revert {registry_type} record {record_id} to previous values",
    })


# ── 17. AwardRecommendation (approval required) ────────────────────────────────

@mcp.tool()
def AwardRecommendation(project_id: int, csi_division: str, recommended_vendor: str,
                          bid_amount: str, basis: str, conditions: str = "") -> dict:
    """
    APPROVAL REQUIRED — Generates a bid award recommendation and queues for Buck's approval.
    This does NOT award anything. Buck must review analysis and explicitly approve.
    project_id: 1=64 Eastwood, 2=101 Francis, 3=1355 Riverside
    csi_division: CSI division number being awarded (e.g. '16')
    recommended_vendor: name of recommended subcontractor
    bid_amount: their bid amount (e.g. '$168,000')
    basis: why they are recommended (scope, value, qualifications, etc.)
    conditions: any conditions or clarifications required before award
    """
    project_names = {1: "64 Eastwood", 2: "101 Francis", 3: "1355 Riverside"}
    project_name  = project_names.get(project_id, f"Project {project_id}")
    return _api("POST", "/api/v1/services/approval-queue/enqueue", {
        "workflow":     "award_recommendation",
        "action_type":  "bid_award",
        "target_system": "hci_os",
        "target_id":    f"project_{project_id}_div_{csi_division}",
        "target_description": f"{project_name} Division {csi_division} — Award to {recommended_vendor}",
        "proposed_payload": {
            "project_id":    project_id,
            "project":       project_name,
            "csi_division":  csi_division,
            "vendor":        recommended_vendor,
            "bid_amount":    bid_amount,
            "basis":         basis,
            "conditions":    conditions,
        },
        "reason": f"GBT recommendation: award {project_name} Div {csi_division} to {recommended_vendor} at {bid_amount}. Basis: {basis}",
        "project_id": project_id,
        "priority": "high",
        "rollback_path": "Reject award recommendation — no contract issued",
    })


# ── 18. ProjectMining ──────────────────────────────────────────────────────────

@mcp.tool()
def ProjectMining(project_id: int, source: str = "all") -> dict:
    """
    Mine project intelligence from all connected sources: Drive documents, HubSpot emails,
    daily logs, schedule variance, bids, and background learning pipeline.
    Returns synthesized intelligence candidates and key insights.
    project_id: 1=64 Eastwood, 2=101 Francis, 3=1355 Riverside
    source: 'drive' | 'hubspot' | 'daily_logs' | 'schedule' | 'bids' | 'all'
    """
    results = {}
    code_map = {1: "64EW", 2: "101F", 3: "1355R"}
    code = code_map.get(project_id, str(project_id))

    if source in ("all", "bids"):
        results["bids"] = _api("GET", f"/api/v1/services/bid-leveling/projects/{project_id}/data")
    if source in ("all", "schedule"):
        results["schedule"] = _api("GET", f"/api/v1/mvp/projects/{code}/schedule-status")
    if source in ("all", "daily_logs"):
        results["recent_activity"] = _api("GET", f"/api/v1/mvp/projects/{code}/pm-review")
    if source in ("all", "hubspot"):
        results["hubspot_deals"] = _api("GET", f"/api/v1/services/bid-intelligence/deals?project_code={code}&limit=20")
    if source in ("all", "drive"):
        results["background_learning"] = _api("GET", f"/api/v1/services/background-learning/records?project_id={project_id}&limit=20")

    return {
        "project_id": project_id,
        "project_code": code,
        "source": source,
        "intelligence": results,
    }


# ── Bonus convenience tools ────────────────────────────────────────────────────

@mcp.tool()
def GetApprovalQueue(status: str = "pending") -> dict:
    """
    Get items in the approval queue waiting for Buck's review.
    status: 'pending' (waiting for approval), 'approved', 'executed', 'rejected'
    All write actions (emails, awards, registry updates, Drive uploads) queue here.
    """
    return _api("GET", f"/api/v1/services/approval-queue/items?status={status}")


@mcp.tool()
def CreateDriveFolder(parent_folder_id: str, folder_name: str) -> dict:
    """
    Create a folder in Google Drive. Returns folder_id. Safe to call — returns existing if already exists.
    parent_folder_id: where to create the folder.
    folder_name: name for the new folder.
    Known parent IDs: 64EW=1ovKLTSyZhmi4RpP5RD6sdhY0oYjwUCJv, 101F=1athsij_coRIngqnIe8SSHQbB51_RyZAs, 1355R=1u4DMaAul951QAZgsp5lAKyQwv2EQNHJt
    """
    return _api("POST", "/api/v1/services/bid-leveling/drive/create-folder",
                {"parent_folder_id": parent_folder_id, "folder_name": folder_name})


@mcp.tool()
def UploadFileToDrive(folder_id: str, filename: str, content_b64: str,
                       mime_type: str = "application/octet-stream") -> dict:
    """
    Upload a file to Google Drive. Creates or replaces a file with the same name.
    folder_id: Drive folder ID where the file should go.
    filename: file name (e.g. 'report.xlsx', 'bid_summary.pdf').
    content_b64: base64-encoded file content.
    mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' for xlsx,
               'application/pdf' for pdf, 'text/plain' for txt, 'application/octet-stream' default.
    """
    return _api("POST", "/api/v1/services/bid-leveling/drive/upload-file",
                {"folder_id": folder_id, "filename": filename,
                 "content_b64": content_b64, "mime_type": mime_type})


@mcp.tool()
def ListDriveFolder(folder_id: str) -> dict:
    """
    List contents of a Google Drive folder — files and subfolders with IDs, names, types.
    Known top-level IDs: HCI Master=1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI,
    64EW=1ovKLTSyZhmi4RpP5RD6sdhY0oYjwUCJv, 101F=1athsij_coRIngqnIe8SSHQbB51_RyZAs,
    1355R=1u4DMaAul951QAZgsp5lAKyQwv2EQNHJt, 101F 00_Bids=1YJatvTnK0-vxiHmI0FxVE8e9jUubVcef
    """
    return _api("GET", f"/api/v1/services/bid-leveling/drive/list/{folder_id}")


@mcp.tool()
def ReadSheet(sheet_id: str, range_name: str = "Sheet1!A1:Z200") -> dict:
    """
    Read data from any Google Sheets range. Returns rows as list of lists.
    sheet_id: Google Sheets file ID.
    range_name: e.g. 'Sheet1!A1:Z200', 'HCI 16 Div Summary!A1:H50', 'Bid Tracking!A1:J100'
    Known sheet IDs: 64EW=1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ,
    101F=1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE,
    1355R=1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA
    """
    params = f"sheet_id={urllib.parse.quote(sheet_id)}&range_name={urllib.parse.quote(range_name)}"
    return _api("GET", f"/api/v1/services/bid-leveling/sheets/read?{params}")


@mcp.tool()
def WriteSheet(sheet_id: str, range_name: str, values: list) -> dict:
    """
    Write values to a Google Sheets range. Takes effect immediately — confirm intent before calling.
    sheet_id: Google Sheets file ID.
    range_name: e.g. 'Sheet1!A5' or 'Bid Tracking!F12:F15'
    values: list of rows, each row a list of cell values.
    Example: values=[['$50,000', 'Received', '2026-06-26']]
    """
    return _api("POST", "/api/v1/services/bid-leveling/sheets/write",
                {"sheet_id": sheet_id, "range_name": range_name, "values": values})


@mcp.tool()
def ExecutiveReport() -> dict:
    """
    Get the cross-project executive morning briefing.
    Returns budget health, schedule health, active risks, approval queue count,
    and key decisions needed across all 3 pilot projects (64EW, 101F, 1355R).
    """
    return _api("GET", "/api/v1/mvp/exec-report")


@mcp.tool()
def GetROISummary() -> dict:
    """Get total ROI summary — minutes saved, workflows run, and per-workflow breakdown."""
    return _api("GET", "/api/v1/mvp/roi")


# ── ACR-001: Chief Architect Integration Tools ────────────────────────────────

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..")

@mcp.tool()
def ReadLiveProjectState() -> dict:
    """
    Read LIVE_PROJECT_STATE.md — the single operational source of truth for the HCI AI OS.
    Created and maintained by Browser Claude in the Program Repository, synced to the
    implementation repo root. Returns 'not_found' if Browser Claude has not yet synced it.
    """
    path = os.path.join(REPO_ROOT, "LIVE_PROJECT_STATE.md")
    try:
        with open(path) as f:
            return {"content": f.read(), "source": path, "status": "found"}
    except FileNotFoundError:
        return {
            "status": "not_found",
            "message": "LIVE_PROJECT_STATE.md does not exist yet. Browser Claude must create and sync it.",
            "expected_path": path,
        }


@mcp.tool()
def ReadCurrentSprint() -> dict:
    """
    Read CURRENT_SPRINT.md — active sprint plan, task assignments, and status.
    Created and maintained by Browser Claude / ChatGPT in the Program Repository.
    Returns 'not_found' if not yet synced.
    """
    path = os.path.join(REPO_ROOT, "CURRENT_SPRINT.md")
    try:
        with open(path) as f:
            return {"content": f.read(), "source": path, "status": "found"}
    except FileNotFoundError:
        return {
            "status": "not_found",
            "message": "CURRENT_SPRINT.md does not exist yet. Issue ACR-001 completion triggers this.",
            "expected_path": path,
        }


@mcp.tool()
def ReadAutomationRegistry() -> dict:
    """
    Read the full automation registry: all n8n workflows, Python workflow files, and MCP tools.
    Provides ChatGPT visibility into every automation in the system to detect duplicates and gaps.
    """
    import subprocess
    n8n_workflows = _api("GET", "/api/v1/workflows")
    mcp_tools = sorted([t.name for t in mcp._tool_manager.list_tools()])
    python_workflows = [
        {"name": "wf001_new_project",          "trigger": "API / manual", "status": "active"},
        {"name": "wf002_meeting_intelligence",  "trigger": "API / manual", "status": "active"},
        {"name": "wf003_morning_brief",         "trigger": "API / schedule", "status": "active"},
        {"name": "wf004_daily_log",             "trigger": "API / manual", "status": "active"},
        {"name": "wf005_lessons_learned",       "trigger": "API / manual", "status": "active"},
        {"name": "wf006_inbox_review",          "trigger": "API / manual", "status": "active"},
        {"name": "wf_pm",                       "trigger": "API / schedule", "status": "active"},
        {"name": "wf_report",                   "trigger": "API / schedule", "status": "active"},
        {"name": "wf_superintendent",           "trigger": "API / manual", "status": "active"},
        {"name": "sync_drive",                  "trigger": "scheduled / manual", "status": "active"},
        {"name": "sync_hubspot",                "trigger": "scheduled / manual", "status": "active"},
        {"name": "sync_houzz",                  "trigger": "scheduled / manual", "status": "hold — pending architecture review"},
    ]
    return {
        "n8n_workflows": n8n_workflows,
        "python_workflows": python_workflows,
        "mcp_tools": mcp_tools,
        "mcp_tool_count": len(mcp_tools),
    }


@mcp.tool()
def ReadDecisionLog(limit: int = 20, status: str = None) -> dict:
    """
    Read the architecture and implementation decision log.
    Returns logged decisions with outcomes — use to avoid revisiting closed decisions.
    status: 'open' | 'resolved' | 'pending_outcome' — omit for all
    limit: max records (default 20)
    """
    params = f"limit={limit}"
    if status:
        params += f"&status={status}"
    return _api("GET", f"/api/v1/services/decision-intelligence/decisions?{params}")


@mcp.tool()
def ReadRepositoryStatus() -> dict:
    """
    Read current implementation repository status: git branch, last commit, service health,
    and the IMPLEMENTATION_REPOSITORY_STATUS.md document.
    Use this to verify what is built, what is running, and what is on hold.
    """
    import subprocess
    repo = REPO_ROOT

    branch = subprocess.run(
        ["git", "-C", repo, "branch", "--show-current"],
        capture_output=True, text=True
    ).stdout.strip()

    last_commit = subprocess.run(
        ["git", "-C", repo, "log", "--oneline", "-3"],
        capture_output=True, text=True
    ).stdout.strip()

    health = _api("GET", "/api/v1/health")

    try:
        with open(os.path.join(repo, "IMPLEMENTATION_REPOSITORY_STATUS.md")) as f:
            status_doc = f.read()
    except Exception:
        status_doc = "IMPLEMENTATION_REPOSITORY_STATUS.md not found"

    return {
        "branch": branch,
        "last_3_commits": last_commit,
        "service_health": health,
        "hold_status": "Holding on ACR-001 — awaiting Sprint 1 approval criteria",
        "status_document": status_doc,
    }


# ── ACR-002: GetProjectState ──────────────────────────────────────────────────

@mcp.tool()
def GetProjectState() -> dict:
    """
    ACR-002: Live system snapshot for architecture review sessions.
    Fetches real-time data from all key services and bundles the LIVE_PROJECT_STATE.md document.
    Use this to open any architecture review, sprint planning, or status check session.

    Returns: system health, all projects, MVP status, ROI, pending approvals,
             background learning state, and the full LIVE_PROJECT_STATE.md content.
    Public HTTP equivalent: GET /project-state (no auth required).
    Drive mirror: https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view
    """
    health   = _api("GET", "/api/v1/health")
    projects = _api("GET", "/api/v1/projects")
    mvp      = _api("GET", "/api/v1/mvp/status")
    roi      = _api("GET", "/api/v1/mvp/roi-summary?project_filter=all")
    aq       = _api("GET", "/api/v1/services/approval-queue/items?status=pending&limit=10")
    bl       = _api("GET", "/api/v1/services/background-learning/summary")

    try:
        with open(os.path.join(REPO_ROOT, "LIVE_PROJECT_STATE.md")) as f:
            live_state_doc = f.read()
    except Exception:
        live_state_doc = "LIVE_PROJECT_STATE.md not found — re-upload needed"

    return {
        "system_health":          health,
        "projects":               projects,
        "mvp_status":             mvp,
        "roi":                    roi,
        "approval_queue_pending": aq,
        "background_learning":    bl,
        "live_state_document":    live_state_doc,
        "public_endpoint":        "https://speculate-armband-retinal.ngrok-free.dev/project-state",
        "drive_url":              "https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view",
    }


# ── Entry point ────────────────────────────────────────────────────────────────

def get_asgi_app():
    """
    Returns ASGI app for mounting on main FastAPI at /mcp.
    Uses streamable_http_path='/' so the MCP route lives at '/' in the sub-app,
    matching what FastAPI delivers after stripping the '/mcp' mount prefix.
    host='0.0.0.0' disables FastMCP's DNS rebinding protection (required for ngrok Host headers).
    """
    from mcp.server.fastmcp import FastMCP as _FM
    mount_mcp = _FM(
        "HCI AI Operating System",
        instructions=mcp._mcp_server.instructions,
        streamable_http_path="/",
        host="0.0.0.0",
    )
    # Copy all registered tools to the mount instance
    for _name, _tool in mcp._tool_manager._tools.items():
        mount_mcp._tool_manager._tools[_name] = _tool
    return mount_mcp.streamable_http_app()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HCI AI MCP Server")
    parser.add_argument("--http", nargs="?", const=8080, type=int,
                        help="Run HTTP/SSE transport on this port (default 8080)")
    args = parser.parse_args()

    if args.http:
        import uvicorn
        port = args.http
        tool_count = len(mcp._tool_manager.list_tools())
        print(f"HCI AI MCP Server — {tool_count} tools, port {port}", flush=True)
        uvicorn.run(mcp.streamable_http_app(), host="0.0.0.0", port=port, log_level="info")
    else:
        print("HCI AI MCP Server — stdio transport", file=sys.stderr, flush=True)
        mcp.run(transport="stdio")
