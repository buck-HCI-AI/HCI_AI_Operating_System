# RECOMMENDED_TOOLS_SPEC.md
## HCI AI OS — Recommended AI Tools, Apps, and Integrations

**Compiled by:** Browser Claude (Operations Intelligence)
**Source:** GBT Cycles 2–6, Buck Adams directives, CONSTRUCTION_OS_COMPLETENESS_AUDIT
**Date:** 2026-07-01
**Status:** Pending ARB review and prioritization

---

## Purpose

This document compiles every AI tool, third-party app, and integration recommended across all GBT cycles and operational audits to date. Each entry includes: what it is, why it was recommended, how it fits into HCI AI OS architecture, the priority level, and the implementation complexity estimate.

This document is the master intake list. Items are moved from here to their own implementation spec when prioritized for an active sprint.

---

## Priority 1 — Active Sprint or Immediate Next Sprint

### 1.1 Perplexity AI
**Category:** Research Intelligence Layer
**What it is:** Perplexity AI is a real-time web search engine built on language models. Unlike standard AI assistants, Perplexity retrieves live data from the web and cites its sources. It excels at current-market research, code documentation lookup, and investigative research tasks.
**Why recommended:** Construction decisions require current market intelligence that AI training data cannot provide. Material prices change weekly. Lead times shift. Local code amendments are not in training data. Perplexity bridges the gap between AI reasoning and real-world current data.
**Use cases for HCI:**
- Material cost benchmarking: "What is current framing lumber pricing in [market]?"
- Local code research: "What are the energy code requirements for IRC 2021 in [jurisdiction]?"
- Subcontractor reputation research: "What is known about [company name] in the construction market?"
- Manufacturer lead time verification: "What is the current lead time on [HVAC brand] commercial rooftop units?"
- Bid opportunity research: "What other contractors are active in [area] custom home market?"
**Architecture:** Perplexity API endpoint called by GBT or Browser Claude when a query requires current-market data. Results returned as structured research summary with citations. Response stored in Project Brain if project-relevant.
**API:** Perplexity API (pplx-api.perplexity.ai) — available via API key. Model: sonar or sonar-pro.
**Priority:** HIGH — directly addresses training-data currency gap
**Complexity:** LOW — API call, structured prompt template, response storage
**Owner (when assigned):** Claude Code

---

### 1.2 Telegram Bot (Integration, Not New Tool)
**Category:** Mobile Governance and Communications
**What it is:** Telegram is already in use as a team communication channel. The Telegram Bot API enables programmatic integration: sending messages, receiving commands, and triggering workflows via chat commands.
**Why recommended:** Buck needs mobile-first governance. Approval queue items must be actionable from his phone. The Telegram bot is the bridge between the AI OS and Buck’s primary communication device.
**Use cases for HCI:**
- /approve [item_id] — approve queue items from phone
- /auth @[user] [role] — grant team member access
- /status — receive full system health report
- /revoke @[user] — remove team member access
- Idle monitor alerts sent to Telegram when system is idle 30+ minutes
- Auto-restart alerts sent when WF-AI-001 detects stale agents
**Architecture:** Telegram Bot API webhook → n8n workflow → gateway command router → database action + audit log
**Spec document:** TELEGRAM_ARCHITECTURE_SPEC.md, TELEGRAM_AUTH_SPEC.md
**Priority:** HIGH — Sprint 3 primary workstream
**Complexity:** MEDIUM — bot setup, webhook, n8n workflow, gateway commands, database tables
**Owner (when assigned):** Claude Code

---

## Priority 2 — Next 3–6 Months

### 2.1 AI Plan Reader — Construction Document Intelligence
**Category:** Document Intelligence
**What it is:** A multi-phase AI pipeline for reading, parsing, and extracting structured data from architectural and engineering drawings (PDFs and image files).
**Why recommended:** Estimators spend enormous time manually reading drawing sets. A plan reader that extracts scope information, identifies conflicts, and flags missing details dramatically accelerates estimating and reduces errors.
**Phases:**
- Phase 1: PDF parsing with PyMuPDF or pdfplumber — extracts keynotes, specifications references, schedules, equipment lists from text layers in PDFs.
- Phase 2: Computer vision with GPT-4V or Claude Vision — analyzes drawing images for elements not captured in text: structural grids, room layouts, equipment locations, accessibility paths.
- Phase 3: Bluebeam API or Procore API integration — pulls live drawing sets from the platform where the design team maintains them.
**Use cases for HCI:**
- Automated scope extraction from drawing set on bid day
- Specification conflict detection (drawing calls for one product, spec calls for another)
- Missing detail identification (framing plan references a detail that does not exist in the set)
- Room-by-room scope takeoff for interior finish specifications
**Architecture:** Plan Reader service layer in FastAPI. GBT or estimator triggers analysis. Output: structured JSON scope extraction attached to Project Brain.
**Priority:** HIGH
**Complexity:** HIGH — multi-phase, computer vision, API integrations
**Owner (when assigned):** Claude Code + GBT architecture

