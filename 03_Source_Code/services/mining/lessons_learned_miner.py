"""
Lessons Learned Miner — extracts lessons from BL records (meetings, daily logs).
Uses Claude Haiku for intelligence extraction when content is available.
Queues all lessons for human review before writing to lessons_learned table.
"""
import json, re
from .base_miner import BaseMiner, MiningResult

_SYSTEM_PROMPT = """You are a construction project intelligence extractor for Hendrickson Construction, Inc.
Extract actionable lessons learned from the provided construction document.
Return JSON only — no other text.
Format: {"lessons": [{"title": "...", "description": "...", "category": "...", "recommendation": "..."}]}
Categories: estimating, procurement, scheduling, field_ops, subcontractor, safety, client, documentation, other
Return an empty lessons array if no clear lessons can be extracted."""


class LessonsLearnedMiner(BaseMiner):
    MINER_NAME = "lessons_learned_miner"
    SOURCE_SYSTEMS = ["postgres:background_learning_records", "postgres:meetings"]
    TARGET_STORES = ["lessons_learned", "approval_queue"]

    def mine(self) -> MiningResult:
        run_id = self.start_run()
        result = MiningResult(self.MINER_NAME, run_id)
        try:
            self._mine_bl_candidates(result)
            self._mine_meetings(result)
            self._dedup_existing_lessons(result)
            return self.complete_run(run_id, result)
        except Exception as e:
            return self.fail_run(run_id, str(e))

    def _mine_bl_candidates(self, result: MiningResult):
        """Process BL records flagged as Human Review Needed for meeting/daily_log types."""
        candidates = self._query("""
            SELECT id, source_name, source_url, document_type,
                   project_id, project_association, summary, intelligence_candidates
            FROM background_learning_records
            WHERE status = 'Human Review Needed'
              AND document_type IN ('meeting', 'daily_log', 'spec', 'rfi')
              AND (intelligence_candidates IS NOT NULL AND intelligence_candidates != '[]')
            ORDER BY created_at DESC
            LIMIT 30
        """)
        result.records_scanned += len(candidates)

        for rec in candidates:
            try:
                candidates_data = rec.get("intelligence_candidates") or []
                if isinstance(candidates_data, str):
                    candidates_data = json.loads(candidates_data)
            except Exception:
                candidates_data = []

            for candidate in candidates_data:
                if candidate.get("type") in ("meeting_summary", "field_intelligence"):
                    self.queue_for_approval(
                        action_type="lessons_learned_candidate",
                        title=f"Lessons candidate: {rec['source_name'][:80]}",
                        description=(
                            f"Document type: {rec['document_type']}\n"
                            f"Project: {rec.get('project_association', 'Unknown')}\n"
                            f"Suggested action: {candidate.get('action', 'review')}\n\n"
                            f"Approve to extract and add to Lessons Learned Registry."
                        ),
                        payload={
                            "bl_record_id": rec["id"],
                            "source_name": rec["source_name"],
                            "doc_type": rec["document_type"],
                            "project_id": rec.get("project_id"),
                            "candidate": candidate,
                        },
                        project_id=rec.get("project_id"),
                        priority="low"
                    )
                    result.items_queued_for_review += 1
                    result.intelligence_extracted += 1

    def _mine_meetings(self, result: MiningResult):
        """Check meetings table for recent entries without associated lessons."""
        meetings = self._query("""
            SELECT m.id, m.title, m.meeting_type, m.summary as notes, m.action_items, m.project_id
            FROM meetings m
            WHERE NOT EXISTS (
                SELECT 1 FROM lessons_learned ll
                WHERE ll.source_reference = 'meeting:' || m.id::text
                   OR ll.title ILIKE '%' || m.title || '%'
            )
            ORDER BY m.meeting_date DESC NULLS LAST
            LIMIT 20
        """)
        result.records_scanned += len(meetings)

        for meeting in meetings:
            notes = meeting.get("notes") or ""
            # action_items is jsonb - comes back as a list/dict from psycopg2, not a
            # string. Found 2026-07-07: this crashed every single run of this miner.
            action_items = meeting.get("action_items")
            if isinstance(action_items, (list, dict)):
                action_items = json.dumps(action_items)
            action_items = action_items or ""
            combined = (notes + " " + action_items).strip()
            if len(combined) < 50:
                continue

            if any(kw in combined.lower() for kw in
                   ["lesson", "problem", "issue", "delay", "change", "risk", "learn"]):
                self.queue_for_approval(
                    action_type="lessons_learned_candidate",
                    title=f"Meeting lessons candidate: {meeting.get('title', 'Untitled')[:80]}",
                    description=(
                        f"Meeting type: {meeting.get('meeting_type')}\n"
                        f"Notes excerpt: {combined[:400]}\n\n"
                        "Approve to extract lessons learned from this meeting."
                    ),
                    payload={
                        "meeting_id": meeting["id"],
                        "title": meeting.get("title"),
                        "meeting_type": meeting.get("meeting_type"),
                        "project_id": meeting.get("project_id"),
                        "notes_excerpt": combined[:500],
                    },
                    project_id=meeting.get("project_id"),
                    priority="low"
                )
                result.items_queued_for_review += 1
                result.intelligence_extracted += 1

    def _dedup_existing_lessons(self, result: MiningResult):
        """Report on lessons learned count and any duplicates."""
        total = self._query_one("SELECT COUNT(*) as cnt FROM lessons_learned")
        by_category = self._query("""
            SELECT category, COUNT(*) as count
            FROM lessons_learned
            GROUP BY category ORDER BY count DESC
        """)
        result.summary["total_lessons"] = total["cnt"] if total else 0
        result.summary["by_category"] = {r["category"]: r["count"] for r in by_category}
