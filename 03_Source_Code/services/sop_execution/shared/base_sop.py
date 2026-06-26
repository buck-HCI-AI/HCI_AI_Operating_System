"""Base class for all SOP execution modules."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import services.db as db
from .sop_data_model import SOPStatus, VALID_TRANSITIONS, TERMINAL_STATUSES

# Platform Event Bus — imported lazily to avoid circular deps at module load time
def _emit(event_type: str, sop_number: str, instance_id: int, actor: str, payload: dict) -> None:
    try:
        # 03_Source_Code is 3 levels up from shared/
        _src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        _plat = os.path.join(_src, "services", "platform")
        _api  = os.path.join(_src, "api")
        for _p in (_plat, _api, _src):
            if _p not in sys.path:
                sys.path.insert(0, _p)
        # Import via the event_bus subpackage (avoids stdlib 'platform' module conflict)
        from event_bus.event_bus_service import EventBus
        row = db.query_one("SELECT project_id FROM sop_instances WHERE id = %s", (instance_id,))
        pid = row["project_id"] if row else None
        EventBus.publish(
            event_type=event_type,
            source_service=f"sop_{sop_number}",
            entity_type="sop_instance",
            entity_id=instance_id,
            project_id=pid,
            payload=payload,
            actor=actor,
        )
    except Exception:
        pass  # event bus failures never break SOP operations


class BaseSOP:
    """
    Shared persistence and workflow logic for all SOP modules.
    Subclasses implement SOP-specific business logic.
    """

    SOP_NUMBER: str = ""

    # ── Instance Management ────────────────────────────────────────────────────

    @classmethod
    def create_instance(cls, project_id: int, owner_name: str, owner_role: str,
                        target_issue_date: str | None = None,
                        bid_due_date: str | None = None,
                        parent_instance_id: int | None = None,
                        meta: dict | None = None) -> dict:
        row = db.execute_returning("""
            INSERT INTO sop_instances
                (project_id, sop_number, status, owner_name, owner_role,
                 target_issue_date, bid_due_date, parent_instance_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, status, created_at
        """, (project_id, cls.SOP_NUMBER, SOPStatus.NOT_STARTED.value,
              owner_name, owner_role, target_issue_date, bid_due_date,
              parent_instance_id))
        cls._log_event(row["id"], "created", SOPStatus.NOT_STARTED.value, owner_name)
        return dict(row)

    @classmethod
    def get_instance(cls, instance_id: int) -> dict | None:
        row = db.query_one(
            "SELECT * FROM sop_instances WHERE id = %s", (instance_id,)
        )
        return dict(row) if row else None

    @classmethod
    def list_instances(cls, project_id: int | None = None,
                       status: str | None = None) -> list[dict]:
        conditions, params = [f"sop_number = '{cls.SOP_NUMBER}'"], []
        if project_id:
            conditions.append("project_id = %s")
            params.append(project_id)
        if status:
            conditions.append("status = %s")
            params.append(status)
        where = " AND ".join(conditions)
        rows = db.query(
            f"SELECT * FROM sop_instances WHERE {where} ORDER BY created_at DESC",
            params or None
        )
        return [dict(r) for r in rows]

    # ── Status Transitions ─────────────────────────────────────────────────────

    @classmethod
    def transition_status(cls, instance_id: int, new_status: SOPStatus,
                          actor: str, notes: str = "") -> dict:
        row = db.query_one(
            "SELECT status FROM sop_instances WHERE id = %s", (instance_id,)
        )
        if not row:
            raise ValueError(f"SOP instance {instance_id} not found")

        current = SOPStatus(row["status"])
        if new_status not in VALID_TRANSITIONS.get(current, []):
            raise ValueError(
                f"Invalid transition: {current.value} → {new_status.value}"
            )
        if current in TERMINAL_STATUSES:
            raise ValueError(f"Cannot transition from terminal status {current.value}")

        db.execute("""
            UPDATE sop_instances
            SET status = %s, status_changed_at = NOW(), status_changed_by = %s
            WHERE id = %s
        """, (new_status.value, actor, instance_id))

        cls._log_event(instance_id, "status_change", new_status.value, actor, notes)

        _emit("sop.status_changed", cls.SOP_NUMBER, instance_id, actor, {
            "from_status": current.value,
            "to_status": new_status.value,
            "notes": notes,
        })

        return {"instance_id": instance_id, "status": new_status.value}

    # ── Inputs ─────────────────────────────────────────────────────────────────

    @classmethod
    def confirm_input(cls, instance_id: int, input_key: str,
                      confirmed_by: str, file_path: str = None,
                      notes: str = None) -> dict:
        existing = db.query_one(
            "SELECT id FROM sop_inputs WHERE sop_instance_id = %s AND input_key = %s",
            (instance_id, input_key)
        )
        if existing:
            db.execute("""
                UPDATE sop_inputs
                SET confirmed = TRUE, confirmed_by = %s, confirmed_at = NOW(),
                    file_path = COALESCE(%s, file_path), notes = COALESCE(%s, notes)
                WHERE id = %s
            """, (confirmed_by, file_path, notes, existing["id"]))
            return {"input_key": input_key, "confirmed": True}
        else:
            db.execute("""
                INSERT INTO sop_inputs
                    (sop_instance_id, input_key, confirmed, confirmed_by,
                     confirmed_at, file_path, notes)
                VALUES (%s, %s, TRUE, %s, NOW(), %s, %s)
            """, (instance_id, input_key, confirmed_by, file_path, notes))
            return {"input_key": input_key, "confirmed": True}

    @classmethod
    def get_missing_inputs(cls, instance_id: int,
                           required_keys: list[str]) -> list[str]:
        confirmed = db.query("""
            SELECT input_key FROM sop_inputs
            WHERE sop_instance_id = %s AND confirmed = TRUE
        """, (instance_id,))
        confirmed_keys = {r["input_key"] for r in confirmed}
        return [k for k in required_keys if k not in confirmed_keys]

    # ── Outputs ────────────────────────────────────────────────────────────────

    @classmethod
    def save_output(cls, instance_id: int, output_type: str, output_label: str,
                    content: dict | None = None, file_path: str | None = None) -> int:
        import json
        row = db.execute_returning("""
            INSERT INTO sop_outputs
                (sop_instance_id, output_type, output_label, content, file_path, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (instance_id, output_type, output_label,
              json.dumps(content) if content else None, file_path))
        return row["id"]

    # ── Audit ──────────────────────────────────────────────────────────────────

    @classmethod
    def _log_event(cls, instance_id: int, event_type: str, event_value: str,
                   actor: str, notes: str = "") -> None:
        try:
            db.execute("""
                INSERT INTO sop_workflow_events
                    (sop_instance_id, event_type, event_value, actor, notes, occurred_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (instance_id, event_type, event_value, actor, notes))
        except Exception:
            pass

    @classmethod
    def get_audit_trail(cls, instance_id: int) -> list[dict]:
        rows = db.query("""
            SELECT event_type, event_value, actor, notes, occurred_at
            FROM sop_workflow_events
            WHERE sop_instance_id = %s
            ORDER BY occurred_at
        """, (instance_id,))
        return [dict(r) for r in rows]
