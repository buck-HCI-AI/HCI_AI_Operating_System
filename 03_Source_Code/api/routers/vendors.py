"""Vendor endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Optional
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import pg

router = APIRouter()

@router.get("/")
def list_vendors(csi: Optional[str] = None, search: Optional[str] = None, limit: int = 50, offset: int = 0):
    """List vendors. Filter by CSI division or name search."""
    with pg() as conn:
        cur = conn.cursor()
        where, params = [], []

        if csi:
            where.append("%s = ANY(csi_divisions)")
            params.append(csi)
        if search:
            where.append("(company_name ILIKE %s OR contact_name ILIKE %s)")
            params += [f"%{search}%", f"%{search}%"]

        sql = "SELECT * FROM vendors"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY company_name LIMIT %s OFFSET %s"
        params += [limit, offset]

        cur.execute(sql, params)
        return cur.fetchall()

@router.get("/{vendor_id}")
def get_vendor(vendor_id: int):
    with pg() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM vendors WHERE id = %s", (vendor_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, f"Vendor {vendor_id} not found")
        return row

@router.get("/{vendor_id}/bids")
def vendor_bids(vendor_id: int):
    """All bids linked to a vendor (via notes field — vendor_id FK is nullable)."""
    with pg() as conn:
        cur = conn.cursor()
        cur.execute("SELECT company_name FROM vendors WHERE id = %s", (vendor_id,))
        v = cur.fetchone()
        if not v:
            raise HTTPException(404, f"Vendor {vendor_id} not found")
        name = v["company_name"]

        cur.execute("""
            SELECT be.id, be.bid_amount, be.date_received, be.status, be.notes,
                   bp.package_name, bp.csi_division,
                   p.name as project_name
            FROM bid_entries be
            JOIN bid_packages bp ON bp.id = be.bid_package_id
            JOIN projects p ON p.id = be.project_id
            WHERE be.vendor_id = %s OR be.notes ILIKE %s
            ORDER BY be.date_received DESC
        """, (vendor_id, f"%{name}%"))
        return cur.fetchall()
