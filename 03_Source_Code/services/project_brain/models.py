"""Project Brain data models."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProjectQuery(BaseModel):
    question: str = Field(..., description="Natural language question about the project")
    context_hint: Optional[str] = Field(
        default=None,
        description="Optional: 'bids', 'schedule', 'vendors', 'budget' to bias search"
    )
    max_sources: int = Field(default=6, ge=1, le=20)


class SourceReference(BaseModel):
    text: str
    source: str
    score: float
    collection: str


class ProjectQueryResponse(BaseModel):
    project_number: str
    question: str
    answer: str
    sources: List[SourceReference]
    model_used: str = "claude-haiku-4-5-20251001"
    cached: bool = False


class BidPackageSummary(BaseModel):
    package_name: str
    csi_division: Optional[str]
    bid_count: int
    lowest_bid: Optional[float]
    highest_bid: Optional[float]
    spread_pct: Optional[float]


class EventCreate(BaseModel):
    event_type: str = Field(..., description="milestone|risk|decision|change_order|document|issue|resolution|note")
    event_date: Optional[str] = Field(default=None, description="ISO date (YYYY-MM-DD); defaults to today")
    title: str
    description: Optional[str] = None
    source_table: Optional[str] = None
    source_id: Optional[int] = None
    created_by: str = Field(default="user")
    metadata: Optional[Dict[str, Any]] = None


class DocumentLinkCreate(BaseModel):
    document_type: str = Field(..., description="bid|meeting|daily_log|drive_file|houzz_file|hubspot_note|email")
    document_id: str
    document_name: str
    document_date: Optional[str] = None
    linked_entity_type: str = Field(..., description="decision|risk|change_order|milestone|issue|vendor")
    linked_entity_id: Optional[str] = None
    linked_entity_name: Optional[str] = None
    relationship: str = Field(default="documented", description="drove|supported|contradicted|documented|resolved")
    notes: Optional[str] = None
    created_by: str = Field(default="user")


class ProjectSnapshot(BaseModel):
    project_number: str
    name: str
    address: str
    status: str
    scope: Optional[str]
    budget_estimate: Optional[float]

    bid_packages: List[BidPackageSummary] = []
    vendor_count: int = 0
    document_count: int = 0
    vector_count: int = 0

    recent_meetings: List[Dict[str, Any]] = []
    recent_daily_logs: List[Dict[str, Any]] = []
    recent_hs_notes: List[Dict[str, Any]] = []

    hubspot_deal_id: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = False
