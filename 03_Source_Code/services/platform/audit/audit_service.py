"""Platform Audit Trail Service.

Centralized cross-service audit log. Provides a unified view of all events
across SOPs, workflows, notifications, and identity changes.

Also bridges sop_workflow_events and workflow_events into a single query surface.
"""
from __future__ import annotations
import os, sys
from datetime import datetime, timedelta

_here = os.path.dirname(os.path.abspath(__file__))
_src = os.path.abspath(os.path.join(_here, "..", "..", ".."))
sys.path.insert(0, _src)
sys.path.insert(0, os.path.join(_src, "api"))

import services.db as db


class AuditTrail:
    """Write and query the cross-platform audit log."""

    # ── Write ─────────────────────────────────────────────────────────────────

    @staticmethod
    def log(
        source: str,
        event_type: str,
        actor: str = "system",
        entity_type: str = "",
        entity_id: int | None = None,
        project_id: int | None = None,
        summary: str = "",
        payload: dict | None = None,
    ) -> int | None:
        """Write one audit record. Returns new record id."""
        try:
            row = db.execute_returning("""
                INSERT INTO platform_audit_log
                    (source, entity_type, entity_id, project_id,
                     event_type, actor, summary, payload)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                RETURNING id
            """, (
                source, entity_type or "", entity_id, project_id,
                event_type, actor, summary,
                __import__("json").dumps(payload or {}),
            ))
            return row["id"] if row else None
        except Exception:
            return None

    @staticmethod
    def log_sop_event(
        sop_instance_id: int,
        event_type: str,
        actor: str,
        summary: str = "",
        project_id: int | None = None,
        payload: dict | None = None,
    ) -> int | None:
        return AuditTrail.log(
            source="sop",
            event_type=event_type,
            actor=actor,
            entity_type="sop_instance",
            entity_id=sop_instance_id,
            project_id=project_id,
            summary=summary,
            payload=payload,
        )

    @staticmethod
    def log_workflow_event(
        workflow_id: str,
        event_type: str,
        actor: str = "system",
        project_id: int | None = None,
        summary: str = "",
        payload: dict | None = None,
    ) -> int | None:
        return AuditTrail.log(
            source="workflow",
            event_type=event_type,
            actor=actor,
            entity_type="workflow",
            entity_id=None,
            project_id=project_id,
            summary=summary or f"Workflow {workflow_id}: {event_type}",
            payload={"workflow_id": workflow_id, **(payload or {})},
        )

    # ── Read — platform_audit_log ─────────────────────────────────────────────

    @staticmethod
    def query(
        source: str | None = None,
        entity_type: str | None = None,
        entity_id: int | None = None,
        project_id: int | None = None,
        actor: str | None = None,
        event_type: str | None = None,
        since_hours: int | None = None,
        limit: int = 100,
    ) -> list[dict]:
        conditions = ["1=1"]
        params: list = []
        if source:
            conditions.append("source = %s")
            params.append(source)
        if entity_type:
            conditions.append("entity_type = %s")
            params.append(entity_type)
        if entity_id is not None:
            conditions.append("entity_id = %s")
            params.append(entity_id)
        if project_id is not None:
            conditions.append("project_id = %s")
            params.append(project_id)
        if actor:
            conditions.append("actor = %s")
            params.append(actor)
        if event_type:
            conditions.append("event_type = %s")
            params.append(event_type)
        if since_hours:
            cutoff = datetime.utcnow() - timedelta(hours=since_hours)
            conditions.append("occurred_at >= %s")
            params.append(cutoff)
        params.append(limit)
        try:
            rows = db.query(f"""
                SELECT * FROM platform_audit_log
                WHERE {' AND '.join(conditions)}
                ORDER BY occurred_at DESC
                LIMIT %s
            """, params)
            return [dict(r) for r in rows]
        except Exception:
            return []

    # ── Read — sop_workflow_events (existing SOP audit log) ───────────────────

    @staticmethod
    def get_sop_trail(sop_instance_id: int) -> list[dict]:
        """Fetch native SOP audit trail from sop_workflow_events."""
        try:
            rows = db.query("""
                SELECT event_type, event_value, actor, notes, occurred_at
                FROM sop_workflow_events
                WHERE sop_instance_id = %s
                ORDER BY occurred_at
            """, (sop_instance_id,))
            return [dict(r) for r in rows]
        except Exception:
            return []

    @staticmethod
    def get_full_sop_trail(sop_instance_id: int) -> dict:
        """Combined view: sop_workflow_events + platform_audit_log for this instance."""
        sop_events = AuditTrail.get_sop_trail(sop_instance_id)
        platform_events = AuditTrail.query(entity_type="sop_instance", entity_id=sop_instance_id, limit=200)
        return {
            "sop_instance_id": sop_instance_id,
            "sop_workflow_events": sop_events,
            "platform_audit_events": platform_events,
            "total_events": len(sop_events) + len(platform_events),
        }

    # ── Read — workflow_events (existing workflow audit log) ──────────────────

    @staticmethod
    def get_workflow_trail(workflow_id: str | None = None, project_id: int | None = None,
                           limit: int = 50) -> list[dict]:
        """Fetch from workflow_events table."""
        conditions = ["1=1"]
        params: list = []
        if workflow_id:
            conditions.append("workflow_id = %s")
            params.append(workflow_id)
        if project_id is not None:
            conditions.append("project_id = %s")
            params.append(project_id)
        params.append(limit)
        try:
            rows = db.query(f"""
                SELECT * FROM workflow_events
                WHERE {' AND '.join(conditions)}
                ORDER BY created_at DESC
                LIMIT %s
            """, params)
            return [dict(r) for r in rows]
        except Exception:
            return []

    # ── Read — unified project timeline ──────────────────────────────────────

    @staticmethod
    def get_project_timeline(project_id: int, since_hours: int = 168) -> dict:
        """All audit events for a project in the last N hours (default 7 days)."""
        platform = AuditTrail.query(project_id=project_id, since_hours=since_hours, limit=200)
        workflow = AuditTrail.get_workflow_trail(project_id=project_id, limit=50)

        sop_rows = []
        try:
            sop_rows = db.query("""
                SELECT si.id AS instance_id, si.sop_number, si.status,
                       swe.event_type, swe.event_value, swe.actor, swe.occurred_at
                FROM sop_workflow_events swe
                JOIN sop_instances si ON si.id = swe.sop_instance_id
                WHERE si.project_id = %s
                ORDER BY swe.occurred_at DESC
                LIMIT 100
            """, (project_id,))
            sop_rows = [dict(r) for r in sop_rows]
        except Exception:
            pass

        return {
            "project_id": project_id,
            "since_hours": since_hours,
            "platform_events": platform,
            "workflow_events": workflow,
            "sop_events": sop_rows,
            "total_events": len(platform) + len(workflow) + len(sop_rows),
        }

    # ── Stats ─────────────────────────────────────────────────────────────────

    @staticmethod
    def summary(project_id: int | None = None) -> dict:
        """Count of events by source in the last 24 hours."""
        try:
            params = [24]
            base = "WHERE occurred_at >= NOW() - INTERVAL '%s hours'"
            if project_id:
                base += " AND project_id = %s"
                params.append(project_id)
            rows = db.query(f"""
                SELECT source, COUNT(*) AS cnt
                FROM platform_audit_log
                {base}
                GROUP BY source ORDER BY cnt DESC
            """, params)
            return {r["source"]: r["cnt"] for r in rows}
        except Exception:
            return {}
