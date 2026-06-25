"""Bid endpoints — packages and entries."""
from fastapi import APIRouter, HTTPException
from typing import Optional
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import pg

router = APIRouter()

@router.get("/")
def list_bids(project_id: Optional[int] = None, csi: Optional[str] = None, status: Optional[str] = None):
    """List all bid entries with package + project context."""
    with pg() as conn:
        cur = conn.cursor()
        where, params = [], []

        if project_id:
            where.append("be.project_id = %s")
            params.append(project_id)
        if csi:
            where.append("bp.csi_division ILIKE %s")
            params.append(f"%{csi}%")
        if status:
            where.append("be.status = %s")
            params.append(status)

        sql = """
            SELECT be.id, be.bid_amount, be.date_received, be.status, be.notes,
                   bp.package_name, bp.csi_division,
                   p.name as project_name, p.address
            FROM bid_entries be
            JOIN bid_packages bp ON bp.id = be.bid_package_id
            JOIN projects p ON p.id = be.project_id
        """
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY p.name, bp.package_name, be.bid_amount"

        cur.execute(sql, params)
        return cur.fetchall()

@router.get("/leveling/{package_id}")
def bid_leveling(package_id: int):
    """Bid leveling sheet for a specific package — all bids ranked low to high."""
    with pg() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT bp.package_name, bp.csi_division, p.name as project_name,
                   bp.budget_estimate, bp.status as pkg_status
            FROM bid_packages bp
            JOIN projects p ON p.id = bp.project_id
            WHERE bp.id = %s
        """, (package_id,))
        pkg = cur.fetchone()
        if not pkg:
            raise HTTPException(404, f"Package {package_id} not found")

        cur.execute("""
            SELECT id, bid_amount, date_received, status, notes
            FROM bid_entries
            WHERE bid_package_id = %s AND bid_amount IS NOT NULL
            ORDER BY bid_amount ASC
        """, (package_id,))
        entries = cur.fetchall()

        if entries:
            amounts = [float(e["bid_amount"]) for e in entries]
            low  = min(amounts)
            high = max(amounts)
            avg  = sum(amounts) / len(amounts)
            spread_pct = round((high - low) / low * 100, 1) if low else 0
        else:
            low = high = avg = spread_pct = 0

        return {
            "package":     dict(pkg),
            "bids":        [dict(e) for e in entries],
            "stats": {
                "count":      len(entries),
                "low":        round(low, 2),
                "high":       round(high, 2),
                "avg":        round(avg, 2),
                "spread_pct": spread_pct,
            }
        }

@router.get("/packages/")
def list_packages(project_id: Optional[int] = None):
    """List bid packages."""
    with pg() as conn:
        cur = conn.cursor()
        if project_id:
            cur.execute("""
                SELECT bp.*, p.name as project_name,
                       COUNT(be.id) as bid_count,
                       MIN(be.bid_amount) as low_bid
                FROM bid_packages bp
                JOIN projects p ON p.id = bp.project_id
                LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
                WHERE bp.project_id = %s
                GROUP BY bp.id, p.name
                ORDER BY bp.package_name
            """, (project_id,))
        else:
            cur.execute("""
                SELECT bp.*, p.name as project_name,
                       COUNT(be.id) as bid_count,
                       MIN(be.bid_amount) as low_bid
                FROM bid_packages bp
                JOIN projects p ON p.id = bp.project_id
                LEFT JOIN bid_entries be ON be.bid_package_id = bp.id
                GROUP BY bp.id, p.name
                ORDER BY p.name, bp.package_name
            """)
        return cur.fetchall()
