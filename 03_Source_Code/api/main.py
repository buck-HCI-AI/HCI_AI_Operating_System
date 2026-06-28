#!/usr/bin/env python3
"""
HCI AI Operating System — FastAPI Layer v1
Single integration point for all applications, automations, and AI agents.

Versioned API:  /api/v1/*
Legacy routes:  /projects, /vendors, /bids, /memory, /workflows, /ingest (unchanged)
Docs:           http://localhost:8000/docs
"""
import sys, os, logging

# Pre-cache stdlib 'platform' before sys.path gains services/platform/ — prevents
# onnxruntime's `import platform` from resolving to our services/platform package.
import platform as _stdlib_platform  # noqa: F401 — side effect: caches in sys.modules

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "workflows"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "services"))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, PlainTextResponse

from config import settings
from middleware.logging import RequestLoggingMiddleware
from middleware.auth import ApiKeyMiddleware

from routers import projects, vendors, bids, memory, health, workflows, ingest
from routers import auth, documents, storage, search, system, ai
from routers import sop
from routers import platform as platform_router
from routers import mvp_ops
from routers import executive as exec_router
from routers import operations as ops_router

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
bl_routes            = _load_svc("background_learning")
aq_routes            = _load_svc("approval_queue")
cr_routes            = _load_svc("connector_registry")
bid_lev_routes       = _load_svc("bid_leveling")
houzz_routes         = _load_svc("houzz_intelligence")
notify_routes        = _load_svc("notification_engine")
connector_routes     = _load_svc("connectors")
autonomy_routes      = _load_svc("autonomy")
cross_project_routes    = _load_svc("cross_project")
predictive_routes       = _load_svc("predictive_engine")
auditor_routes          = _load_svc("system_auditor")
arch_sync_routes        = _load_svc("architecture_sync")
kg_routes               = _load_svc("knowledge_graph")
cd_routes               = _load_svc("continuous_discovery")
drive_routes            = _load_svc("drive_intelligence")

from routers.mining import router as mining_router

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
v1.include_router(houzz_routes,       prefix="/imports/houzz",  tags=["houzz-imports"])
v1.include_router(mvp_ops.router,                           tags=["mvp-operations"])
v1.include_router(exec_router.router, prefix="/executive",   tags=["executive"])
v1.include_router(ops_router.router,                          tags=["operations"])

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
svc.include_router(bl_routes,         prefix="/background-learning",      tags=["background-learning"])
svc.include_router(aq_routes,         prefix="/approval-queue",           tags=["approval-queue"])
svc.include_router(cr_routes,         prefix="/connector-registry",       tags=["connector-registry"])
svc.include_router(bid_lev_routes,    prefix="/bid-leveling",             tags=["bid-leveling"])
svc.include_router(houzz_routes,      prefix="/houzz",                    tags=["houzz-intelligence"])
svc.include_router(notify_routes,     prefix="/notifications",             tags=["notifications"])
svc.include_router(connector_routes,  prefix="/connectors",                tags=["connectors"])
svc.include_router(autonomy_routes,      prefix="/autonomy",                  tags=["autonomy"])
svc.include_router(cross_project_routes, prefix="/cross-project",              tags=["cross-project-intelligence"])
svc.include_router(predictive_routes,   prefix="/predictive-engine",           tags=["predictive-engine"])
svc.include_router(auditor_routes,      prefix="/system-auditor",              tags=["system-auditor"])
svc.include_router(arch_sync_routes,    prefix="/architecture-sync",           tags=["architecture-sync"])
svc.include_router(kg_routes,           prefix="/knowledge-graph",             tags=["knowledge-graph"])
svc.include_router(cd_routes,           prefix="/continuous-discovery",        tags=["continuous-discovery"])
svc.include_router(drive_routes,        prefix="/drive-intelligence",           tags=["drive-intelligence"])
svc.include_router(mining_router,     prefix="",                          tags=["mining"])

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
        {"name": "background-learning",        "status": "active",   "path": "/api/v1/services/background-learning"},
        {"name": "approval-queue",             "status": "active",   "path": "/api/v1/services/approval-queue"},
        {"name": "connector-registry",         "status": "active",   "path": "/api/v1/services/connector-registry"},
        {"name": "bid-leveling",               "status": "active",   "path": "/api/v1/services/bid-leveling"},
        {"name": "houzz-intelligence",         "status": "active",   "path": "/api/v1/services/houzz"},
        {"name": "connectors",                  "status": "active",   "path": "/api/v1/services/connectors"},
        {"name": "notifications",               "status": "active",   "path": "/api/v1/services/notifications"},
        {"name": "knowledge-graph",             "status": "active",   "path": "/api/v1/services/knowledge-graph"},
        {"name": "continuous-discovery",        "status": "active",   "path": "/api/v1/services/continuous-discovery"},
        {"name": "drive-intelligence",          "status": "active",   "path": "/api/v1/services/drive-intelligence"},
    ]}

