"""
Connector Framework Test Suite — Sprint 5

Tests:
  - Migration 009 tables exist
  - connector_sync_state seeded
  - BaseConnector 7-stage pipeline (dry_run)
  - HouzzConnector all 17 entity types (dry_run)
  - Validate required fields
  - Normalize dates/money
  - API endpoints: GET /connectors, POST /connectors/houzz/ingest
  - Legacy houzz ingest still works
  - Full houzz ingest endpoint
  - Sync state API
"""

import sys, os, json, pytest, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services", "connectors"))

from fastapi.testclient import TestClient

os.chdir(os.path.join(os.path.dirname(__file__), "..", "api"))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

from main import app

client = TestClient(app, raise_server_exceptions=False)
API_KEY = "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"
H = {"X-API-Key": API_KEY}


# ── DB Fixtures ───────────────────────────────────────────────────────────────

import psycopg2, psycopg2.extras

def _pg():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        dbname=os.environ.get("POSTGRES_DB", "hci_os"),
        user=os.environ.get("POSTGRES_USER", "hci_admin"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. Migration 009 — schema validation
# ─────────────────────────────────────────────────────────────────────────────

class TestMigration009:

    EXPECTED_TABLES = [
        "connector_sync_state",
        "houzz_files", "houzz_time_entries", "houzz_tasks", "houzz_messages",
        "houzz_budget", "houzz_estimates", "houzz_contracts", "houzz_purchase_orders",
        "houzz_change_orders", "houzz_selections", "houzz_project_vendors",
        "houzz_contacts", "houzz_team_members", "houzz_subcontractors",
    ]

    def test_migration_009_tables_exist(self):
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                existing = {row["table_name"] for row in cur.fetchall()}

        missing = [t for t in self.EXPECTED_TABLES if t not in existing]
        assert not missing, f"Migration 009 tables missing: {missing}\nRun: psql -U hci_admin -d hci_os -f 05_Database/migrations/009_houzz_connector_framework.sql"

    def test_connector_sync_state_seeded(self):
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) AS cnt FROM connector_sync_state
                    WHERE connector_name='houzz' AND external_id='3218059'
                """)
                row = cur.fetchone()
        assert row["cnt"] >= 1, "connector_sync_state not seeded for Houzz project 3218059"

    def test_connector_sync_state_all_entities(self):
        expected_entities = [
            "projects", "daily_logs", "schedule_items", "files", "time_entries",
            "tasks", "messages", "budget", "estimates", "contracts",
            "purchase_orders", "change_orders", "selections", "vendors",
            "contacts", "team_members", "subcontractors",
        ]
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT entity_type FROM connector_sync_state
                    WHERE connector_name='houzz' AND external_id='3218059'
                """)
                found = {row["entity_type"] for row in cur.fetchall()}
        missing = [e for e in expected_entities if e not in found]
        assert not missing, f"Missing sync state rows: {missing}"

    def test_houzz_files_columns(self):
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name='houzz_files'
                """)
                cols = {row["column_name"] for row in cur.fetchall()}
        for col in ["houzz_file_id", "houzz_project_id", "file_name", "file_type", "raw_data"]:
            assert col in cols, f"Missing column houzz_files.{col}"

    def test_houzz_budget_variance_computed(self):
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name, generation_expression
                    FROM information_schema.columns
                    WHERE table_name='houzz_budget' AND column_name='variance'
                """)
                row = cur.fetchone()
        assert row is not None, "houzz_budget.variance column missing"


# ─────────────────────────────────────────────────────────────────────────────
# 2. HouzzConnector — unit tests (dry_run, no DB writes)
# ─────────────────────────────────────────────────────────────────────────────

