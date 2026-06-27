"""
ACR-004: Continuous Mining & Learning Engine — FastAPI router.
All mining runs are DRY RUN by default until Buck issues go-live authorization.
"""
import os, sys

_MINING_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "services", "mining"))
_SRC_DIR     = os.path.abspath(os.path.join(_MINING_DIR, "..", ".."))  # 03_Source_Code/

from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/mining", tags=["mining"])

_DRY_RUN_DEFAULT    = True
_GO_LIVE_AUTHORIZED = False


def _import_mining():
    """
    Import services.mining, handling the sys.path collision from main.py.
    main.py adds both 03_Source_Code/ AND 03_Source_Code/services/ to sys.path.
    That can cause Python to cache 'services' as a namespace package that doesn't
    include the mining subpackage.  We fix it once per process by ensuring the
    canonical 03_Source_Code/ is first and wiping any bad cached entries.
    """
    if _SRC_DIR not in sys.path:
        sys.path.insert(0, _SRC_DIR)

    # If 'services' is already cached but lacks mining, clear the stale entries.
    if "services" in sys.modules and "services.mining" not in sys.modules:
        stale = [k for k in sys.modules if k == "services" or k.startswith("services.")]
        for k in stale:
            del sys.modules[k]

    import services.mining.mining_orchestrator as _orch
    return _orch


def _pg():
    """Return the _pg context manager from base_miner (for log/summary endpoints)."""
    _import_mining()  # ensures sys.path is correct
    import services.mining.base_miner as _bm
    return _bm._pg


def _get_orchestrator(dry_run: bool = True):
    mod = _import_mining()
    return mod.MiningOrchestrator(dry_run=dry_run or _DRY_RUN_DEFAULT)


def _get_registry():
    mod = _import_mining()
    return mod.MINER_REGISTRY, mod.MiningOrchestrator


@router.get("/status")
def mining_status():
    """Current mining engine status — runs, counts, per-miner health."""
    return _get_orchestrator().get_status()


@router.get("/miners")
def list_miners():
    """List all 8 registered miners with their sources and targets."""
    registry, Orch = _get_registry()
    return {"miners": Orch.available_miners(), "total": len(registry)}


@router.post("/run/all")
def run_all_miners(dry_run: bool = Query(True, description="Run in dry-run mode (no writes)")):
    """Run all 8 miners in sequence. dry_run=True by default (safe to call anytime)."""
    return _get_orchestrator(dry_run).run_all()


@router.post("/run/{miner_name}")
def run_single_miner(
    miner_name: str,
    dry_run: bool = Query(True, description="Run in dry-run mode (no writes)")
):
    """Run a single named miner. dry_run=True by default."""
    registry, _ = _get_registry()
    if miner_name not in registry:
        raise HTTPException(status_code=404,
                            detail=f"Unknown miner: '{miner_name}'. "
                                   f"Available: {list(registry.keys())}")
    return _get_orchestrator(dry_run).run_miner(miner_name)


@router.get("/log")
def mining_log(limit: int = Query(20, le=100)):
    """Recent mining run log entries."""
    pg = _pg()
    with pg() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, miner_name, started_at, completed_at, status,
                       records_scanned, intelligence_extracted,
                       items_queued_for_review, items_auto_written,
                       dry_run, error_message
                FROM mining_runs
                ORDER BY started_at DESC
                LIMIT %s
            """, (limit,))
            rows = [dict(r) for r in cur.fetchall()]
    return {"runs": rows, "total": len(rows)}


@router.get("/summary")
def mining_intelligence_summary():
    """High-level summary of what the mining engine has extracted."""
    pg = _pg()
    with pg() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM background_learning_records")
            bl_total = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM background_learning_records WHERE review_status='Pending'")
            bl_pending = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM approval_queue WHERE status='pending'")
            aq_pending = cur.fetchone()["cnt"]
            cur.execute("SELECT COALESCE(SUM(intelligence_extracted),0) as total FROM mining_runs WHERE status='completed'")
            total_extracted = cur.fetchone()["total"] or 0
            cur.execute("""
                SELECT miner_name, SUM(intelligence_extracted) as extracted,
                       SUM(items_queued_for_review) as queued
                FROM mining_runs WHERE status='completed'
                GROUP BY miner_name ORDER BY extracted DESC
            """)
            by_miner = [dict(r) for r in cur.fetchall()]
    return {
        "total_intelligence_extracted": int(total_extracted),
        "background_learning_records": {"total": bl_total, "pending_review": bl_pending},
        "approval_queue_pending": aq_pending,
        "by_miner": by_miner,
        "note": "dry_run=True by default — authorize continuous execution via ChatGPT ACR",
    }
