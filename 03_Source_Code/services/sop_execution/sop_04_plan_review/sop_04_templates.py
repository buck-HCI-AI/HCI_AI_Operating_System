"""SOP 04 — Layer 4: Plan Review data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "project_id",
    "plan_set_file",
    "plan_issue_date",
    "project_type",
]

INPUT_LABELS = {
    "project_id":      "Project ID",
    "plan_set_file":   "Plan set file (Drive path or MinIO key)",
    "plan_issue_date": "Plan issue date (ISO date string)",
    "project_type":    "Project type (commercial, residential, renovation, mixed-use)",
}

OPTIONAL_INPUT_KEYS = ["plan_source", "spec_file", "addendum_files"]


@dataclass
class PlanSection:
    trade_code: str
    trade_name: str
    page_refs: list[str] = field(default_factory=list)
    scope_notes: str = ""
    gaps_found: list[str] = field(default_factory=list)
    conflicts_found: list[str] = field(default_factory=list)
    constructibility_issues: list[str] = field(default_factory=list)
    ai_reviewed: bool = False
    pm_confirmed: bool = False

    def validate(self) -> list[str]:
        errors = []
        if not self.trade_code:
            errors.append("trade_code is required")
        if not self.trade_name:
            errors.append("trade_name is required")
        return errors

    def to_dict(self) -> dict:
        return {
            "trade_code": self.trade_code,
            "trade_name": self.trade_name,
            "page_refs": self.page_refs,
            "scope_notes": self.scope_notes,
            "gaps_found": self.gaps_found,
            "conflicts_found": self.conflicts_found,
            "constructibility_issues": self.constructibility_issues,
            "ai_reviewed": self.ai_reviewed,
            "pm_confirmed": self.pm_confirmed,
        }


@dataclass
class PlanReviewOutput:
    instance_id: int
    project_id: int
    sections: list[PlanSection] = field(default_factory=list)

    def total_gaps(self) -> int:
        return sum(len(s.gaps_found) for s in self.sections)

    def total_conflicts(self) -> int:
        return sum(len(s.conflicts_found) for s in self.sections)

    def total_constructibility_issues(self) -> int:
        return sum(len(s.constructibility_issues) for s in self.sections)

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "sections": [s.to_dict() for s in self.sections],
            "total_gaps": self.total_gaps(),
            "total_conflicts": self.total_conflicts(),
            "total_constructibility_issues": self.total_constructibility_issues(),
        }


class SOP04Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    OPTIONAL_INPUT_KEYS = OPTIONAL_INPUT_KEYS
