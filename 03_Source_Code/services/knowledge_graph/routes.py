"""
Knowledge Graph Service API routes.
Mounted at /api/v1/services/knowledge-graph
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

from fastapi import APIRouter, HTTPException, Query
from graph import (
    build_graph, find_by_vendor, find_similar_issues,
    find_product_history, cross_project_summary,
)

router = APIRouter()


@router.get("")
def service_info():
    return {
        "service": "knowledge-graph",
        "version": "1.0.0",
        "status": "active",
        "description": "Company Knowledge Graph — entity nodes, relationship edges, semantic traversal",
        "endpoints": [
            "GET /graph        — Full graph snapshot (nodes + edges)",
            "GET /summary      — Cross-project relationship summary",
            "GET /vendor       — All projects a vendor worked on (?name=...)",
            "GET /issues       — Similar RFIs + COs matching keywords (?q=...)",
            "GET /product      — Product history across projects (?q=...)",
        ],
    }


@router.get("/graph")
def get_graph(node_type: str = Query(None, description="Filter nodes by type: project|vendor|subcontractor|contact|rfi|change_order|purchase_order|bid")):
    """Full knowledge graph — all entity nodes and relationship edges."""
    g = build_graph()
    if node_type:
        g["nodes"] = [n for n in g["nodes"] if n["type"] == node_type]
        relevant_ids = {n["id"] for n in g["nodes"]}
        g["edges"] = [e for e in g["edges"] if e["from"] in relevant_ids or e["to"] in relevant_ids]
    return g


@router.get("/summary")
def get_summary():
    """Cross-project relationship summary — vendors and subs on multiple projects, RFI/CO stats."""
    return {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        **cross_project_summary(),
    }


@router.get("/vendor")
def query_vendor(name: str = Query(..., description="Vendor or subcontractor name to look up")):
    """Find all projects a vendor was involved in (as sub, PO supplier, or bidder)."""
    if not name.strip():
        raise HTTPException(400, "name parameter is required")
    return find_by_vendor(name.strip())


@router.get("/issues")
def query_issues(q: str = Query(..., description="Keywords to match across RFIs, change orders, daily logs")):
    """Find similar issues (RFIs, COs, daily log entries) matching keywords — cross-project."""
    if not q.strip():
        raise HTTPException(400, "q parameter is required")
    return find_similar_issues(q.strip())


@router.get("/product")
def query_product(q: str = Query(..., description="Product or material name to trace across projects")):
    """Find who installed or ordered a product and on which projects."""
    if not q.strip():
        raise HTTPException(400, "q parameter is required")
    return find_product_history(q.strip())
