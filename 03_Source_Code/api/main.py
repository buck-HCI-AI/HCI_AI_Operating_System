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
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from middleware.logging import RequestLoggingMiddleware
from middleware.auth import ApiKeyMiddleware

from routers import projects, vendors, bids, memory, health, workflows, ingest
from routers import auth, documents, storage, search, system, ai

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

app.include_router(v1)

# ── Legacy routes (backward compat — launchd scripts + existing integrations) ─

app.include_router(health.router,    tags=["_legacy"])
app.include_router(projects.router,  prefix="/projects",  tags=["_legacy"])
app.include_router(vendors.router,   prefix="/vendors",   tags=["_legacy"])
app.include_router(bids.router,      prefix="/bids",      tags=["_legacy"])
app.include_router(memory.router,    prefix="/memory",    tags=["_legacy"])
app.include_router(workflows.router, prefix="/workflows", tags=["_legacy"])
app.include_router(ingest.router,    prefix="/ingest",    tags=["_legacy"])

logger.info("HCI AI API v%s started — %d route groups registered",
            settings.app_version, 13)
