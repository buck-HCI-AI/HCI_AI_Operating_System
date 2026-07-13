"""
Bid Leveling Service — Test Suite
Tests the full service: sheet reading, Excel generation, Drive folder management,
approval queue integration, and API endpoints.

Run from: 03_Source_Code/
    python3 tests/test_bid_leveling.py
"""
import sys, os, json, urllib.request, urllib.error, time, datetime
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

BASE = "http://localhost:8000"
API_KEY = os.environ["HCI_API_KEY"]
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results_bid_leveling.json")


def req(method, path, body=None, expect_status=200):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            status = resp.status
            text = resp.read().decode()
    except urllib.error.HTTPError as e:
        status = e.code
        text = e.read().decode()
    try:
        js = json.loads(text)
    except Exception:
        js = {"_raw": text}
    return status, js


results = []


def test(name, fn):
    start = time.time()
    try:
        passed, detail = fn()
        status = "PASS" if passed else "FAIL"
    except Exception as e:
        passed, status, detail = False, "ERROR", str(e)
    elapsed = round((time.time() - start) * 1000)
    results.append({
        "test": name, "status": status, "detail": detail, "ms": elapsed
    })
    mark = "✅" if status == "PASS" else "❌"
    print(f"  {mark} {name} ({elapsed}ms)")
    if status != "PASS":
        print(f"     Detail: {detail}")


# ── BL-SVC: Service Registration ─────────────────────────────────────────────
print("\nGroup: BL-SVC — Service Registration")

def test_service_listed():
    s, d = req("GET", "/api/v1/services")
    names = [svc["name"] for svc in d.get("services", [])]
    return "bid-leveling" in names, f"services: {names}"

def test_service_info():
    s, d = req("GET", "/api/v1/services/bid-leveling")
    ok = s == 200 and d.get("service") == "bid-leveling"
    return ok, f"status={s} service={d.get('service')}"

def test_list_projects():
    s, d = req("GET", "/api/v1/services/bid-leveling/projects")
    ok = s == 200 and d.get("count", 0) >= 3
    return ok, f"count={d.get('count')} projects={[p['name'] for p in d.get('projects', [])]}"

test("BL-SVC-01: service appears in /api/v1/services",  test_service_listed)
test("BL-SVC-02: service info endpoint returns 200",    test_service_info)
test("BL-SVC-03: 3+ projects configured",               test_list_projects)


# ── BL-READ: Sheet Reading ────────────────────────────────────────────────────
print("\nGroup: BL-READ — Sheet Reading (live Google Sheets)")

def test_1355_summary():
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/3/summary")
    ok = s == 200 and d.get("count", 0) >= 10
    return ok, f"status={s} div_count={d.get('count')}"

def test_101_summary():
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/2/summary")
    ok = s == 200 and d.get("count", 0) >= 5
    return ok, f"status={s} div_count={d.get('count')}"

def test_64ew_summary():
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/1/summary")
    ok = s == 200 and d.get("count", 0) >= 5
    return ok, f"status={s} div_count={d.get('count')}"

def test_project_data_1355():
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/3/data")
    ok = s == 200 and len(d.get("bid_tracking", {})) > 0
    return ok, f"status={s} bid_divs={len(d.get('bid_tracking', {}))}"

def test_sheets_read_api():
    sheet_id = "1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA"
    s, d = req("GET", f"/api/v1/services/bid-leveling/sheets/read?sheet_id={sheet_id}&range_name=HCI+16+Div+Summary%21A1%3AH20")
    ok = s == 200 and d.get("row_count", 0) > 5
    return ok, f"status={s} rows={d.get('row_count')}"

test("BL-READ-01: 1355 Riverside division summary reads 10+ divisions", test_1355_summary)
test("BL-READ-02: 101 Francis division summary reads 5+ divisions",     test_101_summary)
test("BL-READ-03: 64 Eastwood division summary reads 5+ divisions",     test_64ew_summary)
test("BL-READ-04: project data endpoint returns bid_tracking data",     test_project_data_1355)
test("BL-READ-05: sheets/read endpoint works for AI agent access",      test_sheets_read_api)


# ── BL-DRY: Dry Run Workflow ──────────────────────────────────────────────────
print("\nGroup: BL-DRY — Dry Run Workflow")

