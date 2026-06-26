"""SOP 29 — Safety: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = ["project_id", "project_type", "superintendent_name", "sop_23_instance_id"]

INPUT_LABELS = {
    "project_id":           "Project ID",
    "project_type":         "Project type",
    "superintendent_name":  "Superintendent name (safety officer for field)",
    "sop_23_instance_id":   "SOP 23 Project Startup — completed instance ID",
}

HAZARD_CATEGORIES = [
    "fall_protection", "struck_by", "caught_in_between", "electrocution",
    "confined_space", "excavation", "fire", "chemical", "noise",
    "ergonomics", "heat_illness", "covid_protocol",
]

RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
HAZARD_STATUS = ["IDENTIFIED", "CONTROLLED", "ELIMINATED", "MONITORING"]


@dataclass
class SafetyHazard:
    hazard_code: str
    category: str
    description: str
    location: str
    risk_level: str
    controls: list[str] = field(default_factory=list)
    responsible_party: str = "Superintendent"
    status: str = "IDENTIFIED"
    date_identified: str = ""
    date_controlled: str = ""
    ai_identified: bool = False
    superintendent_confirmed: bool = False
    notes: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.hazard_code:
            errors.append("hazard_code required")
        if self.category not in HAZARD_CATEGORIES:
            errors.append(f"category must be one of {HAZARD_CATEGORIES}")
        if self.risk_level not in RISK_LEVELS:
            errors.append(f"risk_level must be one of {RISK_LEVELS}")
        if self.status not in HAZARD_STATUS:
            errors.append(f"status must be one of {HAZARD_STATUS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "hazard_code": self.hazard_code,
            "category": self.category,
            "description": self.description,
            "location": self.location,
            "risk_level": self.risk_level,
            "controls": self.controls,
            "responsible_party": self.responsible_party,
            "status": self.status,
            "date_identified": self.date_identified,
            "date_controlled": self.date_controlled,
            "ai_identified": self.ai_identified,
            "superintendent_confirmed": self.superintendent_confirmed,
            "notes": self.notes,
        }


@dataclass
class SafetyOutput:
    hazards: list[SafetyHazard] = field(default_factory=list)

    def critical_uncontrolled(self) -> list[SafetyHazard]:
        return [h for h in self.hazards
                if h.risk_level == "CRITICAL" and h.status == "IDENTIFIED"]

    def open_hazards(self) -> list[SafetyHazard]:
        return [h for h in self.hazards if h.status == "IDENTIFIED"]

    def is_safe_to_proceed(self) -> bool:
        return len(self.critical_uncontrolled()) == 0


class SOP29Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    HAZARD_CATEGORIES = HAZARD_CATEGORIES
    RISK_LEVELS = RISK_LEVELS
    HAZARD_STATUS = HAZARD_STATUS
