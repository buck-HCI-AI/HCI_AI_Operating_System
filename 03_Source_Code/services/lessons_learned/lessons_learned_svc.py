"""Lessons Learned Service — searchable institutional knowledge."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from base import BaseIntelligenceService


class LessonsLearnedService(BaseIntelligenceService):
    SERVICE_NAME = "lessons_learned"
    STATUS = "active"

    @staticmethod
    def list_lessons(category: str = None, csi_division: str = None) -> dict:
        conditions, params = [], []
        if category:
            conditions.append("category = %s")
            params.append(category)
        if csi_division:
            conditions.append("csi_division = %s")
            params.append(csi_division)
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        rows = LessonsLearnedService.pg_query(
            f"SELECT * FROM lessons_learned {where} ORDER BY recorded_at DESC LIMIT 100",
            params or None
        )
        return {"lessons": rows, "total": len(rows)}

    @staticmethod
    def search_lessons(query: str) -> dict:
        # Semantic search in Qdrant
        vec_results = BaseIntelligenceService.search(
            query, collection="lessons_learned", limit=8)
        # Also search Postgres text
        pg_results = LessonsLearnedService.pg_query(
            "SELECT * FROM lessons_learned WHERE title ILIKE %s OR description ILIKE %s LIMIT 10",
            (f"%{query}%", f"%{query}%")
        )
        return {"query": query, "semantic_results": vec_results, "text_matches": pg_results}

    @staticmethod
    def add_lesson(title: str, description: str, category: str = "other",
                   csi_division: str = None, project_id: int = None,
                   outcome: str = "", recommendation: str = "") -> dict:
        from services.db import execute_returning
        row = execute_returning("""
            INSERT INTO lessons_learned
                (title, description, category, csi_division, project_id,
                 outcome, future_recommendation)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (title, description, category, csi_division, project_id, outcome, recommendation))
        return {"status": "created", "id": row["id"] if row else None}
