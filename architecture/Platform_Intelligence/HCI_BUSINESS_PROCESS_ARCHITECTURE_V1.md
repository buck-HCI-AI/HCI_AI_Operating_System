# HCI Business Process Architecture — Platform Intelligence v1.0
*Source: HCI Opportunity Report HCI-OR-001 | Produced by: HCI Discovery Agent*
*Ingested: 2026-06-27 | Classification: Internal Architecture — Ingestion Ready*
*Scope: HubSpot Sales Hub Starter (Portal 244757054) + Houzz Pro (18 seats, Aspen)*

---

## Executive Summary

Hendrickson Construction operates across two primary platforms: **HubSpot** (CRM, contacts, deals, email) and **Houzz Pro** (project management, financials, field operations). These platforms currently serve distinct lifecycle phases but are **not connected to each other** — the single most critical integration gap in the HCI tech stack.

**Key Findings:**
- HubSpot is used as a bidding CRM + sub-vendor database — not a full sales system
- Houzz Pro is used for project management but underutilized (0 contracts, 0 invoices, no QuickBooks sync)
- The platforms are siloed — no Deal→Project bridge
- HubSpot Workflows locked behind plan upgrade ($70/mo incremental)
- n8n polls HubSpot on 15-min cron — no webhooks, no real-time events
- Zapier is available in Houzz Pro but not configured

**38 opportunities identified:** 20 HubSpot (HS-01→HS-20) + 18 Houzz Pro (HP-01→HP-18)

---

## Scoring Methodology

| Dimension | Scale | Definition |
|-----------|-------|-----------|
| Business Value (BV) | 1-5 | Revenue/cost impact |
| Field Impact (FI) | 1-5 | Superintendent daily value |
| PM Impact (PM) | 1-5 | Project Manager weekly value |
| Executive Impact (EX) | 1-5 | Buck/leadership visibility |
| Technical Complexity (TC) | 1-5 | LOW=1, MEDIUM=3, HIGH=5 |
| Priority Score | (BV+FI+PM+EX)/TC | Higher = build sooner |

---

## Phase Definitions

| Phase | Timeline | Criteria |
|-------|----------|---------|
| Phase 1 | 0-30 days | HIGH value + LOW/MEDIUM complexity + no blocking dependencies |
| Phase 2 | 30-90 days | HIGH/MEDIUM value + MEDIUM complexity |
| Phase 3 | 90-180 days | Any value + HIGH complexity |
| Phase 4 | 180+ days | EVALUATE or IGNORE — revisit when prerequisites met |

---

## Part I: HubSpot Platform Opportunities (HS-01 → HS-20)

---

### HS-01 — Contacts Module
| Field | Value |
|-------|-------|
| **process_id** | HS-01 |
| **lifecycle_phase** | Sub/Vendor Management + CRM |
| **process_owner** | PM / Buck |
| **current_state** | 1,311 records, 217 properties. Used for subs, clients, vendors, architects. COI tracking manual. |
| **systems_involved** | HubSpot |
| **manual_steps** | COI expiration tracking, sub tier classification |
| **duplicate_data_entry** | None — single system |
| **bottlenecks** | COI renewals tracked in spreadsheets/email |
| **missing_automation** | Auto-COI expiry alerts, webhook triggers on status change |
| **missing_ai_opportunities** | Engagement scoring, sub performance ranking |
| **future_state_workflow** | n8n daily cron → flag expiring COIs → notify PM → AI-drafted renewal request |
| **system_ownership** | HubSpot |
| **automation_level** | LOW (polling only) |
| **recommendation** | INTEGRATE + EXTEND |
| **operational_value** | HIGH |
| **complexity** | LOW |
| **BV** | 5 | **FI** | 3 | **PM** | 4 | **EX** | 4 | **TC** | 1 | **score** | 16.0 | **phase** | 1 |

---

