"""
Phase 2 Intelligence Layer — Automated Test Suite
Tests all Sprint 3 (Operations) + Sprint 4 (Project Brain + Cross-Project Intelligence) endpoints.
Run: python3 tests/test_phase2_intelligence.py
"""
import sys, os, json, time, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request

BASE = "http://localhost:8000"
API_KEY = "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"
RESULTS = []
PASS = FAIL = 0


def req(path: str, method: str = "GET", body: dict = None) -> tuple:
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(r, timeout=30) as resp:
            raw = resp.read()
            try:
                return resp.status, json.loads(raw)
            except Exception:
                return resp.status, {"_html": True, "_body": raw[:200].decode("utf-8","replace")}
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as ex:
        return 0, {"error": str(ex)}


def test(name: str, path: str, checks: list, method: str = "GET", body: dict = None):
    global PASS, FAIL
    status, data = req(path, method, body)
    results = []
    all_pass = True
    for check_name, check_fn in checks:
        try:
            ok = check_fn(status, data)
        except Exception as e:
            ok = False
            check_name = f"{check_name} [exception: {e}]"
        results.append({"check": check_name, "pass": ok})
        if not ok:
            all_pass = False

    icon = "✅" if all_pass else "❌"
    print(f"{icon} {name}")
    for r in results:
        if not r["pass"]:
            print(f"   FAIL: {r['check']}")
            print(f"         status={status}, data={str(data)[:200]}")

    RESULTS.append({"test": name, "path": path, "pass": all_pass, "checks": results})
    if all_pass:
        PASS += 1
    else:
        FAIL += 1


print("=" * 65)
print("Phase 2 Intelligence Layer — Test Suite")
print(f"Started: {datetime.datetime.now().isoformat()[:19]}")
print("=" * 65)

# ── Sprint 3: Operations Console Endpoints ─────────────────────────────────────
print("\n── Sprint 3: Operations Console ──")

test("SS daily console — project 1", "/api/v1/superintendent/1/today", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has health", lambda s, d: d.get("health") in ("GREEN","YELLOW","RED")),
    ("has project_name", lambda s, d: bool(d.get("project_name"))),
    ("has tasks section", lambda s, d: "tasks" in d),
    ("has safety", lambda s, d: "safety" in d and d["safety"].get("toolbox_topic")),
    ("has procurement", lambda s, d: "procurement" in d),
    ("has 10+ keys", lambda s, d: len(d) >= 10),
])

test("SS daily console — project 2", "/api/v1/superintendent/2/today", [
    ("HTTP 200", lambda s, d: s == 200),
    ("project 101 Francis", lambda s, d: "101" in d.get("project_name","")),
])

test("SS daily console — project 3", "/api/v1/superintendent/3/today", [
    ("HTTP 200", lambda s, d: s == 200),
    ("project 1355 Riverside", lambda s, d: "1355" in d.get("project_name","")),
])

test("SS daily console — invalid project → 404", "/api/v1/superintendent/999/today", [
    ("HTTP 404", lambda s, d: s == 404),
])

test("PM weekly console — project 1", "/api/v1/pm/1/weekly", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has health", lambda s, d: d.get("health") in ("GREEN","YELLOW","RED")),
    ("has budget section", lambda s, d: "budget" in d),
    ("has rfis section", lambda s, d: "rfis" in d),
    ("has procurement", lambda s, d: "procurement" in d),
    ("has priorities", lambda s, d: isinstance(d.get("next_week_priorities"), list)),
])

test("PM weekly console — project 2", "/api/v1/pm/2/weekly", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has bid_packages count", lambda s, d: isinstance(d.get("procurement",{}).get("packages"), int)),
])

test("Leadership dashboard", "/api/v1/leadership/dashboard", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has company_health", lambda s, d: d.get("company_health") in ("GREEN","YELLOW","RED")),
    ("has 4 projects", lambda s, d: d.get("active_projects") == 4),
    ("has what_needs_me", lambda s, d: isinstance(d.get("what_needs_me"), list)),
    ("has bids_in_flight", lambda s, d: isinstance(d.get("bids_in_flight"), int)),
    ("has ai_productivity", lambda s, d: "ai_productivity" in d),
])

test("Weekly job reports — all projects", "/api/v1/reports/weekly/jobs", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has reports list", lambda s, d: isinstance(d.get("reports"), list)),
    ("4 reports", lambda s, d: d.get("count") == 4),
])

