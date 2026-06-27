# Chief Architect Review Queue

> **Owner:** ChatGPT (Chief Architect) + Buck Adams
> **Maintained by:** Claude Code (flags items; does NOT resolve philosophy items)
> **Last Updated:** 2026-06-27

This queue lists every item requiring Chief Architect review, authorship, or decision.
Claude Code flags and documents; Chief Architect resolves.

---

## SECTION A — Chapters Requiring Authorship

| Volume | Title | Status | Notes |
|---|---|---|---|
| Volume 01 | Executive Vision | **EMPTY — Chief Architect Required** | Platform purpose, values, decision-making philosophy |
| Volume 10 | Future Vision | **EMPTY — Chief Architect Required** | 2026-2028 roadmap, commercial model, scaling strategy |

---

## SECTION B — Missing Architecture (not yet specified)

### B-1: Houzz Extraction Strategy
**Gap:** The platform has a complete connector framework for Houzz (17 entity types, all persist handlers) but no extraction mechanism beyond manual browser work. The BROWSER_AGENT_STANDARD.md defines the protocol, but the "how" of Browser Agent operation is undefined.

**Questions for Chief Architect:**
- Is Browser Claude the permanent extraction mechanism or a stopgap?
- Should we invest in Playwright/Selenium automation for Houzz?
- What is the extraction cadence (nightly? on-demand? per-project)?
- Does HCI have any API access to Houzz beyond the browser interface?

**Implementation Impact:** Until resolved, all Houzz tables remain empty and schedule/budget predictions run at low confidence (0.2–0.4).

---

### B-2: Microsoft Outlook + Google Drive Connector Architecture
**Gap:** These connectors appear in the "expected connectors" list but have no implementation. The system auditor flags them as missing every audit.

**Questions for Chief Architect:**
- What Outlook data is needed? (email threading by project? calendar events? contacts?)
- What Drive data is needed? (SOPs? bid trackers? contract PDFs? all of the above?)
- Should these use the Browser Agent pattern or direct API (Graph API for Outlook, Drive API)?
- Drive API is already active via MCP — should the connector use the same OAuth token?

---

### B-3: HubSpot Writeback Philosophy
**Gap:** A hard rule exists ("never auto-write to HubSpot without Buck's approval") but there is no specification for WHAT should be written back, under what conditions, or what the approval gate looks like in practice.

**Questions for Chief Architect:**
- What HubSpot fields should the platform update? (deal stage? project health? last activity?)
- What events trigger a proposed writeback?
- What does the approval UI look like for Buck?

---

### B-4: Multi-Project Intelligence Cross-Pollination
**Gap:** Volume 02 documents the 4-layer intelligence model, but does not specify how cross-project learning works. The `background_learning_records` table has 406 records but no mining pipeline connected to it.

**Questions for Chief Architect:**
- Should lessons from 1355 Riverside automatically inform predictions for 101 Francis?
- What is the learning model — human review required, or autonomous?
- How does historical intelligence from completed projects feed into new ones?

---

## SECTION C — Implementation Gaps

| Gap | Severity | Detail |
|---|---|---|
| Houzz data not extracted | HIGH | All 17 Houzz entity tables empty; schedule/budget predictions at low confidence |
| 3 services without tests | MEDIUM | mcp_server, mining, sop_execution uncovered |
| 9 n8n workflows not imported | MEDIUM | GATE-G, GATE-H, GATE-E, GATE-F, AUTO-WEEKLY-* JSON files exist on disk but not in n8n |
| 7 n8n workflows inactive | MEDIUM | Includes AUTO-NIGHTLY-AUDIT and HZ-004 Houzz Daily Log Extraction Trigger |
| hubspot_activities not populated | LOW | Table created (migration 015), connector ready, but no sync has run yet |
| 28 empty DB tables | LOW | Most are Houzz tables awaiting first extraction |

---

## SECTION D — Inconsistencies (Implementation vs Handbook)

### D-1: Dual HubSpot Activity Tables
**Conflict:** The database schema has both `hubspot_engagements` (pre-connector-framework, simple schema) and `hubspot_activities` (connector framework, created in migration 015). Both exist simultaneously with different field sets.

**Claude Code Assessment:** `hubspot_engagements` appears to be legacy; `hubspot_activities` is the correct connector-pattern table. Recommend deprecating `hubspot_engagements`.

**Requires Chief Architect Decision:** Is `hubspot_engagements` used by any active integration? If not, deprecate via migration 016.

---

### D-2: Volume 09 Test Count Outdated
**Conflict:** Volume 09 (Governance) records "107 automated tests" — correct at time of writing. The `test_results_sprint3_sprint4.json` was added since but doesn't have a pass count recorded.

**Claude Code Action:** Will update Volume 09 test count when next test suite runs post-migration 015.

---

## SECTION E — Recommendations for Chief Architect

1. **Highest ROI next step: Authorize Houzz Browser Extraction** — 15 minutes per project (3 projects) unlocks schedule/budget/vendor intelligence across all 7 prediction types. Confidence scores jump from 0.2–0.4 to 0.6–0.85.

2. **Import 9 missing n8n workflows** — 30-minute task in n8n UI. These are defined and tested; just not imported.

3. **Activate AUTO-NIGHTLY-AUDIT** — currently inactive in n8n despite being the system's self-monitoring mechanism.

4. **Define the HubSpot writeback approval workflow** — the GATE-H workflow JSON exists but isn't imported. This is the mechanism for Buck to approve CRM updates.

---

## SECTION F — Future Opportunities (for Chief Architect Vision)

These are observations from implementation, not proposals:

1. **Playwright/Selenium Houzz connector** — would eliminate manual browser extraction and enable real-time schedule/budget updates. Requires evaluating whether Houzz ToS permits automation.

2. **Voice interface** — daily logs and site observations via voice would dramatically increase field usage. The platform is AI-first; voice input fits naturally.

3. **Photo AI processing** — daily photos → automatic progress detection, defect flagging, safety observation. Houzz file storage already has the schema.

4. **Cross-company benchmarking** — if platform expands to multiple GCs, cross-company cost benchmarking becomes possible without sharing raw data.

5. **Predictive cash flow with payment schedule optimization** — current cash_flow prediction is basic; a proper model with draw schedule optimization could be a significant client value-add.

---

*Queue last reviewed: 2026-06-27 | Next review: Chief Architect session*
