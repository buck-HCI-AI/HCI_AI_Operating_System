"""SOP 27 — Quality Control: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = ["project_id", "project_type", "sop_23_instance_id"]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "project_type":        "Project type",
    "sop_23_instance_id":  "SOP 23 Project Startup — completed instance ID",
}

QC_RESULTS = ["PASS", "FAIL", "CONDITIONAL", "NOT_INSPECTED"]
QC_SEVERITY = ["MINOR", "MAJOR", "CRITICAL"]
QC_CATEGORIES = [
    "concrete", "structural", "framing", "waterproofing", "roofing",
    "mep_rough", "mep_finish", "insulation", "drywall", "finishes",
    "exterior", "site_work", "fire_life_safety",
]


@dataclass
class QCInspectionItem:
    item_code: str
    category: str
    description: str
    specification_ref: str
    trade_code: str
    inspector: str
    inspection_date: str
    result: str = "NOT_INSPECTED"
    severity: str = "MINOR"
    deficiency_notes: str = ""
    corrective_action: str = ""
    corrected_date: str = ""
    re_inspection_required: bool = False
    ai_generated: bool = False
    pm_confirmed: bool = False
    photo_refs: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors = []
        if not self.item_code:
            errors.append("item_code required")
        if self.category not in QC_CATEGORIES:
            errors.append(f"category must be one of {QC_CATEGORIES}")
        if self.result not in QC_RESULTS:
            errors.append(f"result must be one of {QC_RESULTS}")
        if self.severity not in QC_SEVERITY:
            errors.append(f"severity must be one of {QC_SEVERITY}")
        return errors

    def to_dict(self) -> dict:
        return {
            "item_code": self.item_code,
            "category": self.category,
            "description": self.description,
            "specification_ref": self.specification_ref,
            "trade_code": self.trade_code,
            "inspector": self.inspector,
            "inspection_date": self.inspection_date,
            "result": self.result,
            "severity": self.severity,
            "deficiency_notes": self.deficiency_notes,
            "corrective_action": self.corrective_action,
            "corrected_date": self.corrected_date,
            "re_inspection_required": self.re_inspection_required,
            "ai_generated": self.ai_generated,
            "pm_confirmed": self.pm_confirmed,
            "photo_refs": self.photo_refs,
        }


@dataclass
class QCOutput:
    items: list[QCInspectionItem] = field(default_factory=list)

    def failures(self) -> list[QCInspectionItem]:
        return [i for i in self.items if i.result == "FAIL"]

    def critical_failures(self) -> list[QCInspectionItem]:
        return [i for i in self.items
                if i.result == "FAIL" and i.severity == "CRITICAL"]

    def open_re_inspections(self) -> list[QCInspectionItem]:
        return [i for i in self.items
                if i.re_inspection_required and not i.corrected_date]


class SOP27Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    QC_RESULTS = QC_RESULTS
    QC_SEVERITY = QC_SEVERITY
    QC_CATEGORIES = QC_CATEGORIES
