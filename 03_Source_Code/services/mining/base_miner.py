"""
BaseMiner — shared foundation for all 8 ACR-004 mining agents.

Safety contract:
  - No source system is ever written to (HubSpot, Drive, Houzz, Outlook are read-only)
  - Human approval required for: contracts, awards, budgets, client comms, financial commitments
  - All writes go through approval_queue or update existing records (no phantom creates)
  - dry_run=True logs intent without writing anything
"""
import os, sys, json
from datetime import datetime, timezone
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

import psycopg2, psycopg2.extras

_DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

REQUIRES_APPROVAL = {
    "contract", "award", "budget", "client_communication",
    "financial_commitment", "change_order",
}


def _pg():
    return psycopg2.connect(**_DB, cursor_factory=psycopg2.extras.RealDictCursor)


class MiningResult:
    def __init__(self, miner_name: str, run_id: int):
        self.miner_name = miner_name
        self.run_id = run_id
        self.status = "completed"
        self.records_scanned = 0
        self.records_discovered = 0
        self.intelligence_extracted = 0
        self.items_queued_for_review = 0
        self.items_auto_written = 0
        self.summary: dict = {}
        self.error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "miner": self.miner_name,
            "status": self.status,
            "records_scanned": self.records_scanned,
            "records_discovered": self.records_discovered,
            "intelligence_extracted": self.intelligence_extracted,
            "items_queued_for_review": self.items_queued_for_review,
            "items_auto_written": self.items_auto_written,
            "summary": self.summary,
            "error_message": self.error_message,
        }


class BaseMiner:
    MINER_NAME: str = "base"
    SOURCE_SYSTEMS: list = []
    TARGET_STORES: list = []

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    # ── DB helpers ─────────────────────────────────────────────────────────────

    def _pg(self):
        return _pg()

    def _query(self, sql: str, params=None) -> list:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return [dict(r) for r in cur.fetchall()]

    def _query_one(self, sql: str, params=None) -> Optional[dict]:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                r = cur.fetchone()
                return dict(r) if r else None

    def _execute(self, sql: str, params=None, returning: bool = False):
        if self.dry_run:
            return None
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                result = cur.fetchone() if returning else None
                conn.commit()
                return dict(result) if result else None

    # ── Mining run lifecycle ───────────────────────────────────────────────────

    def start_run(self) -> int:
        row = self._execute(
            "INSERT INTO mining_runs (miner_name, dry_run) VALUES (%s, %s) RETURNING id",
            (self.MINER_NAME, self.dry_run), returning=True
        )
        if self.dry_run:
            return -1
        return row["id"] if row else -1

    def complete_run(self, run_id: int, result: MiningResult) -> MiningResult:
        result.status = "completed"
        if run_id > 0:
            self._execute("""
                UPDATE mining_runs SET
                    completed_at = NOW(), status = %s,
                    records_scanned = %s, records_discovered = %s,
                    intelligence_extracted = %s, items_queued_for_review = %s,
                    items_auto_written = %s, summary = %s
                WHERE id = %s
            """, (result.status, result.records_scanned, result.records_discovered,
                  result.intelligence_extracted, result.items_queued_for_review,
                  result.items_auto_written, json.dumps(result.summary), run_id))
        return result

    def fail_run(self, run_id: int, error: str) -> MiningResult:
        result = MiningResult(self.MINER_NAME, run_id)
        result.status = "failed"
        result.error_message = error
        if run_id > 0:
            self._execute(
                "UPDATE mining_runs SET completed_at=NOW(), status='failed', error_message=%s WHERE id=%s",
                (error[:2000], run_id)
            )
        return result

    # ── Approval queue ─────────────────────────────────────────────────────────

    def queue_for_approval(self, action_type: str, title: str, description: str,
                           payload: dict, project_id: int = None,
                           priority: str = "medium") -> Optional[int]:
        """Route an intelligence item to the approval queue for Buck's review."""
        if self.dry_run:
            return None
        row = self._execute("""
            INSERT INTO approval_queue
                (action_type, target_system, target_description, reason, proposed_payload,
                 project_id, priority, status, workflow, actor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s)
            RETURNING id
        """, (action_type, "mining", title[:255], description, json.dumps(payload),
              project_id, priority, f"mining:{self.MINER_NAME}", self.MINER_NAME),
            returning=True)
        return row["id"] if row else None

    # ── BL discovery registration ──────────────────────────────────────────────

    def register_discovery(self, source_system: str, source_id: str,
                           source_name: str, metadata: dict = None,
                           project_id: int = None) -> Optional[int]:
        if self.dry_run:
            return None
        row = self._execute("""
            INSERT INTO background_learning_records
                (source_system, source_id, source_name, status, confidence, metadata, project_id)
            VALUES (%s, %s, %s, 'Discovered', 0.7, %s, %s)
            ON CONFLICT (source_system, source_id) DO UPDATE
                SET source_name = EXCLUDED.source_name, updated_at = NOW()
            RETURNING id
        """, (source_system, source_id, source_name,
              json.dumps(metadata or {}), project_id), returning=True)
        return row["id"] if row else None

    # ── Claude intelligence extraction ────────────────────────────────────────

    def extract_with_claude(self, prompt: str, system: str = "", max_tokens: int = 512) -> str:
        """Use Claude Haiku to extract structured intelligence from text."""
        try:
            import anthropic
            from dotenv import load_dotenv
            load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
            key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not key:
                return "{}"
            client = anthropic.Anthropic(api_key=key)
            kwargs = {"model": "claude-haiku-4-5-20251001", "max_tokens": max_tokens,
                      "messages": [{"role": "user", "content": prompt}]}
            if system:
                kwargs["system"] = system
            resp = client.messages.create(**kwargs)
            return resp.content[0].text
        except Exception:
            return "{}"

    # ── Interface ──────────────────────────────────────────────────────────────

    def mine(self) -> MiningResult:
        raise NotImplementedError(f"{self.MINER_NAME}.mine() not implemented")

    @classmethod
    def info(cls) -> dict:
        return {
            "miner": cls.MINER_NAME,
            "sources": cls.SOURCE_SYSTEMS,
            "targets": cls.TARGET_STORES,
        }
