"""SOP 11 — Layer 4: Data field definitions and template validators."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date


REQUIRED_INPUT_KEYS = [
    "arch_drawings",
    "structural_drawings",
    "mep_drawings",
    "project_specifications",
    "soils_report",
    "hazmat_assessment",
    "sop04_approved",
    "sop05_complete",
    "sop06_reviewed",
    "sop10_defined",
    "sop09_approved",
]

OPTIONAL_INPUT_KEYS = ["bid_form_required", "prevailing_wage", "bond_required"]

INPUT_LABELS = {
    "arch_drawings":         "Architectural drawings (current revision)",
    "structural_drawings":   "Structural drawings (or N/A)",
    "mep_drawings":          "MEP drawings (or N/A)",
    "project_specifications":"Project specifications — all applicable divisions",
    "soils_report":          "Soils report (or N/A)",
    "hazmat_assessment":     "Hazmat assessment (or N/A)",
    "sop04_approved":        "SOP 04 Plan Review — Approved",
    "sop05_complete":        "SOP 05 Construction Narrative — Complete",
    "sop06_reviewed":        "SOP 06 Risk Log — Reviewed",
    "sop10_defined":         "SOP 10 Allowances/Alternates — Defined",
    "sop09_approved":        "SOP 09 Budget — Approved",
}


@dataclass
class ScopeSection:
    trade_code: str
    trade_name: str
    scope_text: str
    drawing_refs: list[str] = field(default_factory=list)
    spec_refs: list[str] = field(default_factory=list)
    allowances: list[dict] = field(default_factory=list)
    alternates: list[dict] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)
    bid_bond_required: bool = False
    ai_gap_flags: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "trade_code": self.trade_code,
            "trade_name": self.trade_name,
            "scope_text": self.scope_text,
            "drawing_refs": self.drawing_refs,
            "spec_refs": self.spec_refs,
            "allowances": self.allowances,
            "alternates": self.alternates,
            "exclusions": self.exclusions,
            "bid_bond_required": self.bid_bond_required,
            "ai_gap_flags": self.ai_gap_flags,
        }

    def validate(self) -> list[str]:
        errors = []
        if not self.scope_text or len(self.scope_text) < 50:
            errors.append(f"{self.trade_name}: scope_text too short — must be specific (≥ 50 chars)")
        if not self.drawing_refs:
            errors.append(f"{self.trade_name}: no drawing references")
        if not self.spec_refs:
            errors.append(f"{self.trade_name}: no spec references")
        return errors


@dataclass
class BidPackageOutput:
    instance_id: int
    project_id: int
    scope_sections: list[ScopeSection]
    contract_documents: list[dict]
    sub_invite_list: list[dict]
    gap_report: list[dict]
    risk_flags: list[dict]
    bid_due_date: date | None = None
    issue_date: date | None = None
    file_path: str | None = None

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "scope_sections": [s.to_dict() for s in self.scope_sections],
            "contract_documents": self.contract_documents,
            "sub_invite_list": self.sub_invite_list,
            "gap_report": self.gap_report,
            "risk_flags": self.risk_flags,
            "bid_due_date": str(self.bid_due_date) if self.bid_due_date else None,
            "issue_date": str(self.issue_date) if self.issue_date else None,
        }


class SOP11Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    OPTIONAL_INPUT_KEYS = OPTIONAL_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
