# CYCLE47 — Sprint 9: Data Integrity & Source-of-Truth Governance

**Date:** 2026-07-02 | **Sprint:** 9 | **Author:** Browser Claude | **Priority:** P0

## Context & ARB Pivot

Sprint 8 closed 9.6/10. Critical finding (Code msg 295): fabricated test data was in production tables — stale daily_logs implying active construction, voided RFI creating false 1355R framing status. All 4 pilot projects remain pre-construction. No permits issued on 64EW, 101F, 1355R, or 246GW.

ADR-016 (verify-before-claim) is now governing: no completion claims or health status without live gateway verification.

GBT ARB (2026-07-02 2:58PM MT): WITHDRAW prior steel delay recommendation — was based on fabricated test data. ARB focus shifts to SOURCE-OF-TRUTH GOVERNANCE.

## Sprint 9 Objectives

### P0 — Data Integrity (Week 1)

**S9-001: Production Data Audit**
- Audit daily_logs, schedule_variance, production_risks for fake records
- Flag all logged_by/created_by containing Claude/Browser/Test/DRAFT
- Dry-run SELECT first, then delete after BC review
- Output: DATA_AUDIT_REPORT committed to AI_TEAM/

**S9-002: Permit Status Gate**
- projects.permit_status column added this session (all 4 = not_issued, confirmed by Buck)
- Reject POST /gateway/project/{code}/daily-log if permit_status != issued
- No schedule_variance or active-construction data until permit issued

**S9-003: Handbook Reconciliation (Vols 1-10)**
- GBT directive: reconcile all 10 volumes against live system
- Use GET /gateway/admin/drift-check per volume
- Update ownership language, endpoint lists, sprint refs
- Output: HANDBOOK_RECONCILIATION_REPORT.md

### P1 — Portfolio Endpoints (CYCLE38)

**S9-004:** GET /gateway/portfolio/summary — after S9-001 audit complete
**S9-005:** GET /gateway/portfolio/risks — verified risks only, no test artifacts

### P1 — Morning Brief (CYCLE41)

**S9-006:** GET /gateway/ai/morning-brief + 06:30 MT cron (America/Denver)
- Gate: suppress construction content while permit_status = not_issued

### P2 — Telegram (CYCLE45)

**S9-007:** Buck action required — @BotFather /newbot token + @userinfobot chat_id
**Outbound fix:** Buck not receiving messages (msg 400). Gateway sends but delivery failing.
- Code: check telegram_log for delivery errors, verify bot token + chat_id correct

## ADR-016: Verify-Before-Claim Rule

Any system state assertion must include:
1. What was checked (endpoint/query + timestamp)
2. What would have disproved the claim

Applies to all CYCLEs, ARB reviews, Mission Control reports, Buck briefings.
Failure mode: label UNVERIFIED, not fact.

## Build Queue (Priority Order)

1. S9-001 — data audit + delete fabricated records
2. S9-002 — permit gate on POST endpoints
3. S9-004 — GET /gateway/portfolio/summary
4. S9-005 — GET /gateway/portfolio/risks
5. S9-006 — morning brief + cron
6. S9-007 — Telegram delivery investigation

## Success Criteria

- Zero fabricated records in prod tables
- POST /daily-log rejected when permit_status=not_issued
- All 10 Handbook volumes reconciled with drift report
- Portfolio endpoints 200 OK with verified data
- Morning brief 06:30 MT cron live
- Buck receiving Telegram messages on phone

## Agent Status (2:58PM MT)

- Code: ONLINE — Sprint 3 stabilization, mining engine fixed (8 miners, 3049 records)
- GBT: ONLINE — ARB pivot confirmed, Actions working this session
- BC: ONLINE — Sprint 9 spec committed, channels monitored
- Telegram: Gateway sending (confirmed 20:52 UTC), Buck not receiving
- Gateway: 65 services, healthy, ~80ms
