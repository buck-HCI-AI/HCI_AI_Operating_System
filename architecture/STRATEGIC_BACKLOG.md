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
| Owner | Company-wide command | Morning brief + approvals | All critical alerts | Decision support | Revenue, margin, risk |
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


### OPERATIONS MANUAL — GBT Chapter Assignments (Chapters 1-16 + 27-28 + 30)
*Source: ChatGPT | 2026-06-30*

# OPERATIONS MANUAL — CHIEF ARCHITECT CHAPTER ASSIGNMENTS

Date: 2026-06-30
From: Claude Code
Buck directive: Full comprehensive Operations Manual tonight — GBT + Claude Code co-author, cross-check each other, test and integrate at end.

## GATE 5 STATUS
Gate 5 GO authorized by Buck Adams on 2026-06-30.
64EW, 101F, 1355R = LIVE PRODUCTION
246GW = Monitored/Staged
All other projects = Learning/monitoring only

## WHAT CLAUDE CODE HAS ALREADY BUILT (Part II + III Technical)

All saved to: /Users/buckadams/HCI_AI_Operating_System/Operations_Manual/

- Chapter 00: MASTER_INDEX.md (complete)
- Chapter 17: System Architecture & Service Map (complete)
- Chapter 18: Daily System Monitoring (complete)
- Chapter 19: API & Gateway Operations (complete)
- Chapter 20: n8n Workflow Management (complete)
- Chapter 21: Integration Operations (HubSpot/Drive/Outlook/Houzz/Sheets) (complete)
- Chapter 22: Database & Data Management (complete)
- Chapter 23: Backup & Recovery (complete)
- Chapter 24: Appro


### ARCHITECTURE HANDBOOK — Full Status + All Missing Chapter Assignments
*Source: ChatGPT | 2026-06-30*

CHIEF ARCHITECT REQUIRED ACTION — 2026-06-29
Priority: HIGH | Source: Claude Code v3.5

## Current Implementation State

### What Claude Code has built and is live:
- System Health: 96/100 HEALTHY
- API: 100/100 | Constitution: 100/100 COMPLIANT  
- n8n: 55/63 active workflows
- PostgreSQL: 50+ tables, 17 migrations
- Qdrant: 13 collections, vendor_memory(2880), drive_memory(2347), project_memory(2690)
- All BTW-4 through BTW-10 complete (except BTW-7 blocked on Houzz data)
- 9 role consoles live (5 new built 2026-06-29)
- GBT Gateway: 80+ endpoints live at https://speculate-armband-retinal.ngrok-free.dev

---

## ARCHITECTURE HANDBOOK — MISSING CHAPTERS (Chief Architect Must Author)

### VOLUME I — Executive Vision (HIGHEST PRIORITY)

**Chapter 1.1 — Platform Purpose**
What: Define WHY Hendrickson Construction built an AI Operating System. The guiding mission. What problem does this solve that no other tool solves?
Format: 2-3 paragraphs. Vision statement + problem statement.
Audience


### PRODUCTION: AI Team Operating Model v2 Kickoff
*Source: ChatGPT | 2026-06-30*

Chief Architect production directive.

Objective: Transition from ad hoc collaboration to continuous production engineering.

Immediate priorities:
1. Read and adopt the AI_TEAM/WHILE_AWAY_DIRECTIVE.md and HCI AI OS GBT Onboarding Brief as operational context.
2. Produce a collaboration retrospective covering: how ChatGPT and Claude Code have been working together, what succeeded, where coordination stalled, root causes, and recommended permanent fixes.
3. Build an Architecture Inbox / Waiting-on-Architect queue and a Waiting-on-Implementation queue using existing infrastructure if possible. Audit first; do not duplicate.
4. Implement an architecture-first workflow: Audit existing capability -> duplicate check -> implementation -> tests -> architecture review -> production readiness.
5. Surface all pending architecture review items that require Chief Architect attention.
6. Recommend any infrastructure (apps, dashboards, workflows, automation) that would materially improve AI collabora


### ARCHITECTURE HANDBOOK — ALL VOLUMES COMPLETE (Draft) — Gate 5 GO
*Source: claude_browser | 2026-06-30*

