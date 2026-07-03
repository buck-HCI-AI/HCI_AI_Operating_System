# HOUZZ_EXTRACTION_BACKLOG.md
## HCI AI Operating System — Houzz Full-Project Extraction

**Status:** FUTURE SCOPE — not in active sprint
**Directive:** Chief Architect Directive 2026-06-27
**Authorized by:** Buck Adams (PM & SS, Hendrickson Construction; HCI-AI Owner) | HCI Chief Architect
**Sprint Target:** Sprint 5+ (pending architecture review)

---

## Architecture Decision

**Browser Claude = Extractor only. Mining Engine = Analyzer only.**

No intelligence generation in the browser layer. Raw extraction into PostgreSQL only.
All analysis, pattern detection, and intelligence synthesis runs via the Mining Engine post-extraction.

---

## Scope: Full Houzz Project Extraction

### Data Categories to Extract (per project)

| Category | Tables | Notes |
|---|---|---|
| Projects | `houzz_projects` | All accessible projects, not just active 3 |
| Daily Logs | `houzz_daily_logs` | All available logs — no date limit |
| Photos | `houzz_photos` | Metadata + file references; vision AI in Mining Engine |
| Schedules | `houzz_schedule_items` | All items, statuses, dates |
| Tasks | `houzz_tasks` | Open and completed |
| Files | `houzz_files` | Document references and metadata |
| Selections | `houzz_selections` | Product/material selections per project |
| Bids & Estimates | `houzz_bids` | Vendor bids submitted via Houzz |
| Invoices | `houzz_invoices` | Invoice records |
| Change Orders | `houzz_change_orders` | All CO history |
| Punch Lists | `houzz_punch_list_items` | Open and closed items |
| Warranties | `houzz_warranties` | Product and labor warranties |
| Expenses | `houzz_expenses` | Project expense records |
| Time Entries | `houzz_time_entries` | Labor time logs |
| Contacts | `houzz_contacts` | Project-specific contacts |
| Messages | `houzz_messages` | Where accessible/permitted |

### Project Scope

- All accessible Houzz projects (not limited to Gate 5 Pilot 3)
- Current pilot: 64 Eastwood, 101 Francis, 1355 Riverside
- Future: any additional projects as they are added

---

## Implementation Plan

### Phase 1: Schema Design
- [ ] Design PostgreSQL schema for all 15+ houzz tables
- [ ] Migration file: `05_Database/migrations/houzz_full_schema.sql`
- [ ] Apply migration + seed test records

### Phase 2: Browser Claude Extraction
- [ ] Browser Claude logs into Houzz Pro
- [ ] Discovers all accessible projects
- [ ] Extracts all data categories above
- [ ] Writes directly to PostgreSQL (no intelligence generation)
- [ ] Reports row counts per table per project
- [ ] Read-only in Houzz — zero writes to Houzz

### Phase 3: Mining Engine Activation
- [ ] HouzzMiner updated to process all 15+ tables
- [ ] Photo intelligence via vision AI (Claude Haiku)
- [ ] Schedule variance detection
- [ ] Punch list trend analysis
- [ ] Change order pattern recognition
- [ ] Cost vs budget analysis (tie to historical_cost_records)

### Phase 4: Intelligence Output
- [ ] Daily project health artifacts (7 per project per day)
- [ ] Portfolio roll-up via ExecutiveAggregator
- [ ] HubSpot project status writeback (Gate HZ-H1)
- [ ] Drive daily intelligence filing

---

## Gate Requirements Before Starting

- [ ] Buck authorizes full Houzz extraction scope
- [ ] Schema migration reviewed by ChatGPT Architecture Review
- [ ] Browser Claude briefed with updated directive (all 15+ categories)
- [ ] Dedicated extraction session scheduled (not during active pilot work)

---

## Current State (2026-06-27)

- Browser Claude paused per Chief Architect Directive 2026-06-27
- Partial extraction attempted — all three Houzz tables still empty (0 rows)
- `Browser_Houzz_Directive.txt` on Desktop preserved for reference
- HouzzMiner framework built and functional — awaiting data
- HZ-004 n8n trigger deactivated pending full extraction scope approval

---

## Related Tasks

| Task ID | Task | Status |
|---|---|---|
| HZ-001 | Houzz Daily Log Reader (Manual extraction test) | 🚫 Deferred — superseded by full extraction scope |
| HZ-003 | Register Houzz in Integration Registry | ✅ Done 2026-06-27 (status: pending_data) |
| HZ-004 | n8n daily log extraction trigger | ⏸ Paused — deactivated per Chief Architect Directive |
| HZ-FULL-001 | Full Houzz schema design (15+ tables) | Future |
| HZ-FULL-002 | Browser Claude full extraction run | Future |
| HZ-FULL-003 | HouzzMiner full intelligence sweep | Future |

---

*HOUZZ_EXTRACTION_BACKLOG.md | HCI AI Operating System | Hendrickson Construction, Inc.*
*Authority: Chief Architect Directive 2026-06-27 | HCI-AI Owner: Buck Adams*
