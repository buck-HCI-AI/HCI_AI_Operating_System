# HCI AI Strategic Backlog
*Long-Term Vision — BTW-4 through BTW-10*
*Queued: 2026-06-27 | Source: The long.docx*

---

## Long-Term Discovery Flow Vision

```
Browser Discovery
        ↓
Platform Intelligence Document
        ↓
Automatic Ingest
        ↓
Claude Code indexes it
        ↓
Architecture Handbook updates
        ↓
Implementation backlog updates
        ↓
Executive Dashboard reflects new opportunities
```

This flow becomes the operating model once BTW-10 (Continuous Discovery Engine) is complete.

---

## Backlog Queue

### BTW-4 — Project Brain: Extended Memory
**Mission:** BTW-004 | **Priority:** HIGH | **Status:** OPEN

**Already built (pre-delivered):**
- `services/project_brain` — health, intelligence, risks, snapshot endpoints ✅
- `project_brain_snapshots` table ✅
- Cross-project intelligence aggregation ✅
- PROJECT_BRAIN_SPEC.md ✅

**Remaining to build:**
- Event Timeline — chronological log of project events (milestones, risks, decisions, changes)
- Conversation Memory — AI interaction history per project (what was asked, what was decided)
- Document Relationships — link documents to the decisions/risks/change orders they drove
- Daily Project Summary auto-generation (scheduled, not on-demand)

**Handbook:** Volume III (Project Brain) — implementation refs ready; philosophy pending CA

---

### BTW-5 — Role Intelligence: 8 Roles
**Mission:** BTW-005 | **Priority:** HIGH | **Status:** OPEN

**Already built (pre-delivered):**
- Superintendent Daily Console (`/superintendent/{id}/today`) ✅
- Project Manager Weekly Console (`/pm/{id}/weekly`) ✅
- Leadership Dashboard (`/leadership/dashboard`) ✅
- Executive Morning Brief (`/executive/morning-brief`) ✅

**Remaining 5 roles to define + build:**

| Role | Dashboard | Daily Workflow | Notifications | AI Assist | KPIs |
|------|-----------|----------------|---------------|-----------|------|
| Owner (Buck) | Company-wide command | Morning brief + approvals | All critical alerts | Decision support | Revenue, margin, risk |
| Office | Admin queue | Pending items, AP/AR | Approval requests | Document prep | Turnaround time |
| Accounting | Financial health | Invoices, draws, cash flow | Budget alerts | Cost code tagging | Cash position |
| Client | Project status | Milestone updates | Change order alerts | Q&A | Schedule, budget vs contract |
| Trade Partner | My work queue | Today's scope, RFIs | Inspection holds | Scope clarification | On-time delivery |

**Handbook:** Volume IV (Role Intelligence) — philosophy pending CA for all 5 new roles

---

### BTW-6 — Executive Command Center: Weekly/Monthly Reports
**Mission:** BTW-006 | **Priority:** MEDIUM | **Status:** OPEN

**Already built (pre-delivered):**
- Executive Mission Control — 11 sections ✅
- Morning Brief (daily, 6AM push) ✅
- Leadership Dashboard ✅
- All executive endpoints ✅

**Remaining to build:**
- Weekly Executive Report (n8n workflow `AUTO-WEEKLY-EXEC`) — company performance summary, highlights, decisions made, upcoming decisions
- Monthly Business Review (n8n `AUTO-MONTHLY-REVIEW`) — financials, pipeline, client satisfaction, team performance, AI ROI
- Both delivered via ntfy + stored as reports in the platform

**Handbook:** Volume V (Executive Intelligence) — implementation refs ready; philosophy pending CA

---

### BTW-7 — Superintendent Workspace: Field Enhancements
**Mission:** BTW-007 | **Priority:** MEDIUM | **Status:** OPEN

**Already built (pre-delivered):**
- Today's priorities, schedule, safety topics, crew, tasks, daily log ✅
- All from `houzz_schedule_items`, `houzz_tasks`, `houzz_subcontractors` ✅

**Remaining to build (requires Houzz data flowing):**
- Photo documentation — `houzz_files` by project/date (requires Houzz extraction first)
- Delivery tracking — expected PO deliveries (`houzz_purchase_orders`)
- Inspection scheduling — inspection tasks from schedule items
- Material tracking — purchase order status per trade
- Voice notes — transcription endpoint → daily log injection

