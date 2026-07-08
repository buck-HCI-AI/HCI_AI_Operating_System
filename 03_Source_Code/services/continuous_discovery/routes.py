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


@router.post("/scan-and-notify")
def scan_and_notify(connector_name: str = Query(None, description="Connector to scan (omit for all)")):
    """
    Run change detection and log result to platform_events.
    Used by n8n AUTO-CONTINUOUS-DISCOVERY workflow.
    """
    if connector_name:
        valid = {"houzz", "hubspot"}
        if connector_name not in valid:
            raise HTTPException(400, f"Unknown connector '{connector_name}'")
        result = detect_changes(connector_name)
        results = [result]
    else:
        result = detect_all_connectors()
        results = result.get("connectors", [])

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
