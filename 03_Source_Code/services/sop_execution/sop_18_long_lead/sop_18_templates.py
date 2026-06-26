"""SOP 18 — Long-Lead Item Procurement: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = [
    "project_id", "project_type", "construction_start",
    "sop_17_instance_id",
]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "project_type":        "Project type",
    "construction_start":  "Construction start date (YYYY-MM-DD)",
    "sop_17_instance_id":  "SOP 17 Project Schedule — completed instance ID",
}

LONG_LEAD_STATUS = ["IDENTIFIED", "RFQ_SENT", "ORDERED", "CONFIRMED", "RECEIVED", "DELAYED", "CANCELLED"]
LEAD_RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

TYPICAL_LONG_LEAD_ITEMS = [
    "elevator", "structural_steel", "mechanical_equipment", "electrical_switchgear",
    "curtain_wall", "custom_windows", "roofing_membrane", "specialty_doors",
    "generator", "fire_suppression_equipment",
]


@dataclass
class LongLeadItem:
    item_code: str
    description: str
    trade_code: str
    lead_time_weeks: int
    order_by_date: str
    required_on_site: str
    supplier: str = ""
    spec_section: str = ""
    estimated_cost: float = 0.0
    status: str = "IDENTIFIED"
    risk_level: str = "MEDIUM"
    ai_identified: bool = False
    pm_approved: bool = False
    notes: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.item_code:
            errors.append("item_code required")
        if self.lead_time_weeks < 1:
            errors.append("lead_time_weeks must be >= 1")
        if self.status not in LONG_LEAD_STATUS:
            errors.append(f"status must be one of {LONG_LEAD_STATUS}")
        if self.risk_level not in LEAD_RISK_LEVELS:
            errors.append(f"risk_level must be one of {LEAD_RISK_LEVELS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "item_code": self.item_code,
            "description": self.description,
            "trade_code": self.trade_code,
            "lead_time_weeks": self.lead_time_weeks,
            "order_by_date": self.order_by_date,
            "required_on_site": self.required_on_site,
            "supplier": self.supplier,
            "spec_section": self.spec_section,
            "estimated_cost": self.estimated_cost,
            "status": self.status,
            "risk_level": self.risk_level,
            "ai_identified": self.ai_identified,
            "pm_approved": self.pm_approved,
            "notes": self.notes,
        }


@dataclass
class LongLeadOutput:
    items: list[LongLeadItem] = field(default_factory=list)

    def critical_items(self) -> list[LongLeadItem]:
        return [i for i in self.items if i.risk_level == "CRITICAL"]

    def overdue_orders(self, today: str) -> list[LongLeadItem]:
        return [i for i in self.items
                if i.status == "IDENTIFIED" and i.order_by_date < today]

    def total_estimated_cost(self) -> float:
        return sum(i.estimated_cost for i in self.items)


class SOP18Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    LONG_LEAD_STATUS = LONG_LEAD_STATUS
    LEAD_RISK_LEVELS = LEAD_RISK_LEVELS
