"""
Autonomous System Auditor — Phase 3
Nightly self-evaluation: APIs, connectors, workflows, tests, documentation,
security, data freshness, technical debt, and recommendations.

Mounted at /api/v1/services/system-auditor
"""
import os, sys, json, time, subprocess, re
from datetime import datetime, timezone, date, timedelta
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter
from base import BaseIntelligenceService

router = APIRouter()

# Paths
_ROOT = Path(os.path.dirname(__file__)).parent.parent.parent  # HCI_AI_Operating_System
_SVC_DIR = Path(os.path.dirname(__file__)).parent             # services/
_API_DIR = _SVC_DIR.parent / "api"
_TESTS_DIR = _SVC_DIR.parent / "tests"
_DOCS_DIR = _ROOT / "04_Documentation"
_WORKFLOWS_DIR = _SVC_DIR.parent / "workflows"

API_BASE = "http://localhost:8000"
API_KEY = os.environ.get("HCI_API_KEY", "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6")
N8N_BASE = "http://localhost:5678/api/v1"


# ── All known service endpoints to probe ──────────────────────────────────────

_SERVICE_PROBES = [
    ("/api/v1/health", "core"),
    ("/api/v1/executive/morning-brief", "executive"),
    ("/api/v1/executive/mission-control", "executive"),
    ("/api/v1/leadership/dashboard", "operations"),
    ("/api/v1/superintendent/1/today", "operations"),
    ("/api/v1/pm/1/weekly", "operations"),
    ("/api/v1/reports/weekly/company", "operations"),
    ("/api/v1/services/project-brain/1/health", "project-brain"),
    ("/api/v1/services/project-brain/1/risks", "project-brain"),
    ("/api/v1/services/cross-project/health-matrix", "cross-project"),
    ("/api/v1/services/cross-project/company-snapshot", "cross-project"),
    ("/api/v1/services/predictive-engine/1/predictions", "predictive-engine"),
    ("/api/v1/services/predictive-engine/company/predictions", "predictive-engine"),
    ("/api/v1/services/bid-leveling", "bid-leveling"),
    ("/api/v1/services/approval-queue", "approval-queue"),
    ("/api/v1/services/connectors/health", "connectors"),
    ("/api/v1/services/autonomy/opportunities", "autonomy"),
    ("/api/v1/services", "core"),
]

_SERVICES_WITH_TESTS = [
    ("project_brain", "test_phase2_intelligence.py"),
    ("cross_project", "test_phase2_intelligence.py"),
    ("predictive_engine", "test_predictive_engine.py"),
    ("operations", "test_phase2_intelligence.py"),
]


