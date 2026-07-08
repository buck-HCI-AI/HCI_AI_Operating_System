"""
Universal Connector Base Class — HCI AI Operating System

Every connector (Houzz, HubSpot, Outlook, QuickBooks, Google Drive, Procore, Autodesk)
extends BaseConnector and implements the 7-stage pipeline.

Architecture:
  Browser/API Agent (Discovery)
    ↓ canonical JSON
  BaseConnector.ingest()
    ├── Stage 1: Validate      — schema + required fields
    ├── Stage 2: Normalize     — canonical field names, types, dates
    ├── Stage 3: Persist       — upsert to houzz_*/hubspot_* tables
    ├── Stage 4: Mine          — trigger downstream miners
    ├── Stage 5: Knowledge Graph — update relationship graph
    ├── Stage 6: Executive     — surface insights to executive inbox
    └── Stage 7: Sync State    — record last_synced_at, cursor

Division of labor (immutable rule):
  Browser Agent  = Discovery only (extracts data, produces canonical JSON)
  Connector      = Validates, normalizes, persists, mines (never Browser)
  DB             = Written through connector only (never direct from Browser)
"""

import os, sys, json, logging, time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

logger = logging.getLogger("hci.connector")

_DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

MAX_RETRIES = 3
RETRY_BACKOFF = [2, 5, 15]  # seconds between retries

LIVE_STATUSES = {"active", "pilot"}


class NonLiveProjectWriteBlocked(Exception):
    """Raised when an ingest payload targets a project outside the live set
    without an explicit, logged override. See ADR-016 addendum 2026-07-08."""
    def __init__(self, blocked: dict):
        self.blocked = blocked
        super().__init__(f"Write blocked — targets non-live/unresolvable project(s): {blocked}")


class ConnectorResult:
    def __init__(self, connector: str, entity_type: str):
        self.connector = connector
        self.entity_type = entity_type
        self.attempted = 0
        self.inserted = 0
        self.updated = 0
        self.skipped = 0
        self.errors: list[dict] = []
        self.started_at = datetime.now(timezone.utc)
        self.finished_at: Optional[datetime] = None

    def finish(self):
        self.finished_at = datetime.now(timezone.utc)
        return self

    def to_dict(self) -> dict:
        return {
            "connector": self.connector,
            "entity_type": self.entity_type,
            "attempted": self.attempted,
            "inserted": self.inserted,
            "updated": self.updated,
            "skipped": self.skipped,
            "errors": self.errors,
            "duration_ms": int((self.finished_at - self.started_at).total_seconds() * 1000) if self.finished_at else None,
        }


