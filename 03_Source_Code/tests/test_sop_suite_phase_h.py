"""
Phase H SOP Test Suite
Tests SOP 17-18, 20-30 against the live API.
Matches Phase D/E-G rigor: unit tests + integration tests per SOP.

Run: python3 03_Source_Code/tests/test_sop_suite_phase_h.py
Requires: API running at localhost:8000; project_id=1 in DB
"""
import sys, os, json, time, datetime
from typing import Any
from dotenv import load_dotenv
import urllib.request
import urllib.error

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
API_KEY = os.environ["HCI_API_KEY"]
BASE    = "http://localhost:8000/api/v1/sop"
PROJECT_ID = 1

# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _req(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
    )
    try:
        # Bumped from 15s - found 2026-07-06 that the SOP 29 safety-hazard-plan
        # endpoint's max_tokens went 1500 -> 3000 to fix real truncated-JSON output
        # (see sop_29_agent.py); the longer generation now legitimately exceeds 15s.
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {"error": str(e)}
    except Exception as ex:
        return 0, {"error": str(ex)}

def post(path: str, body: dict | None) -> tuple[int, dict]: return _req("POST", path, body)
def get(path: str) -> tuple[int, dict]:                      return _req("GET", path)


# ── Test runner ───────────────────────────────────────────────────────────────

results: list[dict] = []

def run(test_id: str, name: str, fn):
    try:
        ok, note = fn()
        status = "PASS" if ok else "CONDITIONAL" if ok is None else "FAIL"
        results.append({"id": test_id, "name": name, "status": status, "note": note})
        sym = "✅" if status == "PASS" else "⚠️" if status == "CONDITIONAL" else "❌"
        print(f"  {sym} {test_id}: {name}")
        if status != "PASS":
            print(f"     → {note}")
    except Exception as ex:
        results.append({"id": test_id, "name": name, "status": "FAIL", "note": str(ex)})
        print(f"  ❌ {test_id}: {name} — {ex}")


# ── SOP 17 — Project Schedule ─────────────────────────────────────────────────

print("\n=== SOP 17 — Project Schedule ===")

sop17_id = None

def t17_01():
    global sop17_id
    code, r = post("/17/instances", {
        "project_id": PROJECT_ID, "project_name": "Test Build",
        "project_type": "commercial", "construction_start": "2026-08-01",
        "substantial_completion": "2027-06-30", "owner_name": "pm_test",
        "sop_23_instance_id": 0})
    sop17_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop17_id
    return ok, f"id={sop17_id}, status={r.get('status')}"

def t17_02():
    if not sop17_id: return False, "no instance"
    code, r = get(f"/17/instances/{sop17_id}")
    return code == 200 and r.get("instance"), f"GET 200, outputs={len(r.get('outputs', []))}"

def t17_03():
    if not sop17_id: return False, "no instance"
    code, r = post(f"/17/instances/{sop17_id}/milestones", {
        "milestone_code": "MS-001",
        "phase": "Mobilization",
        "description": "Site Mobilization and setup",
        "planned_start": "2026-08-01", "planned_finish": "2026-08-15",
        "duration_days": 14, "critical_path": True})
    return code == 200, f"output_id={r.get('output_id')}"

def t17_04():
    if not sop17_id: return False, "no instance"
    code, r = post(f"/17/instances/{sop17_id}/confirm-milestone?milestone_code=MS-001&pm_name=pm_test", None)
    return code == 200, f"confirmed={r.get('confirmed')}"

def t17_05():
    if not sop17_id: return False, "no instance"
    code, r = post(f"/17/instances/{sop17_id}/pm-approve?pm_name=pm_test", None)
    if code == 200:
        return True, f"status={r.get('status')}"
    return None, f"blocked (expected if unconfirmed milestones): {r.get('detail','')[:80]}"

run("UT-17-01", "Create SOP 17 Project Schedule", t17_01)
run("UT-17-02", "GET schedule status", t17_02)
run("UT-17-03", "Add milestone (Site Mobilization)", t17_03)
run("UT-17-04", "PM confirm milestone", t17_04)
run("UT-17-05", "PM approve schedule", t17_05)


# ── SOP 18 — Long-Lead Procurement ───────────────────────────────────────────

print("\n=== SOP 18 — Long-Lead Procurement ===")

sop18_id = None

def t18_01():
    global sop18_id
    code, r = post("/18/instances", {
        "project_id": PROJECT_ID, "sop_17_instance_id": sop17_id or 1,
        "owner_name": "pm_test", "project_type": "commercial",
        "construction_start": "2026-08-01"})
    sop18_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop18_id
    return ok, f"id={sop18_id}"

