"""Search request and response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List


class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    collection: Optional[str] = Field(
        default=None,
        description="Qdrant collection to search. Omit to auto-route by project/category context."
    )
    limit: int = Field(default=10, ge=1, le=100)
    project_filter: Optional[str] = Field(
        default=None, description="Filter by project number (e.g. 64EW)"
    )
    category_filter: Optional[str] = Field(
        default=None, description="Filter by document category"
    )
    score_threshold: float = Field(default=0.3, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    score: float
    collection: str
    payload: dict
    text: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    collection_searched: str
    total_results: int
    results: List[SearchResult]
