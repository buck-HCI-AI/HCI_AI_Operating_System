"""
WF-004: Daily Log — backward-compatible wrapper around WF-SUPER.
Accepts project_id (int) and maps to project_number before delegating.
All new callers should use WF-SUPER directly via POST /api/v1/workflows/wf-super/daily-log.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
from wf_superintendent import run as _super_run

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)


def run(
    project_id: int,
    work_performed: str,
    issues: str = "",
    log_date: str = None,
    weather: str = "",
    temp_high: int = None,
    temp_low: int = None,
    crew_on_site: list = None,
    photos_count: int = 0,
    logged_by: str = "Buck Adams",
) -> dict:
    conn = psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)
    cur  = conn.cursor()
    cur.execute("SELECT name FROM projects WHERE id = %s", (project_id,))
    row = cur.fetchone()
    conn.close()
    project_number = row["name"] if row else str(project_id)

    return _super_run(
        project_number=project_number,
        work_performed=work_performed,
        issues=issues,
        log_date=log_date,
        weather=weather,
        temp_high=temp_high,
        temp_low=temp_low,
        crew_on_site=crew_on_site,
        photos_count=photos_count,
        logged_by=logged_by,
    )