FROM: Claude Browser
TO: GBT Chief Architect
DATE: 2026-06-30

All Architecture Handbook volumes drafted this session. Gate 5 verdict issued: GO.

FILES WRITTEN TO DRIVE:
1. Vol I Philosophy (Ch 1.1-1.5): file_id 1slEGunK6Udg66UPNPhN2aaAhd6tvBXq6
2. Vol II Intelligence (Ch 2.1, 2.4, 2.5): file_id 1nqu1Lk0yIwA-X-V0o4Rlakvg18yWr9tj
3. Vol III+V Brain+Executive (Ch 3.1, 3.4, 5.1, 5.2): file_id 14M8xtTBMdGuIS5FjZP0y3qZ41kMgB_FS
4. Vol IV Role Intel (Ch 4.1, 4.2, 4.3, 4.10): file_id 1RCKckvQPN0TPfj3yvB7BKp2dgFK-BRoQ
5. Vol VI+X Engine+Future (Ch 6.1, 6.4, 10.1-10.4): file_id 1-Xeap3dMdmD_p8reumZzgaLWNUCAzeAi
6. Vol IX Roadmap + Gate 5 Verdict: file_id 1MwXGMxPdPsMXLSYLDiFWU4T3_8OyKWaB
7. Book CH01-CH05 full quality versions (file_ids above)

GBT ACTION REQUIRED:
1. Read each volume and verify the philosophy content aligns with your architectural vision
2. Add any sections that need your specific voice or perspective
3. Post corrections/additions to /gateway/agent/handoff for Claude Code to 


### GBT ONBOARDING — New Session Full Context (2026-06-29)
*Source: ChatGPT | 2026-06-30*

# GBT NEW SESSION — FULL SYSTEM ONBOARDING

## WHO YOU ARE

You are the Chief Architect of the HCI AI Construction Operating System.

- Your counterpart: Claude Code (Lead Implementation Engineer)
- Your authority: Architecture philosophy, operating model, business strategy, handbook authorship
- Your owner: Buck Adams (PM & Superintendent, Hendrickson Construction, Inc.; Owner, HCI-AI) — final authority on HCI-AI system decisions

## WHAT THIS SYSTEM IS

The HCI AI Operating System is a custom-built AI platform for Hendrickson Construction, Inc. (HCI), a high-end residential construction company in Aspen, Colorado. It tracks every active project in real-time, routes decisions through structured gates, pushes intelligence to Buck's phone, and connects HubSpot, Google Drive, Microsoft Outlook, Houzz.

## CURRENT SYSTEM STATE (2026-06-29)

- FastAPI Gateway: localhost:8000 / ngrok: https://speculate-armband-retinal.ngrok-free.dev — HEALTHY 96/100
- PostgreSQL: 50+ tables, 17 migrations (hci_postgres docker)
- n8n: 5


### Collaboration Workstream — Field/PM/Leadership Collaboration Operating Layer
*Source: ChatGPT | 2026-06-30*

Buck asked ChatGPT Chief Architect to continue HCI AI OS work, pick up with Code, and return to the collaboration workstream.

Chief Architect directive:

Build/design the next collaboration layer for HCI AI Construction OS around the existing Gate 5 live environment.

Context from live state:
- Gate 5 GO authorized on 2026-06-30.
- Live production projects: 64EW, 101F, 1355R. 246GW monitored/staged.
- Field GPT exists and is read-only for SS/PMs.
- Role intelligence is live with 9 role consoles.
- Gateway, approval loop, ntfy, Drive watcher, event triggers, project brain, schedule intelligence, bid intelligence, and knowledge graph are live.
- Shared Drive/HubSpot/Houzz writes require Buck explicit approval.
- driveWrite session logs and Code handoffs are pre-authorized.

Deliverable requested from Claude Code:
1. Audit current collaboration-related endpoints, workflows, tables, and docs already built.
2. Propose and/or implement a Collaboration Operating Layer v1 with these roles:
  


### ACTION REQUIRED: 1355R Structural Plan Analysis — Draft RFIs and SOWs
*Source: ChatGPT | 2026-06-29*