v1.include_router(svc)
app.include_router(v1)

# ── ACR-002: Public project state endpoint (no auth required) ────────────────
# ChatGPT and any AI can read LIVE_PROJECT_STATE.md without an API key.
_LIVE_STATE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "LIVE_PROJECT_STATE.md")
)

@app.get("/project-state", tags=["architecture"])
def get_project_state(fmt: str = "json"):
    """
    Public read-only endpoint — no API key required.
    Returns LIVE_PROJECT_STATE.md, the single source of truth for HCI AI OS architecture.
    fmt=json (default): JSON wrapper with content field.
    fmt=markdown: raw markdown text.
    """
    try:
        with open(_LIVE_STATE_PATH) as f:
            content = f.read()
        if fmt == "markdown":
            return PlainTextResponse(content, media_type="text/markdown")
        return {
            "status": "ok",
            "source": "LIVE_PROJECT_STATE.md",
            "updated_by": "Claude Code",
            "content": content,
        }
    except FileNotFoundError:
        return {"status": "not_found", "message": "LIVE_PROJECT_STATE.md not found at repo root"}


# ── Dashboard + static files ──────────────────────────────────────────────────
_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

@app.get("/dashboard", include_in_schema=False)
def dashboard_redirect():
    return RedirectResponse(url="/static/dashboard/index.html")

# Executive dashboard HTML at /executive (mobile-first, no auth — internal only)
app.include_router(exec_router.router, prefix="/executive", include_in_schema=False)

# Operations console HTML at /superintendent, /pm, /leadership (mobile-first, no auth)
app.include_router(ops_router.router, include_in_schema=False)

# ── Legacy routes (backward compat — launchd scripts + existing integrations) ─

app.include_router(health.router,    tags=["_legacy"])
app.include_router(projects.router,  prefix="/projects",  tags=["_legacy"])
app.include_router(vendors.router,   prefix="/vendors",   tags=["_legacy"])
app.include_router(bids.router,      prefix="/bids",      tags=["_legacy"])
app.include_router(memory.router,    prefix="/memory",    tags=["_legacy"])
app.include_router(workflows.router, prefix="/workflows", tags=["_legacy"])
app.include_router(ingest.router,    prefix="/ingest",    tags=["_legacy"])

# ── MCP Proxy (forwards /mcp/* to standalone MCP server on port 8080) ────────
# Standalone FastMCP server runs via launchd on 8080 with its own lifecycle.
# This proxy makes it reachable at /mcp via the existing ngrok tunnel on 8000.
import httpx as _httpx
from fastapi import Request as _Req
from fastapi.responses import StreamingResponse as _StreamResp, Response as _Resp

_MCP_BACKEND = "http://127.0.0.1:8080"

@app.api_route("/mcp", methods=["GET","POST","PUT","DELETE","OPTIONS","HEAD","PATCH"],
               include_in_schema=False)
@app.api_route("/mcp/{path:path}", methods=["GET","POST","PUT","DELETE","OPTIONS","HEAD","PATCH"],
               include_in_schema=False)
async def _mcp_proxy(request: _Req, path: str = ""):
    """Transparent proxy — forwards all /mcp/* traffic to MCP server on :8080."""
    target_url = f"{_MCP_BACKEND}/mcp/{path}" if path else f"{_MCP_BACKEND}/mcp"
    if request.url.query:
        target_url += f"?{request.url.query}"
    fwd_headers = {k: v for k, v in request.headers.items()
                   if k.lower() not in ("host", "content-length")}
    body = await request.body()
    try:
        async with _httpx.AsyncClient(timeout=60) as client:
            rsp = await client.request(
                method=request.method,
                url=target_url,
                headers=fwd_headers,
                content=body,
            )
            rsp_headers = {k: v for k, v in rsp.headers.items()
                           if k.lower() not in ("transfer-encoding", "content-encoding")}
            if "text/event-stream" in rsp.headers.get("content-type", ""):
                async def _stream():
                    async for chunk in rsp.aiter_bytes():
                        yield chunk
                return _StreamResp(_stream(), status_code=rsp.status_code,
                                   headers=rsp_headers, media_type="text/event-stream")
            return _Resp(content=rsp.content, status_code=rsp.status_code, headers=rsp_headers)
    except _httpx.ConnectError:
        return _Resp(content=b'{"error":"MCP server offline","hint":"Check launchd com.hci.mcp-server"}',
                     status_code=503, media_type="application/json")

logger.info("MCP proxy mounted at /mcp → port 8080")

logger.info("HCI AI API v%s started — %d route groups + 21 intelligence services + MCP + Phase 2 Intelligence Layer",
            settings.app_version, 15)
