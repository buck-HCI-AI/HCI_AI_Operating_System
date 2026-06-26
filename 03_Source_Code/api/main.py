#!/usr/bin/env python3
"""
HCI AI Operating System — FastAPI Layer v1
Single integration point for all applications, automations, and AI agents.

Versioned API:  /api/v1/*
Legacy routes:  /projects, /vendors, /bids, /memory, /workflows, /ingest (unchanged)
Docs:           http://localhost:8000/docs
"""
import sys, os, logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "workflows"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services"))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from config import settings
from middleware.logging import RequestLoggingMiddleware
from middleware.auth import ApiKeyMiddleware

from routers import projects, vendors, bids, memory, health, workflows, ingest
from routers import auth, documents, storage, search, system, ai
from routers import sop
from routers import platform as platform_router

# Construction Intelligence Services — loaded via importlib to avoid service.py name collisions
import importlib.util as _ilu

def _load_svc(name: str):
    """Load a service's routes.py as a uniquely-named module."""
    path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "services", name, "routes.py"))
    spec = _ilu.spec_from_file_location(f"svc_{name}", path)
    mod  = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.router

pb_routes    = _load_svc("project_brain")
bi_routes    = _load_svc("bid_intelligence")
vi_routes    = _load_svc("vendor_intelligence")
proc_routes  = _load_svc("procurement")
hc_routes    = _load_svc("historical_cost")
ll_routes    = _load_svc("lessons_learned")
sched_routes = _load_svc("schedule_intelligence")
risk_routes  = _load_svc("risk_intelligence")
doc_intel_routes     = _load_svc("document_intelligence")
decision_routes      = _load_svc("decision_intelligence")
kpi_routes           = _load_svc("kpi_intelligence")
op_rules_routes      = _load_svc("operating_rules")
bpl_routes           = _load_svc("business_process_library")

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("hci.api")

# ── Application ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    description=(
        "HCI AI Operating System API — single interface for all applications, "
        "automations, and AI agents. PostgreSQL, Redis, MinIO, and Qdrant are "
        "exposed exclusively through this API."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={"name": "Hendrickson Construction Intelligence", "email": "buck@hendricksoninc.com"},
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ApiKeyMiddleware, valid_keys=settings.valid_api_keys)

# ── /api/v1 versioned router ──────────────────────────────────────────────────

v1 = APIRouter(prefix="/api/v1")

v1.include_router(health.router,     tags=["health"])
v1.include_router(auth.router,       prefix="/auth",      tags=["auth"])
v1.include_router(projects.router,   prefix="/projects",  tags=["projects"])
v1.include_router(vendors.router,    prefix="/vendors",   tags=["vendors"])
v1.include_router(bids.router,       prefix="/bids",      tags=["bids"])
v1.include_router(documents.router,  prefix="/documents", tags=["documents"])
v1.include_router(storage.router,    prefix="/storage",   tags=["storage"])
v1.include_router(ingest.router,     prefix="/ingest",    tags=["ingest"])
v1.include_router(search.router,     prefix="/search",    tags=["search"])
v1.include_router(system.router,     prefix="/system",    tags=["system"])
v1.include_router(ai.router,         prefix="/ai",        tags=["ai"])
v1.include_router(workflows.router,  prefix="/workflows", tags=["workflows"])
v1.include_router(memory.router,     prefix="/memory",    tags=["memory"])
v1.include_router(sop.router,                           tags=["sop"])
v1.include_router(platform_router.router,              tags=["platform"])

# ── Construction Intelligence Service Layer ────────────────────────────────
svc = APIRouter(prefix="/services")
svc.include_router(pb_routes,         prefix="/project-brain",         tags=["project-brain"])
svc.include_router(bi_routes,         prefix="/bid-intelligence",      tags=["bid-intelligence"])
svc.include_router(vi_routes,         prefix="/vendor-intelligence",   tags=["vendor-intelligence"])
svc.include_router(proc_routes,       prefix="/procurement",           tags=["procurement"])
svc.include_router(hc_routes,         prefix="/historical-cost",       tags=["historical-cost"])
svc.include_router(ll_routes,         prefix="/lessons-learned",       tags=["lessons-learned"])
svc.include_router(sched_routes,      prefix="/schedule-intelligence", tags=["schedule-intelligence"])
svc.include_router(risk_routes,       prefix="/risk-intelligence",     tags=["risk-intelligence"])
svc.include_router(doc_intel_routes,  prefix="/document-intelligence", tags=["document-intelligence"])
svc.include_router(decision_routes,   prefix="/decision-intelligence", tags=["decision-intelligence"])
svc.include_router(kpi_routes,        prefix="/kpi-intelligence",      tags=["kpi-intelligence"])
svc.include_router(op_rules_routes,   prefix="/operating-rules",       tags=["operating-rules"])
svc.include_router(bpl_routes,        prefix="/business-process-library", tags=["business-process-library"])

@svc.get("")
def list_services():
    return {"services": [
        {"name": "project-brain",          "status": "active",   "path": "/api/v1/services/project-brain"},
        {"name": "bid-intelligence",       "status": "active",   "path": "/api/v1/services/bid-intelligence"},
        {"name": "vendor-intelligence",    "status": "active",   "path": "/api/v1/services/vendor-intelligence"},
        {"name": "document-intelligence",  "status": "active",   "path": "/api/v1/services/document-intelligence"},
        {"name": "lessons-learned",        "status": "active",   "path": "/api/v1/services/lessons-learned"},
        {"name": "procurement",            "status": "active",   "path": "/api/v1/services/procurement"},
        {"name": "historical-cost",        "status": "active",   "path": "/api/v1/services/historical-cost"},
        {"name": "schedule-intelligence",  "status": "active",   "path": "/api/v1/services/schedule-intelligence"},
        {"name": "risk-intelligence",          "status": "active",   "path": "/api/v1/services/risk-intelligence"},
        {"name": "decision-intelligence",      "status": "active",   "path": "/api/v1/services/decision-intelligence"},
        {"name": "kpi-intelligence",           "status": "active",   "path": "/api/v1/services/kpi-intelligence"},
        {"name": "operating-rules",            "status": "active",   "path": "/api/v1/services/operating-rules"},
        {"name": "business-process-library",   "status": "active",   "path": "/api/v1/services/business-process-library"},
    ]}

v1.include_router(svc)
app.include_router(v1)

# ── Dashboard + static files ──────────────────────────────────────────────────
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

@app.get("/dashboard", include_in_schema=False)
def dashboard_redirect():
    return RedirectResponse(url="/static/dashboard/index.html")

# ── Legacy routes (backward compat — launchd scripts + existing integrations) ─

app.include_router(health.router,    tags=["_legacy"])
app.include_router(projects.router,  prefix="/projects",  tags=["_legacy"])
app.include_router(vendors.router,   prefix="/vendors",   tags=["_legacy"])
app.include_router(bids.router,      prefix="/bids",      tags=["_legacy"])
app.include_router(memory.router,    prefix="/memory",    tags=["_legacy"])
app.include_router(workflows.router, prefix="/workflows", tags=["_legacy"])
app.include_router(ingest.router,    prefix="/ingest",    tags=["_legacy"])

logger.info("HCI AI API v%s started — %d route groups + 13 intelligence services + platform integration layer",
            settings.app_version, 14)