class TestHouzzConnectorUnit:

    def _connector(self):
        from houzz_connector import HouzzConnector
        return HouzzConnector(dry_run=True)

    def test_supported_entities_count(self):
        from houzz_connector import HouzzConnector
        assert len(HouzzConnector.supported_entities) == 17

    def test_validate_projects_valid(self):
        c = self._connector()
        ok, errs = c.validate("projects", {"houzz_project_id": "3218059", "name": "Test"})
        assert ok and not errs

    def test_validate_projects_missing_id(self):
        c = self._connector()
        ok, errs = c.validate("projects", {"name": "Test"})
        assert not ok
        assert any("houzz_project_id" in e for e in errs)

    def test_validate_daily_logs_missing_project_id(self):
        c = self._connector()
        ok, errs = c.validate("daily_logs", {"houzz_log_id": "DL-001"})
        assert not ok
        assert any("project_id" in e for e in errs)

    def test_normalize_dates(self):
        c = self._connector()
        rec = {"houzz_project_id": "3218059", "start_date": "2026-03-15", "end_date": "2026-09-30"}
        norm = c.normalize("projects", rec)
        assert norm["start_date"] == "2026-03-15"
        assert norm["end_date"] == "2026-09-30"

    def test_normalize_money(self):
        c = self._connector()
        rec = {"houzz_project_id": "3218059", "budget": "$450,000"}
        norm = c.normalize("projects", rec)
        assert norm["budget"] == 450000.0

    def test_normalize_strips_ids(self):
        c = self._connector()
        rec = {"houzz_project_id": "  3218059  "}
        norm = c.normalize("projects", rec)
        assert norm["houzz_project_id"] == "3218059"

    def test_normalize_hours(self):
        c = self._connector()
        rec = {"houzz_entry_id": "TE-001", "houzz_project_id": "3218059", "hours": "8.5"}
        norm = c.normalize("time_entries", rec)
        assert norm["hours"] == 8.5

    def test_normalize_invalid_date_returns_none(self):
        c = self._connector()
        rec = {"houzz_project_id": "3218059", "start_date": "not-a-date"}
        norm = c.normalize("projects", rec)
        assert norm["start_date"] is None

    def test_all_entity_types_have_validators(self):
        from houzz_connector import HouzzConnector
        c = HouzzConnector(dry_run=True)
        for entity in HouzzConnector.supported_entities:
            assert entity in c._REQUIRED, f"No _REQUIRED entry for {entity}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. BaseConnector — dry_run pipeline
# ─────────────────────────────────────────────────────────────────────────────

