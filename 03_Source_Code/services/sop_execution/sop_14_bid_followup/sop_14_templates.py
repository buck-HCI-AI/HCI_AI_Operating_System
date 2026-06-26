"""SOP 14 — Layer 4: Bid Follow-Up data fields and template validators."""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_INPUT_KEYS = [
    "sop_13_instance_id",
    "sub_list",
    "bid_due_date",
    "trade_name",
]

INPUT_LABELS = {
    "sop_13_instance_id": "SOP 13 Bid Distribution — instance ID",
    "sub_list":           "Sub list from SOP 13 distribution records",
    "bid_due_date":       "Bid due date (from SOP 11)",
    "trade_name":         "Trade being followed up",
}

RESPONSE_STATUSES = [
    "pending",       # No contact yet
    "contacted",     # Follow-up sent; awaiting response
    "confirmed",     # Sub confirmed they are bidding
    "declined",      # Sub confirmed they are not bidding
    "no_response",   # Did not respond after follow-up
    "bid_received",  # Bid has been received
]

MIN_RESPONSIVE_SUBS = 3  # Same rule as SOP 15


@dataclass
class SubFollowUpRecord:
    sub_name: str
    trade_code: str
    contact_email: str
    response_status: str = "pending"
    follow_up_date: str | None = None
    follow_up_method: str = "email"
    response_date: str | None = None
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "sub_name": self.sub_name,
            "trade_code": self.trade_code,
            "contact_email": self.contact_email,
            "response_status": self.response_status,
            "follow_up_date": self.follow_up_date,
            "follow_up_method": self.follow_up_method,
            "response_date": self.response_date,
            "notes": self.notes,
        }


@dataclass
class FollowUpOutput:
    instance_id: int
    project_id: int
    trade_name: str
    follow_up_records: list[SubFollowUpRecord] = field(default_factory=list)
    confirmed_bidding: int = 0
    declined: int = 0
    no_response: int = 0
    bid_received: int = 0

    def ready_for_leveling(self) -> bool:
        return (self.confirmed_bidding + self.bid_received) >= MIN_RESPONSIVE_SUBS

    def to_dict(self) -> dict:
        return {
            "instance_id": self.instance_id,
            "project_id": self.project_id,
            "trade_name": self.trade_name,
            "confirmed_bidding": self.confirmed_bidding,
            "declined": self.declined,
            "no_response": self.no_response,
            "bid_received": self.bid_received,
            "ready_for_leveling": self.ready_for_leveling(),
        }


class SOP14Templates:
    REQUIRED_INPUT_KEYS = REQUIRED_INPUT_KEYS
    INPUT_LABELS = INPUT_LABELS
    RESPONSE_STATUSES = RESPONSE_STATUSES
    MIN_RESPONSIVE_SUBS = MIN_RESPONSIVE_SUBS
