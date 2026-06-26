"""SOP 09 — Layer 4: Budget Review data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "project_id",
    "sop_07_instance_id",
    "project_type",
]

INPUT_LABELS = {
    "project_id":         "Project ID",
    "sop_07_instance_id": "SOP 07 ROM Budget — Completed instance ID",
    "project_type":       "Project type",
}

OPTIONAL_INPUT_KEYS = ["owner_budget_target", "budget_file", "design_phase"]

BUDGET_VARIANCE_ALERT_PCT = 0.10   # 10% over ROM triggers escalation note
BUCK_BUDGET_REVIEW_THRESHOLD = 500_000.00  # Budgets > $500k require Buck approval
REVIEW_OUTCOMES = ["APPROVED", "REVISION_REQUIRED", "HOLD_PENDING_DESIGN", "REJECTED"]


@dataclass
class BudgetLineItem:
    trade_code: str
    trade_name: str
    description: str
    rom_amount: float
    revised_amount: float = 0.0
    basis: str = ""
    pm_notes: str = ""

    def variance(self) -> float:
        base = self.revised_amount if self.revised_amount else self.rom_amount
        return round(base - self.rom_amount, 2)

    def variance_pct(self) -> float:
        if self.rom_amount:
            return round(self.variance() / self.rom_amount * 100, 1)
        return 0.0

    def to_dict(self) -> dict:
        return {
            "trade_code": self.trade_code,
            "trade_name": self.trade_name,
            "description": self.description,
            "rom_amount": self.rom_amount,
            "revised_amount": self.revised_amount if self.revised_amount else self.rom_amount,
            "variance": self.variance(),
            "variance_pct": self.variance_pct(),
            "basis": self.basis,
        }


@dataclass
class BudgetReviewOutput:
    instance_id: int
    project_id: int
    project_type: str
    line_items: list[BudgetLineItem] = field(default_factory=list)
    owner_budget_target: float | None = None
    outcome: str = ""
    approved_by: str = ""
    conditions: str = ""

    def rom_total(self) -> float:
        return round(sum(i.rom_amount for i in self.line_items), 2)

    def revised_total(self) -> float:
        return round(sum(
            (i.revised_amount if i.revised_amount else i.rom_amount)
            for i in self.line_items
        ), 2)

    def variance_pct(self) -> float:
        if self.rom_total():
            return round((self.revised_total() - self.rom_total()) / self.rom_total() * 100, 1)
        return 0.0

    def within_tolerance(self) -> bool:
        return abs(self.variance_pct()) <= BUDGET_VARIANCE_ALERT_PCT * 100

    def requires_buck_approval(self) -> bool:
        return self.revised_total() > BUCK_BUDGET_REVIEW_THRESHOLD

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "project_type": self.project_type,
            "rom_total": self.rom_total(),
            "revised_total": self.revised_total(),
            "variance_pct": self.variance_pct(),
            "within_tolerance": self.within_tolerance(),
            "owner_budget_target": self.owner_budget_target,
            "outcome": self.outcome,
            "approved_by": self.approved_by,
            "requires_buck_approval": self.requires_buck_approval(),
        }


class SOP09Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    OPTIONAL_INPUT_KEYS = OPTIONAL_INPUT_KEYS
    BUCK_BUDGET_REVIEW_THRESHOLD = BUCK_BUDGET_REVIEW_THRESHOLD
    BUDGET_VARIANCE_ALERT_PCT = BUDGET_VARIANCE_ALERT_PCT
    REVIEW_OUTCOMES = REVIEW_OUTCOMES
