"""
WF-001: New Project Setup
Creates HubSpot deal + inserts project into Postgres + seeds Qdrant project_memory.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
from hubspot import create_deal, STAGE, PIPELINE_ID
from memory_utils import upsert_one

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)


def run(
    name: str,
    address: str,
    city: str = "Aspen",
    state: str = "CO",
    scope: str = "",
    owner_name: str = "",
    pm_name: str = "",
    super_name: str = "",
    budget_estimate: float = None,
) -> dict:
    """
    Create a new HCI project end-to-end.
    Returns: {project_id, hubspot_deal_id, status}
    """
    result = {"name": name, "steps": []}

    conn = psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)
    cur  = conn.cursor()

    try:
        # 1 — Check for duplicate
        cur.execute("SELECT id FROM projects WHERE name = %s", (name,))
        existing = cur.fetchone()
        if existing:
            return {"error": f"Project '{name}' already exists", "project_id": existing["id"]}

        # 2 — Create HubSpot deal
        hs_deal, hs_err = create_deal(
            name=f"HCI — {name}",
            stage_key="not_started",
            amount=budget_estimate,
        )
        deal_id = hs_deal.get("id") if hs_deal else None
        if deal_id:
            result["steps"].append(f"HubSpot deal created: {deal_id}")
        else:
            result["steps"].append(f"HubSpot deal failed: {hs_err}")

        # 3 — Insert into Postgres
        cur.execute("""
            INSERT INTO projects (name, address, city, state, status, scope,
                                  hubspot_deal_id, owner_name, pm_name, super_name)
            VALUES (%s, %s, %s, %s, 'active', %s, %s, %s, %s, %s)
            RETURNING id
        """, (name, address, city, state, scope, deal_id, owner_name, pm_name, super_name))
        project_id = cur.fetchone()["id"]
        conn.commit()
        result["steps"].append(f"Postgres project inserted: id={project_id}")

        # 4 — Seed Qdrant project_memory
        text = (
            f"Project: {name} at {address}, {city}, {state}. "
            f"Scope: {scope or 'TBD'}. Status: active. "
            f"Owner: {owner_name or 'TBD'}. PM: {pm_name or 'TBD'}. "
            f"This is an active Hendrickson Construction high-end residential project."
        )
        upsert_one("project_memory", project_id, text, {
            "project_id":   project_id,
            "project_name": name,
            "address":      address,
            "scope":        scope,
            "status":       "active",
        })
        result["steps"].append("Qdrant project_memory seeded")

        result.update({"project_id": project_id, "hubspot_deal_id": deal_id, "status": "created"})

    except Exception as e:
        conn.rollback()
        result["error"] = str(e)
        result["status"] = "failed"
    finally:
        cur.close()
        conn.close()

    return result
