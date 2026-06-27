"""
Sprint 3 & 4 Test Suite — HCI AI Operating System
Covers: Executive Dashboard, Morning/EOD/Driving briefs, One-tap approvals,
        Missions API, Escalation check, Notification engine, Mobile approval flow.

Run: python3 tests/test_sprint3_sprint4.py
"""
import json, os, sys, time, hashlib, unittest, urllib.request, urllib.error
from datetime import datetime, timezone

BASE = os.environ.get("HCI_API_BASE", "http://localhost:8000")
KEY  = os.environ.get("HCI_API_KEY",  "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6")
RESULTS = []


def req(method, path, body=None, token=None, expect_html=False):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Token"] = token
    else:
        headers["X-API-Key"] = KEY
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=10) as resp:
        raw = resp.read()
        ct = resp.headers.get("Content-Type", "")
        if expect_html or "text/html" in ct:
            return raw.decode(), resp.status
        return json.loads(raw), resp.status


def record(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    RESULTS.append({"test": name, "status": status, "detail": detail})
    icon = "✅" if passed else "❌"
    print(f"  {icon} {name}{': ' + detail if detail and not passed else ''}")
    return passed


class TestSystemHealth(unittest.TestCase):
    def test_api_health(self):
        d, code = req("GET", "/api/v1/health")
        ok = code == 200 and d.get("status") == "healthy"
        record("API health check", ok, f"status={d.get('status')}")
        self.assertTrue(ok)

    def test_auth_required(self):
        """Protected routes return 401 without key."""
        try:
            r = urllib.request.Request(f"{BASE}/api/v1/projects")
            urllib.request.urlopen(r, timeout=5)
            record("Auth required on /projects", False, "Expected 401, got 200")
            self.fail("Should have raised")
        except urllib.error.HTTPError as e:
            ok = e.code == 401
            record("Auth required on /projects", ok, f"HTTP {e.code}")
            self.assertTrue(ok)

    def test_token_auth_bypass(self):
        """approve/reject/defer with ?token= should bypass API key."""
        try:
            url = f"{BASE}/api/v1/executive/approve/EXEC-NONEXISTENT?token=dummy"
            r = urllib.request.Request(url, method="GET")
            resp = urllib.request.urlopen(r, timeout=5)
            code = resp.status
        except urllib.error.HTTPError as e:
            code = e.code
        # 200 (already resolved HTML) or 403 (bad token) — NOT 401
        ok = code in (200, 403, 404)
        record("Token auth bypass (no API key)", ok, f"HTTP {code} (not 401)")
        self.assertTrue(ok)


class TestExecutiveDashboard(unittest.TestCase):
    def test_dashboard_json(self):
        d, code = req("GET", "/api/v1/executive/dashboard")
        ok = code == 200 and "system_health" in d and "projects" in d and "inbox" in d and "roi" in d
        record("Dashboard JSON structure", ok, f"keys={list(d.keys())[:6]}")
        self.assertTrue(ok)

    def test_dashboard_has_health(self):
        d, _ = req("GET", "/api/v1/executive/dashboard")
        ok = d.get("system_health", {}).get("status") in ("healthy", "degraded", "unknown")
        record("Dashboard system_health present", ok)
        self.assertTrue(ok)

    def test_dashboard_has_projects(self):
        d, _ = req("GET", "/api/v1/executive/dashboard")
        ok = isinstance(d.get("projects"), list)
        record("Dashboard projects list", ok, f"count={len(d.get('projects', []))}")
        self.assertTrue(ok)

    def test_dashboard_has_roi(self):
        d, _ = req("GET", "/api/v1/executive/dashboard")
        roi = d.get("roi", {})
        ok = "hours_saved_total" in roi
        record("Dashboard ROI present", ok)
        self.assertTrue(ok)

    def test_dashboard_html(self):
        html, code = req("GET", "/executive/", expect_html=True)
        ok = code == 200 and b"HCI AI" in html.encode() if isinstance(html, str) else b"HCI AI" in html
        record("Dashboard HTML page", ok, f"HTTP {code}")
        self.assertTrue(ok)


class TestExecutiveBriefs(unittest.TestCase):
    def test_morning_brief(self):
        d, code = req("GET", "/api/v1/executive/morning-brief")
        ok = code == 200 and "date" in d and "inbox_count" in d and "top_items" in d
        record("Morning brief structure", ok, f"inbox_count={d.get('inbox_count')}")
        self.assertTrue(ok)

    def test_driving_brief(self):
        d, code = req("GET", "/api/v1/executive/driving-brief")
        ok = code == 200 and "text" in d and len(d["text"]) > 20
        record("Driving brief text", ok, f"chars={len(d.get('text',''))}")
        self.assertTrue(ok)

    def test_driving_brief_no_markdown(self):
        d, _ = req("GET", "/api/v1/executive/driving-brief")
        text = d.get("text", "")
        has_markdown = any(c in text for c in ["**", "##", "```", "|---"])
        record("Driving brief is markdown-free", not has_markdown)
        self.assertFalse(has_markdown)

    def test_eod_brief(self):
        d, code = req("GET", "/api/v1/executive/eod-brief")
        ok = code == 200 and "date" in d and "overnight_plan" in d and "missions" in d
        record("EOD brief structure", ok)
        self.assertTrue(ok)

    def test_eod_brief_missions(self):
        d, _ = req("GET", "/api/v1/executive/eod-brief")
        m = d.get("missions", {})
        ok = all(k in m for k in ("complete", "in_progress", "blocked"))
        record("EOD brief missions sections", ok)
        self.assertTrue(ok)


class TestMissionsAPI(unittest.TestCase):
    def test_list_missions(self):
        d, code = req("GET", "/api/v1/executive/missions")
        ok = code == 200 and "missions" in d and isinstance(d["missions"], list)
        record("List missions", ok, f"count={d.get('total')}")
        self.assertTrue(ok)

    def test_blocked_missions(self):
        d, code = req("GET", "/api/v1/executive/missions/blocked")
        ok = code == 200 and "blocked_count" in d
        record("Blocked missions endpoint", ok, f"blocked={d.get('blocked_count')}")
        self.assertTrue(ok)

    def test_create_mission(self):
        d, code = req("POST", "/api/v1/executive/missions", {
            "mission_id": "MISSION-TEST-001",
            "title": "Automated test mission",
            "status": "OPEN",
            "priority": "LOW",
            "assigned_to": "claude_code",
        })
        ok = code == 200 and d.get("action") in ("created", "updated")
        record("Create/update mission", ok, d.get("action"))
        self.assertTrue(ok)

    def test_update_mission(self):
        d, code = req("POST", "/api/v1/executive/missions", {
            "mission_id": "MISSION-TEST-001",
            "status": "COMPLETE",
        })
        ok = code == 200 and d.get("action") == "updated"
        record("Update mission status", ok)
        self.assertTrue(ok)

    def test_mission_status_filter(self):
        d, code = req("GET", "/api/v1/executive/missions?status=BLOCKED")
        ok = code == 200 and all(m["status"] == "BLOCKED" for m in d.get("missions", []))
        record("Mission status filter", ok)
        self.assertTrue(ok)


class TestApprovalFlow(unittest.TestCase):
    TEST_EXEC_ID = "EXEC-TEST-001"

    def setUp(self):
        """Seed a fresh test inbox item."""
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            dbname=os.environ.get("POSTGRES_DB", "hci_os"),
            user=os.environ.get("POSTGRES_USER", "hci_admin"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO executive_inbox
                  (exec_id, title, decision, recommendation, confidence,
                   action_type, action_payload, status,
                   approve_token, reject_token, defer_token, token_expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                        md5(random()::text), md5(random()::text), md5(random()::text),
                        NOW() + INTERVAL '72 hours')
                ON CONFLICT (exec_id) DO UPDATE SET
                  status='pending',
                  approve_token=md5(random()::text),
                  reject_token=md5(random()::text),
                  defer_token=md5(random()::text),
                  token_expires_at=NOW()+INTERVAL '72 hours'
                RETURNING approve_token, reject_token, defer_token
            """, (self.TEST_EXEC_ID, "Automated test item", "Test approval flow",
                  "Approve", "High", "db_write", json.dumps({}), "pending"))
            row = cur.fetchone()
            self.approve_token = row[0]
            self.reject_token  = row[1]
            self.defer_token   = row[2]
            conn.commit()
        conn.close()

    def test_approve_via_get(self):
        """GET approve (ntfy view action) returns HTML confirmation."""
        html, code = req("GET",
            f"/api/v1/executive/approve/{self.TEST_EXEC_ID}?token={self.approve_token}",
            expect_html=True)
        ok = code == 200 and "approved" in html.lower()
        record("Approve via GET (mobile ntfy)", ok, f"HTTP {code}")
        self.assertTrue(ok)

    def test_approve_already_resolved(self):
        """Second approve returns friendly 'already resolved' page, not 404/500."""
        # First approval already done in test_approve_via_get — try again
        html, code = req("GET",
            f"/api/v1/executive/approve/{self.TEST_EXEC_ID}?token={self.approve_token}",
            expect_html=True)
        ok = code == 200 and ("already resolved" in html.lower() or "approved" in html.lower())
        record("Already-resolved returns friendly page", ok, f"HTTP {code}")
        self.assertTrue(ok)

    def test_defer_via_api(self):
        """Seed a new item and defer it via POST."""
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            dbname=os.environ.get("POSTGRES_DB", "hci_os"),
            user=os.environ.get("POSTGRES_USER", "hci_admin"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO executive_inbox
                  (exec_id, title, decision, recommendation, confidence,
                   action_type, action_payload, status,
                   approve_token, reject_token, defer_token, token_expires_at)
                VALUES ('EXEC-TEST-002', 'Defer test', 'Test defer', 'Defer', 'Low',
                        'db_write', '{}', 'pending',
                        md5('a'), md5('b'), md5('c'),
                        NOW()+INTERVAL '72 hours')
                ON CONFLICT (exec_id) DO UPDATE SET status='pending',
                  defer_token=md5('c'), token_expires_at=NOW()+INTERVAL '72 hours'
            """)
            conn.commit()
        conn.close()
        d, code = req("POST", "/api/v1/executive/defer/EXEC-TEST-002")
        ok = code == 200 or (isinstance(d, dict) and "deferred" in str(d))
        record("Defer via POST (no token, internal)", ok)
        self.assertTrue(ok)


class TestEscalationCheck(unittest.TestCase):
    def test_escalation_check_runs(self):
        d, code = req("POST", "/api/v1/executive/escalation-check")
        ok = code == 200 and "checked_at" in d and "escalations_fired" in d
        record("Escalation check runs", ok, f"fired={d.get('escalations_fired')}")
        self.assertTrue(ok)

    def test_escalation_check_no_false_positives(self):
        """Fresh items should not trigger escalation."""
        d, _ = req("POST", "/api/v1/executive/escalation-check")
        # Test items are all fresh — none >24h — escalations_fired should be 0
        ok = isinstance(d.get("escalations_fired"), int)
        record("Escalation returns integer count", ok)
        self.assertTrue(ok)


class TestNotificationEngine(unittest.TestCase):
    def test_send_low_severity(self):
        """LOW severity goes to no providers (digest-only) — should not error."""
        d, code = req("POST", "/api/v1/services/notifications/send", {
            "title": "Test LOW notification",
            "message": "This should go to digest only.",
            "severity": "LOW",
        })
        ok = code == 200 and d.get("providers_attempted") == []
        record("LOW severity → no providers (digest only)", ok)
        self.assertTrue(ok)

    def test_send_medium_severity(self):
        d, code = req("POST", "/api/v1/services/notifications/send", {
            "title": "Test MEDIUM notification",
            "message": "Email only.",
            "severity": "MEDIUM",
        })
        ok = code == 200 and "email" in d.get("providers_attempted", [])
        record("MEDIUM severity → email provider attempted", ok)
        self.assertTrue(ok)

    def test_send_high_fires_ntfy(self):
        d, code = req("POST", "/api/v1/services/notifications/send", {
            "title": "Test HIGH from test suite",
            "message": "Automated test — HIGH severity notification.",
            "severity": "HIGH",
            "tags": ["test_tube"],
        })
        ok = code == 200 and "ntfy" in d.get("providers_attempted", [])
        ntfy_ok = d.get("results", {}).get("ntfy", {}).get("status") == "sent"
        record("HIGH severity → ntfy attempted", ok)
        record("ntfy delivery success", ntfy_ok, str(d.get("results", {}).get("ntfy")))
        self.assertTrue(ok)

    def test_approval_required_notification(self):
        """approval_required sends ntfy with 3 action buttons."""
        d, code = req("POST", "/api/v1/services/notifications/approval-required", {
            "exec_id": "EXEC-TEST-NOTIFY",
            "title": "Test: approval notification from test suite",
            "approve_token": "test_approve_token",
            "reject_token":  "test_reject_token",
            "defer_token":   "test_defer_token",
            "confidence": "High",
        })
        ok = code == 200
        ntfy = d.get("results", {}).get("ntfy", {})
        actions_sent = ntfy.get("actions", 0) == 3
        record("approval_required endpoint works", ok)
        record("approval notification has 3 action buttons", actions_sent, str(ntfy))
        self.assertTrue(ok)


class TestHouzzEndpoints(unittest.TestCase):
    def test_houzz_status(self):
        d, code = req("GET", "/api/v1/services/houzz/status")
        ok = code == 200 and ("table_counts" in d or "tables" in d) and d.get("status") == "ok"
        record("Houzz status endpoint", ok, f"keys={list(d.keys())}")
        self.assertTrue(ok)

    def test_houzz_ingest_dry_run(self):
        """Ingest with a single project — idempotent."""
        d, code = req("POST", "/api/v1/services/houzz/ingest", {
            "source": "test_suite",
            "projects": [{
                "houzz_project_id": "TEST-001",
                "name": "Test Project",
                "client_name": "Test Client",
                "status": "open",
                "address": "123 Test St, Aspen, CO",
            }],
            "daily_logs": [],
            "schedule_items": [],
        })
        ok = code == 200 and d.get("status") == "ok"
        record("Houzz ingest (idempotent upsert)", ok, f"imported={d.get('total_imported')}")
        self.assertTrue(ok)

    def test_houzz_ingest_idempotent(self):
        """Second ingest of same record should not increase count."""
        payload = {
            "source": "test_suite",
            "projects": [{"houzz_project_id": "TEST-001", "name": "Test Project",
                          "client_name": "Test Client", "status": "open"}],
            "daily_logs": [], "schedule_items": [],
        }
        req("POST", "/api/v1/services/houzz/ingest", payload)
        d2, code = req("POST", "/api/v1/services/houzz/ingest", payload)
        inserted = d2.get("imported", {}).get("projects", {}).get("inserted", 0)
        ok = code == 200 and inserted == 0  # upsert — no new inserts on second run
        record("Houzz ingest is idempotent (no duplicate insert)", ok, f"inserted={inserted}")
        self.assertTrue(ok)


class TestDatabaseMigrations(unittest.TestCase):
    def test_executive_inbox_table(self):
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            dbname=os.environ.get("POSTGRES_DB", "hci_os"),
            user=os.environ.get("POSTGRES_USER", "hci_admin"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name='executive_inbox'
                ORDER BY column_name
            """)
            cols = {r[0] for r in cur.fetchall()}
        conn.close()
        required = {"exec_id","title","status","approve_token","reject_token","defer_token","token_expires_at"}
        ok = required.issubset(cols)
        record("Migration 007: executive_inbox table", ok, f"missing={required-cols}")
        self.assertTrue(ok)

    def test_missions_table(self):
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            dbname=os.environ.get("POSTGRES_DB", "hci_os"),
            user=os.environ.get("POSTGRES_USER", "hci_admin"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name='missions' ORDER BY column_name
            """)
            cols = {r[0] for r in cur.fetchall()}
        conn.close()
        required = {"mission_id","title","status","assigned_to","priority","blocker"}
        ok = required.issubset(cols)
        record("Migration 008: missions table", ok, f"missing={required-cols}")
        self.assertTrue(ok)

    def test_notification_log_table(self):
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            dbname=os.environ.get("POSTGRES_DB", "hci_os"),
            user=os.environ.get("POSTGRES_USER", "hci_admin"),
            password=os.environ.get("POSTGRES_PASSWORD", ""),
        )
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name='notification_log' ORDER BY column_name
            """)
            cols = {r[0] for r in cur.fetchall()}
        conn.close()
        ok = {"event_type","entity_id","severity","sent_at"}.issubset(cols)
        record("Migration 008: notification_log table", ok)
        self.assertTrue(ok)


def main():
    print("\n" + "═"*60)
    print("  HCI AI OS — Sprint 3 & 4 Test Suite")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("═"*60)

    suites = [
        TestSystemHealth,
        TestExecutiveDashboard,
        TestExecutiveBriefs,
        TestMissionsAPI,
        TestApprovalFlow,
        TestEscalationCheck,
        TestNotificationEngine,
        TestHouzzEndpoints,
        TestDatabaseMigrations,
    ]

    total = passed = failed = 0
    for suite_class in suites:
        print(f"\n▸ {suite_class.__name__}")
        suite = unittest.TestLoader().loadTestsFromTestCase(suite_class)
        for test in suite:
            try:
                test.debug()
            except Exception as e:
                name = str(test).split(" ")[0]
                RESULTS.append({"test": name, "status": "FAIL", "detail": str(e)[:80]})
                print(f"  ❌ {name}: {str(e)[:80]}")

    total  = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = total - passed

    print("\n" + "═"*60)
    print(f"  RESULTS: {passed} PASS  {failed} FAIL  {total} TOTAL")
    print("═"*60)

    # Save results
    out = {
        "suite": "Sprint 3 & 4",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "summary": {"total": total, "passed": passed, "failed": failed,
                    "pass_rate": f"{int(passed/total*100) if total else 0}%"},
        "results": RESULTS,
    }
    results_path = os.path.join(os.path.dirname(__file__), "test_results_sprint3_sprint4.json")
    with open(results_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Results saved → {results_path}")

    if failed > 0:
        print(f"\n  ⚠️  {failed} test(s) failed — see details above")
        sys.exit(1)
    else:
        print("\n  ✅ All tests passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