**Blocker:** All field enhancements requiring Houzz data depend on Houzz Browser Extraction (15 min × 3 projects).

---

### BTW-8 — PM Workspace: Client Comms + AI Action List
**Mission:** BTW-008 | **Priority:** MEDIUM | **Status:** OPEN

**Already built (pre-delivered):**
- Risks, overdue items, budget health, procurement status, decision queue ✅

**Remaining to build:**
- Client communication queue — outstanding items needing client response, organized by project + urgency
- AI-generated ranked action list — `priority_score = (severity × urgency × financial_impact) / days_remaining`, top 10 actions for the PM's day
- Both additions to existing `/pm/{id}/weekly` response

---

### BTW-9 — Company Knowledge Graph
**Mission:** BTW-009 | **Priority:** HIGH | **Status:** OPEN

**Nothing pre-built** — this is a new capability.

**Foundation available:**
- Qdrant vector search (13 collections) ✅
- `background_learning_records` (406 records) ✅
- All entity tables (projects, contacts, vendors, subcontractors, documents) ✅

**To build:**
```
knowledge_graph service
    ├── Entity nodes: projects, clients, employees, vendors, subs, materials
    ├── Relationship edges: worked_on, supplied_to, installed, inspected, decided
    ├── Semantic search: "similar waterproofing issues" → Qdrant cosine similarity
    └── Natural language queries: "Who installed product X before?" → graph traversal + LLM
```

**Enables queries like:**
- "Show me every project where Vendor X worked"
- "Find similar waterproofing issues across all projects"
- "Who has installed this product before?"
- "What decisions were made on rainy days in 2025?"

**Handbook:** Vol IX (Roadmap) — depends on CA authorship; Vol II — intelligence model philosophy needed

---

### BTW-10 — Continuous Discovery Engine
**Mission:** BTW-010 | **Priority:** HIGH | **Status:** OPEN

**Architecture designed** — the Browser Agent Standard and connector framework define this flow. The continuous discovery piece (automatic triggering) is not yet built.

**To build:**
```
Browser Claude (Research Arm)
    ├── Scheduled scans: Houzz changes (nightly), HubSpot changes (hourly)
    ├── Change detection: compare last-known state vs current
    ├── Platform Intelligence Document: canonical JSON per BTW standard
    └── POST /api/v1/services/connectors/{name}/ingest → auto-ingest
            ↓
Claude Code Indexing
    ├── Architecture Sync Engine: /architecture-sync/review-engine
    ├── Handbook updates: affected volumes flagged
    └── Implementation backlog: new items added to missions table
            ↓
Executive Dashboard
    └── New opportunities surface in Mission Control / Morning Brief
```

**Blockers:**
- Houzz Browser extraction access (manual step required once)
- n8n workflow scheduling for browser triggers
- Change detection logic (delta between extractions)

---

## Implementation Sequence Recommendation

Based on dependencies and pre-built work:

| Order | BTW | Reason |
|-------|-----|--------|
| 1 | BTW-4 | Lowest lift — 3 extensions to existing service; no external deps |
| 2 | BTW-8 | 2 additions to PM console; no external deps |
| 3 | BTW-6 | 2 n8n workflows; no external deps |
| 4 | BTW-7 | Requires Houzz data — blocked until extraction runs |
| 5 | BTW-5 | 5 new role consoles — depends on knowledge of how each role operates (CA authorship Vol I helps) |
| 6 | BTW-9 | Knowledge Graph — large build, depends on data flowing |
| 7 | BTW-10 | Continuous Discovery — depends on all connectors working + BTW-9 |

**Immediate unblocked work (no dependencies):** BTW-4 → BTW-8 → BTW-6

---

*Strategic Backlog maintained by Claude Code. Reviewed by Chief Architect (ChatGPT) + Buck Adams.*


### GBT Gateway Connectivity Confirmed
*Source: ChatGPT | 2026-06-28*

This handoff was sent by Claude Code as a live test of the GBT Gateway Bridge. The gateway is live at https://speculate-armband-retinal.ngrok-free.dev. GBT can call GET /gateway/health with no auth to verify connection, and POST /gateway/agent/handoff with the API key to send Claude Code implementation tasks. All read endpoints require no auth. See AI_TEAM/GBT_GATEWAY_USAGE_GUIDE.md for full reference.


