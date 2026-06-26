"""SOP 17 — Project Schedule: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

REQUIRED_INPUT_KEYS = [
    "project_id", "project_name", "project_type",
    "construction_start", "substantial_completion",
    "sop_23_instance_id",
]

INPUT_LABELS = {
    "project_id":              "Project ID",
    "project_name":            "Project name",
    "project_type":            "Project type (commercial/residential/renovation/mixed-use)",
    "construction_start":      "Target construction start date (YYYY-MM-DD)",
    "substantial_completion":  "Target substantial completion date (YYYY-MM-DD)",
    "sop_23_instance_id":      "SOP 23 Project Startup — completed instance ID",
}

SCHEDULE_PHASES = [
    "preconstruction", "mobilization", "site_work", "foundations",
    "framing", "rough_mep", "exterior", "interior", "finishes",
    "punch_list", "closeout",
]

MILESTONE_STATUS = ["NOT_STARTED", "IN_PROGRESS", "COMPLETE", "DELAYED", "AT_RISK"]


@dataclass
class ScheduleMilestone:
    milestone_code: str
    phase: str
    description: str
    planned_start: str
    planned_finish: str
    duration_days: int = 0
    float_days: int = 0
    critical_path: bool = False
    predecessor_codes: list[str] = field(default_factory=list)
    trade_codes: list[str] = field(default_factory=list)
    status: str = "NOT_STARTED"
    ai_generated: bool = False
    pm_confirmed: bool = False

    def validate(self) -> list[str]:
        errors = []
        if not self.milestone_code:
            errors.append("milestone_code required")
        if self.phase not in SCHEDULE_PHASES:
            errors.append(f"phase must be one of {SCHEDULE_PHASES}")
        if self.status not in MILESTONE_STATUS:
            errors.append(f"status must be one of {MILESTONE_STATUS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "milestone_code": self.milestone_code,
            "phase": self.phase,
            "description": self.description,
            "planned_start": self.planned_start,
            "planned_finish": self.planned_finish,
            "duration_days": self.duration_days,
            "float_days": self.float_days,
            "critical_path": self.critical_path,
            "predecessor_codes": self.predecessor_codes,
            "trade_codes": self.trade_codes,
            "status": self.status,
            "ai_generated": self.ai_generated,
            "pm_confirmed": self.pm_confirmed,
        }


@dataclass
class ScheduleOutput:
    milestones: list[ScheduleMilestone] = field(default_factory=list)
    total_duration_days: int = 0
    critical_path_count: int = 0

    def critical_milestones(self) -> list[ScheduleMilestone]:
        return [m for m in self.milestones if m.critical_path]

    def delayed_milestones(self) -> list[ScheduleMilestone]:
        return [m for m in self.milestones if m.status == "DELAYED"]

    def confirmed_count(self) -> int:
        return sum(1 for m in self.milestones if m.pm_confirmed)


class SOP17Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    SCHEDULE_PHASES = SCHEDULE_PHASES
    MILESTONE_STATUS = MILESTONE_STATUS
