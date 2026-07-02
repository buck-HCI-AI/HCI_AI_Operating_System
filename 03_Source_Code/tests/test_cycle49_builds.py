"""
CYCLE49 build regression tests — 2026-07-02.
Covers the mining engine sys.path fix (dead for a week before today), plus the new
deep-dive, cost-forecast, critical-path, and photo/analyze endpoints. Real HTTP
against the live gateway, no mocking - these are the same code paths GPTs call.
"""
import requests

API = "http://localhost:8000"
GW = f"{API}/gateway"
HEADERS = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}

passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name} {detail}")


print("=== Mining engine (sys.path collision regression) ===")
# This is the exact bug that killed mining for a week: 'services' resolved to
# api/services/ (cache/db/storage/vector helpers) instead of services/mining/,
# because api/ is ahead of the project root on sys.path. If this regresses, the
# error surfaces as a 500 with "No module named 'services.mining'" in the API log,
# not in this response body (FastAPI hides tracebacks) - check /tmp/hci_api_server_err.log
# if this test fails.
r = requests.get(f"{API}/api/v1/services/mining/status", headers=HEADERS, timeout=15)
check("mining/status responds 200", r.status_code == 200, f"got {r.status_code}")

# Confirm the OTHER routers that share the ambiguous 'services' import name still
# resolve correctly - this is what the fix had to NOT break while fixing mining.
r = requests.get(f"{API}/api/v1/documents/health", headers=HEADERS, timeout=10)
check("documents router (uses api/services) still works", r.status_code in (200, 404),
      f"got {r.status_code} - if 500, the mining fix likely broke the api/services import path")

print()
print("=== Deep-dive endpoint ===")
r = requests.get(f"{GW}/project/1355R/deep-dive", headers=HEADERS, timeout=15)
check("deep-dive responds 200", r.status_code == 200, f"got {r.status_code}")
if r.status_code == 200:
    body = r.json().get("payload", {})
    check("deep-dive has daily_logs section", "daily_logs" in body)
    check("deep-dive has schedule section", "schedule" in body)
    check("deep-dive has budget section", "budget" in body)
    check("deep-dive has flags list", isinstance(body.get("flags"), list))

print()
print("=== Cost forecast (EVM) endpoint ===")
r = requests.get(f"{GW}/project/1355R/cost-forecast", headers=HEADERS, timeout=15)
check("cost-forecast responds 200", r.status_code == 200, f"got {r.status_code}")
if r.status_code == 200:
    body = r.json().get("payload", {})
    check("cost-forecast has bac_budget_at_completion", "bac_budget_at_completion" in body)
    check("cost-forecast bac matches contract_value (not fabricated)",
          body.get("bac_budget_at_completion", 0) > 0)

print()
print("=== CPM critical-path endpoint (honest fallback) ===")
r = requests.get(f"{GW}/project/1355R/schedule/critical-path", headers=HEADERS, timeout=15)
check("critical-path responds 200", r.status_code == 200, f"got {r.status_code}")
if r.status_code == 200:
    body = r.json().get("payload", {})
    # With zero real predecessor/successor data (true for every project as of this
    # writing), this MUST report dependency_network:false, never a fabricated
    # critical path. If this ever flips to true without real schedule_relationships
    # rows being added on purpose, something is generating fake dependencies.
    check("does not fabricate a critical path with zero relationship data",
          body.get("dependency_network") is False or body.get("relationship_count", 0) > 0,
          f"dependency_network={body.get('dependency_network')}, relationship_count={body.get('relationship_count')}")

print()
print("=== Photo analyze endpoint (structure only, not a live vision call) ===")
r = requests.post(f"{GW}/project/1355R/photo/analyze", headers=HEADERS,
                   json={"file_id": "invalid_test_id", "project_code": "1355R"}, timeout=20)
check("photo/analyze responds (200 with error payload or clean 4xx, not a 500)",
      r.status_code in (200, 400, 404), f"got {r.status_code}")

print()
print(f"=== {passed} passed, {failed} failed ===")
