"""SOP 07 — Layer 4: ROM Budget data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "project_id",
    "project_type",
    "gross_sf",
    "sop_05_instance_id",
]

INPUT_LABELS = {
    "project_id":         "Project ID",
    "project_type":       "Project type (commercial, residential, renovation, mixed-use)",
    "gross_sf":           "Gross square footage of project",
    "sop_05_instance_id": "SOP 05 Construction Narrative — Completed instance ID",
}

OPTIONAL_INPUT_KEYS = ["sop_06_instance_id", "owner_budget_target", "design_phase"]

BUCK_ROM_REVIEW_THRESHOLD = 500_000.00  # ROMs > $500k require Buck review
CONTINGENCY_DEFAULTS = {
    "renovation": 0.15,
    "commercial": 0.10,
    "residential": 0.10,
    "mixed-use": 0.12,
}
COST_BASIS_TYPES = ["historical_sf", "unit_price", "allowance", "subcontractor_estimate", "ai_estimate"]


@dataclass
class ROMLineItem:
    trade_code: str
    trade_name: str
    description: str
    unit: str = "LS"         # LS, SF, LF, EA, etc.
    quantity: float = 1.0
    unit_cost: float = 0.0
    basis: str = "ai_estimate"
    ai_generated: bool = False
    pm_confirmed: bool = False

    def total(self) -> float:
        return round(self.quantity * self.unit_cost, 2)

    def validate(self) -> list[str]:
        errors = []
        if not self.trade_code:
            errors.append("trade_code is required")
        if not self.description:
            errors.append("description is required")
        return errors

    def to_dict(self) -> dict:
        return {
            "trade_code": self.trade_code,
            "trade_name": self.trade_name,
            "description": self.description,
            "unit": self.unit,
            "quantity": self.quantity,
            "unit_cost": self.unit_cost,
            "total": self.total(),
            "basis": self.basis,
            "ai_generated": self.ai_generated,
            "pm_confirmed": self.pm_confirmed,
        }


@dataclass
class ROMBudgetOutput:
    instance_id: int
    project_id: int
    project_type: str
    gross_sf: float
    line_items: list[ROMLineItem] = field(default_factory=list)
    contingency_pct: float = 0.10

    def subtotal(self) -> float:
        return round(sum(item.total() for item in self.line_items), 2)

    def contingency_amount(self) -> float:
        return round(self.subtotal() * self.contingency_pct, 2)

    def total_estimated_cost(self) -> float:
        return round(self.subtotal() + self.contingency_amount(), 2)

    def cost_per_sf(self) -> float:
        if self.gross_sf:
            return round(self.total_estimated_cost() / self.gross_sf, 2)
        return 0.0

    def requires_buck_review(self) -> bool:
        return self.total_estimated_cost() > BUCK_ROM_REVIEW_THRESHOLD

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "project_type": self.project_type,
            "gross_sf": self.gross_sf,
            "line_items": [i.to_dict() for i in self.line_items],
            "subtotal": self.subtotal(),
            "contingency_pct": self.contingency_pct,
            "contingency_amount": self.contingency_amount(),
            "total_estimated_cost": self.total_estimated_cost(),
            "cost_per_sf": self.cost_per_sf(),
            "requires_buck_review": self.requires_buck_review(),
        }


class SOP07Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    OPTIONAL_INPUT_KEYS = OPTIONAL_INPUT_KEYS
    BUCK_ROM_REVIEW_THRESHOLD = BUCK_ROM_REVIEW_THRESHOLD
    CONTINGENCY_DEFAULTS = CONTINGENCY_DEFAULTS
    COST_BASIS_TYPES = COST_BASIS_TYPES
