"""
Drive Intelligence Service Tests
Covers: service info, folder tree, file metadata, search, audit, classify, route, ingest.
"""
import json, requests
from pathlib import Path

API     = "http://localhost:8000"
HEADERS = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}
DI      = "/api/v1/services/drive-intelligence"
REPORT_DIR = Path("/Users/buckadams/HCI_AI_Operating_System/Architecture/Platform_Intelligence/GoogleDrive/Current")

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + str(detail) if detail else ''}")

def get(path, params=None):
    r = requests.get(f"{API}{path}", headers=HEADERS, params=params, timeout=30)
    return r.status_code, r.json() if r.ok else {}

def post(path, params=None):
    r = requests.post(f"{API}{path}", headers=HEADERS, params=params, timeout=60)
    return r.status_code, r.json() if r.ok else {}

print("Drive Intelligence Service Tests")
print("=" * 50)

# ── 1. Service Info ─────────────────────────────────────────
print("\n1. Service Info")
code, d = get(DI)
check("Returns 200", code == 200, code)
check("Status is active", d.get("status") == "active")
check("Has 8 endpoints", len(d.get("endpoints", [])) >= 8)
check("connected_as is buck@hendricksoninc.com", "hendricksoninc.com" in d.get("connected_as", ""))
check("Has default_folder", "default_folder" in d)

# ── 2. Folder Tree ──────────────────────────────────────────
print("\n2. Folder Tree")
code, d = get(f"{DI}/tree")
check("Returns 200", code == 200, code)
check("Has tree list", isinstance(d.get("tree"), list))
check("Has folder counts", "total_folders" in d and "total_files" in d)
check("Finds folders (>0)", d.get("total_folders", 0) > 0, d.get("total_folders"))
check("Finds files (>0)",   d.get("total_files", 0) > 0, d.get("total_files"))
if d.get("tree"):
    item = d["tree"][0]
    check("Tree item has path", "path" in item)
    check("Tree item has id",   "id" in item)
    check("Tree item has type", item.get("type") in ("folder", "file"))
    check("Tree item has depth", "depth" in item)

# ── 3. Files in Folder ─────────────────────────────────────
print("\n3. Files Listing")
code, d = get(f"{DI}/files")
check("Returns 200", code == 200, code)
check("Has files list", isinstance(d.get("files"), list))
check("Files have category", all("category" in f for f in d.get("files", [])))
check("Files have routing",  all("routing"  in f for f in d.get("files", [])))
check("Files have web_url",  any(f.get("web_url") for f in d.get("files", [])))

# ── 4. Single File ──────────────────────────────────────────
print("\n4. Single File Metadata + Classification")
# Use HCI AI - Master folder ID as a known accessible resource
KNOWN_FILE = "1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP"  # LIVE_PROJECT_STATE.md
code, d = get(f"{DI}/file/{KNOWN_FILE}")
check("Returns 200 for known file", code == 200, code)
check("Has name",       "name" in d)
check("Has category",   "category" in d)
check("Has routing",    "routing"  in d)
check("Has confidence", isinstance(d.get("confidence"), float))
check("Has web_url",    "web_url" in d)

code2, _ = get(f"{DI}/file/nonexistent_id_xyz")
check("Unknown file returns 404", code2 == 404, code2)

# ── 5. Search ───────────────────────────────────────────────
print("\n5. Search")
code, d = get(f"{DI}/search", {"q": "schedule"})
check("Search returns 200", code == 200, code)
check("Has files list", isinstance(d.get("files"), list))
check("Has query echo", d.get("query") == "schedule")
check("Has count", "count" in d)

# ── 6. Classifier Logic ─────────────────────────────────────
print("\n6. Classifier Logic (unit)")
import sys
sys.path.insert(0, "/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/services/drive_intelligence")
from classifier import classify, detect_project, get_routing, confidence_score

