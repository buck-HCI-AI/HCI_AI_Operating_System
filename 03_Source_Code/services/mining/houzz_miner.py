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
            LEFT JOIN projects p ON p.name ILIKE '%' || split_part(hp.name, ' ', 1) || '%'
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
        logs = self._query("""
            SELECT dl.id, dl.project_id, dl.log_date,
                   dl.content, dl.synced_at
            FROM houzz_daily_logs dl
            ORDER BY dl.log_date DESC NULLS LAST
            LIMIT 50
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
                        f"Daily log for project {log.get('project_id')} on {log.get('log_date')} "
                        f"contains risk signals. Review for lessons learned."
                    ),
                    payload={"log_id": log["id"], "log_date": str(log.get("log_date")),
                             "content_excerpt": content[:500]},
                    project_id=log.get("project_id"),
                    priority="low"
                )
                result.items_queued_for_review += 1

        return len(logs)

    def _mine_schedule(self, result: MiningResult) -> int:
        items = self._query("""
            SELECT si.id, si.project_id, si.title as task_name,
                   si.start_date, si.end_date, si.status
            FROM project_schedule_items si
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
                payload=dict(item),
                project_id=item.get("project_id"),
                priority="medium"
            )
            result.items_queued_for_review += 1

        return len(items)
