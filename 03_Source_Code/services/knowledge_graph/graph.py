"""
Knowledge Graph — entity and relationship model.
Builds an in-memory graph from existing DB tables and answers traversal queries.
No new DB tables needed; uses existing: projects, vendors, houzz_subcontractors,
houzz_contacts, hubspot_contacts, rfis, houzz_purchase_orders, houzz_change_orders,
bid_entries, bid_packages.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

from datetime import datetime, timezone


def _pg():
    import psycopg2, psycopg2.extras
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        dbname=os.environ.get("POSTGRES_DB", "hci_os"),
        user=os.environ.get("POSTGRES_USER", "hci_admin"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def _q(sql, params=None):
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]


def _q1(sql, params=None):
    rows = _q(sql, params)
    return rows[0] if rows else {}


# ── Entity Loaders ────────────────────────────────────────────────────────────

def load_projects() -> list[dict]:
    return _q("""
        SELECT id, name, address, pm_name, super_name, status
        FROM projects ORDER BY id
    """)


def load_vendors() -> list[dict]:
    return _q("""
        SELECT id, company_name AS name, trade, email, city
        FROM vendors ORDER BY company_name
    """)


def load_subcontractors() -> list[dict]:
    return _q("""
        SELECT hs.houzz_sub_id, hs.company_name, hs.trade, hs.status,
               hs.houzz_project_id, hp.name AS project_name,
               hs.insurance_expiry
        FROM houzz_subcontractors hs
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = hs.houzz_project_id
        ORDER BY hs.company_name
    """)


def load_contacts() -> list[dict]:
    rows = _q("""
        SELECT hc.id, hc.first_name || ' ' || COALESCE(hc.last_name, '') AS full_name,
               hc.email, hc.company, hc.job_title AS role
        FROM hubspot_contacts hc
        ORDER BY hc.first_name
    """)
    return rows


def load_purchase_orders() -> list[dict]:
    return _q("""
        SELECT po.houzz_po_id, po.vendor_name, po.description, po.status,
               po.po_amount, po.houzz_project_id, hp.name AS project_name
        FROM houzz_purchase_orders po
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = po.houzz_project_id
        ORDER BY po.vendor_name
    """)


def load_rfis() -> list[dict]:
    return _q("""
        SELECT r.id, r.rfi_number, r.subject, r.status,
               r.submitted_by, r.project_id, p.name AS project_name
        FROM rfis r
        LEFT JOIN projects p ON p.id = r.project_id
        ORDER BY r.submitted_date DESC
    """)


def load_change_orders() -> list[dict]:
    return _q("""
        SELECT co.houzz_co_id, co.co_number, co.title, co.status,
               co.amount, co.houzz_project_id, hp.name AS project_name,
               co.submitted_date, co.approved_date
        FROM houzz_change_orders co
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = co.houzz_project_id
        ORDER BY co.submitted_date DESC NULLS LAST
    """)


def load_bids() -> list[dict]:
    return _q("""
        SELECT be.id, be.bid_amount, be.status,
               v.company_name AS vendor_name, bp.package_name AS scope_name,
               bp.project_id, p.name AS project_name
        FROM bid_entries be
        LEFT JOIN vendors v ON v.id = be.vendor_id
        LEFT JOIN bid_packages bp ON bp.id = be.bid_package_id
        LEFT JOIN projects p ON p.id = bp.project_id
        ORDER BY be.created_at DESC
    """)


# ── Graph Builder ─────────────────────────────────────────────────────────────

def build_graph() -> dict:
    """
    Return a snapshot of the knowledge graph with nodes and edges.
    Nodes: project, vendor, subcontractor, contact, rfi, change_order, purchase_order, bid
    Edges: worked_on, supplied_to, submitted_rfi_on, raised_co_on, bid_on
    """
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    def _add(node_id: str, node_type: str, label: str, metadata: dict = None):
        nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "metadata": metadata or {},
        }

    # Projects
    for p in load_projects():
        _add(f"proj:{p['id']}", "project", p.get("name", ""), {"address": p.get("address")})

    # Vendors
    for v in load_vendors():
        _add(f"vendor:{v['id']}", "vendor", v.get("name", ""), {"trade": v.get("trade_category")})

    # Subcontractors → worked_on projects
    for s in load_subcontractors():
        nid = f"sub:{s['houzz_sub_id']}"
        _add(nid, "subcontractor", s.get("company_name", ""), {"trade": s.get("trade"), "status": s.get("status")})
        if s.get("project_name"):
            proj_node = next((k for k, v in nodes.items() if v["label"] == s["project_name"] and v["type"] == "project"), None)
            if proj_node:
                edges.append({"from": nid, "to": proj_node, "relationship": "worked_on", "metadata": {"trade": s.get("trade")}})

    # Contacts
    for c in load_contacts():
        _add(f"contact:{c['id']}", "contact", (c.get("full_name") or "").strip(), {"company": c.get("company"), "role": c.get("role")})

    # Purchase orders → vendor supplied_to project
    for po in load_purchase_orders():
        nid = f"po:{po['houzz_po_id']}"
        _add(nid, "purchase_order", po.get("description") or po.get("vendor_name", ""), {
            "vendor_name": po.get("vendor_name"),
            "status": po.get("status"),
            "amount": float(po.get("po_amount") or 0),
        })
        if po.get("project_name"):
            proj_node = next((k for k, v in nodes.items() if v["label"] == po["project_name"] and v["type"] == "project"), None)
            if proj_node:
                edges.append({"from": nid, "to": proj_node, "relationship": "supplied_to",
                              "metadata": {"vendor": po.get("vendor_name")}})

    # RFIs → submitted_rfi_on project
    for r in load_rfis():
        nid = f"rfi:{r['id']}"
        _add(nid, "rfi", r.get("subject") or r.get("rfi_number", ""), {
            "status": r.get("status"),
            "submitted_by": r.get("submitted_by"),
        })
        if r.get("project_id"):
            proj_node = f"proj:{r['project_id']}"
            if proj_node in nodes:
                edges.append({"from": nid, "to": proj_node, "relationship": "submitted_on", "metadata": {}})

    # Change orders → raised_co_on project
    for co in load_change_orders():
        nid = f"co:{co['houzz_co_id']}"
        _add(nid, "change_order", co.get("title") or co.get("co_number", ""), {
            "status": co.get("status"),
            "amount": float(co.get("amount") or 0),
        })
        if co.get("project_name"):
            proj_node = next((k for k, v in nodes.items() if v["label"] == co["project_name"] and v["type"] == "project"), None)
            if proj_node:
                edges.append({"from": nid, "to": proj_node, "relationship": "raised_on", "metadata": {"amount": float(co.get("amount") or 0)}})

    # Bids → vendor bid_on project
    for b in load_bids():
        nid = f"bid:{b['id']}"
        _add(nid, "bid", b.get("scope_name", ""), {
            "vendor_name": b.get("vendor_name"),
            "amount": float(b.get("bid_amount") or 0),
            "status": b.get("status"),
        })
        if b.get("project_id"):
            proj_node = f"proj:{b['project_id']}"
            if proj_node in nodes:
                edges.append({"from": nid, "to": proj_node, "relationship": "bid_on",
                              "metadata": {"vendor": b.get("vendor_name")}})

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "node_types": _count_types(nodes),
        "nodes": list(nodes.values()),
        "edges": edges,
    }


def _count_types(nodes: dict) -> dict:
    counts: dict = {}
    for n in nodes.values():
        t = n["type"]
        counts[t] = counts.get(t, 0) + 1
    return counts


# ── Traversal Queries ─────────────────────────────────────────────────────────

def find_by_vendor(vendor_name: str) -> dict:
    """Find all projects a vendor worked on (via subs, POs, bids)."""
    like = f"%{vendor_name}%"
    subs = _q("""
        SELECT hs.company_name, hs.trade, hs.status, hp.name AS project_name
        FROM houzz_subcontractors hs
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = hs.houzz_project_id
        WHERE hs.company_name ILIKE %s
    """, (like,))

    pos = _q("""
        SELECT po.vendor_name, po.description, po.status, po.po_amount, hp.name AS project_name
        FROM houzz_purchase_orders po
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = po.houzz_project_id
        WHERE po.vendor_name ILIKE %s
    """, (like,))

    bids = _q("""
        SELECT v.company_name AS vendor_name, bp.package_name AS scope_name, be.bid_amount,
               be.status, p.name AS project_name
        FROM bid_entries be
        JOIN vendors v ON v.id = be.vendor_id
        JOIN bid_packages bp ON bp.id = be.bid_package_id
        LEFT JOIN projects p ON p.id = bp.project_id
        WHERE v.company_name ILIKE %s
    """, (like,))

    projects = list({r["project_name"] for r in subs + pos + bids if r.get("project_name")})

    return {
        "query": f"vendor:{vendor_name}",
        "projects_found": projects,
        "as_subcontractor": subs,
        "as_supplier": pos,
        "as_bidder": bids,
        "total_relationships": len(subs) + len(pos) + len(bids),
    }


def find_similar_issues(issue_keywords: str) -> dict:
    """Find similar RFIs and change orders matching keywords."""
    like = f"%{issue_keywords}%"

    matching_rfis = _q("""
        SELECT r.rfi_number, r.subject, r.status, r.submitted_by,
               p.name AS project_name, r.submitted_date
        FROM rfis r
        LEFT JOIN projects p ON p.id = r.project_id
        WHERE r.subject ILIKE %s OR r.question ILIKE %s
        ORDER BY r.submitted_date DESC
        LIMIT 10
    """, (like, like))

    matching_cos = _q("""
        SELECT co.co_number, co.title, co.status, co.amount,
               hp.name AS project_name, co.submitted_date
        FROM houzz_change_orders co
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = co.houzz_project_id
        WHERE co.title ILIKE %s OR co.description ILIKE %s OR co.reason ILIKE %s
        ORDER BY co.submitted_date DESC
        LIMIT 10
    """, (like, like, like))

    matching_logs = _q("""
        SELECT dl.content, dl.log_date, dl.author, hp.name AS project_name
        FROM houzz_daily_logs dl
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = dl.project_id
        WHERE dl.content ILIKE %s
        ORDER BY dl.log_date DESC
        LIMIT 5
    """, (like,))

    return {
        "query": issue_keywords,
        "rfis_matching": matching_rfis,
        "change_orders_matching": matching_cos,
        "daily_logs_matching": matching_logs,
        "total_matches": len(matching_rfis) + len(matching_cos) + len(matching_logs),
    }


def find_product_history(product_keyword: str) -> dict:
    """Find who installed or ordered a product, and on which projects."""
    like = f"%{product_keyword}%"

    pos = _q("""
        SELECT po.vendor_name, po.description, po.status, po.po_amount,
               hp.name AS project_name, po.issued_date
        FROM houzz_purchase_orders po
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = po.houzz_project_id
        WHERE po.description ILIKE %s
        ORDER BY po.issued_date DESC NULLS LAST
    """, (like,))

    logs = _q("""
        SELECT dl.content, dl.log_date, dl.author, hp.name AS project_name
        FROM houzz_daily_logs dl
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = dl.project_id
        WHERE dl.content ILIKE %s
        ORDER BY dl.log_date DESC
        LIMIT 5
    """, (like,))

    tasks = _q("""
        SELECT ht.title, ht.status, ht.assigned_to, hp.name AS project_name
        FROM houzz_tasks ht
        LEFT JOIN houzz_projects hp ON hp.houzz_project_id = ht.houzz_project_id
        WHERE ht.title ILIKE %s OR ht.description ILIKE %s
        ORDER BY ht.due_date NULLS LAST
        LIMIT 10
    """, (like, like))

    vendors = list({r["vendor_name"] for r in pos if r.get("vendor_name")})
    projects = list({r["project_name"] for r in pos + logs + tasks if r.get("project_name")})

    return {
        "query": product_keyword,
        "vendors_who_supplied": vendors,
        "projects_used_on": projects,
        "purchase_orders": pos,
        "daily_log_mentions": logs,
        "tasks_referencing": tasks,
        "total_records": len(pos) + len(logs) + len(tasks),
    }


def cross_project_summary() -> dict:
    """Cross-project relationship summary for the knowledge graph overview."""
    vendor_counts = _q("""
        SELECT vendor_name, COUNT(DISTINCT houzz_project_id) AS project_count
        FROM houzz_purchase_orders
        WHERE vendor_name IS NOT NULL
        GROUP BY vendor_name
        HAVING COUNT(DISTINCT houzz_project_id) > 1
        ORDER BY project_count DESC
        LIMIT 10
    """)

    sub_counts = _q("""
        SELECT company_name, trade, COUNT(DISTINCT houzz_project_id) AS project_count
        FROM houzz_subcontractors
        WHERE company_name IS NOT NULL
        GROUP BY company_name, trade
        HAVING COUNT(DISTINCT houzz_project_id) > 1
        ORDER BY project_count DESC
        LIMIT 10
    """)

    rfi_stats = _q1("""
        SELECT COUNT(*) AS total, SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) AS open
        FROM rfis
    """)

    co_stats = _q1("""
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN approved_date IS NULL THEN 1 ELSE 0 END) AS pending
        FROM houzz_change_orders
    """)

    return {
        "multi_project_vendors": vendor_counts,
        "multi_project_subcontractors": sub_counts,
        "rfi_stats": rfi_stats,
        "change_order_stats": co_stats,
    }