class SystemAuditor(BaseIntelligenceService):
    SERVICE_NAME = "system_auditor"

    def __init__(self):
        self._auto_fixes_applied = []

    def run_audit(self) -> dict:
        started = time.time()
        results = {}

        results["api_health"] = self._audit_api_health()
        results["connector_health"] = self._audit_connector_health()
        results["workflow_health"] = self._audit_workflow_health()
        results["test_coverage"] = self._audit_test_coverage()
        results["documentation_coverage"] = self._audit_documentation()
        results["technical_debt"] = self._audit_technical_debt()
        results["data_freshness"] = self._audit_data_freshness()
        results["security_review"] = self._audit_security()
        results["recommendations"] = self._compile_recommendations(results)
        results["next_milestones"] = self._next_milestones()
        results["auto_fixes_applied"] = self._auto_fixes_applied

        elapsed = round(time.time() - started, 1)
        overall_score = self._overall_health_score(results)

        report = {
            "audit_date": date.today().isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": elapsed,
            "overall_health_score": overall_score,
            "overall_health_label": self._score_label(overall_score),
            **results,
        }
        self._persist_audit(report, overall_score)
        return report

    # ── API Health ─────────────────────────────────────────────────────────────

    def _audit_api_health(self) -> dict:
        import urllib.request, urllib.error
        results = []
        down = []
        total_latency = 0

        for path, category in _SERVICE_PROBES:
            t0 = time.time()
            try:
                req = urllib.request.Request(
                    API_BASE + path,
                    headers={"X-API-Key": API_KEY}
                )
                with urllib.request.urlopen(req, timeout=10) as r:
                    status = r.status
                    latency = round((time.time() - t0) * 1000)
                    total_latency += latency
                    results.append({"path": path, "category": category,
                                    "status": status, "latency_ms": latency, "ok": True})
            except urllib.error.HTTPError as e:
                latency = round((time.time() - t0) * 1000)
                results.append({"path": path, "category": category,
                                "status": e.code, "latency_ms": latency, "ok": e.code < 500})
                if e.code >= 500:
                    down.append(path)
            except Exception as ex:
                results.append({"path": path, "category": category,
                                "status": 0, "latency_ms": 0, "ok": False, "error": str(ex)})
                down.append(path)

        ok_count = sum(1 for r in results if r["ok"])
        avg_latency = round(total_latency / max(ok_count, 1))
        return {
            "score": round(ok_count / len(results) * 100),
            "endpoints_checked": len(results),
            "endpoints_healthy": ok_count,
            "endpoints_down": down,
            "avg_latency_ms": avg_latency,
            "slow_endpoints": [r["path"] for r in results if r.get("latency_ms", 0) > 2000],
            "details": results,
        }

    # ── Connector Health ───────────────────────────────────────────────────────

    def _audit_connector_health(self) -> dict:
        rows = self.pg_query("""
            SELECT connector_name, entity_type, last_synced_at, status,
                   records_synced, error_message,
                   CURRENT_DATE - last_synced_at::date AS days_stale
            FROM connector_sync_state
            ORDER BY last_synced_at DESC NULLS LAST
        """)

        stale = []
        errored = []
        never_synced = []

        for r in rows:
            days_val = r.get("days_stale")
            days = int(days_val) if days_val is not None else 9999
            name = r.get("connector_name", "unknown")
            if not r.get("last_synced_at"):
                never_synced.append(name)
            elif days > 7:
                stale.append({"connector": name, "days_stale": days})
            if r.get("status") == "error":
                errored.append({"connector": name, "error": r.get("error_message","")[:100]})

        healthy = max(0, len(rows) - len(stale) - len(errored) - len(never_synced))
        score = round(healthy / max(len(rows), 1) * 100) if rows else 50

        return {
            "score": score,
            "total_connectors": len(rows),
            "healthy": max(healthy, 0),
            "stale": stale,
            "errored": errored,
            "never_synced": never_synced,
            "missing_connectors": self._detect_missing_connectors(rows),
        }

    def _detect_missing_connectors(self, existing_rows: list) -> list:
        existing = {r.get("connector_name","").lower() for r in existing_rows}
        expected = {
            "hubspot": "HubSpot CRM — contacts, deals, notes",
            "houzz": "Houzz — schedule, budget, change orders",
            "microsoft_outlook": "Outlook — email, calendar",
            "google_drive": "Drive — SOPs, bid trackers",
        }
        return [
            {"connector": k, "description": v}
            for k, v in expected.items()
            if not any(k in e for e in existing)
        ]

    # ── Workflow Health ────────────────────────────────────────────────────────

    def _audit_workflow_health(self) -> dict:
        try:
            import urllib.request, urllib.error
            n8n_key = os.environ.get("N8N_API_KEY", "")
            if not n8n_key:
                return {"score": 0, "note": "N8N_API_KEY not configured", "workflows": []}

            req = urllib.request.Request(
                f"{N8N_BASE}/workflows?limit=100",
                headers={"X-N8N-API-KEY": n8n_key}
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())

            workflows = data.get("data", [])
            active = [w for w in workflows if w.get("active")]
            inactive = [w for w in workflows if not w.get("active")]

            # Cross-check: workflows on disk that might be missing from n8n
            disk_workflows = list((_WORKFLOWS_DIR / "n8n").glob("*.json")) if (_WORKFLOWS_DIR / "n8n").exists() else []
            disk_names = {f.stem.upper() for f in disk_workflows}
            n8n_names = {w.get("name","").upper() for w in workflows}
            not_imported = [n for n in disk_names if not any(n in nn for nn in n8n_names)]

            score = round(len(active) / max(len(workflows), 1) * 100) if workflows else 50
            return {
                "score": score,
                "total_workflows": len(workflows),
                "active": len(active),
                "inactive": len(inactive),
                "inactive_names": [w.get("name") for w in inactive],
                "disk_workflows_not_in_n8n": not_imported,
            }
        except Exception as e:
            return {"score": 0, "error": str(e), "note": "n8n API unavailable"}

    # ── Test Coverage ──────────────────────────────────────────────────────────

    def _audit_test_coverage(self) -> dict:
        # Find all services
        services = [d.name for d in _SVC_DIR.iterdir()
                    if d.is_dir() and not d.name.startswith("_") and not d.name.startswith(".")]

        # Find all test files and read their contents
        test_files = list(_TESTS_DIR.glob("test_*.py")) if _TESTS_DIR.exists() else []
        # Read test content to check if service names appear in test bodies
        all_test_content = ""
        for tf in test_files:
            try:
                all_test_content += tf.read_text(errors="replace").lower()
            except Exception:
                pass

        covered = []
        uncovered = []
        for svc in sorted(services):
            svc_slug = svc.replace("_", "-")
            # Check service name in test file names OR test file contents
            has_test = (svc in all_test_content or
                        svc_slug in all_test_content or
                        any(svc in f.name or svc_slug in f.name for f in test_files))
            if has_test:
                covered.append(svc)
            else:
                uncovered.append(svc)

        # Check last test results
        test_results = []
        for result_file in sorted(_TESTS_DIR.glob("test_results_*.json"), reverse=True)[:5]:
            try:
                data = json.loads(result_file.read_text())
                test_results.append({
                    "file": result_file.name,
                    "passed": data.get("passed"),
                    "failed": data.get("failed"),
                    "pass_rate": data.get("pass_rate"),
                    "run_at": data.get("run_at"),
                })
            except Exception:
                pass

        pct = round(len(covered) / max(len(services), 1) * 100)
        return {
            "score": pct,
            "services_total": len(services),
            "services_covered": len(covered),
            "services_uncovered": uncovered,
            "test_files": [f.name for f in test_files],
            "latest_results": test_results,
        }

    # ── Documentation Coverage ─────────────────────────────────────────────────

    def _audit_documentation(self) -> dict:
        docs_present = []
        docs_missing = []

        spec_files = {
            "CONSTRUCTION_INTELLIGENCE_MODEL.md": "Overall platform model",
            "PROJECT_BRAIN_SPEC.md": "Project Brain intelligence spec",
            "SUPERINTENDENT_DAILY_CONSOLE_SPEC.md": "SS Console spec",
            "PM_WEEKLY_CONSOLE_SPEC.md": "PM Console spec",
            "LEADERSHIP_MISSION_CONTROL_SPEC.md": "Leadership dashboard spec",
            "WEEKLY_REPORTING_ENGINE_SPEC.md": "Weekly reporting spec",
            "SYSTEM_AUDITOR_SPEC.md": "System auditor spec",
            "ROLE_BASED_OPERATING_MODEL.md": "Role-based operating model",
            "LIVE_PROJECT_STATE.md": "Live project state",
        }

        # Check in docs dir, architecture dir, and root
        search_dirs = [_DOCS_DIR, _ROOT, _ROOT / "03_Source_Code", _ROOT / "architecture"]
        for doc_name, description in spec_files.items():
            found = any((d / doc_name).exists() for d in search_dirs if d.exists())
            if found:
                docs_present.append(doc_name)
            else:
                docs_missing.append({"file": doc_name, "description": description})

        # Services without README
        services = [d for d in _SVC_DIR.iterdir() if d.is_dir() and not d.name.startswith("_")]
        services_without_readme = [d.name for d in services if not (d / "README.md").exists()]

        pct = round(len(docs_present) / max(len(spec_files), 1) * 100)
        return {
            "score": pct,
            "spec_docs_present": docs_present,
            "spec_docs_missing": docs_missing,
            "services_without_readme": services_without_readme[:10],
            "recommendation": "Run architecture documentation generator to create missing specs" if docs_missing else None,
        }

    # ── Technical Debt ─────────────────────────────────────────────────────────

    def _audit_technical_debt(self) -> dict:
        debt_items = []
        todo_count = 0
        fixme_count = 0
        hack_count = 0

        patterns = [
            (re.compile(r'\bTODO\b', re.IGNORECASE), "todo"),
            (re.compile(r'\bFIXME\b', re.IGNORECASE), "fixme"),
            (re.compile(r'\bHACK\b', re.IGNORECASE), "hack"),
            (re.compile(r'\bXXX\b'), "xxx"),
        ]

        scan_dirs = [_SVC_DIR, _API_DIR / "routers"]
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            for py_file in scan_dir.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue
                try:
                    content = py_file.read_text(errors="replace")
                    for pattern, label in patterns:
                        matches = pattern.findall(content)
                        if matches:
                            if label == "todo": todo_count += len(matches)
                            elif label == "fixme": fixme_count += len(matches)
                            elif label == "hack": hack_count += len(matches)
                except Exception:
                    pass

        # Check for duplicate code patterns (basic)
        debt_summary = []
        if todo_count > 10:
            debt_summary.append(f"{todo_count} TODO comments across codebase")
        if fixme_count > 0:
            debt_summary.append(f"{fixme_count} FIXME items requiring attention")
        if hack_count > 0:
            debt_summary.append(f"{hack_count} HACK workarounds to be cleaned up")

        # DB health indicators
        empty_tables = self.pg_query("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='public' AND table_type='BASE TABLE'
              AND table_name NOT IN ('spatial_ref_sys')
            ORDER BY table_name
        """)
        empty_count = 0
        for t in empty_tables:
            tname = t.get("table_name")
            try:
                row = self.pg_one(f'SELECT COUNT(*) as n FROM "{tname}"')
                if row and int(row.get("n") or 0) == 0:
                    empty_count += 1
            except Exception:
                pass

        if empty_count > 5:
            debt_summary.append(f"{empty_count} empty DB tables — may indicate missing data pipeline")

        # Services with no routes or placeholder status
        placeholder_services = []
        for svc_dir in _SVC_DIR.iterdir():
            if not svc_dir.is_dir() or svc_dir.name.startswith("_"):
                continue
            routes_file = svc_dir / "routes.py"
            if routes_file.exists():
                content = routes_file.read_text(errors="replace")
                if '"status": "planned"' in content or "'planned'" in content:
                    placeholder_services.append(svc_dir.name)

        score = max(0, 100 - todo_count - (fixme_count * 3) - (hack_count * 2) - len(placeholder_services) * 5)
        score = min(100, score)

        return {
            "score": score,
            "todo_count": todo_count,
            "fixme_count": fixme_count,
            "hack_count": hack_count,
            "debt_summary": debt_summary,
            "empty_db_tables": empty_count,
            "placeholder_services": placeholder_services,
        }

    # ── Data Freshness ─────────────────────────────────────────────────────────

    def _audit_data_freshness(self) -> dict:
        # Check key tables for recent data
        freshness_checks = [
            ("connector_sync_state", "last_synced_at", "Connector sync"),
            ("executive_inbox", "created_at", "Executive inbox"),
            ("approval_queue", "created_at", "Approval queue"),
            ("roi_log", "created_at", "ROI tracking"),
            ("missions", "last_activity", "AI missions"),
            ("project_brain_snapshots", "created_at", "Project brain"),
            ("company_intelligence_snapshots", "created_at", "Company intelligence"),
            ("predictions_computed", "generated_at", "Predictions"),
            ("background_learning_records", "created_at", "Background learning"),
        ]

        results = []
        stale_tables = []

        for table, ts_col, label in freshness_checks:
            try:
                row = self.pg_one(f"""
                    SELECT MAX({ts_col}) as last_update,
                           COUNT(*) as row_count,
                           CURRENT_DATE - MAX({ts_col})::date AS days_since
                    FROM {table}
                """)
                days_val = row.get("days_since") if row else None
                days = int(days_val) if days_val is not None else 999
                count = int(row.get("row_count") or 0) if row else 0
                last = str(row.get("last_update",""))[:10] if row else None
                is_stale = days > 3 or count == 0
                if is_stale:
                    stale_tables.append(label)
                results.append({
                    "table": table,
                    "label": label,
                    "row_count": count,
                    "last_update": last,
                    "days_since_update": days if days < 999 else None,
                    "status": "stale" if is_stale else "fresh",
                })
            except Exception as e:
                results.append({"table": table, "label": label, "error": str(e), "status": "unknown"})

        # Houzz data availability
        houzz_check = self.pg_one("SELECT COUNT(*) as n FROM project_schedule_items")
        houzz_empty = int((houzz_check or {}).get("n") or 0) == 0

        score = round((len(results) - len(stale_tables)) / max(len(results), 1) * 100)
        return {
            "score": score,
            "tables_checked": len(results),
            "stale_tables": stale_tables,
            "houzz_data_available": not houzz_empty,
            "houzz_note": "Run Houzz Browser Extraction to unlock schedule/budget/vendor intelligence" if houzz_empty else None,
            "details": results,
        }

    # ── Security Review ────────────────────────────────────────────────────────

    def _audit_security(self) -> dict:
        findings = []
        passed = []

        # Check .env is not in git
        try:
            result = subprocess.run(
                ["git", "ls-files", ".env", "03_Source_Code/.env"],
                capture_output=True, text=True, cwd=str(_ROOT)
            )
            if result.stdout.strip():
                findings.append("CRITICAL: .env file tracked in git")
            else:
                passed.append(".env not tracked in git")
        except Exception:
            pass

        # Check .gitignore exists and includes .env
        gitignore = _ROOT / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if ".env" in content:
                passed.append(".gitignore includes .env")
            else:
                findings.append("WARNING: .gitignore does not include .env")
        else:
            findings.append("WARNING: No .gitignore found at repo root")

        # Check for hardcoded credentials in code (basic scan)
        credential_patterns = [
            re.compile(r'password\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
            re.compile(r'api_key\s*=\s*["\'][^"\']{10,}["\']', re.IGNORECASE),
            re.compile(r'secret\s*=\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
        ]
        suspicious_files = []
        for py_file in _API_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(errors="replace")
                for pattern in credential_patterns:
                    matches = pattern.findall(content)
                    for m in matches:
                        # Exclude obvious placeholder patterns and env lookups
                        if "os.environ" not in m and "os.getenv" not in m and "localhost" not in m:
                            suspicious_files.append(f"{py_file.name}: {m[:60]}")
                            break
            except Exception:
                pass

        if suspicious_files:
            findings.append(f"Potential hardcoded credentials in {len(suspicious_files)} files")
        else:
            passed.append("No hardcoded credential patterns detected")

        # API key middleware present
        if ((_API_DIR / "middleware" / "auth.py").exists()):
            passed.append("API key authentication middleware present")
        else:
            findings.append("WARNING: API key auth middleware not found")

        score = max(0, 100 - len(findings) * 20)
        return {
            "score": score,
            "findings": findings,
            "passed_checks": passed,
            "suspicious_files": suspicious_files[:5],
        }

    # ── Recommendations ────────────────────────────────────────────────────────

    def _compile_recommendations(self, results: dict) -> list:
        recs = []

        # From API health
        api = results.get("api_health", {})
        if api.get("endpoints_down"):
            recs.append({
                "priority": "HIGH",
                "category": "api",
                "title": f"{len(api['endpoints_down'])} API endpoints are down",
                "action": f"Investigate: {', '.join(api['endpoints_down'][:3])}",
                "auto_fixable": False,
            })
        if api.get("avg_latency_ms", 0) > 1500:
            recs.append({
                "priority": "MEDIUM",
                "category": "performance",
                "title": f"High API latency: {api['avg_latency_ms']}ms average",
                "action": "Profile slow endpoints and add caching for expensive queries",
                "auto_fixable": False,
            })

        # From connector health
        conn = results.get("connector_health", {})
        if conn.get("stale"):
            recs.append({
                "priority": "HIGH",
                "category": "connectors",
                "title": f"{len(conn['stale'])} connectors are stale (>7 days since sync)",
                "action": "Review connector sync schedules and credentials",
                "auto_fixable": False,
            })
        if conn.get("missing_connectors"):
            for mc in conn["missing_connectors"]:
                recs.append({
                    "priority": "MEDIUM",
                    "category": "integration",
                    "title": f"Missing connector: {mc['connector']}",
                    "action": f"Implement {mc['connector']} connector — {mc['description']}",
                    "auto_fixable": False,
                })

        # From workflow health
        wf = results.get("workflow_health", {})
        if wf.get("inactive"):
            recs.append({
                "priority": "MEDIUM",
                "category": "workflows",
                "title": f"{wf['inactive']} n8n workflows are inactive",
                "action": f"Activate: {', '.join((wf.get('inactive_names') or [])[:3])}",
                "auto_fixable": False,
            })
        if wf.get("disk_workflows_not_in_n8n"):
            not_imp = wf["disk_workflows_not_in_n8n"]
            recs.append({
                "priority": "MEDIUM",
                "category": "workflows",
                "title": f"{len(not_imp)} workflow JSON files not imported to n8n",
                "action": f"Import via n8n UI: {', '.join(not_imp[:3])}",
                "auto_fixable": False,
            })

        # From test coverage
        tests = results.get("test_coverage", {})
        uncovered = tests.get("services_uncovered", [])
        if uncovered:
            recs.append({
                "priority": "MEDIUM",
                "category": "testing",
                "title": f"{len(uncovered)} services have no automated tests",
                "action": f"Write tests for: {', '.join(uncovered[:5])}",
                "auto_fixable": False,
            })

        # From documentation
        docs = results.get("documentation_coverage", {})
        missing_docs = docs.get("spec_docs_missing", [])
        if missing_docs:
            recs.append({
                "priority": "MEDIUM",
                "category": "documentation",
                "title": f"{len(missing_docs)} architecture spec documents missing",
                "action": "Generate missing spec docs (will auto-generate in next pass)",
                "auto_fixable": True,
            })

        # From data freshness
        fresh = results.get("data_freshness", {})
        if not fresh.get("houzz_data_available"):
            recs.append({
                "priority": "HIGH",
                "category": "data",
                "title": "Houzz schedule/budget data not synced",
                "action": "Run Houzz Browser Extraction for 64 Eastwood, 101 Francis, 1355 Riverside",
                "auto_fixable": False,
                "requires_human": True,
            })

        # From security
        sec = results.get("security_review", {})
        for finding in sec.get("findings", []):
            recs.append({
                "priority": "CRITICAL" if "CRITICAL" in finding else "HIGH",
                "category": "security",
                "title": finding,
                "action": "Immediately remediate security finding",
                "auto_fixable": False,
            })

        # From autonomy_opportunities DB
        try:
            opps = self.pg_query("""
                SELECT title, description, category, roi_score, feasibility
                FROM autonomy_opportunities
                WHERE status='backlog' AND feasibility IN ('high','medium')
                ORDER BY roi_score DESC NULLS LAST
                LIMIT 3
            """)
            for opp in opps:
                recs.append({
                    "priority": "LOW",
                    "category": "automation_opportunity",
                    "title": opp.get("title", ""),
                    "action": opp.get("description", "")[:200],
                    "roi_score": float(opp.get("roi_score") or 0),
                    "auto_fixable": opp.get("feasibility") == "high",
                })
        except Exception:
            pass

        recs.sort(key=lambda r: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(r["priority"], 4))
        return recs

    def _next_milestones(self) -> list:
        return [
            {
                "priority": 1,
                "title": "Generate Architecture Specification Documents",
                "description": "Create 8 spec docs: CONSTRUCTION_INTELLIGENCE_MODEL, PROJECT_BRAIN_SPEC, SS/PM/Leadership console specs, Weekly Reporting spec, System Auditor spec, Role-Based Operating Model",
                "phase": "Phase 3 / BTW-2",
                "estimated_effort": "2-3 hours",
            },
            {
                "priority": 2,
                "title": "Houzz Browser Data Extraction",
                "description": "Extract live schedule, budget, change orders for 64EW, 101F, 1355R — unlocks real-time schedule/budget predictions",
                "phase": "Data Pipeline",
                "estimated_effort": "Buck: 15 min per project in browser",
                "requires_human": True,
            },
            {
                "priority": 3,
                "title": "Expand Test Coverage to All Services",
                "description": "Write automated test files for services without coverage: bid_intelligence, vendor_intelligence, document_intelligence, schedule_intelligence, risk_intelligence, kpi_intelligence, decision_intelligence",
                "phase": "Phase 3 Testing",
                "estimated_effort": "3-4 hours",
            },
            {
                "priority": 4,
                "title": "n8n Workflow Activation Audit",
                "description": "Verify all 17 automation workflows are active and working — AUTO-SS-MORNING, AUTO-PM-WEEKLY, AUTO-WEEKLY-JOB, AUTO-WEEKLY-COMPANY plus 13 existing",
                "phase": "Operations",
                "estimated_effort": "30 min",
            },
            {
                "priority": 5,
                "title": "Phase 3 Autonomous Architecture Reviews",
                "description": "Schedule nightly audit cron via n8n to auto-trigger this auditor and surface issues in executive inbox",
                "phase": "Phase 3",
                "estimated_effort": "1 hour",
            },
        ]

    # ── Scoring ────────────────────────────────────────────────────────────────

    def _overall_health_score(self, results: dict) -> int:
        weights = {
            "api_health": 0.30,
            "connector_health": 0.10,
            "workflow_health": 0.10,
            "test_coverage": 0.15,
            "documentation_coverage": 0.10,
            "technical_debt": 0.10,
            "data_freshness": 0.10,
            "security_review": 0.15,
        }
        total = 0
        for key, weight in weights.items():
            score = results.get(key, {}).get("score", 50)
            total += score * weight
        return round(total)

    @staticmethod
    def _score_label(score: int) -> str:
        if score >= 80:
            return "HEALTHY"
        if score >= 60:
            return "NEEDS_ATTENTION"
        if score >= 40:
            return "DEGRADED"
        return "CRITICAL"

    # ── Persistence ────────────────────────────────────────────────────────────

    def _persist_audit(self, report: dict, score: int):
        try:
            import psycopg2
            from dotenv import load_dotenv
            load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
            conn = psycopg2.connect(
                host=os.environ.get("POSTGRES_HOST", "localhost"),
                port=int(os.environ.get("POSTGRES_PORT", 5432)),
                dbname=os.environ.get("POSTGRES_DB", "hci_os"),
                user=os.environ.get("POSTGRES_USER", "hci_admin"),
                password=os.environ.get("POSTGRES_PASSWORD", ""),
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO system_audit_reports
                    (audit_date, overall_health_score, overall_health_label,
                     api_health, connector_health, workflow_health,
                     test_coverage, documentation_coverage, technical_debt,
                     data_freshness, security_review, recommendations,
                     next_milestones, auto_fixes_applied, elapsed_seconds)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (audit_date) DO UPDATE SET
                    overall_health_score = EXCLUDED.overall_health_score,
                    overall_health_label = EXCLUDED.overall_health_label,
                    api_health = EXCLUDED.api_health,
                    connector_health = EXCLUDED.connector_health,
                    workflow_health = EXCLUDED.workflow_health,
                    test_coverage = EXCLUDED.test_coverage,
                    documentation_coverage = EXCLUDED.documentation_coverage,
                    technical_debt = EXCLUDED.technical_debt,
                    data_freshness = EXCLUDED.data_freshness,
                    security_review = EXCLUDED.security_review,
                    recommendations = EXCLUDED.recommendations,
                    next_milestones = EXCLUDED.next_milestones,
                    auto_fixes_applied = EXCLUDED.auto_fixes_applied,
                    updated_at = NOW()
            """, (
                report["audit_date"], score, report["overall_health_label"],
                json.dumps(report.get("api_health", {})),
                json.dumps(report.get("connector_health", {})),
                json.dumps(report.get("workflow_health", {})),
                json.dumps(report.get("test_coverage", {})),
                json.dumps(report.get("documentation_coverage", {})),
                json.dumps(report.get("technical_debt", {})),
                json.dumps(report.get("data_freshness", {})),
                json.dumps(report.get("security_review", {})),
                json.dumps(report.get("recommendations", [])),
                json.dumps(report.get("next_milestones", [])),
                json.dumps(report.get("auto_fixes_applied", [])),
                report.get("elapsed_seconds", 0),
            ))
            conn.close()
        except Exception:
            pass


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("")
def service_info():
    return {
        "service": "system_auditor",
        "status": "active",
        "phase": 3,
        "description": "Autonomous nightly system auditor — APIs, connectors, workflows, tests, docs, security, data freshness",
        "endpoints": [
            "GET /run — trigger full audit now",
            "GET /latest — most recent audit report",
            "GET /history — audit history (last 30 days)",
            "GET /recommendations — actionable improvement list",
        ],
    }


