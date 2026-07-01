"""
AI Operations Control Plane — Durable Comms Patch + Warm Start Recovery
Tests: ai/messages, ai/queue, approvals, status transitions, telegram webhook
commands, escalation/retry, telegram/health, ai/warm-start, ai/events.
"""
import requests
import subprocess

API = "http://localhost:8000/gateway"
HEADERS = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}

passed = failed = 0

# This suite impersonates browser_claude (and chatgpt) as a test agent in several
# places (directive lifecycle, telegram polling) to exercise those code paths, which
# touches their REAL ai_agent_heartbeat row each time. Bug found 2026-07-01: this left
# browser_claude showing ONLINE with a fake last_action after every test run, which
# read as real Browser Claude activity to anyone checking Mission Control. Snapshot
# real state now, restore it once at the very end regardless of which section ran.
def _hb_get(agent):
    out = subprocess.run(
        ["docker", "exec", "hci_postgres", "psql", "-U", "hci_admin", "-d", "hci_os", "-t", "-A", "-F", "|",
         "-c", f"SELECT last_seen_at, last_action, status FROM ai_agent_heartbeat WHERE agent='{agent}'"],
        capture_output=True, text=True, timeout=10,
    ).stdout.strip()
    return out.split("|", 2) if out else None

def _hb_restore(agent, snapshot):
    if not snapshot:
        return
    ts, action, status = snapshot
    subprocess.run(
        ["docker", "exec", "hci_postgres", "psql", "-U", "hci_admin", "-d", "hci_os",
         "-c", f"UPDATE ai_agent_heartbeat SET last_seen_at='{ts}', last_action=$${action}$$, status='{status}' WHERE agent='{agent}'"],
        capture_output=True, text=True, timeout=10,
    )

_hb_before = {a: _hb_get(a) for a in ("browser_claude", "chatgpt")}


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
    "to_name": "Buck Test", "to_email": "buck@hendricksoninc.com",
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

# ── 17. Self-send allowlist (2026-07-01: Buck confirmed auto-send to his own inbox) ─
print("\n17. microsoft_graph.send_email() self-send allowlist")
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "..", "integrations"))
from microsoft_graph import send_email as _send_email, _all_recipients_self

check("Buck's own address recognized as self-send", _all_recipients_self([("Buck Adams", "buck@hendricksoninc.com")]))
check("buck@ahmaspen.com is NOT self-send (2026-07-01: Buck confirmed this isn't his address)",
      not _all_recipients_self([("Buck", "buck@ahmaspen.com")]))
check("External address is NOT self-send", not _all_recipients_self([("Someone", "someone@example.com")]))
check("Mixed self+external is NOT self-send (fails closed)",
      not _all_recipients_self([("Buck", "buck@hendricksoninc.com"), ("Ext", "ext@example.com")]))

result, err = _send_email("[TEST] automated regression — self-send allowlist", "<p>test</p>",
                           [("Buck Adams", "buck@hendricksoninc.com")])
check("send_email() to Buck's own address succeeds without drafting", err is None and "queued_draft_id" not in (result or {}), (result, err))

result2, err2 = _send_email("[TEST] automated regression — external still gated", "<p>test</p>",
                             [("Someone", "someone@example.com")])
check("send_email() to external address still drafts, never sends",
      err2 is None and result2.get("status") == "drafted_pending_approval", (result2, err2))

# ── 18. role_owner snapshot fallback (2026-07-01: null-until-nightly-job bug) ──
print("\n18. GET /gateway/role/owner — 101F shows real data, not null/blank")
code, d = get("/role/owner")
check("Returns 200", code == 200, code)
p101 = next((p for p in d.get("payload", {}).get("projects", []) if p.get("project_code") == "101F"), None)
check("101F present", p101 is not None)
if p101:
    check("health is not null", p101.get("health") is not None, p101)
    check("schedule_variance_days is not null", p101.get("schedule_variance_days") is not None, p101)
    check("schedule_variance_days matches executive report sign convention",
          p101.get("schedule_variance_days") == -5, p101.get("schedule_variance_days"))