cases = [
    ("101 Francis Production Schedule v1.0", "Schedule"),
    ("HCI SOP 00 Master.docx", "SOP"),
    ("Subcontract Agreement Plumbing.pdf", "Contract"),
    ("Change Order #12.xlsx", "Change Order"),
    ("1355 Riverside Bid Package.pdf", "Bid / Estimate"),
    ("Daily Log - 655 Garmisch.docx", "Field Report / Daily Log"),
    ("random_file_xyz.pdf", "Unknown / Needs Review"),
]
for name, expected in cases:
    result = classify(name)
    check(f"Classify '{name[:35]}...' → {expected}", result == expected, f"got: {result}")

project_cases = [
    ("101 Francis Production Schedule", "101 Francis"),
    ("1355_Riverside_Controls", "1355 Riverside"),
    ("655 Garmish Tasks.xlsx", "655 Garmisch"),
    ("random_unrelated.pdf", None),
]
for name, expected in project_cases:
    result = detect_project(name)
    check(f"Detect project '{name[:35]}'", result == expected, f"got: {result}")

check("Confidence for Unknown < 0.5",
      confidence_score("random_xyz.pdf", "Unknown / Needs Review") < 0.5)
check("Confidence for SOP match >= 0.65",
      confidence_score("HCI SOP 00 Master.docx", "SOP") >= 0.65)

# ── 7. Route Endpoint ───────────────────────────────────────
print("\n7. Route")
code, d = post(f"{DI}/route", {"file_id": KNOWN_FILE})
check("Route returns 200", code == 200, code)
check("Has recommendation", "recommendation" in d)
check("Has category",  "category" in d)
check("Has routing",   "routing"  in d)
check("Has confidence","confidence" in d)

# ── 8. Ingest (dry run) ─────────────────────────────────────
print("\n8. Ingest (dry_run=True)")
code, d = post(f"{DI}/ingest", {"file_id": KNOWN_FILE, "dry_run": "true"})
check("Ingest dry run returns 200", code == 200, code)
check("Status is DRY_RUN", d.get("status") == "DRY_RUN")
check("Has message", "message" in d)
check("dry_run flag True", d.get("dry_run") is True)

# ── 9. Audit + Reports ─────────────────────────────────────
print("\n9. Audit Reports")
check("DRIVE_KNOWLEDGE_AUDIT.md exists",     (REPORT_DIR / "DRIVE_KNOWLEDGE_AUDIT.md").exists())
check("DRIVE_FOLDER_TREE.md exists",          (REPORT_DIR / "DRIVE_FOLDER_TREE.md").exists())
check("DRIVE_CLASSIFICATION_REPORT.md exists",(REPORT_DIR / "DRIVE_CLASSIFICATION_REPORT.md").exists())
check("DRIVE_ROUTING_RECOMMENDATIONS.md exists",(REPORT_DIR / "DRIVE_ROUTING_RECOMMENDATIONS.md").exists())
check("DRIVE_PROJECT_BRAIN_CANDIDATES.md exists",(REPORT_DIR / "DRIVE_PROJECT_BRAIN_CANDIDATES.md").exists())
check("DRIVE_UNKNOWN_FILES_REVIEW.md exists",  (REPORT_DIR / "DRIVE_UNKNOWN_FILES_REVIEW.md").exists())

audit_text = (REPORT_DIR / "DRIVE_KNOWLEDGE_AUDIT.md").read_text() if (REPORT_DIR / "DRIVE_KNOWLEDGE_AUDIT.md").exists() else ""
check("Audit has file count", "Files scanned" in audit_text)
check("Audit has category table", "By Category" in audit_text)
check("Audit has routing table",  "By Routing"  in audit_text)

# ── 10. Service registered in list_services ─────────────────
print("\n10. Service Registry")
code, d = get("/api/v1/services")
check("Services list returns 200", code == 200, code)
svc_names = [s.get("name") for s in d.get("services", [])]
check("drive-intelligence in services", "drive-intelligence" in svc_names)

# ── Results ─────────────────────────────────────────────────
print(f"\n{'='*50}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
