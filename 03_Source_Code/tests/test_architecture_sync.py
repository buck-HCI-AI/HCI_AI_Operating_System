import requests, json

BASE = "http://localhost:8000/api/v1/services"
H = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + detail if detail else ''}")

print("Architecture Sync Service Tests")
print("="*40)

# 1. Service info
r = requests.get(f"{BASE}/architecture-sync", headers=H)
check("Service info 200", r.status_code == 200)
d = r.json()
check("Has 8 endpoints listed", len(d.get("endpoints", [])) == 8)

# 2. Status
r = requests.get(f"{BASE}/architecture-sync/status", headers=H)
check("Status 200", r.status_code == 200)
d = r.json()
check("Has 10 volumes", len(d.get("volumes", [])) == 10)
check("Has ADRs", d.get("adr_count", 0) >= 6)
check("Has authoring_queue", "authoring_queue" in d)
check("CA volumes identified", len(d.get("volumes_needing_ca", [])) > 0)

# 3. Conflicts
r = requests.get(f"{BASE}/architecture-sync/conflicts", headers=H)
check("Conflicts 200", r.status_code == 200)
d = r.json()
check("Returns conflict_count", "conflict_count" in d)

# 4. Review engine
r = requests.get(f"{BASE}/architecture-sync/review-engine?files=services/project_brain/routes.py", headers=H)
check("Review engine 200", r.status_code == 200)
d = r.json()
check("Identifies affected volumes", len(d.get("affected_volumes", [])) > 0, str(d.get("affected_volumes")))

# 5. Queue
r = requests.get(f"{BASE}/architecture-sync/queue", headers=H)
check("Queue 200", r.status_code == 200)
d = r.json()
check("Has volumes in queue", len(d.get("volumes", [])) > 0)

# 6. Validate (valid chapter)
r = requests.post(f"{BASE}/architecture-sync/validate", headers=H, json={
    "content": "# Volume II — Test Chapter\n\nTest content for validation.",
    "volume": "II",
    "chapter": "2.test"
})
check("Validate 200", r.status_code == 200)
d = r.json()
check("Validation passed", d.get("validation", {}).get("passed") is True)

# 7. Submit chapter (dry_run)
r = requests.post(f"{BASE}/architecture-sync/submit-chapter", headers=H, json={
    "source": "api",
    "volume": "II",
    "chapter": "2.test",
    "title": "Test Chapter",
    "content": "# Volume II — Test Chapter\n\nImplementation test content.",
    "author": "Claude Code Test",
    "dry_run": True
})
check("Submit chapter 200", r.status_code == 200)
d = r.json()
check("Dry run no publish", "published" not in d or d.get("published") is None, str(d.get("published")))
check("Draft saved path returned", "draft_saved" in d)

# 8. Sync
r = requests.post(f"{BASE}/architecture-sync/sync", headers=H)
check("Sync 200", r.status_code == 200)
d = r.json()
check("Sync complete", d.get("sync_complete") is True)
check("Volumes scanned = 10", d.get("volumes_scanned") == 10)

print()
print(f"Result: {passed} passed, {failed} failed")
