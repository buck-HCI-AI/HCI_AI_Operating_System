"""SOP 08 — Layer 4: Historical Cost Database data fields."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "project_id",
    "trade_code",
    "work_description",
    "project_type",
]

INPUT_LABELS = {
    "project_id":       "Project ID",
    "trade_code":       "CSI trade code",
    "work_description": "Description of the work to price",
    "project_type":     "Project type for historical comparison",
}


@dataclass
class CostRecord:
    trade_code: str
    description: str
    unit: str
    unit_cost: float
    project_type: str
    year: int = 0
    source_project_id: int | None = None
    source: str = "hci_historical"  # hci_historical, rsmeans, ai_estimate
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "trade_code": self.trade_code,
            "description": self.description,
            "unit": self.unit,
            "unit_cost": self.unit_cost,
            "project_type": self.project_type,
            "year": self.year,
            "source": self.source,
            "notes": self.notes,
        }


@dataclass
class CostQueryResult:
    trade_code: str
    work_description: str
    project_type: str
    matching_records: list[CostRecord] = field(default_factory=list)
    ai_estimate: float | None = None
    avg_unit_cost: float | None = None
    min_unit_cost: float | None = None
    max_unit_cost: float | None = None
    confidence: str = "LOW"   # HIGH, MEDIUM, LOW
    ai_note: str = ""

    def to_dict(self) -> dict:
        return {
            "trade_code": self.trade_code,
            "work_description": self.work_description,
            "project_type": self.project_type,
            "record_count": len(self.matching_records),
            "avg_unit_cost": self.avg_unit_cost,
            "min_unit_cost": self.min_unit_cost,
            "max_unit_cost": self.max_unit_cost,
            "ai_estimate": self.ai_estimate,
            "confidence": self.confidence,
            "ai_note": self.ai_note,
        }


class SOP08Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
