"""SOP 28 — QC Detail Card: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = ["project_id", "trade_code", "trade_name", "sop_27_instance_id"]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "trade_code":          "CSI trade code",
    "trade_name":          "Trade name",
    "sop_27_instance_id":  "SOP 27 Quality Control — instance ID",
}

HOLD_POINT_STATUS = ["OPEN", "NOTIFIED", "INSPECTED", "CLEARED", "WAIVED"]


@dataclass
class QCDetailWorkItem:
    work_item_code: str
    description: str
    specification_ref: str
    acceptance_criteria: str
    hold_point: bool = False
    hold_point_status: str = "OPEN"
    inspection_method: str = ""
    frequency: str = ""
    responsible_party: str = "Superintendent"
    ai_drafted: bool = False
    pm_confirmed: bool = False

    def validate(self) -> list[str]:
        errors = []
        if not self.work_item_code:
            errors.append("work_item_code required")
        if self.hold_point and self.hold_point_status not in HOLD_POINT_STATUS:
            errors.append(f"hold_point_status must be one of {HOLD_POINT_STATUS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "work_item_code": self.work_item_code,
            "description": self.description,
            "specification_ref": self.specification_ref,
            "acceptance_criteria": self.acceptance_criteria,
            "hold_point": self.hold_point,
            "hold_point_status": self.hold_point_status,
            "inspection_method": self.inspection_method,
            "frequency": self.frequency,
            "responsible_party": self.responsible_party,
            "ai_drafted": self.ai_drafted,
            "pm_confirmed": self.pm_confirmed,
        }


@dataclass
class QCDetailCard:
    trade_code: str
    trade_name: str
    specification_sections: list[str] = field(default_factory=list)
    work_items: list[QCDetailWorkItem] = field(default_factory=list)

    def open_hold_points(self) -> list[QCDetailWorkItem]:
        return [w for w in self.work_items
                if w.hold_point and w.hold_point_status == "OPEN"]

    def confirmed_count(self) -> int:
        return sum(1 for w in self.work_items if w.pm_confirmed)


class SOP28Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    HOLD_POINT_STATUS = HOLD_POINT_STATUS
