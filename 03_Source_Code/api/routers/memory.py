"""
Memory search endpoints — semantic search over Qdrant collections.
Uses fastembed BAAI/bge-small-en-v1.5 (384 dims, no API key).
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import Q

router = APIRouter()

# Lazy-load the embed model (first call downloads if needed)
_EMBED = None
def get_embed():
    global _EMBED
    if _EMBED is None:
        from fastembed import TextEmbedding
        _EMBED = TextEmbedding("BAAI/bge-small-en-v1.5")
    return _EMBED

VALID_COLLECTIONS = {
    "vendor_memory", "bid_memory", "project_memory",
    "constitution_memory", "meeting_memory", "lessons_learned", "photo_memory"
}

def embed_query(text: str) -> list:
    model = get_embed()
    return list(list(model.embed([text]))[0])

class SearchResult(BaseModel):
    id:      int
    score:   float
    payload: dict

@router.get("/search")
def search_memory(
    q:          str,
    collection: str = "vendor_memory",
    limit:      int = Query(default=5, le=20),
):
    """
    Semantic search over any Qdrant collection.

    Examples:
      GET /memory/search?q=masonry+subcontractor&collection=vendor_memory
      GET /memory/search?q=fire+suppression+bid&collection=bid_memory
      GET /memory/search?q=full+interior+remodel&collection=project_memory
    """
    if collection not in VALID_COLLECTIONS:
        raise HTTPException(400, f"Unknown collection. Valid: {sorted(VALID_COLLECTIONS)}")

    try:
        vector = embed_query(q)
        results = Q.query_points(
            collection_name=collection,
            query=vector,
            limit=limit,
        ).points
        return [{"id": r.id, "score": round(r.score, 4), "payload": r.payload} for r in results]
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search/vendors")
def search_vendors(q: str, limit: int = Query(default=5, le=20)):
    """Find vendors by trade, specialty, or name."""
    return search_memory(q=q, collection="vendor_memory", limit=limit)

@router.get("/search/bids")
def search_bids(q: str, limit: int = Query(default=5, le=20)):
    """Find bids by scope, trade, project, or amount context."""
    return search_memory(q=q, collection="bid_memory", limit=limit)

@router.get("/search/projects")
def search_projects(q: str, limit: int = Query(default=5, le=20)):
    """Find projects by scope, status, or location."""
    return search_memory(q=q, collection="project_memory", limit=limit)

@router.get("/search/docs")
def search_docs(q: str, limit: int = Query(default=5, le=20)):
    """Search system docs, SOPs, architecture, and constitution."""
    return search_memory(q=q, collection="constitution_memory", limit=limit)

@router.get("/search/all")
def search_all(q: str, limit_per: int = Query(default=3, le=10)):
    """
    Search across all populated collections simultaneously.
    Returns top results from each with their collection name.
    """
    populated = ["vendor_memory", "bid_memory", "project_memory", "constitution_memory"]
    out = {}
    for col in populated:
        try:
            vector = embed_query(q)
            results = Q.query_points(collection_name=col, query=vector, limit=limit_per).points
            out[col] = [{"id": r.id, "score": round(r.score, 4), "payload": r.payload} for r in results]
        except Exception as e:
            out[col] = {"error": str(e)}
    return out

@router.get("/collections")
def list_collections():
    """List all Qdrant collections with vector counts."""
    cols = Q.get_collections().collections
    result = []
    for c in cols:
        info = Q.get_collection(c.name)
        result.append({
            "name":         c.name,
            "vector_count": info.points_count,
        })
    return sorted(result, key=lambda x: x["name"])
