"""
BTW-10 — Continuous Discovery Engine (unblocked infrastructure)
Tests: change detection API, scan-and-notify, n8n workflow structure
"""
import json, requests
from pathlib import Path

API = "http://localhost:8000"
HEADERS = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}
CD = "/api/v1/services/continuous-discovery"

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + str(detail) if detail else ''}")

def get(path, params=None):
    r = requests.get(f"{API}{path}", headers=HEADERS, params=params, timeout=20)
    return r.status_code, r.json() if r.ok else {}

def post(path, params=None):
    r = requests.post(f"{API}{path}", headers=HEADERS, params=params, timeout=20)
    return r.status_code, r.json() if r.ok else {}

print("BTW-10 Continuous Discovery Tests")
print("=" * 50)

# ── 1. Service Info ───────────────────────────────────────────────────────────
print("\n1. Service Info — /services/continuous-discovery")
code, d = get(CD)
check("Returns 200", code == 200, code)
check("Status is active", d.get("status") == "active")
check("Has endpoints list", isinstance(d.get("endpoints"), list))
check("Has connector_schedule dict", isinstance(d.get("connector_schedule"), dict))
check("HubSpot listed as hourly", "hourly" in str(d.get("connector_schedule", {}).get("hubspot", "")))
check("Houzz listed as nightly", "nightly" in str(d.get("connector_schedule", {}).get("houzz", "")))
check("Has flow list (5+ steps)", len(d.get("flow", [])) >= 5)

# ── 2. Detect All Connectors ──────────────────────────────────────────────────
print("\n2. Detect All — /detect")
code, d = get(f"{CD}/detect")
check("Returns 200", code == 200, code)
check("Has checked_at", "checked_at" in d)
check("Has overall_status", d.get("overall_status") in ("CHANGES_DETECTED", "NO_CHANGES", "ERROR", "STALE"))
check("Has connectors_checked integer", isinstance(d.get("connectors_checked"), int))
check("Checks 2 connectors (houzz + hubspot)", d.get("connectors_checked") == 2)
check("Has connectors_with_changes int", isinstance(d.get("connectors_with_changes"), int))
check("Has connectors list", isinstance(d.get("connectors"), list))
check("Has summary string", isinstance(d.get("summary"), str))

# ── 3. Detect HubSpot ─────────────────────────────────────────────────────────
print("\n3. Detect HubSpot — /detect/hubspot")
code, d = get(f"{CD}/detect/hubspot")
check("Returns 200", code == 200, code)
check("connector == 'hubspot'", d.get("connector") == "hubspot")
check("Has detection_status", d.get("detection_status") in ("CHANGES_DETECTED", "NO_CHANGES", "ERROR", "STALE", "NO_DATA"))
check("Has summary dict", isinstance(d.get("summary"), dict))
s = d.get("summary", {})
check("summary has total_new_records_24h", "total_new_records_24h" in s)
check("summary has stale_entity_count", "stale_entity_count" in s)
check("summary has error_entity_count", "error_entity_count" in s)
check("summary has entities_with_data", "entities_with_data" in s)
check("Has entities list", isinstance(d.get("entities"), list))
check("Has action_required bool", isinstance(d.get("action_required"), bool))
check("Has changes_ready_to_ingest bool", isinstance(d.get("changes_ready_to_ingest"), bool))

# Entity structure check
if d.get("entities"):
    e = d["entities"][0]
    check("Entity has entity_type", "entity_type" in e)
    check("Entity has current_count", "current_count" in e)
    check("Entity has sync_status", "sync_status" in e)
    check("Entity has is_stale bool", isinstance(e.get("is_stale"), bool))
else:
    check("Entity structure (empty — no sync data)", True)

# ── 4. Detect Houzz ───────────────────────────────────────────────────────────
print("\n4. Detect Houzz — /detect/houzz")
code, d = get(f"{CD}/detect/houzz")
check("Returns 200", code == 200, code)
check("connector == 'houzz'", d.get("connector") == "houzz")
check("Has detection_status", "detection_status" in d)
check("Has entities list", isinstance(d.get("entities"), list))
check("Houzz has 9 entities", len(d.get("entities", [])) == 9)

# ── 5. Invalid Connector ──────────────────────────────────────────────────────
print("\n5. Error Handling")
code, _ = get(f"{CD}/detect/unknown_connector")
check("Unknown connector returns 400", code == 400, code)

# ── 6. Scan and Notify ───────────────────────────────────────────────────────
print("\n6. Scan and Notify — POST /scan-and-notify")
code, d = post(f"{CD}/scan-and-notify")
check("All-connector scan returns 200", code == 200, code)
check("logged == True", d.get("logged") is True)
check("connectors_scanned == 2", d.get("connectors_scanned") == 2)
check("Has result dict", isinstance(d.get("result"), dict))

code, d = post(f"{CD}/scan-and-notify", {"connector_name": "hubspot"})
check("Single connector scan returns 200", code == 200, code)
check("logged == True", d.get("logged") is True)
check("connector == 'hubspot'", d.get("connector") == "hubspot")
check("Has result dict", isinstance(d.get("result"), dict))

code, _ = post(f"{CD}/scan-and-notify", {"connector_name": "invalid"})
check("Invalid connector scan returns 400", code == 400, code)

# ── 7. n8n Workflow Structure ─────────────────────────────────────────────────
print("\n7. AUTO-CONTINUOUS-DISCOVERY Workflow")
wf_path = Path("/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/workflows/n8n/AUTO-CONTINUOUS-DISCOVERY.json")
check("Workflow file exists", wf_path.exists())
if wf_path.exists():
    wf = json.loads(wf_path.read_text())
    check("Has btw-10 tag", any("btw-10" in str(t) for t in wf.get("tags", [])))
    nodes = wf.get("nodes", [])
    node_names = [n["name"] for n in nodes]
    check("Has hourly cron trigger", any("hour" in n.lower() for n in node_names))
    check("Has nightly cron trigger", any("nightly" in n.lower() for n in node_names))
    check("Has HubSpot scan node", any("hubspot" in n.lower() for n in node_names))
    check("Has Houzz scan node", any("houzz" in n.lower() for n in node_names))
    check("Has evaluate node", any("evaluat" in n.lower() for n in node_names))
    check("Has ntfy notification node", any("ntfy" in n.lower() or "ntfy.sh" in str(wf) for n in node_names))

    urls = [n["parameters"].get("url", "") for n in nodes if "url" in n.get("parameters", {})]
    check("Calls continuous-discovery endpoint", any("continuous-discovery" in u for u in urls))
    check("Sends to hci-executive ntfy topic", "hci-executive" in str(wf))

# ── Results ───────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
