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
    q = f"name contains '{query}' and trashed=false"
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
