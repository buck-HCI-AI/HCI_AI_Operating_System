"""SOP 23 — Project Startup: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = [
    "project_id", "project_name", "project_type",
    "superintendent_name", "construction_start",
    "sop_22_instance_id",
]

INPUT_LABELS = {
    "project_id":           "Project ID",
    "project_name":         "Project name",
    "project_type":         "Project type",
    "superintendent_name":  "Assigned superintendent name",
    "construction_start":   "Construction start date (YYYY-MM-DD)",
    "sop_22_instance_id":   "SOP 22 COI/W-9/Lien — completed instance ID",
}

STARTUP_CATEGORIES = [
    "personnel", "site_setup", "safety", "documents",
    "equipment", "utilities", "communication", "subcontractor",
]

STARTUP_STATUS = ["PENDING", "IN_PROGRESS", "COMPLETE", "WAIVED"]


@dataclass
class StartupItem:
    item_code: str
    category: str
    description: str
    responsible_party: str
    due_by: str
    status: str = "PENDING"
    ai_generated: bool = False
    pm_confirmed: bool = False
    notes: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.item_code:
            errors.append("item_code required")
        if self.category not in STARTUP_CATEGORIES:
            errors.append(f"category must be one of {STARTUP_CATEGORIES}")
        if self.status not in STARTUP_STATUS:
            errors.append(f"status must be one of {STARTUP_STATUS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "item_code": self.item_code,
            "category": self.category,
            "description": self.description,
            "responsible_party": self.responsible_party,
            "due_by": self.due_by,
            "status": self.status,
            "ai_generated": self.ai_generated,
            "pm_confirmed": self.pm_confirmed,
            "notes": self.notes,
        }


@dataclass
class StartupOutput:
    items: list[StartupItem] = field(default_factory=list)

    def incomplete_items(self) -> list[StartupItem]:
        return [i for i in self.items
                if i.status not in ("COMPLETE", "WAIVED")]

    def by_category(self, category: str) -> list[StartupItem]:
        return [i for i in self.items if i.category == category]

    def ready_to_build(self) -> bool:
        critical = [i for i in self.items
                    if i.category in ("safety", "personnel", "documents")
                    and i.status == "PENDING"]
        return len(critical) == 0


class SOP23Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    STARTUP_CATEGORIES = STARTUP_CATEGORIES
    STARTUP_STATUS = STARTUP_STATUS