### HANDOFF 2 OF 2 — PILOT REPORTING CONSISTENCY AUDIT
*Source: ChatGPT | 2026-06-28*

Urgent Gate 5 handoff from HCI Chief Architect.

Objective:
Perform an end-to-end consistency audit across all pilot reporting surfaces before Architecture Freeze v1.0.

Scope:
1. Compare LIVE_PROJECT_STATE.md, Executive Gateway Report, PM reports, Project Brain outputs, and gateway project endpoints.
2. Verify project health, risk counts, schedule variance, bid package counts, ROI metrics, and approval queue totals are internally consistent.
3. Identify stale caches, duplicated data sources, or reporting pipelines causing conflicting values.
4. Ensure every reporting surface documents its source of truth and refresh behavior.
5. Produce a reconciliation matrix listing each field, authoritative source, current value, mismatches, root cause, and corrective action.
6. Recommend any code or data fixes required before July 1 Gate 5 close.
7. Conclude with a recommendation: Ready for Architecture Freeze v1.0, Ready with documented exceptions, or Not Ready.

Deliver a concise audit report wi


### GBT Gateway Test
*Source: ChatGPT | 2026-06-28*

Connectivity verified from GBT side


### HANDOFF 1 OF 2 — WF-009 DATA INTEGRITY AUDIT
*Source: ChatGPT | 2026-06-28*

Urgent Gate 5 handoff from HCI Chief Architect.

Scope: WF-009 Schedule Variance Checks / Schedule Intelligence data integrity audit.

Objective:
Audit WF-009 end-to-end to confirm schedule intelligence is using accurate, current, non-duplicated, project-scoped data before Architecture Freeze v1.0.

Required audit checks:
1. Verify Houzz ingestion records are correctly loaded and mapped by project:
   - 64EW / 64 Eastwood: expected 336 schedule items per live state
   - 101F / 101 Francis: expected 259 schedule items per live state
   - 1355R / 1355 Riverside: expected 400 schedule items per live state
2. Confirm WF-009 reads from the intended canonical schedule tables or service layer, not stale files or test fixtures.
3. Confirm project code normalization is consistent across all schedule endpoints:
   - 64EW
   - 101F
   - 1355R
   - 83S excluded unless initialized
4. Check for duplicate schedule rows, orphan rows, null critical dates, malformed dates, and cross-project contaminatio


### test
*Source: ChatGPT | 2026-06-28*

test


### Implement HCI Mobile Command Center with ntfy Notifications
*Source: ChatGPT | 2026-06-28*

Objective: Design and implement mobile approval notifications using ntfy integrated with the existing HCI approval architecture.

Requirements:
1. Integrate ntfy (self-hosted or ntfy.sh configurable) into the notification layer.
2. Use n8n to publish notifications whenever high-priority approval queue items are created.
3. Notification payload should include project, approval type, amount (if applicable), risk level, recommendation, and deep link.
4. Deep links should open either the HCI approval dashboard or ChatGPT conversation for review before approval.
5. Preserve the existing human-in-the-loop governance model. Notifications must never auto-approve or trigger production writes.
6. Support notification categories (Critical, High, Normal) and quiet hours configuration.
7. Store ntfy configuration in environment variables and document deployment steps.
8. Add audit logging for notification delivery attempts and failures.
9. Produce architecture documentation and implementation notes


### Fix driveWrite view_link
*Source: ChatGPT | 2026-06-28*

return https://drive.google.com/file/d/{file_id}/view instead of null


### Auto Processor Test
*Source: ChatGPT | 2026-06-28*

This file tests the automated handoff processor via POST /gateway/admin/process-inbox.


### Phase 2 — Actionable Mobile Approvals with ntfy
*Source: ChatGPT | 2026-06-28*

Queue this behind the current Gate 5 audit work. Claude Code is busy; this is a high-priority backlog handoff, not an immediate production change unless Buck later authorizes go-live.

Objective:
Design and implement Phase 2 of the HCI Mobile Command Center: secure actionable mobile approvals triggered from ntfy notifications while preserving the existing human-in-the-loop governance model.

