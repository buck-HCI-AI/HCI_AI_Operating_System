"""Qdrant vector search service."""
from typing import List, Dict, Any, Optional
from config import settings

EMBED_MODEL = "BAAI/bge-small-en-v1.5"

# Collections routing: category keywords → collection
COLLECTION_ALIASES = {
    "projects":   "hci_project_documents",
    "documents":  "hci_project_documents",
    "vendors":    "hci_vendor_intelligence",
    "sops":       "hci_sops",
    "procurement":"hci_procurement",
    "costs":      "hci_historical_costs",
    "lessons":    "lessons_learned",
    "drive":      "drive_memory",
    "memory":     "drive_memory",
}

DEFAULT_COLLECTION = "hci_project_documents"


def _client():
    from qdrant_client import QdrantClient
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def _embed(text: str) -> List[float]:
    from fastembed import TextEmbedding
    embedder = TextEmbedding(EMBED_MODEL)
    return list(list(embedder.embed([text]))[0])


def resolve_collection(hint: Optional[str]) -> str:
    if not hint:
        return DEFAULT_COLLECTION
    lower = hint.lower()
    for keyword, col in COLLECTION_ALIASES.items():
        if keyword in lower:
            return col
    # Treat as direct collection name if it starts with hci_ or drive_
    if lower.startswith("hci_") or lower.startswith("drive_"):
        return lower
    return DEFAULT_COLLECTION


def search(
    query: str,
    collection: Optional[str] = None,
    limit: int = 10,
    score_threshold: float = 0.3,
    filters: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    col = resolve_collection(collection)
    vector = _embed(query)
    client = _client()

    qdrant_filter = None
    if filters:
        conditions = [
            FieldCondition(key=k, match=MatchValue(value=v))
            for k, v in filters.items() if v
        ]
        if conditions:
            qdrant_filter = Filter(must=conditions)

    # qdrant-client 1.18 removed QdrantClient.search() in favor of query_points()
    # (query= not query_vector=, response wraps points in .points) — found 2026-07-08:
    # every semantic search system-wide was silently returning [] via the bare
    # `except Exception: return []` in base.py, for however long this client version
    # has been installed. No caller could tell the difference between "no relevant
    # results" and "the call itself is broken."
    response = client.query_points(
        collection_name=col,
        query=vector,
        limit=limit,
        score_threshold=score_threshold,
        query_filter=qdrant_filter,
        with_payload=True,
    )

    return [
        {
            "score":      r.score,
            "collection": col,
            "payload":    r.payload or {},
            "text":       (r.payload or {}).get("text", ""),
        }
        for r in response.points
    ]


def list_collections() -> List[Dict[str, Any]]:
    client = _client()
    cols = client.get_collections().collections
    result = []
    for c in cols:
        info = client.get_collection(c.name)
        result.append({
            "name":         c.name,
            "vectors_count": info.points_count,
            "vector_size":  info.config.params.vectors.size if hasattr(info.config.params.vectors, 'size') else None,
        })
    return result


def ping() -> bool:
    try:
        _client().get_collections()
        return True
    except Exception:
        return False
