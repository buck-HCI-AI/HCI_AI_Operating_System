"""
Drive Intelligence Service API routes.
Mounted at /api/v1/services/drive-intelligence
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from drive_client import (
    walk_folder_tree, list_folder_all, get_file_metadata,
    search_files, get_about, HCI_MASTER_FOLDER, MIME_LABELS
)
from classifier import classify_file, classify, get_routing, detect_project

router = APIRouter()

DEFAULT_FOLDER = HCI_MASTER_FOLDER

REPORT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..",
    "Architecture", "Platform_Intelligence", "GoogleDrive", "Current"
))


def _enrich(file: dict) -> dict:
    cl = classify_file(file)
    return {
        "id":           file.get("id"),
        "name":         file.get("name"),
        "mime_type":    file.get("mimeType"),
        "mime_label":   MIME_LABELS.get(file.get("mimeType", ""), "file"),
        "path":         file.get("_path", ""),
        "depth":        file.get("_depth", 0),
        "size":         file.get("size"),
        "modified":     file.get("modifiedTime", "")[:10] if file.get("modifiedTime") else None,
        "created":      file.get("createdTime", "")[:10] if file.get("createdTime") else None,
        "web_url":      file.get("webViewLink"),
        "owner":        (file.get("owners") or [{}])[0].get("emailAddress"),
        "category":     cl["category"],
        "routing":      cl["routing"],
        "project":      cl["project"],
        "confidence":   cl["confidence"],
        "auto_ingest":  cl["auto_ingest"],
    }


@router.get("")
def service_info():
    return {
        "service":     "drive-intelligence",
        "version":     "1.0.0",
        "status":      "active",
        "description": "Google Drive knowledge source for all HCI AI agents — audit, classify, route, and ingest Drive content",
        "default_folder": DEFAULT_FOLDER,
        "connected_as": "buck@hendricksoninc.com",
        "endpoints": [
            "GET  /tree?folder_id=      — recursive folder tree",
            "GET  /files?folder_id=     — files in one folder",
            "GET  /file/{id}            — single file metadata + classification",
            "GET  /search?q=            — search files by name",
            "POST /audit                — full recursive audit with reports",
            "POST /classify             — classify a specific file by ID",
            "POST /route                — get routing recommendation for a file",
            "POST /ingest               — ingest file into correct HCI system (dry_run default)",
        ],
    }


@router.get("/tree")
def folder_tree(
    folder_id: str = Query(DEFAULT_FOLDER, description="Google Drive folder ID"),
    max_depth: int = Query(4, description="Max recursion depth"),
):
    try:
        files = walk_folder_tree(folder_id, max_depth=max_depth)
    except Exception as e:
        raise HTTPException(500, f"Drive API error: {e}")

    folders = [f for f in files if "folder" in f.get("mimeType", "")]
    docs    = [f for f in files if "folder" not in f.get("mimeType", "")]

    return {
        "folder_id":    folder_id,
        "total_items":  len(files),
        "total_folders": len(folders),
        "total_files":  len(docs),
        "tree": [
            {
                "path":       f.get("_path", f.get("name")),
                "id":         f["id"],
                "type":       "folder" if "folder" in f.get("mimeType","") else "file",
                "mime_label": MIME_LABELS.get(f.get("mimeType",""), "file"),
                "depth":      f.get("_depth", 0),
            }
            for f in files
        ],
    }


@router.get("/files")
def list_files(
    folder_id: str = Query(DEFAULT_FOLDER),
    classify: bool = Query(True, description="Include classification"),
):
    try:
        raw = list_folder_all(folder_id)
    except Exception as e:
        raise HTTPException(500, f"Drive API error: {e}")

    files = [_enrich(f) for f in raw] if classify else raw
    return {"folder_id": folder_id, "count": len(files), "files": files}


@router.get("/file/{file_id}")
def get_file(file_id: str):
    try:
        raw = get_file_metadata(file_id)
    except Exception as e:
        raise HTTPException(404, f"File not found or inaccessible: {e}")
    return _enrich(raw)


@router.get("/search")
def search(
    q: str = Query(..., description="Search query"),
    folder_id: str = Query(None, description="Limit to folder"),
):
    try:
        raw = search_files(q, folder_id)
    except Exception as e:
        raise HTTPException(500, f"Drive API error: {e}")
    return {"query": q, "count": len(raw), "files": [_enrich(f) for f in raw]}


@router.post("/audit")
def run_audit(
    folder_id: str = Query(DEFAULT_FOLDER),
    max_depth: int = Query(5),
    write_reports: bool = Query(True),
):
    """Full recursive audit — classify every file, generate 6 markdown reports."""
    try:
        all_files = walk_folder_tree(folder_id, max_depth=max_depth)
    except Exception as e:
        raise HTTPException(500, f"Drive API error: {e}")

    docs    = [f for f in all_files if "folder" not in f.get("mimeType", "")]
    folders = [f for f in all_files if "folder" in f.get("mimeType", "")]
    enriched = [_enrich(f) for f in docs]

    # Tally by category
    by_category: dict[str, list] = {}
    by_routing:  dict[str, list] = {}
    by_project:  dict[str, list] = {}
    unknown      = []
    auto_ingest  = []

    for f in enriched:
        cat  = f["category"]
        dest = f["routing"]
        proj = f["project"] or "Unassigned"

        by_category.setdefault(cat, []).append(f)
        by_routing.setdefault(dest, []).append(f)
        by_project.setdefault(proj, []).append(f)

        if cat == "Unknown / Needs Review":
            unknown.append(f)
        if f["auto_ingest"]:
            auto_ingest.append(f)

    report_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # ── Write 6 markdown reports ───────────────────────────────
    if write_reports:
        os.makedirs(REPORT_DIR, exist_ok=True)
        _write_audit_report(folder_id, all_files, enriched, folders, by_category, by_routing, report_ts)
        _write_folder_tree(all_files, report_ts)
        _write_classification_report(enriched, by_category, report_ts)
        _write_routing_recommendations(enriched, by_routing, report_ts)
        _write_project_brain_candidates(enriched, by_project, report_ts)
        _write_unknown_review(unknown, report_ts)

    return {
        "folder_id":         folder_id,
        "scanned_at":        report_ts,
        "total_folders":     len(folders),
        "total_files":       len(docs),
        "classified":        len(enriched),
        "auto_ingest_ready": len(auto_ingest),
        "unknown_count":     len(unknown),
        "by_category":       {k: len(v) for k, v in sorted(by_category.items(), key=lambda x: -len(x[1]))},
        "by_routing":        {k: len(v) for k, v in sorted(by_routing.items(), key=lambda x: -len(x[1]))},
        "reports_written":   write_reports,
        "report_dir":        REPORT_DIR if write_reports else None,
    }


@router.post("/classify")
def classify_single(file_id: str = Query(...)):
    try:
        raw = get_file_metadata(file_id)
    except Exception as e:
        raise HTTPException(404, f"File not found: {e}")
    return _enrich(raw)


@router.post("/route")
def route_file(file_id: str = Query(...)):
    try:
        raw = get_file_metadata(file_id)
    except Exception as e:
        raise HTTPException(404, f"File not found: {e}")
    enriched = _enrich(raw)
    return {
        "file_id":    file_id,
        "name":       enriched["name"],
        "category":   enriched["category"],
        "routing":    enriched["routing"],
        "project":    enriched["project"],
        "confidence": enriched["confidence"],
        "recommendation": (
            f"Auto-ingest to {enriched['routing']}"
            if enriched["auto_ingest"]
            else f"Queue for review → {enriched['routing']} (confidence {enriched['confidence']})"
        ),
    }


@router.post("/ingest")
def ingest_file(
    file_id: str = Query(...),
    dry_run: bool = Query(True, description="Default true — report without writing"),
):
    """
    Ingest a Drive file into the appropriate HCI system.
    dry_run=True (default): report what would happen.
    dry_run=False: requires explicit Buck approval (future implementation).
    """
    try:
        raw = get_file_metadata(file_id)
    except Exception as e:
        raise HTTPException(404, f"File not found: {e}")
    enriched = _enrich(raw)

    action = {
        "file_id":       file_id,
        "name":          enriched["name"],
        "category":      enriched["category"],
        "destination":   enriched["routing"],
        "project":       enriched["project"],
        "web_url":       enriched["web_url"],
        "confidence":    enriched["confidence"],
        "dry_run":       dry_run,
        "auto_eligible": enriched["auto_ingest"],
    }

    if dry_run:
        action["status"]  = "DRY_RUN"
        action["message"] = (
            f"Would ingest '{enriched['name']}' → {enriched['routing']}"
            + (f" (project: {enriched['project']})" if enriched["project"] else "")
        )
    else:
        action["status"]  = "PENDING_APPROVAL"
        action["message"] = "Production ingest requires Buck Adams approval — not yet implemented"

    return action


# ── Report writers ─────────────────────────────────────────────

def _write_audit_report(folder_id, all_files, enriched, folders, by_category, by_routing, ts):
    path = os.path.join(REPORT_DIR, "DRIVE_KNOWLEDGE_AUDIT.md")
    with open(path, "w") as f:
        f.write(f"# Drive Knowledge Audit\n**Date:** {ts} | **Folder:** {folder_id}\n\n")
        f.write(f"## Summary\n| Metric | Count |\n|---|---|\n")
        f.write(f"| Folders scanned | {len(folders)} |\n")
        f.write(f"| Files scanned | {len(enriched)} |\n")
        f.write(f"| Auto-ingest ready | {sum(1 for x in enriched if x['auto_ingest'])} |\n")
        f.write(f"| Needs review | {sum(1 for x in enriched if x['category']=='Unknown / Needs Review')} |\n\n")
        f.write("## By Category\n| Category | Count |\n|---|---|\n")
        for cat, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
            f.write(f"| {cat} | {len(items)} |\n")
        f.write("\n## By Routing Destination\n| Destination | Count |\n|---|---|\n")
        for dest, items in sorted(by_routing.items(), key=lambda x: -len(x[1])):
            f.write(f"| {dest} | {len(items)} |\n")


def _write_folder_tree(all_files, ts):
    path = os.path.join(REPORT_DIR, "DRIVE_FOLDER_TREE.md")
    with open(path, "w") as f:
        f.write(f"# Drive Folder Tree\n**Date:** {ts}\n\n```\n")
        for item in all_files:
            indent = "  " * item.get("_depth", 0)
            icon   = "📁" if "folder" in item.get("mimeType","") else "📄"
            f.write(f"{indent}{icon} {item['name']}\n")
        f.write("```\n")


def _write_classification_report(enriched, by_category, ts):
    path = os.path.join(REPORT_DIR, "DRIVE_CLASSIFICATION_REPORT.md")
    with open(path, "w") as f:
        f.write(f"# Drive Classification Report\n**Date:** {ts}\n\n")
        for cat, items in sorted(by_category.items(), key=lambda x: -len(x[1])):
            f.write(f"\n## {cat} ({len(items)})\n")
            f.write("| File | Project | Confidence | Routing |\n|---|---|---|---|\n")
            for item in items[:20]:
                f.write(f"| [{item['name']}]({item['web_url'] or '#'}) | {item['project'] or '—'} | {item['confidence']} | {item['routing']} |\n")
            if len(items) > 20:
                f.write(f"| *(+{len(items)-20} more)* | | | |\n")


def _write_routing_recommendations(enriched, by_routing, ts):
    path = os.path.join(REPORT_DIR, "DRIVE_ROUTING_RECOMMENDATIONS.md")
    with open(path, "w") as f:
        f.write(f"# Drive Routing Recommendations\n**Date:** {ts}\n\n")
        for dest, items in sorted(by_routing.items(), key=lambda x: -len(x[1])):
            f.write(f"\n## → {dest} ({len(items)} files)\n")
            auto = [x for x in items if x["auto_ingest"]]
            review = [x for x in items if not x["auto_ingest"]]
            if auto:
                f.write(f"**Auto-ingest ready ({len(auto)}):**\n")
                for item in auto[:10]:
                    f.write(f"- [{item['name']}]({item['web_url'] or '#'}) ({item['category']}, {item['confidence']})\n")
            if review:
                f.write(f"\n**Needs review ({len(review)}):**\n")
                for item in review[:10]:
                    f.write(f"- [{item['name']}]({item['web_url'] or '#'}) ({item['category']}, {item['confidence']})\n")


def _write_project_brain_candidates(enriched, by_project, ts):
    path = os.path.join(REPORT_DIR, "DRIVE_PROJECT_BRAIN_CANDIDATES.md")
    with open(path, "w") as f:
        f.write(f"# Drive Project Brain Candidates\n**Date:** {ts}\n\n")
        for proj, items in sorted(by_project.items()):
            if proj == "Unassigned":
                continue
            f.write(f"\n## {proj} ({len(items)} files)\n")
            f.write("| File | Category | URL |\n|---|---|---|\n")
            for item in items[:15]:
                f.write(f"| {item['name']} | {item['category']} | [link]({item['web_url'] or '#'}) |\n")
        # Unassigned last
        unassigned = by_project.get("Unassigned", [])
        if unassigned:
            f.write(f"\n## Unassigned ({len(unassigned)} files)\n")
            for item in unassigned[:20]:
                f.write(f"- {item['name']} ({item['category']})\n")


def _write_unknown_review(unknown, ts):
    path = os.path.join(REPORT_DIR, "DRIVE_UNKNOWN_FILES_REVIEW.md")
    with open(path, "w") as f:
        f.write(f"# Unknown Files — Needs Review\n**Date:** {ts} | **Count:** {len(unknown)}\n\n")
        f.write("| File | Path | MIME | URL |\n|---|---|---|---|\n")
        for item in unknown:
            f.write(f"| {item['name']} | {item['path']} | {item['mime_label']} | [link]({item['web_url'] or '#'}) |\n")
