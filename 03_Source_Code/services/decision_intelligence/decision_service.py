"""Decision Intelligence Service — stores, queries, and searches decision records."""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

import json
import services.db as db
from base import BaseIntelligenceService


class DecisionIntelligenceService(BaseIntelligenceService):
    SERVICE_NAME = "decision_intelligence"
    STATUS = "active"

    VALID_TYPES = {
        "award", "scope", "risk", "change", "schedule",
        "procurement", "team", "design", "legal", "lessons"
    }

    @classmethod
    def create_decision(cls, project_id: int | None, decision_type: str,
                        decision_date: str, decision_maker: str,
                        context: str, selected_option: str, rationale: str,
                        approver: str | None = None,
                        options_considered: list | None = None,
                        risk_accepted: str | None = None,
                        cost_impact: float | None = None,
                        schedule_impact: int | None = None,
                        related_rfi_ids: list | None = None,
                        related_co_ids: list | None = None) -> dict:
        """Create a new decision record. Required for all award and risk decisions."""
        if decision_type not in cls.VALID_TYPES:
            return {"error": f"Invalid decision_type. Must be one of: {cls.VALID_TYPES}"}

        row = cls.pg_execute_returning("""
            INSERT INTO decision_records
                (project_id, decision_type, decision_date, decision_maker, approver,
                 context, options_considered, selected_option, rationale,
                 risk_accepted, cost_impact, schedule_impact,
                 related_rfi_ids, related_co_ids)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (project_id, decision_type, decision_date, decision_maker, approver,
              context, json.dumps(options_considered) if options_considered else None,
              selected_option, rationale, risk_accepted, cost_impact, schedule_impact,
              related_rfi_ids, related_co_ids))

        # Embed in Qdrant for semantic search
        embed_text = f"{context} {selected_option} {rationale}"
        try:
            import services.vector as vector
            vector.upsert(
                collection="decision_records",
                text=embed_text,
                metadata={
                    "decision_id": row["id"],
                    "project_id": project_id,
                    "decision_type": decision_type,
                    "decision_date": decision_date,
                    "decision_maker": decision_maker,
                }
            )
        except Exception:
            pass  # vector store is best-effort

        return {"decision_id": row["id"], "created_at": str(row["created_at"])}

    @classmethod
    def get_decisions(cls, project_id: int | None = None,
                      decision_type: str | None = None,
                      limit: int = 50) -> list[dict]:
        conditions, params = [], []
        if project_id:
            conditions.append("project_id = %s")
            params.append(project_id)
        if decision_type:
            conditions.append("decision_type = %s")
            params.append(decision_type)
        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        params.append(limit)
        rows = cls.pg_query(f"""
            SELECT id, project_id, decision_type, decision_date, decision_maker,
                   selected_option, rationale, cost_impact, outcome_rating, created_at
            FROM decision_records {where}
            ORDER BY decision_date DESC
            LIMIT %s
        """, params or None)
        return [dict(r) for r in rows]

    @classmethod
    def update_outcome(cls, decision_id: int, outcome: str,
                       outcome_rating: int, lessons_learned: str = "") -> dict:
        """Update a decision record with outcome at project closeout."""
        if not 1 <= outcome_rating <= 5:
            return {"error": "outcome_rating must be 1-5"}
        cls.pg_execute("""
            UPDATE decision_records
            SET outcome = %s, outcome_rating = %s, lessons_learned = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (outcome, outcome_rating, lessons_learned, decision_id))
        return {"decision_id": decision_id, "outcome_recorded": True}

    @classmethod
    def search(cls, query: str, project_id: int | None = None,
               limit: int = 8) -> list[dict]:
        """Semantic search across all decision records."""
        results = super().search(
            query, collection="decision_records", limit=limit,
            project_filter=str(project_id) if project_id else None
        )
        return results

    @classmethod
    def pending_outcomes(cls) -> list[dict]:
        """All decisions where outcome has not yet been recorded."""
        rows = cls.pg_query("""
            SELECT id, project_id, decision_type, decision_date, decision_maker,
                   selected_option
            FROM decision_records
            WHERE outcome IS NULL AND outcome_rating IS NULL
            ORDER BY decision_date DESC
        """)
        return [dict(r) for r in rows]