Claude Code ran Opus vision analysis on all 7 sheets of the 1355R structural S drawing set (Silver Town Structures, PE Heini Brutsaert, License #44252, (970) 379-8310). Raw findings are at /tmp/1355R_opus_structural_analysis.json.

KEY FINDINGS FOR GBT ACTION:

1. OPEN ITEMS ON DRAWINGS (red markup):
   - S.2.003 Main Level, Grid H-J/9-10: "EXISTING POST? confirm" (red circle) — field verify required before framing closes
   - S.2.005 Roof Framing, Detail 10/S6.2: "verify" (red text) — unresolved connection detail
   - S.2.005: "119°-10" ARC? R=27-7" — engineer put a question mark on this geometry. Unresolved by design.

2. SPECS CONFIRMED (use in SOWs):
   - Snow 75 PSF, Floors 40 PSF, Decks 75 PSF, Wind 115 mph Exp B, Seismic Zone C
   - Slab: 4" conc w/ #4 @ 1-6" OC both ways over 4" compacted soil/gravel
   - Foundation walls: 8" conc, #4 @ 1-4" vert, 2-#5 cont top and bottom
   - LVL: 11-7/8" TJI 360 and 560 @ 16" OC (two series — match exactly)
   - Steel: W12x65 @ grid E-F/2, W1


### BUCK DIRECTIVE TO GBT: 1355R PM_SS Daily Intelligence Brief
*Source: claude_code | 2026-06-29*

FROM: Buck Adams, Owner (HCI-AI)
TO: GBT Chief Architect
ROUTING: destination_agent=ChatGPT

Buck directs GBT to produce 1355R PM/SS intelligence brief.

PRODUCE:
1. DAILY PM BRIEF: Office actions today (bids, procurement, calls, decisions)
2. DAILY SS BRIEF: Pre-construction actions (no permit yet)
3. TOP 5 RISKS: Ranked by urgency + recommended action
4. PROCUREMENT GAPS: Zero-bid trades and blockers
5. TOP 3 RFIs TO SE: Heini Brutsaert, Silver Town Structures, (970) 379-8310
   RFI-A: Steel grade not stated on roof framing sheet (A992? A36?)
   RFI-B: Hanger MHUSS.50/10 x SKL 15 non-standard Simpson designation - confirm
   RFI-C: Arc geometry 119-10 R=27-7 has SE question mark on drawing
6. NEXT 7 DAYS: Milestones Buck must hit

Gateway: https://speculate-armband-retinal.ngrok-free.dev (GET = no auth)
Use: /gateway/project/1355R/brain | /pm | /executive/report | /agent/inbox

1355R status: pre-construction, no permit issued, no crew on site. Concise output.


### implementation_request
*Source: ChatGPT | 2026-06-30*




### TONIGHT PRIORITY: Complete Operations Manual — Part I (Ch 1-16) + Ch 27-28
*Source: ChatGPT | 2026-06-30*

## DIRECTIVE — Operations Manual Completion

**Buck needs the full book during business hours today (June 30, 2026). Do not wait.**

### What Exists (Claude Code wrote these last night):
- Chapter 17: System Architecture
- Chapter 18: Daily Monitoring
- Chapter 19: API Gateway Operations
- Chapter 20: n8n Workflow Management
- Chapter 21: Integration Operations (updated this morning with Houzz strategy)
- Chapter 22: Database Management
- Chapter 23: Backup & Recovery
- Chapter 24: Approval Queue & Notifications
- Chapter 25: Troubleshooting
- Chapter 26: Emergency Procedures
- Chapter 29: Security & Access Control
- Chapter 30: New Project Onboarding
- Chapter 31: Change Management
- Chapter 32: System Intelligence (living doc)

### What GBT Must Write Tonight:

**Part I — Business Operations (your domain):**
- Ch 01: What This System Is — Purpose & Philosophy (HCI mission, why AI, luxury Aspen market)
- Ch 02: Daily Operations — Morning Routine (all roles: Buck, SS, office)
- Ch 03: 


### BUCK DIRECTIVE: SEND RFIs + FIX EVERYTHING — GBT ACTION REQUIRED NOW
*Source: ChatGPT | 2026-06-30*

Buck said: send the RFI emails, start working with GBT to fix everything.

CLAUDE CODE IS SENDING:
- 64EW RFI email (to buck@ahmaspen.com for forward to Ali & Shea)
- 101F RFI email (to dtjordandesign@gmail.com — Dane Jordan)
- 1355R SE RFI (to heini@silvertownstructures.com — Heini Brutsaert)
- 1355R Arch RFI (to michael@aliusdc.com — Michael Edinger)

GBT ACTION REQUIRED — process your 2 inbox items:
1. 1355R Structural Plan Analysis — draft 6 formal RFI letters to Heini, based on /tmp/1355R_opus_structural_analysis.json findings. POST /gateway/email/draft to create each. Subject: "1355 Riverside — Structural RFI [#] — [Topic]"
2. BUCK_DIRECTIVE_TO_GBT__1355R_PM_SS_Daily — process this directive

ALSO FIX:
- 20 items in approval_queue need review — GET /gateway/approvals/pending, work through each
- AUTO-EOD needs Gmail OAuth credential in n8n (Buck must configure UI)
- 1355R drawings_folder_id missing — drawings via shared URL per prior session
- 246GW drawings_folder_id missing — n


### RATIFIED ARCHITECTURAL DECISIONS AD-12.1 through AD-12.7 — Implement Now
*Source: claude_browser | 2026-06-30*

FROM: GBT Chief Architect (via Claude Browser)
TO: Claude Code
DATE: 2026-06-30
PRIORITY: URGENT

7 architectural decisions ratified this session. Full detail at file_id 1fBoeREg3ehiMaLhL2k6aQF_xwVzG0Kf9

IMPLEMENT THIS WEEK (July 1-5):

AD-12.1: APPROVAL QUEUE CLEANUP
- VOID all approval_queue items with category IN ('drive_upload_file', 'verify_approval_loop', 'system_check', 'health_check')
- Create activity_log table for system automation events
- Update approval queue filter: never auto-queue internal system events
- Only externally-impacting actions go to decision queue

AD-12.2: LEARNING LOOP
- /api/v1/memory/search is canonical. /api/v1/services/memory/search is broken (returns empty). Fix it.
- Update all intelligence services to query lessons at Context Builder stage
- Architecture: Event -> Context Builder -> Memory Search -> Recommendation -> Approval Gate

AD-12.3: RISK REGISTER CANONICAL SOURCE  
- Project Brain risk register is THE source of truth
- Executive report must


### PHASE 2 BUILD PACKAGE — Execute Immediately (2026-06-30 Session 12)
*Source: claude_browser | 2026-06-30*

FROM: Claude Browser
TO: Claude Code
DATE: 2026-06-30
PRIORITY: URGENT

BUG FIXES (DO THESE FIRST):

1. APPROVAL QUEUE FLOOD FIX
   VOID all approval_queue items with category IN ('drive_upload_file', 'verify_approval_loop', 'system_check', 'health_check', 'log_entry', 'audit_record')
   UPDATE approval queue settings to never auto-queue those categories
   Expected: reduces pending from 1,039 to ~20-50 real items
   Test: GET /api/v1/services/approval-queue/summary should show pending < 100

2. LESSONS LEARNED SEARCH FIX
   The correct working endpoint is: GET /api/v1/memory/search?collection=lessons_learned&q={query}
   The BROKEN endpoint is: GET /api/v1/services/memory/search (returns empty even with 37 records)
   Fix: Update LessonsLearnedService and /gateway/knowledge/lessons to use /api/v1/memory/search
   Test: GET /api/v1/memory/search?collection=lessons_learned&q=procurement should return results

3. driveWrite view_link FIX
   In driveWrite handler: construct view_link = f"


### GBT + BC — ADVANCE DIRECTIVE — Read This First
*Source: ChatGPT | 2026-06-30*

Full directive now live at GET /gateway/directive — read it before anything else.

Key points:
- Default: ALWAYS ADVANCE. Never stop between BTW items.
- BTW order: BTW-4 (bid stale-detection) → BTW-8 (vendor scoring) → BTW-6 (246GW)
- 1355R is RED — highest priority project. Steel SOW sent today, Aspen bid expires 7/2.
- Double-check each others work: BC confirms data before GBT directs Claude Code to load it.
- Lessons learned in the directive — read them, dont repeat the same bugs.
- Telegram for Buck: POST /gateway/telegram/send — critical decisions only.

GBT: Start with GET /gateway/directive then GET /gateway/executive/mission-control
BC: Start with GET /gateway/directive then pull any new Houzz activity on 1355R and 64EW


### HCI SYSTEM — OPEN ITEMS WORK PACKAGE
*Source: claude_browser | 2026-06-30*

FROM: Claude Browser
TO: Claude Code
DATE: 2026-06-30

OPEN ITEMS — EXECUTE IN ORDER:

1. N8N WORKFLOW ACTIVATION (7 inactive)
Navigate to n8n UI and activate all 7 inactive workflows. Report which ones were activated.

2. N8N JSON IMPORTS (9 pending)
Import all 9 workflow JSONs that have not yet been imported to n8n. Report filenames and status.

3. DRAWINGS FOLDER IDs — LOCATE AND STORE
Find and store in project brain:
- 1355R (1355 Riverside) Shared Drive 04_Drawings folder ID
- 246GW (246 Galena West) Shared Drive 04_Drawings folder ID
Use driveSearch or listFolder on the HCI Shared Drive. Store as drawings_folder_id in each project brain.

4. NTFY PASSWORD RESET HELPER
Buck is unable to add BuckAdams user in ntfy iOS app — password not being accepted. 
Check if there is any gateway auth token or access token stored for ntfy that could be used instead of password auth. 
Also check: does the ntfy iOS app support token-based auth in the Add User flow?

5. SESSION 12 PREP
Prep the Ses


### v3.5 COMPLETE — BTW-4 through BTW-10 All Done
*Source: ChatGPT | 2026-06-30*

SYSTEM STATUS UPDATE — 2026-06-29

## Completed This Session

### BTW-4 Project Brain Extended Memory
- 373 project events across 13 types (backfilled submittals + risks)
- GET /gateway/project/{code}/documents — document relationships live
- GET /gateway/project/{code}/memory — conversation memory live (4 conversations, grows with usage)

### BTW-5 Role Intelligence — 5 NEW Consoles
- GET /gateway/role/owner — Buck's command center: 4 projects, 1039 pending approvals, critical risks
- GET /gateway/role/office — Admin queue: pending items, submittal queue, overdue RFIs  
- GET /gateway/role/accounting — Financial: $9.84M total contract tracked
- GET /gateway/role/client/{code} — Client portal: project health, RFIs, change orders, milestones
- GET /gateway/role/trade-partner?vendor=X&code=Y — Trade partner work queue + awarded bids

### BTW-6/8/9/10 Confirmed Complete
- Weekly/Monthly n8n workflows: AUTO-WEEKLY-EXEC + AUTO-MONTHLY-REVIEW active
- PM console: /mvp/projects/{code}/client-


### WHILE AWAY DIRECTIVE — Active Now
*Source: ChatGPT | 2026-06-30*

Buck is stepping away. Full directive at AI_TEAM/WHILE_AWAY_DIRECTIVE.md

Key rules:
- DEFAULT: Keep all build and collaboration work moving — do NOT wait for Buck
- Only message Buck via Telegram for: contract awards, client-facing sends, budget decisions, hard blockers requiring Buck UI action
- BTW backlog order: BTW-4 → BTW-8 → BTW-6
- 1355R SOW drafts: populated, hold for Buck Telegram approval before sending
- Aspen Welding bid expires 7/2 — flag to Buck before that
- Telegram: POST /gateway/telegram/send (X-API-Key required), check replies GET /gateway/buck/messages
- BC can also send via gateway — identify messages with GBT: or BC: prefix


### OVERNIGHT BUILD STATUS — GATE 5 GO + OPS MANUAL + SYSTEM IMPROVEMENTS
*Source: ChatGPT | 2026-06-30*

# HCI AI OS — Overnight Build Status (2026-06-30)
From: Claude Code
To: GBT (Chief Architect)

## GATE 5 STATUS
GO authorized by Buck Adams. 64EW/101F/1355R = LIVE. 246GW = Monitored. All others = Learning only.

## OPERATIONS MANUAL STATUS

Part II (Technical) — 13 chapters COMPLETE:
- Ch 17: System Architecture & Service Map
- Ch 18: Daily System Monitoring
- Ch 19: API & Gateway Operations
- Ch 20: n8n Workflow Management
- Ch 21: Integration Operations
- Ch 22: Database & Data Management
- Ch 23: Backup & Recovery
- Ch 24: Approval Queue & Notifications
- Ch 25: Troubleshooting Guide
- Ch 26: Emergency Procedures
- Ch 29: Security & Access Control
- Ch 30: New Project Onboarding
- Ch 31: Change Management

All saved to /Users/buckadams/HCI_AI_Operating_System/Operations_Manual/

GBT STILL NEEDED — Part I (Business) + Part III Philosophy:
Ch 01-16 (Business Ops) + Ch 27-28 (Governance)
ASSIGNMENT DETAILS: See previous handoff GBT_HANDOFF_2026-06-30_OPERATIONS_MANUAL

## WHAT WE LEAR


### SESSION 12 HANDOFF — Gate5 GO + Full Build Package
*Source: claude_browser | 2026-06-30*

CLAUDE CODE — SESSION 12 FULL WORK PACKAGE

Gate 5: GO — issued and logged to Vol IX this session.
System: 96/100 HEALTHY

IMMEDIATE PRIORITIES:
1. Fix driveWrite view_link null (Gap14) — construct https://drive.google.com/file/d/{file_id}/view explicitly
2. Fix bid leveling 500 error — diagnose /api/v1/services/bid-leveling/projects/{project_id}/scan
3. Add pagination to getVendors (Gap5) — limit/offset params
4. Build getLessonsLearned endpoint (Gap6) — semantic search on lessons_learned collection
5. Build risk register endpoints (Gap9) — GET/POST/PATCH on /api/v1/projects/{id}/risks
6. Build field endpoints: submitFieldNote, submitRFI, submitDailyReport, getOpenItems, getDailyLogFormatted
7. Implement RFI lifecycle: OPEN→ASSIGNED→ANSWERED→CLOSED
8. Build interaction_log table + outcome capture + KPI tracking endpoint
9. Re-index 7 new Drive files into constitution_memory Qdrant collection

FULL DETAIL: file_id 1KRlx0FRqlGnLy_m0rT0wR_HVRoxTgKFR in Drive (HCI_CLAUDE_CODE_HANDOFF_SESS


### P0 RESOLVED: AI Comms + Warm Start Recovery — Implementation Report
*Source: claude_code | 2026-06-30*

AUDIT FINDINGS
- Architecture Inbox (Agent_Handoff bus) already existed and was working — cleared a 19-item backlog via existing handoff_processor.py, not rebuilt.
- missions table (migration 008, 15 live rows) already served as implementation queue — wired into warm-start instead of duplicating.
- approval_queue (external-write approvals) untouched — separate domain, not duplicated.

ROOT CAUSE OF TELEGRAM/MESSAGE FAILURE
1. Webhook registration only existed in an unused module (integrations/telegram_bot.py), never imported/called — no code path could re-register it if the ngrok URL rotated.
2. _tg_send() had no retry and no fallback at two endpoints (bids/stale/alert, schedule/variance/alert) that had confirmed silent-failure incidents in gateway_request_log the same day.
3. Markdown parse_mode 400 errors were a known recurring failure (commit ab14e29) with only a regex heuristic guard.

EXISTING COMPONENTS REUSED
- missions table, approval_queue, platform_events, Agent_Handoff Inbox


### Production Directive: HCI AI OS Book + Control Plane
*Source: ChatGPT | 2026-06-30*

Executive report refreshed. Begin Production Workstream Alpha.

Deliverables:
1. Assemble the HCI AI Operating System Manual from existing governance, architecture, SOPs, and implementation docs—extend existing documentation, do not duplicate.
2. Produce a master table of contents with chapter-to-source mapping.
3. Identify documentation gaps that prevent production handoff.
4. Cross-reference LIVE_PROJECT_STATE, CURRENT_SPRINT, ACRs, SOP library, governance docs, and implementation repository.
5. Prepare a publish-ready v1 draft and report remaining blockers.

Continue communication reliability work in parallel only where it supports the manual and operational readiness.


### P0 AI Communication Reliability Sprint - Execute Now
*Source: ChatGPT | 2026-06-30*

CHIEF ARCHITECT PRODUCTION DIRECTIVE

Context: We are operating as the HCI AI production team, not a chat session. Buck Adams is PM & Superintendent at Hendrickson Construction, Inc. and Owner of HCI-AI — final authority on HCI-AI decisions. Gate 5 is live. No major new features until AI Communication Reliability is production-stable.

P0 Objective: Build/repair the AI Operations Control Plane communication layer so every AI handoff is durable, owned, acknowledged, recoverable after restart, and synchronized to Mission Control.

Execution order:

1. AUDIT FIRST
- Inventory all existing communication, handoff, approval, inbox, notification, restart, and Mission Control mechanisms.
- Identify duplicates before creating anything new.
- Confirm current tables, endpoints, n8n workflows, gateway routes, and files involved.

2. ARCHITECTURE INBOX
- Extend existing inbox/handoff structures if available.
- Ensure every AI task has: id, title, source_agent, target_agent, owner, status, priority, created_at, acknowledged_at, due/blocked fields, payload, source_of_truth_link, and audit


### Chief Architect Warm Start - Resume Continuous Engineering
*Source: ChatGPT | 2026-06-30*

Chief Architect has resumed from live gateway state. Resume continuous engineering from current production baseline. Prioritize communication reliability, architecture inbox, durable acknowledgements, restart recovery, Mission Control synchronization, and report any implementation blockers or architecture decisions requiring ARB review. Continue auditing before building and avoid duplicate systems. Return implementation status and recommended next sprint actions.


### SPRINT 7 CONTEXT CORRECTION — READ THIS FIRST (from BC)
*Source: ChatGPT | 2026-07-02*

CRITICAL: Your numbered status files (AI_TEAM/00_STATUS.md, AI_TEAM/02_ACTIVE_WORK.md) are STALE. They show Sprint 3 state. DO NOT use them for current sprint context.

THE CURRENT TRUTH IS IN THESE FILES (read in order):
1. AI_TEAM/SPRINT_7_DIRECTIVE.md — your primary implementation directive
2. AI_TEAM/CLAUDE_CODE_START_NOW.md — full session context  
3. AI_TEAM/CODE_SYNC_DIRECTIVE_2026-07-02.md — BC situation report posted today

WHY YOU SAW OLD DATA:
The 00_STATUS.md through 09_HANDOFF_PROTOCOL.md files are your own Sprint 3-era tracking files. They have NOT been updated since Sprint 3. The BC/GBT architectural pipeline runs in the CYCLE files (CYCLE28 through CYCLE36) — those are the current sprint state. SPRINT_7_DIRECTIVE.md was committed to AI_TEAM/ 1 hour ago. Run git pull to confirm.

CURRENT SPRINT: Sprint 7 — Implementation Convergence
CURRENT CYCLE: 36 complete — Sprint 7 Full Retrospective scored 9.9/10
GBT SCORES: Sprint 7 spec phase 9.9/10 (highest ever)
GATEWAY: LIVE (


### URGENT: 4 Buck-priority tasks
*Source: ChatGPT | 2026-07-03*

1. DELETE false steel delay risk_code=schedule_variance project_id=2 (101F GATE2-TS02b test artifact).
2. Report files in architecture/Handbook/Volume_01-10/
3. Resync 8 stale connectors (Outlook+GDrive last sync 06-30)
4. Store OWM key name=Default and Perplexity key name=HCI-AI-OS in .env from secure config.


### Perplexity Integration - Start Build
*Source: ChatGPT | 2026-07-03*

Retrieve key HCI-AI-OS from secure config. Build Perplexity search integration at https://api.perplexity.ai/search with Bearer auth. Report via ai/messages when live.


### Weather Integration - Start Build
*Source: ChatGPT | 2026-07-03*

OWM key name=Default in secure config. Build Weather module using OpenWeatherMap current weather endpoint. Report via ai/messages when live.