Required capabilities:
1. Add secure one-time approval tokens for mobile approval actions.
2. Support Approve / Reject / Request Info actions from mobile deep links.
3. Require explicit human confirmation before any approval action is committed.
4. Add optional biometric confirmation support where the mobile client/browser supports passkeys, Face ID, Touch ID, or platform authenticator flows.
5. Ensure mobile actions route through the existing approval queue service and do not bypass governance.
6. Enforce token expiration, single-use semantics, project/item scoping, and audit logging.
7. Store dec


### Pilot Reporting Audit Overnight
*Source: ChatGPT | 2026-06-28*

OVERNIGHT BUILD. Gate 5 blocker. Audit 64EW/101F/1355R across all reporting surfaces: project-state, executive report, PM reports, gateway endpoints. Produce reconciliation matrix: field/source/value/mismatch/root-cause/fix. Conclude: Ready / Ready with exceptions / Not Ready. Write PILOT_REPORTING_AUDIT.md to Drive. July 1 deadline.


### 246 Gallo Pilot Feasibility Analysis
*Source: ChatGPT | 2026-06-28*

Full audit of 246 Gallo as HCI AI OS pilot: find data in Drive/HubSpot/Houzz, determine project scope, what it takes to onboard (schedule ingestion, project brain, workflows), data gaps, recommended AI support directive across all three platforms, comparison to current pilots. Write findings to 246_GALLO_PILOT_FEASIBILITY.md in Drive.


### Add document_type field to sendHandoffToClaude schema
*Source: ChatGPT | 2026-06-28*

The sendHandoffToClaude gateway endpoint needs a document_type parameter added to the schema so GBT can explicitly classify handoffs as architecture_change_request, audit_request, implementation_task, etc. Currently GBT has to embed this in the body text. Add document_type as an optional enum field to the POST /gateway/agent/handoff endpoint and update the GPT schema accordingly. Priority: normal. This is a schema improvement, not a Gate 5 blocker.


### Architecture Freeze v1.0 Declaration
*Source: ChatGPT | 2026-06-28*

Architecture Freeze v1.0 is declared. The freeze document is live in Drive. All structural changes from this point require an Architecture Change Request (ACR) filed via POST /gateway/agent/handoff with document_type: architecture_change_request. Sprint 3 is ready to start. First unblocked items are: (1) Mobile Command Center (GBT handoff), (2) BP-17 schedule automation, and (3) BP-06 risk auto-filing.


### WF-009 Audit Overnight
*Source: ChatGPT | 2026-06-28*

OVERNIGHT BUILD. Gate 5 blocker. Run WF-009 data integrity: duplicate detection, orphan records, schedule baseline, referential integrity 64EW/101F/1355R, Redis sync, Qdrant sync. Write WF009_AUDIT_REPORT.md to Drive. July 1 deadline.


### Overnight Operational Build Continuation
*Source: ChatGPT | 2026-06-28*

Owner directive: Continue overnight execution toward an operational HCI AI OS. After the queued Gate 5 audits, continue implementation and validation where appropriate. Produce a comprehensive morning package including: (1) workflow execution and test report covering all implemented workflows, (2) system health summary, (3) audit results and remaining blockers, (4) deployment readiness assessment, (5) prioritized next actions for Sprint 3. Continue drafting and expanding the system documentation/book and any additional operational documentation needed to support production readiness. Respect existing governance: no automatic production write actions or approvals; maintain audit logging and approval gates; architecture changes require an ACR under the declared freeze.


### PARALLEL WORK DIRECTIVE — HCI AI OS Operations Book
*Source: ChatGPT | 2026-06-28*

Parallel work directive from the owner: Continue developing the HCI AI OS Operations Book alongside implementation work. Expand it into a production-ready operations manual covering system architecture, governance, workflows, SOPs, deployment, monitoring, approval gates, disaster recovery, troubleshooting, onboarding, AI team roles, change management, security, testing, release process, and operational playbooks. Keep it synchronized with the implemented system, organize it for publication and internal operations, and include a morning progress summary identifying completed chapters, remaining gaps, and recommended next sections. This documentation effort runs in parallel with implementation work and respects the Architecture Freeze governance.


### ntfy Mobile Approval System Build
*Source: ChatGPT | 2026-06-28*

Build ntfy.sh mobile approval system for HCI AI OS. n8n monitors approval queue, POSTs to ntfy topic hci-approvals. Each notification: title, priority, deep link to ChatGPT review. One-tap Approve/Deny/Request Info. No auto-approvals. Token expiration + replay protection + full audit logging. Sequence: starts after Gate 5 audits complete.


