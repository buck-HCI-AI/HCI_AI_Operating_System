"""Approval gate engine for all SOP modules."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import services.db as db
from datetime import datetime


class ApprovalEngine:
    """
    Creates, queries, and validates SOP approval gate records.
    All gates are stored in sop_approval_gates.
    """

    @staticmethod
    def create_gate_record(
        sop_instance_id: int,
        gate_id: str,
        gate_name: str,
        required_before_status: str,
        approver_name: str,
        approver_role: str,
        method: str = "in-system",
        conditions: str | None = None,
    ) -> int:
        """Record an approval. Returns the gate record ID."""
        row = db.execute_returning("""
            INSERT INTO sop_approval_gates
                (sop_instance_id, gate_id, gate_name, required_before_status,
                 approver_name, approver_role, approved_at, method, conditions)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s)
            RETURNING id
        """, (sop_instance_id, gate_id, gate_name, required_before_status,
              approver_name, approver_role, method, conditions))
        return row["id"]

    @staticmethod
    def is_gate_approved(sop_instance_id: int, gate_id: str) -> bool:
        """Check if a specific gate has an approved record."""
        row = db.query_one("""
            SELECT id FROM sop_approval_gates
            WHERE sop_instance_id = %s AND gate_id = %s AND approved_at IS NOT NULL
        """, (sop_instance_id, gate_id))
        return row is not None

    @staticmethod
    def get_gates(sop_instance_id: int) -> list[dict]:
        rows = db.query("""
            SELECT gate_id, gate_name, required_before_status,
                   approver_name, approver_role, approved_at, method, conditions
            FROM sop_approval_gates
            WHERE sop_instance_id = %s
            ORDER BY approved_at
        """, (sop_instance_id,))
        return [dict(r) for r in rows]

    @staticmethod
    def create_exception_record(
        sop_instance_id: int,
        gate_id: str,
        reason: str,
        risk_accepted: str,
        mitigation: str,
        approver: str,
        expires_at: str,
        created_by: str,
        project_id: int | None = None,
    ) -> int:
        """Record a gate bypass exception. Every exception requires all fields."""
        row = db.execute_returning("""
            INSERT INTO sop_exceptions
                (sop_instance_id, gate_id, exception_reason, risk_accepted,
                 mitigation, approver, approved_at, expires_at, created_by, project_id)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s::TIMESTAMPTZ, %s, %s)
            RETURNING id
        """, (sop_instance_id, gate_id, reason, risk_accepted,
              mitigation, approver, expires_at, created_by, project_id))
        return row["id"]
