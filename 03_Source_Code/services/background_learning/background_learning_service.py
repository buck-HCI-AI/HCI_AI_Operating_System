"""
Background Learning Service — MVP Sprint 1
Read-only pipeline: Discover → Index → Classify → Extract → Link → Candidates → Review Queue

Safety rules:
  - NEVER modifies, deletes, renames, moves, or writes back to any source system
  - All write actions queued to approval_queue for explicit Buck approval
  - Every record tracked with source system, source ID, project association, confidence, status
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
from datetime import datetime, timezone
from typing import Optional

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

# Background learning status pipeline
STATUS_DISCOVERED              = "Discovered"
STATUS_ACCESS_CONFIRMED        = "Access Confirmed"
STATUS_INDEXED                 = "Indexed"
STATUS_CLASSIFIED              = "Classified"
STATUS_EXTRACTED               = "Extracted"
STATUS_EMBEDDED                = "Embedded"
STATUS_LINKED                  = "Linked to Project Brain"
STATUS_CANDIDATE_CREATED       = "Intelligence Candidate Created"
STATUS_HUMAN_REVIEW_NEEDED     = "Human Review Needed"
STATUS_APPROVED                = "Approved"
STATUS_REJECTED                = "Rejected"
STATUS_ARCHIVED                = "Archived"
STATUS_ERROR                   = "Error"

ALL_STATUSES = [
    STATUS_DISCOVERED, STATUS_ACCESS_CONFIRMED, STATUS_INDEXED, STATUS_CLASSIFIED,
    STATUS_EXTRACTED, STATUS_EMBEDDED, STATUS_LINKED, STATUS_CANDIDATE_CREATED,
    STATUS_HUMAN_REVIEW_NEEDED, STATUS_APPROVED, STATUS_REJECTED, STATUS_ARCHIVED, STATUS_ERROR
]

SOURCE_SYSTEMS = ["google_drive", "hubspot", "houzz", "outlook"]

# Document type classification keywords
_DOC_TYPE_MAP = {
    "drawing":    ["drawing", "dwg", "plan", "floor plan", "elevation", "section", "detail", "sheet"],
    "spec":       ["spec", "specification", "division", "csi"],
    "bid":        ["bid", "proposal", "quote", "pricing", "estimate", "leveling"],
    "budget":     ["budget", "cost", "gcmax", "allowance", "contingency"],
    "schedule":   ["schedule", "gantt", "timeline", "milestone", "lookahead"],
    "meeting":    ["meeting", "minutes", "agenda", "preconstruction", "oac"],
    "photo":      ["photo", "image", "jpg", "jpeg", "png", "picture"],
    "rfi":        ["rfi", "request for information"],
    "submittal":  ["submittal", "shop drawing", "product data"],
    "contract":   ["contract", "agreement", "subcontract", "owner"],
    "closeout":   ["closeout", "punch list", "warranty", "as-built", "lien"],
    "daily_log":  ["daily log", "field report", "daily report"],
}

# Project code → project ID mapping (cached from DB)
_PROJECT_CODES = {
    "64EW": 1, "64 Eastwood": 1, "Eastwood": 1,
    "101F": 2, "101 Francis": 2, "Francis": 2,
    "1355R": 3, "1355 Riverside": 3, "Riverside": 3,
    "83SB": 4, "83 Sagebrusch": 4,
}


def _pg():
    return psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)


def _classify_document_type(name: str) -> str:
    name_lower = name.lower()
    for doc_type, keywords in _DOC_TYPE_MAP.items():
        if any(kw in name_lower for kw in keywords):
            return doc_type
    return "other"


def _infer_project(name: str, url: str = "") -> tuple[Optional[int], Optional[str], float]:
    """Infer project_id from name/url. Returns (project_id, project_association, confidence)."""
    text = (name + " " + url).lower()
    if "eastwood" in text or "64ew" in text:
        return 1, "64 Eastwood", 0.85
    if "francis" in text or "101f" in text or "101 w" in text:
        return 2, "101 Francis", 0.85
    if "riverside" in text or "1355" in text:
        return 3, "1355 Riverside", 0.85
    if "sagebrusch" in text or "83sb" in text:
        return 4, "83 Sagebrusch", 0.7
    return None, None, 0.3


class BackgroundLearningService:

    # ── Discovery: register a new source item ──────────────────────────────────

    @classmethod
    def discover(cls, source_system: str, source_id: str, source_name: str,
                 source_url: str = "", project_id: int = None,
                 metadata: dict = None) -> dict:
        """Register a newly discovered item from an external source."""
        if source_system not in SOURCE_SYSTEMS:
            return {"error": f"Unknown source_system '{source_system}'. Must be one of {SOURCE_SYSTEMS}"}

        pid = project_id
        project_association = None
        confidence = 0.0
        if not pid:
            pid, project_association, confidence = _infer_project(source_name, source_url)
        else:
            for name, id_ in _PROJECT_CODES.items():
                if id_ == pid:
                    project_association = name
                    confidence = 0.9
                    break

        doc_type = _classify_document_type(source_name)

        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO background_learning_records
                        (source_system, source_id, source_name, source_url, project_id,
                         project_association, document_type, status, confidence, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_system, source_id) DO UPDATE SET
                        source_name = EXCLUDED.source_name,
                        source_url  = EXCLUDED.source_url,
                        updated_at  = NOW()
                    RETURNING id, status
                """, (source_system, source_id, source_name, source_url, pid,
                      project_association, doc_type, STATUS_DISCOVERED, confidence,
                      json.dumps(metadata or {})))
                row = cur.fetchone()
                conn.commit()
        return {"record_id": row["id"], "status": row["status"],
                "project_association": project_association, "document_type": doc_type,
                "confidence": float(confidence)}

    # ── Bulk discovery from connector ──────────────────────────────────────────

    @classmethod
    def discover_from_hubspot(cls) -> dict:
        """Read HubSpot deals + contacts in read-only mode and register as BL records."""
        try:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT d.id, d.hubspot_deal_id, d.deal_name, p.id as project_id, p.name as project_name
                        FROM hubspot_deals d
                        LEFT JOIN projects p ON p.hubspot_deal_id = d.hubspot_deal_id
                        LIMIT 100
                    """)
                    deals = cur.fetchall()

            registered = 0
            for deal in deals:
                name = deal["deal_name"] or f"HubSpot Deal {deal['hubspot_deal_id']}"
                result = cls.discover(
                    source_system="hubspot",
                    source_id=str(deal["hubspot_deal_id"]),
                    source_name=name,
                    project_id=deal["project_id"],
                    metadata={"deal_name": name, "hubspot_deal_id": deal["hubspot_deal_id"]}
                )
                if "record_id" in result:
                    registered += 1

            return {"source": "hubspot", "discovered": registered, "status": "complete", "mode": "read_only"}
        except Exception as e:
            return {"source": "hubspot", "error": str(e)}

    @classmethod
    def discover_from_drive(cls) -> dict:
        """Scan drive_sync_log for known files and register as BL records."""
        try:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT file_path, file_name, file_type, synced_at
                        FROM drive_sync_log
                        ORDER BY synced_at DESC LIMIT 200
                    """)
                    files = cur.fetchall()

            registered = 0
            for f in files:
                path = f["file_path"] or ""
                name = f["file_name"] or os.path.basename(path)
                result = cls.discover(
                    source_system="google_drive",
                    source_id=path,
                    source_name=name,
                    source_url=path,
                    metadata={"file_path": path, "file_type": f["file_type"], "synced_at": str(f["synced_at"])}
                )
                if "record_id" in result:
                    registered += 1

            return {"source": "google_drive", "discovered": registered, "status": "complete", "mode": "read_only"}
        except Exception as e:
            return {"source": "google_drive", "error": str(e)}

    @classmethod
    def discover_from_houzz(cls) -> dict:
        """Read Houzz project data (daily logs, schedule items) and register as BL records."""
        try:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT hp.id, hp.project_name, hp.houzz_project_id,
                               p.id as db_project_id
                        FROM houzz_projects hp
                        LEFT JOIN projects p ON p.name ILIKE '%' || split_part(hp.project_name, ' ', 1) || '%'
                        LIMIT 50
                    """)
                    projects = cur.fetchall()

            registered = 0
            for hp in projects:
                result = cls.discover(
                    source_system="houzz",
                    source_id=str(hp["houzz_project_id"] or hp["id"]),
                    source_name=hp["project_name"],
                    project_id=hp["db_project_id"],
                    metadata={"houzz_project_id": hp["houzz_project_id"]}
                )
                if "record_id" in result:
                    registered += 1

            return {"source": "houzz", "discovered": registered, "status": "complete", "mode": "read_only"}
        except Exception as e:
            return {"source": "houzz", "error": str(e)}

    # ── Pipeline advancement ───────────────────────────────────────────────────

    @classmethod
    def advance(cls, record_id: int, new_status: str, updates: dict = None) -> dict:
        """Advance a record through the pipeline to a new status."""
        if new_status not in ALL_STATUSES:
            return {"error": f"Unknown status '{new_status}'"}

        set_clauses = ["status = %s", "updated_at = NOW()"]
        values = [new_status]

        if updates:
            for field in ["title", "summary", "confidence", "document_type",
                          "project_id", "project_association", "error_message",
                          "reviewed_by", "review_status"]:
                if field in updates:
                    set_clauses.append(f"{field} = %s")
                    values.append(updates[field])
            for jsonb_field in ["metadata", "related_documents", "related_vendors",
                                "related_sops", "intelligence_candidates"]:
                if jsonb_field in updates:
                    set_clauses.append(f"{jsonb_field} = %s")
                    values.append(json.dumps(updates[jsonb_field]))

        if new_status == STATUS_HUMAN_REVIEW_NEEDED:
            set_clauses.append("review_status = 'Pending'")
        if new_status in (STATUS_APPROVED, STATUS_REJECTED):
            set_clauses.append("reviewed_at = NOW()")

        values.append(record_id)
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE background_learning_records SET {', '.join(set_clauses)} WHERE id = %s RETURNING id, status",
                    values
                )
                row = cur.fetchone()
                conn.commit()

        if not row:
            return {"error": f"Record {record_id} not found"}
        return {"record_id": row["id"], "status": row["status"]}

    @classmethod
    def extract_and_classify(cls, record_id: int) -> dict:
        """Auto-advance a Discovered/Indexed record through Classified → Extracted."""
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM background_learning_records WHERE id = %s", (record_id,))
                rec = cur.fetchone()
        if not rec:
            return {"error": "Record not found"}

        name = rec["source_name"] or ""
        doc_type = _classify_document_type(name)
        pid, assoc, conf = _infer_project(name, rec["source_url"] or "")

        # Override if already has a project
        if rec["project_id"]:
            pid = rec["project_id"]
            conf = max(float(rec["confidence"] or 0), 0.7)

        candidates = []
        if doc_type == "bid" and pid:
            candidates.append({"type": "bid_record", "description": f"Bid document: {name}", "action": "review_for_bid_intelligence"})
        elif doc_type in ("drawing", "spec") and pid:
            candidates.append({"type": "document_index", "description": f"Technical doc: {name}", "action": "ingest_to_project_brain"})
        elif doc_type == "meeting":
            candidates.append({"type": "meeting_summary", "description": f"Meeting notes: {name}", "action": "extract_action_items"})
        elif doc_type == "daily_log":
            candidates.append({"type": "field_intelligence", "description": f"Daily log: {name}", "action": "analyze_for_schedule_risk"})

        new_status = STATUS_CANDIDATE_CREATED if candidates else STATUS_EXTRACTED
        if candidates:
            new_status = STATUS_HUMAN_REVIEW_NEEDED

        return cls.advance(record_id, new_status, {
            "document_type": doc_type,
            "project_id": pid,
            "project_association": assoc,
            "confidence": conf,
            "intelligence_candidates": candidates,
            "title": name,
            "summary": f"{doc_type.replace('_', ' ').title()} document from {rec['source_system']}",
        })

    # ── Queries ────────────────────────────────────────────────────────────────

    @classmethod
    def get_records(cls, status: str = None, source_system: str = None,
                    project_id: int = None, review_status: str = None,
                    limit: int = 50) -> list:
        clauses = []
        values = []
        if status:
            clauses.append("status = %s"); values.append(status)
        if source_system:
            clauses.append("source_system = %s"); values.append(source_system)
        if project_id:
            clauses.append("project_id = %s"); values.append(project_id)
        if review_status:
            clauses.append("review_status = %s"); values.append(review_status)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        values.append(limit)
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM background_learning_records {where} ORDER BY created_at DESC LIMIT %s",
                    values
                )
                return [dict(r) for r in cur.fetchall()]

    @classmethod
    def summary(cls) -> dict:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT status, COUNT(*) as count
                    FROM background_learning_records
                    GROUP BY status ORDER BY count DESC
                """)
                by_status = {r["status"]: r["count"] for r in cur.fetchall()}
                cur.execute("SELECT COUNT(*) as total FROM background_learning_records")
                total = cur.fetchone()["total"]
                cur.execute("SELECT COUNT(*) as pending FROM background_learning_records WHERE review_status='Pending'")
                pending = cur.fetchone()["pending"]

        return {"total": total, "pending_review": pending, "by_status": by_status}

    @classmethod
    def run_full_discovery(cls) -> dict:
        """Trigger read-only discovery across all connected sources."""
        results = {
            "google_drive": cls.discover_from_drive(),
            "hubspot":      cls.discover_from_hubspot(),
            "houzz":        cls.discover_from_houzz(),
            "mode":         "read_only",
            "timestamp":    datetime.now(timezone.utc).isoformat(),
        }
        total = sum(r.get("discovered", 0) for r in results.values() if isinstance(r, dict))
        results["total_discovered"] = total
        return results
