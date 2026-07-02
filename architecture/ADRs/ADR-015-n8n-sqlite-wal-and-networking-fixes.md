---
id: ADR-015
title: n8n Container Networking + Recurring SQLite Disk I/O Fix
status: accepted
date: 2026-07-02
author: Claude Code (session 2026-07-02)
tags: [n8n, docker, sqlite, infrastructure, audit]
---

## Context

Buck asked for a full audit of the system after the earlier shutdown/merge with GBT
(ChatGPT) and Browser Claude, to confirm nothing broke and everything still follows the
Operations Manual/SOPs. The system auditor (`GET /api/v1/services/system-auditor/run`)
was the starting point; two real, previously-invisible infrastructure bugs surfaced
during the audit.

## Decision 1 — n8n container networking

`docker exec n8n sh -c "wget http://localhost:8000/..."` returned "connection refused,"
while `wget http://host.docker.internal:8000/...` succeeded. `localhost` inside a Docker
container refers to the container itself, not the host — the API server runs directly
on macOS (via `launchd`/`uvicorn`), not inside a container, so no n8n workflow calling
`http://localhost:8000/...` could ever reach it. A scan of all 55 active workflows found
41 referencing `localhost:8000`, including the financial/HubSpot/client-comms approval
gates — 100% silent failure on every run, invisible unless someone checked n8n's
execution history directly.

Fixed by bulk-updating all 41 workflows (via `PUT /api/v1/workflows/{id}`) to use
`host.docker.internal:8000` instead. Verified live: the 30-min health-check workflow
(previously erroring on every run) succeeded on its next scheduled fire.

## Decision 2 — recurring SQLITE_IOERR

n8n's execution database (SQLite) has thrown `SQLITE_IOERR: disk I/O error` repeatedly
across sessions; the standing fix so far had been `docker restart n8n`, which clears the
symptom but recurred again within roughly an hour in this same session. Root cause:
`~/.n8n` is mounted as a host bind mount (`docker-compose.yml`), not a native Docker
volume — SQLite's file-locking (`fcntl`) is documented to be unreliable across Docker
Desktop's bind-mount filesystem layer on macOS (gRPC-FUSE/VirtioFS), especially under
concurrent access.

Added `DB_SQLITE_ENABLE_WAL=true` to the n8n service definition. WAL (write-ahead
logging) mode performs far fewer fsync/lock operations than the default rollback-journal
mode, which is n8n's own documented mitigation for this exact class of issue. Verified
via `docker compose up -d n8n` (container recreate): all 63 workflows and credentials
persisted (the bind mount itself was never the data-loss risk — only the locking
behavior), API auth restored, system auditor back to 94/100 HEALTHY.

## Constraints / Follow-up not done here

- The deeper, more durable fix would be migrating `~/.n8n` from a bind mount to a native
  Docker volume, which fully avoids the cross-boundary locking problem rather than just
  mitigating it. Not done in this session — it requires stopping the container and
  copying data into a new volume, a bigger, riskier change than a session already this
  large should take on unprompted. Flagging for a future session if `SQLITE_IOERR`
  recurs even with WAL enabled.
- One n8n-side HubSpot Private App credential (used only by
  `AUTO-BID-INVITATION-TASKS`) is separately expired and needs Buck's interactive login
  to reconnect — unrelated to the two fixes above, not fixable via API.