### HS-02 — Companies Module (COI Engine)
| Field | Value |
|-------|-------|
| **process_id** | HS-02 |
| **lifecycle_phase** | Sub/Vendor Management |
| **process_owner** | PM / Buck |
| **current_state** | 1,183 company records. COI is the most critical unautomated field. |
| **systems_involved** | HubSpot |
| **manual_steps** | COI renewal tracking, expiration monitoring |
| **duplicate_data_entry** | None |
| **bottlenecks** | COI expiry → no automated alerts → risk exposure |
| **missing_automation** | n8n cron GET companies → compare coi_expiration_date → PATCH companies/{id} → notify |
| **missing_ai_opportunities** | AI-drafted COI renewal emails, sub performance reports |
| **future_state_workflow** | Daily cron: flag expiring COIs → auto-draft renewal email → human review → send |
| **system_ownership** | HubSpot |
| **automation_level** | LOW |
| **recommendation** | INTEGRATE + EXTEND (highest ROI single automation in stack) |
| **operational_value** | HIGH |
| **complexity** | LOW |
| **BV** | 5 | **FI** | 3 | **PM** | 4 | **EX** | 5 | **TC** | 1 | **score** | 17.0 | **phase** | 1 |

---

### HS-03 — Deals Module (Bid + Project Pipeline)
| Field | Value |
|-------|-------|
| **process_id** | HS-03 |
| **lifecycle_phase** | Bidding → Active Project |
| **process_owner** | PM / Buck |
| **current_state** | 309 deals, 2 pipelines (Bidding + Projects). Bridge between them is manual. |
| **systems_involved** | HubSpot, Houzz Pro |
| **manual_steps** | Moving deal from Bidding to Projects pipeline, creating Houzz project manually |
| **duplicate_data_entry** | Deal exists in HubSpot AND project exists in Houzz — no sync |
| **bottlenecks** | Manual deal→project bridge; no HubSpot→Houzz sync |
| **missing_automation** | Auto-create Houzz project when deal moves to "Awarded" stage |
| **missing_ai_opportunities** | AI deal scoring, close probability, bid recommendation |
| **future_state_workflow** | HubSpot webhook → deal stage = "Awarded" → auto-create Houzz project → sync key fields |
| **system_ownership** | HubSpot (primary) + Houzz Pro (operational mirror) |
| **automation_level** | NONE |
| **recommendation** | INTEGRATE + EXTEND (critical bridge) |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 3 | **PM** | 5 | **EX** | 5 | **TC** | 3 | **score** | 6.0 | **phase** | 2 |

---

### HS-04 — Tasks Module
| Field | Value |
|-------|-------|
| **process_id** | HS-04 |
| **lifecycle_phase** | Deal Management |
| **process_owner** | PM |
| **current_state** | 38 open tasks, all manual "Follow up" type. No automation. |
| **missing_automation** | Auto-create tasks on deal stage transitions |
| **missing_ai_opportunities** | AI-suggested follow-up timing based on engagement history |
| **recommendation** | EXTEND |
| **operational_value** | MEDIUM |
| **complexity** | LOW |
| **BV** | 3 | **FI** | 2 | **PM** | 4 | **EX** | 3 | **TC** | 1 | **score** | 12.0 | **phase** | 1 |

---

### HS-05 — Notes Module (AI Layer)
| Field | Value |
|-------|-------|
| **process_id** | HS-05 |
| **lifecycle_phase** | Deal Intelligence |
| **process_owner** | PM |
| **current_state** | Unstructured text notes on deals. Richest unstructured data source in HubSpot. |
| **missing_automation** | AI indexing via Qdrant, semantic retrieval |
| **missing_ai_opportunities** | AI deal summarization from notes + engagements |
| **recommendation** | EXTEND |
| **operational_value** | MEDIUM |
| **complexity** | MEDIUM |
| **BV** | 3 | **FI** | 2 | **PM** | 4 | **EX** | 3 | **TC** | 3 | **score** | 4.0 | **phase** | 2 |

---

### HS-06 — Emails Module (Bid Invitations)
| Field | Value |
|-------|-------|
| **process_id** | HS-06 |
| **lifecycle_phase** | Bidding |
| **process_owner** | PM |
| **current_state** | Outlook connected. 1:1 tracked emails. Sequences locked (requires Pro upgrade). |
| **missing_automation** | AI-drafted bid invitation emails, auto-reply detection, sequences |
| **recommendation** | EXTEND (requires HubSpot Pro upgrade for Sequences) |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 2 | **PM** | 4 | **EX** | 4 | **TC** | 3 | **score** | 5.0 | **phase** | 2 |

