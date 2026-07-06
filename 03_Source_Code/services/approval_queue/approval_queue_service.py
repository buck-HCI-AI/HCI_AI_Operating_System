"""
Approval Queue Service — MVP Sprint 1
Holds ALL proposed write actions (HubSpot, Drive, Houzz, email) until Buck explicitly approves.

Safety rules:
  - status='pending' means NOT executed — nothing has been changed in any system
  - Only transitions to 'executed' after approved_by is set and explicit execute() called
  - Every approval is logged to platform_audit_log
  - Rollback path must be specified for any action that changes structured data
"""
import sys, os, json, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
from datetime import datetime, timezone, timedelta
from typing import Optional

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)


def _pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


def _audit(source: str, event_type: str, actor: str, entity_id: int,
           summary: str, payload: dict = None):
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO platform_audit_log
                        (source, event_type, actor, entity_type, entity_id, summary, payload, correlation_id)
                    VALUES (%s, %s, %s, 'approval_queue', %s, %s, %s, %s)
                """, (source, event_type, actor, entity_id, summary,
                      json.dumps(payload or {}), str(uuid.uuid4())))
                conn.commit()
    except Exception:
        pass


# AD-12.1 (ratified 2026-06-30): these are internal system automation events, not
# externally-impacting actions — they go to activity_log, never to Buck's approval queue.
# drive_upload_file removed 2026-07-06: it's the only action_type used by bid-leveling's
# real Excel-to-Drive uploads (real vendor $ data) — externally-impacting, not internal
# noise. It was bundled into AD-12.1's cleanup by category-name oversight; carving it out
# restores Buck approval before any bid document reaches Drive, matching the bid-leveling
# code's own docstrings and BL-QUEUE-01/02 test expectations. Confirmed no other caller
# in the codebase used this action_type, so this is a no-risk, single-path change.
_INTERNAL_NOISE_ACTION_TYPES = {"verify_approval_loop", "system_check", "health_check"}


class ApprovalQueueService:

    @classmethod
    def enqueue(cls, workflow: str, action_type: str, target_system: str,
                target_id: str, target_description: str, proposed_payload: dict,
                reason: str, project_id: int = None, actor: str = "system",
                priority: str = "normal", source_data: dict = None,
                rollback_path: str = None, expires_hours: int = 72) -> dict:
        """Queue a proposed write action for approval. Returns queue item ID.
        AD-12.1: internal system automation events (action_type in
        _INTERNAL_NOISE_ACTION_TYPES) are logged to activity_log instead —
        they never reach Buck's approval queue."""
        if action_type in _INTERNAL_NOISE_ACTION_TYPES:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO activity_log (event_type, target_system, target_id, description, payload, actor)
                        VALUES (%s,%s,%s,%s,%s,%s) RETURNING id
                    """, (action_type, target_system, target_id, target_description,
                          json.dumps(proposed_payload), actor))
                    row = cur.fetchone()
                conn.commit()
            return {"queue_id": None, "activity_log_id": row["id"], "status": "logged",
                    "message": f"Internal system event ({action_type}) logged to activity_log — "
                               f"not queued for approval per AD-12.1."}

        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
        corr_id = str(uuid.uuid4())

        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO approval_queue
                        (workflow, action_type, target_system, target_id, target_description,
                         proposed_payload, source_data, reason, project_id, actor, priority,
                         rollback_path, audit_correlation_id, expires_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
                """, (workflow, action_type, target_system, target_id, target_description,
                      json.dumps(proposed_payload), json.dumps(source_data or {}), reason,
                      project_id, actor, priority, rollback_path, corr_id, expires_at))
                row = cur.fetchone()
                conn.commit()

        qid = row["id"]
        _audit("approval_queue", "action.queued", actor, qid,
               f"[QUEUED] {action_type} on {target_system}: {target_description}",
               {"workflow": workflow, "target_system": target_system, "priority": priority})

        return {"queue_id": qid, "status": "pending", "correlation_id": corr_id,
                "expires_at": expires_at.isoformat(),
                "message": f"Action queued for Buck approval. No changes made to {target_system}."}

    @classmethod
    def approve(cls, queue_id: int, approved_by: str = "Buck Adams") -> dict:
        """Mark an action as approved. Does NOT execute it — call execute() after."""
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE approval_queue SET status='approved', approved_by=%s, approved_at=NOW()
                    WHERE id=%s AND status='pending'
                    RETURNING id, status, action_type, target_system, target_description
                """, (approved_by, queue_id))
                row = cur.fetchone()
                conn.commit()
        if not row:
            return {"error": f"Queue item {queue_id} not found or not in pending status"}

        _audit("approval_queue", "action.approved", approved_by, queue_id,
               f"[APPROVED] {row['action_type']} on {row['target_system']}: {row['target_description']}")
        return {"queue_id": queue_id, "status": "approved", "approved_by": approved_by,
                "message": "Approved. Call execute() to apply."}

    @classmethod
    def reject(cls, queue_id: int, rejected_by: str = "Buck Adams", reason: str = "") -> dict:
        """Reject a queued action. No changes are made."""
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE approval_queue SET status='rejected', approved_by=%s,
                        approved_at=NOW(), rejected_reason=%s
                    WHERE id=%s AND status='pending'
                    RETURNING id, action_type, target_system
                """, (rejected_by, reason, queue_id))
                row = cur.fetchone()
                conn.commit()
        if not row:
            return {"error": f"Queue item {queue_id} not found or not in pending status"}

        _audit("approval_queue", "action.rejected", rejected_by, queue_id,
               f"[REJECTED] {row['action_type']} on {row['target_system']}: {reason}")
        return {"queue_id": queue_id, "status": "rejected"}

    @classmethod
    def mark_executed(cls, queue_id: int, actor: str = "system") -> dict:
        """Mark an approved action as executed (caller is responsible for actual execution)."""
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE approval_queue SET status='executed', executed_at=NOW()
                    WHERE id=%s AND status='approved'
                    RETURNING id, action_type, target_system, target_description
                """, (queue_id,))
                row = cur.fetchone()
                conn.commit()
        if not row:
            return {"error": f"Queue item {queue_id} not found or not in approved status"}

        _audit("approval_queue", "action.executed", actor, queue_id,
               f"[EXECUTED] {row['action_type']} on {row['target_system']}: {row['target_description']}")
        return {"queue_id": queue_id, "status": "executed"}

    @classmethod
    def get_queue(cls, status: str = "pending", project_id: int = None,
                  workflow: str = None, limit: int = 50) -> list:
        clauses = []
        values = []
        if status:
            clauses.append("status = %s"); values.append(status)
        if project_id:
            clauses.append("project_id = %s"); values.append(project_id)
        if workflow:
            clauses.append("workflow = %s"); values.append(workflow)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        values.append(limit)
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM approval_queue {where} ORDER BY created_at DESC LIMIT %s",
                    values
                )
                return [dict(r) for r in cur.fetchall()]

    @classmethod
    def get_item(cls, queue_id: int) -> dict:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM approval_queue WHERE id = %s", (queue_id,))
                row = cur.fetchone()
        return dict(row) if row else {"error": "Not found"}

    @classmethod
    def summary(cls) -> dict:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT status, COUNT(*) as count FROM approval_queue GROUP BY status
                """)
                by_status = {r["status"]: r["count"] for r in cur.fetchall()}
                cur.execute("SELECT COUNT(*) as total FROM approval_queue")
                total = cur.fetchone()["total"]
        return {"total": total, "by_status": by_status, "pending": by_status.get("pending", 0)}
