"""
BTW-4 Tests — Project Brain Extended Memory
Covers: timeline, event logging, conversations, document links, daily summary
"""
import requests, json

BASE = "http://localhost:8000/api/v1/services"
H = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}
PB = f"{BASE}/project-brain"
PROJECT_ID = 1  # 64 Eastwood

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + str(detail) if detail else ''}")

print("Project Brain Extended Memory Tests (BTW-4)")
print("=" * 50)

# ── 1. Timeline ───────────────────────────────────────────────────────────────
print("\n1. Event Timeline")
r = requests.get(f"{PB}/{PROJECT_ID}/timeline", headers=H)
check("Timeline 200", r.status_code == 200, r.text[:100])
d = r.json()
check("Has project_id", d.get("project_id") == PROJECT_ID)
check("Has event_count", "event_count" in d)
check("Has events list", isinstance(d.get("events"), list))

# With days filter
r2 = requests.get(f"{PB}/{PROJECT_ID}/timeline?days=7", headers=H)
check("Timeline with days filter 200", r2.status_code == 200)

# With event_type filter
r3 = requests.get(f"{PB}/{PROJECT_ID}/timeline?event_type=milestone", headers=H)
check("Timeline with event_type filter 200", r3.status_code == 200)
d3 = r3.json()
check("Filtered events are milestones", all(e["event_type"] == "milestone" for e in d3["events"]))

# ── 2. Event Logging ──────────────────────────────────────────────────────────
print("\n2. Event Logging")
payload = {
    "event_type": "decision",
    "title": "Test decision logged by BTW-4 test suite",
    "description": "Automated test event — safe to delete",
    "created_by": "test_suite",
    "metadata": {"test": True}
}
r = requests.post(f"{PB}/{PROJECT_ID}/events", headers=H, json=payload)
check("Log event 200", r.status_code == 200, r.text[:100])
d = r.json()
check("Event logged=true", d.get("logged") is True)
check("Event has id", "id" in d.get("event", {}))
check("Event type correct", d.get("event", {}).get("event_type") == "decision")

# Verify it appears in timeline
r2 = requests.get(f"{PB}/{PROJECT_ID}/timeline?event_type=decision", headers=H)
d2 = r2.json()
check("Logged event appears in timeline", any(
    "Test decision" in e["title"] for e in d2["events"]
))

# ── 3. Conversation Memory ────────────────────────────────────────────────────
print("\n3. Conversation Memory")
r = requests.get(f"{PB}/{PROJECT_ID}/conversations", headers=H)
check("Conversations 200", r.status_code == 200, r.text[:100])
d = r.json()
check("Has project_id", d.get("project_id") == PROJECT_ID)
check("Has conversation_count", "conversation_count" in d)
check("Has conversations list", isinstance(d.get("conversations"), list))

# Verify limit param works
r2 = requests.get(f"{PB}/{PROJECT_ID}/conversations?limit=5", headers=H)
check("Conversations with limit 200", r2.status_code == 200)
d2 = r2.json()
check("Limit respected", len(d2.get("conversations", [])) <= 5)

# ── 4. Document Links ─────────────────────────────────────────────────────────
print("\n4. Document Links")
r = requests.get(f"{PB}/{PROJECT_ID}/document-links", headers=H)
check("Document links 200", r.status_code == 200, r.text[:100])
d = r.json()
check("Has project_id", d.get("project_id") == PROJECT_ID)
check("Has link_count", "link_count" in d)
check("Has document_links list", isinstance(d.get("document_links"), list))

# Create a document link
link_payload = {
    "document_type": "meeting",
    "document_id": "test-meeting-001",
    "document_name": "Test Meeting — BTW-4 test",
    "linked_entity_type": "decision",
    "linked_entity_id": "test-dec-001",
    "linked_entity_name": "Test Decision",
    "relationship": "drove",
    "notes": "Automated test — safe to delete",
    "created_by": "test_suite"
}
r2 = requests.post(f"{PB}/{PROJECT_ID}/document-links", headers=H, json=link_payload)
check("Create document link 200", r2.status_code == 200, r2.text[:100])
d2 = r2.json()
check("Link created=true", d2.get("linked") is True)
check("Link has id", "id" in d2.get("link", {}))
check("Link relationship correct", d2.get("link", {}).get("relationship") == "drove")

# Filter by entity type
r3 = requests.get(f"{PB}/{PROJECT_ID}/document-links?entity_type=decision", headers=H)
check("Document links with entity_type filter 200", r3.status_code == 200)

# ── 5. Daily Summary (cached) ─────────────────────────────────────────────────
print("\n5. Daily Summary")
r = requests.get(f"{PB}/{PROJECT_ID}/daily-summary", headers=H, timeout=120)
check("Daily summary 200", r.status_code == 200, r.text[:100])
d = r.json()
check("Has project_id", d.get("project_id") == PROJECT_ID)
check("Has health field", d.get("health") in ("GREEN", "YELLOW", "RED"))
check("Has ai_summary text", bool(d.get("ai_summary")))
check("Has key_risks list", isinstance(d.get("key_risks"), list))
check("Has key_actions list", isinstance(d.get("key_actions"), list))
check("Has summary_date", bool(d.get("summary_date")))

# Second call should return cached version faster
import time
t0 = time.time()
r2 = requests.get(f"{PB}/{PROJECT_ID}/daily-summary", headers=H)
elapsed = time.time() - t0
check("Second call returns 200", r2.status_code == 200)
check("Second call is fast (<5s)", elapsed < 5, f"{elapsed:.1f}s")

# ── Results ───────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
