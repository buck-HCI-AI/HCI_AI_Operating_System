"""
HCI AI API — FastAPI dependency injection
Provides shared service clients as request-scoped dependencies.
"""
from fastapi import Header, HTTPException, status
from typing import Optional, Generator
from config import settings


# ── Authentication ─────────────────────────────────────────────────────────

def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    """
    Validate X-API-Key header.
    Development mode (no keys configured): all requests pass.
    Production mode: key must match one in settings.api_keys.
    """
    valid = settings.valid_api_keys
    if not valid:
        return None  # dev mode — open
    if not x_api_key or x_api_key not in valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key


# ── PostgreSQL ──────────────────────────────────────────────────────────────

def get_db() -> Generator:
    """Yield a psycopg2 connection, close on exit."""
    import psycopg2
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )
    try:
        yield conn
    finally:
        conn.close()


# ── Redis ───────────────────────────────────────────────────────────────────

def get_redis():
    """Return a Redis client."""
    import redis
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
    )


# ── MinIO ───────────────────────────────────────────────────────────────────

def get_minio():
    """Return a Minio client."""
    from minio import Minio
    endpoint = settings.minio_endpoint.replace("http://", "").replace("https://", "")
    return Minio(
        endpoint,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=settings.minio_secure,
    )


# ── Qdrant ──────────────────────────────────────────────────────────────────

def get_qdrant():
    """Return a QdrantClient."""
    from qdrant_client import QdrantClient
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