### CYCLE 2 IMPROVEMENTS: Gap-15 Fixed + Procurement Risk Built + System Cleaned
*Source: ChatGPT | 2026-06-28*

# Claude Code: Cycle 2 Improvements — 2026-06-28

## WHAT CHANGED

### 1. GAP-15 FIXED: Health Score Now Includes Bid Coverage

Previously: 64EW showed GREEN despite 94% of packages having zero bids.
Now: Health scoring includes procurement as a first-class signal.

Live project status (real, as of now):
- 64EW: RED — only 6% bid coverage (2/35 packages have bids)
- 101F: RED — only 4% bid coverage (1/26 packages)
- 1355R: YELLOW — 38% bid coverage (23/61 packages)
- 246GW: RED — 0% bid coverage (0/44 packages)

Health logic: <25% coverage + 5+ packages = RED. 25-49% = YELLOW. This is the real state of procurement on these jobs.

### 2. NEW ENDPOINT: Procurement Risk View

GET /gateway/project/{code}/procurement-risk

Buckets every package into: no_bids / single_bid / competitive / awarded.
Returns: risk_score (red/yellow/green), bid_coverage_pct, spread analysis.
MCP tool: GetProcurementRisk(project_code)

1355R result: RED | 38% coverage | 38 packages with no bids, 23 single-bid, 0 c


### SunnySide Full Test Results + Gap Updates
*Source: ChatGPT | 2026-06-28*

Subject: SunnySide Full Test Results + Gap Updates
Priority: Critical
From: Claude via Chief Architect GBT
To: Code

All 4 pilot projects tested. Results saved to Drive (HCI_AI_OS_SunnySide_PhaseA_Test_Results.md).

KEY FINDINGS:
1) GAP 3 CONFIRMED CRITICAL - getProjectState fails for 1355R, inconsistent routing by project code format. Fix immediately.
2) GAP 8 CONFIRMED - Tool slot exhaustion after 3 gateway reads per session. Limit design: 3 calls per GBT session maximum.
3) GAP 9 CONFIRMED SYSTEMIC - No Risk Register on any project.
4) GAP 11 CONFIRMED SYSTEMIC - No RFIs on any project. Universal gap. RFI build is critical path.
5) GAP 12 CONFIRMED SYSTEMIC - No Submittals tracker on any project. Universal gap.
6) GAP 10 ACTIVE - 246GW superintendent still unassigned. Field pilot blocked.
7) GAP 15 NEW - Health scoring logic incorrect. Projects show GREEN despite 90%+ bid packages with no bids. Procurement risk not factored into health score. Fix health scoring algorithm.
8) 1355R h


### CODE-1 through CODE-5 Project Data Corrections
*Source: ChatGPT | 2026-06-28*

Implement the following project data corrections:

CODE-1: 246GW Gateway daily log sync is broken. Houzz contains 6 daily logs but Gateway returns 0. Investigate sync pipeline and restore Gateway ingestion.

CODE-2: Update 64EW owner from Adnan Rawjee to Anthony Greene in the project database.

CODE-3: Update 1355R budget ROM from $75K to $3.541M in the project database.

CODE-4: Add the following 246GW vendors to the vendor registry: Poss Architecture, Premier Landworks, Keller North America, TJ Concrete.

CODE-5: Assign Buck Adams as both Project Manager and Superintendent for 101F in the project table.

Please implement, validate, and report completion with any migration or data integrity notes.


### 1355R Bid Import Complete + Real-World Test Readiness — 2026-06-29
*Source: ChatGPT | 2026-06-29*

22 real bid entries imported from Drive. Bid coverage 37.7% → 62%. 5 real risks added (0→5). Health: RED. RFI-001 Axis B beam pocket DUE TOMORROW (June 30). Field test READY. Full detail in Architecture/Agent_Handoff/Inbox/CLAUDE_HANDOFF_2026-06-29_1355R_BidImport.md


### Field Interface — System Prompt + Test Suite
*Source: Claude Code | 2026-06-28*

# GBT Field Interface — Setup + Test Request

Buck wants SS and PM using GBT as the one field contact point before Gate 5 (July 1).
Claude Code has built the backend. GBT needs to run the field test suite and confirm it works.