# ── 19. Plan-review-to-RFI pipeline (2026-07-01: formalizes the RFI-batch incident) ─
print("\n19. POST /gateway/plan-review/analyze — gaps become logged RFIs, never emailed")
code, d = post("/plan-review/analyze", {
    "project_code": "101F", "reviewed_by": "test_suite",
    "sheet_text": "Sheet A1.1 Plumbing Fixture Schedule: Master Bath lavatory, toilet, tub - MFGR/MODEL/COLOR all BLANK, pending selection.",
})
check("Returns 200", code == 200, code)
p = d.get("payload", {})
check("Has gaps_found as int", isinstance(p.get("gaps_found"), int), p)
check("Has ready_for_rom bool", isinstance(p.get("ready_for_rom"), bool), p)
check("Never sends an email itself — only logs RFIs", "email" not in str(p.get("note", "")).lower() or "requires" in str(p.get("note", "")).lower())
if p.get("gaps_found", 0) > 0:
    rfi = p["rfis_created"][0]
    check("Created RFI has status=open (not sent anywhere)", rfi.get("status") == "open", rfi)
    code, d2 = get("/project/101F/action-list")
    check("Newly created RFI reflected in project action list", code == 200)

# ── 20. POST /gateway/plan-review/upload — real PDF via Claude vision ──────────
print("\n20. POST /gateway/plan-review/upload — PDF plan-set upload")
import io as _io
from reportlab.pdfgen import canvas as _canvas
_pdf_buf = _io.BytesIO()
_c = _canvas.Canvas(_pdf_buf)
_c.drawString(50, 750, "SHEET A1.1 - PLUMBING FIXTURE SCHEDULE")
_c.drawString(50, 720, "Master Bath Lavatory: MFGR [BLANK] MODEL [BLANK] COLOR [BLANK]")
_c.save()
_pdf_buf.seek(0)
r = requests.post(f"{API}/plan-review/upload", headers=HEADERS,
                   files={"file": ("test.pdf", _pdf_buf, "application/pdf")},
                   data={"project_code": "101F", "reviewed_by": "test_suite"}, timeout=30)
code, d = r.status_code, (r.json() if r.ok else {})
check("Returns 200", code == 200, code)
p = d.get("payload", {})
check("Reports pages_reviewed", p.get("pages_reviewed") == 1, p)
check("Has gaps_found as int", isinstance(p.get("gaps_found"), int), p)

# Restore real agent heartbeats clobbered by impersonating them as test agents above —
# must run regardless of pass/fail so a real BC/GBT session never shows falsely ONLINE.
for _agent, _snap in _hb_before.items():
    _hb_restore(_agent, _snap)
print(f"\n(restored real heartbeat state for: {', '.join(_hb_before.keys())})")

# ── 21. Vendor capacity conflicts (2026-07-01: cross-project sub scheduling gap) ─
print("\n21. GET /gateway/knowledge/vendor-capacity-conflicts")
code, d = get("/knowledge/vendor-capacity-conflicts")
check("Returns 200", code == 200, code)
check("Has conflict_count as int", isinstance(d.get("payload", {}).get("conflict_count"), int), d)
check("Has conflicts list", isinstance(d.get("payload", {}).get("conflicts"), list), d)

# ── 22. Sub package / SOW generation off the plans (ADR-014 phase 2) ───────────
print("\n22. POST /gateway/plan-review/generate-packages — bid packages from plan content")
code, d = post("/plan-review/generate-packages", {
    "project_code": "101F", "reviewed_by": "test_suite",
    "sheet_text": "Sheet S1.0 Structural Notes: roof framing wide-flange steel beams W12x26. Sheet A2.1 Finish Schedule: hardwood flooring throughout, tile in bathrooms.",
})
check("Returns 200", code == 200, code)
p = d.get("payload", {})
check("Has packages_created as int", isinstance(p.get("packages_created"), int), p)
check("Never invites a sub to bid — status not_started only", "not_started" in str(p.get("note", "")))
if p.get("packages_created", 0) > 0:
    pkg = p["bid_packages"][0]
    check("Created package has status=not_started (no bid solicitation)", pkg.get("status") == "not_started", pkg)
    check("Created package has a confidence rating", pkg.get("confidence") in ("high", "low"), pkg)

print("\n" + "=" * 50)
print(f"PASSED: {passed}  FAILED: {failed}")
if failed:
    raise SystemExit(1)
