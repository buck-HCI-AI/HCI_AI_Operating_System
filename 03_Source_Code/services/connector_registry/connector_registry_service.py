"""
Connector Registry Service — MVP Sprint 1
Tracks which external sources (Drive, HubSpot, Houzz, Outlook) are registered per project.
All connectors start read_only=True. Write access requires Buck approval.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
from datetime import datetime, timezone

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

VALID_SOURCES = ["google_drive", "hubspot", "houzz", "outlook"]


def _pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


class ConnectorRegistryService:

    @classmethod
    def register(cls, project_id: int, project_code: str, source_system: str,
                 source_reference: str, notes: str = "", sync_config: dict = None) -> dict:
        """Register a source connection for a project. Always read_only=True initially."""
        if source_system not in VALID_SOURCES:
            return {"error": f"Unknown source_system. Must be one of {VALID_SOURCES}"}

        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO connector_registry
                        (project_id, project_code, source_system, source_reference,
                         connection_status, read_only, sync_config, notes)
                    VALUES (%s, %s, %s, %s, 'registered', TRUE, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id, connection_status
                """, (project_id, project_code, source_system, source_reference,
                      json.dumps(sync_config or {}), notes))
                row = cur.fetchone()
                conn.commit()

        if not row:
            return {"status": "already_registered", "source_system": source_system,
                    "project_code": project_code}
        return {"connector_id": row["id"], "status": row["connection_status"],
                "read_only": True, "source_system": source_system, "project_code": project_code}

    @classmethod
    def update_status(cls, connector_id: int, status: str, record_count: int = None) -> dict:
        updates = ["connection_status = %s", "updated_at = NOW()"]
        values = [status]
        if status == "confirmed":
            updates.append("last_discovered = NOW()")
        if record_count is not None:
            updates.append("record_count = %s"); values.append(record_count)
        values.append(connector_id)
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE connector_registry SET {', '.join(updates)} WHERE id = %s RETURNING id, connection_status",
                    values
                )
                row = cur.fetchone()
                conn.commit()
        return dict(row) if row else {"error": "Not found"}

    @classmethod
    def initialize_pilot_projects(cls) -> dict:
        """Register all known source connections for the 3 pilot projects."""
        registrations = []

        pilot_connectors = [
            # 64 Eastwood
            (1, "64EW", "hubspot",      "332246098523", "HubSpot deal for 64 Eastwood"),
            (1, "64EW", "google_drive", "HCI AI - Master /64 Eastwood", "Drive folder for 64 Eastwood"),
            (1, "64EW", "houzz",        "64-eastwood",  "Houzz project for 64 Eastwood"),
            # 101 Francis
            (2, "101F", "hubspot",      "332313009897", "HubSpot deal for 101 Francis"),
            (2, "101F", "google_drive", "HCI AI - Master /101 Francis", "Drive folder for 101 Francis"),
            (2, "101F", "houzz",        "101-francis",  "Houzz project for 101 Francis"),
            # 1355 Riverside
            (3, "1355R", "hubspot",     "1355-riverside", "HubSpot deal for 1355 Riverside"),
            (3, "1355R", "google_drive","HCI AI - Master /1355 Riverside", "Drive folder for 1355 Riverside"),
            (3, "1355R", "houzz",       "1355-riverside", "Houzz project for 1355 Riverside"),
        ]

        for project_id, code, source, ref, notes in pilot_connectors:
            result = cls.register(project_id, code, source, ref, notes)
            registrations.append({
                "project_code": code, "source_system": source,
                "result": result.get("status", result.get("connector_id", "error"))
            })

        return {"registrations": registrations, "total": len(registrations)}

    @classmethod
    def get_connectors(cls, project_id: int = None, source_system: str = None) -> list:
        clauses = []
        values = []
        if project_id:
            clauses.append("project_id = %s"); values.append(project_id)
        if source_system:
            clauses.append("source_system = %s"); values.append(source_system)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM connector_registry {where} ORDER BY project_id, source_system",
                    values
                )
                return [dict(r) for r in cur.fetchall()]

    @classmethod
    def summary(cls) -> dict:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT source_system, connection_status, COUNT(*) as count
                    FROM connector_registry GROUP BY source_system, connection_status
                """)
                rows = cur.fetchall()
                cur.execute("SELECT COUNT(*) as total FROM connector_registry")
                total = cur.fetchone()["total"]
        return {"total": total, "by_source": [dict(r) for r in rows]}
