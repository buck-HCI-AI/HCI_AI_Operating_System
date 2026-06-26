"""Platform Notification Center Service.

Creates and delivers in-system notifications.
Email delivery via Outlook Graph API is wired but requires explicit trigger — never auto-sends.
"""
from __future__ import annotations
import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
_src = os.path.abspath(os.path.join(_here, "..", "..", ".."))
sys.path.insert(0, _src)
sys.path.insert(0, os.path.join(_src, "api"))

import services.db as db

# ── Notification types ────────────────────────────────────────────────────────
APPROVAL_REQUIRED    = "approval_required"
WORK_STOPPED         = "work_stopped"
AI_DRAFT_READY       = "ai_draft_ready"
HANDOFF_READY        = "handoff_ready"
EXCEPTION_CREATED    = "exception_created"
REVIEW_REQUIRED      = "review_required"
PROCUREMENT_DELAY    = "procurement_delay"
SCHEDULE_IMPACT      = "schedule_impact"
RFI_OPEN             = "rfi_open"
SUBMITTAL_DUE        = "submittal_due"
BID_RECEIVED         = "bid_received"
BID_DEADLINE         = "bid_deadline"
DAILY_LOG_MISSING    = "daily_log_missing"
QA_FAILURE           = "qa_failure"
WORKFLOW_EXCEPTION   = "workflow_exception"
SAFETY_HAZARD        = "safety_hazard"
INFO                 = "info"

# Notification types that always go to Buck in addition to primary recipient
OWNER_NOTIFICATION_TYPES = {APPROVAL_REQUIRED, EXCEPTION_CREATED, WORK_STOPPED, SAFETY_HAZARD}

# Escalation thresholds: hours before a notification escalates
ESCALATION_HOURS: dict[str, int] = {
    APPROVAL_REQUIRED: 4,
    WORK_STOPPED:      2,
    RFI_OPEN:         24,
    SUBMITTAL_DUE:    24,
    BID_DEADLINE:      8,
    QA_FAILURE:        4,
    SAFETY_HAZARD:     1,
}

# Actor → email address map (authoritative; update when team changes)
ACTOR_EMAILS: dict[str, str] = {
    "Buck Adams": "buck@ahmaspen.com",
}


