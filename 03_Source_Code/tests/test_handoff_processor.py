"""
Tests for Agent Handoff Bus Processor
Covers: parsing, validation, routing, dry-run processing
"""
import sys, os, tempfile, shutil, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Architecture" / "Agent_Handoff"))
import handoff_processor as hp

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + str(detail) if detail else ''}")

# ── Test Setup ────────────────────────────────────────────────────────────────
VALID_FRONTMATTER = """---
source_agent: browser_claude
destination_agent: claude_code
document_type: browser_discovery
priority: high
status: pending
created_at: 2026-06-27
related_project: all
related_system: houzz_pro
intended_action: ingest_to_platform_intelligence
requires_approval: false
summary: Test browser discovery report
---

# Discovery Report

Test content here.
"""

VALID_JSON = json.dumps({
    "source_agent": "chatgpt_chief_architect",
    "destination_agent": "claude_code",
    "document_type": "chief_architect_directive",
    "priority": "high",
    "status": "pending",
    "created_at": "2026-06-27",
    "related_project": "all",
    "related_system": "hci_ai_os",
    "intended_action": "implement_directive",
    "requires_approval": False,
    "summary": "Test CA directive",
    "payload": "Build this feature."
})

print("Agent Handoff Bus Tests")
print("=" * 50)

# ── 1. Frontmatter Parsing ────────────────────────────────────────────────────
print("\n1. Frontmatter Parsing")
with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
    f.write(VALID_FRONTMATTER)
    fpath = Path(f.name)

header, payload = hp.parse_handoff(fpath)
check("Parses YAML frontmatter", bool(header))
check("source_agent extracted", header.get("source_agent") == "browser_claude")
check("document_type extracted", header.get("document_type") == "browser_discovery")
check("summary extracted", bool(header.get("summary")))
check("Payload is remaining content", "Discovery Report" in payload)
fpath.unlink()

# ── 2. JSON Parsing ───────────────────────────────────────────────────────────
print("\n2. JSON Parsing")
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    f.write(VALID_JSON)
    jpath = Path(f.name)

header_j, payload_j = hp.parse_handoff(jpath)
check("Parses JSON handoff", bool(header_j))
check("JSON source_agent", header_j.get("source_agent") == "chatgpt_chief_architect")
check("JSON document_type", header_j.get("document_type") == "chief_architect_directive")
check("JSON payload extracted", payload_j == "Build this feature.")
jpath.unlink()

# ── 3. Validation ─────────────────────────────────────────────────────────────
print("\n3. Validation")
valid_header = {
    "source_agent": "browser_claude", "destination_agent": "claude_code",
    "document_type": "browser_discovery", "priority": "high",
    "status": "pending", "created_at": "2026-06-27",
    "summary": "Test"
}
ok, msg = hp.validate_handoff(valid_header)
check("Valid header passes", ok, msg)

# Missing field - use a genuinely required one. created_at/summary are deliberately
# NOT in REQUIRED_FIELDS (auto-injected if absent, see handoff_processor.py comment) -
# this test used to delete "summary" and expect a failure that correctly no longer
# happens now that auto-injection exists. Found 2026-07-06 re-running the full suite.
bad = {**valid_header}
del bad["status"]
ok2, msg2 = hp.validate_handoff(bad)
check("Missing field fails", not ok2)
check("Error mentions missing field", "status" in msg2)

# Unknown document type
bad2 = {**valid_header, "document_type": "unknown_type"}
ok3, msg3 = hp.validate_handoff(bad2)
check("Unknown type fails", not ok3)
check("Error mentions unknown type", "unknown_type" in msg3)

# Empty header
ok4, msg4 = hp.validate_handoff({})
check("Empty header fails", not ok4)

# ── 4. All Valid Document Types ───────────────────────────────────────────────
print("\n4. Valid Document Types")
for doc_type in hp.VALID_TYPES:
    h = {**valid_header, "document_type": doc_type}
    ok, msg = hp.validate_handoff(h)
    check(f"Type '{doc_type}' validates", ok, msg)

# ── 5. Routing Map Coverage ───────────────────────────────────────────────────
print("\n5. Routing Coverage")
check("All types have routing entry", len(hp.ROUTING) == len(hp.VALID_TYPES))
# browser_discovery deliberately routes to None in ROUTING - it's resolved
# dynamically per related_system via SYSTEM_CURRENT_DIRS instead of one flat
# directory. Test used to assert the opposite; fixed 2026-07-06.
check("browser_discovery resolves dynamically via SYSTEM_CURRENT_DIRS",
      hp.ROUTING.get("browser_discovery") is None and len(hp.SYSTEM_CURRENT_DIRS) > 0)
check("chief_architect_directive routes to Handbook/Drafts",
      "Drafts" in str(hp.ROUTING.get("chief_architect_directive", "")))
check("implementation_request routing is None (append mode)",
      hp.ROUTING.get("implementation_request") is None)
check("approval_request routing is None (API mode)",
      hp.ROUTING.get("approval_request") is None)

# ── 6. Dry Run Processing ─────────────────────────────────────────────────────
print("\n6. Dry Run Processing")
tmp_dir = Path(tempfile.mkdtemp())
inbox = tmp_dir / "Inbox"
inbox.mkdir()

# Write a valid handoff to temp inbox
test_file = inbox / "test_handoff.md"
test_file.write_text(VALID_FRONTMATTER)

# Temporarily override paths for dry-run test
orig_inbox = hp.INBOX
orig_processing = hp.PROCESSING
orig_processed = hp.PROCESSED
orig_failed = hp.FAILED

hp.INBOX = inbox
hp.PROCESSING = tmp_dir / "Processing"
hp.PROCESSED = tmp_dir / "Processed"
hp.FAILED = tmp_dir / "Failed"
hp.INDEX = tmp_dir / "HANDOFF_INDEX.md"
for d in [hp.PROCESSING, hp.PROCESSED, hp.FAILED]:
    d.mkdir()

result = hp.process_file(test_file, dry_run=True)
check("Dry run returns result", bool(result))
check("Dry run status is PROCESSED", result["status"] == "PROCESSED")
check("Dry run file not moved", test_file.exists())  # dry run — no move
check("Dry run document_type correct", result["document_type"] == "browser_discovery")

# Restore
hp.INBOX = orig_inbox
hp.PROCESSING = orig_processing
hp.PROCESSED = orig_processed
hp.FAILED = orig_failed
shutil.rmtree(tmp_dir)

# ── 7. Required Fields List ───────────────────────────────────────────────────
# created_at/summary are deliberately excluded - auto-injected if absent rather than
# hard-required (see handoff_processor.py's REQUIRED_FIELDS comment). Test used to
# expect 7 fields including those two; fixed 2026-07-06.
print("\n7. Required Fields")
check("5 required fields defined", len(hp.REQUIRED_FIELDS) == 5)
for f in ["source_agent", "destination_agent", "document_type", "priority", "status"]:
    check(f"'{f}' is required", f in hp.REQUIRED_FIELDS)
for f in ["created_at", "summary"]:
    check(f"'{f}' is auto-injected, not hard-required", f not in hp.REQUIRED_FIELDS)

# ── Results ───────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