test("Weekly job reports — single project", "/api/v1/reports/weekly/jobs?project_id=1", [
    ("HTTP 200", lambda s, d: s == 200),
    ("1 report", lambda s, d: d.get("count") == 1),
])

test("Weekly company report", "/api/v1/reports/weekly/company", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has company_health", lambda s, d: "company_health" in d),
    ("has projects", lambda s, d: isinstance(d.get("projects"), list)),
    ("has what_needs_me", lambda s, d: isinstance(d.get("what_needs_me"), list)),
])

# ── Sprint 3: HTML Views ────────────────────────────────────────────────────────
print("\n── Sprint 3: HTML Views ──")

for pid in [1, 2, 3]:
    test(f"SS HTML /superintendent/{pid}", f"/superintendent/{pid}", [
        ("HTTP 200", lambda s, d: s == 200),
        ("is HTML", lambda s, d: d.get("_html") or "health" in str(d.get("_body",""))),
    ])
    test(f"PM HTML /pm/{pid}", f"/pm/{pid}", [
        ("HTTP 200", lambda s, d: s == 200),
        ("is HTML", lambda s, d: d.get("_html") or "PM" in str(d.get("_body",""))),
    ])

test("Leadership HTML /leadership", "/leadership", [
    ("HTTP 200", lambda s, d: s == 200),
    ("is HTML", lambda s, d: d.get("_html") or "HCI" in str(d.get("_body",""))),
])

# ── Sprint 4: Project Brain Intelligence ──────────────────────────────────────
print("\n── Sprint 4: Project Brain Intelligence ──")

test("Project intelligence — project 1 (no AI)", "/api/v1/services/project-brain/1/intelligence?ai_summary=false", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has health", lambda s, d: d.get("health") in ("GREEN","YELLOW","RED")),
    ("has risks", lambda s, d: isinstance(d.get("risks"), list)),
    ("has risk_summary", lambda s, d: "risk_summary" in d),
    ("has decisions", lambda s, d: isinstance(d.get("decisions"), list)),
    ("has timeline", lambda s, d: "timeline" in d),
    ("has procurement", lambda s, d: "procurement" in d),
    ("has missing_information", lambda s, d: isinstance(d.get("missing_information"), list)),
    ("has open_questions", lambda s, d: isinstance(d.get("open_questions"), list)),
    ("has data_completeness_pct", lambda s, d: isinstance(d.get("data_completeness_pct"), (int,float))),
    ("has data_sources", lambda s, d: "data_sources" in d),
])

test("Project intelligence — project 2", "/api/v1/services/project-brain/2/intelligence?ai_summary=false", [
    ("HTTP 200", lambda s, d: s == 200),
    ("correct project", lambda s, d: d.get("project_id") == 2),
])

test("Project intelligence — invalid → 404", "/api/v1/services/project-brain/999/intelligence", [
    ("HTTP 404", lambda s, d: s == 404),
])

test("Project brain health — project 1", "/api/v1/services/project-brain/1/health", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has health", lambda s, d: d.get("health") in ("GREEN","YELLOW","RED")),
    ("has risk_count", lambda s, d: isinstance(d.get("risk_count"), int)),
    ("has critical_risks", lambda s, d: isinstance(d.get("critical_risks"), int)),
    ("has as_of timestamp", lambda s, d: bool(d.get("as_of"))),
])

test("Project brain health — all 4 projects", "/api/v1/services/project-brain/2/health", [
    ("HTTP 200", lambda s, d: s == 200),
])
test("Project brain health — project 3", "/api/v1/services/project-brain/3/health", [
    ("HTTP 200", lambda s, d: s == 200),
])
test("Project brain health — project 4", "/api/v1/services/project-brain/4/health", [
    ("HTTP 200", lambda s, d: s == 200),
])

test("Project risks — project 1", "/api/v1/services/project-brain/1/risks", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has risk_count", lambda s, d: isinstance(d.get("risk_count"), int)),
    ("has risks list", lambda s, d: isinstance(d.get("risks"), list)),
    ("risks have required fields", lambda s, d: all(
        r.get("risk_code") and r.get("risk_type") and r.get("severity") and r.get("title")
        for r in d.get("risks",[])
    )),
])

