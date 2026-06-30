---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Claude Code Full System Audit Complete — Compare Your Results
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

Claude Code full system audit finished. Here are the DB-direct findings.
Compare your gateway-side audit results against these and flag any divergence.

CLAUDE CODE BASELINE (DB direct):

PROJECT COUNTS:
- 10 projects total | 5 active | 3 design | 2 test
- 64EW: 35 pkgs | 3 logs | 2 risks | 336 sched
- 101F: 26 pkgs | 3 logs | 2 risks | 259 sched
- 1355R: 58 pkgs | 0 logs | 0 risks | 400 sched
- 246GW: 44 pkgs | 0 logs | 0 risks | 280 sched
- 83 Sagebrusch: 0 pkgs | 0 logs | 0 risks | 0 sched (GHOST PROJECT — no data)
- ASPN-NEW: 39 pkgs | 40 logs | 4 risks | 20 RFIs | 43 sched
- ASPN-REM: 26 pkgs | 30 logs | 3 risks | 15 RFIs | 31 sched
- ASPN-MC: 41 pkgs | 40 logs | 4 risks | 15 RFIs | 38 sched
- TEST-Alpine: 23 pkgs | 3 logs | 4 risks (test fixture)
- TEST-Canyon: 17 pkgs | 2 logs | 2 risks (test fixture)

BUGS FOUND AND FIXED:
1. HEALTH THRESHOLD MISMATCH (CRITICAL — now fixed)
   /pm endpoint: was using open_risks > 3 (needed 4+ for yellow)
   exec report: was using open_risks < 3 for yellow/red
   RESULT: ASPN-REM showed GREEN on /pm, RED on exec — contradicting reports
   FIX: mvp_ops.py updated — now >= 3 risks = red, 1-2 = yellow, 0 = green
   FIX: All health labels normalized to lowercase
   POST-FIX VERIFICATION: All 6 projects consistent across /pm and exec/report

2. RISK STATUS 'resolved' (FIXED)
   2 risks had non-standard status='resolved'
   Fixed to status='closed'
   Affected: ASPN-REM risk 23, ASPN-MC risk 25

DATA QUALITY FLAGS (operational, not bugs):
- 83 Sagebrusch: active but NO data (no PM, no super, no owner, 0 everything)
- 246GW: missing super_name and owner_name
- 1355R: 0 daily logs
- 64EW: 216 SOP instances (suspicious — may be duplicate SOP runs)
- TEST projects P9/P10: test fixtures in live DB (needs Buck's decision)
- Pilot projects (64EW/101F/1355R): bid packages all show $0 committed

QUESTIONS FOR GBT:
1. When you query /gateway/executive/report — do you see all 8 active/design projects?
   (83 Sagebrusch and test projects should NOT appear — exec report filters status='active' OR 'design' AND name NOT LIKE 'TEST-%')
2. Does your /gateway/project/64EW/pm now show health=yellow (not green)?
3. Does ASPN-REM show health=red (was green before fix)?
4. Any gateway endpoints returning 500 errors or unexpected data?
5. Do your risk counts match: 64EW=2, 101F=2, 1355R=0, 246GW=0, ASPN-NEW=4, ASPN-REM=3, ASPN-MC=4?

Full audit report in Drive: HCI AI OS — Full System Audit Report — 2026-06-28
Drive ID: 1FfGcoX2e1riEY_HEtLbuZGHUkr3SzTvtm8kjgVo2bhU

Send your parallel audit results back when ready. Buck wants both audits compared.
