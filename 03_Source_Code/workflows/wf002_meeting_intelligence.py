"""
WF-002: Meeting Intelligence
Parses meeting notes → extracts action items → logs to Postgres + Qdrant + HubSpot tasks.
"""
import sys, os, re, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import psycopg2, psycopg2.extras, json
from datetime import date, timedelta
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
from hubspot import create_task
from memory_utils import upsert_one

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

# Lines matching these patterns are extracted as action items
ACTION_PATTERNS = [
    r"^[-*]\s*ACTION[:\s]+(.+)",
    r"^[-*]\s*TODO[:\s]+(.+)",
    r"^[-*]\s*FOLLOW.?UP[:\s]+(.+)",
    r"^ACTION[:\s]+(.+)",
    r"^TODO[:\s]+(.+)",
]


def _extract_actions(notes: str) -> list[str]:
    actions = []
    for line in notes.splitlines():
        line = line.strip()
        for pattern in ACTION_PATTERNS:
            m = re.match(pattern, line, re.IGNORECASE)
            if m:
                actions.append(m.group(1).strip())
                break
    return actions


def run(
    project_id: int,
    title: str,
    notes: str,
    meeting_date: str = None,          # YYYY-MM-DD, defaults to today
    attendees: list = None,
    meeting_type: str = "site_meeting",
    create_hs_tasks: bool = True,
    due_days: int = 3,
) -> dict:
    """
    Process meeting notes and log everything.
    Returns: {meeting_id, action_items, hs_tasks_created}
    """
    if not meeting_date:
        meeting_date = date.today().isoformat()
    attendees = attendees or []

    action_items = _extract_actions(notes)
    result = {
        "title":        title,
        "meeting_date": meeting_date,
        "action_items": action_items,
        "steps":        [],
    }

    conn = psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)
    cur  = conn.cursor()

    try:
        # 1 — Insert meeting into Postgres
        cur.execute("""
            INSERT INTO meetings (project_id, meeting_type, title, meeting_date,
                                  attendees, summary, action_items)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            project_id, meeting_type, title, meeting_date,
            json.dumps(attendees),
            notes[:2000],
            json.dumps(action_items),
        ))
        meeting_id = cur.fetchone()["id"]
        conn.commit()
        result["meeting_id"] = meeting_id
        result["steps"].append(f"Meeting logged: id={meeting_id}")

        # 2 — Ingest into Qdrant meeting_memory
        text = (
            f"Meeting: {title} on {meeting_date}. "
            f"Attendees: {', '.join(attendees) if attendees else 'unspecified'}. "
            f"Notes: {notes[:600]}. "
            f"Action items: {'; '.join(action_items) if action_items else 'none'}."
        )
        upsert_one("meeting_memory", meeting_id, text, {
            "meeting_id":   meeting_id,
            "project_id":   project_id,
            "title":        title,
            "meeting_date": meeting_date,
            "action_count": len(action_items),
        })
        result["steps"].append("Qdrant meeting_memory seeded")

        # 3 — Create HubSpot tasks for each action item
        hs_count = 0
        if create_hs_tasks and action_items:
            due_ms = int((time.time() + due_days * 86400) * 1000)
            for item in action_items:
                t, err = create_task(
                    subject=f"[{title}] {item}",
                    body=f"From meeting on {meeting_date}. Project ID: {project_id}.",
                    due_date_ms=due_ms,
                )
                if t:
                    hs_count += 1
        result["hs_tasks_created"] = hs_count
        result["steps"].append(f"HubSpot tasks created: {hs_count}")
        result["status"] = "success"

    except Exception as e:
        conn.rollback()
        result["error"] = str(e)
        result["status"] = "failed"
    finally:
        cur.close()
        conn.close()

    return result
