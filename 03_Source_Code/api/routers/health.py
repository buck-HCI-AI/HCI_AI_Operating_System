"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
def root():
    return {"system": "HCI AI Operating System", "status": "live", "ts": datetime.utcnow().isoformat()}

@router.get("/health")
def health():
    import psycopg2
    from qdrant_client import QdrantClient
    import redis as redis_lib

    results = {}

    try:
        from config import settings as _s
        c = psycopg2.connect(host=_s.postgres_host, port=_s.postgres_port,
                             dbname=_s.postgres_db, user=_s.postgres_user,
                             password=_s.postgres_password)
        cur = c.cursor()
        cur.execute("SELECT COUNT(*) FROM projects")
        n = cur.fetchone()[0]
        c.close()
        results["postgres"] = {"status": "ok", "projects": n}
    except Exception as e:
        results["postgres"] = {"status": "error", "detail": str(e)}

    try:
        q = QdrantClient(host="localhost", port=6333)
        cols = q.get_collections().collections
        results["qdrant"] = {"status": "ok", "collections": len(cols)}
    except Exception as e:
        results["qdrant"] = {"status": "error", "detail": str(e)}

    try:
        from config import settings as _s
        r = redis_lib.Redis(host=_s.redis_host, port=_s.redis_port, password=_s.redis_password)
        r.ping()
        results["redis"] = {"status": "ok"}
    except Exception as e:
        results["redis"] = {"status": "error", "detail": str(e)}

    all_ok = all(v["status"] == "ok" for v in results.values())
    return {"status": "healthy" if all_ok else "degraded", "services": results, "ts": datetime.utcnow().isoformat()}
