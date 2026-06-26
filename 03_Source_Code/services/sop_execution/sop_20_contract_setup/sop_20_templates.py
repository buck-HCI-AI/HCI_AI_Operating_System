"""SOP 20 — Contract Setup: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = [
    "project_id", "project_name", "contract_type", "owner_name",
    "gc_contract_value", "sop_19_instance_id",
]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "project_name":        "Project name",
    "contract_type":       "Prime contract type (GMP/lump_sum/cost_plus/unit_price)",
    "owner_name":          "Owner / client name",
    "gc_contract_value":   "Prime contract value ($)",
    "sop_19_instance_id":  "SOP 19 Subcontract Agreement — completed instance ID (first sub, or N/A)",
}

CONTRACT_TYPES = ["GMP", "lump_sum", "cost_plus", "unit_price", "time_and_material"]

SETUP_ITEM_CATEGORIES = [
    "prime_contract", "subcontract", "insurance", "bonds",
    "permits", "schedule_of_values", "billing_procedures",
    "change_order_procedures", "lien_rights", "owner_requirements",
]

SETUP_ITEM_STATUS = ["PENDING", "IN_PROGRESS", "COMPLETE", "WAIVED"]


@dataclass
class ContractSetupItem:
    item_code: str
    category: str
    description: str
    responsible_party: str
    due_date: str
    status: str = "PENDING"
    document_ref: str = ""
    ai_flagged: bool = False
    pm_confirmed: bool = False
    notes: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.item_code:
            errors.append("item_code required")
        if self.category not in SETUP_ITEM_CATEGORIES:
            errors.append(f"category must be one of {SETUP_ITEM_CATEGORIES}")
        if self.status not in SETUP_ITEM_STATUS:
            errors.append(f"status must be one of {SETUP_ITEM_STATUS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "item_code": self.item_code,
            "category": self.category,
            "description": self.description,
            "responsible_party": self.responsible_party,
            "due_date": self.due_date,
            "status": self.status,
            "document_ref": self.document_ref,
            "ai_flagged": self.ai_flagged,
            "pm_confirmed": self.pm_confirmed,
            "notes": self.notes,
        }


@dataclass
class ContractSetupOutput:
    items: list[ContractSetupItem] = field(default_factory=list)

    def pending_items(self) -> list[ContractSetupItem]:
        return [i for i in self.items if i.status == "PENDING"]

    def flagged_items(self) -> list[ContractSetupItem]:
        return [i for i in self.items if i.ai_flagged]

    def is_complete(self) -> bool:
        return all(i.status in ("COMPLETE", "WAIVED") for i in self.items)


class SOP20Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    CONTRACT_TYPES = CONTRACT_TYPES
    SETUP_ITEM_CATEGORIES = SETUP_ITEM_CATEGORIES
