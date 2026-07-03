"""
ACR-004: Continuous Mining & Learning Engine — FastAPI router.
GO-LIVE AUTHORIZED by Buck Adams (Owner) 2026-06-27.
dry_run defaults True (safe) — pass dry_run=False for live execution.
"""
import os, sys
import importlib.util

_MINING_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "services", "mining"))
_SRC_DIR     = os.path.abspath(os.path.join(_MINING_DIR, "..", ".."))  # 03_Source_Code/
_MINING_PKG_ALIAS = "_hci_mining_pkg"  # see _import_mining() docstring

from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/mining", tags=["mining"])

_DRY_RUN_DEFAULT    = True   # default stays safe — explicit dry_run=False required for live
_GO_LIVE_AUTHORIZED = True   # authorized by Buck Adams (Owner) 2026-06-27


def _import_mining():
    """
    Load services/mining/ directly by file path under a private sys.modules alias.
    'services' as a dotted name is PERMANENTLY shadowed by 03_Source_Code/api/services/
    (a small, unrelated cache/db/storage/vector helper package used by documents.py,
    system.py, storage.py, search.py) because main.py inserts 03_Source_Code/api onto
    sys.path ahead of the project root. Clearing sys.modules['services'] and re-importing
    just re-triggers the same path search and finds api/services again every time -
    this was found 2026-07-02 after discovering it made every mining run (HubSpot/
    Houzz/Drive/Outlook sync) fail with ModuleNotFoundError, 100% of the time, since
    api/services was added on 06-26. Loading by absolute path under a private alias
    sidesteps the collision without touching the global 'services' name those other
    four routers depend on.
    """
    alias_orch = f"{_MINING_PKG_ALIAS}.mining_orchestrator"
    if alias_orch in sys.modules:
        return sys.modules[alias_orch]

    pkg_spec = importlib.util.spec_from_file_location(
        _MINING_PKG_ALIAS, os.path.join(_MINING_DIR, "__init__.py"),
        submodule_search_locations=[_MINING_DIR],
    )
    pkg_mod = importlib.util.module_from_spec(pkg_spec)
    sys.modules[_MINING_PKG_ALIAS] = pkg_mod
    pkg_spec.loader.exec_module(pkg_mod)

    orch_spec = importlib.util.spec_from_file_location(
        alias_orch, os.path.join(_MINING_DIR, "mining_orchestrator.py"),
    )
    orch_mod = importlib.util.module_from_spec(orch_spec)
    orch_mod.__package__ = _MINING_PKG_ALIAS
    sys.modules[alias_orch] = orch_mod
    orch_spec.loader.exec_module(orch_mod)
    return orch_mod


def _pg():
    """Return the _pg context manager from base_miner (for log/summary endpoints)."""
    _import_mining()  # ensures the private mining package alias is loaded
    return sys.modules[f"{_MINING_PKG_ALIAS}.base_miner"]._pg


def _get_orchestrator(dry_run: bool = True):
    mod = _import_mining()
    # When not authorized: force dry_run regardless of caller. When authorized: respect caller's intent.
    effective_dry_run = dry_run if _GO_LIVE_AUTHORIZED else True
    return mod.MiningOrchestrator(dry_run=effective_dry_run)


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
