---
source_agent: Browser Claude
destination_agent: Claude Code
document_type: platform_watch
priority: high
status: ready_for_processing
related_system: HubSpot + Houzz Pro
intended_action: ingest_and_route
requires_approval: false
discovery_date: 2026-06-27
document_id: HCI-PW-001
version: 1.0
watch_cycle: 1
---

# PLATFORM WATCH — CYCLE 1
## HCI Continuous Platform Intelligence | 2026-06-27

## SCOPE
Platforms checked: HubSpot Product Updates (in-app), Houzz Pro Latest Releases
Platforms not yet checked: n8n (docs.n8n.io blocked), Google Workspace, Microsoft 365
Next check due: 2026-07-27 (monthly cadence recommended)

---

## HUBSPOT — NEW FEATURES (June 2026)

### CRITICAL FOR HCI

**Real-Time Table Updates in CRM**
Status: Public Beta - releasing Jun 30 2026
Impact: CRM list views update in real time without page refresh
HCI Relevance: Improves live deal pipeline monitoring during bid leveling sessions
Recommendation: JOIN BETA
Value: MEDIUM | Complexity: LOW

**View All Properties Panel on Activity Timeline**
Status: Live
Impact: See all object properties in a slide-out panel from the activity timeline
HCI Relevance: Faster sub-vendor lookup during phone calls without navigating away
Recommendation: EXTEND (use immediately, no config needed)
Value: MEDIUM | Complexity: LOW

**Dashboard Settings Panel**
Status: Live
Impact: New settings panel for dashboard configuration and sharing
HCI Relevance: Enables building the 4 recommended HCI dashboards more easily
Recommendation: EXTEND - use to build AO-HS-008 dashboards now
Value: HIGH | Complexity: LOW

**New Actions Library for Customer Agent (CRM + Workflows + Shopify)**
Status: Private Beta
Impact: HubSpot AI Customer Agent can now take actions in CRM and Workflows
HCI Relevance: AI agent could handle sub-vendor inquiries, update COI status, create tasks
Recommendation: REQUEST BETA - evaluate for COI automation use case
Value: HIGH | Complexity: MEDIUM
Note: Requires Smart CRM or paid hub

**HubSpot Agent CLI**
Status: Public Beta
Impact: Command-line interface for building and deploying HubSpot AI agents
HCI Relevance: Claude Code could build HCI-specific HubSpot agents via CLI
Recommendation: JOIN BETA - hand off to Claude Code for evaluation
Value: HIGH | Complexity: HIGH

**Prospecting Agent (all paid Hubs)**
Status: Live
Impact: AI prospecting agent that researches and reaches out to prospects automatically
HCI Relevance: Could automate sub-vendor outreach for new CSI divisions
Recommendation: EVALUATE - assess fit for sub-vendor prospecting
Value: MEDIUM | Complexity: LOW

**Track 20 New Company News Signals in Buyer Intent**
Status: Live
Impact: Monitor company news signals (funding, expansions, leadership changes)
HCI Relevance: Low relevance for construction sub-vendor CRM
Recommendation: IGNORE
Value: LOW | Complexity: LOW

**Activity Auto-Associations for App Objects**
Status: Live
Impact: Activities auto-associate to related CRM objects via app integrations
HCI Relevance: n8n-created activities will auto-associate to correct contacts/deals
Recommendation: INTEGRATE - verify n8n Construction OS activities are auto-associating
Value: MEDIUM | Complexity: LOW

**Centralized Data Model Management**
Status: Public Beta - releasing Jul 15 2026
Impact: Manage all custom objects, properties, and associations from one place
HCI Relevance: Easier management of COI fields, pipeline stages, deal properties
Recommendation: JOIN BETA
Value: MEDIUM | Complexity: LOW

**Reporting Search Enhancements**
Status: Live
Impact: Improved search within Reports module
HCI Relevance: Useful once AO-HS-008 dashboards are built
Recommendation: NOTE - no action needed
Value: LOW | Complexity: LOW

**Customer Agent now responds to Forms**
Status: Live
Impact: AI Customer Agent can respond to form submissions automatically
HCI Relevance: If COI submission form (AO-HS-005) is built, AI can auto-acknowledge
Recommendation: EXTEND - incorporate into COI form workflow design
Value: MEDIUM | Complexity: LOW

