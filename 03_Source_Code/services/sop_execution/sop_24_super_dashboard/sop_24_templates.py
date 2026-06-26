"""SOP 24 — Superintendent Daily Dashboard: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = [
    "project_id", "superintendent_name", "sop_23_instance_id",
]

INPUT_LABELS = {
    "project_id":           "Project ID",
    "superintendent_name":  "Superintendent name",
    "sop_23_instance_id":   "SOP 23 Project Startup — completed instance ID",
}

ALERT_LEVELS = ["GREEN", "YELLOW", "RED"]
METRIC_CATEGORIES = [
    "schedule", "safety", "quality", "manpower",
    "materials", "rfi", "weather", "budget",
]


@dataclass
class DashboardMetric:
    metric_code: str
    category: str
    label: str
    value: str
    threshold_warning: str = ""
    threshold_critical: str = ""
    alert_level: str = "GREEN"
    date: str = ""
    notes: str = ""

    def validate(self) -> list[str]:
        errors = []
        if not self.metric_code:
            errors.append("metric_code required")
        if self.category not in METRIC_CATEGORIES:
            errors.append(f"category must be one of {METRIC_CATEGORIES}")
        if self.alert_level not in ALERT_LEVELS:
            errors.append(f"alert_level must be one of {ALERT_LEVELS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "metric_code": self.metric_code,
            "category": self.category,
            "label": self.label,
            "value": self.value,
            "threshold_warning": self.threshold_warning,
            "threshold_critical": self.threshold_critical,
            "alert_level": self.alert_level,
            "date": self.date,
            "notes": self.notes,
        }


@dataclass
class DashboardSnapshot:
    date: str
    metrics: list[DashboardMetric] = field(default_factory=list)
    ai_brief: str = ""
    alerts: list[str] = field(default_factory=list)

    def red_metrics(self) -> list[DashboardMetric]:
        return [m for m in self.metrics if m.alert_level == "RED"]

    def yellow_metrics(self) -> list[DashboardMetric]:
        return [m for m in self.metrics if m.alert_level == "YELLOW"]

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "metrics": [m.to_dict() for m in self.metrics],
            "ai_brief": self.ai_brief,
            "alerts": self.alerts,
            "red_count": len(self.red_metrics()),
            "yellow_count": len(self.yellow_metrics()),
        }


class SOP24Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    ALERT_LEVELS = ALERT_LEVELS
    METRIC_CATEGORIES = METRIC_CATEGORIES