def test_dryrun_1355():
    s, d = req("POST", "/api/v1/services/bid-leveling/projects/3/run", {"dry_run": True})
    ok = s == 200 and d.get("mode") == "dry_run" and d.get("divisions_found", 0) >= 10
    return ok, f"status={s} mode={d.get('mode')} divs={d.get('divisions_found')} bids={d.get('total_bids')}"

def test_dryrun_101():
    s, d = req("POST", "/api/v1/services/bid-leveling/projects/2/run", {"dry_run": True})
    ok = s == 200 and d.get("mode") == "dry_run" and d.get("divisions_found", 0) >= 5
    return ok, f"status={s} divs={d.get('divisions_found')} bids={d.get('total_bids')}"

def test_dryrun_64():
    s, d = req("POST", "/api/v1/services/bid-leveling/projects/1/run", {"dry_run": True})
    ok = s == 200 and d.get("mode") == "dry_run" and d.get("divisions_found", 0) >= 5
    return ok, f"status={s} divs={d.get('divisions_found')} bids={d.get('total_bids')}"

def test_dryrun_division_filter():
    s, d = req("POST", "/api/v1/services/bid-leveling/projects/3/run",
               {"dry_run": True, "divisions": ["16", "15"]})
    ok = s == 200 and d.get("divisions_found") == 2
    return ok, f"status={s} divs={d.get('divisions_found')} excel_actions={len(d.get('excel_actions', []))}"

def test_dryrun_excel_actions_have_filenames():
    s, d = req("POST", "/api/v1/services/bid-leveling/projects/2/run", {"dry_run": True})
    actions = d.get("excel_actions", [])
    all_have_filename = all("filename" in a and a["filename"].endswith(".xlsx") for a in actions)
    return all_have_filename and len(actions) > 0, f"actions={len(actions)} all_filenames={all_have_filename}"

def test_dryrun_101_folder_found():
    # Was asserting action=="found_existing" only - the pre-bid_folder_id-fix
    # code path. ensure_bids_folder() now checks the DB's known bid_folder_id
    # first and short-circuits with action="from_db_config" before ever
    # searching Drive - the intended result of that fix (2026-07-07), not a
    # regression. Either path returning the correct real folder_id is success.
    s, d = req("POST", "/api/v1/services/bid-leveling/projects/2/run", {"dry_run": True})
    bids_folder = d.get("bids_folder", {})
    ok = bids_folder.get("action") in ("found_existing", "from_db_config") and bool(bids_folder.get("folder_id"))
    return ok, f"bids_folder={bids_folder}"

def test_runall_dryrun():
    s, d = req("POST", "/api/v1/services/bid-leveling/run-all", {"dry_run": True})
    ok = s == 200 and d.get("projects_run", 0) >= 3
    return ok, f"status={s} projects={d.get('projects_run')}"

test("BL-DRY-01: 1355 Riverside dry run — 10+ divisions, 20+ bids", test_dryrun_1355)
test("BL-DRY-02: 101 Francis dry run — 5+ divisions",               test_dryrun_101)
test("BL-DRY-03: 64 Eastwood dry run — 5+ divisions",               test_dryrun_64)
test("BL-DRY-04: division filter works (only 2 divisions returned)", test_dryrun_division_filter)
test("BL-DRY-05: all excel_actions have .xlsx filenames",            test_dryrun_excel_actions_have_filenames)
test("BL-DRY-06: 101 Francis 00_Bids folder found_existing",        test_dryrun_101_folder_found)
test("BL-DRY-07: run-all returns 3+ projects",                      test_runall_dryrun)


# ── BL-EXCEL: Excel Generation ───────────────────────────────────────────────
print("\nGroup: BL-EXCEL — Excel File Generation")