**Sunset of Legacy Public App Creation**
Status: Sunset notice
Impact: Legacy public apps being deprecated; private apps only going forward
HCI Relevance: n8n Construction OS uses private app - NOT AFFECTED
Recommendation: NOTE - verify WF-002 is also private app format
Value: LOW | Complexity: LOW

**New HubSpot Theme Rolling Out Aug 31 2026**
Status: In Development - early access available
Impact: Full UI redesign rolling out Aug 31
HCI Relevance: All users will see new UI; training refresh may be needed
Recommendation: NOTE - communicate to HCI team before Aug 31
Value: LOW | Complexity: LOW

---

## HOUZZ PRO — NEW FEATURES (Q1-Q2 2026)

### CRITICAL FOR HCI

**Company Files (Q2 2026) — HIGH PRIORITY**
Feature: Centralized company-wide document library separate from project folders
HCI Use Case: Store COI documents, licenses, insurance certificates, brand assets company-wide
HCI Action: Migrate COI files from HubSpot COI File Link field to Houzz Pro Company Files
Recommendation: EXTEND - activate immediately
Value: HIGH | Complexity: LOW

**Meetings in Projects (Q2 2026) — HIGH PRIORITY**
Feature: Schedule and manage client meetings directly within Houzz Pro projects
HCI Use Case: Client milestone meetings tracked per project without leaving Houzz Pro
HCI Action: Migrate client meeting scheduling from HubSpot to Houzz Pro project context
Recommendation: EXTEND
Value: HIGH | Complexity: LOW

**Team Calendar in Schedule Overview (Q2 2026) — HIGH PRIORITY**
Feature: View all team members schedules across all projects in one calendar; filter by person/project/task; daily and weekly views
HCI Use Case: PM visibility across 24 active projects and 18 team members
HCI Action: Activate scheduling module; build project templates; use team calendar for PM oversight
Recommendation: EXTEND - this directly addresses the schedule gap identified in discovery
Value: HIGH | Complexity: LOW

**Quick Payment Requests (Q2 2026) — HIGH PRIORITY**
Feature: Send secure payment link to client instantly without creating formal invoice; track transactions; convert to retainer
HCI Use Case: Request deposits or progress payments without full invoice workflow
HCI Action: Use for retainer collection at contract signing; complements invoice automation
Recommendation: EXTEND
Value: HIGH | Complexity: LOW

**Warranties & Claims (Q2 2026)**
Feature: Issue warranties tied to projects; track expiration; assign claims tasks
HCI Use Case: Post-construction warranty tracking for Aspen luxury projects
HCI Action: Activate at project Closeout stage; integrate with HCI AI OS closeout workflow
Recommendation: EXTEND
Value: MEDIUM | Complexity: LOW

**Client List Renamed to Contacts with Account Grouping (Q2 2026)**
Feature: Client List renamed Contacts; group related contacts under accounts; define roles; custom tags; custom list views
HCI Use Case: Align Houzz Pro contact model with HubSpot contact model for bridge sync
HCI Action: Map Houzz Pro Contact fields to HubSpot Contact fields in Zapier bridge design
Recommendation: INTEGRATE - critical for HubSpot bridge design
Value: HIGH | Complexity: MEDIUM

**Subcontractor Chat (Q1 2026)**
Feature: Add subcontractors to project chats - only specific conversations they need
HCI Use Case: Field coordination with subs on active projects without sharing full project access
HCI Action: Activate for 655 Garmish (45-task project); invite key subs to relevant chat threads
Recommendation: EXTEND
Value: MEDIUM | Complexity: LOW

**AI-Powered Lead Responses - AutoMate AI (Q1 2026)**
Feature: AutoMate AI suggests ready-to-send responses to Houzz leads; professional replies quickly
HCI Use Case: Respond to the 303 homeowners searching in HCI area without manual drafting
HCI Action: Enable AutoMate AI for lead response; review suggested replies before sending
Recommendation: EXTEND - directly addresses P1 lead capture gap
Value: HIGH | Complexity: LOW

