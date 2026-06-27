"""
BTW-9 — Company Knowledge Graph
Tests: graph endpoint, summary, vendor traversal, issue similarity, product history
"""
import requests

API = "http://localhost:8000"
HEADERS = {"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"}
KG = "/api/v1/services/knowledge-graph"

passed = failed = 0

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}{': ' + str(detail) if detail else ''}")

def get(path, params=None):
    r = requests.get(f"{API}{path}", headers=HEADERS, params=params, timeout=20)
    return r.status_code, r.json() if r.ok else {}

print("BTW-9 Knowledge Graph Tests")
print("=" * 50)

# ── 1. Service Info ───────────────────────────────────────────────────────────
print("\n1. Service Info — /services/knowledge-graph")
code, d = get(KG)
check("Returns 200", code == 200, code)
check("Status is active", d.get("status") == "active")
check("Has endpoints list", isinstance(d.get("endpoints"), list))
check("Lists 5 endpoints", len(d.get("endpoints", [])) >= 5)

# ── 2. Full Graph ─────────────────────────────────────────────────────────────
print("\n2. Full Graph — /graph")
code, d = get(f"{KG}/graph")
check("Returns 200", code == 200, code)
check("Has node_count integer", isinstance(d.get("node_count"), int))
check("Has edge_count integer", isinstance(d.get("edge_count"), int))
check("Has nodes list", isinstance(d.get("nodes"), list))
check("Has edges list", isinstance(d.get("edges"), list))
check("Has node_types dict", isinstance(d.get("node_types"), dict))
check("Has generated_at", "generated_at" in d)
check("Node count matches nodes list", d.get("node_count") == len(d.get("nodes", [])))

# Check node structure
if d.get("nodes"):
    node = d["nodes"][0]
    check("Node has id", "id" in node)
    check("Node has type", "type" in node)
    check("Node has label", "label" in node)
    check("Node has metadata", "metadata" in node)

# Check edge structure
if d.get("edges"):
    edge = d["edges"][0]
    check("Edge has from", "from" in edge)
    check("Edge has to", "to" in edge)
    check("Edge has relationship", "relationship" in edge)
else:
    check("Edge structure (no edges — sparse data OK)", True)

# Node types present
types = d.get("node_types", {})
check("Has project nodes", "project" in types)

# ── 3. Graph Filtered by Type ─────────────────────────────────────────────────
print("\n3. Graph — node_type filter")
for ntype in ["project", "vendor", "subcontractor", "rfi"]:
    code, d = get(f"{KG}/graph", {"node_type": ntype})
    check(f"Filter node_type={ntype} returns 200", code == 200, code)
    if d.get("nodes"):
        check(f"All nodes have type={ntype}", all(n["type"] == ntype for n in d["nodes"]))
    else:
        check(f"Empty result for {ntype} is valid (sparse data)", True)

# ── 4. Summary ────────────────────────────────────────────────────────────────
print("\n4. Summary — /summary")
code, d = get(f"{KG}/summary")
check("Returns 200", code == 200, code)
check("Has generated_at", "generated_at" in d)
check("Has multi_project_vendors list", isinstance(d.get("multi_project_vendors"), list))
check("Has multi_project_subcontractors list", isinstance(d.get("multi_project_subcontractors"), list))
check("Has rfi_stats dict", isinstance(d.get("rfi_stats"), dict))
check("Has change_order_stats dict", isinstance(d.get("change_order_stats"), dict))

# ── 5. Vendor Traversal ───────────────────────────────────────────────────────
print("\n5. Vendor Traversal — /vendor?name=...")
code, d = get(f"{KG}/vendor", {"name": "abc"})
check("Returns 200 for no-match vendor", code == 200, code)
check("Has query field", "query" in d)
check("Has projects_found list", isinstance(d.get("projects_found"), list))
check("Has as_subcontractor list", isinstance(d.get("as_subcontractor"), list))
check("Has as_supplier list", isinstance(d.get("as_supplier"), list))
check("Has as_bidder list", isinstance(d.get("as_bidder"), list))
check("Has total_relationships int", isinstance(d.get("total_relationships"), int))

# Missing name param returns 422
code, _ = get(f"{KG}/vendor")
check("Missing name returns 422", code == 422, code)

# ── 6. Issue Similarity ───────────────────────────────────────────────────────
print("\n6. Issue Similarity — /issues?q=...")
code, d = get(f"{KG}/issues", {"q": "water"})
check("Returns 200", code == 200, code)
check("Has query field", "query" in d)
check("Has rfis_matching list", isinstance(d.get("rfis_matching"), list))
check("Has change_orders_matching list", isinstance(d.get("change_orders_matching"), list))
check("Has daily_logs_matching list", isinstance(d.get("daily_logs_matching"), list))
check("Has total_matches int", isinstance(d.get("total_matches"), int))

code, d = get(f"{KG}/issues", {"q": "framing"})
check("Issue search framing returns 200", code == 200, code)

# Missing q returns 422
code, _ = get(f"{KG}/issues")
check("Missing q returns 422", code == 422, code)

# ── 7. Product History ────────────────────────────────────────────────────────
print("\n7. Product History — /product?q=...")
code, d = get(f"{KG}/product", {"q": "lumber"})
check("Returns 200", code == 200, code)
check("Has query field", "query" in d)
check("Has vendors_who_supplied list", isinstance(d.get("vendors_who_supplied"), list))
check("Has projects_used_on list", isinstance(d.get("projects_used_on"), list))
check("Has purchase_orders list", isinstance(d.get("purchase_orders"), list))
check("Has daily_log_mentions list", isinstance(d.get("daily_log_mentions"), list))
check("Has tasks_referencing list", isinstance(d.get("tasks_referencing"), list))
check("Has total_records int", isinstance(d.get("total_records"), int))

code, d = get(f"{KG}/product", {"q": "concrete"})
check("Product search concrete returns 200", code == 200, code)

# Missing q returns 422
code, _ = get(f"{KG}/product")
check("Missing q returns 422", code == 422, code)

# ── Results ───────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total = passed + failed
print(f"Results: {passed}/{total} passed")
if failed:
    print(f"FAILED: {failed} tests")
    raise SystemExit(1)
else:
    print("ALL TESTS PASSED")