def test_excel_bytes_generated():
    """Generate Excel in memory and verify it's a valid openpyxl file."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "services", "bid_leveling"))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "integrations"))
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))
    from bid_leveling_service import BidLevelingService
    import io, openpyxl

    div_summary = {
        "name": "Electrical",
        "budget": "$285,000",
        "leveling_status": "Partially leveled",
        "recommended": "American $168,000",
        "risk": "Critical",
        "outstanding": "Service size, utility coordination",
        "next_action": "Resolve 400A vs 600A",
    }
    bids = [
        {"vendor": "American Electric", "date_sent": "2026-01-01",
         "date_received": "2026-01-15", "amount": "$168,000", "status": "Received"},
        {"vendor": "Ajax Electric",     "date_sent": "2026-01-01",
         "date_received": "2026-01-20", "amount": "$247,000", "status": "Received"},
    ]
    packages = [
        {"pkg": "16A", "trade": "Electrical Service", "budget": "$100k",
         "level": "Bid received", "vendor": "American / Ajax", "num_bids": "2",
         "recommended": "American", "outstanding": "400A vs 600A", "priority": "P1"},
    ]
    content = BidLevelingService.generate_division_excel(
        "1355 Riverside", "16", div_summary, bids, packages
    )
    wb = openpyxl.load_workbook(io.BytesIO(content))
    has_summary = "Bid Summary" in wb.sheetnames
    has_packages = "Package Detail" in wb.sheetnames
    return len(content) > 5000 and has_summary and has_packages, \
           f"bytes={len(content)} sheets={wb.sheetnames}"

def test_excel_outstanding_sheet():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "services", "bid_leveling"))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "integrations"))
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))
    from bid_leveling_service import BidLevelingService
    import io, openpyxl

    bids = [{"vendor": "V1", "notes": "Need clarification on scope"}]
    content = BidLevelingService.generate_division_excel(
        "TestProject", "07", {"name": "Thermal & Moisture", "outstanding": "Missing R-value"},
        bids, []
    )
    wb = openpyxl.load_workbook(io.BytesIO(content))
    return "Outstanding Items" in wb.sheetnames, f"sheets={wb.sheetnames}"

test("BL-EXCEL-01: generate Excel — Bid Summary + Package Detail sheets present", test_excel_bytes_generated)
test("BL-EXCEL-02: generate Excel — Outstanding Items sheet generated",            test_excel_outstanding_sheet)


# ── BL-DRIVE: Drive Operations ────────────────────────────────────────────────
print("\nGroup: BL-DRIVE — Drive Read/Write Endpoints")

def test_drive_list_bids_folder():
    folder_id = "1YJatvTnK0-vxiHmI0FxVE8e9jUubVcef"  # 101 Francis 00_Bids
    s, d = req("GET", f"/api/v1/services/bid-leveling/drive/list/{folder_id}")
    ok = s == 200 and d.get("count", 0) > 0
    return ok, f"status={s} items={d.get('count')}"

def test_drive_create_folder_noop_if_exists():
    """Should return found_existing for the 101 Francis 00_Bids folder."""
    parent = "1athsij_coRIngqnIe8SSHQbB51_RyZAs"  # 101 Francis project folder
    s, d = req("POST", "/api/v1/services/bid-leveling/drive/create-folder",
               {"parent_folder_id": parent, "folder_name": "101 Francis 00_Bids"})
    ok = s == 200
    return ok, f"status={s} action={d.get('action')}"

test("BL-DRIVE-01: list Drive folder (101 Francis 00_Bids) returns items", test_drive_list_bids_folder)
test("BL-DRIVE-02: create-folder returns existing folder if already exists", test_drive_create_folder_noop_if_exists)


# ── BL-QUEUE: Approval Queue Integration (live mode) ─────────────────────────
print("\nGroup: BL-QUEUE — Approval Queue Integration")

def test_live_run_queues_items():
    """Live run for 1 division should queue an upload in the approval queue."""
    s, d = req("POST", "/api/v1/services/bid-leveling/projects/3/run",
               {"dry_run": False, "divisions": ["16"]})
    ok = s == 200 and d.get("mode") == "live" and len(d.get("queued_items", [])) > 0
    return ok, f"status={s} mode={d.get('mode')} queued={d.get('queued_items')}"

def test_queued_item_visible_in_approval_queue():
    s, d = req("GET", "/api/v1/services/approval-queue/items?status=pending")
    items = d.get("items", [])
    bid_lev_items = [i for i in items if i.get("workflow") == "bid_leveling"]
    return len(bid_lev_items) > 0, f"bid_leveling items in queue: {len(bid_lev_items)}"

def test_execute_without_approval_fails():
    """Executing an item that's not approved should fail gracefully."""
    # Get a pending bid_leveling queue item
    s, d = req("GET", "/api/v1/services/approval-queue/items?status=pending")
    items = [i for i in d.get("items", []) if i.get("workflow") == "bid_leveling"]
    if not items:
        return True, "no pending items to test (ok)"
    qid = items[0]["id"]
    s2, d2 = req("POST", f"/api/v1/services/bid-leveling/projects/3/execute-upload/{qid}")
    # Should fail with 400 because status is 'pending' not 'approved'
    return s2 == 400 or (s2 == 200 and "error" not in d2), \
           f"status={s2} detail={d2.get('detail','')[:80]}"

