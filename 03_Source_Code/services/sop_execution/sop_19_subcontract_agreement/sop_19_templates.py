"""SOP 19 — Layer 4: Subcontract Agreement data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "project_id",
    "sop_16_instance_id",
    "awarded_sub",
    "award_amount",
    "scope_basis",
    "trade_name",
    "trade_code",
]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "sop_16_instance_id":  "SOP 16 Buyout — Completed instance ID (Gate 16-C required)",
    "awarded_sub":         "Awarded subcontractor name",
    "award_amount":        "Contract sum ($) from Gate 15-C / Gate 16-C",
    "scope_basis":         "Scope basis statement confirmed in SOP 16",
    "trade_name":          "Trade name",
    "trade_code":          "CSI trade code",
}

CONTRACT_SECTIONS = [
    "scope_of_work",
    "contract_sum",
    "payment_terms",
    "schedule_of_work",
    "insurance_requirements",
    "general_conditions",
    "special_conditions",
]

HCI_INSURANCE_MINIMUMS = {
    "general_liability": 1_000_000,      # per occurrence
    "aggregate": 2_000_000,
    "workers_comp": 1_000_000,
    "auto_liability": 1_000_000,
}

EXECUTION_AUTHORITY = "Principal or PM with written delegation"


@dataclass
class SubcontractSection:
    section_type: str
    content: str = ""
    ai_drafted: bool = False
    pm_confirmed: bool = False
    issues_flagged: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors = []
        if self.section_type not in CONTRACT_SECTIONS:
            errors.append(f"section_type must be one of {CONTRACT_SECTIONS}")
        if not self.content:
            errors.append("content is required")
        return errors

    def to_dict(self) -> dict:
        return {
            "section_type": self.section_type,
            "content": self.content,
            "ai_drafted": self.ai_drafted,
            "pm_confirmed": self.pm_confirmed,
            "issues_flagged": self.issues_flagged,
        }


@dataclass
class SubcontractRecord:
    instance_id: int
    project_id: int
    awarded_sub: str
    trade_name: str
    trade_code: str
    award_amount: float
    sections: list[SubcontractSection] = field(default_factory=list)
    executed: bool = False
    execution_date: str = ""
    execution_authority: str = ""
    subcontract_number: str = ""

    def all_sections_confirmed(self) -> bool:
        return (
            len(self.sections) >= len(CONTRACT_SECTIONS) and
            all(s.pm_confirmed for s in self.sections)
        )

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "awarded_sub": self.awarded_sub,
            "trade_name": self.trade_name,
            "award_amount": self.award_amount,
            "section_count": len(self.sections),
            "all_confirmed": self.all_sections_confirmed(),
            "executed": self.executed,
            "execution_date": self.execution_date,
            "subcontract_number": self.subcontract_number,
        }


class SOP19Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    CONTRACT_SECTIONS = CONTRACT_SECTIONS
    HCI_INSURANCE_MINIMUMS = HCI_INSURANCE_MINIMUMS
    EXECUTION_AUTHORITY = EXECUTION_AUTHORITY