---

### HS-07 — Meetings Module
| Field | Value |
|-------|-------|
| **process_id** | HS-07 |
| **lifecycle_phase** | Bidding / Client Management |
| **process_owner** | PM / Buck |
| **current_state** | meet.hubspot.com/buck-adams/meeting exists. Synced with Outlook Calendar. |
| **missing_automation** | Embed scheduling link in bid invitations, pre-meeting AI briefings |
| **recommendation** | INTEGRATE |
| **operational_value** | MEDIUM |
| **complexity** | LOW |
| **BV** | 3 | **FI** | 2 | **PM** | 3 | **EX** | 3 | **TC** | 1 | **score** | 11.0 | **phase** | 1 |

---

### HS-08 — Line Items Module
| Field | Value |
|-------|-------|
| **process_id** | HS-08 |
| **lifecycle_phase** | Estimating / CPQ |
| **process_owner** | PM / Buck |
| **current_state** | Not in use. Foundation for Quotes. |
| **missing_automation** | Scope catalog → AI estimate generation |
| **recommendation** | EXTEND (future — prerequisite: HS-09 and HS-10 first) |
| **operational_value** | HIGH (future) |
| **complexity** | HIGH |
| **BV** | 4 | **FI** | 1 | **PM** | 3 | **EX** | 4 | **TC** | 5 | **score** | 2.4 | **phase** | 3 |

---

### HS-09 — Quotes Module
| Field | Value |
|-------|-------|
| **process_id** | HS-09 |
| **lifecycle_phase** | Estimating |
| **process_owner** | PM / Buck |
| **current_state** | Not in use. AI-powered CPQ available. Maps to "ROM Submitted" stage. |
| **missing_automation** | Auto-generate ROM from deal scope, e-signature workflow |
| **recommendation** | EXTEND |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 1 | **PM** | 5 | **EX** | 5 | **TC** | 3 | **score** | 5.3 | **phase** | 2 |

---

### HS-10 — Products Module
| Field | Value |
|-------|-------|
| **process_id** | HS-10 |
| **lifecycle_phase** | Estimating |
| **process_owner** | PM |
| **current_state** | Not in use. Prerequisite for Quotes. |
| **recommendation** | EXTEND (prerequisite for HS-09) |
| **operational_value** | MEDIUM |
| **complexity** | LOW |
| **BV** | 3 | **FI** | 1 | **PM** | 3 | **EX** | 3 | **TC** | 1 | **score** | 10.0 | **phase** | 2 |

---

### HS-11 — Workflows Module
| Field | Value |
|-------|-------|
| **process_id** | HS-11 |
| **lifecycle_phase** | All phases |
| **process_owner** | PM / n8n |
| **current_state** | LOCKED on Starter plan. Upgrade required ($70/mo incremental). |
| **ROI_case** | Eliminates 4 hrs/week COI tracking + 3 hrs/week bid follow-up. Pays for itself in 1 week. |
| **missing_automation** | COI alerts, bid invitations, deal stage automations, task creation |
| **recommendation** | UPGRADE + INTEGRATE (highest leverage investment after Houzz extraction) |
| **operational_value** | HIGH |
| **complexity** | LOW (after upgrade) |
| **BV** | 5 | **FI** | 3 | **PM** | 5 | **EX** | 5 | **TC** | 2 | **score** | 9.0 | **phase** | 1 (Buck decision required — upgrade cost) |

---

### HS-12 — Forms Module
| Field | Value |
|-------|-------|
| **process_id** | HS-12 |
| **lifecycle_phase** | Sub Onboarding |
| **current_state** | Not in use. COI submission form would eliminate manual data entry. |
| **missing_automation** | COI submission form → auto-update company record |
| **recommendation** | EXTEND |
| **operational_value** | HIGH |
| **complexity** | LOW |
| **BV** | 5 | **FI** | 2 | **PM** | 4 | **EX** | 4 | **TC** | 1 | **score** | 15.0 | **phase** | 1 |

