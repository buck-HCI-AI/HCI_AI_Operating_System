"""
sync_hubspot.py
Daily read sync — pulls all HubSpot deals, notes, and tasks into Postgres + Qdrant.
Read-only from HubSpot. No writes back.
Scheduled: 6:50 AM daily (before morning brief).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

import psycopg2, psycopg2.extras
from datetime import datetime
from hubspot import _request, get_owner_name
from memory_utils import upsert_one

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)


def pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


# ── Pull all deals ─────────────────────────────────────────────────────────────

def get_all_deals():
    props = "dealname,dealstage,amount,closedate,hs_lastmodifieddate,description,hubspot_owner_id"
    results, after = [], None
    while True:
        url = f"/crm/v3/objects/deals?limit=100&properties={props}"
        if after:
            url += f"&after={after}"
        data, err = _request("GET", url)
        if err or not data:
            break
        results.extend(data.get("results", []))
        after = (data.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
    return results


def get_deal_notes(deal_id: str) -> list:
    """Pull recent notes/activities associated with a deal."""
    data, _ = _request("GET",
        f"/crm/v3/objects/deals/{deal_id}/associations/notes?limit=20")
    if not data:
        return []
    note_ids = [r["id"] for r in data.get("results", [])]
    notes = []
    for nid in note_ids[:10]:
        n, _ = _request("GET", f"/crm/v3/objects/notes/{nid}?properties=hs_note_body,hs_timestamp")
        if n:
            notes.append(n)
    return notes


def get_all_tasks(limit: int = 50) -> list:
    data, _ = _request("GET",
        f"/crm/v3/objects/tasks?limit={limit}"
        f"&properties=hs_task_subject,hs_task_body,hs_task_status,hs_timestamp")
    return (data or {}).get("results", [])


# ── Upsert to Postgres ─────────────────────────────────────────────────────────

STAGE_NAMES = {
    "3524209344": "Not Started",
    "3524209345": "Scope Ready",
    "3524209346": "Sent Out",
    "3524209347": "Bids Receiving",
    "3524209348": "Leveling",
    "3524209349": "Awarded",
    "3524209350": "Not Awarded",
}

def upsert_deal(cur, deal: dict) -> int:
    """Upsert deal into hubspot_deals table (create if not exists)."""
    p = deal.get("properties", {})
    deal_id = deal["id"]
    stage_key = p.get("dealstage", "")
    stage_name = STAGE_NAMES.get(stage_key, stage_key)
    amount = p.get("amount")
    try:
        amount = float(amount) if amount else None
    except (ValueError, TypeError):
        amount = None

    owner = get_owner_name(p.get("hubspot_owner_id")) or p.get("hubspot_owner_id")

    cur.execute("""
        INSERT INTO hubspot_deals (hubspot_deal_id, deal_name, stage, amount,
                                   close_date, last_modified, raw_properties, owner, synced_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (hubspot_deal_id) DO UPDATE SET
            deal_name     = EXCLUDED.deal_name,
            stage         = EXCLUDED.stage,
            amount        = EXCLUDED.amount,
            close_date    = EXCLUDED.close_date,
            last_modified = EXCLUDED.last_modified,
            raw_properties= EXCLUDED.raw_properties,
            owner         = COALESCE(EXCLUDED.owner, hubspot_deals.owner),
            synced_at     = NOW()
        RETURNING id
    """, (
        deal_id,
        p.get("dealname", ""),
        stage_name,
        amount,
        p.get("closedate"),
        p.get("hs_lastmodifieddate"),
        json.dumps(p),
        owner,
    ))
    return cur.fetchone()["id"]


def ensure_hubspot_tables(cur):
    """Create sync tables if they don't exist."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hubspot_deals (
            id               SERIAL PRIMARY KEY,
            hubspot_deal_id  TEXT UNIQUE NOT NULL,
            deal_name        TEXT,
            stage            TEXT,
            amount           NUMERIC,
            close_date       TEXT,
            last_modified    TEXT,
            raw_properties   JSONB,
            synced_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hubspot_notes (
            id              SERIAL PRIMARY KEY,
            hubspot_note_id TEXT UNIQUE NOT NULL,
            deal_id         TEXT,
            body            TEXT,
            note_timestamp  TEXT,
            synced_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hubspot_tasks (
            id               SERIAL PRIMARY KEY,
            hubspot_task_id  TEXT UNIQUE NOT NULL,
            subject          TEXT,
            body             TEXT,
            status           TEXT,
            due_timestamp    TEXT,
            synced_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)


# ── Main sync ─────────────────────────────────────────────────────────────────

def run() -> dict:
    print("\n=== HubSpot Daily Sync ===")
    result = {"deals": 0, "notes": 0, "tasks": 0, "vectors": 0, "errors": []}

    conn = pg()
    cur  = conn.cursor()

    try:
        ensure_hubspot_tables(cur)
        conn.commit()

        # 1 — Deals
        deals = get_all_deals()
        print(f"  Fetched {len(deals)} deals from HubSpot")
        for deal in deals:
            try:
                row_id = upsert_deal(cur, deal)
                p = deal.get("properties", {})
                deal_name = p.get("dealname", "")
                stage = STAGE_NAMES.get(p.get("dealstage", ""), "unknown")
                amount = p.get("amount", "")
                desc = p.get("description", "")

                # Ingest into Qdrant project_memory — offset 20000 for deal vectors
                text = (
                    f"HubSpot deal: {deal_name}. "
                    f"Stage: {stage}. "
                    f"Amount: {'$' + str(amount) if amount else 'not set'}. "
                    f"Description: {desc or 'none'}."
                )
                upsert_one("project_memory", 20000 + int(deal["id"]), text, {
                    "type":        "hubspot_deal",
                    "deal_id":     deal["id"],
                    "deal_name":   deal_name,
                    "stage":       stage,
                    "amount":      float(amount) if amount else 0,
                })
                result["deals"] += 1
                result["vectors"] += 1
            except Exception as e:
                result["errors"].append(f"deal {deal.get('id')}: {e}")

        conn.commit()
        print(f"  ✓ {result['deals']} deals synced")

        # 2 — Notes (top 5 deals only — avoid API rate limits)
        for deal in deals[:5]:
            notes = get_deal_notes(deal["id"])
            for n in notes:
                try:
                    p = n.get("properties", {})
                    cur.execute("""
                        INSERT INTO hubspot_notes (hubspot_note_id, deal_id, body, note_timestamp)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (hubspot_note_id) DO UPDATE SET
                            body = EXCLUDED.body, synced_at = NOW()
                    """, (n["id"], deal["id"], p.get("hs_note_body", ""), p.get("hs_timestamp")))
                    result["notes"] += 1
                except Exception as e:
                    result["errors"].append(f"note {n.get('id')}: {e}")
        conn.commit()
        print(f"  ✓ {result['notes']} notes synced")

        # 3 — Tasks
        tasks = get_all_tasks()
        for t in tasks:
            try:
                p = t.get("properties", {})
                cur.execute("""
                    INSERT INTO hubspot_tasks (hubspot_task_id, subject, body, status, due_timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (hubspot_task_id) DO UPDATE SET
                        status = EXCLUDED.status, synced_at = NOW()
                """, (t["id"], p.get("hs_task_subject"), p.get("hs_task_body"),
                      p.get("hs_task_status"), p.get("hs_timestamp")))
                result["tasks"] += 1
            except Exception as e:
                result["errors"].append(f"task {t.get('id')}: {e}")
        conn.commit()
        print(f"  ✓ {result['tasks']} tasks synced")

    except Exception as e:
        conn.rollback()
        result["errors"].append(str(e))
        import traceback; traceback.print_exc()
    finally:
        cur.close()
        conn.close()

    result["status"] = "success" if not result["errors"] else "partial"
    print(f"  ✓ HubSpot sync complete — {result['vectors']} vectors, {len(result['errors'])} errors")
    return result


if __name__ == "__main__":
    run()
