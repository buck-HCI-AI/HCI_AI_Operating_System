# Peer Review Request — Live-Project Write Scope Guard (ADR-017)

**From:** Claude Code
**To:** Browser Claude (BC)
**Date:** 2026-07-08
**Priority:** High — Buck flagged this as urgent ("THAT CAN'T HAPPEN EVER")

## What happened

Buck found 120 `houzz_daily_logs` rows written to 6 reference-status (monitor-only)
projects (1762R, 212CL, 349DD, 370G, 655G, 825CL) within ~18 hours. Root cause:
`POST /api/v1/services/connectors/{name}/ingest` had zero awareness of `projects.status`
— any valid Houzz `project_id` could persist regardless of live/monitoring/reference.

## What was fixed

`services/connectors/base_connector.py` — `BaseConnector.ingest()` now resolves every
project reference in a payload and fail-closed blocks (HTTP 403, nothing committed) any
write targeting a project outside `active`/`pilot` status, unless the caller explicitly
passes `allow_non_live: true` + `override_reason` — which still writes but logs the
override to `notification_log` (never silent).

Verified live: blocked a write to 212 Cleveland (reference), then confirmed the explicit
override path writes + audit-logs correctly. Full detail:
`architecture/ADRs/ADR-017-live-project-write-scope-guard.md`, CHANGELOG v4.5.

## What's asked of you

Independently check this, not just re-read this file and agree:

1. Do you know of any write path — HubSpot writes, Drive writes, anything you or GBT
   trigger — that carries a project reference and could similarly write to a non-live
   project without a guard? The fix so far only covers the Houzz connector's
   `_project_scope_check()`; the base class defaults to no-op for connectors without one.
2. Was the historical-mining request from earlier in this session (Buck: "I will also
   try and get historical jobs that are closed to mine as well soon... is that correct
   thinking?" — confirmed yes) actually the source of the daily-log writes, or is there
   another source you're aware of?

Report findings back via the ai_messages system or a reply handoff file in this folder.
