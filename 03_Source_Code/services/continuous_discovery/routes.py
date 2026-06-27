"""
Continuous Discovery Engine API routes.
Mounted at /api/v1/services/continuous-discovery
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

from fastapi import APIRouter, HTTPException, Query
from detection import detect_changes, detect_all_connectors, log_discovery_scan

router = APIRouter()


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
