"""Project endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Optional
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import pg

router = APIRouter()

@router.get("/")
def list_projects(status: Optional[str] = None):
    with pg() as conn:
        cur = conn.cursor()
        if status:
            cur.execute("SELECT * FROM projects WHERE status = %s ORDER BY name", (status,))
        else:
            cur.execute("SELECT * FROM projects ORDER BY name")
        return cur.fetchall()

@router.get("/{project_id}")
def get_project(project_id: int):
    with pg() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, f"Project {project_id} not found")
        return row

@router.get("/{project_id}/bids")
def project_bids(project_id: int):
    """All bid packages + entries for a project, grouped by package."""
    with pg() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT bp.id as package_id, bp.package_name, bp.csi_division, bp.status as pkg_status,
                   be.id as bid_id, be.bid_amount, be.date_received, be.status as bid_status, be.notes
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
            WHERE bp.project_id = %s
            ORDER BY bp.package_name, be.bid_amount
        """, (project_id,))
        rows = cur.fetchall()

        # Group by package
        packages = {}
        for r in rows:
            pid = r["package_id"]
            if pid not in packages:
                packages[pid] = {
                    "package_id":   pid,
                    "package_name": r["package_name"],
                    "csi_division": r["csi_division"],
                    "status":       r["pkg_status"],
                    "bids":         [],
                }
            if r["bid_id"]:
                packages[pid]["bids"].append({
                    "bid_id":       r["bid_id"],
                    "amount":       float(r["bid_amount"]) if r["bid_amount"] else None,
                    "date_received":str(r["date_received"]) if r["date_received"] else None,
                    "status":       r["bid_status"],
                    "notes":        r["notes"],
                })
        return list(packages.values())

@router.get("/{project_id}/summary")
def project_summary(project_id: int):
    """Budget summary: total bids received, low/high/avg per package."""
    with pg() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        project = cur.fetchone()
        if not project:
            raise HTTPException(404, f"Project {project_id} not found")

        cur.execute("""
            SELECT bp.package_name, bp.csi_division,
                   COUNT(be.id) as bid_count,
                   MIN(be.bid_amount) as low_bid,
                   MAX(be.bid_amount) as high_bid,
                   AVG(be.bid_amount) as avg_bid
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id AND be.bid_amount IS NOT NULL
            WHERE bp.project_id = %s
            GROUP BY bp.id, bp.package_name, bp.csi_division
            ORDER BY bp.package_name
        """, (project_id,))
        packages = cur.fetchall()

        total_low = sum(float(p["low_bid"]) for p in packages if p["low_bid"])
        return {
            "project":        dict(project),
            "packages":       [dict(p) for p in packages],
            "total_low_bid":  round(total_low, 2),
            "package_count":  len(packages),
        }
