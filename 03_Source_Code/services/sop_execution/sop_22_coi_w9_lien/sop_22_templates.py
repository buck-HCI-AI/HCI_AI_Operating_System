"""SOP 22 — COI / W-9 / Lien Waiver: Layer 4 data fields and validators."""
from __future__ import annotations
from dataclasses import dataclass, field

REQUIRED_INPUT_KEYS = [
    "project_id", "sop_21_instance_id",
]

INPUT_LABELS = {
    "project_id":          "Project ID",
    "sop_21_instance_id":  "SOP 21 Compliance — completed instance ID",
}

DOC_TYPES = ["COI", "W9", "CONDITIONAL_LIEN_WAIVER", "UNCONDITIONAL_LIEN_WAIVER", "PRELIMINARY_NOTICE"]
DOC_STATUS = ["REQUESTED", "RECEIVED", "VERIFIED", "EXPIRED", "REJECTED"]

HCI_COI_MINIMUMS = {
    "general_liability": 1_000_000,
    "aggregate": 2_000_000,
    "workers_comp": 1_000_000,
    "auto_liability": 1_000_000,
}


@dataclass
class ComplianceDoc:
    doc_code: str
    doc_type: str
    party_name: str
    party_role: str
    issue_date: str = ""
    expiry_date: str = ""
    status: str = "REQUESTED"
    verified_by: str = ""
    deficiencies: list[str] = field(default_factory=list)
    ai_verified: bool = False
    file_ref: str = ""
    notes: str = ""

    def is_current(self, today: str) -> bool:
        if not self.expiry_date:
            return self.status == "VERIFIED"
        return self.status == "VERIFIED" and self.expiry_date >= today

    def validate(self) -> list[str]:
        errors = []
        if not self.doc_code:
            errors.append("doc_code required")
        if self.doc_type not in DOC_TYPES:
            errors.append(f"doc_type must be one of {DOC_TYPES}")
        if self.status not in DOC_STATUS:
            errors.append(f"status must be one of {DOC_STATUS}")
        return errors

    def to_dict(self) -> dict:
        return {
            "doc_code": self.doc_code,
            "doc_type": self.doc_type,
            "party_name": self.party_name,
            "party_role": self.party_role,
            "issue_date": self.issue_date,
            "expiry_date": self.expiry_date,
            "status": self.status,
            "verified_by": self.verified_by,
            "deficiencies": self.deficiencies,
            "ai_verified": self.ai_verified,
            "file_ref": self.file_ref,
            "notes": self.notes,
        }


@dataclass
class ComplianceDocOutput:
    docs: list[ComplianceDoc] = field(default_factory=list)

    def missing_or_expired(self, today: str) -> list[ComplianceDoc]:
        return [d for d in self.docs if not d.is_current(today)]

    def by_party(self, party_name: str) -> list[ComplianceDoc]:
        return [d for d in self.docs if d.party_name == party_name]

    def cois_verified(self) -> int:
        return sum(1 for d in self.docs
                   if d.doc_type == "COI" and d.status == "VERIFIED")


class SOP22Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    DOC_TYPES = DOC_TYPES
    DOC_STATUS = DOC_STATUS
    HCI_COI_MINIMUMS = HCI_COI_MINIMUMS
