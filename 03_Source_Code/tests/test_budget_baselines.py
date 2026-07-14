"""
BUDGET-BASELINE-01..04 — regression tests for the Budget Baseline Register
(architected by GBT 2026-07-13 after 3 competing "original ROM" figures for
1355R and 101F circulated with no record of source/date/status).
"""
import os
import requests

API = "http://localhost:8000"
KEY = os.environ.get("HCI_API_KEY", "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6")
HEADERS = {"X-API-Key": KEY}


def test_1355r_has_exactly_one_working_baseline():
    r = requests.get(f"{API}/gateway/project/1355R/budget-baselines", headers=HEADERS, timeout=15)
    assert r.status_code == 200
    payload = r.json()["payload"]
    working = [b for b in payload["baselines"] if b["status"] == "working"]
    assert len(working) == 1, "1355R must have exactly one unambiguous working baseline"
    assert payload["warning"] is None


def test_101f_has_exactly_one_working_baseline():
    r = requests.get(f"{API}/gateway/project/101F/budget-baselines", headers=HEADERS, timeout=15)
    assert r.status_code == 200
    payload = r.json()["payload"]
    working = [b for b in payload["baselines"] if b["status"] == "working"]
    assert len(working) == 1
    assert payload["working_baseline"]["total"] == 5732588.0


def test_historical_figures_preserved_not_deleted():
    r = requests.get(f"{API}/gateway/project/1355R/budget-baselines", headers=HEADERS, timeout=15)
    payload = r.json()["payload"]
    totals = {b["total"] for b in payload["baselines"]}
    assert 3541000.0 in totals, "earlier working number must stay on record, not be overwritten"
    assert 4842136.0 in totals, "BC's uncited figure must stay on record for audit trail"


def test_working_baseline_null_when_ambiguous():
    r = requests.get(f"{API}/gateway/project/101F/budget-baselines", headers=HEADERS, timeout=15)
    payload = r.json()["payload"]
    working_count = sum(1 for b in payload["baselines"] if b["status"] == "working")
    if working_count != 1:
        assert payload["working_baseline"] is None
        assert payload["warning"] is not None
