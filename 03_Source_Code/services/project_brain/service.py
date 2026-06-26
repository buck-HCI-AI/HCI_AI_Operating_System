"""
Project Brain Service — unified intelligence model per project.

Combines every data source (Postgres structured data, Qdrant vectors, MinIO documents)
into a single queryable intelligence layer. Answer questions across all project information.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from typing import Optional
from base import BaseIntelligenceService
import services.vector as vector
from models import ProjectSnapshot, ProjectQueryResponse, BidPackageSummary, SourceReference

SNAPSHOT_TTL = 1800   # 30 min
QUERY_TTL    = 300    # 5 min

# All Qdrant collections that may contain project-relevant content
PROJECT_COLLECTIONS = [
    "drive_memory",
    "project_memory",
    "bid_memory",
    "vendor_memory",
    "lessons_learned",
]

SYSTEM_PROMPT = """You are the Project Brain for Hendrickson Construction — a high-end residential
remodeler in Aspen, Colorado. You have complete knowledge of the project including bids, budgets,
schedule, vendors, drawings, specifications, RFIs, submittals, change orders, meeting notes,
daily logs, and correspondence.

Answer questions accurately and specifically. When you reference a number (cost, date, quantity),
cite the source document or data table. If information is not in the provided context, say so
rather than guessing. Be concise and professional."""


class ProjectBrainService(BaseIntelligenceService):
    SERVICE_NAME = "project_brain"
    STATUS = "active"

    def __init__(self, project_number: str):
        self.project_number = project_number.upper()
        self._project_row = None

    def _get_project_row(self) -> Optional[dict]:
        if not self._project_row:
            import re
            # Extract numeric prefix for matching (e.g. "64EW" → "64", "1355RV" → "1355")
            m = re.match(r'^(\d+)', self.project_number)
            num_prefix = m.group(1) if m else self.project_number

            sql = """
                SELECT p.*,
                       hd.stage        AS deal_stage,
                       hd.amount       AS deal_amount,
                       hd.close_date   AS deal_close_date
                FROM   projects p
                LEFT JOIN hubspot_deals hd
                       ON hd.hubspot_deal_id = p.hubspot_deal_id
                WHERE  p.name ILIKE %s OR p.address ILIKE %s
                LIMIT 1
            """
            self._project_row = self.pg_one(sql, (f"{num_prefix}%", f"{num_prefix}%"))
        return self._project_row

    def snapshot(self, force_refresh: bool = False) -> dict:
        cache_key = f"project_brain:snapshot:{self.project_number}"
        if not force_refresh:
            cached = self.cache_get(cache_key)
            if cached:
                cached["cached"] = True
                return cached

        project = self._get_project_row()
        if not project:
            return {"error": f"Project '{self.project_number}' not found",
                    "hint": "Valid codes: 64EW, 101F, 1355R, 83SB"}

        project_id = project["id"]

        # ── Bid packages + entries ─────────────────────────────────────────
        bid_rows = self.pg_query("""
            SELECT bp.package_name, bp.csi_division,
                   COUNT(be.id)         AS bid_count,
                   MIN(be.bid_amount)   AS lowest_bid,
                   MAX(be.bid_amount)   AS highest_bid
            FROM bid_packages bp
            LEFT JOIN bid_entries be ON be.bid_package_id = bp.id AND be.project_id = %s
            WHERE bp.project_id = %s
            GROUP BY bp.id, bp.package_name, bp.csi_division
            ORDER BY bp.csi_division NULLS LAST, bp.package_name
        """, (project_id, project_id))

        bid_packages = []
        for b in bid_rows:
            lo = float(b["lowest_bid"]) if b["lowest_bid"] else None
            hi = float(b["highest_bid"]) if b["highest_bid"] else None
            spread = round((hi - lo) / lo * 100, 1) if lo and hi and lo > 0 else None
            bid_packages.append(BidPackageSummary(
                package_name=b["package_name"],
                csi_division=b["csi_division"],
                bid_count=int(b["bid_count"]),
                lowest_bid=lo,
                highest_bid=hi,
                spread_pct=spread,
            ).model_dump())

        # ── Meetings ──────────────────────────────────────────────────────
        meetings = self.pg_query("""
            SELECT title, meeting_date, meeting_type, summary AS notes
            FROM meetings WHERE project_id = %s
            ORDER BY meeting_date DESC LIMIT 5
        """, (project_id,))

        # ── Daily logs ────────────────────────────────────────────────────
        daily_logs = self.pg_query("""
            SELECT log_date, work_performed, issues, weather
            FROM daily_logs WHERE project_id = %s
            ORDER BY log_date DESC LIMIT 5
        """, (project_id,))

        # ── HubSpot notes — joined via projects.hubspot_deal_id ───────────
        hs_notes = self.pg_query("""
            SELECT hn.body AS note_body, hn.note_timestamp AS created_date
            FROM hubspot_notes hn
            JOIN hubspot_deals hd ON hd.hubspot_deal_id = hn.deal_id
            JOIN projects p       ON p.hubspot_deal_id  = hd.hubspot_deal_id
            WHERE p.id = %s
            ORDER BY hn.note_timestamp DESC LIMIT 5
        """, (project_id,)) if self.pg_one(
            "SELECT 1 FROM pg_tables WHERE tablename='hubspot_notes'") else []

        # ── Vendor count ──────────────────────────────────────────────────
        vendor_row = self.pg_one(
            "SELECT COUNT(DISTINCT vendor_id) AS n FROM bid_entries WHERE project_id = %s",
            (project_id,)
        )
        vendor_count = int(vendor_row["n"]) if vendor_row else 0

        # ── Qdrant vector count for project ───────────────────────────────
        total_vectors = 0
        try:
            from qdrant_client import QdrantClient
            from config import settings as cfg
            qc = QdrantClient(host=cfg.qdrant_host, port=cfg.qdrant_port)
            for col in ["drive_memory", "project_memory", "bid_memory"]:
                info = qc.get_collection(col)
                total_vectors += info.points_count or 0
        except Exception:
            pass

        result = {
            "project_number":    self.project_number,
            "name":              project.get("name", ""),
            "address":           project.get("address", ""),
            "status":            project.get("status", ""),
            "scope":             project.get("scope", ""),
            "budget_estimate":   float(project["deal_amount"]) if project.get("deal_amount") else None,
            "hubspot_deal_id":   project.get("hubspot_deal_id"),
            "bid_packages":      bid_packages,
            "vendor_count":      vendor_count,
            "vector_count":      total_vectors,
            "recent_meetings":   [dict(m) for m in meetings],
            "recent_daily_logs": [dict(d) for d in daily_logs],
            "recent_hs_notes":   [dict(n) for n in hs_notes],
            "last_updated":      datetime.utcnow().isoformat(),
            "cached":            False,
        }

        self.cache_set(cache_key, result, ttl=SNAPSHOT_TTL)
        return result

    def query(self, question: str, context_hint: Optional[str] = None,
              max_sources: int = 6) -> dict:
        cache_key = f"project_brain:query:{self.project_number}:{hash(question)}"
        cached = self.cache_get(cache_key)
        if cached:
            cached["cached"] = True
            return cached

        # ── Multi-collection semantic search ──────────────────────────────
        all_results = []

        # Search with project filter first
        hint_collection = self._hint_to_collection(context_hint)
        results = self.search(question, collection=hint_collection,
                              limit=4, project_filter=self.project_number)
        all_results.extend(results)

        # Broader drive_memory search (no project filter — content proximity)
        if len(all_results) < 4:
            drive_results = self.search(question, collection="drive_memory", limit=4)
            # Deduplicate by text similarity
            seen = {r["text"][:100] for r in all_results}
            for r in drive_results:
                if r.get("text", "")[:100] not in seen:
                    all_results.append(r)
                    seen.add(r.get("text", "")[:100])

        all_results = all_results[:max_sources]

        # ── Structured context from Postgres ──────────────────────────────
        project = self._get_project_row() or {}
        snap    = self.snapshot()

        context_lines = [
            f"PROJECT: {project.get('name', self.project_number)} | {project.get('address', '')}",
            f"Status: {project.get('status', 'unknown')} | Scope: {project.get('scope', 'TBD')}",
        ]

        if snap.get("bid_packages"):
            bid_lines = []
            for b in snap["bid_packages"][:8]:
                if b["bid_count"] > 0:
                    lo = f"${b['lowest_bid']:,.0f}" if b["lowest_bid"] else "no bids"
                    bid_lines.append(f"  {b['package_name']} ({b['csi_division'] or '—'}): "
                                    f"{b['bid_count']} bids, low {lo}")
            if bid_lines:
                context_lines.append("BIDS:\n" + "\n".join(bid_lines))

        if snap.get("recent_meetings"):
            mtg = snap["recent_meetings"][0]
            context_lines.append(
                f"LAST MEETING: {mtg.get('title')} on {mtg.get('meeting_date')} — "
                f"{str(mtg.get('notes', ''))[:300]}"
            )

        if snap.get("recent_daily_logs"):
            dl = snap["recent_daily_logs"][0]
            context_lines.append(
                f"LAST DAILY LOG ({dl.get('log_date')}): {str(dl.get('work_performed', ''))[:300]}"
            )

        for r in all_results:
            text = r.get("payload", {}).get("text") or r.get("text", "")
            src  = r.get("payload", {}).get("source") or r.get("payload", {}).get("original_filename", "")
            if text:
                context_lines.append(f"\n[Source: {src}]\n{text[:600]}")

        context = "\n".join(context_lines)

        # ── Claude synthesis ───────────────────────────────────────────────
        prompt = f"PROJECT CONTEXT:\n{context}\n\nQUESTION: {question}"
        answer = self.ask_claude(prompt, system=SYSTEM_PROMPT, max_tokens=1024)

        sources = [
            SourceReference(
                text=r.get("payload", {}).get("text", "")[:200],
                source=r.get("payload", {}).get("source")
                       or r.get("payload", {}).get("original_filename", ""),
                score=round(r.get("score", 0), 3),
                collection=r.get("collection", ""),
            ).model_dump()
            for r in all_results
        ]

        result = {
            "project_number": self.project_number,
            "question":       question,
            "answer":         answer,
            "sources":        sources,
            "model_used":     "claude-haiku-4-5-20251001",
            "cached":         False,
        }
        self.cache_set(cache_key, result, ttl=QUERY_TTL)
        return result

    @staticmethod
    def _hint_to_collection(hint: Optional[str]) -> Optional[str]:
        if not hint:
            return None
        h = hint.lower()
        if "bid" in h:         return "bid_memory"
        if "vendor" in h:      return "vendor_memory"
        if "lesson" in h:      return "lessons_learned"
        if "project" in h:     return "project_memory"
        return "drive_memory"
