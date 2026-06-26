"""SOP 30 — Inspection: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = ["project_id", "jurisdiction", "sop_21_instance_id"]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "jurisdiction":        "AHJ / jurisdiction name",
    "sop_21_instance_id":  "SOP 21 Compliance — completed instance ID",
}

INSPECTION_TYPES = [
    "foundation", "rough_framing", "rough_electrical", "rough_plumbing",
    "rough_mechanical", "insulation", "drywall_nailing", "exterior_lath",
    "fire_sprinkler_rough", "fire_alarm_rough", "final_electrical",
    "final_plumbing", "final_mechanical", "final_building",
    "T24_energy", "special_inspection", "deputy_inspection",
]

INSPECTION_RESULTS = ["PASS", "FAIL", "PARTIAL", "CORRECTION_NOTICE", "PENDING", "SCHEDULED"]


@dataclass
class InspectionRecord:
    inspection_code: str
    inspection_type: str
    description: str
    permit_number: str
    inspector_name: str = ""
    inspector_agency: str = ""
    scheduled_date: str = ""
    inspection_date: str = ""
    result: str = "PENDING"
    correction_items: list[str] = field(default_factory=list)
    re_inspection_date: str = ""
    card_signed: bool = False
    superintendent: str = ""
    ai_prep_notes: str = ""
    pm_confirmed: bool = False

    def validate(self) -> list[str]:
        errors = []
        if not self.inspection_code:
            errors.append("inspection_code required")
        if self.inspection_type not in INSPECTION_TYPES:
            errors.append(f"inspection_type must be one of {INSPECTION_TYPES}")
        if self.result not in INSPECTION_RESULTS:
            errors.append(f"result must be one of {INSPECTION_RESULTS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "inspection_code": self.inspection_code,
            "inspection_type": self.inspection_type,
            "description": self.description,
            "permit_number": self.permit_number,
            "inspector_name": self.inspector_name,
            "inspector_agency": self.inspector_agency,
            "scheduled_date": self.scheduled_date,
            "inspection_date": self.inspection_date,
            "result": self.result,
            "correction_items": self.correction_items,
            "re_inspection_date": self.re_inspection_date,
            "card_signed": self.card_signed,
            "superintendent": self.superintendent,
            "ai_prep_notes": self.ai_prep_notes,
            "pm_confirmed": self.pm_confirmed,
        }


@dataclass
class InspectionOutput:
    records: list[InspectionRecord] = field(default_factory=list)

    def failed(self) -> list[InspectionRecord]:
        return [r for r in self.records if r.result in ("FAIL", "CORRECTION_NOTICE")]

    def pending(self) -> list[InspectionRecord]:
        return [r for r in self.records if r.result in ("PENDING", "SCHEDULED")]

    def all_passed(self) -> bool:
        required = [r for r in self.records if r.result != "PENDING"]
        return all(r.result == "PASS" for r in required)


class SOP30Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    INSPECTION_TYPES = INSPECTION_TYPES
    INSPECTION_RESULTS = INSPECTION_RESULTS
