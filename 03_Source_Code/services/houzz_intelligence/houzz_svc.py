"""
Houzz Intelligence Service — persistence bridge for Browser Claude extraction.
Accepts structured JSON payloads and writes to houzz_* tables via upsert.
"""
import os, sys, json
from datetime import datetime, date
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))

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


def _pg():
    return psycopg2.connect(**_DB, cursor_factory=psycopg2.extras.RealDictCursor)


def _parse_date(val) -> Optional[date]:
    if not val:
        return None
    if isinstance(val, date):
        return val
    try:
        return datetime.strptime(str(val)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


class TableMetrics:
    def __init__(self):
        self.attempted = 0
        self.imported = 0
        self.skipped = 0
        self.duplicate = 0

    def to_dict(self):
        return {
            "attempted": self.attempted,
            "imported": self.imported,
            "skipped": self.skipped,
            "duplicate": self.duplicate,
        }


class HouzzIngestionService:

    @staticmethod
    def ingest(payload: dict) -> dict:
        projects = payload.get("projects", [])
        daily_logs = payload.get("daily_logs", [])
        schedule_items = payload.get("schedule_items", [])

        pm = TableMetrics()
        lm = TableMetrics()
        sm = TableMetrics()
        validation_errors = []

        with _pg() as conn:
            with conn.cursor() as cur:

                # ── Projects ────────────────────────────────────────────────
                for p in projects:
                    pm.attempted += 1
                    pid = p.get("houzz_project_id", "").strip()
                    if not pid:
                        validation_errors.append({"table": "projects", "error": "missing houzz_project_id", "record": p})
                        pm.skipped += 1
                        continue
                    try:
                        cur.execute("""
                            INSERT INTO houzz_projects
                                (houzz_project_id, name, client_name, status,
                                 address, budget, start_date, end_date,
                                 project_type, properties, synced_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                            ON CONFLICT (houzz_project_id) DO UPDATE SET
                                name        = EXCLUDED.name,
                                client_name = EXCLUDED.client_name,
                                status      = EXCLUDED.status,
                                address     = COALESCE(EXCLUDED.address, houzz_projects.address),
                                budget      = COALESCE(EXCLUDED.budget, houzz_projects.budget),
                                start_date  = COALESCE(EXCLUDED.start_date, houzz_projects.start_date),
                                end_date    = COALESCE(EXCLUDED.end_date, houzz_projects.end_date),
                                project_type = COALESCE(EXCLUDED.project_type, houzz_projects.project_type),
                                properties  = EXCLUDED.properties,
                                synced_at   = NOW()
                            RETURNING (xmax = 0) AS is_insert
                        """, (
                            pid,
                            p.get("name"),
                            p.get("client_name"),
                            p.get("status"),
                            p.get("address"),
                            p.get("budget"),
                            _parse_date(p.get("start_date")),
                            _parse_date(p.get("end_date")),
                            p.get("project_type"),
                            json.dumps(p.get("properties") or {}),
                        ))
                        row = cur.fetchone()
                        if row and row["is_insert"]:
                            pm.imported += 1
                        else:
                            pm.duplicate += 1
                    except Exception as e:
                        validation_errors.append({"table": "projects", "error": str(e), "houzz_project_id": pid})
                        pm.skipped += 1
                        conn.rollback()
                        continue

                # ── Daily Logs ───────────────────────────────────────────────
                for log in daily_logs:
                    lm.attempted += 1
                    lid = log.get("houzz_log_id", "").strip()
                    lpid = log.get("project_id", "").strip()
                    if not lid:
                        validation_errors.append({"table": "daily_logs", "error": "missing houzz_log_id", "record": log})
                        lm.skipped += 1
                        continue
                    if not lpid:
                        validation_errors.append({"table": "daily_logs", "error": "missing project_id", "houzz_log_id": lid})
                        lm.skipped += 1
                        continue
                    try:
                        cur.execute("""
                            INSERT INTO houzz_daily_logs
                                (houzz_log_id, project_id, log_date, content,
                                 weather, crew_size, author, raw_json, synced_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                            ON CONFLICT (houzz_log_id) DO UPDATE SET
                                content   = COALESCE(EXCLUDED.content, houzz_daily_logs.content),
                                weather   = COALESCE(EXCLUDED.weather, houzz_daily_logs.weather),
                                crew_size = COALESCE(EXCLUDED.crew_size, houzz_daily_logs.crew_size),
                                author    = COALESCE(EXCLUDED.author, houzz_daily_logs.author),
                                raw_json  = COALESCE(EXCLUDED.raw_json, houzz_daily_logs.raw_json),
                                synced_at = NOW()
                            RETURNING (xmax = 0) AS is_insert
                        """, (
                            lid,
                            lpid,
                            _parse_date(log.get("log_date")),
                            log.get("content"),
                            log.get("weather"),
                            log.get("crew_size"),
                            log.get("author"),
                            json.dumps(log.get("raw_json")) if log.get("raw_json") else None,
                        ))
                        row = cur.fetchone()
                        if row and row["is_insert"]:
                            lm.imported += 1
                        else:
                            lm.duplicate += 1
                    except Exception as e:
                        validation_errors.append({"table": "daily_logs", "error": str(e), "houzz_log_id": lid})
                        lm.skipped += 1
                        conn.rollback()
                        continue

                # ── Schedule Items ───────────────────────────────────────────
                for item in schedule_items:
                    sm.attempted += 1
                    iid = item.get("houzz_item_id", "").strip()
                    ipid = item.get("project_id", "").strip()
                    if not iid:
                        validation_errors.append({"table": "schedule_items", "error": "missing houzz_item_id", "record": item})
                        sm.skipped += 1
                        continue
                    if not ipid:
                        validation_errors.append({"table": "schedule_items", "error": "missing project_id", "houzz_item_id": iid})
                        sm.skipped += 1
                        continue
                    try:
                        cur.execute("""
                            INSERT INTO houzz_schedule_items
                                (houzz_item_id, project_id, title, start_date, end_date,
                                 status, parent_item_id, assignee, completion_pct,
                                 task_type, notes, synced_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                            ON CONFLICT (houzz_item_id) DO UPDATE SET
                                title          = COALESCE(EXCLUDED.title, houzz_schedule_items.title),
                                start_date     = COALESCE(EXCLUDED.start_date, houzz_schedule_items.start_date),
                                end_date       = COALESCE(EXCLUDED.end_date, houzz_schedule_items.end_date),
                                status         = COALESCE(EXCLUDED.status, houzz_schedule_items.status),
                                parent_item_id = COALESCE(EXCLUDED.parent_item_id, houzz_schedule_items.parent_item_id),
                                assignee       = COALESCE(EXCLUDED.assignee, houzz_schedule_items.assignee),
                                completion_pct = COALESCE(EXCLUDED.completion_pct, houzz_schedule_items.completion_pct),
                                task_type      = COALESCE(EXCLUDED.task_type, houzz_schedule_items.task_type),
                                notes          = COALESCE(EXCLUDED.notes, houzz_schedule_items.notes),
                                synced_at      = NOW()
                            RETURNING (xmax = 0) AS is_insert
                        """, (
                            iid,
                            ipid,
                            item.get("title"),
                            _parse_date(item.get("start_date")),
                            _parse_date(item.get("end_date")),
                            item.get("status"),
                            item.get("parent_item_id"),
                            item.get("assignee"),
                            item.get("completion_pct"),
                            item.get("task_type"),
                            item.get("notes"),
                        ))
                        row = cur.fetchone()
                        if row and row["is_insert"]:
                            sm.imported += 1
                        else:
                            sm.duplicate += 1
                    except Exception as e:
                        validation_errors.append({"table": "schedule_items", "error": str(e), "houzz_item_id": iid})
                        sm.skipped += 1
                        conn.rollback()
                        continue

                conn.commit()

        total_imported = pm.imported + lm.imported + sm.imported

        return {
            "status": "ok" if not validation_errors else "partial",
            "total_imported": total_imported,
            "imported": {
                "projects": pm.to_dict(),
                "daily_logs": lm.to_dict(),
                "schedule_items": sm.to_dict(),
            },
            "validation_errors": validation_errors,
        }

    @staticmethod
    def status() -> dict:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        (SELECT COUNT(*) FROM houzz_projects)       AS projects,
                        (SELECT COUNT(*) FROM houzz_daily_logs)     AS daily_logs,
                        (SELECT COUNT(*) FROM houzz_schedule_items) AS schedule_items,
                        (SELECT MAX(synced_at) FROM houzz_daily_logs)     AS last_log_sync,
                        (SELECT MAX(synced_at) FROM houzz_schedule_items) AS last_sched_sync
                """)
                row = dict(cur.fetchone())
        return {
            "status": "ok",
            "table_counts": {
                "houzz_projects": row["projects"],
                "houzz_daily_logs": row["daily_logs"],
                "houzz_schedule_items": row["schedule_items"],
            },
            "last_sync": {
                "daily_logs": str(row["last_log_sync"]) if row["last_log_sync"] else None,
                "schedule_items": str(row["last_sched_sync"]) if row["last_sched_sync"] else None,
            },
        }