class BaseConnector(ABC):
    """Abstract base for all HCI AI connectors."""

    name: str = "base"          # Override in subclass: "houzz", "hubspot", etc.
    version: str = "1.0"
    supported_entities: list[str] = []  # Override in subclass

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self._conn = None

    # ── Public API ─────────────────────────────────────────────────────────────

    def ingest(self, payload: dict, allow_non_live: bool = False, override_reason: Optional[str] = None) -> dict:
        """
        Entry point for all connector data.
        Runs the 7-stage pipeline per entity type found in payload.

        Fixed 2026-07-08 (ADR-016 addendum): this had no awareness of
        projects.status at all. A generic /connectors/{name}/ingest call with
        a valid Houzz project_id would persist to any project regardless of
        whether it was live, monitoring, or reference — the only thing
        stopping a write to a non-live project was the caller choosing not
        to. That's exactly what happened: 120 houzz_daily_logs rows landed
        on 6 reference-status projects in one session. Now every non-dry-run
        ingest is checked against LIVE_STATUSES before anything is written;
        an unresolvable or non-live project reference blocks the whole batch
        unless allow_non_live=True is passed explicitly, in which case the
        override is written to notification_log with override_reason so it's
        traceable, not silent.
        """
        results = {}
        total_inserted = 0
        all_errors = []

        with self._db() as conn:
            self._conn = conn

            if not self.dry_run:
                blocked = self._project_scope_check(payload, conn)
                if blocked:
                    if not allow_non_live:
                        conn.rollback()
                        self._conn = None
                        raise NonLiveProjectWriteBlocked(blocked)
                    self._log_scope_override(blocked, override_reason, conn)

            for entity_type in self.supported_entities:
                records = payload.get(entity_type, [])
                if not records:
                    continue
                result = self._run_with_recovery(entity_type, records)
                results[entity_type] = result.to_dict()
                total_inserted += result.inserted
                all_errors.extend(result.errors)

            if not self.dry_run:
                conn.commit()
                self._update_sync_states(payload, results)
            else:
                conn.rollback()
            self._conn = None

        return {
            "connector": self.name,
            "dry_run": self.dry_run,
            "total_inserted": total_inserted,
            "results": results,
            "errors": all_errors,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_sync_state(self, entity_type: str, external_id: Optional[str] = None) -> Optional[dict]:
        with self._db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM connector_sync_state
                    WHERE connector_name=%s AND entity_type=%s
                      AND COALESCE(external_id,'') = COALESCE(%s,'')
                """, (self.name, entity_type, external_id))
                row = cur.fetchone()
                return dict(row) if row else None

    def list_sync_states(self) -> list[dict]:
        with self._db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT * FROM connector_sync_state
                    WHERE connector_name=%s
                    ORDER BY entity_type, external_id
                """, (self.name,))
                return [dict(r) for r in cur.fetchall()]

    # ── Abstract methods — implement in each connector ─────────────────────────

    @abstractmethod
    def validate(self, entity_type: str, record: dict) -> tuple[bool, list[str]]:
        """
        Return (is_valid, list_of_errors).
        Validate required fields, types, and business rules.
        """

    @abstractmethod
    def normalize(self, entity_type: str, record: dict) -> dict:
        """
        Return a normalized record with canonical field names and types.
        Dates → YYYY-MM-DD strings, amounts → floats, IDs → stripped strings.
        """

    @abstractmethod
    def persist(self, entity_type: str, record: dict, cur) -> bool:
        """
        Upsert one normalized record to the database.
        Return True if inserted (new), False if updated (existing).
        """

    # ── Optional hooks — override as needed ───────────────────────────────────

    def post_persist(self, entity_type: str, results: ConnectorResult) -> None:
        """Called after all records of an entity type are persisted. Override to trigger miners."""

    def publish_event(self, event_type: str, entity_type: str, count: int) -> None:
        """Override to publish events to n8n or internal event bus."""
        logger.info("[%s] event:%s entity:%s count:%d", self.name, event_type, entity_type, count)

    def _project_scope_check(self, payload: dict, conn) -> dict:
        """
        Return {project_ref: {"project_code": ..., "status": ...}} for every
        project referenced in payload that is NOT in LIVE_STATUSES (including
        refs that can't be resolved at all — fail closed). Base implementation
        does no project-scoped writes, so it returns {} (nothing to check).
        Override in connectors whose entities carry a project reference.
        """
        return {}

    def _log_scope_override(self, blocked: dict, override_reason: Optional[str], conn) -> None:
        """Audit trail for an explicit allow_non_live write. Never silent."""
        reason = override_reason or "(no reason given)"
        logger.warning("[%s] NON-LIVE PROJECT WRITE OVERRIDE: %s — reason: %s", self.name, blocked, reason)
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO notification_log
                        (event_type, entity_type, entity_id, severity, message, success)
                    VALUES ('non_live_project_write_override', %s, %s, 'WARNING', %s, true)
                """, (self.name, json.dumps(blocked)[:200], f"reason: {reason} | blocked: {json.dumps(blocked)}"))
        except Exception as e:
            logger.error("[%s] Failed to log scope override: %s", self.name, e)

    # ── 7-Stage Pipeline ───────────────────────────────────────────────────────

    def _run_with_recovery(self, entity_type: str, records: list[dict]) -> ConnectorResult:
        """Wraps _run_pipeline with autonomous retry and recovery."""
        result = ConnectorResult(self.name, entity_type)
        attempt = 0
        last_error = None

        while attempt < MAX_RETRIES:
            try:
                result = self._run_pipeline(entity_type, records)
                if attempt > 0:
                    logger.info("[%s] recovered %s after %d retries", self.name, entity_type, attempt)
                return result.finish()
            except Exception as e:
                last_error = e
                attempt += 1
                if attempt < MAX_RETRIES:
                    wait = RETRY_BACKOFF[attempt - 1]
                    logger.warning("[%s] %s failed (attempt %d/%d), retrying in %ds: %s",
                                   self.name, entity_type, attempt, MAX_RETRIES, wait, e)
                    time.sleep(wait)
                else:
                    logger.error("[%s] %s failed after %d attempts: %s", self.name, entity_type, MAX_RETRIES, e)
                    self._log_escalation(entity_type, str(last_error))

        result.errors.append({"entity_type": entity_type, "error": str(last_error), "retries": MAX_RETRIES})
        return result.finish()

    def _run_pipeline(self, entity_type: str, records: list[dict]) -> ConnectorResult:
        result = ConnectorResult(self.name, entity_type)

        with self._conn.cursor() as cur:
            for record in records:
                result.attempted += 1

                # Stage 1: Validate
                is_valid, errors = self.validate(entity_type, record)
                if not is_valid:
                    result.skipped += 1
                    result.errors.append({"entity_type": entity_type, "errors": errors, "record_keys": list(record.keys())})
                    continue

                # Stage 2: Normalize
                try:
                    normalized = self.normalize(entity_type, record)
                except Exception as e:
                    result.skipped += 1
                    result.errors.append({"entity_type": entity_type, "stage": "normalize", "error": str(e)})
                    continue

                # Stage 3: Persist (skip write in dry_run but still count)
                if self.dry_run:
                    result.inserted += 1
                    continue

                try:
                    is_new = self.persist(entity_type, normalized, cur)
                    if is_new:
                        result.inserted += 1
                    else:
                        result.updated += 1
                except Exception as e:
                    result.skipped += 1
                    result.errors.append({"entity_type": entity_type, "stage": "persist", "error": str(e)})
                    self._conn.rollback()
                    continue

        # Stage 4: Mine (post-persist hook)
        if not self.dry_run and (result.inserted + result.updated) > 0:
            self.post_persist(entity_type, result)

        # Stage 5-7: Events + sync state (handled by caller for batching)
        if result.inserted + result.updated > 0:
            self.publish_event("synced", entity_type, result.inserted + result.updated)

        return result

    # ── Sync State Management ──────────────────────────────────────────────────

    def _update_sync_states(self, payload: dict, results: Optional[dict] = None) -> None:
        """Update connector_sync_state for every entity type that had data.

        Fixed 2026-07-07: this used to stamp last_synced_at/status='idle'/
        records_synced += len(records) (the ATTEMPTED count) unconditionally,
        with no reference to whether persist() actually succeeded. Found live:
        the HubSpot connector's persist_contact/company/deal had a column-name
        mismatch (hubspot_id vs the real hubspot_contact_id etc.) so every
        single persist() call threw, was caught per-record inside
        _run_pipeline, and never propagated - _run_with_recovery saw no
        exception, so no retry/escalation ever fired. connector_sync_state
        kept reporting status='idle', error_message=NULL, records_synced
        climbing normally for 12+ days while 0 rows were actually written.
        Every drift-check and audit up to this point only checked
        connector_registry.last_indexed / sync_age_hours - a connector that
        syncs "successfully" and persists nothing was invisible to all of
        them. Now records_synced reflects rows actually inserted/updated, and
        a fully-failed entity_type is written as status='error' with the real
        error text instead of silently reporting idle."""
        results = results or {}
        try:
            with self._db() as conn:
                with conn.cursor() as cur:
                    for entity_type in self.supported_entities:
                        records = payload.get(entity_type, [])
                        if not records:
                            continue
                        result = results.get(entity_type, {})
                        persisted = result.get("inserted", 0) + result.get("updated", 0)
                        attempted = result.get("attempted", len(records))
                        errors = result.get("errors", [])
                        failed = attempted > 0 and persisted == 0
                        error_message = "; ".join(str(e) for e in errors[:3])[:1000] if errors else None
                        project_ids = list({
                            r.get("houzz_project_id") or r.get("project_id") or r.get("external_id", "")
                            for r in records
                        })
                        for ext_id in project_ids:
                            if failed:
                                cur.execute("""
                                    INSERT INTO connector_sync_state
                                        (connector_name, entity_type, external_id, last_synced_at,
                                         records_synced, status, error_message, retry_count, updated_at)
                                    VALUES (%s, %s, %s, NOW(), 0, 'error', %s, 1, NOW())
                                    ON CONFLICT (connector_name, entity_type, (COALESCE(external_id, ''))) DO UPDATE SET
                                        status         = 'error',
                                        error_message  = EXCLUDED.error_message,
                                        retry_count    = connector_sync_state.retry_count + 1,
                                        updated_at     = NOW()
                                """, (self.name, entity_type, ext_id or None, error_message))
                            else:
                                cur.execute("""
                                    INSERT INTO connector_sync_state
                                        (connector_name, entity_type, external_id, last_synced_at,
                                         records_synced, status, error_message, updated_at)
                                    VALUES (%s, %s, %s, NOW(), %s, 'idle', %s, NOW())
                                    ON CONFLICT (connector_name, entity_type, (COALESCE(external_id, ''))) DO UPDATE SET
                                        last_synced_at = NOW(),
                                        records_synced = connector_sync_state.records_synced + EXCLUDED.records_synced,
                                        status         = 'idle',
                                        error_message  = EXCLUDED.error_message,
                                        retry_count    = 0,
                                        updated_at     = NOW()
                                """, (self.name, entity_type, ext_id or None, persisted, error_message))
                conn.commit()
        except Exception as e:
            logger.error("[%s] Failed to update sync states: %s", self.name, e)

    def _log_escalation(self, entity_type: str, error: str) -> None:
        """Log persistent failure to notification_log for executive escalation."""
        try:
            with self._db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO notification_log
                            (event_type, entity_type, entity_id, severity, message, success)
                        VALUES ('connector_failure', %s, %s, 'CRITICAL', %s, false)
                    """, (entity_type, self.name, f"Connector {self.name} failed on {entity_type}: {error}"))
                    cur.execute("""
                        UPDATE connector_sync_state
                        SET status='error', error_message=%s, retry_count=retry_count+1, updated_at=NOW()
                        WHERE connector_name=%s AND entity_type=%s
                    """, (error[:1000], self.name, entity_type))
                conn.commit()
        except Exception as log_err:
            logger.error("[%s] Failed to log escalation: %s", self.name, log_err)

    # ── DB Helper ─────────────────────────────────────────────────────────────

    def _db(self):
        return psycopg2.connect(**_DB, cursor_factory=psycopg2.extras.RealDictCursor)
