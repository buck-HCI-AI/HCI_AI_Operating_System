"""Universal stop condition enforcement for all SOP modules."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import services.db as db
from datetime import datetime


class WorkflowBlockedError(Exception):
    """Raised when a stop condition blocks workflow progression."""
    def __init__(self, condition_code: str, message: str, resolution_path: str = ""):
        self.condition_code = condition_code
        self.resolution_path = resolution_path
        super().__init__(f"[{condition_code}] {message}")


class StopConditionChecker:
    """
    Evaluates and enforces the 7 universal stop conditions.
    Records every trigger to sop_stop_events.
    """

    CONDITION_LABELS = {
        "SC-01": "Required inputs missing or outdated",
        "SC-02": "Output depends on unapproved assumption",
        "SC-03": "Scope, pricing, schedule, or contract risk unclear",
        "SC-04": "External commitment without required approval",
        "SC-05": "Reviewer marked work Revision Required",
        "SC-06": "Approval gate bypass attempted",
        "SC-07": "Handoff destination missing",
    }

    @staticmethod
    def _log_stop_event(sop_instance_id: int, condition_code: str,
                        description: str, resolution_path: str) -> None:
        try:
            db.execute("""
                INSERT INTO sop_stop_events
                    (sop_instance_id, condition_code, blocker_description,
                     resolution_path, triggered_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (sop_instance_id, condition_code, description, resolution_path))
        except Exception:
            pass  # never let logging failures hide the real stop

    @classmethod
    def check_sc01_inputs(cls, sop_instance_id: int, missing_inputs: list[str]) -> None:
        """SC-01: Block if required inputs are missing."""
        if not missing_inputs:
            return
        description = "Missing required inputs: " + "; ".join(missing_inputs)
        resolution = "PM to confirm each missing input before proceeding."
        cls._log_stop_event(sop_instance_id, "SC-01", description, resolution)
        raise WorkflowBlockedError(
            "SC-01", description, resolution
        )

    @classmethod
    def check_sc02_assumption(cls, sop_instance_id: int, assumption: str) -> None:
        """SC-02: Block if output rests on an unapproved assumption."""
        description = f"Unapproved assumption: {assumption}"
        resolution = "Owner must confirm or resolve assumption before proceeding."
        cls._log_stop_event(sop_instance_id, "SC-02", description, resolution)
        raise WorkflowBlockedError("SC-02", description, resolution)

    @classmethod
    def check_sc03_risk_flags(cls, sop_instance_id: int,
                              open_high_risks: list[dict]) -> None:
        """SC-03: Block if HIGH severity risk flags are undispositioned."""
        if not open_high_risks:
            return
        flags = "; ".join(f"[{r['risk_class']}] {r['description']}"
                          for r in open_high_risks)
        description = f"Unresolved HIGH risk flags: {flags}"
        resolution = "PM must disposition all HIGH risk flags before submission."
        cls._log_stop_event(sop_instance_id, "SC-03", description, resolution)
        raise WorkflowBlockedError("SC-03", description, resolution)

    @classmethod
    def check_sc04_approval_gate(cls, sop_instance_id: int, gate_id: str,
                                 gate_name: str) -> None:
        """SC-04: Block external commitment without approval gate record."""
        row = db.query_one("""
            SELECT id FROM sop_approval_gates
            WHERE sop_instance_id = %s AND gate_id = %s AND approved_at IS NOT NULL
        """, (sop_instance_id, gate_id))
        if row:
            return
        description = f"Gate {gate_id} ({gate_name}) not yet approved."
        resolution = f"Route to required approver for {gate_name} before proceeding."
        cls._log_stop_event(sop_instance_id, "SC-04", description, resolution)
        raise WorkflowBlockedError("SC-04", description, resolution)

    @classmethod
    def check_sc06_bypass_attempt(cls, sop_instance_id: int, gate_id: str,
                                  actor: str) -> None:
        """SC-06: Log and block bypass attempt."""
        description = f"User {actor!r} attempted to bypass gate {gate_id}"
        resolution = "Either the required approver submits their approval, or create an exception record."
        cls._log_stop_event(sop_instance_id, "SC-06", description, resolution)
        raise WorkflowBlockedError("SC-06", description, resolution)

    @classmethod
    def check_sc07_handoff_destination(cls, sop_instance_id: int,
                                       recipient_name: str | None) -> None:
        """SC-07: Block Issued/Handed-Off without named recipient."""
        if recipient_name and recipient_name.strip():
            return
        description = "Handoff destination is missing — no recipient named."
        resolution = "PM must name the next SOP owner and confirm notification."
        cls._log_stop_event(sop_instance_id, "SC-07", description, resolution)
        raise WorkflowBlockedError("SC-07", description, resolution)

    @staticmethod
    def resolve_stop_event(stop_event_id: int, resolved_by: str) -> None:
        db.execute("""
            UPDATE sop_stop_events
            SET resolved_at = NOW(), resolved_by = %s
            WHERE id = %s
        """, (resolved_by, stop_event_id))
