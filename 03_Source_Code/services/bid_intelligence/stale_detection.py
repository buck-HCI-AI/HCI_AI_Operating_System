"""
BTW-4 — Bid Stale Detection Service.

Three alert classes:
  EXPIRING  — bid_expiry_date within 3 days
  EXPIRED   — bid_expiry_date in the past, bid not yet received/awarded
  NO_RESPONSE — date_sent set, no date_received, past threshold (default 14 days)
  STALE_PACKAGE — bid_package in bids_receiving/bidding with no activity > 21 days
"""
import os
from datetime import date, timedelta
from typing import Any


_THRESHOLDS = {
    "no_response_warn_days": int(os.environ.get("BID_STALE_WARN_DAYS", "7")),
    "no_response_alert_days": int(os.environ.get("BID_STALE_ALERT_DAYS", "14")),
    "stale_package_days": int(os.environ.get("BID_STALE_PACKAGE_DAYS", "21")),
    "expiry_warn_days": int(os.environ.get("BID_EXPIRY_WARN_DAYS", "3")),
}

LIVE_PROJECT_IDS = [1, 2, 3]  # 64EW, 101F, 1355R. Fixed 2026-07-08: id 8 (246GW) was
# wrongly included - it's a pilot candidate, not live (Buck). Read-only alert generation,
# no writes, but was generating stale/expiry alerts for it as if it were an active pilot.


def run_stale_check(conn) -> dict[str, Any]:
    """Run all stale checks. Returns structured results ready for alert/API."""
    today = date.today()
    results = {
        "run_date": today.isoformat(),
        "thresholds": _THRESHOLDS,
        "expiring": [],
        "expired": [],
        "no_response": [],
        "stale_packages": [],
    }

    with conn.cursor() as cur:
        # ── 1. Expiring bids (within N days) ─────────────────────────────────
        cur.execute("""
            SELECT be.id, v.company_name, p.name AS project, bp.csi_division,
                   be.date_sent, be.bid_expiry_date,
                   be.bid_expiry_date - %s AS days_until_expiry, be.status
            FROM bid_entries be
            JOIN vendors v   ON v.id  = be.vendor_id
            JOIN projects p  ON p.id  = be.project_id
            LEFT JOIN bid_packages bp ON bp.id = be.bid_package_id
            WHERE be.project_id = ANY(%s)
              AND be.bid_expiry_date IS NOT NULL
              AND be.bid_expiry_date >= %s
              AND be.bid_expiry_date <= %s
              AND be.status NOT IN ('received','awarded','bid_received')
            ORDER BY be.bid_expiry_date ASC
        """, (today, LIVE_PROJECT_IDS, today, today + timedelta(days=_THRESHOLDS["expiry_warn_days"])))
        for row in cur.fetchall():
            results["expiring"].append({
                "id": row[0], "vendor": row[1], "project": row[2],
                "csi": row[3], "date_sent": str(row[4]) if row[4] else None,
                "expiry": str(row[5]), "days_until_expiry": row[6], "status": row[7],
            })

        # ── 2. Expired bids ───────────────────────────────────────────────────
        cur.execute("""
            SELECT be.id, v.company_name, p.name AS project, bp.csi_division,
                   be.date_sent, be.bid_expiry_date,
                   %s - be.bid_expiry_date AS days_overdue, be.status
            FROM bid_entries be
            JOIN vendors v   ON v.id  = be.vendor_id
            JOIN projects p  ON p.id  = be.project_id
            LEFT JOIN bid_packages bp ON bp.id = be.bid_package_id
            WHERE be.project_id = ANY(%s)
              AND be.bid_expiry_date IS NOT NULL
              AND be.bid_expiry_date < %s
              AND be.status NOT IN ('received','awarded','bid_received')
            ORDER BY be.bid_expiry_date ASC
        """, (today, LIVE_PROJECT_IDS, today))
        for row in cur.fetchall():
            results["expired"].append({
                "id": row[0], "vendor": row[1], "project": row[2],
                "csi": row[3], "date_sent": str(row[4]) if row[4] else None,
                "expiry": str(row[5]), "days_overdue": row[6], "status": row[7],
            })

        # ── 3. Sent but no response past threshold ────────────────────────────
        cur.execute("""
            SELECT be.id, v.company_name, p.name AS project, bp.csi_division,
                   be.date_sent,
                   %s - be.date_sent AS days_waiting, be.status,
                   CASE WHEN %s - be.date_sent > %s THEN 'ALERT' ELSE 'WARN' END AS severity
            FROM bid_entries be
            JOIN vendors v   ON v.id  = be.vendor_id
            JOIN projects p  ON p.id  = be.project_id
            LEFT JOIN bid_packages bp ON bp.id = be.bid_package_id
            WHERE be.project_id = ANY(%s)
              AND be.date_sent IS NOT NULL
              AND be.date_received IS NULL
              AND be.status NOT IN ('received','awarded','bid_received')
              AND %s - be.date_sent >= %s
            ORDER BY days_waiting DESC
        """, (today, today, _THRESHOLDS["no_response_alert_days"],
              LIVE_PROJECT_IDS, today, _THRESHOLDS["no_response_warn_days"]))
        for row in cur.fetchall():
            results["no_response"].append({
                "id": row[0], "vendor": row[1], "project": row[2],
                "csi": row[3], "date_sent": str(row[4]),
                "days_waiting": row[5], "status": row[6], "severity": row[7],
            })

        # ── 4. Stale packages — collecting bids but no update in N days ───────
        cur.execute("""
            SELECT bp.id, p.name AS project, bp.csi_division, bp.package_name,
                   bp.status, bp.updated_at::date AS last_updated,
                   %s - bp.updated_at::date AS days_stale
            FROM bid_packages bp
            JOIN projects p ON p.id = bp.project_id
            WHERE bp.project_id = ANY(%s)
              AND bp.status IN ('bids_receiving','bidding')
              AND %s - bp.updated_at::date >= %s
              AND bp.package_name NOT ILIKE '%%DRAFT%%'
              AND bp.package_name NOT ILIKE '%%CSI Division%%'
              AND bp.package_name NOT ILIKE '%%Subcontractor%%'
              AND bp.package_name NOT ILIKE '%%PM:%%'
            ORDER BY days_stale DESC
            LIMIT 30
        """, (today, LIVE_PROJECT_IDS, today, _THRESHOLDS["stale_package_days"]))
        for row in cur.fetchall():
            results["stale_packages"].append({
                "id": row[0], "project": row[1], "csi": row[2],
                "package": row[3], "status": row[4],
                "last_updated": str(row[5]), "days_stale": row[6],
            })

    results["summary"] = {
        "expiring_count": len(results["expiring"]),
        "expired_count": len(results["expired"]),
        "no_response_count": len(results["no_response"]),
        "stale_packages_count": len(results["stale_packages"]),
        "total_flags": (len(results["expiring"]) + len(results["expired"]) +
                        len(results["no_response"]) + len(results["stale_packages"])),
        "needs_attention": any([results["expiring"], results["expired"], results["no_response"]]),
    }
    return results


