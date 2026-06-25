"""
Unified semantic search endpoint.
Single entry point for all Qdrant collections — routes by context or explicit collection name.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from schemas.search import SearchRequest, SearchResponse, SearchResult
import services.vector as vector
import services.cache as cache
import json

router = APIRouter()


@router.post("", response_model=SearchResponse)
def search(req: SearchRequest):
    """
    Semantic search across HCI AI knowledge base.

    - Omit `collection` to auto-route (default: hci_project_documents)
    - Pass `project_filter` to scope results to a project (e.g. '64EW')
    - Pass `category_filter` to scope by document category (e.g. 'bids')
    """
    cache_key = f"search:{req.query}:{req.collection}:{req.limit}:{req.project_filter}:{req.category_filter}"
    cached = cache.get(cache_key)
    if cached:
        return SearchResponse(**cached)

    filters = {}
    if req.project_filter:
        filters["project_number"] = req.project_filter
    if req.category_filter:
        filters["document_category"] = req.category_filter

    try:
        results = vector.search(
            query=req.query,
            collection=req.collection,
            limit=req.limit,
            score_threshold=req.score_threshold,
            filters=filters or None,
        )
    except Exception as e:
        raise HTTPException(503, f"Search unavailable: {e}")

    col_searched = vector.resolve_collection(req.collection)
    response = SearchResponse(
        query=req.query,
        collection_searched=col_searched,
        total_results=len(results),
        results=[SearchResult(**r) for r in results],
    )

    cache.set(cache_key, response.model_dump(), ttl=120)
    return response


@router.get("/collections")
def list_collections():
    """List all available Qdrant collections with vector counts."""
    try:
        return {"collections": vector.list_collections()}
    except Exception as e:
        raise HTTPException(503, f"Qdrant unavailable: {e}")
