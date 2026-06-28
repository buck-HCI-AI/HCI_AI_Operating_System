"""Schedule Intelligence Service — project schedules, milestones, lookahead, variance analysis."""
import os, sys, json, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base import BaseIntelligenceService
import services.db as db

SCHEDULE_ANALYSIS_SYSTEM = """You are a construction schedule analyst for Hendrickson Construction.
Analyze daily field log data and identify schedule variance or risk.
Always respond with valid JSON only — no prose, no markdown, just the JSON object."""


class ScheduleIntelligenceService(BaseIntelligenceService):
    SERVICE_NAME = "schedule_intelligence"
    STATUS = "active"

    @staticmethod
    def project_schedule(project_number: str) -> dict:
        pid = ScheduleIntelligenceService.resolve_project_id(project_number)
        if not pid:
            return {"error": f"Project {project_number} not found"}
        project = ScheduleIntelligenceService.pg_one(
            "SELECT id, name FROM projects WHERE id = %s", (pid,))

        schedule_items = ScheduleIntelligenceService.pg_query("""
            SELECT hsi.* FROM project_schedule_items hsi
            WHERE hsi.project_id = %s::text ORDER BY hsi.start_date
        """, (project["id"],)) if ScheduleIntelligenceService.pg_one(
            "SELECT 1 FROM pg_tables WHERE tablename='project_schedule_items' AND schemaname='public'") else []

        daily_logs = ScheduleIntelligenceService.pg_query("""
            SELECT log_date, work_performed, weather, subcontractor_progress,
                   constraints, field_risks, lookahead
            FROM daily_logs WHERE project_id = %s ORDER BY log_date DESC LIMIT 14
        """, (project["id"],))

        recent_variance = ScheduleIntelligenceService.pg_query("""
            SELECT activity_name, risk_level, variance_days, cause, recovery_action, detected_at
            FROM schedule_variance WHERE project_id = %s
            ORDER BY detected_at DESC LIMIT 5
        """, (project["id"],))

        return {
            "project_number": project_number,
            "schedule_items": schedule_items,
            "recent_progress": daily_logs,
            "recent_variance": recent_variance,
            "note": "Full CPM schedule integration planned (MS Project / Procore)"
        }

    @staticmethod
    def analyze_log(daily_log_id: int) -> dict:
        """Analyze a submitted daily log for schedule variance using Claude Haiku.
        Writes detected variance to schedule_variance table.
        Writes high/critical risks to risks table.
        Called automatically by WF-SUPER on each log submission."""
        log = ScheduleIntelligenceService.pg_one("""
            SELECT dl.*, p.name AS project_name
            FROM daily_logs dl JOIN projects p ON p.id = dl.project_id
            WHERE dl.id = %s
        """, (daily_log_id,))
        if not log:
            return {"error": f"Log {daily_log_id} not found", "risk_level": "none"}

        # Get recent schedule items for context (table may not exist yet)
        schedule_items = []
        if ScheduleIntelligenceService.pg_one(
            "SELECT 1 FROM pg_tables WHERE tablename='project_schedule_items' AND schemaname='public'"
        ):
            schedule_items = ScheduleIntelligenceService.pg_query("""
                SELECT hsi.title AS item_name, hsi.start_date, hsi.end_date, hsi.status
                FROM project_schedule_items hsi
                WHERE hsi.project_id = %s::text AND hsi.end_date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY hsi.start_date LIMIT 10
            """, (log["project_id"],))
        schedule_context = "\n".join([
            f"- {s['item_name']}: {s['start_date']} to {s['end_date']} ({s['status']})"
            for s in schedule_items
        ]) if schedule_items else "No schedule items on file."

        constraints = log.get("constraints") or []
        field_risks = log.get("field_risks") or []
        if isinstance(constraints, str):
            try: constraints = json.loads(constraints)
            except: constraints = [constraints]
        if isinstance(field_risks, str):
            try: field_risks = json.loads(field_risks)
            except: field_risks = [field_risks]

        prompt = f"""Daily field log — {log['project_name']} — {log['log_date']}:
Work performed: {log.get('work_performed', '')}
Subcontractor progress: {log.get('subcontractor_progress') or 'not reported'}
Constraints: {', '.join(str(c) for c in constraints) if constraints else 'none'}
Field risks: {', '.join(str(r) for r in field_risks) if field_risks else 'none'}
Lookahead: {log.get('lookahead') or 'not provided'}
Known schedule items:
{schedule_context}

Analyze for schedule variance. Return JSON only:
{{
  "activity_name": "activity affected or General Progress",
  "baseline_status": "what was planned",
  "current_status": "what actually happened",
  "variance_days": 0,
  "variance_pct": 0,
  "cause": "root cause or none",
  "responsible_party": "who is responsible or N/A",
  "risk_level": "none",
  "recovery_action": "recommended recovery or none needed",
  "decision_needed": "decision Buck needs to make or empty string",
  "recommended_notification": "who should be notified or empty string"
}}"""

        try:
            raw = ScheduleIntelligenceService.ask_claude(
                prompt, system=SCHEDULE_ANALYSIS_SYSTEM, max_tokens=600
            )
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not match:
                return {"raw_response": raw, "risk_level": "unknown"}
            analysis = json.loads(match.group(0))

            # Write to schedule_variance if any variance detected
            risk_level = analysis.get("risk_level", "none")
            if risk_level and risk_level != "none":
                db.execute_returning("""
                    INSERT INTO schedule_variance (
                        project_id, daily_log_id, activity_name, baseline_status,
                        current_status, variance_days, variance_pct, cause,
                        responsible_party, risk_level, recovery_action,
                        decision_needed, recommended_notification
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
                """, (
                    log["project_id"], daily_log_id,
                    analysis.get("activity_name"), analysis.get("baseline_status"),
                    analysis.get("current_status"), analysis.get("variance_days", 0),
                    analysis.get("variance_pct", 0), analysis.get("cause"),
                    analysis.get("responsible_party"), risk_level,
                    analysis.get("recovery_action"), analysis.get("decision_needed"),
                    analysis.get("recommended_notification"),
                ))

                # Escalate high/critical to risks table
                if risk_level in ("high", "critical"):
                    db.execute("""
                        INSERT INTO risks (project_id, risk_type, severity, description,
                                           mitigation, status, identified_date)
                        VALUES (%s, 'schedule_variance', %s, %s, %s, 'open', CURRENT_DATE)
                    """, (
                        log["project_id"], risk_level,
                        f"Schedule variance on {log['log_date']}: {analysis.get('cause', '')}",
                        analysis.get("recovery_action"),
                    ))

            return analysis

        except Exception as e:
            return {"error": str(e), "risk_level": "unknown"}

    @staticmethod
    def recent_variance(project_number: str, limit: int = 10) -> dict:
        pid = ScheduleIntelligenceService.resolve_project_id(project_number)
        if not pid:
            return {"error": f"Project {project_number} not found"}
        rows = ScheduleIntelligenceService.pg_query("""
            SELECT sv.*, dl.log_date FROM schedule_variance sv
            LEFT JOIN daily_logs dl ON dl.id = sv.daily_log_id
            WHERE sv.project_id = %s ORDER BY sv.detected_at DESC LIMIT %s
        """, (pid, limit))
        return {"project_number": project_number, "variance_records": rows, "total": len(rows)}

    @staticmethod
    def search(query: str) -> dict:
        results = BaseIntelligenceService.search(query, collection="drive_memory", limit=8)
        return {"query": query, "results": results}
