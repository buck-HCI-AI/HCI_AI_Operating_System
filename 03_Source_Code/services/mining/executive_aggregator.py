"""
Executive Intelligence Aggregator — synthesizes outputs from all miners.
Generates portfolio health snapshot, ROI update, approval queue summary.
Writes to: kpi_snapshots, roi_log, LIVE_PROJECT_STATE.md (header section only).
All writes are generated summaries — safe for auto-write.
"""
import os, json
from datetime import datetime, timezone
from .base_miner import BaseMiner, MiningResult

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


class ExecutiveAggregator(BaseMiner):
    MINER_NAME = "executive_aggregator"
    SOURCE_SYSTEMS = ["postgres:all_tables"]
    TARGET_STORES = ["kpi_snapshots", "roi_log", "LIVE_PROJECT_STATE.md"]

    def mine(self) -> MiningResult:
        run_id = self.start_run()
        result = MiningResult(self.MINER_NAME, run_id)
        try:
            snapshot = self._build_portfolio_snapshot()
            self._write_kpi_snapshot(snapshot)
            mining_summary = self._get_mining_summary()
            self._update_live_state_header(snapshot, mining_summary)
            result.intelligence_extracted = 1
            result.items_auto_written = 2
            result.summary = snapshot
            return self.complete_run(run_id, result)
        except Exception as e:
            return self.fail_run(run_id, str(e))

    def _build_portfolio_snapshot(self) -> dict:
        projects = self._query("SELECT id, name, status FROM projects WHERE status = 'active'")
        roi = self._query_one("SELECT COALESCE(SUM(minutes_saved),0) as total FROM roi_log")
        pending_queue = self._query_one(
            "SELECT COUNT(*) as cnt FROM approval_queue WHERE status = 'pending'"
        )
        risks = self._query_one(
            "SELECT COUNT(*) as cnt FROM risks WHERE status = 'open'"
        )
        vendors = self._query_one("SELECT COUNT(*) as cnt FROM vendors")
        lessons = self._query_one("SELECT COUNT(*) as cnt FROM lessons_learned")
        cost_records = self._query_one("SELECT COUNT(*) as cnt FROM historical_cost_records")
        bl_total = self._query_one("SELECT COUNT(*) as cnt FROM background_learning_records")
        last_mining = self._query_one("""
            SELECT MAX(completed_at) as last_run
            FROM mining_runs WHERE status = 'completed'
        """)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "active_projects": len(projects),
            "project_names": [p["name"] for p in projects],
            "total_roi_minutes": int(roi["total"] if roi else 0),
            "pending_approvals": int(pending_queue["cnt"] if pending_queue else 0),
            "open_risks": int(risks["cnt"] if risks else 0),
            "vendor_count": int(vendors["cnt"] if vendors else 0),
            "lessons_learned_count": int(lessons["cnt"] if lessons else 0),
            "historical_cost_records": int(cost_records["cnt"] if cost_records else 0),
            "background_learning_records": int(bl_total["cnt"] if bl_total else 0),
            "last_mining_run": str(last_mining["last_run"]) if last_mining and last_mining["last_run"] else "never",
        }

    def _write_kpi_snapshot(self, snapshot: dict):
        for kpi_code, value in [
            ("active_projects", snapshot.get("active_projects", 0)),
            ("total_roi_minutes", snapshot.get("total_roi_minutes", 0)),
            ("pending_approvals", snapshot.get("pending_approvals", 0)),
            ("open_risks", snapshot.get("open_risks", 0)),
            ("lessons_learned_count", snapshot.get("lessons_learned_count", 0)),
            ("historical_cost_records", snapshot.get("historical_cost_records", 0)),
            ("background_learning_records", snapshot.get("background_learning_records", 0)),
        ]:
            self._execute("""
                INSERT INTO kpi_snapshots
                    (kpi_code, scope, value, unit, source_service, calculated_at)
                VALUES (%s, 'portfolio', %s, 'count', 'executive_aggregator', NOW())
            """, (kpi_code, float(value)))

    def _get_mining_summary(self) -> dict:
        recent = self._query("""
            SELECT miner_name, status, completed_at,
                   intelligence_extracted, items_queued_for_review
            FROM mining_runs
            WHERE completed_at > NOW() - INTERVAL '25 hours'
            ORDER BY completed_at DESC
        """)
        return {
            "miners_ran_today": len(recent),
            "miners": [{"name": r["miner_name"], "status": r["status"],
                        "extracted": r["intelligence_extracted"]} for r in recent]
        }

    def _update_live_state_header(self, snapshot: dict, mining_summary: dict):
        """Update the 'Last Updated' line and mining status in LIVE_PROJECT_STATE.md."""
        live_path = os.path.join(REPO_ROOT, "LIVE_PROJECT_STATE.md")
        if not os.path.exists(live_path):
            return
        if self.dry_run:
            return

        now_mst = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M MST")
        try:
            with open(live_path) as f:
                content = f.read()

            import re
            content = re.sub(
                r'\*\*Last Updated:\*\*.*',
                f"**Last Updated:** {now_mst}",
                content
            )
            content = re.sub(
                r'\*\*Updated By:\*\*.*',
                f"**Updated By:** AUTO (executive_aggregator) — {snapshot['active_projects']} projects, "
                f"{snapshot['total_roi_minutes']} min ROI, "
                f"{snapshot['pending_approvals']} pending approvals",
                content
            )

            with open(live_path, "w") as f:
                f.write(content)
        except Exception:
            pass