---

### HS-13 — Lists / Segments Module
| Field | Value |
|-------|-------|
| **process_id** | HS-13 |
| **lifecycle_phase** | Bidding |
| **current_state** | Not in use. Critical for bulk bid invitations. |
| **missing_automation** | Dynamic lists by CSI division → bulk bid invitation campaigns |
| **recommendation** | EXTEND |
| **operational_value** | HIGH |
| **complexity** | LOW |
| **BV** | 4 | **FI** | 2 | **PM** | 4 | **EX** | 4 | **TC** | 1 | **score** | 14.0 | **phase** | 1 |

---

### HS-14 — Marketing Emails Module
| Field | Value |
|-------|-------|
| **process_id** | HS-14 |
| **lifecycle_phase** | Bidding / Client Management |
| **current_state** | Not in use. 2-3 templates would cover 90% of needs. |
| **recommendation** | EXTEND |
| **operational_value** | MEDIUM |
| **complexity** | LOW |
| **BV** | 3 | **FI** | 1 | **PM** | 3 | **EX** | 3 | **TC** | 1 | **score** | 10.0 | **phase** | 2 |

---

### HS-15 — Documents Module
| Field | Value |
|-------|-------|
| **process_id** | HS-15 |
| **lifecycle_phase** | Bidding |
| **current_state** | Not in use. Track when subs open bid packages — highly actionable. |
| **missing_automation** | Bid package → HubSpot Document → tracking link in invitation |
| **recommendation** | EXTEND |
| **operational_value** | HIGH |
| **complexity** | LOW |
| **BV** | 5 | **FI** | 2 | **PM** | 4 | **EX** | 4 | **TC** | 1 | **score** | 15.0 | **phase** | 1 |

---

### HS-16 — Attachments
| Field | Value |
|-------|-------|
| **process_id** | HS-16 |
| **lifecycle_phase** | Sub Management |
| **current_state** | COI files stored as external links. Should be native HubSpot attachments. |
| **recommendation** | EXTEND |
| **operational_value** | MEDIUM |
| **complexity** | LOW |
| **BV** | 3 | **FI** | 2 | **PM** | 3 | **EX** | 3 | **TC** | 1 | **score** | 11.0 | **phase** | 2 |

---

### HS-17 — Activities / Activity Feed (AI Summarization)
| Field | Value |
|-------|-------|
| **process_id** | HS-17 |
| **lifecycle_phase** | Deal Intelligence |
| **current_state** | 2,135 engagements logged. No AI summarization. |
| **missing_ai_opportunities** | n8n → GET engagements by deal → Claude Haiku summary → store in HCI AI OS |
| **recommendation** | INTEGRATE |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 2 | **PM** | 4 | **EX** | 5 | **TC** | 3 | **score** | 5.3 | **phase** | 2 |

---

### HS-18 — Dashboards & Reports
| Field | Value |
|-------|-------|
| **process_id** | HS-18 |
| **lifecycle_phase** | Executive |
| **current_state** | 0 dashboards, 0 reports created. 2-hour setup = immediate executive visibility. |
| **missing_automation** | COI Health, Bid Pipeline, AR, Sub Performance dashboards |
| **recommendation** | EXTEND |
| **operational_value** | HIGH |
| **complexity** | LOW |
| **BV** | 5 | **FI** | 2 | **PM** | 4 | **EX** | 5 | **TC** | 1 | **score** | 16.0 | **phase** | 1 |

---

### HS-19 — Connected Apps & Integration Layer
| Field | Value |
|-------|-------|
| **process_id** | HS-19 |
| **lifecycle_phase** | Platform Integration |
| **current_state** | n8n Private App ID 43234028. 15-min polling. No HubSpot→Houzz bridge. |
| **missing_automation** | HubSpot Deal → Houzz Pro Project bridge (THE critical missing integration) |
| **recommendation** | EXTEND (critical) |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 3 | **PM** | 4 | **EX** | 5 | **TC** | 3 | **score** | 5.7 | **phase** | 1 |

---

