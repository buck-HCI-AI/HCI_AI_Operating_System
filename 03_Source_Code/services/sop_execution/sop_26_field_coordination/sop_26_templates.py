"""SOP 26 — Field Coordination: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = ["project_id", "sop_23_instance_id"]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "sop_23_instance_id":  "SOP 23 Project Startup — completed instance ID",
}

COORD_TYPES = ["RFI", "SUBMITTAL", "COORDINATION_ISSUE", "TRADE_CONFLICT", "DESIGN_CLARIFICATION", "OWNER_REQUEST"]
COORD_STATUS = ["OPEN", "IN_REVIEW", "RESPONDED", "CLOSED", "ESCALATED"]
COORD_PRIORITY = ["ROUTINE", "URGENT", "CRITICAL"]


@dataclass
class FieldCoordItem:
    item_code: str
    coord_type: str
    description: str
    submitted_by: str = ""
    assigned_to: str = ""
    date_opened: str = ""
    priority: str = "ROUTINE"
    status: str = "OPEN"
    date_required: str = ""
    date_closed: str = ""
    response: str = ""
    drawing_refs: list[str] = field(default_factory=list)
    spec_refs: list[str] = field(default_factory=list)
    cost_impact: bool = False
    schedule_impact: bool = False
    ai_drafted_response: bool = False
    pm_confirmed: bool = False

    def validate(self) -> list[str]:
        errors = []
        if not self.item_code:
            errors.append("item_code required")
        if self.coord_type not in COORD_TYPES:
            errors.append(f"coord_type must be one of {COORD_TYPES}")
        if self.status not in COORD_STATUS:
            errors.append(f"status must be one of {COORD_STATUS}")
        if self.priority not in COORD_PRIORITY:
            errors.append(f"priority must be one of {COORD_PRIORITY}")
        return errors

    def to_dict(self) -> dict:
        return {
            "item_code": self.item_code,
            "coord_type": self.coord_type,
            "description": self.description,
            "submitted_by": self.submitted_by,
            "assigned_to": self.assigned_to,
            "date_opened": self.date_opened,
            "priority": self.priority,
            "status": self.status,
            "date_required": self.date_required,
            "date_closed": self.date_closed,
            "response": self.response,
            "drawing_refs": self.drawing_refs,
            "spec_refs": self.spec_refs,
            "cost_impact": self.cost_impact,
            "schedule_impact": self.schedule_impact,
            "ai_drafted_response": self.ai_drafted_response,
            "pm_confirmed": self.pm_confirmed,
        }


@dataclass
class FieldCoordOutput:
    items: list[FieldCoordItem] = field(default_factory=list)

    def open_critical(self) -> list[FieldCoordItem]:
        return [i for i in self.items
                if i.status == "OPEN" and i.priority == "CRITICAL"]

    def overdue(self, today: str) -> list[FieldCoordItem]:
        return [i for i in self.items
                if i.status in ("OPEN", "IN_REVIEW")
                and i.date_required and i.date_required < today]


class SOP26Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    COORD_TYPES = COORD_TYPES
    COORD_STATUS = COORD_STATUS
    COORD_PRIORITY = COORD_PRIORITY
