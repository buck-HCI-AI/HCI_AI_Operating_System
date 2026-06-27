"""
Autonomy Backlog Service — /api/v1/services/autonomy

Self-improvement loop: detect manual tasks → log opportunity → estimate ROI →
prioritize → implement autonomously or queue for sprint.

Endpoints:
  POST /opportunity         — log a new automation opportunity (Claude Code, miners, etc.)
  GET  /opportunities       — list all opportunities sorted by ROI score
  GET  /report              — weekly top-3 opportunities report
  POST /opportunities/{id}/status  — update status (in_progress/complete/deferred)
  GET  /backlog             — filtered view: backlog items only
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

router = APIRouter()

_DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)


def _pg():
    return psycopg2.connect(**_DB, cursor_factory=psycopg2.extras.RealDictCursor)


def _q(sql, params=None):
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]


def _run(sql, params=None):
    with _pg() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            try:
                result = cur.fetchone()
                return dict(result) if result else {}
            except Exception:
                return {}


class OpportunityPayload(BaseModel):
    title: str
    description: Optional[str] = None
    detected_by: Optional[str] = "claude_code"
    category: Optional[str] = "repetitive_task"
    current_process: Optional[str] = None
    proposed_automation: Optional[str] = None
    estimated_minutes_per_week: Optional[float] = None
    frequency_per_week: Optional[float] = 1.0
    feasibility: Optional[str] = "medium"
    sprint_target: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str
    implementation_notes: Optional[str] = None
    approved_by: Optional[str] = None


@router.get("")
def service_info():
    return {
        "service": "autonomy",
        "description": "Self-improvement loop — detect, log, and prioritize automation opportunities",
        "endpoints": {
            "POST /opportunity": "Log a new automation opportunity",
            "GET  /opportunities": "List all opportunities sorted by ROI",
            "GET  /report": "Weekly top-3 opportunities report",
            "GET  /backlog": "Backlog items only",
        },
    }


@router.post("/opportunity")
def log_opportunity(payload: OpportunityPayload):
    """Log a new automation opportunity. Claude Code calls this whenever it detects a manual task."""
    # Generate next AUTO-NNN ID
    row = _run("SELECT COUNT(*) as cnt FROM autonomy_opportunities")
    next_num = (row.get("cnt") or 0) + 1
    opp_id = f"AUTO-{next_num:03d}"

    _run("""
        INSERT INTO autonomy_opportunities
            (opportunity_id, title, description, detected_by, category,
             current_process, proposed_automation,
             estimated_minutes_per_week, frequency_per_week,
             feasibility, sprint_target, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'backlog')
        ON CONFLICT (opportunity_id) DO NOTHING
    """, (
        opp_id, payload.title, payload.description, payload.detected_by,
        payload.category, payload.current_process, payload.proposed_automation,
        payload.estimated_minutes_per_week, payload.frequency_per_week,
        payload.feasibility, payload.sprint_target,
    ))

    _update_backlog_file()

    return {
        "opportunity_id": opp_id,
        "title": payload.title,
        "roi_score": round((payload.estimated_minutes_per_week or 0) * (payload.frequency_per_week or 1), 1),
        "message": "Opportunity logged and added to AUTONOMY_BACKLOG.md",
    }


@router.get("/opportunities")
def list_opportunities(status: Optional[str] = None, category: Optional[str] = None):
    wheres = []
    params = []
    if status:
        wheres.append("status = %s"); params.append(status)
    if category:
        wheres.append("category = %s"); params.append(category)
    where_sql = ("WHERE " + " AND ".join(wheres)) if wheres else ""
    rows = _q(f"""
        SELECT opportunity_id, title, category, estimated_minutes_per_week,
               frequency_per_week, roi_score, feasibility, status, sprint_target,
               created_at
        FROM autonomy_opportunities
        {where_sql}
        ORDER BY roi_score DESC NULLS LAST, created_at
    """, params or None)
    total_roi = sum(float(r.get("roi_score") or 0) for r in rows)
    total_hrs = round(total_roi / 60, 1)
    return {
        "opportunities": rows,
        "total": len(rows),
        "total_roi_minutes_per_week": round(total_roi, 1),
        "total_roi_hours_per_week": total_hrs,
    }


@router.get("/backlog")
def backlog():
    rows = _q("""
        SELECT opportunity_id, title, category, roi_score, feasibility,
               estimated_minutes_per_week, frequency_per_week, proposed_automation
        FROM autonomy_opportunities
        WHERE status = 'backlog'
        ORDER BY roi_score DESC NULLS LAST
    """)
    return {"backlog": rows, "count": len(rows)}


@router.get("/report")
def weekly_report():
    """
    Top automation opportunities for executive review.
    Delivered Sunday 19:00 via n8n AUTO-WEEKLY-REPORT.
    """
    top = _q("""
        SELECT opportunity_id, title, description, category,
               estimated_minutes_per_week, frequency_per_week, roi_score,
               feasibility, proposed_automation, current_process, sprint_target
        FROM autonomy_opportunities
        WHERE status = 'backlog' AND feasibility IN ('high','medium')
        ORDER BY roi_score DESC NULLS LAST
        LIMIT 3
    """)

    in_progress = _q("""
        SELECT opportunity_id, title, implementation_notes, sprint_target
        FROM autonomy_opportunities
        WHERE status = 'in_progress'
    """)

    completed = _q("""
        SELECT opportunity_id, title, completed_at,
               estimated_minutes_per_week * frequency_per_week as roi_saved
        FROM autonomy_opportunities
        WHERE status = 'complete'
        ORDER BY completed_at DESC
        LIMIT 10
    """)

    total_weekly_savings = sum(float(r.get("roi_score") or 0) for r in completed)

    return {
        "report_date": datetime.now(timezone.utc).date().isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "top_3_opportunities": [
            {
                "id": o["opportunity_id"],
                "title": o["title"],
                "why": o["description"],
                "current": o["current_process"],
                "proposed": o["proposed_automation"],
                "roi_minutes_per_week": float(o.get("roi_score") or 0),
                "roi_hours_per_week": round(float(o.get("roi_score") or 0) / 60, 2),
                "feasibility": o["feasibility"],
                "sprint_target": o["sprint_target"],
            }
            for o in top
        ],
        "in_progress": in_progress,
        "completed_automations": len(completed),
        "cumulative_weekly_savings_minutes": round(total_weekly_savings, 1),
        "cumulative_weekly_savings_hours": round(total_weekly_savings / 60, 1),
    }


@router.post("/opportunities/{opportunity_id}/status")
def update_status(opportunity_id: str, payload: StatusUpdate):
    allowed = {"backlog", "in_progress", "complete", "deferred", "rejected"}
    if payload.status not in allowed:
        raise HTTPException(status_code=422, detail=f"status must be one of {allowed}")

    extras = ""
    params = [payload.status]

    if payload.implementation_notes:
        extras += ", implementation_notes = %s"
        params.append(payload.implementation_notes)
    if payload.approved_by:
        extras += ", approved_by = %s, approved_at = NOW()"
        params.append(payload.approved_by)
    if payload.status == "complete":
        extras += ", completed_at = NOW()"

    params.append(opportunity_id.upper())
    _run(f"""
        UPDATE autonomy_opportunities
        SET status = %s, updated_at = NOW() {extras}
        WHERE opportunity_id = %s
    """, params)

    _update_backlog_file()
    return {"opportunity_id": opportunity_id.upper(), "status": payload.status}


def _update_backlog_file():
    """Keep AUTONOMY_BACKLOG.md in sync with DB state."""
    try:
        rows = _q("""
            SELECT opportunity_id, title, category, roi_score, feasibility,
                   status, estimated_minutes_per_week, frequency_per_week,
                   proposed_automation, sprint_target
            FROM autonomy_opportunities
            ORDER BY
                CASE status WHEN 'in_progress' THEN 0 WHEN 'backlog' THEN 1 ELSE 2 END,
                roi_score DESC NULLS LAST
        """)

        backlog = [r for r in rows if r["status"] == "backlog"]
        in_prog = [r for r in rows if r["status"] == "in_progress"]
        done    = [r for r in rows if r["status"] == "complete"]
        total_roi = sum(float(r.get("roi_score") or 0) for r in backlog)

        lines = [
            "# Autonomy Backlog",
            f"**Auto-generated** | Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | Source: `/api/v1/services/autonomy/opportunities`",
            "",
            f"> **{len(backlog)} opportunities** | Potential savings: **{round(total_roi/60,1)} hrs/week**",
            "",
        ]

        if in_prog:
            lines += ["## In Progress", ""]
            for r in in_prog:
                lines.append(f"- **{r['opportunity_id']}** — {r['title']} (Sprint {r['sprint_target'] or 'TBD'})")
            lines.append("")

        if backlog:
            lines += ["## Backlog (sorted by ROI)", "", "| ID | Title | Category | Hrs/Wk | Feasibility | Sprint |", "|---|---|---|---|---|---|"]
            for r in backlog:
                hrs = round(float(r.get("roi_score") or 0) / 60, 1)
                lines.append(f"| {r['opportunity_id']} | {r['title']} | {r['category']} | {hrs} | {r['feasibility']} | {r['sprint_target'] or 'TBD'} |")
            lines.append("")

        if done:
            lines += ["## Completed", ""]
            for r in done:
                lines.append(f"- ~~{r['opportunity_id']} — {r['title']}~~")
            lines.append("")

        lines.append("*Managed by Claude Code autonomy service. Add opportunities via `POST /api/v1/services/autonomy/opportunity`.*")

        backlog_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "AUTONOMY_BACKLOG.md"
        )
        with open(os.path.abspath(backlog_path), "w") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass
