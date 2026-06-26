"""Platform Search Gateway Service.

Unified search across Qdrant (semantic) and Postgres (structured).
Routes queries intelligently: entity lookups → Postgres; conceptual queries → Qdrant.
Returns a normalized result list regardless of source.
"""
from __future__ import annotations
import os, sys
import re

_here = os.path.dirname(os.path.abspath(__file__))
_src = os.path.abspath(os.path.join(_here, "..", "..", ".."))
sys.path.insert(0, _src)
sys.path.insert(0, os.path.join(_src, "api"))

import services.db as db

# ── Intent patterns — structured Postgres queries ─────────────────────────────
_VENDOR_PATTERN = re.compile(r"\b(vendor|sub|subcontractor|company|supplier)\b", re.I)
_PROJECT_PATTERN = re.compile(r"\b(project|job|site|address)\b", re.I)
_SOP_PATTERN = re.compile(r"\b(sop|workflow|status|instance)\b", re.I)
_COST_PATTERN = re.compile(r"\b(cost|budget|bid|price|amount|award)\b", re.I)
_RISK_PATTERN = re.compile(r"\b(risk|stop|blocked|critical|hazard)\b", re.I)


def _normalize_result(source: str, score: float, payload: dict, text: str = "",
                      citation: str = "", related_project: str = "",
                      confidence: float | None = None) -> dict:
    return {
        "source":          source,
        "score":           round(score, 4),
        "confidence":      round(confidence if confidence is not None else min(score, 1.0), 4),
        "text":            text or payload.get("title", payload.get("name", "")),
        "citation":        citation,
        "related_project": related_project,
        "payload":         payload,
    }


def _best_keyword(query: str) -> str:
    """Extract the most useful single keyword from a multi-word query for LIKE matching."""
    stopwords = {"the", "a", "an", "in", "of", "for", "to", "and", "or", "is",
                 "find", "show", "get", "list", "search", "what", "who", "where"}
    tokens = [t.strip().lower() for t in query.split() if len(t.strip()) > 2]
    for tok in tokens:
        if tok not in stopwords:
            return tok
    return tokens[0] if tokens else query.lower()


