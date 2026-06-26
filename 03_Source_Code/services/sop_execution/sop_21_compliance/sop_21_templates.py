"""SOP 21 — Compliance: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = [
    "project_id", "project_type", "jurisdiction", "sop_20_instance_id",
]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "project_type":        "Project type",
    "jurisdiction":        "AHJ / jurisdiction name",
    "sop_20_instance_id":  "SOP 20 Contract Setup — completed instance ID",
}

COMPLIANCE_CATEGORIES = [
    "building_permit", "electrical_permit", "mechanical_permit", "plumbing_permit",
    "fire_permit", "grading_permit", "encroachment_permit",
    "prevailing_wage", "certified_payroll", "apprenticeship_ratio",
    "davis_bacon", "dir_registration", "contractor_license",
    "ahj_pre_construction", "utility_coordination",
]

COMPLIANCE_STATUS = ["REQUIRED", "APPLIED", "APPROVED", "POSTED", "INSPECTED", "CLOSED", "NOT_REQUIRED"]


@dataclass
class ComplianceItem:
    item_code: str
    category: str
    description: str
    issuing_authority: str
    required_by_date: str
    responsible_party: str = "PM"
    status: str = "REQUIRED"
    permit_number: str = ""
    expiry_date: str = ""
    ai_identified: bool = False
    pm_confirmed: bool = False
    notes: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.item_code:
            errors.append("item_code required")
        if self.category not in COMPLIANCE_CATEGORIES:
            errors.append(f"category must be one of {COMPLIANCE_CATEGORIES}")
        if self.status not in COMPLIANCE_STATUS:
            errors.append(f"status must be one of {COMPLIANCE_STATUS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "item_code": self.item_code,
            "category": self.category,
            "description": self.description,
            "issuing_authority": self.issuing_authority,
            "required_by_date": self.required_by_date,
            "responsible_party": self.responsible_party,
            "status": self.status,
            "permit_number": self.permit_number,
            "expiry_date": self.expiry_date,
            "ai_identified": self.ai_identified,
            "pm_confirmed": self.pm_confirmed,
            "notes": self.notes,
        }


@dataclass
class ComplianceOutput:
    items: list[ComplianceItem] = field(default_factory=list)

    def open_items(self) -> list[ComplianceItem]:
        return [i for i in self.items
                if i.status not in ("CLOSED", "NOT_REQUIRED")]

    def overdue_items(self, today: str) -> list[ComplianceItem]:
        return [i for i in self.items
                if i.status == "REQUIRED" and i.required_by_date < today]

    def is_clear_to_build(self) -> bool:
        critical = [i for i in self.items
                    if i.category in ("building_permit", "contractor_license")
                    and i.status not in ("APPROVED", "POSTED", "NOT_REQUIRED")]
        return len(critical) == 0


class SOP21Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    COMPLIANCE_CATEGORIES = COMPLIANCE_CATEGORIES
    COMPLIANCE_STATUS = COMPLIANCE_STATUS