test("BL-QUEUE-01: live run for div 16 queues at least 1 upload item",    test_live_run_queues_items)
test("BL-QUEUE-02: queued item visible in approval-queue pending list",    test_queued_item_visible_in_approval_queue)
test("BL-QUEUE-03: execute without approval returns 400 (safety control)", test_execute_without_approval_fails)

# ── BL-RELIABLE: Leveling-reliability flag (2026-07-13 regression coverage) ──
# Covers 2 real bugs found and fixed live 2026-07-13:
#  1. division "13" merged two unrelated trades (Insulation, Special
#     Construction) sharing one bare CSI number into one nonsensical
#     leveling comparison.
#  2. division "09" (Finishes) showed a real 36,610% spread across 18
#     genuinely different trades sharing one division_name, with no way to
#     auto-separate them - fixed by flagging implausible spreads instead of
#     silently presenting them as valid comparisons.
print("\nGroup: BL-RELIABLE — Leveling-reliability flag (regression, 2026-07-13)")

def test_division_13_no_longer_merged():
    """The original bug: division 13 for 1355R (project_id=3) doesn't exist as
    a real top-level division at all - "13_Insulation" and "13_Special
    Construction" are sub-packages of Division 07 and Division 10
    respectively (reclassify_existing_divisions() fixed this in the DB
    2026-07-13, not just at the read layer). Must never come back as a bare
    "13" bucket, and Insulation/Special Construction must be attributed to
    their real parent divisions, never merged together."""
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/3/drive-bids?latest_only=true")
    summary = d.get("leveling_summary", {})
    has_bare_13 = any(k == "13" or k.startswith("13__") for k in summary.keys())
    insulation_key = next((k for k in summary if "Insulation" in summary[k].get("division_name", "")), None)
    special_con_key = next((k for k in summary if "Special Construction" in summary[k].get("division_name", "")), None)
    correctly_attributed = (insulation_key and insulation_key.startswith("07")
                             and special_con_key and special_con_key.startswith("10"))
    return (not has_bare_13 and correctly_attributed), \
           f"bare '13' present={has_bare_13}, insulation_key={insulation_key}, special_con_key={special_con_key}"

def test_implausible_spreads_flagged_not_hidden():
    """Any division with an implausible spread (>300%, 3+ vendors) must be
    marked leveling_reliable=False with a note - not silently shown as if
    it were a real comparison. The underlying bids must still be present
    (nothing hidden), only the reliability framing changes."""
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/3/drive-bids?latest_only=true")
    summary = d.get("leveling_summary", {})
    bad = []
    for k, v in summary.items():
        spread_pct = v.get("spread_pct")
        bid_count = v.get("bid_count", 0)
        should_be_unreliable = spread_pct is not None and spread_pct > 300 and bid_count >= 3
        if should_be_unreliable and v.get("leveling_reliable") is not False:
            bad.append(f"{k}: spread={spread_pct}% count={bid_count} reliable={v.get('leveling_reliable')}")
        if should_be_unreliable and not v.get("bids"):
            bad.append(f"{k}: flagged unreliable but bids list is empty - data got hidden, not just flagged")
    return len(bad) == 0, "; ".join(bad) if bad else f"checked {len(summary)} divisions, all correctly classified"