class SearchGateway:
    """Route search queries to the right backend and return normalized results."""

    @staticmethod
    def search(
        query: str,
        sources: list[str] | None = None,
        project_filter: str | None = None,
        limit: int = 10,
        score_threshold: float = 0.3,
    ) -> dict:
        """
        Unified search across all data sources.

        sources: list of ["qdrant", "vendors", "projects", "sops", "bids", "risks"]
                 None = auto-detect from query intent
        """
        all_sources = sources or SearchGateway._detect_sources(query)
        results: list[dict] = []
        sources_queried: list[str] = []
        errors: dict[str, str] = {}

        for src in all_sources:
            try:
                src_results = SearchGateway._query_source(
                    src, query, project_filter, limit, score_threshold
                )
                results.extend(src_results)
                sources_queried.append(src)
            except Exception as e:
                errors[src] = str(e)

        results.sort(key=lambda r: r["score"], reverse=True)
        results = results[:limit]

        return {
            "query":           query,
            "total_results":   len(results),
            "sources_queried": sources_queried,
            "results":         results,
            "errors":          errors or None,
        }

    @staticmethod
    def _detect_sources(query: str) -> list[str]:
        """Detect which sources are most relevant from query text."""
        sources = []
        if _VENDOR_PATTERN.search(query):
            sources.append("vendors")
        if _PROJECT_PATTERN.search(query):
            sources.append("projects")
        if _SOP_PATTERN.search(query):
            sources.append("sops")
        if _COST_PATTERN.search(query):
            sources.extend(["bids", "qdrant_costs"])
        if _RISK_PATTERN.search(query):
            sources.append("risks")
        if not sources:
            sources = ["qdrant_documents", "vendors", "projects"]
        return list(dict.fromkeys(sources))  # dedup, preserve order

    @staticmethod
    def _query_source(
        source: str, query: str, project_filter: str | None, limit: int, score_threshold: float
    ) -> list[dict]:
        if source == "vendors":
            return SearchGateway._search_vendors(query, limit)
        if source == "projects":
            return SearchGateway._search_projects(query, limit)
        if source == "sops":
            return SearchGateway._search_sops(query, limit)
        if source == "bids":
            return SearchGateway._search_bids(query, limit)
        if source == "risks":
            return SearchGateway._search_risks(query, limit)
        if source.startswith("qdrant"):
            col_hint = source.replace("qdrant_", "")
            return SearchGateway._search_qdrant(query, col_hint, project_filter, limit, score_threshold)
        return []

    # ── Postgres source queries ───────────────────────────────────────────────

    @staticmethod
    def _search_vendors(query: str, limit: int) -> list[dict]:
        kw = _best_keyword(query)
        q = f"%{kw}%"
        try:
            rows = db.query("""
                SELECT id, company_name, contact_name, trade, tier, email, phone, csi_divisions
                FROM vendors
                WHERE LOWER(company_name) LIKE %s
                   OR LOWER(trade) LIKE %s
                   OR LOWER(contact_name) LIKE %s
                ORDER BY tier, company_name
                LIMIT %s
            """, (q, q, q, limit))
            return [_normalize_result(
                "vendors", 0.9, dict(r),
                f"{r['company_name']} — {r.get('trade','')} ({r.get('tier','')})",
                citation=f"vendors.id={r['id']}",
                confidence=0.95,
            ) for r in rows]
        except Exception:
            return []

    @staticmethod
    def _search_projects(query: str, limit: int) -> list[dict]:
        kw = _best_keyword(query)
        q = f"%{kw}%"
        try:
            rows = db.query("""
                SELECT id, name, address, city, state, status, scope
                FROM projects
                WHERE LOWER(name) LIKE %s
                   OR LOWER(address) LIKE %s
                   OR LOWER(scope) LIKE %s
                ORDER BY status, name
                LIMIT %s
            """, (q, q, q, limit))
            return [_normalize_result(
                "projects", 0.9, dict(r),
                f"{r['name']} — {r.get('address','')} ({r.get('status','')})",
                citation=f"projects.id={r['id']}",
                related_project=r['name'],
                confidence=0.95,
            ) for r in rows]
        except Exception:
            return []

    @staticmethod
    def _search_sops(query: str, limit: int) -> list[dict]:
        kw = _best_keyword(query)
        q = f"%{kw}%"
        try:
            rows = db.query("""
                SELECT si.id, si.sop_number, si.status, si.owner_name,
                       p.name AS project_name, si.created_at
                FROM sop_instances si
                JOIN projects p ON p.id = si.project_id
                WHERE LOWER(si.sop_number) LIKE %s
                   OR LOWER(si.status) LIKE %s
                   OR LOWER(p.name) LIKE %s
                ORDER BY si.created_at DESC
                LIMIT %s
            """, (q, q, q, limit))
            return [_normalize_result(
                "sops", 0.85, dict(r),
                f"SOP {r['sop_number']} — {r['project_name']} [{r['status']}]",
                citation=f"sop_instances.id={r['id']}",
                related_project=r['project_name'],
                confidence=0.90,
            ) for r in rows]
        except Exception:
            return []

    @staticmethod
    def _search_bids(query: str, limit: int) -> list[dict]:
        kw = _best_keyword(query)
        q = f"%{kw}%"
        try:
            rows = db.query("""
                SELECT be.id, be.subcontractor_name, be.amount,
                       bp.package_name, bp.trade, p.name AS project_name
                FROM bid_entries be
                JOIN bid_packages bp ON bp.id = be.bid_package_id
                JOIN projects p ON p.id = bp.project_id
                WHERE LOWER(be.subcontractor_name) LIKE %s
                   OR LOWER(bp.package_name) LIKE %s
                   OR LOWER(bp.trade) LIKE %s
                ORDER BY be.amount DESC NULLS LAST
                LIMIT %s
            """, (q, q, q, limit))
            return [_normalize_result(
                "bids", 0.85, dict(r),
                f"Bid: {r.get('subcontractor_name','')} — {r.get('package_name','')} ${r.get('amount',0):,.0f}",
                citation=f"bid_entries.id={r['id']}",
                related_project=r.get('project_name',''),
                confidence=0.90,
            ) for r in rows]
        except Exception:
            return []

    @staticmethod
    def _search_risks(query: str, limit: int) -> list[dict]:
        kw = _best_keyword(query)
        q = f"%{kw}%"
        try:
            rows = db.query("""
                SELECT r.id, r.risk_type, r.severity, r.description, r.status,
                       p.name AS project_name
                FROM risks r
                JOIN projects p ON p.id = r.project_id
                WHERE LOWER(r.description) LIKE %s
                   OR LOWER(r.risk_type) LIKE %s
                   OR LOWER(r.severity) LIKE %s
                ORDER BY
                    CASE r.severity WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
                    r.identified_date DESC
                LIMIT %s
            """, (q, q, q, limit))
            return [_normalize_result(
                "risks", 0.85, dict(r),
                f"Risk [{r.get('severity','').upper()}] {r.get('project_name','')} — {r.get('description','')[:80]}",
                citation=f"risks.id={r['id']}",
                related_project=r.get('project_name',''),
                confidence=0.88,
            ) for r in rows]
        except Exception:
            return []

    # ── Qdrant semantic search ────────────────────────────────────────────────

    @staticmethod
    def _search_qdrant(
        query: str, col_hint: str, project_filter: str | None,
        limit: int, score_threshold: float
    ) -> list[dict]:
        try:
            import services.vector as vector
            filters = {}
            if project_filter:
                filters["project_number"] = project_filter
            raw = vector.search(
                query=query,
                collection=col_hint or None,
                limit=limit,
                score_threshold=score_threshold,
                filters=filters or None,
            )
            col_name = vector.resolve_collection(col_hint)
            return [_normalize_result(
                f"qdrant:{col_name}", r["score"],
                r.get("payload", {}),
                r.get("text", ""),
                citation=f"qdrant:{col_name}",
                related_project=r.get("payload", {}).get("project_number", ""),
                confidence=round(r["score"], 4),
            ) for r in raw]
        except Exception:
            return []

    # ── Convenience wrappers ──────────────────────────────────────────────────

    @staticmethod
    def find_vendor(name: str, limit: int = 10) -> list[dict]:
        return SearchGateway.search(name, sources=["vendors"], limit=limit)["results"]

    @staticmethod
    def find_sop(project_name: str = "", sop_number: str = "", limit: int = 10) -> list[dict]:
        q = " ".join(filter(None, [project_name, sop_number, "sop"]))
        return SearchGateway.search(q, sources=["sops"], limit=limit)["results"]

    @staticmethod
    def find_lessons_learned(topic: str, limit: int = 5) -> list[dict]:
        return SearchGateway.search(topic, sources=["qdrant_lessons"], limit=limit)["results"]

    @staticmethod
    def find_decisions(topic: str, limit: int = 5) -> list[dict]:
        """Search decision records for related past decisions."""
        kw = _best_keyword(topic)
        q = f"%{kw}%"
        try:
            rows = db.query("""
                SELECT dr.id, dr.decision_type, dr.decision_date, dr.decision_maker,
                       dr.context, dr.selected_option, dr.rationale,
                       p.name AS project_name
                FROM decision_records dr
                LEFT JOIN projects p ON p.id = dr.project_id
                WHERE LOWER(dr.context) LIKE %s
                   OR LOWER(dr.rationale) LIKE %s
                   OR LOWER(dr.selected_option) LIKE %s
                ORDER BY dr.decision_date DESC
                LIMIT %s
            """, (q, q, q, limit))
            return [_normalize_result(
                "decisions", 0.85, dict(r),
                f"Decision [{r.get('decision_type','')}] {r.get('project_name','')} — {r.get('selected_option','')[:80]}",
                citation=f"decision_records.id={r['id']}",
                related_project=r.get('project_name',''),
                confidence=0.85,
            ) for r in rows]
        except Exception:
            return []

    @staticmethod
    def search_with_decisions(query: str, limit: int = 10) -> dict:
        """Full cross-source search including decisions and lessons learned."""
        result = SearchGateway.search(query, limit=limit)
        decisions = SearchGateway.find_decisions(query, limit=3)
        lessons = SearchGateway.find_lessons_learned(query, limit=3)
        result["related_decisions"] = decisions
        result["related_lessons"] = lessons
        return result
