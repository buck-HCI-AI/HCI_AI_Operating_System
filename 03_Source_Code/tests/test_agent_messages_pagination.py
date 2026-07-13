"""
Agent Message Retrieval — Pagination — Test Suite
Per GBT's P0 "Fix ADR-003 Message Retrieval Scalability" report (2026-07-13):
both /gateway/agent/unread and /gateway/agent/messages/unread had no LIMIT
at all - with GBT's real backlog (hundreds of messages some days), the
serialized response exceeded ChatGPT Actions' response-size cap and failed
outright (ResponseTooLargeError) with no partial data. Fixed with real
pagination (default page of 10, newest-first, true total_unread count
returned separately from the page).

Run from: 03_Source_Code/
    python3 tests/test_agent_messages_pagination.py
"""
import sys, os, json, time, urllib.request, urllib.error
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

BASE = "http://localhost:8000"
API_KEY = os.environ["HCI_API_KEY"]
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

results = []


def req(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            status, text = resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        status, text = e.code, e.read().decode()
    try:
        js = json.loads(text)
    except Exception:
        js = {"_raw": text}
    return status, js, len(text.encode())


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


def test_agent_messages_unread_default_page_bounded():
    """A real backlog (GBT has 28+ pending agent_messages) must never return
    more than the default limit in one response - proves the endpoint is no
    longer unbounded, the exact bug GBT reported."""
    s, d, size_bytes = req("GET", "/gateway/agent/messages/unread?agent=GBT")
    p = d.get("payload", {})
    returned, limit = p.get("returned"), p.get("limit")
    ok = s == 200 and returned is not None and limit is not None and returned <= limit
    return ok, f"status={s}, returned={returned}, limit={limit}, response_size={size_bytes} bytes"


def test_agent_messages_unread_total_count_independent_of_page_size():
    """total_unread must reflect the REAL backlog size, not just what's
    returned on this page - a caller must be able to tell how much more
    there is without fetching it all."""
    s, d, _ = req("GET", "/gateway/agent/messages/unread?agent=GBT&limit=1")
    p = d.get("payload", {})
    ok = p.get("returned") == 1 and p.get("total_unread", 0) >= 1
    return ok, f"returned={p.get('returned')}, total_unread={p.get('total_unread')}"


def test_agent_messages_unread_pagination_covers_full_backlog_no_gaps():
    """Paging through offset=0, limit, offset=limit, ... must eventually
    return every pending message exactly once - no message skipped or
    duplicated across pages."""
    s, d, _ = req("GET", "/gateway/agent/messages/unread?agent=GBT&limit=5")
    total = d["payload"]["total_unread"]
    seen_ids = set()
    offset = 0
    for _ in range(50):  # safety cap
        s, d, _ = req("GET", f"/gateway/agent/messages/unread?agent=GBT&limit=5&offset={offset}")
        p = d["payload"]
        for m in p["messages"]:
            seen_ids.add(m["message_id"])
        if not p["has_more"]:
            break
        offset += 5
    return len(seen_ids) == total, f"expected {total} unique messages, collected {len(seen_ids)}"


def test_agent_unread_ai_messages_also_paginated():
    """The older /agent/unread (ai_messages-backed) endpoint had the same
    unbounded-query bug - must also be paginated now."""
    s, d, _ = req("GET", "/gateway/agent/unread?agent=chatgpt")
    p = d.get("payload", {})
    ok = s == 200 and "limit" in p and "total_unread" in p and "has_more" in p
    return ok, f"status={s}, keys_present={list(p.keys())}"


def test_newest_first_ordering_is_default():
    """GBT explicitly asked for newest-first retrieval - verify the default
    ordering actually returns messages in descending timestamp order."""
    s, d, _ = req("GET", "/gateway/agent/messages/unread?agent=GBT&limit=10")
    msgs = d["payload"]["messages"]
    if len(msgs) < 2:
        return True, "fewer than 2 messages, ordering not meaningfully testable"
    timestamps = [m["timestamp_mt"] for m in msgs]
    is_descending = timestamps == sorted(timestamps, reverse=True)
    return is_descending, f"timestamps in order: {is_descending}"


print("\nGroup: AGENT-MSG-PAGE — Agent message retrieval pagination (regression, 2026-07-13)")
test("AGENT-MSG-PAGE-01: default page bounded to limit",              test_agent_messages_unread_default_page_bounded)
test("AGENT-MSG-PAGE-02: total_unread independent of page size",      test_agent_messages_unread_total_count_independent_of_page_size)
test("AGENT-MSG-PAGE-03: paging covers full backlog, no gaps/dupes",  test_agent_messages_unread_pagination_covers_full_backlog_no_gaps)
test("AGENT-MSG-PAGE-04: /agent/unread (ai_messages) also paginated", test_agent_unread_ai_messages_also_paginated)
test("AGENT-MSG-PAGE-05: newest-first is the default ordering",       test_newest_first_ordering_is_default)

failed = [r for r in results if r["status"] != "PASS"]
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
if failed:
    print("FAILURES:")
    for r in failed:
        print(f"  - {r['name']}: {r['detail']}")
    sys.exit(1)
