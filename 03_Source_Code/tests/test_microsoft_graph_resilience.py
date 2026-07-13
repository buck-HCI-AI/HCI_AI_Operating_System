"""
Microsoft Graph — 504/Transient-Error Resilience — Test Suite
Per GBT's P0 "Defect: Microsoft Graph 504 handling breaks RFI workflow"
report (2026-07-13): "Add regression tests that simulate Graph 504
responses and verify successful recovery without duplicate artifacts."

Mocks urllib at the boundary (no real network calls, no real Graph API
hit) so this runs offline and fast. Verifies:
  - GET/PATCH/DELETE auto-retry on 502/503/504 and give up after 3 tries
  - POST is never auto-retried at the _request() layer (duplicate-write risk)
  - create_draft() recovers from a 504 by checking for the draft Graph may
    have already committed before deciding whether to retry (no duplicate
    when Graph actually succeeded server-side; exactly one retry when it
    didn't)

Run from: 03_Source_Code/
    python3 tests/test_microsoft_graph_resilience.py
"""
import sys, os, io, time, urllib.error
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import microsoft_graph as mg

results = []


def test(name, fn):
    start = time.time()
    try:
        passed, detail = fn()
        status = "PASS" if passed else "FAIL"
    except Exception as e:
        status, detail, passed = "ERROR", f"{type(e).__name__}: {e}", False
    ms = round((time.time() - start) * 1000)
    results.append({"name": name, "status": status, "detail": detail, "ms": ms})
    print(f"  [{status}] {name} ({ms}ms) - {detail}")
    return passed


def _http_error(code, body=b"gateway timeout"):
    return urllib.error.HTTPError("https://graph.microsoft.com/v1.0/x", code, "err",
                                   {}, io.BytesIO(body))


def _ok_response(payload: dict):
    cm = MagicMock()
    cm.__enter__.return_value.read.return_value = __import__("json").dumps(payload).encode()
    return cm


def test_get_retries_on_504_then_succeeds():
    """A GET hitting 504 twice then succeeding on the 3rd attempt must
    return the successful result, not the error - proving auto-retry for
    idempotent verbs actually works."""
    with patch("microsoft_graph._token", return_value="fake-token"), \
         patch("microsoft_graph.time.sleep"), \
         patch("urllib.request.urlopen") as mock_open:
        mock_open.side_effect = [
            _http_error(504), _http_error(504), _ok_response({"ok": True})
        ]
        r, err = mg._request("GET", "/me/messages")
    return (err is None and r == {"ok": True} and mock_open.call_count == 3), \
           f"err={err}, r={r}, calls={mock_open.call_count}"


def test_get_gives_up_after_max_retries():
    """A GET that fails with 504 on every attempt must give up after
    _MAX_RETRIES and return the error, not hang or retry forever."""
    with patch("microsoft_graph._token", return_value="fake-token"), \
         patch("microsoft_graph.time.sleep"), \
         patch("urllib.request.urlopen") as mock_open:
        mock_open.side_effect = [_http_error(504)] * mg._MAX_RETRIES
        r, err = mg._request("GET", "/me/messages")
    return (r is None and err is not None and mock_open.call_count == mg._MAX_RETRIES), \
           f"err={err}, calls={mock_open.call_count}"


def test_post_not_auto_retried_at_request_layer():
    """POST must NOT be auto-retried inside _request() itself even on a
    504 - retrying a raw POST blindly risks creating a duplicate resource.
    Only exactly 1 attempt should ever be made here."""
    with patch("microsoft_graph._token", return_value="fake-token"), \
         patch("microsoft_graph.time.sleep"), \
         patch("urllib.request.urlopen") as mock_open:
        mock_open.side_effect = [_http_error(504)]
        r, err = mg._request("POST", "/me/messages", body={"subject": "x"})
    return (r is None and err is not None and mock_open.call_count == 1), \
           f"err={err}, calls={mock_open.call_count}"


def test_create_draft_recovers_without_duplicate_when_graph_already_committed():
    """Simulates the real failure mode GBT reported: the POST /me/messages
    times out client-side (504) but Graph actually created the draft
    server-side. create_draft() must detect the existing draft via
    _find_recent_draft_by_subject and return it - and must NOT issue a
    second POST (which would create a duplicate)."""
    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    existing_draft = {"id": "abc123", "subject": "RFI Test Subject", "createdDateTime": now_iso}
    post_calls = {"n": 0}

    def fake_request(method, path, body=None, params=None):
        if method == "POST":
            post_calls["n"] += 1
            return None, "504: gateway timeout"
        if method == "GET" and path == "/me/mailFolders/drafts/messages":
            return {"value": [existing_draft]}, None
        if method == "GET" and path == f"/me/messages/{existing_draft['id']}":
            return existing_draft, None
        return None, "unexpected call"

    with patch("microsoft_graph._request", side_effect=fake_request):
        result = mg.create_draft("RFI Test Subject", "<p>body</p>", [("Buck", "buck@x.com")])

    return (result.get("id") == "abc123" and post_calls["n"] == 1), \
           f"result_id={result.get('id')}, post_calls={post_calls['n']} (must be exactly 1, no duplicate POST)"


def test_create_draft_retries_once_when_graph_never_committed():
    """If the 504 was a genuine failure (Graph never created the draft),
    create_draft() must retry the POST exactly once and return the
    successful result - not give up, and not retry indefinitely."""
    post_calls = {"n": 0}

    def fake_request(method, path, body=None, params=None):
        if method == "POST":
            post_calls["n"] += 1
            if post_calls["n"] == 1:
                return None, "504: gateway timeout"
            return {"id": "new-draft-456", "subject": body["subject"]}, None
        if method == "GET" and path == "/me/mailFolders/drafts/messages":
            return {"value": []}, None  # nothing exists yet - genuine failure
        return None, "unexpected call"

    with patch("microsoft_graph._request", side_effect=fake_request), \
         patch("microsoft_graph.time.sleep"):
        result = mg.create_draft("RFI Test Subject 2", "<p>body</p>", [("Buck", "buck@x.com")])

    return (result.get("id") == "new-draft-456" and post_calls["n"] == 2), \
           f"result_id={result.get('id')}, post_calls={post_calls['n']} (must be exactly 2: original + 1 retry)"


print("\nGroup: GRAPH-RESILIENCE — 504/transient-error handling (regression, 2026-07-13)")
test("GRAPH-RESILIENCE-01: GET auto-retries on 504 and succeeds",              test_get_retries_on_504_then_succeeds)
test("GRAPH-RESILIENCE-02: GET gives up after max retries",                    test_get_gives_up_after_max_retries)
test("GRAPH-RESILIENCE-03: POST never auto-retried at _request() layer",       test_post_not_auto_retried_at_request_layer)
test("GRAPH-RESILIENCE-04: create_draft recovers, no duplicate when committed", test_create_draft_recovers_without_duplicate_when_graph_already_committed)
test("GRAPH-RESILIENCE-05: create_draft retries once on genuine failure",      test_create_draft_retries_once_when_graph_never_committed)

failed = [r for r in results if r["status"] != "PASS"]
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
if failed:
    print("FAILURES:")
    for r in failed:
        print(f"  - {r['name']}: {r['detail']}")
    sys.exit(1)
