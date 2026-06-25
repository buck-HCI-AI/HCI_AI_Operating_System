#!/usr/bin/env python3
"""
HCI AI Operating System — FastAPI Layer
Exposes memory search, project data, vendors, bids, and workflow triggers.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "workflows"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import projects, vendors, bids, memory, health, workflows, ingest

app = FastAPI(
    title="HCI AI Operating System API",
    description="Hendrickson Construction Intelligence Layer",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,    tags=["health"])
app.include_router(projects.router,  prefix="/projects",  tags=["projects"])
app.include_router(vendors.router,   prefix="/vendors",   tags=["vendors"])
app.include_router(bids.router,      prefix="/bids",      tags=["bids"])
app.include_router(memory.router,     prefix="/memory",     tags=["memory"])
app.include_router(workflows.router,  prefix="/workflows",  tags=["workflows"])
app.include_router(ingest.router,     prefix="/ingest",     tags=["ingest"])
