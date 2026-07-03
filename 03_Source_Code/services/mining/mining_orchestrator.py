"""
Mining Orchestrator — runs all 8 ACR-004 miners in sequence.
Used by FastAPI router and n8n scheduled workflows.
Miners run in order: source miners first, then intelligence miners, then aggregator.

SAFETY: dry_run=True by default until Buck issues go-live authorization.
"""
from datetime import datetime, timezone
from typing import Optional

from .hubspot_miner import HubSpotMiner
from .drive_miner import DriveMiner
from .houzz_miner import HouzzMiner
from .outlook_miner import OutlookMiner
from .historical_cost_miner import HistoricalCostMiner
from .vendor_intelligence_miner import VendorIntelligenceMiner
from .lessons_learned_miner import LessonsLearnedMiner
from .executive_aggregator import ExecutiveAggregator
from .base_miner import _pg

MINER_ORDER = [
    HubSpotMiner,
    DriveMiner,
    HouzzMiner,
    OutlookMiner,
    HistoricalCostMiner,
    VendorIntelligenceMiner,
    LessonsLearnedMiner,
    ExecutiveAggregator,
]

MINER_REGISTRY = {cls.MINER_NAME: cls for cls in MINER_ORDER}


def _touch_connector_registry(source_systems: list) -> None:
    """Mark connector_registry rows as freshly synced after a successful miner run.
    Added 2026-07-02: miners never touched this before, so drift-check's dead-connector
    rule kept flagging HubSpot/Drive/Houzz as never-synced even while mining ran fine -
    had to set it by hand once. External sources only (google_drive/hubspot/houzz/
    outlook) - the postgres:* sources on internal miners aren't tracked here."""
    external = [s for s in source_systems if not s.startswith("postgres:")]
    if not external:
        return
    try:
        with _pg() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE connector_registry SET last_indexed = NOW() WHERE source_system = ANY(%s)",
                    (external,),
                )
    except Exception:
        pass  # best-effort - never let this fail the actual mining run


class MiningOrchestrator:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def run_all(self) -> dict:
        """Run all 8 miners in sequence. Returns aggregated summary."""
        started = datetime.now(timezone.utc).isoformat()
        results = {}
        totals = {
            "records_scanned": 0, "records_discovered": 0,
            "intelligence_extracted": 0, "items_queued_for_review": 0,
            "items_auto_written": 0,
        }

        for MinerClass in MINER_ORDER:
            miner = MinerClass(dry_run=self.dry_run)
            try:
                result = miner.mine()
                results[MinerClass.MINER_NAME] = result.to_dict()
                for key in totals:
                    totals[key] += getattr(result, key, 0)
                if not self.dry_run:
                    _touch_connector_registry(MinerClass.SOURCE_SYSTEMS)
            except Exception as e:
                results[MinerClass.MINER_NAME] = {"status": "failed", "error": str(e)}

        return {
            "orchestrator": "MiningOrchestrator",
            "dry_run": self.dry_run,
            "started_at": started,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "miners_run": len(MINER_ORDER),
            "totals": totals,
            "results": results,
        }

    def run_miner(self, miner_name: str) -> dict:
        """Run a single named miner."""
        cls = MINER_REGISTRY.get(miner_name)
        if not cls:
            return {"error": f"Unknown miner: {miner_name}",
                    "available": list(MINER_REGISTRY.keys())}
        miner = cls(dry_run=self.dry_run)
        result = miner.mine()
        if not self.dry_run:
            _touch_connector_registry(cls.SOURCE_SYSTEMS)
        return result.to_dict()

    def get_status(self) -> dict:
        """Return mining engine status — recent runs, counts, health."""
        try:
            with _pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT miner_name, status, started_at, completed_at,
                               records_scanned, intelligence_extracted,
                               items_queued_for_review, items_auto_written,
                               dry_run, error_message
                        FROM mining_runs
                        ORDER BY started_at DESC
                        LIMIT 40
                    """)
                    rows = [dict(r) for r in cur.fetchall()]

                    cur.execute("""
                        SELECT miner_name,
                               MAX(completed_at) as last_run,
                               COUNT(*) as total_runs,
                               COUNT(*) FILTER (WHERE status='completed') as successes
                        FROM mining_runs
                        GROUP BY miner_name
                        ORDER BY miner_name
                    """)
                    per_miner = [dict(r) for r in cur.fetchall()]

                    cur.execute("""
                        SELECT SUM(intelligence_extracted) as total_extracted,
                               SUM(items_queued_for_review) as total_queued,
                               SUM(items_auto_written) as total_written
                        FROM mining_runs
                        WHERE status = 'completed'
                    """)
                    lifetime = dict(cur.fetchone() or {})
        except Exception as e:
            return {"status": "error", "error": str(e)}

        return {
            "status": "active",
            "registered_miners": list(MINER_REGISTRY.keys()),
            "dry_run_mode": self.dry_run,
            "lifetime_stats": lifetime,
            "per_miner_summary": per_miner,
            "recent_runs": rows[:20],
        }

    @staticmethod
    def available_miners() -> list:
        return [{"name": cls.MINER_NAME, "sources": cls.SOURCE_SYSTEMS,
                 "targets": cls.TARGET_STORES} for cls in MINER_ORDER]
