# HCI Automation Opportunity Catalog
**Generated:** 2026-06-27 | **Sources:** HCI-BH-HP-001, HCI-BH-HS-001

---

## Prioritized Build Queue

### P0 — Critical Integration (Build Now)
| ID | Opportunity | System | Complexity | Blocker |
|---|---|---|---|---|
| AO-HP-001 | HubSpot Deal (ROM Accepted) → Houzz Pro Project auto-create | Houzz↔HubSpot | MEDIUM | Houzz API investigation needed |
| AO-HP-002 | Houzz Lead Connected → HubSpot Contact sync (via Zapier) | Houzz↔HubSpot | MEDIUM | Configure Zapier |

### P1 — COI Automation (Ready to Build)
| ID | Opportunity | System | Complexity | Notes |
|---|---|---|---|---|
| AO-HS-001 | COI Expiration daily auto-update (coi_status field) | HubSpot | LOW | n8n cron comparing coi_expiration_date to today |
| AO-HS-002 | COI Renewal email 30 days before expiry | HubSpot | LOW | Requires AO-HS-001 first |
| AO-HS-005 | COI Submission HubSpot form → auto-update company fields | HubSpot | LOW | HubSpot Forms (available in Starter) |

### P1 — Pipeline Visibility (Ready to Build)
| ID | Opportunity | System | Complexity | Notes |
|---|---|---|---|---|
| AO-HS-008 | 4 Pipeline Dashboards (Pipeline Overview, Sub Vendor, Bidding Activity, COI Compliance) | HubSpot | LOW | Native HubSpot dashboard builder |
| AO-HS-004 | Bid Invitation Auto-Task on Sent Out stage | HubSpot | LOW | n8n poll → create tasks on all associated contacts |

### P1 — AI Intelligence (Ready to Build)
| ID | Opportunity | System | Complexity | Notes |
|---|---|---|---|---|
| AO-HS-010 | AI Deal Summarization (n8n fetches engagements, Claude API generates briefing) | HubSpot + Claude | MEDIUM | Integrate with HCI AI API /services/bid-intelligence |

### P2 — Houzz Financial Automation (Ready to Build)
| ID | Opportunity | System | Complexity | Notes |
|---|---|---|---|---|
| AO-HP-006 | Milestone-Based Auto-Invoicing | Houzz | MEDIUM | Define milestone triggers per project type |
| AO-HP-008 | Selection Reminder Cadence (weekly) | Houzz | LOW | n8n weekly scan of Selections Tracker |
| AO-HP-011 | Project Folder Template Auto-Create | Houzz | LOW | Trigger on project creation |
| AO-HP-013 | Client Dashboard Auto-Share at Contract Signing | Houzz | LOW | Trigger on contract status change |
| AO-HP-014 | Sub Dashboard Activation when PO issued | Houzz | LOW | Trigger on PO creation |
| AO-HP-005 | Estimate Total Sync to HubSpot Deal Amount | Houzz↔HubSpot | LOW | Read Houzz estimate, PATCH HubSpot deal amount |
| AO-HP-003 | AI Lead Response (5-min auto-reply to new Houzz leads) | Houzz | MEDIUM | Zapier + Claude API |

### P2 — Project Data (Ready to Configure)
| ID | Opportunity | System | Complexity | Notes |
|---|---|---|---|---|
| AO-HP-010 | QuickBooks Online Sync | Houzz↔QBO | LOW | Native Houzz Pro integration — flip the switch |
| AO-HP-012 | Schedule Phase Templates (Remodel 8-phase, Ground-Up 12-phase) | Houzz | MEDIUM | One-time build of template libraries |

### Future Phase (Buck-Gated or Pending API)
| ID | Opportunity | System | Status |
|---|---|---|---|
| AO-HP-004 | Contract Auto-Generate from HubSpot Deal Stage | Houzz | PENDING_HOUZZ_API |
| AO-HP-007 | Change Order AI Drafting from Daily Log Flags | Houzz | FUTURE_PHASE |
| AO-HP-009 | AI Punchlist Generation from 30-Day Daily Logs | Houzz | FUTURE_PHASE |
| AO-HS-003 | HubSpot Deal Stage → Houzz Pro Project Bridge (programmatic) | HubSpot | PENDING_HOUZZ_API |
| AO-HS-006 | Webhook Event-Driven Architecture | HubSpot | PENDING_UPGRADE |
| AO-HS-009 | ROM Quote Automation | HubSpot | FUTURE_PHASE |

### Executive Decision Required
| ID | Opportunity | Cost | Unlocks |
|---|---|---|---|
| AO-HS-007 | Sales Hub Professional Upgrade | ~$70/mo incremental | Workflows, Sequences, Webhooks (AO-HS-006) |

---

## P0 Gap Summary
| Gap | Impact |
|---|---|
| No Houzz ↔ HubSpot integration | Every project requires dual manual entry; data drifts between systems |
| 303 area homeowners not captured | Revenue leakage from unconverted Houzz inbound leads |
| COI Status not automated | Expired subs may appear active — compliance risk |
| No schedules built in Houzz | Zero project timeline visibility for any of 24 active projects |
| Zero pipeline dashboards | Leadership has no real-time visibility into bid or project pipeline |

---

## Integration Architecture Notes
- **Zapier BETA** is available in Houzz Pro settings — enables Houzz Lead → HubSpot Contact flow (AO-HP-002) today, before API
- **n8n Construction OS** (HubSpot Private App 43234028) already has contacts+companies+deals read/write — can drive AO-HS-001, AO-HS-004, AO-HS-010 immediately
- **Houzz API** status unknown — AO-HP-001/003/004 depend on whether Houzz Pro exposes a project creation API
- **QuickBooks** requires only connecting the native Houzz Pro integration in /settings/quickbooks

---

## Next Recommended Build Sequence
1. AO-HS-001 + AO-HS-002: COI auto-update + renewal email (1 n8n workflow, no blockers)
2. AO-HS-008: 4 HubSpot dashboards (native HubSpot, no code, 1 hour)
3. AO-HS-004: Bid invitation task auto-creation on Sent Out (1 n8n workflow)
4. AO-HS-010: AI deal summarization (n8n + Claude API, leverages existing /services/bid-intelligence)
5. AO-HP-002: Houzz Lead → HubSpot Contact via Zapier (requires Buck to configure Zapier)
6. AO-HP-010: QuickBooks connect (requires Buck to flip switch in Houzz settings)
7. AO-HP-001: HubSpot → Houzz Pro project bridge (requires Houzz API investigation first)
