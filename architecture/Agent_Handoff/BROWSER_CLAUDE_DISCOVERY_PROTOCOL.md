# Browser Claude Discovery Protocol
**Version:** 1.0 | **Maintained by:** Claude Code | **Last updated:** 2026-06-27

---

## Purpose

This protocol governs what Browser Claude does the moment it opens in any HCI-connected platform.
No manual direction from Buck is required. Browser Claude reads this protocol, detects which
platform it's in, runs the appropriate discovery checklist, and saves the output directly to
`~/Downloads/` using the naming convention below. The launchd watcher picks it up within seconds,
routes it to the Inbox, and processes it — no Buck involvement.

---

## Step 1 — Detect Platform

Identify the current platform from the browser URL:

| URL Pattern | Platform | `related_system` value |
|---|---|---|
| `app-na2.hubspot.com` or `app.hubspot.com` | HubSpot | `HubSpot` |
| `pro.houzz.com` | Houzz Pro | `Houzz Pro` |
| `drive.google.com` | Google Drive | `Google Drive` |
| `outlook.office.com` or `outlook.live.com` | Outlook / Microsoft 365 | `Microsoft365` |
| `app.qbo.intuit.com` | QuickBooks Online | `QuickBooks` |
| `app.n8n.cloud` or `localhost:5678` | n8n | `n8n` |
| `app.buildingconnected.com` | BuildingConnected | `BuildingConnected` |
| `app.procore.com` | Procore | `Procore` |

---

## Step 2 — Run Platform Discovery Checklist

### HubSpot Discovery Checklist
- [ ] Account metadata: portal ID, plan, region, user count, API quota
- [ ] Object counts: Contacts, Companies, Deals, Tasks, Notes, Emails, Meetings
- [ ] All pipelines: stages, deal counts per stage
- [ ] Custom properties: all 3 objects (Contacts, Companies, Deals)
- [ ] Connected apps: name, type, scopes, last active, status
- [ ] Workflows: count, locked/active status
- [ ] Identify zero-use objects (Quotes, Products, Line Items, Forms, Lists)
- [ ] Automation opportunities: list with value/complexity/status
- [ ] Critical gaps: P0/P1/P2 classification

### Houzz Pro Discovery Checklist
- [ ] Account metadata: plan, seats used, active projects, leads, archived leads
- [ ] Active projects list: name, client, location, created date, project type
- [ ] Team roster: name, email, role, status for all seats
- [ ] Module inventory: Contracts, Estimates, Schedules, Tasks, Daily Logs, Files,
      Invoices, POs, Change Orders, Budget, Time, Expenses, Client Dashboard — each
      with status (ACTIVE/LOW USE/UNUSED/NOT IN USE), record counts, and recommendation
- [ ] Financial documents: all estimates and invoices with amount and status
- [ ] Leads module: active count, archived count, stages available, conversion pipeline
- [ ] Integration status: QuickBooks, Zapier, Google Drive
- [ ] URL patterns for all key pages
- [ ] Automation opportunities: list with value/complexity/status
- [ ] Critical gaps: P0/P1/P2 classification

### Google Drive Discovery Checklist
- [ ] Top-level folder structure and key shared drives
- [ ] HCI project folders: naming convention, completeness
- [ ] File types in use: most common, total count estimates
- [ ] Permission model: who has access to what
- [ ] Integration with other tools

### QuickBooks Online Discovery Checklist
- [ ] Account plan and version
- [ ] Chart of accounts summary
- [ ] Customers (projects): count and open balance
- [ ] Vendors: count, COD vs net terms
- [ ] Open invoices: count and total AR
- [ ] Recent transactions: last 30 days summary
- [ ] Integration status: Houzz Pro, HubSpot, bank feeds
- [ ] Automation opportunities

---

## Step 3 — Produce Output File

**Filename convention:**
```
BROWSER_HANDOFF_{SYSTEM}_{DATE}_{TOPIC}.md
```
Examples:
- `BROWSER_HANDOFF_HUBSPOT_2026-06-27_BUSINESS_PROCESS.md`
- `BROWSER_HANDOFF_HOUZZ_2026-06-27_PLATFORM_INTELLIGENCE.md`
- `BROWSER_HANDOFF_QUICKBOOKS_2026-07-01_FINANCIAL_SNAPSHOT.md`

**Required frontmatter (copy exactly — all fields required):**
```markdown
---
source_agent: Browser Claude
destination_agent: Claude Code
document_type: browser_discovery
priority: high
status: ready_for_processing
related_system: {platform name exactly as in Step 1 table}
intended_action: ingest_and_route
requires_approval: false
discovery_date: {YYYY-MM-DD}
document_id: HCI-BH-{SYSTEM_SHORT}-{NNN}
version: 1.0
created_at: {YYYY-MM-DD}
summary: {One sentence: what was discovered, key metric, primary finding}
---
```

**Save to (preferred — zero-click intake):**
```
/Users/buckadams/HCI_AI_Operating_System/Architecture/Agent_Handoff/Inbox/
```
Write the file directly to the Inbox using the Write tool. The handoff processor runs automatically.

**Fallback (if Write tool unavailable — download to Downloads):**
Save to `~/Downloads/`. Claude Code or the launchd watcher picks it up within seconds.

---

## Step 4 — What Claude Code Does Automatically

1. launchd detects the new file in `~/Downloads` within seconds
2. `handoff_intake_watcher.py` moves the file to `Architecture/Agent_Handoff/Inbox/`
3. `handoff_processor.py` validates and routes:
   - HubSpot → `Architecture/Platform_Intelligence/HubSpot/Current/`
   - Houzz Pro → `Architecture/Platform_Intelligence/Houzz/Current/`
   - Previous file with same name is archived to `Archive/` before overwrite
4. Claude Code ingests the intelligence, updates structured documents, and notifies via ntfy

**Buck does nothing.** The moment Browser Claude saves the file to Downloads, the rest is automatic.

---

## Discovery Document Structure

Every discovery document should include these sections (in order):

```
## SUMMARY              — 3-5 sentence executive summary
## ACCOUNT METADATA     — key/value table of account facts
## OBJECT INVENTORY     — what exists, counts, status
## [PLATFORM SECTIONS]  — platform-specific modules/pipelines/properties
## AUTOMATION OPPORTUNITIES — ID, description, value, complexity, status
## CRITICAL GAPS        — P0/P1/P2 prioritized list
## NEXT ACTIONS FOR CLAUDE CODE — numbered action list
```

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-06-27 | Initial protocol — covers HubSpot + Houzz Pro |
