"""
Continuous Discovery Engine API routes.
Mounted at /api/v1/services/continuous-discovery
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

from fastapi import APIRouter, HTTPException, Query
from detection import detect_changes, detect_all_connectors, log_discovery_scan

router = APIRouter()


def _ensure_standing_alert(r: dict) -> None:
    """Found 2026-07-07 (ADR-016 addendum): this scan was correctly detecting real
    staleness/errors and firing a real ntfy push every time - but ntfy is a
    fire-and-forget notification, not a tracked item. A real "HubSpot: STALE"
    alert sat in the push history unread while the underlying problem (a dead
    AUTO-004 scheduler) went unfixed for days. ntfy still fires (n8n handles that
    side) - this makes the same detection also create a standing, visible
    ai_messages record that stays open until someone resolves it, so a stale
    alert can't just scroll off a notification feed unnoticed. Idempotent: won't
    create a second open alert for the same connector+status while one is
    already outstanding."""
    status = r.get("detection_status", "UNKNOWN")
    if status not in ("STALE", "ERROR"):
        return
    connector = r.get("connector", "unknown")
    title = f"Continuous-discovery: {connector} is {status}"
    try:
        import psycopg2, psycopg2.extras, os as _os
        conn = psycopg2.connect(
            host=_os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(_os.environ.get("POSTGRES_PORT", 5432)),
            dbname=_os.environ.get("POSTGRES_DB", "hci_os"),
            user=_os.environ.get("POSTGRES_USER", "hci_admin"),
            password=_os.environ.get("POSTGRES_PASSWORD", ""),
        )
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id FROM ai_messages WHERE title = %s AND status NOT IN ('COMPLETE','REJECTED') LIMIT 1",
                (title,),
            )
            if cur.fetchone():
                conn.close()
                return  # already open, don't spam a duplicate every hourly run
            cur.execute("""
                INSERT INTO ai_messages
                    (source_agent, target_agent, message_type, title, body, status, priority)
                VALUES ('continuous_discovery', 'buck', 'status_update', %s, %s, 'ISSUED', 'high')
            """, (title, json.dumps(r, default=str)))
            conn.commit()
        conn.close()
    except Exception:
        pass  # best-effort - never let alert-tracking break the actual scan


@router.get("")
def service_info():
    return {
        "service": "continuous-discovery",
        "version": "1.0.0",
        "status": "active",
        "description": (
            "Continuous Discovery Engine — detects new/changed records across connectors, "
            "triggers architecture sync, surfaces opportunities in Executive Dashboard"
        ),
        "endpoints": [
            "GET /detect           — Run change detection across all connectors",
            "GET /detect/{name}    — Run change detection for one connector (houzz|hubspot)",
            "POST /scan-and-notify — Run detection + log result to platform_events",
        ],
        "connector_schedule": {
            "hubspot": "hourly (AUTO-CONTINUOUS-DISCOVERY n8n workflow)",
            "houzz":   "nightly at 02:00 (requires Browser extraction first)",
        },
        "flow": [
            "1. n8n triggers detection on schedule",
            "2. /detect checks connector sync state vs current DB record counts",
            "3. If CHANGES_DETECTED → existing /services/connectors/{name}/ingest handles delta",
            "4. Architecture Sync Engine flags affected volumes",
            "5. New opportunities surface in Executive Mission Control",
        ],
    }


@router.get("/detect")
def detect_all():
    """Run change detection across all registered connectors (houzz + hubspot)."""
    return detect_all_connectors()


@router.get("/detect/{connector_name}")
def detect_one(connector_name: str):
    """Run change detection for a specific connector."""
    valid = {"houzz", "hubspot"}
    if connector_name not in valid:
        raise HTTPException(400, f"Unknown connector '{connector_name}'. Valid: {sorted(valid)}")
    return detect_changes(connector_name)


_AUTO_HEAL_CAPABLE = {"hubspot"}  # houzz has no self-fetching sync() - no official API exists to pull from


def _auto_heal_if_stale(r: dict) -> dict:
    """
    Found 2026-07-08 (Buck: "what needs fixing right now"): this workflow has
    been running hourly, correctly detecting HubSpot as STALE, correctly firing
    a standing alert every time - and then doing nothing about it. The alert
    sat unactioned for 33+ hours until manually checked. detect_changes() was
    never wired to actually fix what it detects.

    A HubSpot sync is a pure read from HubSpot's own API into our local mirror
    tables - no write-back to HubSpot, no external commitment, same safety
    class as the existing n8n SQLITE_IOERR self-heal (/gateway/admin/self-heal
    - container-level infra only, never business data). Auto-triggering it here
    is that same pattern applied to connector staleness: safe to auto-fix,
    still visibly alerted (not silent), re-detects after to log the real
    outcome rather than assuming success.
    """
    if r.get("detection_status") != "STALE" or r.get("connector") not in _AUTO_HEAL_CAPABLE:
        return r
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "connectors"))
        from hubspot_connector import HubSpotConnector
        c = HubSpotConnector(dry_run=False)
        heal_result = c.sync()
        r["auto_heal"] = {"attempted": True, "result": heal_result}
        return detect_changes(r["connector"]) | {"auto_heal": r["auto_heal"]}
    except Exception as e:
        r["auto_heal"] = {"attempted": True, "error": str(e)}
        return r


@router.post("/scan-and-notify")
def scan_and_notify(connector_name: str = Query(None, description="Connector to scan (omit for all)")):
    """
    Run change detection, auto-heal known-safe staleness (HubSpot only - see
    _auto_heal_if_stale), and log the result to platform_events.
    Used by n8n AUTO-CONTINUOUS-DISCOVERY workflow.
    """
    if connector_name:
        valid = {"houzz", "hubspot"}
        if connector_name not in valid:
            raise HTTPException(400, f"Unknown connector '{connector_name}'")
        result = detect_changes(connector_name)
        result = _auto_heal_if_stale(result)
        results = [result]
    else:
        result = detect_all_connectors()
        results = [_auto_heal_if_stale(c) for c in result.get("connectors", [])]

    for r in results:
        log_discovery_scan(
            connector=r["connector"],
            status=r.get("detection_status", "UNKNOWN"),
            new_records=r.get("summary", {}).get("total_new_records_24h", 0),
            notes=r.get("summary", {}).get("summary", "") if isinstance(r.get("summary"), dict) else "",
        )
        _ensure_standing_alert(r)

    if connector_name:
        return {
            "logged": True,
            "connector": connector_name,
            "result": result,
        }
    return {
        "logged": True,
        "connectors_scanned": len(results),
        "result": result,
    }