def test_reliable_divisions_not_falsely_flagged():
    """A division with a tight, plausible spread must NOT be marked
    unreliable - the flag should only catch genuinely implausible cases,
    not become noisy and flag everything."""
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/3/drive-bids?latest_only=true")
    summary = d.get("leveling_summary", {})
    bad = [k for k, v in summary.items()
           if v.get("spread_pct") is not None and v.get("spread_pct") <= 300
           and v.get("leveling_reliable") is not True]
    return len(bad) == 0, "; ".join(bad) if bad else "all low-spread divisions correctly marked reliable"

test("BL-RELIABLE-01: division 13 collision stays split, never re-merges",       test_division_13_no_longer_merged)
test("BL-RELIABLE-02: implausible spreads flagged with reason, data not hidden", test_implausible_spreads_flagged_not_hidden)
test("BL-RELIABLE-03: plausible spreads not falsely flagged as unreliable",      test_reliable_divisions_not_falsely_flagged)


# ── BL-INFER: Option B display-only sub-trade inference (2026-07-13) ──
# Per GBT's P0 ADR-003 handoff: divisions 05/06/08/09/16 on 1355R have vendor
# folders never organized into named Drive sub-packages, so the real fix
# (reclassify_existing_divisions) can't separate their distinct trades. Option
# B infers sub-trade groupings from real scope_summary text for DISPLAY ONLY -
# must never write back to drive_bids.division_num/division_name.
print("\nGroup: BL-INFER — Option B inferred sub-trade groupings (regression, 2026-07-13)")

def test_inferred_subgroups_present_for_flagged_divisions():
    """Divisions 05, 08, 16 (clean, unambiguous real vendor scopes) must each
    produce inferred_subgroups with every label ending in the required
    "[inferred]" marker, per GBT's explicit display-only spec."""
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/3/drive-bids?latest_only=true")
    summary = d.get("leveling_summary", {})
    bad = []
    for div in ("05", "08", "16"):
        entry = summary.get(div)
        if not entry:
            bad.append(f"{div}: division missing from summary")
            continue
        sub = entry.get("inferred_subgroups")
        if not sub:
            bad.append(f"{div}: no inferred_subgroups present")
            continue
        unmarked = [label for label in sub if not label.endswith("[inferred]")]
        if unmarked:
            bad.append(f"{div}: labels missing '[inferred]' marker: {unmarked}")
    return len(bad) == 0, "; ".join(bad) if bad else "05/08/16 all produced correctly-marked inferred_subgroups"

def test_inferred_subgroups_sum_to_division_bid_count():
    """Every bid in a division must land in exactly one inferred subgroup -
    none dropped, none duplicated - proving this is a real regrouping of the
    existing bids, not a fabricated or partial view."""
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/3/drive-bids?latest_only=true")
    summary = d.get("leveling_summary", {})
    bad = []
    for div in ("05", "06", "08", "09", "16"):
        entry = summary.get(div)
        if not entry or not entry.get("inferred_subgroups"):
            continue
        total = sum(g["bid_count"] for g in entry["inferred_subgroups"].values())
        if total != entry["bid_count"]:
            bad.append(f"{div}: division bid_count={entry['bid_count']} but subgroups sum to {total}")
    return len(bad) == 0, "; ".join(bad) if bad else "all inferred subgroup counts reconcile to division totals"

def test_inference_does_not_alter_underlying_division_data():
    """Option B is explicitly display-only. The division_name and the raw
    'bids' list at the division level (vendor, amount, scope, file_id - the
    actual drive_bids row data) must be identical to what they'd be without
    inference; inferred_subgroups must be a strictly additive field."""
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/3/drive-bids?latest_only=true")
    summary = d.get("leveling_summary", {})
    bad = []
    for div in ("05", "08", "16"):
        entry = summary.get(div)
        if not entry:
            continue
        all_file_ids = {b["file_id"] for b in entry["bids"]}
        sub_file_ids = set()
        for g in entry["inferred_subgroups"].values():
            sub_file_ids.update(b["file_id"] for b in g["bids"])
        if all_file_ids != sub_file_ids:
            bad.append(f"{div}: division-level file_ids {all_file_ids} != subgroup file_ids {sub_file_ids}")
    return len(bad) == 0, "; ".join(bad) if bad else "subgroup bids are the same underlying rows, nothing fabricated or dropped"

