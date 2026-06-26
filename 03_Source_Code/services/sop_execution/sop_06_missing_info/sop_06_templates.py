"""SOP 06 — Layer 4: Missing Information / Risk Log data fields."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "project_id",
    "sop_05_instance_id",
]

INPUT_LABELS = {
    "project_id":         "Project ID",
    "sop_05_instance_id": "SOP 05 Construction Narrative — Completed instance ID",
}

PRIORITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
RISK_PROBABILITIES = ["HIGH", "MEDIUM", "LOW"]
RISK_IMPACTS = ["HIGH", "MEDIUM", "LOW"]


@dataclass
class MissingInfoItem:
    item_code: str
    description: str
    source: str = ""          # where the gap was found (plan section, SOP 04, etc.)
    responsible_party: str = ""  # who must provide the info
    due_date: str = ""
    priority: str = "MEDIUM"
    resolved: bool = False
    resolution_note: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.item_code:
            errors.append("item_code is required")
        if not self.description:
            errors.append("description is required")
        if self.priority not in PRIORITY_LEVELS:
            errors.append(f"priority must be one of {PRIORITY_LEVELS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "item_code": self.item_code,
            "description": self.description,
            "source": self.source,
            "responsible_party": self.responsible_party,
            "due_date": self.due_date,
            "priority": self.priority,
            "resolved": self.resolved,
            "resolution_note": self.resolution_note,
        }


@dataclass
class RiskItem:
    risk_code: str
    description: str
    probability: str = "MEDIUM"
    impact: str = "MEDIUM"
    risk_score: str = "MEDIUM"  # derived from probability × impact
    mitigation: str = ""
    owner: str = ""
    ai_flagged: bool = False
    pm_confirmed: bool = False

    def calculate_score(self) -> str:
        matrix = {
            ("HIGH", "HIGH"): "CRITICAL",
            ("HIGH", "MEDIUM"): "HIGH",
            ("MEDIUM", "HIGH"): "HIGH",
            ("HIGH", "LOW"): "MEDIUM",
            ("LOW", "HIGH"): "MEDIUM",
            ("MEDIUM", "MEDIUM"): "MEDIUM",
            ("LOW", "MEDIUM"): "LOW",
            ("MEDIUM", "LOW"): "LOW",
            ("LOW", "LOW"): "LOW",
        }
        return matrix.get((self.probability, self.impact), "MEDIUM")

    def to_dict(self) -> dict:
        return {
            "risk_code": self.risk_code,
            "description": self.description,
            "probability": self.probability,
            "impact": self.impact,
            "risk_score": self.calculate_score(),
            "mitigation": self.mitigation,
            "owner": self.owner,
            "ai_flagged": self.ai_flagged,
            "pm_confirmed": self.pm_confirmed,
        }


@dataclass
class MissingInfoOutput:
    instance_id: int
    project_id: int
    missing_items: list[MissingInfoItem] = field(default_factory=list)
    risks: list[RiskItem] = field(default_factory=list)

    def open_critical(self) -> list[MissingInfoItem]:
        return [i for i in self.missing_items
                if i.priority == "CRITICAL" and not i.resolved]

    def high_risks(self) -> list[RiskItem]:
        return [r for r in self.risks if r.calculate_score() in ("CRITICAL", "HIGH")]

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "missing_items": [i.to_dict() for i in self.missing_items],
            "risks": [r.to_dict() for r in self.risks],
            "open_critical_count": len(self.open_critical()),
            "high_risk_count": len(self.high_risks()),
        }


class SOP06Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    PRIORITY_LEVELS = PRIORITY_LEVELS
