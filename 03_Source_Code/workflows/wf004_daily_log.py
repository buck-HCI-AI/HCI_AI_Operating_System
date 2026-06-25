"""
WF-004: Daily Log
Captures jobsite notes → Postgres daily_logs + Qdrant project_memory.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import psycopg2, psycopg2.extras, json
from datetime import date
from memory_utils import upsert_one

DB = dict(host="localhost", port=5432, dbname="hci_os", user="hci_admin", password="hci_postgres_2026")


def run(
    project_id: int,
    work_performed: str,
    issues: str = "",
    log_date: str = None,           # YYYY-MM-DD, defaults to today
    weather: str = "",
    temp_high: int = None,
    temp_low: int = None,
    crew_on_site: list = None,
    photos_count: int = 0,
    logged_by: str = "Buck Adams",
) -> dict:
    """
    Log a daily site report.
    Returns: {log_id, project_id, log_date, status}
    """
    if not log_date:
        log_date = date.today().isoformat()
    crew_on_site = crew_on_site or []

    result = {"project_id": project_id, "log_date": log_date, "steps": []}

    conn = psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)
    cur  = conn.cursor()

    try:
        # 1 — Insert into Postgres
        cur.execute("""
            INSERT INTO daily_logs (project_id, log_date, weather, temp_high, temp_low,
                                    crew_on_site, work_performed, issues, photos_count, logged_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            project_id, log_date, weather or None, temp_high, temp_low,
            json.dumps(crew_on_site), work_performed, issues or None, photos_count, logged_by,
        ))
        log_id = cur.fetchone()["id"]
        conn.commit()
        result["log_id"] = log_id
        result["steps"].append(f"Daily log inserted: id={log_id}")

        # 2 — Ingest into Qdrant project_memory
        crew_str = ", ".join(crew_on_site) if crew_on_site else "not recorded"
        text = (
            f"Daily log {log_date} for project id {project_id}. "
            f"Work performed: {work_performed}. "
            f"Issues: {issues or 'none'}. "
            f"Weather: {weather or 'not recorded'}, high {temp_high or '?'}F / low {temp_low or '?'}F. "
            f"Crew: {crew_str}. Logged by: {logged_by}."
        )
        # Use log_id + 10000 offset to avoid colliding with existing project_memory vectors
        upsert_one("project_memory", 10000 + log_id, text, {
            "type":        "daily_log",
            "log_id":      log_id,
            "project_id":  project_id,
            "log_date":    log_date,
            "logged_by":   logged_by,
        })
        result["steps"].append("Qdrant project_memory updated")
        result["status"] = "success"

    except Exception as e:
        conn.rollback()
        result["error"] = str(e)
        result["status"] = "failed"
    finally:
        cur.close()
        conn.close()

    return result
