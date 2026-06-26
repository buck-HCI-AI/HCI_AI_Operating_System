"""SOP 16 — Layer 4: Buyout data fields and template validators."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "sop_15_instance_id",
    "awarded_sub",
    "award_amount",
    "scope_basis",
    "trade_name",
    "trade_code",
]

INPUT_LABELS = {
    "sop_15_instance_id": "SOP 15 Bid Leveling — Handed Off instance ID",
    "awarded_sub":        "Awarded subcontractor name (from Gate 15-C)",
    "award_amount":       "Award amount ($) confirmed by Buck (from Gate 15-C)",
    "scope_basis":        "Scope basis statement (what is and is not included)",
    "trade_name":         "Trade name",
    "trade_code":         "CSI trade code",
}

SUBCONTRACT_TYPES = [
    "lump_sum",
    "unit_price",
    "cost_plus",
    "guaranteed_max",
]


@dataclass
class BuyoutRecord:
    sub_name: str
    trade_name: str
    trade_code: str
    award_amount: float
    scope_basis: str
    subcontract_type: str = "lump_sum"
    rationale: str = ""
    risks_accepted: str = ""
    conditions: str = ""
    award_memo_draft: str | None = None
    scope_confirmed: bool = False
    subcontract_initiated: bool = False
    pm_confirmed: bool = False

    def to_dict(self) -> dict:
        return {
            "sub_name": self.sub_name,
            "trade_name": self.trade_name,
            "trade_code": self.trade_code,
            "award_amount": self.award_amount,
            "scope_basis": self.scope_basis,
            "subcontract_type": self.subcontract_type,
            "scope_confirmed": self.scope_confirmed,
            "subcontract_initiated": self.subcontract_initiated,
            "pm_confirmed": self.pm_confirmed,
        }


@dataclass
class ScopeComparisonResult:
    aligned: bool
    discrepancies: list[dict] = field(default_factory=list)
    ai_note: str = ""
    confidence: str = "MEDIUM"

    def to_dict(self) -> dict:
        return {
            "aligned": self.aligned,
            "discrepancy_count": len(self.discrepancies),
            "discrepancies": self.discrepancies,
            "ai_note": self.ai_note,
            "confidence": self.confidence,
        }


class SOP16Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    SUBCONTRACT_TYPES = SUBCONTRACT_TYPES
