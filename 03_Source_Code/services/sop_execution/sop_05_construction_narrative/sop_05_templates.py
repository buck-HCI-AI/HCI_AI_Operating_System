"""SOP 05 — Layer 4: Construction Narrative data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "project_id",
    "sop_04_instance_id",
    "project_type",
    "plan_issue_date",
]

INPUT_LABELS = {
    "project_id":         "Project ID",
    "sop_04_instance_id": "SOP 04 Plan Review — Completed instance ID",
    "project_type":       "Project type",
    "plan_issue_date":    "Plan issue date used for plan review",
}


@dataclass
class NarrativeSection:
    trade_code: str
    trade_name: str
    narrative_text: str = ""
    inclusions: list[str] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)
    allowances_noted: list[str] = field(default_factory=list)
    ai_drafted: bool = False
    pm_confirmed: bool = False
    pm_notes: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.trade_code:
            errors.append("trade_code is required")
        if not self.trade_name:
            errors.append("trade_name is required")
        if not self.narrative_text:
            errors.append("narrative_text is required")
        return errors

    def to_dict(self) -> dict:
        return {
            "trade_code": self.trade_code,
            "trade_name": self.trade_name,
            "narrative_text": self.narrative_text,
            "inclusions": self.inclusions,
            "exclusions": self.exclusions,
            "allowances_noted": self.allowances_noted,
            "ai_drafted": self.ai_drafted,
            "pm_confirmed": self.pm_confirmed,
            "pm_notes": self.pm_notes,
        }


@dataclass
class NarrativeOutput:
    instance_id: int
    project_id: int
    sections: list[NarrativeSection] = field(default_factory=list)

    def is_complete(self) -> bool:
        return all(s.pm_confirmed for s in self.sections)

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "sections": [s.to_dict() for s in self.sections],
            "section_count": len(self.sections),
            "all_confirmed": self.is_complete(),
        }


class SOP05Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