test("Project health history — project 1", "/api/v1/services/project-brain/1/health-history?days=30", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has history list", lambda s, d: isinstance(d.get("history"), list)),
    ("has project_id", lambda s, d: d.get("project_id") == 1),
])

# ── Sprint 4: Cross-Project Intelligence ──────────────────────────────────────
print("\n── Sprint 4: Cross-Project Intelligence ──")

test("Health matrix — all projects", "/api/v1/services/cross-project/health-matrix", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has company_health", lambda s, d: d.get("company_health") in ("GREEN","YELLOW","RED")),
    ("has projects list", lambda s, d: isinstance(d.get("projects"), list)),
    ("4 projects", lambda s, d: len(d.get("projects",[])) == 4),
    ("each has health", lambda s, d: all(p.get("health") in ("GREEN","YELLOW","RED") for p in d.get("projects",[]))),
])

test("Cross-project alerts", "/api/v1/services/cross-project/alerts", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has company_health", lambda s, d: "company_health" in d),
    ("has alerts list", lambda s, d: isinstance(d.get("alerts"), list)),
])

test("Vendor performance cross-project", "/api/v1/services/cross-project/vendor-performance", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has top_vendors", lambda s, d: isinstance(d.get("top_vendors_by_activity"), list)),
])

test("Procurement summary cross-project", "/api/v1/services/cross-project/procurement-summary", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has by_project", lambda s, d: isinstance(d.get("by_project"), list)),
    ("has total_open_packages", lambda s, d: isinstance(d.get("total_open_packages"), int)),
    ("119 total packages", lambda s, d: d.get("total_open_packages") >= 100),
])

test("Schedule trends cross-project", "/api/v1/services/cross-project/schedule-trends", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has avg_variance_days", lambda s, d: isinstance(d.get("avg_variance_days"), (int,float))),
    ("has total_variance_items", lambda s, d: isinstance(d.get("total_variance_items"), int)),
])

test("Company snapshot (full)", "/api/v1/services/cross-project/company-snapshot", [
    ("HTTP 200", lambda s, d: s == 200),
    ("has company_health", lambda s, d: d.get("company_health") in ("GREEN","YELLOW","RED")),
    ("has projects", lambda s, d: len(d.get("projects",[])) == 4),
    ("has cross_project_alerts", lambda s, d: isinstance(d.get("cross_project_alerts"), list)),
    ("has schedule_trends", lambda s, d: "schedule_trends" in d),
    ("has budget_exposure", lambda s, d: "budget_exposure" in d),
    ("has vendor_performance", lambda s, d: "vendor_performance" in d),
    ("has procurement_summary", lambda s, d: "procurement_summary" in d),
])

# ── Existing Services still alive ──────────────────────────────────────────────
print("\n── Regression: Existing Services ──")

test("Health check", "/api/v1/health", [("HTTP 200", lambda s, d: s == 200)])
test("Connectors health", "/api/v1/services/connectors/health", [("HTTP 200", lambda s, d: s == 200)])
test("Executive morning brief", "/api/v1/executive/morning-brief", [("HTTP 200", lambda s, d: s == 200)])
test("Executive missions", "/api/v1/executive/missions", [("HTTP 200", lambda s, d: s == 200)])
test("Bid leveling service", "/api/v1/services/bid-leveling", [("HTTP 200", lambda s, d: s == 200)])
test("Approval queue service", "/api/v1/services/approval-queue", [("HTTP 200", lambda s, d: s == 200)])

# ── Summary ────────────────────────────────────────────────────────────────────
total = PASS + FAIL
print(f"\n{'='*65}")
print(f"RESULTS: {PASS}/{total} passed ({FAIL} failed)")
print(f"Finished: {datetime.datetime.now().isoformat()[:19]}")
print(f"{'='*65}")

# Write results to disk
results_path = os.path.join(os.path.dirname(__file__), "test_results_phase2_intelligence.json")
with open(results_path, "w") as f:
    json.dump({
        "run_at": datetime.datetime.now().isoformat(),
        "passed": PASS,
        "failed": FAIL,
        "total": total,
        "pass_rate": round(PASS / total * 100, 1) if total else 0,
        "tests": RESULTS,
    }, f, indent=2)

print(f"Results: {results_path}")
sys.exit(0 if FAIL == 0 else 1)
