"""
BTW-7 — Superintendent Field Enhancements (unblocked subset)
Tests: deliveries, inspections, materials, voice-notes
Photo documentation deferred — requires Houzz extraction.
"""
import requests

API = "http://localhost:8000"
HEADERS = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + str(detail) if detail else ''}")

def get(path):
    r = requests.get(f"{API}{path}", headers=HEADERS, timeout=15)
    return r.status_code, r.json() if r.ok else {}

def post(path, payload):
    r = requests.post(f"{API}{path}", headers=HEADERS, json=payload, timeout=15)
    return r.status_code, r.json() if r.ok or r.status_code == 400 else {}

print("BTW-7 Field Enhancement Tests")
print("=" * 50)

# ── 1. Delivery Tracking ──────────────────────────────────────────────────────
print("\n1. Delivery Tracking — /superintendent/{project_id}/deliveries")
for pid in [1, 2, 3]:
    code, d = get(f"/api/v1/superintendent/{pid}/deliveries")
    check(f"Project {pid} returns 200", code == 200, code)
    check(f"Project {pid} has delivery_urgency (LOW/MEDIUM/HIGH)", d.get("delivery_urgency") in ("LOW", "MEDIUM", "HIGH"))
    check(f"Project {pid} has expected_today section", "expected_today" in d)
    check(f"Project {pid} expected_today has count", isinstance(d.get("expected_today", {}).get("count"), int))
    check(f"Project {pid} has expected_this_week section", "expected_this_week" in d)
    check(f"Project {pid} has overdue_deliveries section", "overdue_deliveries" in d)
    check(f"Project {pid} has confirmed_received section", "confirmed_received" in d)
    check(f"Project {pid} has data_status", "data_status" in d)
    check(f"Project {pid} has field_actions list", isinstance(d.get("field_actions"), list))

# ── 2. Inspection Scheduling ──────────────────────────────────────────────────
print("\n2. Inspection Scheduling — /superintendent/{project_id}/inspections")
for pid in [1, 2, 3]:
    code, d = get(f"/api/v1/superintendent/{pid}/inspections")
    check(f"Project {pid} returns 200", code == 200, code)
    check(f"Project {pid} has inspection_urgency", d.get("inspection_urgency") in ("LOW", "MEDIUM", "HIGH"))
    check(f"Project {pid} has due_today list", isinstance(d.get("due_today"), list))
    check(f"Project {pid} has overdue list", isinstance(d.get("overdue"), list))
    check(f"Project {pid} has upcoming_7_days list", isinstance(d.get("upcoming_7_days"), list))
    check(f"Project {pid} has open_inspection_tasks list", isinstance(d.get("open_inspection_tasks"), list))
    check(f"Project {pid} has data_status", "data_status" in d)
    check(f"Project {pid} has field_actions list", isinstance(d.get("field_actions"), list))

# ── 3. Material Tracking ──────────────────────────────────────────────────────
print("\n3. Material Tracking — /superintendent/{project_id}/materials")
for pid in [1, 2, 3]:
    code, d = get(f"/api/v1/superintendent/{pid}/materials")
    check(f"Project {pid} returns 200", code == 200, code)
    check(f"Project {pid} has summary section", "summary" in d)
    s = d.get("summary", {})
    check(f"Project {pid} summary has total_pos", "total_pos" in s)
    check(f"Project {pid} summary has total_value", "total_value" in s)
    check(f"Project {pid} summary has pending_value", "pending_value" in s)
    check(f"Project {pid} summary has pct_received", "pct_received" in s)
    check(f"Project {pid} has by_status dict", isinstance(d.get("by_status"), dict))
    check(f"Project {pid} has critical_needed_soon section", "critical_needed_soon" in d)
    check(f"Project {pid} has data_status", "data_status" in d)
    check(f"Project {pid} has field_actions list", isinstance(d.get("field_actions"), list))

# ── 4. Voice Notes ────────────────────────────────────────────────────────────
print("\n4. Voice Notes — POST /superintendent/{project_id}/voice-note")

# Valid observation
code, d = post("/api/v1/superintendent/1/voice-note", {
    "transcription": "Foundation pour complete on north wall, no issues",
    "note_type": "observation",
    "location": "north wall"
})
check("Valid observation note returns 200", code == 200, code)
check("Returns note_type", d.get("note_type") == "observation")
check("Returns formatted_entry with [OBS] tag", "[OBS]" in str(d.get("formatted_entry", "")))
check("Returns db_status", "db_status" in d)
check("Returns location", d.get("location") == "north wall")

# Safety note
code, d = post("/api/v1/superintendent/1/voice-note", {
    "transcription": "Hard hat area enforced on second floor",
    "note_type": "safety"
})
check("Safety note returns 200", code == 200, code)
check("Safety formatted_entry has [SAFETY] tag", "[SAFETY]" in str(d.get("formatted_entry", "")))

# Issue note
code, d = post("/api/v1/superintendent/2/voice-note", {
    "transcription": "Window rough opening on master bedroom is 2 inches too narrow",
    "note_type": "issue",
    "location": "master bedroom"
})
check("Issue note returns 200", code == 200, code)
check("Issue formatted_entry has [ISSUE] tag", "[ISSUE]" in str(d.get("formatted_entry", "")))

# Invalid note_type defaults to observation
code, d = post("/api/v1/superintendent/1/voice-note", {
    "transcription": "Random note",
    "note_type": "invalid_type"
})
check("Invalid note_type defaults gracefully", code == 200)
check("Defaults to observation type", d.get("note_type") == "observation")

# Empty transcription returns 400
code, d = post("/api/v1/superintendent/1/voice-note", {
    "transcription": "",
    "note_type": "observation"
})
check("Empty transcription returns 400", code == 400, code)

# ── 5. Error Handling ─────────────────────────────────────────────────────────
print("\n5. Error Handling")
for ep in ["deliveries", "inspections", "materials"]:
    code, _ = get(f"/api/v1/superintendent/9999/{ep}")
    check(f"{ep} 9999 returns 404", code == 404, code)

code, _ = post("/api/v1/superintendent/9999/voice-note", {"transcription": "test"})
check("voice-note 9999 returns 404", code == 404, code)

# ── Results ───────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