---

### 2.2 CPM Scheduling Engine
**Category:** Project Management Intelligence
**What it is:** A Critical Path Method (CPM) scheduling engine implemented in PostgreSQL with a FastAPI layer for querying and updating.
**Why recommended:** Current scheduling is superintendent-driven and manually updated. CPM enables the system to automatically identify the critical path, calculate float, and alert when critical activities are at risk — before the project is behind.
**Database tables required:**
- schedule_activities (id, project_id, name, duration, planned_start, planned_end, actual_start, actual_end, status)
- schedule_relationships (id, predecessor_id, successor_id, relationship_type, lag)
- schedule_baselines (id, project_id, baseline_date, activities_json)
**Algorithms:**
- Forward pass: calculate Early Start and Early Finish for all activities
- Backward pass: calculate Late Start and Late Finish
- Float calculation: Total Float = LS - ES (or LF - EF)
- Critical path: all activities with Total Float = 0
**Use cases for HCI:**
- Real-time critical path identification on every active project
- Automatic alert when critical activity falls behind
- What-if analysis: "If concrete pour delays 3 days, what is impact on completion?"
- Integration with field reports: superintendent logs completion, system updates float automatically
**Priority:** HIGH
**Complexity:** MEDIUM — SQL-based CPM is well-understood, FastAPI wrapper straightforward
**Owner (when assigned):** Claude Code

---

### 2.3 Cost Forecasting Engine (Earned Value Management)
**Category:** Financial Intelligence
**What it is:** A real-time cost-to-complete forecast that runs against live project financial data.
**Why recommended:** Monthly cost reports are too slow for active project management. A continuous forecast gives Buck visibility into every project’s financial trajectory without waiting for a formal report.
**Inputs:** Original budget, committed costs, actual costs to date, earned value % by trade, remaining scope from CPM schedule.
**Outputs:** Projected final cost, projected variance ($), projected variance (%), confidence interval, trade-level breakdowns, alert when any trade exceeds threshold.
**Database tables required:**
- project_budgets (id, project_id, trade, budget_amount, committed_amount, actual_amount, earned_value_pct)
- cost_forecasts (id, project_id, forecast_date, projected_final, projected_variance, confidence)
**Use cases for HCI:**
- Weekly automated forecast for all active projects
- Immediate alert when trade variance exceeds threshold (e.g., 5%)
- Budget trend visualization over project duration
**Priority:** HIGH
**Complexity:** MEDIUM
**Owner (when assigned):** Claude Code

---

### 2.4 Bluebeam Revu (PDF Markup and Plan Management)
**Category:** Construction Document Platform
**What it is:** Bluebeam Revu is the industry standard tool for PDF markup, plan management, and construction document collaboration.
**Why recommended:** Most construction firms already use Bluebeam. Integration via Bluebeam Studio API or document sync allows the AI system to access the living drawing set without manual PDF uploads.
**Integration approach:** Bluebeam Studio Sessions API — monitor active sessions for drawing set changes, pull updated PDFs when sets are revised, trigger Plan Reader analysis on new document versions.
**Use cases for HCI:**
- Automatic plan reader trigger when drawing set is revised
- RFI tracking synchronized with Bluebeam markup sessions
- Submittal package management
**Priority:** MEDIUM — requires Bluebeam Studio subscription
**Complexity:** MEDIUM
**Owner (when assigned):** Claude Code

---

### 2.5 Procore (Construction Management Platform)
**Category:** Construction Management Platform
**What it is:** Procore is the leading cloud-based construction management platform used by general contractors and owners.
**Why recommended:** Many HCI clients and design teams may use Procore. API integration enables bi-directional data sync without manual re-entry.
**Integration approach:** Procore REST API — OAuth2 authentication, read/write access to projects, drawings, RFIs, submittals, and daily logs.
**Use cases for HCI:**
- Import project drawings from Procore without manual upload
- Sync RFI log bi-directionally
- Export daily log content to Procore for owner-facing visibility
- Import schedule updates from Procore Schedule module
**Priority:** MEDIUM — depends on client adoption
**Complexity:** HIGH — OAuth, complex data model
**Owner (when assigned):** Claude Code

---

## Priority 3 — 6–18 Month Roadmap

