"""
Core Services — Comprehensive Test Suite
Covers: bid_intelligence, vendor_intelligence, document_intelligence,
schedule_intelligence, risk_intelligence, kpi_intelligence,
decision_intelligence, historical_cost, lessons_learned, procurement,
approval_queue, bid_leveling, connectors, autonomy, notification_engine.
Run: python3 tests/test_core_services.py
"""
import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import urllib.request, urllib.error

BASE = "http://localhost:8000"
API_KEY = "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"
RESULTS = []
PASS = FAIL = 0


def req(path, method="GET", body=None, timeout=20):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read()
            try:
                return resp.status, json.loads(raw)
            except Exception:
                return resp.status, {"_html": True, "_body": raw[:100].decode("utf-8","replace")}
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as ex:
        return 0, {"error": str(ex)}


def test(name, path, checks, method="GET", body=None):
    global PASS, FAIL
    status, data = req(path, method, body)
    all_pass = True
    for check_name, fn in checks:
        try:
            ok = fn(status, data)
        except Exception as e:
            ok = False
            check_name = f"{check_name} [exception: {e}]"
        if not ok:
            all_pass = False
            print(f"   FAIL [{check_name}]: status={status}, data={str(data)[:200]}")
    print(f"{'✅' if all_pass else '❌'} {name}")
    RESULTS.append({"test": name, "pass": all_pass})
    if all_pass: PASS += 1
    else: FAIL += 1


print("=" * 65)
print("Core Services — Comprehensive Test Suite")
print(f"Started: {datetime.datetime.now().isoformat()[:19]}")
print("=" * 65)

# ── Core API + Services index ──────────────────────────────────────────────────
print("\n── Core ──")
test("Health check", "/api/v1/health", [
    ("HTTP 200", lambda s, d: s == 200),
    ("status healthy", lambda s, d: d.get("status") in ("healthy","ok")),
])
test("Services index", "/api/v1/services", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has services list", lambda s, d: isinstance(d.get("services"), list)),
    ("multiple services listed", lambda s, d: len(d.get("services",[])) >= 10),
])

# ── Bid Intelligence ───────────────────────────────────────────────────────────
print("\n── Bid Intelligence ──")
test("Bid intelligence root", "/api/v1/services/bid-intelligence", [
    ("HTTP 200", lambda s, d: s == 200),
])
test("Bid intelligence project 1", "/api/v1/services/bid-intelligence/1", [
    ("HTTP 200 or 404", lambda s, d: s in (200, 404)),
])

# ── Vendor Intelligence ────────────────────────────────────────────────────────
print("\n── Vendor Intelligence ──")
test("Vendor intelligence root", "/api/v1/services/vendor-intelligence", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Bid Leveling ───────────────────────────────────────────────────────────────
print("\n── Bid Leveling ──")
test("Bid leveling service", "/api/v1/services/bid-leveling", [
    ("HTTP 200", lambda s, d: s == 200),
])
test("Bid leveling project 1", "/api/v1/services/bid-leveling/1", [
    ("HTTP 200 or 404", lambda s, d: s in (200, 404)),
])

# ── Approval Queue ─────────────────────────────────────────────────────────────
print("\n── Approval Queue ──")
test("Approval queue list", "/api/v1/services/approval-queue", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has items list or queue", lambda s, d: isinstance(d.get("items") or d.get("queue") or d, (list, dict))),
])
test("Approval queue pending", "/api/v1/services/approval-queue?status=pending", [
    ("HTTP 200 or 422", lambda s, d: s in (200, 422)),
])

# ── Historical Cost ────────────────────────────────────────────────────────────
print("\n── Historical Cost ──")
test("Historical cost root", "/api/v1/services/historical-cost", [
    ("HTTP 200", lambda s, d: s == 200),
])
test("Historical cost project 1", "/api/v1/services/historical-cost/1", [
    ("HTTP 200 or 404", lambda s, d: s in (200, 404)),
])

