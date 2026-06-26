"""SOP 10 — Layer 4: Allowances, Alternates, and Exclusions data fields."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "project_id",
    "sop09_budget_approved",
    "project_type",
    "scope_narrative",
]

INPUT_LABELS = {
    "project_id":             "Project ID",
    "sop09_budget_approved":  "SOP 09 Budget Review — Approved (confirmed before SOP 10)",
    "project_type":           "Project type (commercial, residential, renovation, mixed-use)",
    "scope_narrative":        "Construction narrative (SOP 05 output or equivalent)",
}

BUCK_REVIEW_THRESHOLD = 50_000.00  # Total allowance pool requiring Buck review

ALLOWANCE_TYPES = [
    "owner_allowance",       # Owner-directed item, cost TBD
    "construction_allowance", # Contractor allowance for undefined work
    "contingency_allowance",  # Risk-based contingency (not a line-item)
    "design_allowance",       # Design-phase item not yet fully detailed
]

ALTERNATE_TYPES = [
    "additive",    # Add to base scope if accepted
    "deductive",   # Deduct from base scope if accepted
    "substitution", # Replace base item with alternate
]


@dataclass
class AllowanceItem:
    allowance_code: str
    description: str
    allowance_type: str
    amount: float
    trade_code: str
    basis: str = ""
    ai_suggested: bool = False
    pm_confirmed: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "allowance_code": self.allowance_code,
            "description": self.description,
            "allowance_type": self.allowance_type,
            "amount": self.amount,
            "trade_code": self.trade_code,
            "basis": self.basis,
            "ai_suggested": self.ai_suggested,
            "pm_confirmed": self.pm_confirmed,
        }


@dataclass
class AlternateItem:
    alternate_code: str
    description: str
    alternate_type: str
    estimated_cost_impact: float
    trade_code: str
    basis: str = ""
    pm_confirmed: bool = False
    included_in_base: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "alternate_code": self.alternate_code,
            "description": self.description,
            "alternate_type": self.alternate_type,
            "estimated_cost_impact": self.estimated_cost_impact,
            "trade_code": self.trade_code,
            "included_in_base": self.included_in_base,
        }


@dataclass
class ExclusionItem:
    exclusion_code: str
    description: str
    trade_code: str
    excluded_party: str = "subcontractor"
    basis: str = ""
    pm_confirmed: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "exclusion_code": self.exclusion_code,
            "description": self.description,
            "trade_code": self.trade_code,
            "excluded_party": self.excluded_party,
        }


@dataclass
class AllowancesOutput:
    instance_id: int
    project_id: int
    allowances: list[AllowanceItem] = field(default_factory=list)
    alternates: list[AlternateItem] = field(default_factory=list)
    exclusions: list[ExclusionItem] = field(default_factory=list)

    def total_allowance_pool(self) -> float:
        return sum(a.amount for a in self.allowances)

    def requires_buck_review(self) -> bool:
        return self.total_allowance_pool() > BUCK_REVIEW_THRESHOLD

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "allowances": [a.to_dict() for a in self.allowances],
            "alternates": [a.to_dict() for a in self.alternates],
            "exclusions": [e.to_dict() for e in self.exclusions],
            "total_allowance_pool": self.total_allowance_pool(),
            "requires_buck_review": self.requires_buck_review(),
        }


class SOP10Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    BUCK_REVIEW_THRESHOLD = BUCK_REVIEW_THRESHOLD
    ALLOWANCE_TYPES = ALLOWANCE_TYPES
    ALTERNATE_TYPES = ALTERNATE_TYPES
