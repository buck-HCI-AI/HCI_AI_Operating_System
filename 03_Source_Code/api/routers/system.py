"""
System status endpoints — detailed health of all services.
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter
from datetime import datetime, timezone
from schemas.common import SystemStatusResponse, ServiceStatus
from config import settings
import services.db as db
import services.cache as cache
import services.storage as storage
import services.vector as vector

router = APIRouter()


def _check_postgres() -> ServiceStatus:
    t = time.perf_counter()
    try:
        result = db.query_one("SELECT COUNT(*) as n FROM projects")
        ms = (time.perf_counter() - t) * 1000
        return ServiceStatus(name="postgres", status="ok",
                             detail=f"{result['n']} projects", latency_ms=round(ms, 1))
    except Exception as e:
        return ServiceStatus(name="postgres", status="down", detail=str(e))


def _check_redis() -> ServiceStatus:
    t = time.perf_counter()
    try:
        ok = cache.ping()
        ms = (time.perf_counter() - t) * 1000
        return ServiceStatus(name="redis", status="ok" if ok else "down", latency_ms=round(ms, 1))
    except Exception as e:
        return ServiceStatus(name="redis", status="down", detail=str(e))


def _check_minio() -> ServiceStatus:
    t = time.perf_counter()
    try:
        buckets = storage.list_buckets()
        ms = (time.perf_counter() - t) * 1000
        return ServiceStatus(name="minio", status="ok",
                             detail=f"{len(buckets)} buckets", latency_ms=round(ms, 1))
    except Exception as e:
        return ServiceStatus(name="minio", status="down", detail=str(e))


def _check_qdrant() -> ServiceStatus:
    t = time.perf_counter()
    try:
        cols = vector.list_collections()
        ms = (time.perf_counter() - t) * 1000
        total_vectors = sum(c.get("vectors_count") or 0 for c in cols)
        return ServiceStatus(name="qdrant", status="ok",
                             detail=f"{len(cols)} collections, {total_vectors:,} vectors",
                             latency_ms=round(ms, 1))
    except Exception as e:
        return ServiceStatus(name="qdrant", status="down", detail=str(e))


@router.get("", response_model=SystemStatusResponse)
def system_status():
    """Full system health check — all services, latencies, counts."""
    services_status = [
        _check_postgres(),
        _check_redis(),
        _check_minio(),
        _check_qdrant(),
    ]
    any_down     = any(s.status == "down" for s in services_status)
    any_degraded = any(s.status == "degraded" for s in services_status)

    overall = "down" if any_down else ("degraded" if any_degraded else "healthy")

    return SystemStatusResponse(
        status=overall,
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
        services=services_status,
    )


@router.get("/collections")
def qdrant_collections():
    """List all Qdrant collections with vector counts."""
    try:
        return {"collections": vector.list_collections()}
    except Exception as e:
        return {"error": str(e), "collections": []}


@router.get("/storage")
def storage_status():
    """List MinIO buckets and object counts."""
    try:
        buckets = storage.list_buckets()
        detail = []
        for b in buckets:
            objects = storage.list_objects(b, limit=1000)
            detail.append({"bucket": b, "objects": len(objects)})
        return {"status": "ok", "buckets": detail}
    except Exception as e:
        return {"status": "down", "error": str(e)}


@router.get("/config")
def config_info():
    """Return non-sensitive config summary for debugging."""
    return {
        "app_version":   settings.app_version,
        "postgres_host": settings.postgres_host,
        "postgres_db":   settings.postgres_db,
        "redis_host":    settings.redis_host,
        "minio_endpoint":settings.minio_endpoint,
        "qdrant_host":   settings.qdrant_host,
        "storage_root":  settings.hci_storage_root or "(named volumes)",
        "auth_mode":     "production" if settings.valid_api_keys else "development",
    }
