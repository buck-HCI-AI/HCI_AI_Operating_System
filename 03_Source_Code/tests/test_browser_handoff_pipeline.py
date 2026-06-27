"""
Browser Handoff Pipeline + Handoff Intake Infrastructure Tests
Covers: handoff_processor.py auto-inject, routing, folder structure,
watcher script, Browser Claude protocol, n8n workflow imports.
"""
import json, subprocess, sys
from pathlib import Path

BASE   = Path("/Users/buckadams/HCI_AI_Operating_System")
AGENT  = BASE / "Architecture/Agent_Handoff"
PI     = BASE / "Architecture/Platform_Intelligence"
WF_DIR = BASE / "03_Source_Code/workflows/n8n"
INFRA  = BASE / "infrastructure"

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + str(detail) if detail else ''}")

print("Browser Handoff Pipeline Tests")
print("=" * 55)

# ── 1. Folder Structure ───────────────────────────────────────
print("\n1. Platform Intelligence Folder Structure")
for system in ["HubSpot", "Houzz", "GoogleDrive", "Microsoft365", "QuickBooks",
                "n8n", "PostgreSQL", "BuildingConnected", "Procore"]:
    check(f"{system}/ exists", (PI / system).is_dir())

for system in ["HubSpot", "Houzz"]:
    check(f"{system}/Current/ exists",  (PI / system / "Current").is_dir())
    check(f"{system}/Archive/ exists",  (PI / system / "Archive").is_dir())
    check(f"{system}/Opportunities/ exists", (PI / system / "Opportunities").is_dir())

# ── 2. Platform Intelligence Documents ───────────────────────
print("\n2. Platform Intelligence Documents")
check("HubSpot intelligence V1 exists",
      (PI / "HubSpot/Current/HUBSPOT_PLATFORM_INTELLIGENCE_V1.md").exists())
check("Houzz intelligence V1 exists",
      (PI / "Houzz/Current/HOUZZ_PLATFORM_INTELLIGENCE_V1.md").exists())
check("Automation opportunity catalog exists",
      (PI / "AUTOMATION_OPPORTUNITY_CATALOG.md").exists())
check("HubSpot opportunities doc exists",
      (PI / "HubSpot/Opportunities/HUBSPOT_AUTOMATION_OPPORTUNITIES.md").exists())
check("Houzz opportunities doc exists",
      (PI / "Houzz/Opportunities/HOUZZ_AUTOMATION_OPPORTUNITIES.md").exists())

# ── 3. Agent Handoff Bus ──────────────────────────────────────
print("\n3. Agent Handoff Bus")
for d in ["Inbox", "Processing", "Processed", "Failed", "Archive"]:
    check(f"{d}/ directory exists", (AGENT / d).is_dir())
check("handoff_processor.py exists", (AGENT / "handoff_processor.py").exists())
check("BROWSER_CLAUDE_DISCOVERY_PROTOCOL.md exists",
      (AGENT / "BROWSER_CLAUDE_DISCOVERY_PROTOCOL.md").exists())

# Protocol content checks
protocol = (AGENT / "BROWSER_CLAUDE_DISCOVERY_PROTOCOL.md").read_text()
check("Protocol has HubSpot checklist", "HubSpot Discovery Checklist" in protocol)
check("Protocol has Houzz checklist", "Houzz Pro Discovery Checklist" in protocol)
check("Protocol has direct Inbox path", "Agent_Handoff/Inbox" in protocol)
check("Protocol has required frontmatter", "created_at" in protocol and "summary" in protocol)
check("Protocol has filename convention", "BROWSER_HANDOFF_" in protocol)

# ── 4. Processor Auto-Inject & Routing ───────────────────────
print("\n4. Handoff Processor — Auto-Inject + Routing")
# Test with a file missing created_at/summary
test_file = AGENT / "Inbox" / "_TEST_AUTO_INJECT.md"
test_file.write_text("""---
source_agent: Browser Claude
destination_agent: Claude Code
document_type: browser_discovery
priority: high
status: ready_for_processing
related_system: HubSpot
intended_action: ingest_and_route
requires_approval: false
---
# Auto-inject test
""")
result = subprocess.run(
    [sys.executable, str(AGENT / "handoff_processor.py")],
    capture_output=True, text=True
)
check("Processor runs without error", result.returncode == 0, result.stderr[:100])
check("Auto-inject accepted file (no INVALID)", "INVALID" not in result.stdout)
check("File routed to HubSpot/Current", "HubSpot/Current" in result.stdout)

