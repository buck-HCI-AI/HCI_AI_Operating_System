"""SOP 12 — Layer 4: Subcontractor CRM data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "project_id",
    "trade_code",
    "trade_name",
    "sop_11_instance_id",
]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "trade_code":          "CSI trade code",
    "trade_name":          "Trade name",
    "sop_11_instance_id":  "SOP 11 Bid Package — instance ID requiring subs for this trade",
}

MIN_QUALIFIED_SUBS = 3      # Operating rule: MIN_BIDDERS
PERFORMANCE_RATINGS = ["PREFERRED", "QUALIFIED", "CONDITIONAL", "DO_NOT_USE"]
DISQUALIFICATION_REASONS = [
    "poor_performance", "insurance_lapsed", "unlicensed",
    "failed_to_bid", "failed_to_complete", "payment_dispute",
]


@dataclass
class SubCandidateRecord:
    sub_name: str
    trade_code: str
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    license_number: str = ""
    bonded: bool = False
    insured: bool = False
    prequalified: bool = False
    performance_rating: str = "QUALIFIED"
    last_hci_project: str = ""
    ai_risk_flag: str = ""
    pm_approved: bool = False
    notes: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.sub_name:
            errors.append("sub_name is required")
        if not self.trade_code:
            errors.append("trade_code is required")
        if self.performance_rating not in PERFORMANCE_RATINGS:
            errors.append(f"performance_rating must be one of {PERFORMANCE_RATINGS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "sub_name": self.sub_name,
            "trade_code": self.trade_code,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "bonded": self.bonded,
            "insured": self.insured,
            "prequalified": self.prequalified,
            "performance_rating": self.performance_rating,
            "last_hci_project": self.last_hci_project,
            "ai_risk_flag": self.ai_risk_flag,
            "pm_approved": self.pm_approved,
            "notes": self.notes,
        }


@dataclass
class BidListRecommendation:
    trade_code: str
    trade_name: str
    recommended_subs: list[str] = field(default_factory=list)
    excluded_subs: list[dict] = field(default_factory=list)  # {sub, reason}
    total_candidates: int = 0
    coverage_adequate: bool = False
    ai_note: str = ""

    def to_dict(self) -> dict:
        return {
            "trade_code": self.trade_code,
            "trade_name": self.trade_name,
            "recommended_subs": self.recommended_subs,
            "excluded_subs": self.excluded_subs,
            "recommended_count": len(self.recommended_subs),
            "total_candidates": self.total_candidates,
            "coverage_adequate": self.coverage_adequate,
            "ai_note": self.ai_note,
        }


class SOP12Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    MIN_QUALIFIED_SUBS = MIN_QUALIFIED_SUBS
    PERFORMANCE_RATINGS = PERFORMANCE_RATINGS