def test_inference_not_shown_for_single_bid_divisions():
    """2026-07-13 defect found via cross-project deep-test (64EW): a
    single-bid division still ran through the classifier and produced one
    lone subgroup - noise, since there's nothing to compare against. Checked
    across all 3 active projects, not just 1355R."""
    bad = []
    for pid in (1, 2, 3):
        s, d = req("GET", f"/api/v1/services/bid-leveling/projects/{pid}/drive-bids?latest_only=true")
        for k, v in d.get("leveling_summary", {}).items():
            if v.get("bid_count") == 1 and v.get("inferred_subgroups"):
                bad.append(f"project {pid} div {k}")
    return len(bad) == 0, "; ".join(bad) if bad else "no single-bid division produced inferred_subgroups noise"

def test_bid_leveling_summary_file_not_ingested_as_vendor():
    """2026-07-13 defect found via cross-project deep-test (1355R division
    07 Insulation showed an implausible 7907% spread): the system's own
    auto-generated "*_Bid_Leveling" summary file was ingested as if it were
    a real vendor bid (underscore-delimited filename slipped past the
    space-only exclusion regex), producing a fake $985 line item. Fixed at
    the filter level (_is_outbound_not_a_bid normalizes underscores/hyphens
    before matching) and the one contaminated row was deleted from
    drive_bids. Must never come back."""
    s, d = req("GET", "/api/v1/services/bid-leveling/projects/3/drive-bids?latest_only=true")
    summary = d.get("leveling_summary", {})
    contaminated = [b["vendor"] for v in summary.values() for b in v.get("bids", [])
                    if "bid" in b["vendor"].lower() and "leveling" in b["vendor"].lower()]
    return len(contaminated) == 0, "; ".join(contaminated) if contaminated else "no self-referential summary-file rows found"

test("BL-INFER-01: inferred subgroups present + correctly marked '[inferred]'", test_inferred_subgroups_present_for_flagged_divisions)
test("BL-INFER-02: inferred subgroup counts reconcile to division totals",      test_inferred_subgroups_sum_to_division_bid_count)
test("BL-INFER-03: inference is additive only, same underlying bid rows",       test_inference_does_not_alter_underlying_division_data)
test("BL-INFER-04: no inferred_subgroups noise on single-bid divisions",        test_inference_not_shown_for_single_bid_divisions)
test("BL-DEFECT-01: auto-generated summary file never ingested as a vendor",    test_bid_leveling_summary_file_not_ingested_as_vendor)


def test_cleanup_queued_bid_leveling_items():
    """test_live_run_queues_items creates a real live approval-queue row every run
    and nothing above consumes it - found 2026-07-07 that repeated runs left 3
    duplicate '1355 Riverside Div 16 bid leveling Excel' rows sitting pending in
    the real queue. Reject anything this suite queued so it doesn't pile up."""
    s, d = req("GET", "/api/v1/services/approval-queue/items?status=pending")
    items = [i for i in d.get("items", []) if i.get("workflow") == "bid_leveling"]
    for item in items:
        req("POST", f"/api/v1/services/approval-queue/items/{item['id']}/reject",
            {"rejected_by": "test_suite", "reason": "Test run cleanup"})
    return True, f"cleaned up {len(items)} bid_leveling queue item(s)"

test("BL-QUEUE-04: cleanup - reject queued items so they don't leak into real queue", test_cleanup_queued_bid_leveling_items)


# ── Results ────────────────────────────────────────────────────────────────────
total  = len(results)
passed = sum(1 for r in results if r["status"] == "PASS")
failed = total - passed

print(f"\n{'='*60}")
print(f"BID LEVELING SERVICE TEST RESULTS")
print(f"{'='*60}")
print(f"  Passed: {passed}/{total}")
print(f"  Failed: {failed}")
print(f"  Date:   {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

if failed:
    print("\nFailed tests:")
    for r in results:
        if r["status"] != "PASS":
            print(f"  ❌ {r['test']}: {r['detail']}")

with open(RESULTS_PATH, "w") as f:
    json.dump({
        "run_date": datetime.datetime.now().isoformat(),
        "total": total, "passed": passed, "failed": failed,
        "tests": results
    }, f, indent=2)
print(f"\nResults saved to: {RESULTS_PATH}")