@router.get("/run")
def run_audit():
    """Trigger a full system audit. Takes 5-15 seconds."""
    auditor = SystemAuditor()
    return auditor.run_audit()


@router.get("/latest")
def latest_audit():
    """Most recent stored audit report."""
    svc = SystemAuditor()
    row = svc.pg_one("""
        SELECT * FROM system_audit_reports
        ORDER BY audit_date DESC LIMIT 1
    """)
    if not row:
        return {"message": "No audit reports found. Run GET /run to generate first report."}
    result = dict(row)
    for col in ["api_health","connector_health","workflow_health","test_coverage",
                "documentation_coverage","technical_debt","data_freshness",
                "security_review","recommendations","next_milestones","auto_fixes_applied"]:
        if col in result and isinstance(result[col], str):
            try:
                result[col] = json.loads(result[col])
            except Exception:
                pass
    return result


@router.get("/history")
def audit_history(days: int = 30):
    """Audit history — health scores over time."""
    svc = SystemAuditor()
    rows = svc.pg_query("""
        SELECT audit_date, overall_health_score, overall_health_label,
               elapsed_seconds, created_at
        FROM system_audit_reports
        WHERE audit_date >= CURRENT_DATE - %s
        ORDER BY audit_date DESC
    """, (days,))
    return {"history": [dict(r) for r in rows], "days": days}


@router.get("/recommendations")
def recommendations():
    """Actionable improvement recommendations from latest audit."""
    svc = SystemAuditor()
    row = svc.pg_one("""
        SELECT audit_date, overall_health_score, recommendations, next_milestones
        FROM system_audit_reports
        ORDER BY audit_date DESC LIMIT 1
    """)
    if not row:
        return {"message": "Run GET /run first to generate recommendations."}
    recs = row.get("recommendations") or []
    milestones = row.get("next_milestones") or []
    if isinstance(recs, str):
        recs = json.loads(recs)
    if isinstance(milestones, str):
        milestones = json.loads(milestones)
    return {
        "as_of": str(row.get("audit_date",""))[:10],
        "overall_health_score": row.get("overall_health_score"),
        "recommendations": recs,
        "next_milestones": milestones,
    }
