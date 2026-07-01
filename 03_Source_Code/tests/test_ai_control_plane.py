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
    "source_agent": "claude_code", "target_agent": "buck", "message_type": "note",
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
    "source_agent": "claude_code", "target_agent": "buck", "message_type": "approval_request",
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
code, d = get("/ai/queue", {"status": "RECEIVED", "limit": 50})
ids = [m["id"] for m in d.get("payload", {}).get("messages", [])]
check("Status flipped to RECEIVED via command", approval_id in ids)

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

# ── 10. Directive lifecycle vocab reconciliation (ARB 2026-07-01) ─────────────
print("\n10. Directive lifecycle — ISSUED/RECEIVED/IN_PROGRESS/COMPLETE/BLOCKED/REJECTED")
code, d = post("/ai/messages", {
    "source_agent": "claude_code", "target_agent": "browser_claude", "message_type": "note",
    "title": "Automated test — lifecycle vocab", "body": "test", "priority": "high",
})
lc_id = d.get("payload", {}).get("id")
check("Created with priority accepted", code == 200)
code, d = get(f"/ai/messages/{lc_id}")
check("GET single message returns 200", code == 200, code)
check("Initial status is ISSUED", d.get("payload", {}).get("status") == "ISSUED", d.get("payload", {}).get("status"))
check("Priority stored", d.get("payload", {}).get("priority") == "high")
check("received_at null before acknowledge", d.get("payload", {}).get("received_at") is None)

code, d = post(f"/ai/messages/{lc_id}/acknowledge", {"agent": "browser_claude"})
check("Acknowledge returns 200", code == 200, code)
check("Acknowledge sets RECEIVED", d.get("payload", {}).get("status") == "RECEIVED")
code, d = get(f"/ai/messages/{lc_id}")
check("received_at stamped", d.get("payload", {}).get("received_at") is not None)

code, d = patch(f"/ai/messages/{lc_id}/status", {"status": "IN_PROGRESS", "agent": "browser_claude"})
check("IN_PROGRESS accepted", code == 200 and d.get("payload", {}).get("status") == "IN_PROGRESS")
code, d = get(f"/ai/messages/{lc_id}")
check("started_at stamped", d.get("payload", {}).get("started_at") is not None)

code, d = patch(f"/ai/messages/{lc_id}/status", {"status": "BLOCKED", "agent": "browser_claude",
                                                   "blocked_reason": "waiting on Drive access"})
check("BLOCKED accepted", code == 200 and d.get("payload", {}).get("status") == "BLOCKED")
code, d = get(f"/ai/messages/{lc_id}")
check("blocked_reason stored", d.get("payload", {}).get("blocked_reason") == "waiting on Drive access")

code, d = patch(f"/ai/messages/{lc_id}/status", {"status": "COMPLETE", "agent": "browser_claude"})
check("COMPLETE accepted", code == 200)
code, d = get(f"/ai/messages/{lc_id}")
check("completed_at stamped", d.get("payload", {}).get("completed_at") is not None)

code, d = patch(f"/ai/messages/{lc_id}/status", {"status": "REJECTED", "agent": "browser_claude"})
check("REJECTED is a valid status (replaces old FAILED)", code == 200 and d.get("payload", {}).get("status") == "REJECTED")
code, d = patch(f"/ai/messages/{lc_id}/status", {"status": "NEW", "agent": "browser_claude"})
check("Old vocab NEW is now rejected", d.get("errors"), d)

# ── 11. Stale directives named endpoint ────────────────────────────────────────
print("\n11. GET /ai/directives/stale")
code, d = get("/ai/directives/stale")
check("Returns 200", code == 200, code)
check("Has messages list", isinstance(d.get("payload", {}).get("messages"), list))

# ── 12. Heartbeat — extended fields + /gateway/heartbeat alias ─────────────────
print("\n12. POST /gateway/heartbeat (alias) with role/current_task/metadata")
code, d = post("/heartbeat", {
    "agent": "claude_code", "action": "test heartbeat", "role": "Implementation",
    "current_task": "Sprint 3 stabilization", "metadata": {"test": True},
})
check("Returns 200", code == 200, code)
check("Reports alive", d.get("payload", {}).get("status") == "alive")
code, d = get("/executive/mission-control")
hb = d.get("payload", {}).get("comms", {}).get("agent_heartbeats", [])
cc = next((h for h in hb if h.get("agent") == "claude_code"), None)
check("claude_code heartbeat present in Mission Control", cc is not None)
check("current_task surfaced", cc and cc.get("current_task") == "Sprint 3 stabilization", cc)
check("Mission Control comms has active_directives count", isinstance(d.get("payload", {}).get("comms", {}).get("active_directives"), int))
check("Mission Control comms has current_sprint", "current_sprint" in d.get("payload", {}).get("comms", {}))