### HS-20 — Webhooks & Event-Driven Architecture
| Field | Value |
|-------|-------|
| **process_id** | HS-20 |
| **lifecycle_phase** | Platform Integration |
| **current_state** | n8n polling every 15 min. No real-time webhooks. |
| **missing_automation** | Webhook triggers → real-time n8n execution (requires Pro upgrade) |
| **recommendation** | EXTEND (requires HubSpot Pro) |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 2 | **PM** | 4 | **EX** | 5 | **TC** | 3 | **score** | 5.3 | **phase** | 2 |

---

## Part II: Houzz Pro Platform Opportunities (HP-01 → HP-18)

---

### HP-01 — Projects Module (Critical Bridge)
| Field | Value |
|-------|-------|
| **process_id** | HP-01 |
| **lifecycle_phase** | Active Project |
| **process_owner** | PM / SS |
| **current_state** | 24 active projects in Houzz. No HubSpot sync. Zapier BETA available but not configured. |
| **duplicate_data_entry** | Project data exists in BOTH HubSpot (deals) and Houzz (projects) — no sync |
| **bottlenecks** | Manual project creation in Houzz after deal awarded in HubSpot |
| **missing_automation** | HubSpot Deal "Awarded" → auto-create Houzz project + populate fields |
| **recommendation** | INTEGRATE (most critical Houzz opportunity) |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 4 | **PM** | 5 | **EX** | 5 | **TC** | 3 | **score** | 6.3 | **phase** | 1 |

---

### HP-02 — Leads Module
| Field | Value |
|-------|-------|
| **process_id** | HP-02 |
| **lifecycle_phase** | Lead Capture |
| **current_state** | 303 homeowners interested in HCI's area. Only 1 in active pipeline. 56 archived. |
| **missing_automation** | AI-powered lead response, CRM sync to HubSpot, lead scoring |
| **recommendation** | INTEGRATE |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 1 | **PM** | 3 | **EX** | 5 | **TC** | 3 | **score** | 4.7 | **phase** | 2 |

---

### HP-03 — Contracts Module
| Field | Value |
|-------|-------|
| **process_id** | HP-03 |
| **lifecycle_phase** | Contract Execution |
| **current_state** | 0 contracts created. HCI using external methods (DocuSign, paper). |
| **missing_automation** | Auto-generate contract from deal scope + auto-e-signature workflow |
| **recommendation** | EXTEND |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 1 | **PM** | 5 | **EX** | 5 | **TC** | 3 | **score** | 5.3 | **phase** | 2 |

---

### HP-04 — Estimates Module
| Field | Value |
|-------|-------|
| **process_id** | HP-04 |
| **lifecycle_phase** | Estimating |
| **current_state** | 1 estimate sent across 24 projects. Feature not integrated in standard workflow. |
| **missing_automation** | Auto-create estimate when project created + sync total to HubSpot deal amount |
| **missing_ai_opportunities** | AI estimate generation from project scope + historical unit costs |
| **recommendation** | EXTEND |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 2 | **PM** | 5 | **EX** | 5 | **TC** | 3 | **score** | 5.7 | **phase** | 2 |

---

### HP-05 — Invoices Module
| Field | Value |
|-------|-------|
| **process_id** | HP-05 |
| **lifecycle_phase** | Billing |
| **current_state** | 2 draft invoices ($0.63, $0). HCI invoicing through QuickBooks or check. |
| **missing_automation** | Milestone-based invoice generation, payment → HubSpot deal update |
| **recommendation** | EXTEND |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 1 | **PM** | 4 | **EX** | 5 | **TC** | 3 | **score** | 5.0 | **phase** | 2 |

---

### HP-06 — Change Orders Module
| Field | Value |
|-------|-------|
| **process_id** | HP-06 |
| **lifecycle_phase** | Active Project |
| **current_state** | 0 change orders created. HCI managing via email/paper. |
| **missing_automation** | AI CO drafting from daily log notes, auto-advance deal amount on approval |
| **missing_ai_opportunities** | AI change order language generation, risk flagging |
| **recommendation** | EXTEND (high-value, low complexity) |
| **operational_value** | HIGH |
| **complexity** | LOW |
| **BV** | 5 | **FI** | 3 | **PM** | 5 | **EX** | 5 | **TC** | 1 | **score** | 18.0 | **phase** | 1 |

