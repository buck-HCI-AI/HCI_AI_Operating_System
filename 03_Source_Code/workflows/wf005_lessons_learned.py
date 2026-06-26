"""
WF-005: Lessons Learned
Captures project knowledge → Postgres lessons_learned + Qdrant lessons_learned collection.
"""
import sys, os
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

CATEGORIES = [
    "scheduling", "cost_overrun", "vendor_performance", "design_change",
    "site_condition", "permit", "weather", "communication", "quality",
    "safety", "procurement", "other"
]


def run(
    title: str,
    description: str,
    project_id: int = None,
    vendor_id: int = None,
    csi_division: str = "",
    category: str = "other",
    outcome: str = "",
    action_taken: str = "",
    future_recommendation: str = "",
    recorded_by: str = "Buck Adams",
) -> dict:
    """
    Record a lesson learned.
    Returns: {lesson_id, status}
    """
    result = {"title": title, "steps": []}

    conn = psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)
    cur  = conn.cursor()

    try:
        # 1 — Insert into Postgres
        cur.execute("""
            INSERT INTO lessons_learned (project_id, vendor_id, csi_division, category,
                                         title, description, outcome, action_taken,
                                         future_recommendation, recorded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            project_id, vendor_id, csi_division, category,
            title, description, outcome, action_taken,
            future_recommendation, recorded_by,
        ))
        lesson_id = cur.fetchone()["id"]
        conn.commit()
        result["lesson_id"] = lesson_id
        result["steps"].append(f"Lesson inserted: id={lesson_id}")

        # 2 — Ingest into Qdrant lessons_learned
        text = (
            f"Lesson: {title}. "
            f"Category: {category}. CSI: {csi_division or 'general'}. "
            f"Description: {description}. "
            f"Outcome: {outcome or 'not specified'}. "
            f"Action taken: {action_taken or 'none'}. "
            f"Future recommendation: {future_recommendation or 'none'}."
        )
        upsert_one("lessons_learned", lesson_id, text, {
            "lesson_id":    lesson_id,
            "project_id":   project_id,
            "vendor_id":    vendor_id,
            "title":        title,
            "category":     category,
            "csi_division": csi_division,
        })
        result["steps"].append("Qdrant lessons_learned seeded")
        result["status"] = "success"

    except Exception as e:
        conn.rollback()
        result["error"] = str(e)
        result["status"] = "failed"
    finally:
        cur.close()
        conn.close()

    return result
