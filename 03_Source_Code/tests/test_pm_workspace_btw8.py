"""
BTW-8 Tests — PM Workspace: Client Comm Queue + AI Ranked Actions
Verifies additions to /api/v1/pm/{project_id}/weekly response
"""
import requests

BASE = "http://localhost:8000/api/v1"
H = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + str(detail) if detail else ''}")

print("PM Workspace BTW-8 Tests")
print("=" * 50)

for project_id, name in [(1, "64 Eastwood"), (2, "101 Francis"), (3, "1355 Riverside")]:
    print(f"\n{name} (project_id={project_id})")

    r = requests.get(f"{BASE}/pm/{project_id}/weekly", headers=H)
    check(f"PM weekly 200", r.status_code == 200, r.text[:80])
    if r.status_code != 200:
        continue

    d = r.json()
    keys = list(d.keys())

    # Existing keys still present
    for key in ["project_id", "health", "budget", "rfis", "procurement",
                "change_orders", "next_week_priorities"]:
        check(f"Has {key}", key in keys)

    # BTW-8: new client_comms structure
    cc = d.get("client_comms", {})
    check("client_comms present", bool(cc))
    check("client_comms has data_status", "data_status" in cc)
    check("client_comms has days_since_contact key", "days_since_contact" in cc)
    check("client_comms data_status not stub",
          cc.get("data_status") != "pending_hubspot_sync",
          cc.get("data_status"))

    if cc.get("data_status") == "live":
        check("client_comms has urgency", cc.get("urgency") in ("CURRENT", "DUE_SOON", "OVERDUE"))
        check("client_comms has recent_engagements list", isinstance(cc.get("recent_engagements"), list))
        check("client_comms has recent_notes list", isinstance(cc.get("recent_notes"), list))

    # BTW-8: new ai_ranked_actions
    actions = d.get("ai_ranked_actions", [])
    check("ai_ranked_actions present", "ai_ranked_actions" in keys)
    check("ai_ranked_actions is list", isinstance(actions, list))
    if actions:
        a0 = actions[0]
        check("Action has rank", "rank" in a0)
        check("Action has category", "category" in a0)
        check("Action has severity", a0.get("severity") in ("HIGH", "MEDIUM", "LOW"))
        check("Action has action text", bool(a0.get("action")))
        check("Action has priority_score", "priority_score" in a0)
        check("Rank 1 is highest score",
              all(a["priority_score"] <= a0["priority_score"] for a in actions))
        check("Max 10 actions", len(actions) <= 10)

# Final
print(f"\n{'='*50}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
