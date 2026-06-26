# BOOK_00 § 00 — Executive Overview

**Company:** Hendrickson Construction, Inc. (HCI) — high-end residential remodels, Aspen CO  
**Owner/Operator:** Buck Adams  
**Mission:** Build the permanent AI operating system that runs HCI's construction operations.

---

## Prime Directives

> Preserve Knowledge. Protect Relationships. Scale Expertise. Improve Decisions. Document Everything. Think In Decades.

## Core Philosophy

> Memory First. Intelligence Second. Automation Third.

The system accumulates institutional knowledge before it automates decisions. Intelligence layers on top of memory. Automation executes on top of intelligence. Nothing is built before its data foundation is stable.

---

## What This System Does

The HCI AI Operating System is a self-hosted, company-owned intelligence layer that:

1. **Captures** every project document, bid, meeting, daily log, email, and field note
2. **Structures** that data into PostgreSQL (facts), Qdrant (meaning), and MinIO (files)
3. **Synthesizes** project intelligence via Claude AI on demand
4. **Automates** daily operations: morning brief, inbox routing, bid analysis, reporting
5. **Protects** HCI's institutional knowledge permanently — it never leaves the company

---

## Active Projects (as of 2026-06-25)

| Project | Address | Scope | Bid Status |
|---------|---------|-------|------------|
| 64 Eastwood | 64 Eastwood Dr., Aspen | Exterior & Site | 2 bids received, 35 packages |
| 101 Francis | 101 W Francis St., Aspen | Full Interior Remodel | Bidding, 58+ packages |
| 1355 Riverside | 1355 Riverside Dr., Aspen | Full Remodel | Bidding, 58 packages |
| 83 Sagebrusch | 83 Sagebrusch Ln., Aspen | TBD | Setup pending |

---

## Current System State (2026-06-25)

**Phases 1-7 Complete.** The infrastructure, data, API, and intelligence service layers are running.

| Layer | State |
|-------|-------|
| PostgreSQL (hci_os) | ✅ Live — 4 projects, 392 vendors, 119 bid packages, 26 bid entries |
| Redis | ✅ Live |
| MinIO | ✅ Live — 5 buckets |
| Qdrant | ✅ Live — 8 collections, 3,108 vectors |
| FastAPI `/api/v1` | ✅ Live — port 8000, launchd-managed |
| 9 Intelligence Services | ✅ 8 active, 1 partial (schedule) |
| Morning Brief | ✅ Live — daily 7 AM |
| Inbox Review | ✅ Live — daily after brief |
| WF-007 Bid Leveling | ✅ Live — n8n, daily 5 PM |

**Next:** Phase 8 (Workflow Engine core) then Phase 9 (PM, Superintendent, and field workflows).

---

## Technology Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| API | FastAPI (Python) | Fast, async, self-documenting |
| Database | PostgreSQL 16 | ACID, relational, construction data is structured |
| Vector store | Qdrant | Self-hosted, semantic search |
| Cache | Redis 7 | Session state, response caching |
| Object storage | MinIO | Self-hosted S3-compatible |
| AI synthesis | Claude Haiku (Anthropic) | Fast, cheap, construction-aware |
| CRM | HubSpot | Already live with vendor/deal history |
| Drive | Google Drive | Project document source of truth |
| Email | Microsoft 365 / Outlook | HCI communication platform |
| Automation | n8n (Docker) | Visual workflow, self-hosted |
| Dev drive | WD My Passport SSD (HCI_AI_DEV) | Local Docker volumes, hot-pluggable |
