"""
Houzz Connector — Reference Implementation of BaseConnector

Covers all 17 Houzz entity types:
  projects, daily_logs, schedule_items, files, time_entries, tasks,
  messages, budget, estimates, contracts, purchase_orders, change_orders,
  selections, vendors, contacts, team_members, subcontractors

Incremental sync:
  connector_sync_state.last_synced_at → Browser Agent passes changed_since param
  Only records updated after last_synced_at are extracted and sent here

Change detection:
  Every Browser extraction includes extracted_at timestamp.
  Connector skips records where synced_at >= extracted_at (already current).

Event publishing:
  After each entity batch persisted → n8n webhook triggers downstream miners.
"""

import os, json, logging
from datetime import datetime, date
from typing import Optional

from base_connector import BaseConnector, ConnectorResult

logger = logging.getLogger("hci.connector.houzz")

_N8N_WEBHOOK = os.environ.get("N8N_HOUZZ_SYNC_WEBHOOK", "")


class HouzzConnector(BaseConnector):

    name = "houzz"
    version = "2.0"
    supported_entities = [
        "projects",
        "daily_logs",
        "schedule_items",
        "files",
        "time_entries",
        "tasks",
        "messages",
        "budget",
        "estimates",
        "contracts",
        "purchase_orders",
        "change_orders",
        "selections",
        "vendors",
        "contacts",
        "team_members",
        "subcontractors",
    ]

    # ── Required field sets per entity ────────────────────────────────────────

    _REQUIRED = {
        "projects":        ["houzz_project_id"],
        "daily_logs":      ["houzz_log_id", "project_id"],
        "schedule_items":  ["houzz_item_id", "project_id"],
        "files":           ["houzz_file_id", "houzz_project_id"],
        "time_entries":    ["houzz_entry_id", "houzz_project_id"],
        "tasks":           ["houzz_task_id", "houzz_project_id"],
        "messages":        ["houzz_message_id", "houzz_project_id"],
        "budget":          ["houzz_project_id", "category"],
        "estimates":       ["houzz_estimate_id", "houzz_project_id"],
        "contracts":       ["houzz_contract_id", "houzz_project_id"],
        "purchase_orders": ["houzz_po_id", "houzz_project_id"],
        "change_orders":   ["houzz_co_id", "houzz_project_id"],
        "selections":      ["houzz_selection_id", "houzz_project_id"],
        "vendors":         ["houzz_vendor_id", "houzz_project_id"],
        "contacts":        ["houzz_contact_id"],
        "team_members":    ["houzz_member_id", "houzz_project_id"],
        "subcontractors":  ["houzz_sub_id", "houzz_project_id"],
    }

    # ── Stage 1: Validate ─────────────────────────────────────────────────────

    def validate(self, entity_type: str, record: dict) -> tuple[bool, list[str]]:
        errors = []
        for field in self._REQUIRED.get(entity_type, []):
            val = record.get(field)
            if not val or (isinstance(val, str) and not val.strip()):
                errors.append(f"missing required field: {field}")
        return (len(errors) == 0, errors)

    # ── Stage 2: Normalize ────────────────────────────────────────────────────

    def normalize(self, entity_type: str, record: dict) -> dict:
        norm = {k: v for k, v in record.items()}

        # Strip string IDs
        for key in list(norm.keys()):
            if key.endswith("_id") and isinstance(norm[key], str):
                norm[key] = norm[key].strip()

        # Normalize dates
        date_fields = [
            "start_date", "end_date", "log_date", "date", "due_date",
            "completed_date", "signed_date", "expiration_date", "sent_date",
            "approved_date", "issued_date", "expected_date", "received_date",
            "submitted_date", "insurance_expiry", "joined_date", "created_date",
            "as_of_date",
        ]
        for field in date_fields:
            if field in norm:
                norm[field] = _parse_date(norm[field])

        # Normalize money fields
        money_fields = [
            "budget", "total_amount", "contract_amount", "po_amount",
            "amount", "allowance_amount", "actual_amount", "budgeted_amount",
            "committed_amount",
        ]
        for field in money_fields:
            if field in norm and norm[field] is not None:
                try:
                    norm[field] = float(str(norm[field]).replace(",", "").replace("$", ""))
                except (ValueError, TypeError):
                    norm[field] = None

        # Normalize numeric
        if "hours" in norm and norm["hours"] is not None:
            try:
                norm["hours"] = float(norm["hours"])
            except (ValueError, TypeError):
                norm["hours"] = None

        if "completion_pct" in norm and norm["completion_pct"] is not None:
            try:
                norm["completion_pct"] = float(norm["completion_pct"])
            except (ValueError, TypeError):
                norm["completion_pct"] = None

        if "crew_size" in norm and norm["crew_size"] is not None:
            try:
                norm["crew_size"] = int(norm["crew_size"])
            except (ValueError, TypeError):
                norm["crew_size"] = None

        return norm

    # ── Stage 3: Persist ─────────────────────────────────────────────────────

    def persist(self, entity_type: str, record: dict, cur) -> bool:
        method = getattr(self, f"_persist_{entity_type}", None)
        if not method:
            raise NotImplementedError(f"No persist handler for {entity_type}")
        return method(record, cur)

    def _upsert(self, cur, sql: str, params: tuple) -> bool:
        cur.execute(sql, params)
        row = cur.fetchone()
        return bool(row and row.get("is_insert"))

    # ── Persist handlers ──────────────────────────────────────────────────────

    def _persist_projects(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_projects
                (houzz_project_id, name, client_name, status, address,
                 budget, start_date, end_date, project_type, properties, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_project_id) DO UPDATE SET
                name         = EXCLUDED.name,
                client_name  = EXCLUDED.client_name,
                status       = EXCLUDED.status,
                address      = COALESCE(EXCLUDED.address, houzz_projects.address),
                budget       = COALESCE(EXCLUDED.budget, houzz_projects.budget),
                start_date   = COALESCE(EXCLUDED.start_date, houzz_projects.start_date),
                end_date     = COALESCE(EXCLUDED.end_date, houzz_projects.end_date),
                project_type = COALESCE(EXCLUDED.project_type, houzz_projects.project_type),
                properties   = EXCLUDED.properties,
                synced_at    = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_project_id"), r.get("name"), r.get("client_name"),
            r.get("status"), r.get("address"), r.get("budget"),
            r.get("start_date"), r.get("end_date"), r.get("project_type"),
            json.dumps(r.get("properties") or {}),
        ))

    def _persist_daily_logs(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_daily_logs
                (houzz_log_id, project_id, log_date, content,
                 weather, crew_size, author, raw_json, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_log_id) DO UPDATE SET
                content   = COALESCE(EXCLUDED.content, houzz_daily_logs.content),
                weather   = COALESCE(EXCLUDED.weather, houzz_daily_logs.weather),
                crew_size = COALESCE(EXCLUDED.crew_size, houzz_daily_logs.crew_size),
                author    = COALESCE(EXCLUDED.author, houzz_daily_logs.author),
                raw_json  = COALESCE(EXCLUDED.raw_json, houzz_daily_logs.raw_json),
                synced_at = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_log_id"), r.get("project_id"), r.get("log_date"),
            r.get("content"), r.get("weather"), r.get("crew_size"),
            r.get("author"), json.dumps(r.get("raw_json")) if r.get("raw_json") else None,
        ))

    def _persist_schedule_items(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_schedule_items
                (houzz_item_id, project_id, title, start_date, end_date,
                 status, parent_item_id, assignee, completion_pct,
                 task_type, notes, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_item_id) DO UPDATE SET
                title          = COALESCE(EXCLUDED.title, houzz_schedule_items.title),
                start_date     = COALESCE(EXCLUDED.start_date, houzz_schedule_items.start_date),
                end_date       = COALESCE(EXCLUDED.end_date, houzz_schedule_items.end_date),
                status         = COALESCE(EXCLUDED.status, houzz_schedule_items.status),
                completion_pct = COALESCE(EXCLUDED.completion_pct, houzz_schedule_items.completion_pct),
                assignee       = COALESCE(EXCLUDED.assignee, houzz_schedule_items.assignee),
                notes          = COALESCE(EXCLUDED.notes, houzz_schedule_items.notes),
                synced_at      = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_item_id"), r.get("project_id"), r.get("title"),
            r.get("start_date"), r.get("end_date"), r.get("status"),
            r.get("parent_item_id"), r.get("assignee"), r.get("completion_pct"),
            r.get("task_type"), r.get("notes"),
        ))

    def _persist_files(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_files
                (houzz_file_id, houzz_project_id, file_name, file_type, category,
                 url, thumbnail_url, uploaded_by, uploaded_at, room, tags, raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_file_id) DO UPDATE SET
                file_name    = COALESCE(EXCLUDED.file_name, houzz_files.file_name),
                url          = COALESCE(EXCLUDED.url, houzz_files.url),
                category     = COALESCE(EXCLUDED.category, houzz_files.category),
                room         = COALESCE(EXCLUDED.room, houzz_files.room),
                tags         = COALESCE(EXCLUDED.tags, houzz_files.tags),
                raw_data     = EXCLUDED.raw_data,
                synced_at    = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_file_id"), r.get("houzz_project_id"), r.get("file_name"),
            r.get("file_type"), r.get("category"), r.get("url"), r.get("thumbnail_url"),
            r.get("uploaded_by"), r.get("uploaded_at"), r.get("room"),
            r.get("tags"), json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_time_entries(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_time_entries
                (houzz_entry_id, houzz_project_id, date, worker_name, role,
                 hours, description, cost_code, billable, raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_entry_id) DO UPDATE SET
                hours       = COALESCE(EXCLUDED.hours, houzz_time_entries.hours),
                description = COALESCE(EXCLUDED.description, houzz_time_entries.description),
                raw_data    = EXCLUDED.raw_data,
                synced_at   = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_entry_id"), r.get("houzz_project_id"), r.get("date"),
            r.get("worker_name"), r.get("role"), r.get("hours"), r.get("description"),
            r.get("cost_code"), r.get("billable", True), json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_tasks(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_tasks
                (houzz_task_id, houzz_project_id, title, description, status,
                 priority, assigned_to, due_date, completed_date, is_punch_list,
                 location, raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_task_id) DO UPDATE SET
                status         = COALESCE(EXCLUDED.status, houzz_tasks.status),
                completed_date = COALESCE(EXCLUDED.completed_date, houzz_tasks.completed_date),
                priority       = COALESCE(EXCLUDED.priority, houzz_tasks.priority),
                assigned_to    = COALESCE(EXCLUDED.assigned_to, houzz_tasks.assigned_to),
                raw_data       = EXCLUDED.raw_data,
                synced_at      = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_task_id"), r.get("houzz_project_id"), r.get("title"),
            r.get("description"), r.get("status"), r.get("priority"),
            r.get("assigned_to"), r.get("due_date"), r.get("completed_date"),
            r.get("is_punch_list", False), r.get("location"),
            json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_messages(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_messages
                (houzz_message_id, houzz_project_id, sender_name, sender_role,
                 message_text, sent_at, has_attachments, thread_id, raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_message_id) DO UPDATE SET
                raw_data  = EXCLUDED.raw_data,
                synced_at = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_message_id"), r.get("houzz_project_id"), r.get("sender_name"),
            r.get("sender_role"), r.get("message_text"), r.get("sent_at"),
            r.get("has_attachments", False), r.get("thread_id"),
            json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_budget(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_budget
                (houzz_project_id, category, budgeted_amount, actual_amount,
                 committed_amount, as_of_date, raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT DO UPDATE SET
                budgeted_amount  = COALESCE(EXCLUDED.budgeted_amount, houzz_budget.budgeted_amount),
                actual_amount    = COALESCE(EXCLUDED.actual_amount, houzz_budget.actual_amount),
                committed_amount = COALESCE(EXCLUDED.committed_amount, houzz_budget.committed_amount),
                raw_data         = EXCLUDED.raw_data,
                synced_at        = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_project_id"), r.get("category"), r.get("budgeted_amount"),
            r.get("actual_amount"), r.get("committed_amount"), r.get("as_of_date"),
            json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_estimates(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_estimates
                (houzz_estimate_id, houzz_project_id, estimate_number, title, status,
                 total_amount, created_date, sent_date, approved_date, client_name,
                 raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_estimate_id) DO UPDATE SET
                status        = COALESCE(EXCLUDED.status, houzz_estimates.status),
                total_amount  = COALESCE(EXCLUDED.total_amount, houzz_estimates.total_amount),
                approved_date = COALESCE(EXCLUDED.approved_date, houzz_estimates.approved_date),
                raw_data      = EXCLUDED.raw_data,
                synced_at     = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_estimate_id"), r.get("houzz_project_id"), r.get("estimate_number"),
            r.get("title"), r.get("status"), r.get("total_amount"), r.get("created_date"),
            r.get("sent_date"), r.get("approved_date"), r.get("client_name"),
            json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_contracts(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_contracts
                (houzz_contract_id, houzz_project_id, contract_number, title, status,
                 contract_amount, signed_date, expiration_date, counterparty,
                 raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_contract_id) DO UPDATE SET
                status          = COALESCE(EXCLUDED.status, houzz_contracts.status),
                contract_amount = COALESCE(EXCLUDED.contract_amount, houzz_contracts.contract_amount),
                signed_date     = COALESCE(EXCLUDED.signed_date, houzz_contracts.signed_date),
                raw_data        = EXCLUDED.raw_data,
                synced_at       = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_contract_id"), r.get("houzz_project_id"), r.get("contract_number"),
            r.get("title"), r.get("status"), r.get("contract_amount"), r.get("signed_date"),
            r.get("expiration_date"), r.get("counterparty"), json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_purchase_orders(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_purchase_orders
                (houzz_po_id, houzz_project_id, po_number, vendor_name, description,
                 status, po_amount, issued_date, expected_date, received_date,
                 raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_po_id) DO UPDATE SET
                status        = COALESCE(EXCLUDED.status, houzz_purchase_orders.status),
                received_date = COALESCE(EXCLUDED.received_date, houzz_purchase_orders.received_date),
                raw_data      = EXCLUDED.raw_data,
                synced_at     = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_po_id"), r.get("houzz_project_id"), r.get("po_number"),
            r.get("vendor_name"), r.get("description"), r.get("status"), r.get("po_amount"),
            r.get("issued_date"), r.get("expected_date"), r.get("received_date"),
            json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_change_orders(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_change_orders
                (houzz_co_id, houzz_project_id, co_number, title, description,
                 status, amount, reason, submitted_date, approved_date,
                 raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_co_id) DO UPDATE SET
                status        = COALESCE(EXCLUDED.status, houzz_change_orders.status),
                amount        = COALESCE(EXCLUDED.amount, houzz_change_orders.amount),
                approved_date = COALESCE(EXCLUDED.approved_date, houzz_change_orders.approved_date),
                raw_data      = EXCLUDED.raw_data,
                synced_at     = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_co_id"), r.get("houzz_project_id"), r.get("co_number"),
            r.get("title"), r.get("description"), r.get("status"), r.get("amount"),
            r.get("reason"), r.get("submitted_date"), r.get("approved_date"),
            json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_selections(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_selections
                (houzz_selection_id, houzz_project_id, category, item_name, description,
                 status, selected_option, allowance_amount, actual_amount, vendor,
                 due_date, raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_selection_id) DO UPDATE SET
                status          = COALESCE(EXCLUDED.status, houzz_selections.status),
                selected_option = COALESCE(EXCLUDED.selected_option, houzz_selections.selected_option),
                actual_amount   = COALESCE(EXCLUDED.actual_amount, houzz_selections.actual_amount),
                raw_data        = EXCLUDED.raw_data,
                synced_at       = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_selection_id"), r.get("houzz_project_id"), r.get("category"),
            r.get("item_name"), r.get("description"), r.get("status"),
            r.get("selected_option"), r.get("allowance_amount"), r.get("actual_amount"),
            r.get("vendor"), r.get("due_date"), json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_vendors(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_project_vendors
                (houzz_vendor_id, houzz_project_id, company_name, contact_name,
                 email, phone, trade, status, raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_vendor_id, houzz_project_id) DO UPDATE SET
                company_name = COALESCE(EXCLUDED.company_name, houzz_project_vendors.company_name),
                status       = COALESCE(EXCLUDED.status, houzz_project_vendors.status),
                raw_data     = EXCLUDED.raw_data,
                synced_at    = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_vendor_id"), r.get("houzz_project_id"), r.get("company_name"),
            r.get("contact_name"), r.get("email"), r.get("phone"), r.get("trade"),
            r.get("status"), json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_contacts(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_contacts
                (houzz_contact_id, houzz_project_id, name, role, email, phone,
                 company, raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_contact_id) DO UPDATE SET
                name     = COALESCE(EXCLUDED.name, houzz_contacts.name),
                email    = COALESCE(EXCLUDED.email, houzz_contacts.email),
                phone    = COALESCE(EXCLUDED.phone, houzz_contacts.phone),
                raw_data = EXCLUDED.raw_data,
                synced_at= NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_contact_id"), r.get("houzz_project_id"), r.get("name"),
            r.get("role"), r.get("email"), r.get("phone"), r.get("company"),
            json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_team_members(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_team_members
                (houzz_member_id, houzz_project_id, name, role, email,
                 permissions, joined_date, raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_member_id, houzz_project_id) DO UPDATE SET
                role        = COALESCE(EXCLUDED.role, houzz_team_members.role),
                permissions = COALESCE(EXCLUDED.permissions, houzz_team_members.permissions),
                raw_data    = EXCLUDED.raw_data,
                synced_at   = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_member_id"), r.get("houzz_project_id"), r.get("name"),
            r.get("role"), r.get("email"), r.get("permissions"), r.get("joined_date"),
            json.dumps(r.get("raw_data") or {}),
        ))

    def _persist_subcontractors(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO houzz_subcontractors
                (houzz_sub_id, houzz_project_id, company_name, contact_name,
                 trade, email, phone, license_number, insurance_expiry, status,
                 raw_data, synced_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (houzz_sub_id, houzz_project_id) DO UPDATE SET
                status           = COALESCE(EXCLUDED.status, houzz_subcontractors.status),
                insurance_expiry = COALESCE(EXCLUDED.insurance_expiry, houzz_subcontractors.insurance_expiry),
                raw_data         = EXCLUDED.raw_data,
                synced_at        = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r.get("houzz_sub_id"), r.get("houzz_project_id"), r.get("company_name"),
            r.get("contact_name"), r.get("trade"), r.get("email"), r.get("phone"),
            r.get("license_number"), r.get("insurance_expiry"), r.get("status"),
            json.dumps(r.get("raw_data") or {}),
        ))

    # ── Stage 4: Post-persist hook ─────────────────────────────────────────────

    def post_persist(self, entity_type: str, result: ConnectorResult) -> None:
        """Trigger downstream miners via n8n webhook after each entity batch."""
        if not _N8N_WEBHOOK:
            return
        try:
            import urllib.request, ssl, certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
            payload = {
                "event": "houzz_sync_complete",
                "entity_type": entity_type,
                "inserted": result.inserted,
                "updated": result.updated,
            }
            req = urllib.request.Request(
                _N8N_WEBHOOK,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5, context=ctx)
        except Exception as e:
            logger.warning("[houzz] Failed to trigger n8n webhook: %s", e)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_date(val) -> Optional[str]:
    if not val:
        return None
    if isinstance(val, date):
        return val.isoformat()
    try:
        return datetime.strptime(str(val)[:10], "%Y-%m-%d").date().isoformat()
    except (ValueError, TypeError):
        return None
