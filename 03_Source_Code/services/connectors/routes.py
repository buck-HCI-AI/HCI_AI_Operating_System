"""
Connector Framework Routes — /api/v1/services/connectors

Endpoints:
  GET  /connectors               — list all connectors + sync state summary
  GET  /connectors/{name}        — connector detail + per-entity sync state
  POST /connectors/{name}/ingest — receive canonical JSON from Browser Agent
  GET  /connectors/{name}/sync-state — raw sync state per entity
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any
from houzz_connector import HouzzConnector

router = APIRouter()

# Registry — add new connectors here as they're built
CONNECTORS: dict[str, type] = {
    "houzz": HouzzConnector,
}


class IngestPayload(BaseModel):
    data: dict[str, list[Any]]      # {entity_type: [records...]}
    source: Optional[str] = "browser_claude"
    extraction_notes: Optional[str] = None
    dry_run: Optional[bool] = True


def _get_connector(name: str, dry_run: bool = True):
    cls = CONNECTORS.get(name)
    if not cls:
        raise HTTPException(status_code=404, detail=f"Connector '{name}' not found. Available: {list(CONNECTORS.keys())}")
    return cls(dry_run=dry_run)


@router.get("")
def list_connectors():
    result = []
    for name, cls in CONNECTORS.items():
        c = cls(dry_run=True)
        try:
            states = c.list_sync_states()
            last_sync = max((s["last_synced_at"] for s in states if s.get("last_synced_at")), default=None)
            error_count = sum(1 for s in states if s.get("status") == "error")
        except Exception:
            states = []
            last_sync = None
            error_count = 0

        result.append({
            "name": name,
            "version": cls.version,
            "entities": cls.supported_entities,
            "entity_count": len(cls.supported_entities),
            "last_synced_at": str(last_sync) if last_sync else None,
            "error_count": error_count,
            "status": "error" if error_count > 0 else "ok",
        })
    return {"connectors": result, "total": len(result)}


@router.get("/{name}")
def connector_detail(name: str):
    c = _get_connector(name)
    try:
        states = c.list_sync_states()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB unavailable: {e}")
    return {
        "connector": name,
        "version": type(c).version,
        "supported_entities": type(c).supported_entities,
        "sync_states": states,
    }


@router.get("/{name}/sync-state")
def sync_state(name: str, entity_type: Optional[str] = None, external_id: Optional[str] = None):
    c = _get_connector(name)
    if entity_type:
        state = c.get_sync_state(entity_type, external_id)
        if not state:
            raise HTTPException(status_code=404, detail=f"No sync state for {name}/{entity_type}")
        return state
    return {"sync_states": c.list_sync_states()}


@router.post("/{name}/ingest")
def ingest(name: str, payload: IngestPayload):
    """
    Receive canonical JSON from Browser Agent.
    Set dry_run=false in payload to write to DB (requires prior dry_run pass).
    """
    c = _get_connector(name, dry_run=payload.dry_run)

    if not payload.data:
        raise HTTPException(status_code=422, detail="payload.data is empty")

    total_records = sum(len(v) for v in payload.data.values())
    if total_records == 0:
        raise HTTPException(status_code=422, detail="No records found in payload.data")

    result = c.ingest(payload.data)
    result["source"] = payload.source
    result["extraction_notes"] = payload.extraction_notes
    result["entity_types_received"] = list(payload.data.keys())
    result["total_records_received"] = total_records

    return result
