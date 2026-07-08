"""
Houzz Intelligence Miner — reads houzz_daily_logs, houzz_projects, project_schedule_items.
Extracts: daily log intelligence, schedule variance signals, manpower data.
Writes to: background_learning_records, approval_queue (lessons learned candidates).

STATUS: Active framework. Live Houzz data requires Browser Agent extraction.
Architecture is ready — populate houzz_daily_logs via Browser Agent to activate.
"""
from .base_miner import BaseMiner, MiningResult


class HouzzMiner(BaseMiner):
    MINER_NAME = "houzz_miner"
    SOURCE_SYSTEMS = ["houzz"]
    TARGET_STORES = ["background_learning_records", "lessons_learned", "schedule_variance"]

    def mine(self) -> MiningResult:
        run_id = self.start_run()
        result = MiningResult(self.MINER_NAME, run_id)
        try:
            projects = self._mine_projects(result)
            daily_logs = self._mine_daily_logs(result)
            schedule = self._mine_schedule(result)
            result.summary = {
                "houzz_projects": projects,
                "daily_logs_scanned": daily_logs,
                "schedule_items_scanned": schedule,
                "status": "framework_active" if projects > 0 else "awaiting_browser_agent_data",
            }
            return self.complete_run(run_id, result)
        except Exception as e:
            return self.fail_run(run_id, str(e))

    def _mine_projects(self, result: MiningResult) -> int:
        projects = self._query("""
            SELECT hp.id, hp.name as project_name, hp.houzz_project_id,
                   p.id as db_project_id
            FROM houzz_projects hp
            LEFT JOIN projects p ON p.name = hp.name
            LIMIT 10
        """)
        result.records_scanned += len(projects)
        for hp in projects:
            self.register_discovery(
                source_system="houzz",
                source_id=str(hp.get("houzz_project_id") or hp["id"]),
                source_name=hp["project_name"] or hp.get("name", ""),
                project_id=hp.get("db_project_id"),
                metadata={"houzz_project_id": hp.get("houzz_project_id")}
            )
        return len(projects)

    def _mine_daily_logs(self, result: MiningResult) -> int:
        # dl.project_id stores the external Houzz project id (e.g. "3218059"), not our
        # internal projects.id - approval_queue.project_id is a real FK to projects.id.
        # Found 2026-07-07: this miner had been passing the raw Houzz id straight through
        # and failing its FK constraint on every single run since the daily mining engine
        # went live - the whole miner was dead on arrival, silently, because AUTO-004
        # itself wasn't executing (separate n8n/SQLite issue) so nobody ever saw the error.
        # Was LIMIT 50 ORDER BY log_date DESC across ALL projects combined - found
        # 2026-07-07 registering 212 Cleveland (a real historical/reference project,
        # logs dated 2025-08 through 2026-02) that its logs never got mined at all,
        # because live-project activity alone (101F/64EW/etc, all 2026 dates) fills
        # the top 50 every time. A single global recency window structurally can't
        # ever reach historical data - defeats the entire point of learning from
        # past jobs. Mine per-project instead, most-recent-first within each, so
        # every project (live or reference) gets covered regardless of what else
        # is happening system-wide.
        logs = self._query("""
            WITH ranked AS (
                SELECT dl.id, dl.project_id as houzz_project_id, dl.log_date,
                       dl.content, dl.synced_at,
                       ROW_NUMBER() OVER (PARTITION BY dl.project_id ORDER BY dl.log_date DESC NULLS LAST) as rn
                FROM houzz_daily_logs dl
            )
            SELECT r.id, r.houzz_project_id, r.log_date, r.content, r.synced_at, p.id as db_project_id
            FROM ranked r
            LEFT JOIN houzz_projects hp ON hp.houzz_project_id = r.houzz_project_id
            LEFT JOIN projects p ON p.name = hp.name
            WHERE r.rn <= 50
            ORDER BY r.log_date DESC NULLS LAST
        """)
        result.records_scanned += len(logs)

        for log in logs:
            result.intelligence_extracted += 1
            content = log.get("content") or ""
            risk_keywords = ["delay", "weather", "missing", "error", "change", "problem", "issue"]
            if any(kw in content.lower() for kw in risk_keywords):
                self.queue_for_approval(
                    action_type="lessons_learned_candidate",
                    title=f"Houzz daily log risk signal — {log.get('log_date')}",
                    description=(
                        f"Daily log for Houzz project {log.get('houzz_project_id')} on {log.get('log_date')} "
                        f"contains risk signals. Review for lessons learned."
                    ),
                    payload={"log_id": log["id"], "log_date": str(log.get("log_date")),
                             "content_excerpt": content[:500]},
                    project_id=log.get("db_project_id"),
                    priority="low"
                )
                result.items_queued_for_review += 1

        return len(logs)

    def _mine_schedule(self, result: MiningResult) -> int:
        # Same external-vs-internal project_id issue as _mine_daily_logs above.
        items = self._query("""
            SELECT si.id, si.project_id as houzz_project_id, si.title as task_name,
                   si.start_date, si.end_date, si.status, p.id as db_project_id
            FROM project_schedule_items si
            LEFT JOIN houzz_projects hp ON hp.houzz_project_id = si.project_id
            LEFT JOIN projects p ON p.name = hp.name
            WHERE si.status IN ('delayed', 'overdue', 'at_risk', 'behind')
            LIMIT 30
        """)
        result.records_scanned += len(items)

        for item in items:
            result.intelligence_extracted += 1
            self.queue_for_approval(
                action_type="schedule_variance",
                title=f"Schedule variance: {item.get('task_name')}",
                description=(
                    f"Houzz schedule item '{item.get('task_name')}' is {item.get('status')}. "
                    "Approve to update schedule_variance table."
                ),
                payload={k: v for k, v in item.items() if k != "db_project_id"},
                project_id=item.get("db_project_id"),
                priority="medium"
            )
            result.items_queued_for_review += 1

        return len(items)