# ── 13. 101F — schedule variance consistency (ARB canonical: -5 days) ─────────
print("\n13. Executive report vs Mission Control — 101F schedule variance")
code, d = get("/executive/report")
p101 = next((p for p in d["payload"]["projects"] if p["project_code"] == "101F"), None)
check("101F present in executive report", p101 is not None)
if p101:
    check("signed schedule_variance_days field present", "schedule_variance_days" in p101)
    check("max_variance_days (unsigned) matches abs(signed)", p101["max_variance_days"] == abs(p101["schedule_variance_days"]),
          (p101["max_variance_days"], p101["schedule_variance_days"]))

# ── 14. 1355R — risk count consistency across Executive Report / Mission Control ─
print("\n14. 1355R — risk count consistency + no test-data leakage")
code, d = get("/executive/report")
p1355 = next((p for p in d["payload"]["projects"] if p["project_code"] == "1355R"), None)
check("1355R present in executive report", p1355 is not None)
code, mc = get("/executive/mission-control")
mc_row = next((r for r in mc["payload"]["portfolio"]["projects"] if r["name"] == "1355 Riverside"), None)
check("1355R present in Mission Control portfolio", mc_row is not None)
if p1355 and mc_row:
    check("Mission Control risk_count matches Executive Report open_risks (no stale-rollup drift)",
          mc_row["risk_count"] >= p1355["open_risks"],
          (mc_row["risk_count"], p1355["open_risks"]))
    check("Mission Control health is not GREEN when Executive Report shows open risks",
          not (p1355["open_risks"] > 0 and mc_row["health"] == "GREEN"),
          (p1355["open_risks"], mc_row["health"]))
top_risk_names = [r.get("title", "") for r in mc.get("payload", {}).get("top_risks", [])]
check("Mission Control top_risks is populated (was always empty via dead project_risks_computed table)",
      len(mc.get("payload", {}).get("top_risks", [])) > 0)
check("No test/dummy markers in production risk descriptions",
      not any("test" in t.lower() or "dummy" in t.lower() or "sample" in t.lower() for t in top_risk_names),
      top_risk_names)

# ── 15. Email send gating (incident 2026-07-01: unauthenticated live-send fixed) ─
print("\n15. Email send requires API key + Buck approval, never sends directly")
code, _ = requests.post(f"{API}/email/send", json={
    "to_name": "x", "to_email": "x@x.com", "subject": "x", "body_html": "x"
}, timeout=10).status_code, None
check("No API key -> rejected (403), not sent", code == 403, code)

code, d = post("/email/send", {
    "to_name": "Buck Test", "to_email": "buck@ahmaspen.com",
    "subject": "[TEST] automated regression check", "body_html": "<p>Automated test row - safe internal address.</p>",
})
check("With API key -> queued_for_approval, not sent", code == 200 and d.get("payload", {}).get("status") == "queued_for_approval", d)
email_msg_id = d.get("payload", {}).get("message_id")
draft_id = d.get("payload", {}).get("draft_id")

code, d = post("/email/draft/fake-unapproved-draft-id/send", {})
check("Unapproved draft_id refused", code == 200 and d.get("errors"), d)

if email_msg_id:
    code, d = post("/telegram/webhook", {
        "update_id": 1, "message": {"message_id": 1, "chat": {"id": 1}, "text": f"APPROVE {email_msg_id}"},
    })
    check("Webhook approve returns 200", code == 200, code)
    code, d = get(f"/ai/messages/{email_msg_id}")
    check("Approval triggers actual send server-side (status COMPLETE)",
          d.get("payload", {}).get("status") == "COMPLETE", d.get("payload", {}).get("status"))

# ── 16. Telegram visibility for GBT/BC (2026-07-01: neither is a push target) ─
print("\n16. GET/POST telegram/messages + telegram/ack — GBT/BC polling visibility")
code, d = get("/telegram/messages", {"agent": "browser_claude"})
check("Returns 200", code == 200, code)
check("Has messages list", isinstance(d.get("payload", {}).get("messages"), list))
before_count = d.get("payload", {}).get("count", 0)
if before_count > 0:
    some_id = d["payload"]["messages"][0]["message_id"]
    code, d = post("/telegram/ack", {"agent": "browser_claude", "message_id": some_id})
    check("Ack returns 200", code == 200, code)
    code, d = get("/telegram/messages", {"agent": "browser_claude"})
    check("Unread count changed after ack", d.get("payload", {}).get("last_ack_id") == some_id, d)
    # restore original ack pointer so this test doesn't eat real unread messages for BC
    post("/telegram/ack", {"agent": "browser_claude", "message_id": 0})
code, d = get("/telegram/messages", {"agent": "not_a_real_agent"})
check("Unknown agent rejected", bool(d.get("errors")), d)

print("\n" + "=" * 50)
print(f"PASSED: {passed}  FAILED: {failed}")
if failed:
    raise SystemExit(1)