---

### HP-07 — Purchase Orders Module
| Field | Value |
|-------|-------|
| **process_id** | HP-07 |
| **lifecycle_phase** | Procurement |
| **current_state** | 0 POs created. Sub payments managed through HubSpot + check. |
| **missing_automation** | Auto-generate PO when subcontract status = "Fully Executed" |
| **recommendation** | EXTEND |
| **operational_value** | MEDIUM |
| **complexity** | MEDIUM |
| **BV** | 3 | **FI** | 2 | **PM** | 4 | **EX** | 4 | **TC** | 3 | **score** | 4.3 | **phase** | 2 |

---

### HP-08 — Retainers & Credits Module
| Field | Value |
|-------|-------|
| **process_id** | HP-08 |
| **lifecycle_phase** | Billing |
| **current_state** | 0 retainers created. |
| **missing_automation** | Auto-request retainer when contract signed |
| **recommendation** | EXTEND (future phase) |
| **operational_value** | MEDIUM |
| **complexity** | LOW |
| **BV** | 3 | **FI** | 1 | **PM** | 3 | **EX** | 4 | **TC** | 1 | **score** | 11.0 | **phase** | 3 |

---

### HP-09 — Budget Module (Critical)
| Field | Value |
|-------|-------|
| **process_id** | HP-09 |
| **lifecycle_phase** | Active Project |
| **process_owner** | PM / Buck |
| **current_state** | Not observed in use. Without it, zero real-time project profitability visibility. |
| **missing_automation** | Auto-populate from estimate, AI variance alerts, weekly budget reports |
| **recommendation** | EXTEND (most operationally valuable Houzz Pro financial feature) |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 3 | **PM** | 5 | **EX** | 5 | **TC** | 3 | **score** | 6.0 | **phase** | 1 |

---

### HP-10 — Takeoffs Module
| Field | Value |
|-------|-------|
| **process_id** | HP-10 |
| **lifecycle_phase** | Estimating |
| **current_state** | Not in use. AI-assisted takeoff is emerging technology. |
| **recommendation** | EVALUATE |
| **operational_value** | MEDIUM |
| **complexity** | HIGH |
| **BV** | 3 | **FI** | 2 | **PM** | 3 | **EX** | 3 | **TC** | 5 | **score** | 2.2 | **phase** | 4 |

---

### HP-11 — 3D Floor Plans Module
| Field | Value |
|-------|-------|
| **process_id** | HP-11 |
| **lifecycle_phase** | Design |
| **current_state** | Not in use. Quality below Aspen luxury market expectations. |
| **recommendation** | IGNORE (Aspen luxury market requires professional renderings) |
| **operational_value** | LOW |
| **complexity** | MEDIUM |
| **BV** | 1 | **FI** | 1 | **PM** | 1 | **EX** | 1 | **TC** | 3 | **score** | 1.3 | **phase** | 4 |

---

### HP-12 — Mood Boards Module
| Field | Value |
|-------|-------|
| **process_id** | HP-12 |
| **lifecycle_phase** | Design |
| **current_state** | Not in use. GC not responsible for design direction. |
| **recommendation** | IGNORE (design-build firms only) |
| **operational_value** | LOW |
| **complexity** | LOW |
| **BV** | 1 | **FI** | 1 | **PM** | 1 | **EX** | 1 | **TC** | 1 | **score** | 4.0 | **phase** | 4 |

---

### HP-13 — Selection Boards Module
| Field | Value |
|-------|-------|
| **process_id** | HP-13 |
| **lifecycle_phase** | Active Project |
| **process_owner** | PM / Client |
| **current_state** | Not in use. Delayed selections cascade into schedule delays on luxury projects. |
| **missing_automation** | Auto-create selection board at "Budget Locked" stage, AI reminders |
| **recommendation** | EXTEND (high field value) |
| **operational_value** | HIGH |
| **complexity** | LOW |
| **BV** | 5 | **FI** | 3 | **PM** | 5 | **EX** | 4 | **TC** | 1 | **score** | 17.0 | **phase** | 1 |

---