### 3.1 Subcontractor Portal
**Category:** External Collaboration
**What it is:** A secure, minimal web interface for subcontractors and vendors to submit bids, acknowledge POs, confirm deliveries, and submit lien waivers — without requiring email.
**Why recommended:** Email back-and-forth with subs is unstructured, hard to audit, and creates data-entry work for PM staff. A portal creates structured, auditable interactions.
**Tech stack:** FastAPI backend + simple React or plain HTML frontend. Auth: unique token per vendor per project (no account required).
**Priority:** MEDIUM
**Complexity:** MEDIUM

---

### 3.2 Photo AI and Field Documentation
**Category:** Field Intelligence
**What it is:** Computer vision analysis of construction site photographs submitted by superintendents.
**Why recommended:** Photos are already being taken on every job site. AI analysis of those photos creates structured operational data from unstructured images — work in place, safety observations, progress tracking.
**Use cases:**
- Work-in-place verification against approved drawings
- Safety hazard detection (PPE, fall protection, housekeeping)
- Visual progress tracking by location (framing complete, drywall complete, etc.)
**Integration:** Superintendent submits photos via Telegram or a mobile-friendly upload interface. Photos go to storage. Vision model analyzes. Structured observation record created. Attached to Project Brain.
**Models:** GPT-4V (OpenAI) or Claude Vision (Anthropic). Both available via API.
**Priority:** MEDIUM
**Complexity:** MEDIUM

---

### 3.3 OpenAI Realtime API / Voice Interface
**Category:** Voice Intelligence
**What it is:** OpenAI’s Realtime API enables low-latency voice conversations with AI models. Superintendents could dictate field reports, ask questions about drawings, or log observations hands-free.
**Why recommended:** Superintendents are often not at a desk. A voice interface reduces friction for field data entry — a superintendent can log a daily report by talking while walking the site.
**Use cases:**
- Voice-dictated daily log ("I poured the south foundation wall today, crew of 8, no issues")
- Hands-free drawing questions ("What’s the slab thickness in the garage?")
- Field observation logging
**Priority:** LOWER — requires mobile app development or dedicated device
**Complexity:** HIGH

---

### 3.4 Microsoft Power BI / Data Visualization
**Category:** Executive Dashboard
**What it is:** Power BI is Microsoft’s business intelligence platform. Already likely licensed through HCI’s Microsoft 365 subscription.
**Why recommended:** GBT noted the need for a multi-project executive dashboard. Power BI connects directly to the PostgreSQL database and provides drag-and-drop dashboard creation without custom development.
**Use cases:**
- Portfolio dashboard: all active projects, health scores, variances
- Financial dashboard: cost forecasts, budget performance, cash flow projection
- Vendor performance dashboard: scores, win rates, cost performance
**Priority:** MEDIUM — may already be licensed
**Complexity:** LOW — database connection + report building

---

### 3.5 DocuSign or Adobe Sign
**Category:** Contract Execution
**What it is:** Electronic signature platform for contract execution.
**Why recommended:** Contract execution currently requires physical or manual digital signature. Integration allows the system to: prepare the contract, route it to Buck for review, and upon Buck’s approval, send for e-signature execution — all within the governed approval workflow.
**Integration approach:** DocuSign eSignature API or Adobe Sign API. Contract document prepared by AI, uploaded to signing platform, recipient list configured, envelope sent after Buck approval.
**Priority:** MEDIUM
**Complexity:** MEDIUM

---

### 3.6 Sage 300 CRE or Quickbooks Integration
**Category:** Financial System Integration
**What it is:** Many construction firms use Sage 300 Construction and Real Estate or QuickBooks for accounting. API integration enables cost data from accounting to flow into the HCI AI OS cost forecasting engine.
**Why recommended:** Cost data is more accurate when pulled from the accounting system rather than manually entered. Integration eliminates double-entry and provides real-time actuals.
**Priority:** MEDIUM — depends on current accounting system
**Complexity:** HIGH — accounting integrations are typically complex

---

### 3.7 Weather API Integration
**Category:** Environmental Intelligence
**What it is:** Real-time weather data integrated with project scheduling.
**Why recommended:** Weather is one of the most common causes of construction schedule delay. An active weather integration allows the system to: alert superintendents of incoming weather, automatically log weather delays in the daily report, and flag schedule activities at risk from forecast conditions.
**Integration approach:** OpenWeatherMap API or Tomorrow.io (construction-focused weather service). One API call per active project per day, keyed to project site coordinates.
**Priority:** MEDIUM — low complexity, high operational value
**Complexity:** LOW

---

### 3.8 Lien Tracking and Conditional Lien Waiver Automation
**Category:** Legal / Financial Risk Management
**What it is:** Automated tracking of conditional and unconditional lien waiver collection from subcontractors and suppliers through the payment cycle.
**Why recommended:** Lien waivers are a legal risk management requirement on every project. Manual tracking is error-prone and time-consuming. Automation ensures no payment is released without the required waiver.
**Integration:** Subcontractor portal (3.1) + Approval Queue. Payment approval items automatically include lien waiver status.
**Priority:** MEDIUM
**Complexity:** MEDIUM