# Verify file landed in correct directory
hubspot_files = list((PI / "HubSpot/Current").glob("_TEST_AUTO_INJECT.md"))
check("Auto-inject file in HubSpot/Current", len(hubspot_files) > 0)

# Test Houzz routing
test_houzz = AGENT / "Inbox" / "_TEST_HOUZZ_ROUTE.md"
test_houzz.write_text("""---
source_agent: Browser Claude
destination_agent: Claude Code
document_type: browser_discovery
priority: high
status: ready_for_processing
related_system: Houzz Pro
intended_action: ingest_and_route
requires_approval: false
created_at: 2026-06-27
summary: Houzz routing test
---
# Houzz test
""")
result2 = subprocess.run(
    [sys.executable, str(AGENT / "handoff_processor.py")],
    capture_output=True, text=True
)
check("Houzz routing works", "Houzz/Current" in result2.stdout, result2.stdout)

# ── 5. Intake Watcher ────────────────────────────────────────
print("\n5. Handoff Intake Watcher")
watcher = INFRA / "handoff_intake_watcher.py"
check("handoff_intake_watcher.py exists", watcher.exists())

watcher_text = watcher.read_text()
check("Watcher has BROWSER_HANDOFF_ prefix", "BROWSER_HANDOFF_" in watcher_text)
check("Watcher has HCI_HANDOFF_ prefix", "HCI_HANDOFF_" in watcher_text)
check("Watcher calls handoff_processor.py", "handoff_processor.py" in watcher_text)
check("Watcher logs to infrastructure/logs", "handoff_intake.log" in watcher_text)

check("Desktop command file exists",
      Path.home().joinpath("Desktop/HCI_Process_Handoffs.command").exists())
check("launchd plist exists",
      Path.home().joinpath("Library/LaunchAgents/com.hci.handoff-intake.plist").exists())

# ── 6. n8n Workflows — AO-HS-001/002/004/010 ─────────────────
print("\n6. New n8n Workflows")
for fname, required_nodes in [
    ("AUTO-COI-COMPLIANCE-ENGINE.json",
     ["Cron Daily 07:00", "Evaluate COI Status", "Update COI Status in HubSpot", "Build Renewal Alert"]),
    ("AUTO-BID-INVITATION-TASKS.json",
     ["Poll 3x Daily", "Fetch Sent Out Deals", "Create HubSpot Task"]),
    ("AUTO-AI-DEAL-SUMMARIZATION.json",
     ["Cron Weekdays 06:00", "Fetch Active Deals", "Claude API", "Post to Executive Inbox"]),
]:
    path = WF_DIR / fname
    check(f"{fname} exists", path.exists())
    if path.exists():
        wf = json.loads(path.read_text())
        node_names = [n["name"] for n in wf.get("nodes", [])]
        for req in required_nodes:
            check(f"  Has '{req}' node", any(req in n for n in node_names))
        check(f"  Has ntfy notification", "ntfy.sh/hci-executive" in str(wf))
        check(f"  Has HUBSPOT_API_KEY ref", "HUBSPOT_API_KEY" in str(wf))

# AO-HS-010 specific: Claude API
wf010 = json.loads((WF_DIR / "AUTO-AI-DEAL-SUMMARIZATION.json").read_text())
check("AI summarization calls Claude Haiku", "claude-haiku" in str(wf010))
check("AI summarization uses ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY" in str(wf010))

# ── 7. COI Workflow Logic ──────────────────────────────────────
print("\n7. COI Workflow Logic")
coi_wf = json.loads((WF_DIR / "AUTO-COI-COMPLIANCE-ENGINE.json").read_text())
eval_node = next((n for n in coi_wf["nodes"] if "Evaluate" in n["name"]), None)
check("Evaluate node exists", eval_node is not None)
if eval_node:
    code = eval_node["parameters"].get("jsCode", "")
    check("Evaluates Expired status", "Expired" in code)
    check("Evaluates Active status", "'Active'" in code)
    check("Evaluates Missing status", "Missing" in code)
    check("30-day renewal window", "30" in code)
    check("Calculates days_until_expiry", "daysUntil" in code)

# 7-day urgency is in the renewal message node
renewal_node = next((n for n in coi_wf["nodes"] if n["name"] == "Build Renewal Alert"), None)
check("7-day urgent window in renewal node",
      renewal_node is not None and "7" in renewal_node["parameters"].get("jsCode", ""))

# ── Results ────────────────────────────────────────────────────
print(f"\n{'='*55}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
