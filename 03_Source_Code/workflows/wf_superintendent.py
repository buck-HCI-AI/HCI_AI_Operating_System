"""
WF-SUPER: Superintendent Daily Log
7-stage pipeline: Save → Embed → Analyze Schedule → Flag Risks → Invalidate Cache → Log Event → Return

Absorbs WF-004. wf004_daily_log.py is now a thin wrapper around this module.
Accepts project_number (string like '64EW') instead of project_id (int).
"""
import sys, os, json, re, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
from memory_utils import upsert_one

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)


def _resolve_project(cur, project_number: str):
    m = re.match(r'^(\d+)', str(project_number).upper())
    prefix = m.group(1) if m else project_number
    cur.execute(
        "SELECT id, name FROM projects WHERE name ILIKE %s OR address ILIKE %s LIMIT 1",
        (f"{prefix}%", f"{prefix}%")
    )
    row = cur.fetchone()
    return (row["id"], row["name"]) if row else (None, None)


def _write_event(conn, project_id, event_type, payload):
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO workflow_events (workflow_id, project_id, event_type, payload) "
            "VALUES ('WF-SUPER', %s, %s, %s::jsonb)",
            (project_id, event_type, json.dumps(payload))
        )
        conn.commit()
    except Exception:
        pass


def run(
    project_number: str,
    work_performed: str,
    log_date: str = None,
    weather: str = "",
    temp_high: int = None,
    temp_low: int = None,
    crew_on_site: list = None,
    deliveries: list = None,
    inspections: list = None,
    quality_notes: str = "",
    safety_notes: str = "",
    subcontractor_progress: str = "",
    constraints: list = None,
    lookahead: str = "",
    field_risks: list = None,
    issues: str = "",
    photos_count: int = 0,
    logged_by: str = "Buck Adams",
) -> dict:
    if not log_date:
        log_date = datetime.date.today().isoformat()
    crew_on_site  = crew_on_site  or []
    deliveries    = deliveries    or []
    inspections   = inspections   or []
    constraints   = constraints   or []
    field_risks   = field_risks   or []

    result = {"project": project_number, "date": log_date, "steps": []}

    conn = psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)
    cur  = conn.cursor()

    try:
        # Stage 1: Resolve project
        project_id, project_name = _resolve_project(cur, project_number)
        if not project_id:
            return {**result, "status": "failed", "error": f"Project '{project_number}' not found"}
        result["project"] = project_name or project_number

        # Stage 2: Save to daily_logs
        cur.execute("""
            INSERT INTO daily_logs (
                project_id, log_date, weather, temp_high, temp_low,
                crew_on_site, work_performed, issues, photos_count, logged_by,
                manpower, deliveries, inspections, quality_notes, safety_notes,
                subcontractor_progress, constraints, lookahead, field_risks
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            ) RETURNING id
        """, (
            project_id, log_date, weather or None, temp_high, temp_low,
            json.dumps(crew_on_site), work_performed, issues or None, photos_count, logged_by,
            json.dumps(crew_on_site),
            json.dumps(deliveries),
            json.dumps(inspections),
            quality_notes or None,
            safety_notes or None,
            subcontractor_progress or None,
            json.dumps(constraints),
            lookahead or None,
            json.dumps(field_risks),
        ))
        log_id = cur.fetchone()["id"]
        conn.commit()
        result["log_id"] = log_id
        result["saved"]  = True
        result["steps"].append(f"Saved daily_log id={log_id}")

        # Stage 3: Embed into Qdrant project_memory
        risk_str = "; ".join(str(r) for r in field_risks) if field_risks else "none"
        constr_str = "; ".join(str(c) for c in constraints) if constraints else "none"
        embed_text = (
            f"Daily log {log_date} — {project_name}. "
            f"Work performed: {work_performed}. "
            f"Issues: {issues or 'none'}. "
            f"Subcontractor progress: {subcontractor_progress or 'not reported'}. "
            f"Constraints: {constr_str}. Field risks: {risk_str}. "
            f"Lookahead: {lookahead or 'not provided'}. "
            f"Weather: {weather or 'not recorded'}, {temp_high or '?'}F/{temp_low or '?'}F. "
            f"Quality: {quality_notes or 'no issues'}. Safety: {safety_notes or 'no issues'}. "
            f"Logged by: {logged_by}."
        )
        upsert_one("project_memory", 10000 + log_id, embed_text, {
            "type": "daily_log", "log_id": log_id,
            "project_id": project_id, "project_number": project_number,
            "log_date": log_date, "logged_by": logged_by,
        })
        result["steps"].append("Embedded in Qdrant project_memory")

        # Stage 4: Schedule analysis
        schedule_analysis = {}
        try:
            for p in [
                os.path.join(os.path.dirname(__file__), "..", "api"),
                os.path.join(os.path.dirname(__file__), "..", "services"),
                os.path.join(os.path.dirname(__file__), "..", "services", "schedule_intelligence"),
            ]:
                if p not in sys.path:
                    sys.path.insert(0, p)
            from schedule_intelligence_svc import ScheduleIntelligenceService
            schedule_analysis = ScheduleIntelligenceService.analyze_log(log_id)
            result["steps"].append("Schedule analysis complete")
        except Exception as e:
            schedule_analysis = {"skipped": True, "reason": str(e)}
            result["steps"].append(f"Schedule analysis skipped: {e}")
        result["schedule_analysis"] = schedule_analysis

        # Stage 5: Flag field risks and constraints to risks table
        risks_written = 0
        for risk_text in [str(r) for r in field_risks + constraints if r]:
            cur.execute("""
                INSERT INTO risks (project_id, risk_type, severity, description, status, identified_date)
                VALUES (%s, 'field_risk', 'medium', %s, 'open', %s)
            """, (project_id, risk_text, log_date))
            risks_written += 1
        if risks_written:
            conn.commit()
        result["risks_written"] = risks_written
        result["steps"].append(f"Risks flagged: {risks_written}")

        # Stage 6: Invalidate Project Brain cache
        try:
            import redis
            redis_kwargs = dict(
                host=os.environ.get("REDIS_HOST", "localhost"),
                port=int(os.environ.get("REDIS_PORT", 6379)),
                decode_responses=True,
            )
            if os.environ.get("REDIS_PASSWORD"):
                redis_kwargs["password"] = os.environ["REDIS_PASSWORD"]
            r = redis.Redis(**redis_kwargs)
            prefix_key = re.sub(r'[^a-z0-9]', '', project_number.lower())[:6]
            keys = list(r.keys(f"pb:*{prefix_key}*") or []) + list(r.keys(f"pb:*{project_id}*") or [])
            unique_keys = list(set(keys))
            if unique_keys:
                r.delete(*unique_keys)
            result["steps"].append(f"Project Brain cache invalidated ({len(unique_keys)} keys)")
        except Exception as e:
            result["steps"].append(f"Cache invalidation skipped: {e}")
        result["project_brain_cache"] = "invalidated"

        # Stage 7: Log workflow event
        _write_event(conn, project_id, "daily_log_submitted", {
            "log_id": log_id, "log_date": log_date, "risks_written": risks_written,
        })
        result["steps"].append("workflow_events logged")

        # Stage 8: Schedule variance alert (if high/critical)
        sa = result.get("schedule_analysis", {})
        if isinstance(sa, dict) and sa.get("risk_level") in ("high", "critical"):
            try:
                from wf_report import schedule_variance_alert
                sv = __import__("psycopg2").connect(**DB, cursor_factory=__import__("psycopg2.extras", fromlist=["RealDictCursor"]).RealDictCursor)
                sv_cur = sv.cursor()
                sv_cur.execute(
                    "SELECT id FROM schedule_variance WHERE daily_log_id=%s ORDER BY detected_at DESC LIMIT 1",
                    (log_id,)
                )
                sv_row = sv_cur.fetchone()
                sv.close()
                if sv_row:
                    # send=False since 2026-07-01 incident (ADR-011) — draft only, no
                    # autonomous send. Re-enable per-call only after Buck confirms.
                    schedule_variance_alert(sv_row["id"], send=False)
                    result["steps"].append("Schedule variance alert drafted (pending approval)")
            except Exception as e:
                result["steps"].append(f"Variance alert skipped: {e}")

        # Stage 9: Daily field report email (non-blocking)
        try:
            from wf_report import daily_field_report
            # send=False since 2026-07-01 incident (ADR-011) — draft only, no autonomous send.
            rpt = daily_field_report(log_id, send=False)
            result["steps"].append(f"Daily field report: {rpt.get('status','?')}")
            result["report_sent"] = rpt.get("email_sent", False)
        except Exception as e:
            result["steps"].append(f"Daily field report skipped: {e}")

        result["status"] = "success"

    except Exception as e:
        conn.rollback()
        result["error"]  = str(e)
        result["status"] = "failed"
    finally:
        cur.close()
        conn.close()

    return result
