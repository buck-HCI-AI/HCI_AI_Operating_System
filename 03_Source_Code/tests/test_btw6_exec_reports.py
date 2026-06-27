"""
BTW-6 — Executive Command Center: Weekly + Monthly Report Workflows
Tests: workflow structure, required nodes, data endpoints, ntfy integration
"""
import json
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent.parent / "workflows" / "n8n"
WEEKLY = WORKFLOWS_DIR / "AUTO-WEEKLY-EXEC.json"
MONTHLY = WORKFLOWS_DIR / "AUTO-MONTHLY-REVIEW.json"

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + str(detail) if detail else ''}")

def load(path):
    return json.loads(path.read_text())

print("BTW-6 Executive Command Center Tests")
print("=" * 50)

# ── 1. File Existence ─────────────────────────────────────────────────────────
print("\n1. Workflow Files Exist")
check("AUTO-WEEKLY-EXEC.json exists", WEEKLY.exists())
check("AUTO-MONTHLY-REVIEW.json exists", MONTHLY.exists())

weekly = load(WEEKLY)
monthly = load(MONTHLY)

# ── 2. Weekly Exec — Schedule ─────────────────────────────────────────────────
print("\n2. Weekly Exec — Schedule")
w_nodes = {n["name"]: n for n in weekly["nodes"]}
w_cron = next((n for n in weekly["nodes"] if "cron" in n["name"].lower() or "schedule" in n["type"].lower()), None)
check("Has scheduler node", w_cron is not None)
if w_cron:
    cron_expr = str(w_cron["parameters"])
    check("Friday 16:00 schedule (cron '0 16 * * 5')", "0 16 * * 5" in cron_expr, cron_expr[:100])

# ── 3. Weekly Exec — Required API Calls ──────────────────────────────────────
print("\n3. Weekly Exec — Required API Calls")
w_urls = [n["parameters"].get("url", "") for n in weekly["nodes"] if "url" in n.get("parameters", {})]
check("Calls /reports/weekly/company", any("reports/weekly/company" in u for u in w_urls))
check("Calls /executive/missions", any("executive/missions" in u for u in w_urls))
check("Calls /executive/morning-brief", any("morning-brief" in u for u in w_urls))

# ── 4. Weekly Exec — Report Generation ───────────────────────────────────────
print("\n4. Weekly Exec — Report Generation")
w_code_nodes = [n for n in weekly["nodes"] if "code" in n["type"].lower()]
check("Has code/JS node for report building", len(w_code_nodes) >= 1)
if w_code_nodes:
    code = w_code_nodes[0]["parameters"].get("jsCode", "")
    check("Builds company health section", "company_health" in code or "company health" in code.lower())
    check("Builds mission status section", "mission" in code.lower())
    check("Builds pending approvals section", "inbox_count" in code or "pending" in code.lower())
    check("Writes to reports/weekly/ path", "reports/weekly" in code)
    check("Priority escalates on risk/blocked", "projects_at_risk" in code or "at_risk" in code)

# ── 5. Weekly Exec — Output ───────────────────────────────────────────────────
print("\n5. Weekly Exec — Output Nodes")
w_write = [n for n in weekly["nodes"] if "write" in n["name"].lower() or "disk" in n["name"].lower()]
w_ntfy = [n for n in weekly["nodes"] if "ntfy" in n["name"].lower() or "ntfy.sh" in str(n.get("parameters", {}))]
check("Has write-to-disk node", len(w_write) >= 1)
check("Has ntfy notification node", len(w_ntfy) >= 1)
if w_ntfy:
    ntfy_params = str(w_ntfy[0]["parameters"])
    check("ntfy sends to hci-executive topic", "hci-executive" in ntfy_params)
    check("ntfy title is executive report", "Weekly Executive" in ntfy_params or "Executive Report" in ntfy_params)