---

## ARCHITECTURE DECISION: One Contact Point = Hendrickson GPT

Recommend creating a Custom GPT called **"Hendrickson AI"** with:
- The system prompt below
- MCP server connected at: `https://speculate-armband-retinal.ngrok-free.dev/mcp`
- Simple, field-friendly response format

For the pilot, Buck and GBT both test it using the EXISTING GBT session (no separate GPT needed yet).

---

## SYSTEM PROMPT (for Hendrickson AI Custom GPT or GBT session start)

```
You are Hendrickson Construction's AI field assistant.

You help two types of users:
- SUPERINTENDENT (SS): Jim Hendrickson (1355R), field supers on 64EW/101F
- PROJECT MANAGER (PM): Buck Adams (all projects)

PROJECT CODES: 64EW (64 Eastwood), 101F (101 Francis), 1355R (1355 Riverside), 246GW (246 Gallo


### READY: SunnySide Test — All Field Endpoints Built + Tested 2026-06-28
*Source: ChatGPT | 2026-06-28*

# Claude Code -> GBT: SunnySide Directive Acknowledged + System Ready

**Date:** 2026-06-28 14:30 UTC
**From:** Claude Code (Lead Implementation Engineer)
**To:** GBT (Chief Architect)
**Re:** SunnySide_DummyJob_Directive.md — Response + System Status

---

## DIRECTIVE RECEIVED AND EXECUTED

Read your SunnySide directive. All pre-conditions are now met. System is ready for your 14-call test sequence.

---

## FIELD ENDPOINTS — ALL BUILT + TESTED (5/5)

| Endpoint | Path | Status |
|----------|------|--------|
| submitFieldNote | POST /gateway/field/note | LIVE |
| submitRFI (Gap11) | POST /gateway/field/rfi | LIVE |
| submitDailyReport | POST /gateway/field/daily-report | LIVE |
| getOpenItems | GET /gateway/field/open-items?code= | LIVE |
| getDailyLogFormatted | GET /gateway/field/daily-log-formatted?code= | BUILT THIS SESSION |

getDailyLogFormatted was the only missing endpoint from your directive. Built, tested, and confirmed working 2026-06-28 14:20 UTC.

---

## ALL GAPS FROM Y


### Fix GBT session tool call limit — business blocker
*Source: ChatGPT | 2026-06-28*

Priority: CRITICAL — HIGHEST PRIORITY IN SYSTEM.

The current effective limit of approximately 3 gateway tool calls per GBT session makes the system unusable for field operations. Superintendents are expected to check status at least 5 times per day and PMs 10+ times per day. Requiring a new GBT session after only a few interactions is a major adoption risk.

Required implementation:
- Increase supported gateway interactions to a minimum of 15 consecutive tool calls per session.
- Implement server-side session persistence so tool slots do not degrade during normal field use.
- Prioritize this work before Adam and Traff go live.

Business impact: This is a release-blocking UX issue. Without this change, field adoption is at significant risk.


### SYSTEM UPGRADE REPORT 2026-06-28: Deep Mine + Intelligence Build
*Source: ChatGPT | 2026-06-28*

# Claude Code to GBT: Full System Upgrade

## WHAT CHANGED

### Projects: 20 real (was 10), 0 test (deleted TSNB/TSREM)

Live ops (4): 64EW, 101F, 1355R, 246GW
Reference/monitoring (13): 655G, 275SS, 574J, 212CL, 825CL, 675M, 370G, 843CML, 349DD, 1762R, 606SW, 813MS, 83SB
Design/scenario (3): ASPN-NEW, ASPN-REM, ASPN-MC

Buck confirmed: only the 4 live ops are operationally managed. All others = monitoring + learning.

### Data Corrections
64EW owner: Anthony Greene (was Adnan Rawjee)
1355R owner: Tobin and Oakleigh Ryan (was Tahoe Property Trust)
1355R HubSpot deal ID corrected to 321351275221
813MS owner: Ray and Kelly Spitzley

### New Gateway Endpoints (33 services, was 29)
- GET /gateway/knowledge/market-rates: Real Aspen sub pricing from 323 actual bids, 22 CSI divisions
- GET /gateway/knowledge/rom-estimate?sf=X&project_type=Y: ROM calibrated from real HCI projects
- GET /gateway/project/{code}/bid-level: Bid leveling ranked low-to-high per package
- GET /gateway/projects: Full 


### FULL BRAIN REPORT Part1 — ALL Systems Deep Mine 2026-06-28
*Source: ChatGPT | 2026-06-28*

HCI AI OS Full Portfolio Brain Report — Part 1 of 2

Date: 2026-06-28 | From: Claude Code | To: GBT Chief Architect

Full report written to Drive: HCI_AI_OS_FULL_BRAIN_REPORT_2026-06-28_Part1.md

HEADLINE: 18 HCI Shared Drives exist. Only 3 are in the OS. 15 real projects unmapped.

TOP 5 GAPS:
GAP-A: 15 real HCI projects with Shared Drives NOT in OS — CRITICAL
GAP-B: 813 Mcskimming Spitzley — active (Jun 26 activity), zero OS coverage — CRITICAL  
GAP-C: $0 bid amounts on 64EW/101F/1355R — real data in Drive bid tracking sheets — HIGH
GAP-D: 986 HubSpot vendor candidates pending approval — HIGH
GAP-E: Houzz not synced for real pilot projects — HIGH

ACRs NEEDED FROM GBT:
ACR-IMPORT-001: Priority order for onboarding 15 unmapped projects
ACR-IMPORT-002: Vendor approval protocol for 986 pending candidates
ACR-IMPORT-003: Bid amount importer — read Google Sheets, populate bid_entries
ACR-IMPORT-004: Houzz sync scope for pilot projects
ACR-IMPORT-005: Auto-extract answered RFIs to lessons


### CLAUDE_HANDOFF_2026-06-29_1355R_BidImport_and_RealWorldReadiness
*Source: claude_code | 2026-06-29*

**From:** Claude Code
**To:** GBT (Chief Architect)
**Date:** 2026-06-29
**Priority:** HIGH — URGENT RFI DUE TOMORROW

---

## WHAT HAPPENED THIS SESSION

### 1355R Bid Leveling Sheet Imported (Drive → DB)
Read "1355 Riverside - HCI 16 Division Bid Leveling FINAL LEVELED 2026-06-16" from Google Drive.
Imported ALL real bid amounts into the system:

- **22 new bid entries added** — real vendor prices from the leveling audit
- **12 new bid packages created** — Div 9 finishes (missing: NuVision, InStone, Ragged Mtn, Mark Williams), Div 15 HVAC/Plumbing, Div 16 Electrical (3 bidders + Performance)
- **9 new vendors added** — American PHCE, Garcia Welding, Pinnacle Constructors, CR Drywall, NuVision Drywall, InStone LLC, Cabplex, American Electric, Green Point Roofing

**Bid Coverage: 37.7% → 62% (73 packages, 45 with bids)**

### Daily Logs Committed
3 real daily logs approved and committed to DB:
- 2026-06-26: Concrete pour north wall, pump truck delay 2hr
- 2026-06-27: Framing inspection


### CLAUDE_HANDOFF_2026-06-28_Gap9_Gap12_Complete
*Source: claude_code | 2026-06-29*

**From:** Claude Code
**To:** GBT (Chief Architect)
**Date:** 2026-06-28 09:20 UTC
**Re:** Gap9 (Risk Register) + Gap12 (Submittals Tracker) — BUILT + TESTED

---

## GAP9: Risk Register — COMPLETE ✅

3 gateway endpoints + 3 MCP tools now live:

| Endpoint | MCP Tool | Status |
|----------|----------|--------|
| GET /gateway/project/{code}/risks | GetRisks(project_code, status?) | ✅ |
| POST /gateway/risks/create | CreateRisk(project_code, risk_type, description, severity, mitigation) | ✅ |
| PATCH /gateway/risks/{id}/status | UpdateRiskStatus(risk_id, status, notes?) | ✅ |

**Severity values:** low | medium | high | critical
**Status flow:** open → mitigated → closed
**Risk types:** schedule | budget | quality | safety | procurement | weather | subcontractor
**Auto-writes to:** risks table + project_events (risk_flagged)

---

## GAP12: Submittals Tracker — COMPLETE ✅

3 gateway endpoints + 3 MCP tools now live:

| Endpoint | MCP Tool | Status |
|----------|----------|--------|
| GET 
