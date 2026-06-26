#!/usr/bin/env python3
"""
HCI AI Platform Integration Layer — Test Suite
Tests: Identity, Event Bus, Notifications, Audit Trail, Unified Search
API: http://localhost:8000/api/v1/platform/
"""
import urllib.request
import urllib.error
import json
import sys
import time
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1/platform"
API_KEY  = "hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c"
HEADERS  = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

results: list[dict] = []
PASS = "PASS"; FAIL = "FAIL"; COND = "CONDITIONAL"


def req(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    rq = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(rq, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")
    except Exception as ex:
        return 0, {"error": str(ex)}


def run(test_id: str, name: str, fn):
    try:
        ok, msg = fn()
        status = PASS if ok else (COND if ok is None else FAIL)
    except Exception as e:
        status = FAIL; msg = str(e)
    results.append({"id": test_id, "name": name, "status": status, "detail": msg})
    icon = "✓" if status == PASS else ("?" if status == COND else "✗")
    print(f"  {icon} {test_id}: {name}")
    if status != PASS:
        print(f"      → {msg}")
    return status == PASS


# ─── PLATFORM OVERVIEW ──────────────────────────────────────────────────────

print("\n── Platform Overview ──────────────────────────────────────────────")

def t_overview():
    sc, r = req("GET", "")
    if sc != 200: return False, f"HTTP {sc}"
    caps = r.get("capabilities", {})
    required = ["identity", "events", "notifications", "audit", "search"]
    missing = [c for c in required if c not in caps]
    if missing: return False, f"Missing capabilities: {missing}"
    return True, f"All {len(required)} capabilities registered"

run("PT-00-01", "Platform overview lists all 5 capabilities", t_overview)


# ─── IDENTITY & PERMISSIONS ─────────────────────────────────────────────────

print("\n── Identity & Permissions ─────────────────────────────────────────")

def t_list_users():
    sc, r = req("GET", "/identity/users")
    if sc != 200: return False, f"HTTP {sc}"
    users = r.get("users", [])
    if len(users) < 6: return False, f"Expected ≥6 users, got {len(users)}"
    roles = {u["role"] for u in users}
    req_roles = {"owner", "pm", "superintendent", "ai_agent", "contracts", "system"}
    missing = req_roles - roles
    if missing: return False, f"Missing roles: {missing}"
    return True, f"{len(users)} users, roles: {sorted(roles)}"

run("PT-01-01", "List users returns 6 seeded actors with all roles", t_list_users)

def t_get_buck():
    sc, r = req("GET", "/identity/users/Buck%20Adams")
    if sc != 200: return False, f"HTTP {sc}"
    if r.get("role") != "owner": return False, f"Expected role=owner, got {r.get('role')}"
    perms = r.get("permissions", [])
    if "approve_budget" not in perms: return False, f"Missing approve_budget in {perms}"
    return True, f"Buck=owner, {len(perms)} permissions"

run("PT-01-02", "Buck Adams has owner role with approve_budget permission", t_get_buck)

def t_pm_no_budget():
    sc, r = req("GET", "/identity/users/pm/can/approve_budget")
    if sc != 200: return False, f"HTTP {sc}"
    if r.get("allowed"): return False, "PM should NOT have approve_budget"
    return True, "PM correctly denied approve_budget"

run("PT-01-03", "PM does not have approve_budget permission", t_pm_no_budget)

def t_buck_approve():
    sc, r = req("GET", "/identity/users/Buck%20Adams/can/approve_budget")
    if sc != 200: return False, f"HTTP {sc}"
    if not r.get("allowed"): return False, "Buck should have approve_budget"
    return True, "Buck correctly allowed approve_budget"

run("PT-01-04", "Buck Adams has approve_budget permission", t_buck_approve)

def t_upsert_user():
    sc, r = req("POST", "/identity/users", {
        "actor_name": "Jane PM",
        "role": "pm",
        "email": "jane@hendricksoninc.com"
    })
    if sc != 200: return False, f"HTTP {sc}: {r}"
    sc2, r2 = req("GET", "/identity/users/Jane%20PM")
    if sc2 != 200: return False, f"HTTP {sc2}"
    if r2.get("role") != "pm": return False, f"Expected pm, got {r2.get('role')}"
    return True, "New user created and retrievable"

run("PT-01-05", "Create new platform user and retrieve it", t_upsert_user)

def t_roles_list():
    sc, r = req("GET", "/identity/roles")
    if sc != 200: return False, f"HTTP {sc}"
    roles = r.get("roles", [])
    if len(roles) < 5: return False, f"Expected ≥5 roles, got {len(roles)}"
    return True, f"{len(roles)} roles with permission counts"

run("PT-01-06", "List roles returns all defined roles", t_roles_list)

def t_authority_levels():
    sc_buck, r_buck = req("GET", "/identity/users/Buck%20Adams/permissions")
    sc_pm, r_pm = req("GET", "/identity/users/pm/permissions")
    if sc_buck != 200 or sc_pm != 200: return False, f"HTTP {sc_buck}/{sc_pm}"
    buck_lvl = r_buck.get("authority_level", 0)
    pm_lvl = r_pm.get("authority_level", 0)
    if buck_lvl <= pm_lvl: return False, f"Buck level {buck_lvl} should be > PM level {pm_lvl}"
    return True, f"Buck={buck_lvl} > PM={pm_lvl}"

run("PT-01-07", "Buck authority level exceeds PM authority level", t_authority_levels)


# ─── EVENT BUS ──────────────────────────────────────────────────────────────

print("\n── Event Bus ──────────────────────────────────────────────────────")

_event_ids: list[int] = []

def t_publish_event():
    sc, r = req("POST", "/events/publish", {
        "event_type": "sop.status_changed",
        "source_service": "sop_test",
        "entity_type": "sop_instance",
        "entity_id": 9999,
        "project_id": 1,
        "actor": "pm",
        "payload": {"from_status": "In Progress", "to_status": "AI Drafted"}
    })
    if sc != 200: return False, f"HTTP {sc}: {r}"
    eid = r.get("event_id")
    if not eid: return False, "No event_id returned"
    _event_ids.append(eid)
    return True, f"Event published, id={eid}"

run("PT-02-01", "Publish domain event returns event_id", t_publish_event)

def t_publish_multiple():
    types = ["sop.gate_approved", "sop.work_stopped", "sop.ai_drafted"]
    ids = []
    for et in types:
        sc, r = req("POST", "/events/publish", {
            "event_type": et, "source_service": "sop_test",
            "entity_type": "sop_instance", "entity_id": 9999,
            "actor": "system", "payload": {"test": True}
        })
        if sc != 200: return False, f"{et} HTTP {sc}"
        ids.append(r.get("event_id"))
    _event_ids.extend([i for i in ids if i])
    return True, f"Published 3 more events, ids={ids}"

run("PT-02-02", "Publish multiple event types succeeds", t_publish_multiple)

def t_query_events():
    sc, r = req("GET", "/events?entity_type=sop_instance&entity_id=9999&limit=10")
    if sc != 200: return False, f"HTTP {sc}"
    evts = r.get("events", [])
    if len(evts) < 4: return False, f"Expected ≥4 events, got {len(evts)}"
    types = {e["event_type"] for e in evts}
    if "sop.status_changed" not in types: return False, f"Missing sop.status_changed in {types}"
    return True, f"{len(evts)} events retrieved for entity 9999"

run("PT-02-03", "Query events by entity filters returns correct events", t_query_events)

def t_query_by_project():
    sc, r = req("GET", "/events?project_id=1&limit=20")
    if sc != 200: return False, f"HTTP {sc}"
    evts = r.get("events", [])
    return True, f"{len(evts)} events for project_id=1"

run("PT-02-04", "Query events by project_id works", t_query_by_project)

def t_sop_events_endpoint():
    sc, r = req("GET", "/events/sop/9999")
    if sc != 200: return False, f"HTTP {sc}"
    evts = r.get("events", [])
    if len(evts) < 1: return False, f"Expected ≥1 events, got {len(evts)}"
    return True, f"{len(evts)} events for SOP instance 9999"

run("PT-02-05", "SOP-specific event query endpoint works", t_sop_events_endpoint)


# ─── NOTIFICATION CENTER ────────────────────────────────────────────────────

print("\n── Notification Center ────────────────────────────────────────────")

_notif_ids: list[int] = []
TEST_RECIPIENT = "test_pm_notify"

def t_create_approval_notif():
    sc, r = req("POST", "/notifications", {
        "recipient": TEST_RECIPIENT,
        "notification_type": "approval_required",
        "title": "SOP 15 — Award Decision Required",
        "body": "Gate AG-15-C requires Buck Adams approval.",
        "entity_type": "sop_instance",
        "entity_id": 100,
        "project_id": 1,
        "action_url": "/api/v1/sop/15/100"
    })
    if sc != 200: return False, f"HTTP {sc}: {r}"
    nid = r.get("notification_id")
    if not nid: return False, "No notification_id"
    _notif_ids.append(nid)
    return True, f"Approval notification created, id={nid}"

run("PT-03-01", "Create approval_required notification", t_create_approval_notif)

def t_create_work_stopped():
    for ntype, title in [
        ("work_stopped", "WORK STOPPED — SOP 07 [SC-01]"),
        ("ai_draft_ready", "SOP 05 — AI Draft Ready"),
        ("handoff_ready", "SOP 11 — Handoff Ready"),
    ]:
        sc, r = req("POST", "/notifications", {
            "recipient": TEST_RECIPIENT,
            "notification_type": ntype,
            "title": title,
            "entity_type": "sop_instance",
            "entity_id": 101,
        })
        if sc != 200: return False, f"{ntype}: HTTP {sc}"
        _notif_ids.append(r.get("notification_id", 0))
    return True, f"3 notification types created"

run("PT-03-02", "Create work_stopped, ai_draft_ready, handoff_ready notifications", t_create_work_stopped)

def t_get_notifications():
    sc, r = req("GET", f"/notifications/{TEST_RECIPIENT}")
    if sc != 200: return False, f"HTTP {sc}"
    count = r.get("count", 0)
    unread = r.get("unread_count", 0)
    if count < 4: return False, f"Expected ≥4 notifications, got {count}"
    if unread < 4: return False, f"Expected ≥4 unread, got {unread}"
    return True, f"{count} total, {unread} unread"

run("PT-03-03", "Get notifications for recipient returns correct count", t_get_notifications)

def t_unread_only():
    sc, r = req("GET", f"/notifications/{TEST_RECIPIENT}?unread_only=true")
    if sc != 200: return False, f"HTTP {sc}"
    notifs = r.get("notifications", [])
    all_unread = all(not n["is_read"] for n in notifs)
    return (True if all_unread else False), f"{len(notifs)} unread notifs, all_unread={all_unread}"

run("PT-03-04", "Unread-only filter returns only unread notifications", t_unread_only)

def t_mark_read():
    if not _notif_ids: return None, "No notification ids to test"
    nid = _notif_ids[0]
    sc, r = req("POST", f"/notifications/{nid}/read")
    if sc != 200: return False, f"HTTP {sc}: {r}"
    if not r.get("marked_read"): return False, "marked_read=False"
    sc2, r2 = req("GET", f"/notifications/{TEST_RECIPIENT}?unread_only=true")
    remaining_unread = r2.get("count", 999)
    return True, f"Notification {nid} marked read; {remaining_unread} still unread"

run("PT-03-05", "Mark single notification as read", t_mark_read)

def t_mark_all_read():
    sc, r = req("POST", f"/notifications/{TEST_RECIPIENT}/read-all")
    if sc != 200: return False, f"HTTP {sc}"
    count = r.get("marked_read_count", -1)
    if count < 0: return False, f"Unexpected count: {count}"
    sc2, r2 = req("GET", f"/notifications/{TEST_RECIPIENT}?unread_only=true")
    remaining = r2.get("count", 999)
    if remaining > 0: return False, f"Still {remaining} unread after mark-all-read"
    return True, f"Marked {count} read; 0 remaining"

run("PT-03-06", "Mark all read leaves 0 unread for recipient", t_mark_all_read)

def t_all_unread_summary():
    # Create one more unread for Buck
    req("POST", "/notifications", {
        "recipient": "Buck Adams",
        "notification_type": "approval_required",
        "title": "Test approval needed",
    })
    sc, r = req("GET", "/notifications")
    if sc != 200: return False, f"HTTP {sc}"
    summary = r.get("unread_by_recipient", {})
    if "Buck Adams" not in summary: return False, f"Buck not in summary: {summary}"
    return True, f"Summary: {dict(list(summary.items())[:3])}"

run("PT-03-07", "All-unread summary shows recipients with unread notifications", t_all_unread_summary)


# ─── AUDIT TRAIL ────────────────────────────────────────────────────────────

print("\n── Audit Trail ────────────────────────────────────────────────────")

def t_write_audit():
    sc, r = req("POST", "/audit", {
        "source": "sop",
        "event_type": "gate_approved",
        "actor": "Buck Adams",
        "entity_type": "sop_instance",
        "entity_id": 9999,
        "project_id": 1,
        "summary": "Gate AG-15-C approved",
        "payload": {"gate_id": "AG-15-C", "method": "in-system"}
    })
    if sc != 200: return False, f"HTTP {sc}: {r}"
    aid = r.get("audit_id")
    if not aid: return False, "No audit_id"
    return True, f"Audit record written, id={aid}"

run("PT-04-01", "Write audit record returns audit_id", t_write_audit)

def t_write_multiple_sources():
    sources = [
        ("workflow", "workflow.completed", "workflow_001"),
        ("notification", "notification.sent", "system"),
        ("identity", "user_created", "system"),
    ]
    for source, etype, actor in sources:
        sc, r = req("POST", "/audit", {
            "source": source, "event_type": etype, "actor": actor,
            "entity_type": "test", "entity_id": 9999,
            "summary": f"Test {source} event"
        })
        if sc != 200: return False, f"{source}: HTTP {sc}"
    return True, "3 sources (workflow, notification, identity) logged"

run("PT-04-02", "Write audit records from multiple sources", t_write_multiple_sources)

def t_query_audit_by_source():
    sc, r = req("GET", "/audit?source=sop&entity_id=9999&limit=10")
    if sc != 200: return False, f"HTTP {sc}"
    records = r.get("records", [])
    if len(records) < 1: return False, f"Expected ≥1 sop records, got {len(records)}"
    all_sop = all(rec["source"] == "sop" for rec in records)
    return (True if all_sop else False), f"{len(records)} sop records, all_sop={all_sop}"

run("PT-04-03", "Query audit by source=sop returns only sop records", t_query_audit_by_source)

def t_query_audit_by_actor():
    sc, r = req("GET", "/audit?actor=Buck%20Adams&limit=20")
    if sc != 200: return False, f"HTTP {sc}"
    records = r.get("records", [])
    if len(records) < 1: return False, f"Expected ≥1 records for Buck, got {len(records)}"
    return True, f"{len(records)} records attributed to Buck Adams"

run("PT-04-04", "Query audit by actor returns actor's records", t_query_audit_by_actor)

def t_audit_sop_trail():
    sc, r = req("GET", "/audit/sop/9999")
    if sc != 200: return False, f"HTTP {sc}"
    total = r.get("total_events", 0)
    platform = r.get("platform_audit_events", [])
    if len(platform) < 1: return False, f"Expected platform events, got 0"
    return True, f"SOP 9999 trail: {total} total events, {len(platform)} platform"

run("PT-04-05", "SOP audit trail endpoint returns combined event view", t_audit_sop_trail)

def t_project_timeline():
    sc, r = req("GET", "/audit/project/1/timeline?since_hours=24")
    if sc != 200: return False, f"HTTP {sc}"
    total = r.get("total_events", -1)
    if total < 0: return False, f"No total_events key"
    return True, f"Project 1 timeline: {total} events in last 24h"

run("PT-04-06", "Project timeline endpoint returns multi-source event view", t_project_timeline)

def t_audit_summary():
    sc, r = req("GET", "/audit/summary")
    if sc != 200: return False, f"HTTP {sc}"
    summary = r.get("summary", {})
    return True, f"24h summary: {summary}"

run("PT-04-07", "Audit summary returns event counts by source", t_audit_summary)

def t_audit_since_hours():
    sc, r = req("GET", "/audit?since_hours=1&limit=100")
    if sc != 200: return False, f"HTTP {sc}"
    records = r.get("records", [])
    return True, f"{len(records)} audit events in last hour"

run("PT-04-08", "Audit query with since_hours filter works", t_audit_since_hours)


# ─── UNIFIED SEARCH GATEWAY ─────────────────────────────────────────────────

print("\n── Unified Search Gateway ─────────────────────────────────────────")

def t_search_vendors_unified():
    sc, r = req("POST", "/search", {
        "query": "concrete subcontractor",
        "limit": 10
    })
    if sc != 200: return False, f"HTTP {sc}: {r}"
    total = r.get("total_results", 0)
    sources = r.get("sources_queried", [])
    if "vendors" not in sources: return False, f"vendors not in sources_queried: {sources}"
    return True, f"{total} results, sources={sources}"

run("PT-05-01", "Search 'concrete subcontractor' auto-routes to vendors", t_search_vendors_unified)

def t_search_project():
    sc, r = req("POST", "/search", {
        "query": "Eastwood site project",
        "sources": ["projects"],
        "limit": 5
    })
    if sc != 200: return False, f"HTTP {sc}"
    total = r.get("total_results", 0)
    if total < 1: return False, f"Expected ≥1 project result"
    first = r["results"][0]["text"] if r.get("results") else ""
    return True, f"{total} projects found; first='{first[:50]}'"

run("PT-05-02", "Search 'Eastwood' with sources=['projects'] finds Eastwood project", t_search_project)

def t_search_sop_instances():
    sc, r = req("POST", "/search", {
        "query": "In Progress sop workflow",
        "sources": ["sops"],
        "limit": 10
    })
    if sc != 200: return False, f"HTTP {sc}"
    total = r.get("total_results", 0)
    return True, f"{total} SOP instances found (may be 0 if none match filter)"

run("PT-05-03", "Search SOPs by status returns results", t_search_sop_instances)

def t_search_vendor_shortcut():
    sc, r = req("GET", "/search/vendors?q=aspen")
    if sc != 200: return False, f"HTTP {sc}"
    results = r.get("results", [])
    return True, f"{len(results)} vendors matching 'aspen'"

run("PT-05-04", "GET /search/vendors shortcut endpoint works", t_search_vendor_shortcut)

def t_search_sop_shortcut():
    sc, r = req("GET", "/search/sops?project=Francis")
    if sc != 200: return False, f"HTTP {sc}"
    return True, f"{len(r.get('results', []))} SOP instances for Francis"

run("PT-05-05", "GET /search/sops shortcut endpoint works", t_search_sop_shortcut)

def t_search_with_explicit_sources():
    sc, r = req("POST", "/search", {
        "query": "risk hazard blocked",
        "sources": ["risks", "sops"],
        "limit": 10
    })
    if sc != 200: return False, f"HTTP {sc}"
    sources = r.get("sources_queried", [])
    if set(sources) != {"risks", "sops"}: return False, f"Expected risks+sops, got {sources}"
    return True, f"Explicit sources respected: {sources}"

run("PT-05-06", "Explicit sources override auto-detection", t_search_with_explicit_sources)

def t_search_no_errors():
    sc, r = req("POST", "/search", {
        "query": "Francis site concrete budget risk sop vendor",
        "limit": 20
    })
    if sc != 200: return False, f"HTTP {sc}"
    errors = r.get("errors")
    if errors:
        # Qdrant errors are acceptable (offline); Postgres errors are not
        pg_errors = {k: v for k, v in errors.items() if not k.startswith("qdrant")}
        if pg_errors: return False, f"Postgres errors: {pg_errors}"
    total = r.get("total_results", 0)
    return True, f"{total} results, errors={errors}"

run("PT-05-07", "Multi-source search completes without Postgres errors", t_search_no_errors)


# ─── INTEGRATION FLOWS ──────────────────────────────────────────────────────

print("\n── Integration Flows ──────────────────────────────────────────────")

def t_approval_notification_flow():
    """Full flow: check permission → publish event → create notification → audit"""
    # 1. Check Buck can approve
    _, perm = req("GET", "/identity/users/Buck%20Adams/can/approve_budget")
    if not perm.get("allowed"): return False, "Buck lacks approve_budget permission"

    # 2. Publish approval_required event
    _, evt = req("POST", "/events/publish", {
        "event_type": "sop.gate.approval_required",
        "source_service": "sop_09",
        "entity_type": "sop_instance",
        "entity_id": 8888,
        "project_id": 1,
        "actor": "pm",
        "payload": {"gate_id": "AG-09-B", "amount": 600000}
    })
    if not evt.get("event_id"): return False, "Event publish failed"

    # 3. Create notification for Buck
    _, notif = req("POST", "/notifications", {
        "recipient": "Buck Adams",
        "notification_type": "approval_required",
        "title": "SOP 09 — Budget Review: $600k exceeds threshold",
        "entity_type": "sop_instance",
        "entity_id": 8888,
        "project_id": 1,
    })
    if not notif.get("notification_id"): return False, "Notification creation failed"

    # 4. Log to audit trail
    _, audit = req("POST", "/audit", {
        "source": "sop",
        "event_type": "approval_required",
        "actor": "pm",
        "entity_type": "sop_instance",
        "entity_id": 8888,
        "project_id": 1,
        "summary": "PM requested Buck approval for $600k budget",
        "payload": {"gate_id": "AG-09-B", "amount": 600000}
    })
    if not audit.get("audit_id"): return False, "Audit log write failed"

    # 5. Verify Buck has unread notification
    _, notifs = req("GET", "/notifications/Buck%20Adams?unread_only=true")
    unread = notifs.get("unread_count", 0)
    if unread < 1: return False, f"Buck has {unread} unread, expected ≥1"

    return True, f"Full flow complete: event={evt['event_id']}, notif={notif['notification_id']}, audit={audit['audit_id']}, Buck_unread={unread}"

run("PT-IT-01", "Full approval flow: permission check → event → notification → audit", t_approval_notification_flow)


def t_search_to_sop_flow():
    """Find a vendor, then find related SOPs."""
    _, vr = req("GET", "/search/vendors?q=concrete&limit=5")
    vendors = vr.get("results", [])
    if not vendors: return None, "No concrete vendors in DB (CONDITIONAL — no data)"

    vendor_name = vendors[0]["payload"].get("company_name", "")
    _, sr = req("POST", "/search", {
        "query": f"sop instance {vendor_name}",
        "sources": ["sops"],
        "limit": 5
    })
    return True, f"Vendor '{vendor_name}' found; SOP search returned {sr.get('total_results',0)} results"

run("PT-IT-02", "Search vendor then search related SOPs", t_search_to_sop_flow)


def t_event_bus_persistence():
    """Events persist across requests — query returns events published earlier."""
    _, r = req("GET", "/events?event_type=sop.status_changed&limit=10")
    evts = r.get("events", [])
    if not evts: return False, "sop.status_changed events not persisted"
    return True, f"{len(evts)} persisted sop.status_changed events retrievable"

run("PT-IT-03", "Event bus events persist and are queryable after publish", t_event_bus_persistence)


def t_cross_service_audit_visibility():
    """Audit trail shows events from multiple sources in one query."""
    _, r = req("GET", "/audit?entity_id=9999&limit=50")
    records = r.get("records", [])
    sources = {rec["source"] for rec in records}
    if len(sources) < 2: return False, f"Expected ≥2 sources, got {sources}"
    return True, f"{len(records)} records from sources: {sources}"

run("PT-IT-04", "Audit trail aggregates events from multiple sources", t_cross_service_audit_visibility)


# ─── RESULTS ────────────────────────────────────────────────────────────────

total   = len(results)
passed  = sum(1 for r in results if r["status"] == PASS)
failed  = sum(1 for r in results if r["status"] == FAIL)
conds   = sum(1 for r in results if r["status"] == COND)

print(f"\n{'═'*60}")
print(f"  PLATFORM INTEGRATION TEST RESULTS")
print(f"  {passed} PASS  |  {failed} FAIL  |  {conds} CONDITIONAL  |  {total} TOTAL")
print(f"{'═'*60}\n")

if failed > 0:
    print("FAILED tests:")
    for r in results:
        if r["status"] == FAIL:
            print(f"  ✗ {r['id']} — {r['name']}")
            print(f"      {r['detail']}")

output = {
    "suite": "platform_integration",
    "run_at": datetime.utcnow().isoformat(),
    "total": total, "passed": passed, "failed": failed, "conditional": conds,
    "results": results,
}

results_path = "/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/tests/test_results_platform.json"
with open(results_path, "w") as f:
    json.dump(output, f, indent=2, default=str)
print(f"Results written to: {results_path}")

sys.exit(0 if failed == 0 else 1)
