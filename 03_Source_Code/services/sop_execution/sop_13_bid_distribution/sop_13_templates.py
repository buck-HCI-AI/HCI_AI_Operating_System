"""SOP 13 — Layer 4: Bid Distribution data fields and template validators."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "sop_11_instance_id",
    "sub_invite_list",
    "bid_package_file",
    "bid_due_date",
    "scope_summary",
]

INPUT_LABELS = {
    "sop_11_instance_id":  "SOP 11 Bid Package — Issued instance ID",
    "sub_invite_list":     "Sub invite list — minimum 3 subs per trade",
    "bid_package_file":    "Bid package file path (MinIO or Drive link)",
    "bid_due_date":        "Bid due date (from SOP 11)",
    "scope_summary":       "Scope summary per trade (from SOP 11 scope sections)",
}

DISTRIBUTION_METHODS = ["email", "fax", "hand_delivery", "portal"]


@dataclass
class SubDistributionRecord:
    sub_name: str
    trade_code: str
    contact_email: str
    sent_date: str
    method: str = "email"
    confirmed_received: bool = False
    confirmed_date: str | None = None
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "sub_name": self.sub_name,
            "trade_code": self.trade_code,
            "contact_email": self.contact_email,
            "sent_date": self.sent_date,
            "method": self.method,
            "confirmed_received": self.confirmed_received,
            "confirmed_date": self.confirmed_date,
            "notes": self.notes,
        }

    def validate(self) -> list[str]:
        errors = []
        if not self.sub_name:
            errors.append("sub_name is required")
        if not self.contact_email or "@" not in self.contact_email:
            errors.append(f"{self.sub_name}: valid contact_email required")
        if not self.sent_date:
            errors.append(f"{self.sub_name}: sent_date required")
        return errors


@dataclass
class DistributionOutput:
    instance_id: int
    project_id: int
    sop_11_instance_id: int
    distribution_records: list[SubDistributionRecord] = field(default_factory=list)
    total_sent: int = 0
    total_confirmed: int = 0
    ai_outreach_email: str | None = None

    def confirmation_rate(self) -> float:
        if not self.total_sent:
            return 0.0
        return round(self.total_confirmed / self.total_sent * 100, 1)

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "sop_11_instance_id": self.sop_11_instance_id,
            "distribution_records": [r.to_dict() for r in self.distribution_records],
            "total_sent": self.total_sent,
            "total_confirmed": self.total_confirmed,
            "confirmation_rate_pct": self.confirmation_rate(),
        }


class SOP13Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    DISTRIBUTION_METHODS = DISTRIBUTION_METHODS