### HP-14 — Selections Tracker Module
| Field | Value |
|-------|-------|
| **process_id** | HP-14 |
| **lifecycle_phase** | Active Project |
| **current_state** | Not in use. XLS export is an API opportunity for procurement intelligence. |
| **missing_automation** | Weekly XLS export → n8n parse → AI procurement bottleneck report |
| **recommendation** | INTEGRATE |
| **operational_value** | MEDIUM |
| **complexity** | MEDIUM |
| **BV** | 4 | **FI** | 3 | **PM** | 4 | **EX** | 4 | **TC** | 3 | **score** | 5.0 | **phase** | 2 |

---

### HP-15 — Bids Module (Houzz Pro)
| Field | Value |
|-------|-------|
| **process_id** | HP-15 |
| **lifecycle_phase** | Bidding |
| **current_state** | Not in use. HCI uses HubSpot + email for bidding. |
| **missing_automation** | Consolidate bidding to Houzz Pro (requires sub-vendor adoption) |
| **recommendation** | EVALUATE (sub-vendor adoption risk) |
| **operational_value** | MEDIUM |
| **complexity** | HIGH |
| **BV** | 3 | **FI** | 2 | **PM** | 3 | **EX** | 3 | **TC** | 5 | **score** | 2.2 | **phase** | 4 |

---

### HP-16 — Files & Photos Module
| Field | Value |
|-------|-------|
| **process_id** | HP-16 |
| **lifecycle_phase** | Active Project |
| **process_owner** | SS / PM |
| **current_state** | Presumably active. No standard folder structure. Google Drive separate. |
| **missing_automation** | Auto-create folder templates, Google Drive native sync |
| **recommendation** | EXTEND |
| **operational_value** | MEDIUM |
| **complexity** | LOW |
| **BV** | 3 | **FI** | 4 | **PM** | 3 | **EX** | 3 | **TC** | 1 | **score** | 13.0 | **phase** | 1 |

---

### HP-17 — Schedule Module (Critical)
| Field | Value |
|-------|-------|
| **process_id** | HP-17 |
| **lifecycle_phase** | Active Project |
| **process_owner** | SS / PM |
| **current_state** | Not confirmed in use. No schedules observed in explored projects. |
| **missing_automation** | AI schedule generation from contract scope, delay detection, milestone sync |
| **missing_ai_opportunities** | AI phase duration estimation, critical path delay detection |
| **recommendation** | EXTEND (high field + PM value; unlocks BTW-7 Houzz browser extraction ROI) |
| **operational_value** | HIGH |
| **complexity** | MEDIUM |
| **BV** | 5 | **FI** | 5 | **PM** | 5 | **EX** | 5 | **TC** | 3 | **score** | 6.7 | **phase** | 1 |

---

### HP-18 — Tasks & Punchlist Module
| Field | Value |
|-------|-------|
| **process_id** | HP-18 |
| **lifecycle_phase** | Active Project / Closeout |
| **process_owner** | SS / PM |
| **current_state** | Active — 1 task observed. No punchlist automation. |
| **missing_automation** | AI punchlist from daily logs, photo-evidence required on completion, PM notification |
| **missing_ai_opportunities** | AI-generated punchlist from 30 days of daily logs |
| **recommendation** | EXTEND |
| **operational_value** | HIGH |
| **complexity** | LOW |
| **BV** | 5 | **FI** | 5 | **PM** | 4 | **EX** | 4 | **TC** | 1 | **score** | 18.0 | **phase** | 1 |

---

## Strategic Summary

| Recommendation | Count | Rationale |
|---------------|-------|-----------|
| INTEGRATE + EXTEND | 4 | Critical — do now |
| INTEGRATE | 5 | Must do — missing connections |
| EXTEND | 21 | Build out existing features |
| UPGRADE + INTEGRATE | 1 | HubSpot Pro — high ROI unlock |
| EVALUATE | 3 | Needs decision from Chief Architect |
| IGNORE | 3 | Out of scope for GC |
| EXTEND (future) | 2 | Phase 3+ |

**Critical Gap:** HubSpot Deal ↔ Houzz Pro Project bridge (HS-19 / HP-01) — zero automation, 100% manual today.