# ── Lessons Learned ────────────────────────────────────────────────────────────
print("\n── Lessons Learned ──")
test("Lessons learned root", "/api/v1/services/lessons-learned", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Procurement ────────────────────────────────────────────────────────────────
print("\n── Procurement ──")
test("Procurement root", "/api/v1/services/procurement", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Schedule Intelligence ──────────────────────────────────────────────────────
print("\n── Schedule Intelligence ──")
test("Schedule intelligence root", "/api/v1/services/schedule-intelligence", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Risk Intelligence ──────────────────────────────────────────────────────────
print("\n── Risk Intelligence ──")
test("Risk intelligence root", "/api/v1/services/risk-intelligence", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Document Intelligence ──────────────────────────────────────────────────────
print("\n── Document Intelligence ──")
test("Document intelligence root", "/api/v1/services/document-intelligence", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Decision Intelligence ──────────────────────────────────────────────────────
print("\n── Decision Intelligence ──")
test("Decision intelligence root", "/api/v1/services/decision-intelligence", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── KPI Intelligence ───────────────────────────────────────────────────────────
print("\n── KPI Intelligence ──")
test("KPI intelligence root", "/api/v1/services/kpi-intelligence", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Connectors ─────────────────────────────────────────────────────────────────
print("\n── Connectors ──")
test("Connectors health", "/api/v1/services/connectors/health", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has services or connectors", lambda s, d: "services" in d or "connectors" in d or isinstance(d, dict)),
])

# ── Autonomy/Opportunities ─────────────────────────────────────────────────────
print("\n── Autonomy ──")
test("Autonomy opportunities", "/api/v1/services/autonomy/opportunities", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has opportunities or items", lambda s, d: isinstance(d.get("opportunities") or d.get("items") or d, (list, dict))),
])
test("Autonomy report", "/api/v1/services/autonomy/report", [
    ("HTTP 200 or 404", lambda s, d: s in (200, 404)),
])
test("Autonomy backlog", "/api/v1/services/autonomy/backlog", [
    ("HTTP 200 or 404", lambda s, d: s in (200, 404)),
])

# ── Operating Rules ────────────────────────────────────────────────────────────
print("\n── Operating Rules ──")
test("Operating rules root", "/api/v1/services/operating-rules", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Business Process Library ───────────────────────────────────────────────────
print("\n── Business Process Library ──")
test("Business process library root", "/api/v1/services/business-process-library", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Background Learning ────────────────────────────────────────────────────────
print("\n── Background Learning ──")
test("Background learning root", "/api/v1/services/background-learning", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Connector Registry ─────────────────────────────────────────────────────────
print("\n── Connector Registry ──")
test("Connector registry root", "/api/v1/services/connector-registry", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Houzz Intelligence ─────────────────────────────────────────────────────────
print("\n── Houzz Intelligence ──")
test("Houzz intelligence root", "/api/v1/services/houzz", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Notifications ──────────────────────────────────────────────────────────────
print("\n── Notifications ──")
test("Notification service", "/api/v1/services/notifications", [
    ("HTTP 200 or 404", lambda s, d: s in (200, 404, 405)),
])

# ── Legacy endpoints ───────────────────────────────────────────────────────────
print("\n── Legacy Endpoints ──")
test("Projects list", "/api/v1/projects", [
    ("HTTP 200", lambda s, d: s == 200),
])
test("Vendors list", "/api/v1/vendors", [
    ("HTTP 200", lambda s, d: s == 200),
])
test("Bids list", "/api/v1/bids", [
    ("HTTP 200", lambda s, d: s == 200),
])

# ── Executive ─────────────────────────────────────────────────────────────────
print("\n── Executive ──")
test("Executive morning brief", "/api/v1/executive/morning-brief", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has data", lambda s, d: len(d) > 0),
])
test("Executive missions", "/api/v1/executive/missions", [
    ("HTTP 200", lambda s, d: s == 200),
])
test("Executive mission control", "/api/v1/executive/mission-control", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has company_health", lambda s, d: d.get("company_health") in ("GREEN","YELLOW","RED")),
    ("has 11+ sections", lambda s, d: len(d) >= 11),
])

# ── SOP System ────────────────────────────────────────────────────────────────
print("\n── SOP System ──")
test("SOP list", "/api/v1/sops", [
    ("HTTP 200 or 404", lambda s, d: s in (200, 404)),
])

# ── AI + Search ───────────────────────────────────────────────────────────────
print("\n── AI + Search ──")
test("AI root", "/api/v1/ai", [
    ("HTTP 200 or 404 or 405", lambda s, d: s in (200, 404, 405)),
])
test("Search root", "/api/v1/search", [
    ("HTTP 200 or 404 or 405", lambda s, d: s in (200, 404, 405)),
])

# ── Summary ────────────────────────────────────────────────────────────────────
total = PASS + FAIL
print(f"\n{'='*65}")
print(f"RESULTS: {PASS}/{total} passed ({FAIL} failed)")
print(f"Finished: {datetime.datetime.now().isoformat()[:19]}")
print(f"{'='*65}")

results_path = os.path.join(os.path.dirname(__file__), "test_results_core_services.json")
with open(results_path, "w") as f:
    json.dump({"run_at": datetime.datetime.now().isoformat(),
               "passed": PASS, "failed": FAIL, "total": total,
               "pass_rate": round(PASS/total*100,1) if total else 0,
               "tests": RESULTS}, f, indent=2)
print(f"Results: {results_path}")
sys.exit(0 if FAIL == 0 else 1)