class NotificationService:
    """Create, deliver, and query in-system notifications."""

    @staticmethod
    def create(
        recipient: str,
        notification_type: str,
        title: str,
        body: str = "",
        entity_type: str = "",
        entity_id: int | None = None,
        project_id: int | None = None,
        action_url: str = "",
    ) -> int | None:
        """Create a notification record. Returns notification id."""
        try:
            row = db.execute_returning("""
                INSERT INTO platform_notifications
                    (recipient, notification_type, title, body,
                     entity_type, entity_id, project_id, action_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (recipient, notification_type, title, body,
                  entity_type, entity_id, project_id, action_url))
            return row["id"] if row else None
        except Exception:
            return None

    @staticmethod
    def notify_approval_required(
        sop_instance_id: int,
        sop_number: str,
        gate_id: str,
        approver: str,
        project_id: int | None = None,
    ) -> int | None:
        return NotificationService.create(
            recipient=approver,
            notification_type=APPROVAL_REQUIRED,
            title=f"SOP {sop_number} — Approval Required: {gate_id}",
            body=f"Gate {gate_id} for SOP {sop_number} instance #{sop_instance_id} requires your approval.",
            entity_type="sop_instance",
            entity_id=sop_instance_id,
            project_id=project_id,
            action_url=f"/api/v1/sop/{sop_number}/{sop_instance_id}",
        )

    @staticmethod
    def notify_work_stopped(
        sop_instance_id: int,
        sop_number: str,
        condition_code: str,
        description: str,
        actor: str,
        project_id: int | None = None,
    ) -> list[int]:
        nids = []
        for recipient in [actor, "Buck Adams"]:
            nid = NotificationService.create(
                recipient=recipient,
                notification_type=WORK_STOPPED,
                title=f"WORK STOPPED — SOP {sop_number} [{condition_code}]",
                body=description,
                entity_type="sop_instance",
                entity_id=sop_instance_id,
                project_id=project_id,
                action_url=f"/api/v1/sop/{sop_number}/{sop_instance_id}",
            )
            if nid:
                nids.append(nid)
        return nids

    @staticmethod
    def notify_ai_draft_ready(
        sop_instance_id: int,
        sop_number: str,
        actor: str,
        project_id: int | None = None,
    ) -> int | None:
        return NotificationService.create(
            recipient=actor,
            notification_type=AI_DRAFT_READY,
            title=f"SOP {sop_number} — AI Draft Ready for Review",
            body=f"AI has drafted SOP {sop_number} instance #{sop_instance_id}. PM review required.",
            entity_type="sop_instance",
            entity_id=sop_instance_id,
            project_id=project_id,
            action_url=f"/api/v1/sop/{sop_number}/{sop_instance_id}",
        )

    @staticmethod
    def notify_handoff(
        sop_instance_id: int,
        sop_number: str,
        recipient: str,
        next_sop: str = "",
        project_id: int | None = None,
    ) -> int | None:
        body = f"SOP {sop_number} #{sop_instance_id} has been handed off."
        if next_sop:
            body += f" Next step: {next_sop}."
        return NotificationService.create(
            recipient=recipient,
            notification_type=HANDOFF_READY,
            title=f"SOP {sop_number} — Handoff Ready",
            body=body,
            entity_type="sop_instance",
            entity_id=sop_instance_id,
            project_id=project_id,
        )

    @staticmethod
    def get_notifications(
        recipient: str,
        unread_only: bool = False,
        notification_type: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        conditions = ["recipient = %s"]
        params: list = [recipient]
        if unread_only:
            conditions.append("is_read = FALSE")
        if notification_type:
            conditions.append("notification_type = %s")
            params.append(notification_type)
        params.append(limit)
        try:
            rows = db.query(f"""
                SELECT * FROM platform_notifications
                WHERE {' AND '.join(conditions)}
                ORDER BY delivered_at DESC
                LIMIT %s
            """, params)
            return [dict(r) for r in rows]
        except Exception:
            return []

    @staticmethod
    def mark_read(notification_id: int, actor: str = "") -> bool:
        try:
            db.execute("""
                UPDATE platform_notifications
                SET is_read = TRUE, read_at = NOW()
                WHERE id = %s AND is_read = FALSE
            """, (notification_id,))
            return True
        except Exception:
            return False

    @staticmethod
    def mark_all_read(recipient: str) -> int:
        """Mark all unread notifications read for a recipient. Returns count."""
        try:
            rows = db.query(
                "SELECT id FROM platform_notifications WHERE recipient = %s AND is_read = FALSE",
                (recipient,)
            )
            count = len(rows)
            if count:
                db.execute("""
                    UPDATE platform_notifications
                    SET is_read = TRUE, read_at = NOW()
                    WHERE recipient = %s AND is_read = FALSE
                """, (recipient,))
            return count
        except Exception:
            return 0

    @staticmethod
    def unread_count(recipient: str) -> int:
        try:
            row = db.query_one(
                "SELECT COUNT(*) AS cnt FROM platform_notifications WHERE recipient = %s AND is_read = FALSE",
                (recipient,)
            )
            return row["cnt"] if row else 0
        except Exception:
            return 0

    @staticmethod
    def get_all_unread() -> dict[str, int]:
        """Summary of unread counts per recipient."""
        try:
            rows = db.query("""
                SELECT recipient, COUNT(*) AS cnt
                FROM platform_notifications
                WHERE is_read = FALSE
                GROUP BY recipient ORDER BY cnt DESC
            """)
            return {r["recipient"]: r["cnt"] for r in rows}
        except Exception:
            return {}

    # ── Construction-specific notifiers ───────────────────────────────────────

    @staticmethod
    def notify_procurement_delay(
        item_name: str, vendor: str, delay_weeks: int,
        recipient: str = "pm", project_id: int | None = None,
    ) -> int | None:
        return NotificationService.create(
            recipient=recipient,
            notification_type=PROCUREMENT_DELAY,
            title=f"Procurement Delay — {item_name}",
            body=f"{vendor} is delayed {delay_weeks} week(s) on {item_name}. Schedule impact possible.",
            project_id=project_id,
        )

    @staticmethod
    def notify_rfi_open(
        rfi_number: str, subject: str, days_open: int,
        recipient: str = "pm", project_id: int | None = None,
    ) -> int | None:
        return NotificationService.create(
            recipient=recipient,
            notification_type=RFI_OPEN,
            title=f"RFI {rfi_number} Open {days_open}d — {subject[:60]}",
            body=f"RFI {rfi_number} has been open {days_open} days without response.",
            project_id=project_id,
        )

    @staticmethod
    def notify_schedule_impact(
        activity: str, variance_days: int,
        recipient: str = "pm", project_id: int | None = None,
    ) -> int | None:
        return NotificationService.create(
            recipient=recipient,
            notification_type=SCHEDULE_IMPACT,
            title=f"Schedule Impact — {activity} ({'+' if variance_days > 0 else ''}{variance_days}d)",
            body=f"Schedule variance of {variance_days} days detected on '{activity}'.",
            project_id=project_id,
        )

    @staticmethod
    def notify_bid_received(
        package_name: str, vendor: str, amount: float,
        recipient: str = "pm", project_id: int | None = None,
    ) -> int | None:
        return NotificationService.create(
            recipient=recipient,
            notification_type=BID_RECEIVED,
            title=f"Bid Received — {package_name} from {vendor}",
            body=f"{vendor} submitted ${amount:,.0f} for {package_name}.",
            project_id=project_id,
        )

    @staticmethod
    def notify_qa_failure(
        check_name: str, severity: str,
        sop_instance_id: int | None = None,
        recipient: str = "pm", project_id: int | None = None,
    ) -> int | None:
        return NotificationService.create(
            recipient=recipient,
            notification_type=QA_FAILURE,
            title=f"QA Failure [{severity}] — {check_name}",
            body=f"Quality check '{check_name}' failed at severity {severity}.",
            entity_type="sop_instance",
            entity_id=sop_instance_id,
            project_id=project_id,
        )

    @staticmethod
    def notify_safety_hazard(
        hazard_code: str, description: str, risk_level: str,
        sop_instance_id: int | None = None,
        recipient: str = "super", project_id: int | None = None,
    ) -> list[int]:
        nids = []
        for r in [recipient, "Buck Adams"]:
            nid = NotificationService.create(
                recipient=r,
                notification_type=SAFETY_HAZARD,
                title=f"SAFETY [{risk_level}] — {hazard_code}: {description[:60]}",
                body=f"Uncontrolled {risk_level} hazard {hazard_code}: {description}",
                entity_type="sop_instance",
                entity_id=sop_instance_id,
                project_id=project_id,
            )
            if nid:
                nids.append(nid)
        return nids

    # ── Escalation ────────────────────────────────────────────────────────────

    @staticmethod
    def escalate_overdue(escalate_to: str = "Buck Adams") -> list[dict]:
        """Find unread notifications past their escalation threshold and escalate."""
        from datetime import datetime, timedelta
        escalated = []
        for ntype, hours in ESCALATION_HOURS.items():
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            try:
                rows = db.query("""
                    SELECT id, recipient, notification_type, title, delivered_at
                    FROM platform_notifications
                    WHERE notification_type = %s
                      AND is_read = FALSE
                      AND escalation_level = 0
                      AND delivered_at < %s
                """, (ntype, cutoff))
                for row in rows:
                    db.execute("""
                        UPDATE platform_notifications
                        SET escalation_level = 1,
                            escalated_at = NOW(),
                            escalated_to = %s
                        WHERE id = %s
                    """, (escalate_to, row["id"]))
                    NotificationService.create(
                        recipient=escalate_to,
                        notification_type=ntype,
                        title=f"[ESCALATED] {row['title']}",
                        body=f"Escalated — originally sent to {row['recipient']} and unacknowledged for {hours}h.",
                        entity_id=row["id"],
                    )
                    escalated.append({"id": row["id"], "type": ntype, "original_recipient": row["recipient"]})
            except Exception:
                pass
        return escalated
