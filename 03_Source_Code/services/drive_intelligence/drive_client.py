"""
Google Drive API client for Drive Intelligence Service.
Uses existing n8n OAuth credentials via credentials.py.
"""
import sys, os, json, ssl, urllib.request, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

import certifi
from credentials import get_google_token

SSL_CTX = ssl.create_default_context(cafile=certifi.where())
BASE_URL = "https://www.googleapis.com/drive/v3"

HCI_MASTER_FOLDER = "1ejYXRgS34c7JmQKfHwaPNnzEBcCGUmwI"

MIME_LABELS = {
    "application/vnd.google-apps.folder":       "folder",
    "application/vnd.google-apps.document":     "google_doc",
    "application/vnd.google-apps.spreadsheet":  "google_sheet",
    "application/vnd.google-apps.presentation": "google_slides",
    "application/pdf":                          "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":       "xlsx",
    "application/vnd.ms-excel":                 "xls",
    "text/plain":                               "txt",
    "text/markdown":                            "md",
    "image/jpeg":                               "jpg",
    "image/png":                                "png",
    "video/mp4":                                "mp4",
}

FILE_FIELDS = "id,name,mimeType,size,createdTime,modifiedTime,owners,webViewLink,parents,exportLinks"


def _token():
    return get_google_token("drive")


def _get(url: str, params: dict = None) -> dict:
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {_token()}"})
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as r:
        return json.loads(r.read())


def get_file_metadata(file_id: str) -> dict:
    return _get(f"{BASE_URL}/files/{file_id}", {"fields": FILE_FIELDS,
                "supportsAllDrives": "true", "includeItemsFromAllDrives": "true"})


def list_folder(folder_id: str, page_token: str = None) -> dict:
    params = {
        "q": f"'{folder_id}' in parents and trashed=false",
        "fields": f"files({FILE_FIELDS}),nextPageToken",
        "pageSize": 100,
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
    }
    if page_token:
        params["pageToken"] = page_token
    return _get(f"{BASE_URL}/files", params)


def list_folder_all(folder_id: str) -> list:
    """Return all files in a folder, handling pagination."""
    files, token = [], None
    while True:
        resp = list_folder(folder_id, token)
        files.extend(resp.get("files", []))
        token = resp.get("nextPageToken")
        if not token:
            break
    return files


def search_files(query: str, folder_id: str = None) -> list:
    # 2026-07-02: was "name contains" only, which misses matches inside document
    # content and even some folder-name matches - found while GBT couldn't locate a
    # real, existing "Asbestos Report" folder for 1355R. fullText covers both name
    # and body content in one query.
    q = f"fullText contains '{query}' and trashed=false"
    if folder_id:
        q += f" and '{folder_id}' in parents"
    params = {
        "q": q,
        "fields": f"files({FILE_FIELDS})",
        "pageSize": 50,
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
    }
    return _get(f"{BASE_URL}/files", params).get("files", [])


def walk_folder_tree(folder_id: str, path: str = "", depth: int = 0, max_depth: int = 6) -> list:
    """Recursively walk a folder. Returns flat list of file dicts with path."""
    if depth > max_depth:
        return []

    items = list_folder_all(folder_id)
    results = []
    for item in items:
        item["_path"] = f"{path}/{item['name']}" if path else item["name"]
        item["_depth"] = depth
        item["_mime_label"] = MIME_LABELS.get(item.get("mimeType", ""), "file")
        results.append(item)
        if "folder" in item.get("mimeType", ""):
            results.extend(walk_folder_tree(
                item["id"], item["_path"], depth + 1, max_depth))
    return results


def get_about() -> dict:
    return _get(f"{BASE_URL}/about", {"fields": "user,storageQuota"})


def get_file_content(file_id: str) -> dict:
    """
    Return text content of a Drive file.
    Google Docs/Sheets/Slides → exported as plain text via Drive export API.
    PDFs and binary files → not extractable via Drive API; returns empty with a note.
    """
    meta = get_file_metadata(file_id)
    mime = meta.get("mimeType", "")
    name = meta.get("name", file_id)

    EXPORT_MIME = {
        "application/vnd.google-apps.document":     "text/plain",
        "application/vnd.google-apps.spreadsheet":  "text/csv",
        "application/vnd.google-apps.presentation": "text/plain",
    }

    if mime in EXPORT_MIME:
        export_type = EXPORT_MIME[mime]
        url = f"{BASE_URL}/files/{file_id}/export"
        params = {"mimeType": export_type, "supportsAllDrives": "true"}
        url_with_params = url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url_with_params, headers={"Authorization": f"Bearer {_token()}"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as r:
            content = r.read().decode("utf-8", errors="replace")
        return {"file_id": file_id, "file_name": name, "mime_type": mime,
                "content": content, "char_count": len(content), "source": "drive_export"}

    # For DOCX/XLSX — use exportLinks if available
    export_links = meta.get("exportLinks", {})
    txt_link = export_links.get("text/plain") or export_links.get("text/csv")
    if txt_link:
        req = urllib.request.Request(txt_link, headers={"Authorization": f"Bearer {_token()}"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as r:
            content = r.read().decode("utf-8", errors="replace")
        return {"file_id": file_id, "file_name": name, "mime_type": mime,
                "content": content, "char_count": len(content), "source": "export_link"}

    # Plain-text-family files uploaded as-is (not native Google Docs) need a direct
    # media download, not the export API above - export only applies to converting a
    # native Google Doc/Sheet/Slide into another format. Found 2026-07-06: a raw
    # text/plain file (Drive-uploaded .txt, real mimeType confirmed via metadata) fell
    # through both branches above straight to the "binary, needs OCR" fallback, even
    # though it's the simplest possible format - GBT hit exactly this trying to read
    # a real SOW/contact-directory file for a live 1355R electrical re-bid.
    if mime.startswith("text/") or mime in ("application/json", "application/csv"):
        url = f"{BASE_URL}/files/{file_id}"
        params = {"alt": "media", "supportsAllDrives": "true"}
        url_with_params = url + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url_with_params, headers={"Authorization": f"Bearer {_token()}"})
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=60) as r:
            content = r.read().decode("utf-8", errors="replace")
        return {"file_id": file_id, "file_name": name, "mime_type": mime,
                "content": content, "char_count": len(content), "source": "direct_download"}

    return {"file_id": file_id, "file_name": name, "mime_type": mime,
            "content": "", "char_count": 0,
            "source": "none",
            "note": f"Binary file ({mime}) — text extraction requires MCP session or local OCR"}