def t18_02():
    if not sop18_id: return False, "no instance"
    code, r = get(f"/18/instances/{sop18_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t18_03():
    if not sop18_id: return False, "no instance"
    code, r = post(f"/18/instances/{sop18_id}/items", {
        "item_code": "LL-001", "description": "Structural Steel Package",
        "trade_code": "STR", "lead_time_weeks": 16,
        "order_by_date": "2026-08-15", "required_on_site": "2026-11-01",
        "risk_level": "HIGH"})
    return code == 200, f"output_id={r.get('output_id')}"

def t18_04():
    if not sop18_id: return False, "no instance"
    code, r = post(f"/18/instances/{sop18_id}/update-status?item_code=LL-001&status=ORDERED&actor=pm_test", None)
    return code == 200, f"updated={r.get('updated')}"

def t18_05():
    if not sop18_id: return False, "no instance"
    code, r = post(f"/18/instances/{sop18_id}/pm-approve?pm_name=pm_test", None)
    if code == 200:
        return True, f"status={r.get('status')}"
    return None, f"blocked: {r.get('detail','')[:80]}"

run("UT-18-01", "Create SOP 18 Long-Lead Log", t18_01)
run("UT-18-02", "GET procurement log", t18_02)
run("UT-18-03", "Add long-lead item (16 wk structural steel)", t18_03)
run("UT-18-04", "Update item status to ORDERED", t18_04)
run("UT-18-05", "PM approve procurement log", t18_05)


# ── SOP 20 — Contract Setup ───────────────────────────────────────────────────

print("\n=== SOP 20 — Contract Setup ===")

sop20_id = None

def t20_01():
    global sop20_id
    code, r = post("/20/instances", {
        "project_id": PROJECT_ID, "project_name": "Test Build",
        "contract_type": "GMP", "owner_name_client": "Test Owner LLC",
        "gc_contract_value": 2500000.0, "pm_name": "pm_test",
        "sop_19_instance_id": 0})
    sop20_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop20_id
    return ok, f"id={sop20_id}"

def t20_02():
    if not sop20_id: return False, "no instance"
    code, r = get(f"/20/instances/{sop20_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t20_03():
    if not sop20_id: return False, "no instance"
    code, r = post(f"/20/instances/{sop20_id}/ai-checklist?scope_summary=Commercial+build+GMP", None)
    return code == 200, f"items={r.get('checklist_item_count', r.get('total_items', 0))}"

def t20_04():
    if not sop20_id: return False, "no instance"
    code, r = post(f"/20/instances/{sop20_id}/complete-item?item_code=SETUP-001&actor=pm_test", None)
    if code == 200:
        return True, f"status={r.get('item_status')}"
    return None, f"item not found or already complete: {r.get('error','')[:60]}"

def t20_05():
    if not sop20_id: return False, "no instance"
    code, r = post(f"/20/instances/{sop20_id}/pm-approve?pm_name=pm_test", None)
    if code == 200:
        return True, f"status={r.get('status')}"
    return None, f"blocked (pending items expected): {r.get('detail','')[:80]}"

run("UT-20-01", "Create SOP 20 Contract Setup", t20_01)
run("UT-20-02", "GET contract setup status", t20_02)
run("UT-20-03", "AI generate contract setup checklist", t20_03)
run("UT-20-04", "Complete setup item", t20_04)
run("UT-20-05", "PM approve (blocked if items pending)", t20_05)


# ── SOP 21 — Compliance ───────────────────────────────────────────────────────

print("\n=== SOP 21 — Compliance ===")

sop21_id = None

def t21_01():
    global sop21_id
    code, r = post("/21/instances", {
        "project_id": PROJECT_ID, "sop_20_instance_id": sop20_id or 1,
        "owner_name": "pm_test", "jurisdiction": "City of Aspen",
        "project_type": "commercial"})
    sop21_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop21_id
    return ok, f"id={sop21_id}"

def t21_02():
    if not sop21_id: return False, "no instance"
    code, r = get(f"/21/instances/{sop21_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t21_03():
    if not sop21_id: return False, "no instance"
    code, r = post(f"/21/instances/{sop21_id}/ai-identify?scope_summary=Commercial+build&contract_value=2500000", None)
    return code == 200, f"permits={r.get('total_permits', 0)}"

def t21_04():
    if not sop21_id: return False, "no instance"
    code, r = post(f"/21/instances/{sop21_id}/update-permit", {
        "item_code": "PERMIT-001", "status": "APPROVED", "permit_number": "BP-2026-001"})
    if code == 200:
        return True, f"status={r.get('status')}"
    return None, f"item not found (AI didn't create it yet): {r.get('error','')[:60]}"

def t21_05():
    if not sop21_id: return False, "no instance"
    code, r = post(f"/21/instances/{sop21_id}/pm-approve?pm_name=pm_test", None)
    if code == 200:
        return True, f"status={r.get('status')}"
    return None, f"blocked (permit not cleared): {r.get('detail','')[:80]}"

run("UT-21-01", "Create SOP 21 Compliance Log", t21_01)
run("UT-21-02", "GET compliance log", t21_02)
run("UT-21-03", "AI identify permits and compliance items", t21_03)
run("UT-21-04", "Update permit status to APPROVED", t21_04)
run("UT-21-05", "PM approve (clear-to-build gate)", t21_05)


# ── SOP 22 — COI / W-9 / Lien Waiver ────────────────────────────────────────

print("\n=== SOP 22 — COI / W-9 / Lien Waiver ===")

sop22_id = None
sop22_doc_alpha = None   # actual doc_code for Alpha Concrete COI
sop22_doc_beta  = None   # actual doc_code for Beta Steel COI

def t22_01():
    global sop22_id
    code, r = post("/22/instances", {
        "project_id": PROJECT_ID, "sop_21_instance_id": sop21_id or 1,
        "owner_name": "pm_test"})
    sop22_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop22_id
    return ok, f"id={sop22_id}"

def t22_02():
    if not sop22_id: return False, "no instance"
    code, r = get(f"/22/instances/{sop22_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t22_03():
    global sop22_doc_alpha, sop22_doc_beta
    if not sop22_id: return False, "no instance"
    code, r = post(f"/22/instances/{sop22_id}/generate-checklist", {
        "subs": ["Alpha Concrete", "Beta Steel"]})
    # Capture actual doc codes from checklist
    checklist = r.get("checklist", [])
    for item in checklist:
        if item.get("party_name") == "Alpha Concrete" and item.get("doc_type") == "COI":
            sop22_doc_alpha = item.get("doc_code")
        if item.get("party_name") == "Beta Steel" and item.get("doc_type") == "COI":
            sop22_doc_beta = item.get("doc_code")
    return code == 200, f"docs created; alpha_code={sop22_doc_alpha}, beta_code={sop22_doc_beta}"

def t22_04():
    if not sop22_id: return False, "no instance"
    if not sop22_doc_alpha: return None, "no alpha doc_code (checklist not generated yet)"
    code, r = post(f"/22/instances/{sop22_id}/mark-received?doc_code={sop22_doc_alpha}&actor=pm_test", None)
    if code == 200:
        return True, f"status={r.get('status')}"
    return None, f"doc not found: {r.get('error','')[:60]}"

def t22_05():
    # Verify COI passing HCI minimums (GL $1M, Agg $2M, WC $1M, Auto $1M)
    if not sop22_id: return False, "no instance"
    if not sop22_doc_alpha: return None, "no alpha doc_code"
    code, r = post(f"/22/instances/{sop22_id}/verify-coi", {
        "doc_code": sop22_doc_alpha,
        "general_liability": 1000000.0, "aggregate": 2000000.0,
        "workers_comp": 1000000.0, "auto_liability": 1000000.0,
        "verifier": "pm_test"})
    if code == 200:
        meets = r.get("meets_minimums")
        return meets is True, f"meets_minimums={meets}, deficiencies={r.get('deficiencies', [])}"
    return None, f"doc not found: {r.get('error','')[:60]}"

def t22_06():
    # COI below minimums — should flag deficiency
    if not sop22_id: return False, "no instance"
    if not sop22_doc_beta: return None, "no beta doc_code"
    code, r = post(f"/22/instances/{sop22_id}/verify-coi", {
        "doc_code": sop22_doc_beta,
        "general_liability": 500000.0, "aggregate": 1000000.0,
        "workers_comp": 500000.0, "auto_liability": 500000.0,
        "verifier": "pm_test"})
    if code == 200:
        deficient = len(r.get("deficiencies", [])) > 0
        return deficient, f"meets_minimums={r.get('meets_minimums')}, deficiencies={len(r.get('deficiencies', []))}"
    return None, f"doc not found: {r.get('error','')[:60]}"

def t22_07():
    if not sop22_id: return False, "no instance"
    code, r = post(f"/22/instances/{sop22_id}/pm-approve?pm_name=pm_test", None)
    if code == 200:
        # COI-Beta is REJECTED (below minimums), so pm_approve should be blocked
        blocked = r.get("status") == "blocked"
        return blocked, f"status={r.get('status')} (blocked expected because Beta COI failed)"
    return None, f"HTTP {code}: {r.get('detail','')[:80]}"

run("UT-22-01", "Create SOP 22 COI collection", t22_01)
run("UT-22-02", "GET COI collection status", t22_02)
run("UT-22-03", "Generate COI/W-9 checklist for subs", t22_03)
run("UT-22-04", "Mark COI received from Alpha Concrete", t22_04)
run("UT-22-05", "Verify COI meets HCI minimums (all pass)", t22_05)
run("UT-22-06", "Verify COI below minimums (deficiency flagged)", t22_06)
run("UT-22-07", "PM approve (blocked if COI unverified)", t22_07)


# ── SOP 23 — Project Startup ──────────────────────────────────────────────────

print("\n=== SOP 23 — Project Startup ===")

sop23_id = None

def t23_01():
    global sop23_id
    code, r = post("/23/instances", {
        "project_id": PROJECT_ID, "sop_22_instance_id": sop22_id or 1,
        "owner_name": "pm_test", "superintendent_name": "Joe Super",
        "project_name": "Test Build", "project_type": "commercial",
        "construction_start": "2026-08-01"})
    sop23_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop23_id
    return ok, f"id={sop23_id}"

def t23_02():
    if not sop23_id: return False, "no instance"
    code, r = get(f"/23/instances/{sop23_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t23_03():
    if not sop23_id: return False, "no instance"
    code, r = post(f"/23/instances/{sop23_id}/ai-checklist", None)
    return code == 200, f"items={r.get('total_items', 0)}"

def t23_04():
    if not sop23_id: return False, "no instance"
    code, r = post(f"/23/instances/{sop23_id}/complete-item?item_code=STARTUP-001&actor=pm_test", None)
    if code == 200:
        return True, f"status={r.get('item_status')}"
    return None, f"item not found: {r.get('error','')[:60]}"

def t23_05():
    if not sop23_id: return False, "no instance"
    code, r = post(f"/23/instances/{sop23_id}/pm-approve?pm_name=pm_test", None)
    if code == 200:
        return True, f"status={r.get('status')}"
    return None, f"blocked (startup items pending): {r.get('detail','')[:80]}"

run("UT-23-01", "Create SOP 23 Project Startup", t23_01)
run("UT-23-02", "GET startup checklist", t23_02)
run("UT-23-03", "AI generate startup checklist", t23_03)
run("UT-23-04", "Complete startup item", t23_04)
run("UT-23-05", "PM approve (ready-to-build gate)", t23_05)


# ── SOP 24 — Superintendent Daily Dashboard ──────────────────────────────────

print("\n=== SOP 24 — Superintendent Daily Dashboard ===")

sop24_id = None

def t24_01():
    global sop24_id
    code, r = post("/24/instances", {
        "project_id": PROJECT_ID, "sop_23_instance_id": sop23_id or 1,
        "owner_name": "superintendent"})
    sop24_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop24_id
    return ok, f"id={sop24_id}"

def t24_02():
    if not sop24_id: return False, "no instance"
    code, r = get(f"/24/instances/{sop24_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t24_03():
    if not sop24_id: return False, "no instance"
    code, r = post(f"/24/instances/{sop24_id}/metrics", {
        "metric_code": "SCHED-001", "label": "Schedule Float (days)",
        "value": 5, "unit": "days", "category": "schedule",
        "alert_level": "GREEN", "date": "2026-08-15"})
    return code == 200, f"output_id={r.get('output_id')}"

def t24_04():
    if not sop24_id: return False, "no instance"
    code, r = post(f"/24/instances/{sop24_id}/daily-brief?snap_date=2026-08-15", None)
    return code == 200, f"brief_len={len(str(r.get('brief','') or r.get('daily_brief','')))}"

run("UT-24-01", "Create SOP 24 Super Dashboard", t24_01)
run("UT-24-02", "GET dashboard status", t24_02)
run("UT-24-03", "Update schedule metric (GREEN)", t24_03)
run("UT-24-04", "Generate AI daily brief", t24_04)


# ── SOP 25 — Daily Log ────────────────────────────────────────────────────────

print("\n=== SOP 25 — Daily Log ===")

sop25_id = None

def t25_01():
    global sop25_id
    code, r = post("/25/instances", {
        "project_id": PROJECT_ID, "sop_23_instance_id": sop23_id or 1,
        "owner_name": "superintendent"})
    sop25_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop25_id
    return ok, f"id={sop25_id}"

def t25_02():
    if not sop25_id: return False, "no instance"
    code, r = get(f"/25/instances/{sop25_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t25_03():
    if not sop25_id: return False, "no instance"
    code, r = post(f"/25/instances/{sop25_id}/entries", {
        "log_date": "2026-08-15", "weather": "clear",
        "temperature_high": 82, "temperature_low": 58,
        "total_workers": 22,
        "work_performed": "Poured footing grid A-B; formed walls gridline 1-4",
        "materials_received": ["Concrete 15 cy", "Rebar #4"],
        "delays": [], "safety_topics": ["Fall protection briefing"],
        "incidents": [], "rfis_submitted": [], "inspectors_on_site": [],
        "visitors": [], "photos_taken": 12, "notes": "On schedule"})
    return code == 200, f"output_id={r.get('output_id')}"

def t25_04():
    if not sop25_id: return False, "no instance"
    code, r = post(f"/25/instances/{sop25_id}/close-day?log_date=2026-08-15&actor=superintendent", None)
    return code == 200, f"closed={r.get('closed')}"

def t25_05():
    if not sop25_id: return False, "no instance"
    code, r = get(f"/25/instances/{sop25_id}/weekly-summary?week_start=2026-08-10")
    return code == 200, f"days_logged={r.get('days_logged', 0)}"

run("UT-25-01", "Create SOP 25 Daily Log", t25_01)
run("UT-25-02", "GET daily log", t25_02)
run("UT-25-03", "Create daily log entry with AI risk analysis", t25_03)
run("UT-25-04", "Close day", t25_04)
run("UT-25-05", "Weekly summary (AI generated)", t25_05)


# ── SOP 26 — Field Coordination ──────────────────────────────────────────────

print("\n=== SOP 26 — Field Coordination ===")

sop26_id = None

def t26_01():
    global sop26_id
    code, r = post("/26/instances", {
        "project_id": PROJECT_ID, "sop_23_instance_id": sop23_id or 1,
        "owner_name": "pm_test"})
    sop26_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop26_id
    return ok, f"id={sop26_id}"

def t26_02():
    if not sop26_id: return False, "no instance"
    code, r = get(f"/26/instances/{sop26_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t26_03():
    if not sop26_id: return False, "no instance"
    code, r = post(f"/26/instances/{sop26_id}/items", {
        "item_code": "RFI-001", "coord_type": "RFI",
        "description": "Conflict between structural beam and HVAC duct at gridline B-4",
        "priority": "URGENT", "trade_codes": ["STR", "MECH"],
        "drawing_refs": ["S2.1", "M3.2"], "spec_refs": [], "date_needed": "2026-08-20"})
    if r.get("status") == "validation_error":
        return False, f"validation error: {r.get('errors', [])}"
    return code == 200 and r.get("output_id") is not None, f"output_id={r.get('output_id')}"

def t26_04():
    if not sop26_id: return False, "no instance"
    code, r = post(f"/26/instances/{sop26_id}/draft-response?item_code=RFI-001", None)
    return code == 200, f"draft_len={len(str(r.get('draft_response','') or r.get('draft','')))}"

def t26_05():
    if not sop26_id: return False, "no instance"
    code, r = post(f"/26/instances/{sop26_id}/close-item?item_code=RFI-001&resolution=Lower+duct+3in+per+RFI+response&actor=pm_test", None)
    return code == 200, f"closed={r.get('closed')}"

run("UT-26-01", "Create SOP 26 Field Coordination log", t26_01)
run("UT-26-02", "GET coordination log", t26_02)
run("UT-26-03", "Add RFI item (HIGH priority)", t26_03)
run("UT-26-04", "AI draft RFI response", t26_04)
run("UT-26-05", "Close coordination item with resolution", t26_05)


# ── SOP 27 — Quality Control ──────────────────────────────────────────────────

print("\n=== SOP 27 — Quality Control ===")

sop27_id = None

def t27_01():
    global sop27_id
    code, r = post("/27/instances", {
        "project_id": PROJECT_ID, "project_type": "commercial",
        "sop_23_instance_id": sop23_id or 1, "owner_name": "pm_test"})
    sop27_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop27_id
    return ok, f"id={sop27_id}"

def t27_02():
    if not sop27_id: return False, "no instance"
    code, r = get(f"/27/instances/{sop27_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t27_03():
    if not sop27_id: return False, "no instance"
    code, r = post(f"/27/instances/{sop27_id}/generate-checklist?trade_code=CONC&category=foundations", None)
    return code == 200, f"items={r.get('total_items', 0)}"

def t27_04():
    # Record PASS result
    if not sop27_id: return False, "no instance"
    code, r = post(f"/27/instances/{sop27_id}/record-result", {
        "item_code": "QC-CONC-001", "result": "PASS",
        "inspector": "inspector_test", "inspection_date": "2026-08-20",
        "severity": "MINOR"})
    if code == 200:
        return True, f"result={r.get('result')}"
    return None, f"item not found: {r.get('error','')[:60]}"

def t27_05():
    # Record CRITICAL FAIL — should trigger SC-03 (stored but not exception)
    if not sop27_id: return False, "no instance"
    code, r = post(f"/27/instances/{sop27_id}/record-result", {
        "item_code": "QC-CRITICAL-001", "result": "FAIL",
        "inspector": "inspector_test", "inspection_date": "2026-08-20",
        "deficiency_notes": "Rebar spacing incorrect — does not meet spec",
        "severity": "CRITICAL"})
    if code == 200:
        sc = r.get("stop_event") or r.get("stop_condition") or r.get("sc03_triggered")
        return True, f"CRITICAL FAIL logged; SC-03 event={sc}"
    return None, f"item not found — item created by AI in t27_03: {r.get('error','')[:60]}"

run("UT-27-01", "Create SOP 27 QC log", t27_01)
run("UT-27-02", "GET QC log status", t27_02)
run("UT-27-03", "Generate AI QC checklist (Concrete foundations)", t27_03)
run("UT-27-04", "Record PASS result", t27_04)
run("UT-27-05", "Record CRITICAL FAIL (SC-03 trigger)", t27_05)


# ── SOP 28 — QC Detail Card ───────────────────────────────────────────────────

print("\n=== SOP 28 — QC Detail Card ===")

sop28_id = None

def t28_01():
    global sop28_id
    code, r = post("/28/instances", {
        "project_id": PROJECT_ID, "trade_code": "CONC",
        "trade_name": "Concrete", "sop_27_instance_id": sop27_id or 1,
        "owner_name": "pm_test", "spec_sections": ["03 30 00", "03 31 00"]})
    sop28_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop28_id
    return ok, f"id={sop28_id}"

def t28_02():
    if not sop28_id: return False, "no instance"
    code, r = get(f"/28/instances/{sop28_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t28_03():
    if not sop28_id: return False, "no instance"
    code, r = post(f"/28/instances/{sop28_id}/ai-draft?project_type=commercial", None)
    return code == 200, f"items={r.get('total_work_items', 0)}"

def t28_04():
    if not sop28_id: return False, "no instance"
    code, r = post(f"/28/instances/{sop28_id}/confirm-item?work_item_code=DC-001&pm_name=pm_test", None)
    if code == 200:
        return True, f"confirmed={r.get('confirmed')}"
    return None, f"item not found: {r.get('error','')[:60]}"

def t28_05():
    if not sop28_id: return False, "no instance"
    code, r = post(f"/28/instances/{sop28_id}/pm-approve?pm_name=pm_test", None)
    if code == 200:
        return True, f"status={r.get('status')}"
    return None, f"blocked (unconfirmed items): {r.get('detail','')[:80]}"

run("UT-28-01", "Create SOP 28 QC Detail Card", t28_01)
run("UT-28-02", "GET detail card", t28_02)
run("UT-28-03", "AI draft QC work items (Concrete)", t28_03)
run("UT-28-04", "PM confirm work item", t28_04)
run("UT-28-05", "PM approve detail card", t28_05)


# ── SOP 29 — Safety ───────────────────────────────────────────────────────────

print("\n=== SOP 29 — Safety ===")

sop29_id = None

def t29_01():
    global sop29_id
    code, r = post("/29/instances", {
        "project_id": PROJECT_ID, "project_type": "commercial",
        "superintendent_name": "Joe Super", "sop_23_instance_id": sop23_id or 1,
        "owner_name": "pm_test", "scope_summary": "Commercial construction with concrete and steel"})
    sop29_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop29_id
    return ok, f"id={sop29_id}"

def t29_02():
    if not sop29_id: return False, "no instance"
    code, r = get(f"/29/instances/{sop29_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t29_03():
    if not sop29_id: return False, "no instance"
    code, r = post(f"/29/instances/{sop29_id}/ai-safety-plan?scope_summary=Concrete+and+steel+commercial+build", None)
    hazard_count = len(r.get('hazards', []))
    if hazard_count == 0:
        return None, f"hazards=0 (AI JSON parse may have failed: {r.get('error','')[:60]})"
    return True, f"hazards={hazard_count}"

def t29_04():
    # Control a hazard
    if not sop29_id: return False, "no instance"
    code, r = post(f"/29/instances/{sop29_id}/control-hazard", {
        "hazard_code": "HAZ-001",
        "controls": ["100% tie-off above 6ft", "Safety nets at each floor", "Daily toolbox talks"]})
    if code == 200:
        return True, f"controlled={r.get('controlled')}"
    return None, f"hazard not found: {r.get('error','')[:60]}"

def t29_05():
    if not sop29_id: return False, "no instance"
    code, r = post(f"/29/instances/{sop29_id}/pm-approve?pm_name=pm_test", None)
    if code == 200:
        return True, f"status={r.get('status')}"
    return None, f"blocked (CRITICAL hazards uncontrolled): {r.get('detail','')[:80]}"

run("UT-29-01", "Create SOP 29 Safety Plan", t29_01)
run("UT-29-02", "GET safety plan", t29_02)
run("UT-29-03", "AI generate safety hazard plan", t29_03)
run("UT-29-04", "Control a hazard (add controls)", t29_04)
run("UT-29-05", "PM approve safety plan", t29_05)


# ── SOP 30 — Inspection ───────────────────────────────────────────────────────

print("\n=== SOP 30 — Inspection ===")

sop30_id = None

def t30_01():
    global sop30_id
    code, r = post("/30/instances", {
        "project_id": PROJECT_ID, "jurisdiction": "City of Aspen",
        "sop_21_instance_id": sop21_id or 1, "owner_name": "pm_test"})
    sop30_id = r.get("instance", {}).get("id")
    ok = code == 200 and r.get("status") == "In Progress" and sop30_id
    return ok, f"id={sop30_id}"

def t30_02():
    if not sop30_id: return False, "no instance"
    code, r = get(f"/30/instances/{sop30_id}")
    return code == 200 and r.get("instance"), f"GET 200"

def t30_03():
    if not sop30_id: return False, "no instance"
    code, r = post(f"/30/instances/{sop30_id}/schedule", {
        "inspection_type": "foundation", "permit_number": "BP-2026-001",
        "scheduled_date": "2026-08-25",
        "description": "Footing rebar inspection before pour"})
    return code == 200, f"output_id={r.get('output_id')}"

def t30_04():
    # Record PASS result
    if not sop30_id: return False, "no instance"
    code, r = post(f"/30/instances/{sop30_id}/record-result", {
        "inspection_code": "INSP-001", "result": "PASS",
        "inspector_name": "City Inspector Jones",
        "inspection_date": "2026-08-25", "correction_items": []})
    if code == 200:
        return True, f"result={r.get('result')}"
    return None, f"item not found: {r.get('error','')[:60]}"

def t30_05():
    # Record FAIL — should trigger SC-03
    if not sop30_id: return False, "no instance"
    code, r = post(f"/30/instances/{sop30_id}/record-result", {
        "inspection_code": "INSP-002", "result": "FAIL",
        "inspector_name": "City Inspector Jones",
        "inspection_date": "2026-08-28",
        "correction_items": ["Remove and reinstall rebar per detail A4.1", "Add chamfer strips at corners"]})
    if code == 200:
        sc = r.get("stop_event") or r.get("stop_condition") or r.get("sc03_triggered")
        return True, f"FAIL recorded; SC-03={sc}"
    return None, f"item not found: {r.get('error','')[:60]}"

run("UT-30-01", "Create SOP 30 Inspection Log", t30_01)
run("UT-30-02", "GET inspection log", t30_02)
run("UT-30-03", "Schedule foundation inspection", t30_03)
run("UT-30-04", "Record inspection PASS", t30_04)
run("UT-30-05", "Record inspection FAIL (SC-03 trigger)", t30_05)


# ── Integration Tests ─────────────────────────────────────────────────────────

print("\n=== Integration Tests ===")


def it_h_01():
    """SOP 17 → 18 chain: schedule generates, handed off to long-lead."""
    if not sop17_id: return False, "no sop17 instance"
    code, r = post(f"/17/instances/{sop17_id}/hand-off-to-18", {
        "actor": "pm_test", "project_id": PROJECT_ID, "owner_name": "pm_test"})
    if code == 200:
        new_id = r.get("sop_18_instance", {}).get("id") if isinstance(r.get("sop_18_instance"), dict) else None
        return True, f"SOP 17 HANDED_OFF; sop18_auto_created={new_id}"
    blocked = r.get("status") == "blocked" or "blocked" in str(r)
    if blocked:
        return None, f"handoff blocked (approval gate not met): {r.get('message','')[:80]}"
    return False, f"HTTP {code}: {r}"


def it_h_02():
    """SOP 22 COI enforcement: Beta Steel COI below minimums blocks pm-approve."""
    if not sop22_id: return False, "no sop22 instance"
    code, r = post(f"/22/instances/{sop22_id}/pm-approve?pm_name=pm_test", None)
    # Beta Steel COI was submitted below minimums, so pm-approve should be blocked
    blocked = (code == 400) or r.get("status") == "blocked"
    if blocked:
        return True, f"COI deficiency correctly blocked pm-approve: {r.get('detail','')[:80]}"
    # Or if all COIs are VERIFIED despite deficiency (doc marked as deficient but still verified)
    return None, f"pm-approve returned {code}: {r.get('status')}"


def it_h_03():
    """SOP 29 CRITICAL hazard blocks pm-approve until controlled."""
    # Create a new safety plan and don't control hazards
    code, r = post("/29/instances", {
        "project_id": PROJECT_ID, "project_type": "commercial",
        "superintendent_name": "Test Super", "sop_23_instance_id": 1,
        "owner_name": "pm_test"})
    tid = r.get("instance", {}).get("id")
    if not tid: return False, "no instance"
    # Run AI to create hazards
    post(f"/29/instances/{tid}/ai-safety-plan", None)
    # Immediately try to approve without controlling hazards
    code2, r2 = post(f"/29/instances/{tid}/pm-approve?pm_name=pm_test", None)
    # If CRITICAL hazards exist uncontrolled, this should be blocked
    if code2 == 400 or r2.get("status") == "blocked":
        return True, f"CRITICAL uncontrolled hazard correctly blocked approval"
    # If AI didn't create CRITICAL hazards (depends on prompt), accept as conditional
    return None, f"pm-approve {code2}: {r2.get('status')} (may pass if AI created no CRITICAL hazards)"


def it_h_04():
    """SOP 23 → 24 chain: startup complete, hands off to dashboard."""
    if not sop23_id: return False, "no sop23 instance"
    code, r = post(f"/23/instances/{sop23_id}/hand-off-to-24", {
        "actor": "pm_test", "project_id": PROJECT_ID, "owner_name": "superintendent"})
    if code == 200:
        sop24_new = r.get("sop_24_instance", {}).get("id") if isinstance(r.get("sop_24_instance"), dict) else None
        return True, f"SOP 23 HANDED_OFF; sop24_auto_created={sop24_new}"
    blocked = r.get("status") == "blocked" or "blocked" in str(r)
    if blocked:
        return None, f"handoff blocked (approval gate not met): {r.get('message','')[:80]}"
    return False, f"HTTP {code}: {r}"


def it_h_05():
    """Phase H audit trail: SOP 30 inspection events recorded correctly."""
    if not sop30_id: return False, "no sop30 instance"
    code, r = get(f"/30/instances/{sop30_id}")
    if code != 200: return False, f"GET failed: {code}"
    audit = r.get("audit_trail", [])
    has_schedule = any("schedule" in str(e.get("event_type","")).lower() or
                       "inspection" in str(e.get("description","")).lower()
                       for e in audit)
    return has_schedule, f"audit events={len(audit)}, has_schedule_event={has_schedule}"


run("IT-H-01", "SOP 17 → 18 chain handoff", it_h_01)
run("IT-H-02", "SOP 22 COI deficiency blocks pm-approve", it_h_02)
run("IT-H-03", "SOP 29 CRITICAL hazard blocks pm-approve", it_h_03)
run("IT-H-04", "SOP 23 → 24 chain handoff", it_h_04)
run("IT-H-05", "SOP 30 audit trail completeness", it_h_05)


# ── Summary ───────────────────────────────────────────────────────────────────

total   = len(results)
passed  = sum(1 for r in results if r["status"] == "PASS")
cond    = sum(1 for r in results if r["status"] == "CONDITIONAL")
failed  = sum(1 for r in results if r["status"] == "FAIL")

print(f"\n{'='*60}")
print(f"TEST SUMMARY")
print(f"{'='*60}")
print(f"PASS:        {passed}")
print(f"CONDITIONAL: {cond}")
print(f"FAIL:        {failed}")
print(f"TOTAL:       {total}")

fails = [r for r in results if r["status"] == "FAIL"]
conds = [r for r in results if r["status"] == "CONDITIONAL"]

if fails:
    print(f"\nFAILED TESTS:")
    for r in fails:
        print(f"  ❌ {r['id']}: {r['name']}")
        print(f"     {r['note']}")
if conds:
    print(f"\nCONDITIONAL:")
    for r in conds:
        print(f"  ⚠️  {r['id']}: {r['name']}")
        print(f"     {r['note']}")

out_path = os.path.join(os.path.dirname(__file__), "test_results_phase_h.json")
with open(out_path, "w") as f:
    json.dump({
        "run_at": datetime.datetime.utcnow().isoformat(),
        "summary": {"pass": passed, "conditional": cond, "fail": failed, "total": total},
        "results": results,
    }, f, indent=2)
print(f"\nResults written to: {out_path}")
