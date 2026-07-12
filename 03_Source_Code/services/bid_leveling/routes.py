import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "approval_queue"))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from bid_leveling_service import BidLevelingService, reject_if_monitored_folder, MonitoredFolderWriteError
from hubspot_bid_sync import sync_project_hubspot_bids

router = APIRouter()


class RunRequest(BaseModel):
    dry_run: bool = True
    divisions: Optional[List[str]] = None   # e.g. ["06", "07"] — None means all


class ExecuteQueueRequest(BaseModel):
    queue_id: int


class CreateFolderRequest(BaseModel):
    parent_folder_id: str
    folder_name: str


class UploadFileRequest(BaseModel):
    folder_id: str
    filename: str
    content_b64: str
    mime_type: Optional[str] = "application/octet-stream"


class WriteSheetRequest(BaseModel):
    sheet_id: str
    range_name: str
    values: List[List]


@router.get("")
def service_info():
    return {
        "service":     "bid-leveling",
        "description": "Reads bid tracking sheets, generates per-division Excel files, manages Drive folder structure",
        "endpoints": {
            "GET  /projects":                       "List all configured projects",
            "GET  /projects/{id}/data":             "Read all raw bid data for a project (AI/GBT)",
            "GET  /projects/{id}/summary":          "Read division summary for a project",
            "POST /projects/{id}/run":              "Run bid leveling (dry_run=True default)",
            "POST /run-all":                        "Run all configured projects",
            "POST /projects/{id}/execute-upload/{queue_id}": "Execute an approved upload queue item",
            "POST /drive/create-folder":            "Create a Drive folder (AI/GBT write)",
            "POST /drive/upload-file":              "Upload a file to Drive (AI/GBT write)",
            "GET  /drive/list/{folder_id}":         "List Drive folder contents (AI/GBT read)",
            "GET  /sheets/read":                    "Read a Google Sheets range (AI/GBT read)",
            "POST /sheets/write":                   "Write to a Google Sheets range (AI/GBT write)",
        },
    }


@router.get("/projects")
def list_projects():
    projects = BidLevelingService.get_all_configured_projects()
    return {"projects": projects, "count": len(projects)}


