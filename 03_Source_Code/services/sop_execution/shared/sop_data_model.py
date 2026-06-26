"""Core data models for the SOP Execution Layer."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Any


class SOPStatus(str, Enum):
    NOT_STARTED       = "Not Started"
    INPUTS_MISSING    = "Inputs Missing"
    READY_TO_START    = "Ready to Start"
    IN_PROGRESS       = "In Progress"
    AI_DRAFTED        = "AI Drafted"
    INTERNAL_REVIEW   = "Internal Review"
    REVISION_REQUIRED = "Revision Required"
    APPROVAL_REQUIRED = "Approval Required"
    APPROVED          = "Approved"
    ISSUED            = "Issued / Completed"
    HANDED_OFF        = "Handed Off"
    BLOCKED           = "Blocked"
    EXCEPTION_APPROVED = "Exception Approved"
    CANCELLED         = "Cancelled"
    ARCHIVED          = "Archived"


# Valid forward transitions per status
VALID_TRANSITIONS: dict[SOPStatus, list[SOPStatus]] = {
    SOPStatus.NOT_STARTED:       [SOPStatus.INPUTS_MISSING, SOPStatus.READY_TO_START, SOPStatus.IN_PROGRESS],
    SOPStatus.INPUTS_MISSING:    [SOPStatus.READY_TO_START, SOPStatus.IN_PROGRESS],
    SOPStatus.READY_TO_START:    [SOPStatus.IN_PROGRESS],
    SOPStatus.IN_PROGRESS:       [SOPStatus.AI_DRAFTED, SOPStatus.INTERNAL_REVIEW, SOPStatus.BLOCKED],
    SOPStatus.AI_DRAFTED:        [SOPStatus.INTERNAL_REVIEW],
    SOPStatus.INTERNAL_REVIEW:   [SOPStatus.REVISION_REQUIRED, SOPStatus.APPROVAL_REQUIRED, SOPStatus.APPROVED],
    SOPStatus.REVISION_REQUIRED: [SOPStatus.IN_PROGRESS, SOPStatus.INTERNAL_REVIEW],
    SOPStatus.APPROVAL_REQUIRED: [SOPStatus.APPROVED, SOPStatus.REVISION_REQUIRED],
    SOPStatus.APPROVED:          [SOPStatus.ISSUED, SOPStatus.HANDED_OFF],
    SOPStatus.ISSUED:            [SOPStatus.HANDED_OFF, SOPStatus.ARCHIVED],
    SOPStatus.HANDED_OFF:        [SOPStatus.ARCHIVED],
    SOPStatus.BLOCKED:           [SOPStatus.IN_PROGRESS, SOPStatus.INPUTS_MISSING],
    SOPStatus.EXCEPTION_APPROVED:[SOPStatus.IN_PROGRESS, SOPStatus.APPROVED],
    SOPStatus.CANCELLED:         [],   # terminal
    SOPStatus.ARCHIVED:          [],   # terminal
}

TERMINAL_STATUSES = {SOPStatus.CANCELLED, SOPStatus.ARCHIVED}


@dataclass
class SOPInstance:
    project_id: int
    sop_number: str
    owner_name: str
    owner_role: str
    target_issue_date: date | None = None
    bid_due_date: date | None = None
    id: int | None = None
    status: SOPStatus = SOPStatus.NOT_STARTED
    created_at: datetime | None = None
    actual_issue_date: date | None = None
    parent_instance_id: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class SOPInput:
    sop_instance_id: int
    input_key: str
    input_label: str
    confirmed: bool = False
    confirmed_by: str | None = None
    confirmed_at: datetime | None = None
    file_path: str | None = None
    notes: str | None = None


@dataclass
class SOPOutput:
    sop_instance_id: int
    output_type: str
    output_label: str
    content: dict[str, Any] | None = None
    file_path: str | None = None
    created_at: datetime | None = None


class RiskClass(str, Enum):
    SCOPE    = "Scope"
    COST     = "Cost"
    SCHEDULE = "Schedule"
    CONTRACT = "Contract"
    COVERAGE = "Coverage"
    DOCUMENT = "Document Control"


class RiskSeverity(str, Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"


@dataclass
class RiskFlag:
    risk_class: RiskClass
    description: str
    severity: RiskSeverity
    location: str = ""
    recommended_resolution: str = ""
    dispositioned: bool = False
    disposition: str | None = None  # Accepted / Resolved / Escalated
    disposition_by: str | None = None


@dataclass
class StopEvent:
    sop_instance_id: int
    condition_code: str  # SC-01 through SC-07
    blocker_description: str
    resolution_path: str = ""
    triggered_at: datetime | None = None
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    exception_flag: bool = False
