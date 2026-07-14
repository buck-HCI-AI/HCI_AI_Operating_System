"""
AGENT-SYNC-01..03 — regression tests for the checkpoint-based state
recovery endpoint (Phase 1 of the AI Team OS stabilization roadmap,
GBT's own architecture: "what changed since checkpoint X" instead of
"give me unread messages").
"""
import os
import requests

API = "http://localhost:8000"
KEY = os.environ.get("HCI_API_KEY", "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6")
HEADERS = {"X-API-Key": KEY}


def test_sync_returns_ok():
    r = requests.get(f"{API}/gateway/agent/sync?agent=BC", headers=HEADERS, timeout=15)
    assert r.status_code == 200
    assert r.json()["errors"] == []


def test_second_sync_advances_checkpoint():
    r1 = requests.get(f"{API}/gateway/agent/sync?agent=CODE", headers=HEADERS, timeout=15)
    p1 = r1.json()["payload"]
    r2 = requests.get(f"{API}/gateway/agent/sync?agent=CODE", headers=HEADERS, timeout=15)
    p2 = r2.json()["payload"]
    assert p2["is_first_sync"] is False
    assert p2["new_agent_messages_count"] == 0
    assert p2["new_directives_count"] == 0
    assert p2["checkpoint_now"] >= p1["checkpoint_now"]


def test_agent_alias_normalization():
    r = requests.get(f"{API}/gateway/agent/sync?agent=chatgpt", headers=HEADERS, timeout=15)
    assert r.json()["payload"]["agent"] == "GBT"