# ── 6. Weekly Exec — Workflow Connections ─────────────────────────────────────
print("\n6. Weekly Exec — Connections")
w_conns = weekly["connections"]
check("Trigger fans out to 3 parallel API calls", len(list(w_conns.values())[0]["main"][0]) >= 3)
code_node_name = w_code_nodes[0]["name"] if w_code_nodes else None
if code_node_name:
    check("Build node feeds write + ntfy", len(w_conns.get(code_node_name, {}).get("main", [[]])[0]) >= 2)

# ── 7. Monthly Review — Schedule ─────────────────────────────────────────────
print("\n7. Monthly Review — Schedule")
m_cron = next((n for n in monthly["nodes"] if "cron" in n["name"].lower() or "schedule" in n["type"].lower()), None)
check("Has scheduler node", m_cron is not None)
if m_cron:
    cron_expr = str(m_cron["parameters"])
    check("1st of month 09:00 (cron '0 9 1 * *')", "0 9 1 * *" in cron_expr, cron_expr[:100])

# ── 8. Monthly Review — Required API Calls ───────────────────────────────────
print("\n8. Monthly Review — Required API Calls")
m_urls = [n["parameters"].get("url", "") for n in monthly["nodes"] if "url" in n.get("parameters", {})]
check("Calls /executive/mission-control", any("mission-control" in u for u in m_urls))
check("Calls /services/autonomy/report", any("autonomy/report" in u for u in m_urls))
check("Calls /reports/weekly/company", any("reports/weekly/company" in u for u in m_urls))

# ── 9. Monthly Review — Report Content ───────────────────────────────────────
print("\n9. Monthly Review — Report Content")
m_code_nodes = [n for n in monthly["nodes"] if "code" in n["type"].lower()]
check("Has code/JS node for report building", len(m_code_nodes) >= 1)
if m_code_nodes:
    code = m_code_nodes[0]["parameters"].get("jsCode", "")
    check("Includes AI ROI section", "hours_saved" in code or "roi" in code.lower())
    check("Includes portfolio health section", "company_health" in code or "portfolio" in code.lower())
    check("Includes mission status section", "mission" in code.lower())
    check("Writes to reports/monthly/ path", "reports/monthly" in code)
    check("Generates next month priorities", "Next Month" in code or "priorities" in code.lower())
    check("Uses prev month label", "prevMonth" in code or "prev_month" in code.lower())

# ── 10. Monthly Review — Output Nodes ────────────────────────────────────────
print("\n10. Monthly Review — Output Nodes")
m_write = [n for n in monthly["nodes"] if "write" in n["name"].lower() or "disk" in n["name"].lower()]
m_ntfy = [n for n in monthly["nodes"] if "ntfy" in n["name"].lower() or "ntfy.sh" in str(n.get("parameters", {}))]
check("Has write-to-disk node", len(m_write) >= 1)
check("Has ntfy notification node", len(m_ntfy) >= 1)
if m_ntfy:
    ntfy_params = str(m_ntfy[0]["parameters"])
    check("ntfy sends to hci-executive", "hci-executive" in ntfy_params)
    check("ntfy title is monthly review", "Monthly" in ntfy_params)

# ── 11. Monthly Review — Connections ─────────────────────────────────────────
print("\n11. Monthly Review — Connections")
m_conns = monthly["connections"]
check("Trigger fans out to 3 parallel API calls", len(list(m_conns.values())[0]["main"][0]) >= 3)

# ── 12. Metadata / Tags ───────────────────────────────────────────────────────
print("\n12. Metadata and Tags")
check("Weekly workflow has btw-6 tag", any("btw-6" in str(t) for t in weekly.get("tags", [])))
check("Monthly workflow has btw-6 tag", any("btw-6" in str(t) for t in monthly.get("tags", [])))
check("Weekly has _hci_notes", bool(weekly.get("_hci_notes")))
check("Monthly has _hci_notes", bool(monthly.get("_hci_notes")))

# ── Results ───────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