class TestBaseConnectorDryRun:

    def _sample_payload(self):
        return {
            "projects": [
                {"houzz_project_id": "TEST-001", "name": "Dry Run Project",
                 "status": "active", "budget": "100000"},
            ],
            "daily_logs": [
                {"houzz_log_id": "DL-TEST-001", "project_id": "TEST-001",
                 "log_date": "2026-06-27", "content": "Dry run test log"},
            ],
            "tasks": [
                {"houzz_task_id": "T-TEST-001", "houzz_project_id": "TEST-001",
                 "title": "Test task", "status": "open"},
            ],
        }

    def test_dry_run_returns_correct_structure(self):
        from houzz_connector import HouzzConnector
        c = HouzzConnector(dry_run=True)
        result = c.ingest(self._sample_payload())
        assert result["dry_run"] is True
        assert result["connector"] == "houzz"
        assert "results" in result
        assert "total_inserted" in result

    def test_dry_run_counts_records(self):
        from houzz_connector import HouzzConnector
        c = HouzzConnector(dry_run=True)
        result = c.ingest(self._sample_payload())
        # Dry-run counts as inserted (validation pass)
        assert result["total_inserted"] >= 3

    def test_dry_run_does_not_write_to_db(self):
        from houzz_connector import HouzzConnector
        c = HouzzConnector(dry_run=True)
        c.ingest({"projects": [{"houzz_project_id": "DRYRUN-SENTINEL-99", "name": "Should not appear"}]})
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM houzz_projects WHERE houzz_project_id='DRYRUN-SENTINEL-99'")
                assert cur.fetchone() is None, "dry_run wrote to DB — this is a bug"

    def test_invalid_records_skipped_not_crashed(self):
        from houzz_connector import HouzzConnector
        c = HouzzConnector(dry_run=True)
        result = c.ingest({"projects": [{"name": "Missing ID"}]})
        proj = result["results"].get("projects", {})
        assert proj.get("skipped", 0) >= 1

    def test_mixed_valid_invalid(self):
        from houzz_connector import HouzzConnector
        c = HouzzConnector(dry_run=True)
        result = c.ingest({"projects": [
            {"houzz_project_id": "VALID-001", "name": "Valid"},
            {"name": "Invalid — no ID"},
        ]})
        proj = result["results"]["projects"]
        assert proj["attempted"] == 2
        assert proj["inserted"] == 1
        assert proj["skipped"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# 4. Connector API endpoints
# ─────────────────────────────────────────────────────────────────────────────

class TestConnectorAPI:

    def test_list_connectors(self):
        r = client.get("/api/v1/services/connectors", headers=H)
        assert r.status_code == 200
        data = r.json()
        assert "connectors" in data
        names = [c["name"] for c in data["connectors"]]
        assert "houzz" in names

    def test_connector_detail(self):
        r = client.get("/api/v1/services/connectors/houzz", headers=H)
        assert r.status_code == 200
        data = r.json()
        assert data["connector"] == "houzz"
        assert "supported_entities" in data
        assert len(data["supported_entities"]) == 17

    def test_unknown_connector_404(self):
        r = client.get("/api/v1/services/connectors/notarealconnector", headers=H)
        assert r.status_code == 404

    def test_ingest_dry_run(self):
        payload = {
            "dry_run": True,
            "source": "test_suite",
            "data": {
                "projects": [
                    {"houzz_project_id": "TEST-API-001", "name": "API Test Project",
                     "status": "active", "budget": 250000}
                ]
            }
        }
        r = client.post("/api/v1/services/connectors/houzz/ingest", headers=H, json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["dry_run"] is True
        assert data["connector"] == "houzz"
        assert data["total_inserted"] >= 1

    def test_ingest_empty_data_rejected(self):
        r = client.post("/api/v1/services/connectors/houzz/ingest", headers=H,
                        json={"dry_run": True, "data": {}})
        assert r.status_code == 422

    def test_ingest_multiple_entity_types(self):
        payload = {
            "dry_run": True,
            "source": "test_suite",
            "data": {
                "projects": [{"houzz_project_id": "TEST-MULTI-001", "name": "Multi Entity Test"}],
                "tasks": [{"houzz_task_id": "T-MULTI-001", "houzz_project_id": "TEST-MULTI-001", "title": "Test task"}],
                "messages": [{"houzz_message_id": "MSG-MULTI-001", "houzz_project_id": "TEST-MULTI-001",
                              "sender_name": "Test", "message_text": "Hello"}],
                "change_orders": [{"houzz_co_id": "CO-MULTI-001", "houzz_project_id": "TEST-MULTI-001",
                                   "title": "Test CO", "amount": 5000}],
                "budget": [{"houzz_project_id": "TEST-MULTI-001", "category": "Framing",
                            "budgeted_amount": 50000, "actual_amount": 45000}],
            }
        }
        r = client.post("/api/v1/services/connectors/houzz/ingest", headers=H, json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["total_inserted"] >= 5
        assert len(data["results"]) >= 5

    def test_sync_state_endpoint(self):
        r = client.get("/api/v1/services/connectors/houzz/sync-state", headers=H)
        assert r.status_code == 200
        data = r.json()
        assert "sync_states" in data
        assert len(data["sync_states"]) >= 1

    def test_sync_state_entity_filter(self):
        r = client.get("/api/v1/services/connectors/houzz/sync-state?entity_type=daily_logs&external_id=3218059", headers=H)
        assert r.status_code == 200
        data = r.json()
        assert data["entity_type"] == "daily_logs"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Legacy Houzz ingest (backwards compat)
# ─────────────────────────────────────────────────────────────────────────────

class TestHouzzLegacyAPI:

    def test_legacy_ingest_still_works(self):
        payload = {
            "projects": [{"houzz_project_id": "LEGACY-001", "name": "Legacy Test"}],
            "daily_logs": [],
            "schedule_items": [],
        }
        r = client.post("/api/v1/services/houzz/ingest", headers=H, json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "imported" in data or "total_imported" in data

    def test_houzz_status_includes_new_tables(self):
        r = client.get("/api/v1/services/houzz/status", headers=H)
        assert r.status_code == 200
        data = r.json()
        counts = data.get("table_counts", data.get("tables", {}))
        new_tables = ["houzz_files", "houzz_tasks", "houzz_change_orders"]
        for table in new_tables:
            assert table in counts, f"New table {table} missing from status response"

    def test_houzz_full_ingest_endpoint(self):
        payload = {
            "dry_run": True,
            "source": "test_suite",
            "projects": [{"houzz_project_id": "FULL-001", "name": "Full Ingest Test"}],
            "tasks": [{"houzz_task_id": "T-FULL-001", "houzz_project_id": "FULL-001",
                       "title": "Punch list item", "is_punch_list": True}],
            "selections": [{"houzz_selection_id": "SEL-FULL-001", "houzz_project_id": "FULL-001",
                            "category": "Plumbing", "item_name": "Faucet", "status": "pending"}],
        }
        r = client.post("/api/v1/services/houzz/ingest/full", headers=H, json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data["dry_run"] is True
        assert data["total_inserted"] >= 3
        assert "projects" in data["results"]


# ─────────────────────────────────────────────────────────────────────────────
# 6. All 17 entity types — dry_run validation pass
# ─────────────────────────────────────────────────────────────────────────────

class TestAllEntityTypes:
    """Verify every entity type passes validate → normalize in dry_run."""

    SAMPLES = {
        "projects":        {"houzz_project_id": "T", "name": "Test", "budget": "100000"},
        "daily_logs":      {"houzz_log_id": "T", "project_id": "T", "log_date": "2026-06-27", "crew_size": "6"},
        "schedule_items":  {"houzz_item_id": "T", "project_id": "T", "completion_pct": "75"},
        "files":           {"houzz_file_id": "T", "houzz_project_id": "T", "file_type": "photo"},
        "time_entries":    {"houzz_entry_id": "T", "houzz_project_id": "T", "hours": "8"},
        "tasks":           {"houzz_task_id": "T", "houzz_project_id": "T", "title": "Task"},
        "messages":        {"houzz_message_id": "T", "houzz_project_id": "T", "message_text": "Hi"},
        "budget":          {"houzz_project_id": "T", "category": "Framing", "budgeted_amount": "$50,000"},
        "estimates":       {"houzz_estimate_id": "T", "houzz_project_id": "T", "total_amount": "125000"},
        "contracts":       {"houzz_contract_id": "T", "houzz_project_id": "T", "contract_amount": "450000"},
        "purchase_orders": {"houzz_po_id": "T", "houzz_project_id": "T", "po_amount": "18500"},
        "change_orders":   {"houzz_co_id": "T", "houzz_project_id": "T", "amount": "4500"},
        "selections":      {"houzz_selection_id": "T", "houzz_project_id": "T", "category": "Plumbing"},
        "vendors":         {"houzz_vendor_id": "T", "houzz_project_id": "T", "company_name": "ACME"},
        "contacts":        {"houzz_contact_id": "T", "name": "Jane"},
        "team_members":    {"houzz_member_id": "T", "houzz_project_id": "T", "name": "Buck"},
        "subcontractors":  {"houzz_sub_id": "T", "houzz_project_id": "T", "company_name": "Rocky Mtn Electric"},
    }

    @pytest.mark.parametrize("entity_type", SAMPLES.keys())
    def test_entity_validates_and_normalizes(self, entity_type):
        from houzz_connector import HouzzConnector
        c = HouzzConnector(dry_run=True)
        record = self.SAMPLES[entity_type]
        ok, errs = c.validate(entity_type, record)
        assert ok, f"{entity_type} validation failed: {errs}"
        norm = c.normalize(entity_type, record)
        assert isinstance(norm, dict)
        # Money fields should be float or None
        for mf in ["budget", "total_amount", "budgeted_amount", "po_amount", "amount", "contract_amount"]:
            if mf in norm and norm[mf] is not None:
                assert isinstance(norm[mf], float), f"{entity_type}.{mf} should be float, got {type(norm[mf])}"

    @pytest.mark.parametrize("entity_type", SAMPLES.keys())
    def test_entity_ingest_dry_run(self, entity_type):
        from houzz_connector import HouzzConnector
        c = HouzzConnector(dry_run=True)
        result = c.ingest({entity_type: [self.SAMPLES[entity_type]]})
        assert result["total_inserted"] >= 1, f"{entity_type} dry_run returned 0 inserted"


# ─────────────────────────────────────────────────────────────────────────────
# 7. Regression — Sprint 3 & 4 still passing
# ─────────────────────────────────────────────────────────────────────────────

class TestRegressionSprint3Sprint4:

    def test_health_check(self):
        r = client.get("/health", headers=H)
        assert r.status_code == 200

    def test_executive_dashboard_accessible(self):
        r = client.get("/api/v1/executive/dashboard", headers=H)
        assert r.status_code == 200

    def test_executive_morning_brief(self):
        r = client.get("/api/v1/executive/morning-brief", headers=H)
        assert r.status_code == 200

    def test_houzz_intelligence_status(self):
        r = client.get("/api/v1/services/houzz/status", headers=H)
        assert r.status_code == 200

    def test_missions_list(self):
        r = client.get("/api/v1/executive/missions", headers=H)
        assert r.status_code == 200

    def test_services_list(self):
        r = client.get("/api/v1/services", headers=H)
        assert r.status_code == 200
        data = r.json()
        names = [s["name"] for s in data.get("services", [])]
        assert "connectors" in names
        assert "houzz-intelligence" in names


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
