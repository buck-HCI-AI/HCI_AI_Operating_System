"""SOP 12 — Subcontractor CRM."""
from .sop_12_templates import (
    SubCandidateRecord, BidListRecommendation, SOP12Templates,
    REQUIRED_INPUT_KEYS, MIN_QUALIFIED_SUBS,
)
from .sop_12_agent import SOP12Agent
from .sop_12_service import SOP12SubCRMService

__all__ = [
    "SubCandidateRecord", "BidListRecommendation", "SOP12Templates",
    "REQUIRED_INPUT_KEYS", "MIN_QUALIFIED_SUBS",
    "SOP12Agent",
    "SOP12SubCRMService",
]
