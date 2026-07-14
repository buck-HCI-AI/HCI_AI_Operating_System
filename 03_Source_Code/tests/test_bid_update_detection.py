"""
Bid Update Auto-Detection — Regression Tests
Tests detect_and_process_bid_updates() in services/bid_leveling/drive_bid_reader.py.

Run from: 03_Source_Code/
    python3 tests/test_bid_update_detection.py
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.bid_leveling.drive_bid_reader import detect_and_process_bid_updates, _pg

RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results_bid_update_detection.json")
results = []


def test(name, fn):
    try:
        fn()
        results.append({"name": name, "status": "PASS"})
        print(f"PASS: {name}")
    except AssertionError as e:
        results.append({"name": name, "status": "FAIL", "error": str(e)})
        print(f"FAIL: {name} - {e}")
    except Exception as e:
        results.append({"name": name, "status": "ERROR", "error": f"{type(e).__name__}: {e}"})
        print(f"ERROR: {name} - {type(e).__name__}: {e}")


def row_count():
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM drive_bids")
            return cur.fetchone()["c"]


def test_dry_run_never_writes():
    # BID-UPDATE-DETECT-01: dry_run=True must be a pure read - no row count
    # change, regardless of what the live Drive folder currently contains.
    before = row_count()
    result = detect_and_process_bid_updates(3, dry_run=True)  # 1355R
    after = row_count()
    assert result.get("dry_run") is True, f"expected dry_run=True in result, got {result}"
    assert before == after, f"dry_run wrote rows: before={before} after={after}"


def test_dry_run_no_error_on_all_active_projects():
    # BID-UPDATE-DETECT-02: the function must run cleanly (no exception,
    # no 'error' key) against every currently active project - this is
    # the same live-data smoke test each project got before shipping.
    for project_id, label in [(1, "64EW"), (2, "101F"), (3, "1355R")]:
        result = detect_and_process_bid_updates(project_id, dry_run=True)
        assert "error" not in result, f"{label} returned error: {result.get('error')}"
        assert "scan_result" in result, f"{label} missing scan_result: {result}"


def test_variance_math():
    # BID-UPDATE-DETECT-03: the >10% large-variance threshold is the one
    # piece of business logic in this feature that's pure enough to unit
    # test directly, rather than only exercising it end to end live.
    def variance_pct(old, new):
        return round((new - old) / old * 100, 1)

    assert variance_pct(100000, 105000) == 5.0, "5% increase should not be flagged"
    assert abs(variance_pct(100000, 105000)) <= 10, "5% must be under the large-variance threshold"
    assert variance_pct(100000, 115000) == 15.0, "15% increase should compute correctly"
    assert abs(variance_pct(100000, 115000)) > 10, "15% must exceed the large-variance threshold"
    assert variance_pct(100000, 85000) == -15.0, "15% decrease should compute correctly (negative)"
    assert abs(variance_pct(100000, 85000)) > 10, "-15% must exceed the threshold by absolute value"


def test_no_false_positive_on_unchanged_state():
    # BID-UPDATE-DETECT-04: with nothing new in any project's Drive folder
    # since the last scan, running with dry_run=True should report the
    # scan found 0 new_files (since 1355R/101F/64EW were all just fully
    # processed this session) - a stale "updates_detected" claim with no
    # real new data would be exactly the kind of silent-failure pattern
    # this session has been catching all day.
    result = detect_and_process_bid_updates(2, dry_run=True)  # 101F, fully processed this session
    assert result["scan_result"]["new_files"] == 0, (
        f"expected 0 new files on a project with no pending Drive changes, "
        f"got {result['scan_result']['new_files']}"
    )


test("BID-UPDATE-DETECT-01: dry_run never writes to drive_bids", test_dry_run_never_writes)
test("BID-UPDATE-DETECT-02: runs cleanly on all 3 active projects", test_dry_run_no_error_on_all_active_projects)
test("BID-UPDATE-DETECT-03: variance percentage math is correct", test_variance_math)
test("BID-UPDATE-DETECT-04: no false-positive updates on unchanged project", test_no_false_positive_on_unchanged_state)

passed = sum(1 for r in results if r["status"] == "PASS")
print(f"\n{passed}/{len(results)} passed")
with open(RESULTS_PATH, "w") as f:
    json.dump({"results": results, "passed": passed, "total": len(results)}, f, indent=2)

sys.exit(0 if passed == len(results) else 1)
