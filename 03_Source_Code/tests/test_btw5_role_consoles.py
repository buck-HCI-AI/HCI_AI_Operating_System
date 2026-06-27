"""
BTW-5 — Role Intelligence: 5 New Role Consoles
Tests: owner, office, accounting, client, trade-partner endpoints
"""
import sys, os, requests

API = "http://localhost:8000"
HEADERS = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}

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
    r = requests.get(f"{API}{path}", headers=HEADERS, params=params, timeout=15)
    return r.status_code, r.json() if r.ok else {}

print("BTW-5 Role Console Tests")
print("=" * 50)

# ── 1. Owner Dashboard ────────────────────────────────────────────────────────
print("\n1. Owner Dashboard — /owner/dashboard")
code, d = get("/api/v1/owner/dashboard")
check("Returns 200", code == 200, code)
check("Has generated_at", "generated_at" in d)
check("Has company_health (GREEN/YELLOW/RED)", d.get("company_health") in ("GREEN", "YELLOW", "RED"))
check("Has portfolio.active_projects", isinstance(d.get("portfolio", {}).get("active_projects"), int))
check("Has portfolio.projects list", isinstance(d.get("portfolio", {}).get("projects"), list))
check("Has executive_inbox section", "executive_inbox" in d)
check("executive_inbox has pending_count", isinstance(d.get("executive_inbox", {}).get("pending_count"), int))
check("Has missions section", "missions" in d)
check("missions has blocked_count", isinstance(d.get("missions", {}).get("blocked_count"), int))
check("Has bids section", "bids" in d)
check("Has rfis section", "rfis" in d)
check("Has change_orders section", "change_orders" in d)
check("Has ai_roi section", "ai_roi" in d)
check("Has owner_actions list", isinstance(d.get("owner_actions"), list))

# ── 2. Office Queue ───────────────────────────────────────────────────────────
print("\n2. Office Queue — /office/queue")
code, d = get("/api/v1/office/queue")
check("Returns 200", code == 200, code)
check("Has queue_urgency (LOW/MEDIUM/HIGH)", d.get("queue_urgency") in ("LOW", "MEDIUM", "HIGH"))
check("Has queue_depth integer", isinstance(d.get("queue_depth"), int))
check("Has pending_approvals section", "pending_approvals" in d)
check("pending_approvals has count", isinstance(d.get("pending_approvals", {}).get("count"), int))
check("Has rfis section", "rfis" in d)
check("rfis has open_count", isinstance(d.get("rfis", {}).get("open_count"), int))
check("rfis has overdue_count", isinstance(d.get("rfis", {}).get("overdue_count"), int))
check("Has bid_packages section", "bid_packages" in d)
check("Has submittals section", "submittals" in d)
check("Has priority_actions list", isinstance(d.get("priority_actions"), list))

# ── 3. Accounting Financials — 3 projects ────────────────────────────────────
print("\n3. Accounting Financials — /accounting/{project_id}/financials")
for pid in [1, 2, 3]:
    code, d = get(f"/api/v1/accounting/{pid}/financials")
    check(f"Project {pid} returns 200", code == 200, code)
    check(f"Project {pid} has financial_health", d.get("financial_health") in ("GREEN", "YELLOW", "RED"))
    check(f"Project {pid} has budget_summary", "budget_summary" in d)
    bs = d.get("budget_summary", {})
    check(f"Project {pid} budget_summary has total_budget", "total_budget" in bs)
    check(f"Project {pid} budget_summary has total_variance", "total_variance" in bs)
    check(f"Project {pid} budget_summary has status", "status" in bs)
    check(f"Project {pid} has change_orders section", "change_orders" in d)
    check(f"Project {pid} change_orders has pending_count", isinstance(d.get("change_orders", {}).get("pending_count"), int))
    check(f"Project {pid} has purchase_orders section", "purchase_orders" in d)
    check(f"Project {pid} has accounting_actions list", isinstance(d.get("accounting_actions"), list))

# ── 4. Client Project Status — 3 projects ────────────────────────────────────
print("\n4. Client Status — /client/{project_id}/status")
for pid in [1, 2, 3]:
    code, d = get(f"/api/v1/client/{pid}/status")
    check(f"Project {pid} returns 200", code == 200, code)
    check(f"Project {pid} has project_health", d.get("project_health") in ("GREEN", "YELLOW", "RED"))
    check(f"Project {pid} has schedule section", "schedule" in d)
    sched = d.get("schedule", {})
    check(f"Project {pid} schedule has upcoming_milestones", isinstance(sched.get("upcoming_milestones"), list))
    check(f"Project {pid} schedule has completed_milestones", isinstance(sched.get("completed_milestones"), int))
    check(f"Project {pid} has change_orders section", "change_orders" in d)
    co = d.get("change_orders", {})
    check(f"Project {pid} CO has pending_client_action", isinstance(co.get("pending_client_action"), int))
    check(f"Project {pid} has open_rfis section", "open_rfis" in d)
    check(f"Project {pid} has client_summary string", isinstance(d.get("client_summary"), str))

# ── 5. Trade Partner Work Queue ───────────────────────────────────────────────
print("\n5. Trade Work Queue — /trade/{project_id}/my-work")
for pid, trade in [(1, ""), (2, "framing"), (3, "plumbing")]:
    params = {"trade": trade} if trade else {}
    code, d = get(f"/api/v1/trade/{pid}/my-work", params=params)
    label = f"Project {pid}" + (f" trade={trade}" if trade else "")
    check(f"{label} returns 200", code == 200, code)
    check(f"{label} has work_health", d.get("work_health") in ("GREEN", "YELLOW", "RED"))
    check(f"{label} has tasks section", "tasks" in d)
    check(f"{label} tasks has open_count", isinstance(d.get("tasks", {}).get("open_count"), int))
    check(f"{label} tasks has overdue_count", isinstance(d.get("tasks", {}).get("overdue_count"), int))
    check(f"{label} has upcoming_schedule section", "upcoming_schedule" in d)
    check(f"{label} has purchase_orders section", "purchase_orders" in d)
    check(f"{label} has rfis section", "rfis" in d)
    check(f"{label} has trade_actions list", isinstance(d.get("trade_actions"), list))
    check(f"{label} trade_filter matches", d.get("trade_filter") == (trade or "all"))

# ── 6. Error Handling — Invalid Project ──────────────────────────────────────
print("\n6. Error Handling")
code404, _ = get("/api/v1/accounting/9999/financials")
check("Accounting 9999 returns 404", code404 == 404, code404)
code404, _ = get("/api/v1/client/9999/status")
check("Client 9999 returns 404", code404 == 404, code404)
code404, _ = get("/api/v1/trade/9999/my-work")
check("Trade 9999 returns 404", code404 == 404, code404)

# ── Results ───────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