**Cost Codes for Budget Tracking (Q4 2025)**
Feature: Enable cost codes to track every dollar spent; compare estimated vs actual; analyze performance
HCI Use Case: Track actual costs vs budget on Ground-Up Construction projects (813 McSkimming, 655 Garmish, 655 South Garmisch)
HCI Action: Activate cost codes; align with CSI Division codes used in HubSpot
Recommendation: EXTEND - use CSI division numbering as cost code structure
Value: HIGH | Complexity: MEDIUM

**Kanban View for Projects (Q4 2025)**
Feature: Kanban-style column view to move projects between stages
HCI Use Case: PM view of all 24 projects by stage; drag to advance
Recommendation: EXTEND - use immediately
Value: MEDIUM | Complexity: LOW

**Open Invoices Report (Q4 2025)**
Feature: Detailed report of unpaid and partially paid invoices with aging
HCI Use Case: Track outstanding client payments across all active projects
Recommendation: EXTEND - once invoicing is activated
Value: HIGH | Complexity: LOW

**Sync Expenses to QuickBooks Online (Q1 2026)**
Feature: Sync expenses from Houzz Pro directly to QuickBooks Online
HCI Use Case: Eliminate double-entry of project expenses between Houzz Pro and QuickBooks
Recommendation: INTEGRATE - activate QuickBooks connection + expense sync
Value: HIGH | Complexity: LOW

**AI Edits in Mood Boards (Q2 2026)**
Feature: Change finishes, swap items, update colors using text prompts in Mood Boards
Recommendation: IGNORE - low relevance for GC operations
Value: LOW

**Bulk Download Documents (Q2 2026)**
Feature: Select multiple invoices/estimates/POs and download at once
HCI Use Case: Monthly document export for accounting review
Recommendation: EXTEND - useful once financial documents are activated
Value: MEDIUM | Complexity: LOW

**Product Library in Takeoffs (Q2 2026)**
Feature: Use Items and Cost Codes from Takeoff canvas; markup and unit cost carry to estimate
HCI Use Case: Faster quantity takeoffs that auto-populate estimates
Recommendation: EVALUATE - assess takeoff workflow fit for HCI project types
Value: MEDIUM | Complexity: MEDIUM

**Add Selections to Existing Documents (Q2 2026)**
Feature: Add selection board items directly to existing estimates/invoices
HCI Use Case: Client-approved selections auto-added to change orders
Recommendation: EXTEND
Value: MEDIUM | Complexity: LOW

**Offline Mode for Mobile - iOS Only (Q1 2026)**
Feature: View all project data offline on iOS; view-only mode
HCI Use Case: Field crew access to project info at Aspen jobsites with poor connectivity
Recommendation: EXTEND - ensure all Field Crew have iOS Houzz Pro app installed
Value: HIGH | Complexity: LOW

**Dispute Management Portal (Q1 2026)**
Feature: Handle client payment disputes; view/filter; accept or respond with documents
HCI Use Case: Protection on luxury project payment disputes
Recommendation: EXTEND - activate when invoicing goes live
Value: MEDIUM | Complexity: LOW

---

## WATCH BASELINE — ESTABLISHED

Platforms checked this cycle:
- HubSpot in-app Product Updates (all 3 pages as of 2026-06-27)
- Houzz Pro Latest Releases (pages 1-3 as of 2026-06-27)

Platforms pending next cycle:
- n8n changelog (docs blocked - needs approval)
- Google Workspace updates
- Microsoft 365 / Copilot updates
- Meta Ads AI features
- Zapier new Houzz Pro triggers (BETA)

Next watch cycle: 2026-07-27 (recommended monthly)
Delta threshold: Any feature tagged HIGH value or any deprecation notice

---

## TOP 5 IMMEDIATE ACTION ITEMS (for Claude Code)

1. ACTIVATE Houzz Pro Company Files - store COI documents company-wide
2. ACTIVATE Team Calendar - PM visibility across all 24 projects
3. ENABLE AutoMate AI Lead Responses - recover 303 homeowner leads
4. CONFIGURE Zapier HubSpot-to-Houzz bridge - P0 integration gap
5. EVALUATE HubSpot Agent CLI beta - Claude Code builds HCI agents natively

---
Browser Claude - Platform Intelligence Agent | Read-only. Do not modify production systems.