@router.get("/projects/{project_id}/data")
def get_project_data(project_id: int):
    """Full raw bid data — intended for AI agent consumption (GBT, Claude, etc.)."""
    try:
        return BidLevelingService.get_project_data(project_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/projects/{project_id}/summary")
def get_division_summary(project_id: int):
    """Division-level summary from the HCI Division Summary sheet tab."""
    try:
        config   = BidLevelingService.get_project_config(project_id)
        sheet_id = config["gsheet_bid_tracker"]
        if not sheet_id:
            raise HTTPException(400, "No sheet configured for this project")
        from bid_leveling_service import get_google_token
        token   = get_google_token("sheets")
        summary = BidLevelingService.read_division_summary(sheet_id, token)
        return {"project": config["name"], "project_id": project_id,
                "divisions": summary, "count": len(summary)}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/projects/{project_id}/run")
def run_bid_leveling(project_id: int, req: RunRequest):
    """
    Run bid leveling workflow for one project.
    dry_run=True (default): read + analyze only, no Drive writes.
    dry_run=False: generate Excel files and queue all Drive uploads.
    divisions: optional list to limit which divisions to process.
    """
    try:
        result = BidLevelingService.run_bid_leveling(
            project_id, dry_run=req.dry_run, divisions_filter=req.divisions
        )
        if "error" in result:
            raise HTTPException(400, result["error"])
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/run-all")
def run_all_projects(req: RunRequest):
    """Run bid leveling for all projects that have a sheet and Drive folder configured."""
    try:
        return BidLevelingService.run_all_projects(dry_run=req.dry_run)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/projects/{project_id}/scan-drive")
def scan_drive_bids(project_id: int, dry_run: bool = True):
    """
    Scan a project's Drive bid folders for new vendor PDFs.
    Extracts bid amounts via Gemini and upserts to drive_bids table.
    dry_run=True (default): preview without writing.
    """
    try:
        return BidLevelingService.scan_drive_bids(project_id, dry_run=dry_run)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/projects/{project_id}/drive-bids")
def get_drive_bids(project_id: int, latest_only: bool = True):
    """Read all Drive-sourced bids from the drive_bids table for a project."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from drive_bid_reader import read_drive_bids, get_leveling_summary
        bids    = read_drive_bids(project_id, latest_only=latest_only)
        summary = get_leveling_summary(project_id)
        return {"project_id": project_id, "divisions": bids,
                "leveling_summary": summary, "division_count": len(bids)}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/projects/{project_id}/execute-upload/{queue_id}")
def execute_queued_upload(project_id: int, queue_id: int):
    """
    Executes an approved approval queue item — actually uploads the Excel file to Drive.
    Requires the queue item to be in 'approved' status first.
    """
    try:
        result = BidLevelingService.execute_queued_upload(queue_id)
        if "error" in result:
            raise HTTPException(400, result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Drive read/write endpoints (for GBT and AI agent access) ─────────────────

@router.post("/drive/create-folder")
def create_drive_folder(req: CreateFolderRequest):
    """
    Creates a folder in Google Drive.
    For use by ChatGPT/GBT and AI agents with full write access.
    """
    try:
        reject_if_monitored_folder(req.parent_folder_id)
        return BidLevelingService.create_folder(req.parent_folder_id, req.folder_name)
    except MonitoredFolderWriteError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/drive/upload-file")
def upload_drive_file(req: UploadFileRequest):
    """
    Uploads a file to Google Drive (creates or updates).
    content_b64: base64-encoded file content.
    For use by ChatGPT/GBT and AI agents with full write access.
    """
    try:
        reject_if_monitored_folder(req.folder_id)
        return BidLevelingService.upload_file(
            req.folder_id, req.filename, req.content_b64, req.mime_type or "application/octet-stream"
        )
    except MonitoredFolderWriteError as e:
        raise HTTPException(403, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/drive/list/{folder_id}")
def list_drive_folder(folder_id: str):
    """Lists contents of a Google Drive folder. For AI agent read access."""
    try:
        return BidLevelingService.list_drive_folder(folder_id)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/sheets/read")
def read_sheet_range(
    sheet_id: str = Query(..., description="Google Sheets file ID"),
    range_name: str = Query("Sheet1!A1:Z200", description="Sheet range e.g. 'Sheet1!A1:Z100'"),
):
    """Reads a Google Sheets range. For AI agent read access."""
    try:
        return BidLevelingService.read_sheet_range(sheet_id, range_name)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/sheets/write")
def write_sheet_range(req: WriteSheetRequest):
    """
    Writes values to a Google Sheets range.
    For use by ChatGPT/GBT and AI agents with full write access.
    """
    try:
        return BidLevelingService.write_sheet_range(req.sheet_id, req.range_name, req.values)
    except Exception as e:
        raise HTTPException(500, str(e))


class SyncHubSpotBidsRequest(BaseModel):
    dry_run: bool = True
    csi_division: Optional[str] = None  # e.g. "06" — None means every division-level deal


@router.post("/projects/{project_id}/sync-hubspot")
def sync_hubspot_bids(project_id: int, req: SyncHubSpotBidsRequest):
    """
    Pulls bid attachments off each division-level HubSpot deal's associated emails
    and places them into 00_Bids/{div}/{vendor}/ in Drive, so the existing Drive scan
    (run_bid_leveling with scan_drive=True) picks them up on its next run. Requires
    the HubSpot Private App to have crm.objects.emails.read + sales-email-read scopes -
    without them every division comes back with an explicit scope-missing error rather
    than silently finding nothing.
    """
    try:
        return sync_project_hubspot_bids(project_id, csi_division=req.csi_division, dry_run=req.dry_run)
    except Exception as e:
        raise HTTPException(500, str(e))
