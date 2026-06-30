"""
AI Operations Control Plane — Durable Comms Patch + Warm Start Recovery
Tests: ai/messages, ai/queue, approvals, status transitions, telegram webhook
commands, escalation/retry, telegram/health, ai/warm-start, ai/events.
"""
import requests

API = "http://localhost:8000/gateway"
HEADERS = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}

passed = failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS {label}")
    else:
        failed += 1
        print(f"  FAIL {label}{': ' + str(detail) if detail else ''}")


def post(path, body=None):
    r = requests.post(f"{API}{path}", headers=HEADERS, json=body or {}, timeout=20)
    return r.status_code, (r.json() if r.ok else {})


def patch(path, body=None):
    r = requests.patch(f"{API}{path}", headers=HEADERS, json=body or {}, timeout=20)
    return r.status_code, (r.json() if r.ok else {})


def get(path, params=None):
    r = requests.get(f"{API}{path}", headers=HEADERS, params=params, timeout=20)
    return r.status_code, (r.json() if r.ok else {})


print("AI Operations Control Plane — Test Suite")
print("=" * 50)

# ── 1. Create a durable message (no Telegram notify expected — message_type=note) ──
print("\n1. POST /ai/messages — durable create")
code, d = post("/ai/messages", {
    "source": "claude_code", "target": "buck", "message_type": "note",
    "title": "Automated test — control plane suite", "body": "non-notifying test row",
})
check("Returns 200", code == 200, code)
msg_id = d.get("payload", {}).get("id")
check("Has id", isinstance(msg_id, int))
check("Delivery skipped for non-notify type", d.get("payload", {}).get("delivery", {}).get("status") == "skipped")

# ── 2. Durable queue is readable regardless of Telegram ──────────────────────
print("\n2. GET /ai/queue — fallback polling")
code, d = get("/ai/queue", {"limit": 5})
check("Returns 200", code == 200, code)
check("Has messages list", isinstance(d.get("payload", {}).get("messages"), list))
check("Test row visible in queue", any(m["id"] == msg_id for m in d["payload"]["messages"]))

# ── 3. Status transition (agent self-report) ──────────────────────────────────
print("\n3. PATCH /ai/messages/{id}/status")
code, d = patch(f"/ai/messages/{msg_id}/status", {"status": "IN_PROGRESS", "agent": "claude_code"})
check("Returns 200", code == 200, code)
check("Status updated", d.get("payload", {}).get("status") == "IN_PROGRESS")
code, d = patch(f"/ai/messages/{msg_id}/status", {"status": "INVALID_STATE"})
check("Rejects invalid status", code == 200 and d.get("errors"), d)
patch(f"/ai/messages/{msg_id}/status", {"status": "COMPLETE", "agent": "claude_code"})

# ── 4. Approvals visible without Telegram round-trip ──────────────────────────
print("\n4. GET /approvals")
code, d = post("/ai/messages", {
    "source": "claude_code", "target": "buck", "message_type": "approval_request",
    "title": "Automated test — approval row", "body": "test", "requires_buck_approval": True,
})
approval_id = d.get("payload", {}).get("id")
check("Approval create returns 200", code == 200, code)
check("Telegram attempted (sent or failed, not skipped)",
      d.get("payload", {}).get("delivery", {}).get("status") in ("sent", "failed", "error"))
code, d = get("/approvals")
check("Approvals endpoint 200", code == 200, code)
ids = [a["id"] for a in d.get("payload", {}).get("approvals", [])]
check("New approval present in queue", approval_id in ids)

# ── 5. Telegram webhook command parsing (synthetic update, no real Telegram) ──
print("\n5. Webhook command parsing — APPROVE <id>")
code, d = post("/telegram/webhook", {
    "update_id": 1, "message": {"message_id": 1, "chat": {"id": 1}, "text": f"APPROVE {approval_id}"},
})
check("Webhook returns 200", code == 200, code)
code, d = get("/ai/queue", {"status": "ACKNOWLEDGED", "limit": 50})
ids = [m["id"] for m in d.get("payload", {}).get("messages", [])]
check("Status flipped to ACKNOWLEDGED via command", approval_id in ids)

# ── 6. Escalation / retry path for stale unacknowledged approvals ─────────────
print("\n6. POST /ai/escalation-check")
code, d = post("/ai/escalation-check")
check("Returns 200", code == 200, code)
check("Has escalated_count", isinstance(d.get("payload", {}).get("escalated_count"), int))

# ── 7. Telegram health diagnostic ──────────────────────────────────────────────
print("\n7. GET /telegram/health")
code, d = get("/telegram/health")
check("Returns 200", code == 200, code)
check("Has webhook_url field", "webhook_url" in d.get("payload", {}))

# ── 8. Warm start — single-call recovery snapshot ─────────────────────────────
print("\n8. GET /ai/warm-start")
code, d = get("/ai/warm-start")
check("Returns 200", code == 200, code)
p = d.get("payload", {})
for field in ("active_projects", "top_risks", "pending_buck_approvals",
              "pending_chief_architect_reviews", "pending_code_tasks", "pending_bc_tasks",
              "blocked_missions", "stale_handoffs", "agent_heartbeats", "next_recommended_action"):
    check(f"Has {field}", field in p)

# ── 9. AI events feed ──────────────────────────────────────────────────────────
print("\n9. GET /ai/events")
code, d = get("/ai/events", {"limit": 5})
check("Returns 200", code == 200, code)
check("Has events list", isinstance(d.get("payload", {}).get("events"), list))

# cleanup
patch(f"/ai/messages/{approval_id}/status", {"status": "COMPLETE"})

print("\n" + "=" * 50)
print(f"PASSED: {passed}  FAILED: {failed}")
if failed:
    raise SystemExit(1)