---

## Priority 4 — Research and Evaluation

### 4.1 Anthropic Claude Vision / Claude 3.5 Sonnet
**Category:** Advanced AI Model
**What it is:** Claude Vision capability for image analysis tasks including plan reading and photo AI.
**Why:** Already in the Anthropic ecosystem. May provide better construction-context understanding than competing vision models.
**Status:** Available via Anthropic API.

---

### 4.2 GPT-4V (OpenAI Vision)
**Category:** Advanced AI Model
**What it is:** OpenAI’s vision-capable model for image analysis.
**Why:** Strong general vision capability, well-documented for construction document analysis use cases in research literature.
**Status:** Available via OpenAI API.

---

### 4.3 Autodesk Construction Cloud (ACC)
**Category:** Construction Management Platform
**What it is:** Autodesk’s cloud platform for BIM, drawing management, RFI tracking, and field management.
**Why:** If clients or design teams use Autodesk products (Revit, AutoCAD, BIM 360), ACC integration provides a direct path to structured drawing data rather than PDF parsing.
**Status:** Evaluate based on client and design team tool adoption.

---

### 4.4 StructuredLabs / Structify (AI for Construction Data)
**Category:** Specialized Construction AI
**What it is:** Purpose-built AI tools for construction data extraction and analysis.
**Why:** May provide higher-quality construction document parsing than general-purpose vision models.
**Status:** Research and evaluate. Market is evolving rapidly.

---

### 4.5 ProcureHub / iSqFt / BuildingConnected
**Category:** Bid Management and Subcontractor Network
**What it is:** Platforms for managing bid invitations and accessing a broader subcontractor network.
**Why:** Expanding the bidder list beyond HCI’s existing vendor database increases competition and improves bid quality.
**Status:** Evaluate based on market coverage in HCI’s target geographies.

---

### 4.6 LLM-Optimized Vector Database (Pinecone / Weaviate)
**Category:** Knowledge Graph Enhancement
**What it is:** A vector database optimized for semantic search over large document corpora.
**Why:** As the HCI Knowledge Graph grows, semantic search (finding documents by meaning rather than keyword) becomes more valuable. A vector database enables: "Find all projects where we had concrete QA issues in winter conditions."
**Status:** Evaluate when Knowledge Graph exceeds 1,000 document entries.

---

## Implementation Priority Matrix

| Tool | Priority | Complexity | Sprint Target | Owner |
|------|----------|------------|---------------|-------|
| Perplexity AI | HIGH | LOW | Sprint 4 | Claude Code |
| Telegram Bot | HIGH | MEDIUM | Sprint 3 | Claude Code |
| AI Plan Reader Phase 1 | HIGH | MEDIUM | Sprint 4 | Claude Code |
| CPM Scheduling Engine | HIGH | MEDIUM | Sprint 4 | Claude Code |
| Cost Forecasting Engine | HIGH | MEDIUM | Sprint 4 | Claude Code |
| Bluebeam Integration | MEDIUM | MEDIUM | Sprint 5 | Claude Code |
| Procore Integration | MEDIUM | HIGH | Sprint 5-6 | Claude Code |
| Subcontractor Portal | MEDIUM | MEDIUM | Sprint 5 | Claude Code |
| Photo AI | MEDIUM | MEDIUM | Sprint 5 | Claude Code |
| Weather API | MEDIUM | LOW | Sprint 4 | Claude Code |
| DocuSign/Adobe Sign | MEDIUM | MEDIUM | Sprint 5 | Claude Code |
| Power BI Dashboard | MEDIUM | LOW | Sprint 4 | Claude Code |
| Voice Interface | LOWER | HIGH | Sprint 7+ | Claude Code |
| Sage/QuickBooks Integration | MEDIUM | HIGH | Sprint 6 | Claude Code |
| Lien Waiver Automation | MEDIUM | MEDIUM | Sprint 5 | Claude Code |

---

## Notes for ARB Review

1. Perplexity AI should be the first new tool integrated in Sprint 4 — lowest complexity, highest immediate value, fills a real gap in current AI capabilities.
2. CPM and Cost Forecasting are architectural dependencies — they should be designed together since CPM progress data feeds cost forecasting.
3. Plan Reader Phase 1 (PDF parsing) can be started before Phase 2 (vision) — text extraction alone provides significant value.
4. Voice interface requires mobile app development or dedicated device provisioning — scope significantly larger than API integrations.
5. All tools require ARB approval before implementation begins.

---

*Compiled by Browser Claude | Source: GBT Cycles 2–6, Buck Adams directives, CONSTRUCTION_OS_COMPLETENESS_AUDIT | 2026-07-01*
