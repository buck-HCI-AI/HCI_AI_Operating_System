"""
Change Detection Engine
Compares current connector sync state vs last known state to detect:
- New records since last scan
- Sync health changes (idle → error)
- Connectors that have gone stale (no sync > threshold hours)
"""
import os, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

STALE_HOURS = {
    "houzz": 26,    # nightly — flag if >26h since last sync
    "hubspot": 2,   # hourly — flag if >2h since last sync
}

ENTITY_TABLE_MAP = {
    # connector_name → (entity_type, db_table, count_column)
    "houzz": [
        ("projects",       "houzz_projects",       "id"),
        ("tasks",          "houzz_tasks",           "id"),
        ("schedule_items", "project_schedule_items",  "id"),
        ("purchase_orders","houzz_purchase_orders",  "id"),
        ("change_orders",  "houzz_change_orders",    "id"),
        ("subcontractors", "houzz_subcontractors",   "id"),
        ("daily_logs",     "houzz_daily_logs",       "id"),
        ("budget",         "houzz_budget",           "id"),
        ("messages",       "houzz_messages",         "id"),
    ],
    "hubspot": [
        ("contacts",  "hubspot_contacts",  "id"),
        ("deals",     "hubspot_deals",     "id"),
        ("companies", "hubspot_companies", "id"),
        ("notes",     "hubspot_notes",     "id"),
    ],
}


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


def _count_table(table: str) -> int:
    try:
        row = _q1(f"SELECT COUNT(*) AS cnt FROM {table}")
        return int(row.get("cnt") or 0)
    except Exception:
        return -1


def _count_recent(table: str, hours: int = 24) -> int:
    """Count records added in the last N hours — uses synced_at if available."""
    for col in ("synced_at", "created_at", "updated_at"):
        try:
            row = _q1(f"SELECT COUNT(*) AS cnt FROM {table} WHERE {col} > NOW() - INTERVAL '{hours} hours'")
            return int(row.get("cnt") or 0)
        except Exception:
            continue
    return 0


def detect_changes(connector_name: str) -> dict:
    """
    Run change detection for a connector.
    Returns: status, changes, stale_entities, new_records summary.
    """
    now = datetime.now(timezone.utc)
    entities = ENTITY_TABLE_MAP.get(connector_name, [])
    stale_threshold = STALE_HOURS.get(connector_name, 26)

    sync_states = _q("""
        SELECT entity_type, last_synced_at, records_synced, status, error_message
        FROM connector_sync_state
        WHERE connector_name = %s
        ORDER BY entity_type
    """, (connector_name,))

    sync_by_entity = {s["entity_type"]: s for s in sync_states}

    entity_reports = []
    total_new_records = 0
    stale_count = 0
    error_count = 0

    for entity_type, table, _ in entities:
        state = sync_by_entity.get(entity_type, {})
        last_synced = state.get("last_synced_at")
        status = state.get("status", "never_synced")
        records_synced = state.get("records_synced") or 0

        current_count = _count_table(table)
        new_in_24h = _count_recent(table, 24)
        total_new_records += new_in_24h

        age_hours = None
        is_stale = False
        if last_synced:
            age_hours = round((now - last_synced).total_seconds() / 3600, 1)
            is_stale = age_hours > stale_threshold
            if is_stale:
                stale_count += 1

        if status == "error":
            error_count += 1

        entity_reports.append({
            "entity_type": entity_type,
            "table": table,
            "current_count": current_count,
            "new_in_24h": new_in_24h,
            "last_synced_at": last_synced.isoformat() if last_synced else None,
            "age_hours": age_hours,
            "is_stale": is_stale,
            "sync_status": status,
            "error_message": state.get("error_message"),
        })

    # Overall connector health
    has_data = any(r["current_count"] > 0 for r in entity_reports)
    has_recent_activity = total_new_records > 0
    has_errors = error_count > 0

    if has_errors:
        detection_status = "ERROR"
    elif stale_count > len(entities) // 2:
        detection_status = "STALE"
    elif not has_data:
        detection_status = "NO_DATA"
    elif has_recent_activity:
        detection_status = "CHANGES_DETECTED"
    else:
        detection_status = "NO_CHANGES"

    return {
        "connector": connector_name,
        "checked_at": now.isoformat(),
        "detection_status": detection_status,
        "summary": {
            "total_new_records_24h": total_new_records,
            "stale_entity_count": stale_count,
            "error_entity_count": error_count,
            "entities_with_data": sum(1 for r in entity_reports if r["current_count"] > 0),
            "total_entities": len(entity_reports),
        },
        "entities": entity_reports,
        "action_required": detection_status in ("ERROR", "STALE"),
        "changes_ready_to_ingest": detection_status == "CHANGES_DETECTED",
    }


def detect_all_connectors() -> dict:
    """Run change detection across all registered connectors."""
    now = datetime.now(timezone.utc)
    results = []
    for connector in ENTITY_TABLE_MAP:
        try:
            result = detect_changes(connector)
            results.append(result)
        except Exception as e:
            results.append({
                "connector": connector,
                "checked_at": now.isoformat(),
                "detection_status": "ERROR",
                "error": str(e),
            })

    changes_detected = [r for r in results if r.get("detection_status") == "CHANGES_DETECTED"]
    connectors_with_errors = [r for r in results if r.get("detection_status") in ("ERROR", "STALE")]

    return {
        "checked_at": now.isoformat(),
        "overall_status": (
            "CHANGES_DETECTED" if changes_detected else
            "ERROR" if connectors_with_errors else
            "NO_CHANGES"
        ),
        "connectors_checked": len(results),
        "connectors_with_changes": len(changes_detected),
        "connectors_with_issues": len(connectors_with_errors),
        "connectors": results,
        "summary": (
            f"{len(changes_detected)} connector(s) with new data" if changes_detected
            else f"No new data — {len(connectors_with_errors)} connector issue(s)" if connectors_with_errors
            else "All connectors current — no new data detected"
        ),
    }


def log_discovery_scan(connector: str, status: str, new_records: int, notes: str = "") -> None:
    """Write a scan result to platform_events for audit trail."""
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO platform_events
                        (event_type, source, severity, title, body, created_at)
                    VALUES ('discovery_scan', %s, 'INFO', %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                """, (
                    f"connector:{connector}",
                    f"Discovery scan: {connector} — {status}",
                    f"new_records={new_records} | {notes}",
                ))
                conn.commit()
    except Exception:
        pass  # Non-critical audit; do not surface to caller