def format_telegram_alert(results: dict) -> str | None:
    """Build a Telegram message from stale check results. Returns None if nothing urgent."""
    s = results["summary"]
    if not s["needs_attention"] and s["stale_packages_count"] == 0:
        return None

    lines = ["BID STALE ALERT — " + results["run_date"]]

    if results["expiring"]:
        lines.append(f"\nEXPIRING SOON ({s['expiring_count']}):")
        for b in results["expiring"]:
            lines.append(f"  {b['vendor']} | {b['project']} | expires {b['expiry']} ({b['days_until_expiry']}d)")

    if results["expired"]:
        lines.append(f"\nEXPIRED ({s['expired_count']}):")
        for b in results["expired"]:
            lines.append(f"  {b['vendor']} | {b['project']} | expired {b['expiry']} ({b['days_overdue']}d ago)")

    if results["no_response"]:
        alerts = [b for b in results["no_response"] if b["severity"] == "ALERT"]
        warns  = [b for b in results["no_response"] if b["severity"] == "WARN"]
        if alerts:
            lines.append(f"\nNO RESPONSE — OVERDUE ({len(alerts)}):")
            for b in alerts[:5]:
                lines.append(f"  {b['vendor']} | {b['project']} | sent {b['date_sent']} ({b['days_waiting']}d)")
        if warns:
            lines.append(f"\nNO RESPONSE — WARNING ({len(warns)}):")
            for b in warns[:3]:
                lines.append(f"  {b['vendor']} | {b['project']} | sent {b['date_sent']} ({b['days_waiting']}d)")

    if results["stale_packages"] and not results["expiring"] and not results["expired"]:
        lines.append(f"\nSTALE PACKAGES ({s['stale_packages_count']}) — no activity 21+ days:")
        for pkg in results["stale_packages"][:5]:
            lines.append(f"  {pkg['project']} | {pkg['package']} | {pkg['days_stale']}d idle")

    return "\n".join(lines)
