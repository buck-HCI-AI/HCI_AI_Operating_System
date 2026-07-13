"""
Drift-Check — Agent Outage Detection & Recovery — Test Suite
Per GBT's P0 "Restore 100/100 Team Initiative and Self-Healing Enforcement"
handoff (2026-07-13): "add regression tests proving agent outage detection
and recovery" for detectors #25 (stale heartbeats) and #26 (failed handoffs)
in GET /gateway/admin/drift-check. Both detectors existed and were manually
spot-tested live 2026-07-13, but never had automated coverage - this closes
that gap.

Run from: 03_Source_Code/
    python3 tests/test_drift_check_agent_outage.py
"""
import sys, os, json, time, urllib.request, urllib.error, datetime
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.bid_leveling.drive_bid_reader import _pg

BASE = "http://localhost:8000"
API_KEY = os.environ["HCI_API_KEY"]
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
FAILED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                           "architecture", "Agent_Handoff", "Failed")


def req(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            status, text = resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        status, text = e.code, e.read().decode()
    try:
        js = json.loads(text)
    except Exception:
        js = {"_raw": text}
    return status, js


def drift_findings(category):
    s, d = req("GET", "/gateway/admin/drift-check")
    findings = d.get("payload", {}).get("findings", [])
    return [f for f in findings if f.get("category") == category]


results = []


def test(name, fn):
    start = time.time()
    try:
        passed, detail = fn()
        status = "PASS" if passed else "FAIL"
    except Exception as e:
        status, detail, passed = "ERROR", f"{type(e).__name__}: {e}", False
    ms = round((time.time() - start) * 1000)
    results.append({"name": name, "status": status, "detail": detail, "ms": ms})
    print(f"  [{status}] {name} ({ms}ms) - {detail}")
    return passed


def _backdate_code_heartbeat(minutes_ago: int):
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE agent_heartbeats
                SET last_heartbeat_mt = NOW() - (%s || ' minutes')::interval
                WHERE agent_id = 'CODE'
            """, (minutes_ago,))
        conn.commit()


def test_code_stale_heartbeat_is_detected():
    """OUTAGE DETECTION: backdating CODE's heartbeat 45 minutes must trip the
    code_heartbeat_stale HIGH-severity finding - proving detector #25 actually
    fires, not just that its code exists."""
    _backdate_code_heartbeat(45)
    findings = drift_findings("code_heartbeat_stale")
    ok = len(findings) == 1 and findings[0]["severity"] == "high"
    return ok, f"findings={findings}" if not ok else "code_heartbeat_stale fired at HIGH severity as expected"


def test_code_heartbeat_recovery_clears_finding():
    """OUTAGE RECOVERY: a real POST /agent/heartbeat call after the backdated
    state must clear the finding on the next drift-check - proving recovery
    is actually observable, not just that the stale state alone was real."""
    s, d = req("POST", "/gateway/agent/heartbeat",
               {"agent": "claude_code", "mission": "test_drift_check_agent_outage.py regression run"})
    if s != 200:
        return False, f"heartbeat POST failed: {s} {d}"
    findings = drift_findings("code_heartbeat_stale")
    return len(findings) == 0, f"remaining findings={findings}" if findings else "cleared after real heartbeat"


def test_gbt_bc_staleness_never_flagged_high():
    """OUTAGE vs. NORMAL distinction: GBT/BC are chat-based and routinely go
    quiet for hours-to-days between human-initiated sessions - that is normal,
    not an outage. Whatever their current staleness, they must never produce a
    HIGH-severity finding for heartbeat quietness alone (only CODE can)."""
    s, d = req("GET", "/gateway/admin/drift-check")
    findings = d.get("payload", {}).get("findings", [])
    bad = [f for f in findings if f["category"] == "code_heartbeat_stale"
           and any(a in str(f.get("items", [])) for a in ("GBT:", "BC:"))]
    return len(bad) == 0, "; ".join(str(b) for b in bad) if bad else "no GBT/BC row ever produced a HIGH stale finding"


def test_failed_handoff_over_1hr_is_detected():
    """OUTAGE DETECTION: a handoff file sitting in Agent_Handoff/Failed/ with
    an mtime > 1 hour old must trip unaddressed_failed_handoffs - proving
    detector #26 actually fires against a real file, not just that 6
    pre-existing files happened to already be old."""
    os.makedirs(FAILED_DIR, exist_ok=True)
    test_path = os.path.join(FAILED_DIR, "TEST_DELETE_ME_drift_check_regression.md")
    with open(test_path, "w") as f:
        f.write("TEST-DELETE-ME - drift-check regression test artifact, safe to delete.\n")
    two_hours_ago = time.time() - 7200
    os.utime(test_path, (two_hours_ago, two_hours_ago))
    try:
        findings = drift_findings("unaddressed_failed_handoffs")
        hit = any("TEST_DELETE_ME_drift_check_regression.md" in item for f in findings for item in f.get("items", []))
        return hit, f"findings={findings}" if not hit else "test file correctly flagged as stale-failed-handoff"
    finally:
        os.remove(test_path)


def test_recent_failed_handoff_not_flagged():
    """A handoff that just failed (< 1 hour old) should NOT be flagged yet -
    proving the 1-hour grace window is real, not a detector that fires on
    every file in the directory regardless of age."""
    os.makedirs(FAILED_DIR, exist_ok=True)
    test_path = os.path.join(FAILED_DIR, "TEST_DELETE_ME_drift_check_fresh.md")
    with open(test_path, "w") as f:
        f.write("TEST-DELETE-ME - fresh failed-handoff test artifact, safe to delete.\n")
    try:
        findings = drift_findings("unaddressed_failed_handoffs")
        hit = any("TEST_DELETE_ME_drift_check_fresh.md" in item for f in findings for item in f.get("items", []))
        return not hit, "fresh (<1hr) failed handoff correctly NOT flagged" if not hit else f"falsely flagged: {findings}"
    finally:
        os.remove(test_path)


print("\nGroup: DRIFT-OUTAGE — Agent outage detection & recovery (regression, 2026-07-13)")
test("DRIFT-OUTAGE-01: stale CODE heartbeat detected at HIGH severity",     test_code_stale_heartbeat_is_detected)
test("DRIFT-OUTAGE-02: real heartbeat POST clears the stale finding",       test_code_heartbeat_recovery_clears_finding)
test("DRIFT-OUTAGE-03: GBT/BC staleness never flagged as HIGH (normal, not outage)", test_gbt_bc_staleness_never_flagged_high)
test("DRIFT-OUTAGE-04: failed handoff >1hr old is detected",                test_failed_handoff_over_1hr_is_detected)
test("DRIFT-OUTAGE-05: fresh (<1hr) failed handoff not falsely flagged",    test_recent_failed_handoff_not_flagged)

failed = [r for r in results if r["status"] != "PASS"]
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
if failed:
    print("FAILURES:")
    for r in failed:
        print(f"  - {r['name']}: {r['detail']}")
    sys.exit(1)
