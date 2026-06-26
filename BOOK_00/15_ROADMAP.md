# BOOK_00 § 15 — Roadmap and Implementation Status

**Last Updated:** 2026-06-25

---

## Phase Status

| Phase | Description | Status | Completion |
|-------|-------------|--------|-----------|
| 1 | AI_TEAM + repository collaboration layer | ✅ Complete | 2026-06-20 |
| 2 | Infrastructure: PostgreSQL, Redis, MinIO, Qdrant | ✅ Complete | 2026-06-21 |
| 3 | Storage: HCI_AI_DEV drive + launchd | ✅ Complete | 2026-06-22 |
| 4 | Data architecture + schema | ✅ Complete | 2026-06-22 |
| 5 | Knowledge ingestion + document intelligence | ✅ Partial | Pipeline built; ingest endpoint needs wiring |
| 6 | API Layer v1 | ✅ Complete | 2026-06-23 |
| 7 | Construction Intelligence Service Layer | ✅ Complete | 2026-06-25 |
| 8 | Workflow Engine core | 🔜 Next | — |
| 9 | PM, Superintendent, Field workflows | 🔜 After 8 | — |
| 10 | Reporting and Dashboards | 🔜 After 9 | — |
| 11 | Production hardening + Mac mini | 🔜 After 10 | — |

---

## Phase 8 Checklist

| Item | Description | Priority |
|------|-------------|----------|
| 8.1 | Fix vendor_id FK on bid_entries | P0 |
| 8.2 | Wire document-intelligence/ingest to pipeline | P0 |
| 8.3 | Create workflow_events table | P1 |
| 8.4 | Workflow registry endpoint | P1 |

---

## Phase 9 Checklist

| Item | Description | Priority | Dependency |
|------|-------------|----------|-----------|
| 9.1 | Superintendent Workflow (WF-SUPER) | P0 | Phase 8 complete |
| 9.2 | Schedule Intelligence tie-in (WF-SCHED) | P0 | 9.1 |
| 9.3 | PM Workflow (WF-PM) | P1 | 9.1, 9.2 |
| 9.4 | Bid email → bid_entries pipeline | P1 | 8.1 |
| 9.5 | RFI / Submittal workflow | P2 | 9.3 |

---

## Intelligence Service Activation Status

| Service | Status | Needs |
|---------|--------|-------|
| Project Brain | ✅ Active | More data (meetings, daily logs) |
| Bid Intelligence | ✅ Active | vendor_id FK populated (Phase 8.1) |
| Vendor Intelligence | ✅ Active | Stable |
| Document Intelligence | ✅ Active | Ingest endpoint wiring (Phase 8.2) |
| Lessons Learned | ✅ Active | More lessons added over time |
| Procurement | ✅ Active | Data entry (via WF-PM) |
| Historical Cost | ✅ Active | Data entry (via WF-PM post-project) |
| Risk Intelligence | ✅ Active | Data from WF-SUPER (Phase 9.1) |
| Schedule Intelligence | ⚠️ Partial | WF-SUPER data (Phase 9.1) + baseline |

---

## Data Gaps to Fill

| Gap | Impact | Resolution |
|-----|--------|-----------|
| vendor_id NULL on bid_entries | Vendor Intelligence can't cross-ref bids | Phase 8.1 |
| 0 daily logs | Schedule, Risk, Project Brain starved of field data | Phase 9.1 WF-SUPER |
| 0 meetings | Project Brain has no meeting intelligence | WF-002 use + Teams integration |
| WF-007 reads Sheets not Postgres | Bid data in two places | Phase 9.4 |
| ingest endpoint stub | Document Intelligence can't ingest | Phase 8.2 |

---

## Workflow Build Sequence

```
8.1 vendor_id fix ──────────────────────────────────────────────────────┐
8.2 ingest endpoint ────────────────────────────────────────────────────┤
8.3 workflow_events table ──────────────────────────────────────────────┤
8.4 workflow registry ──────────────────────────────────────────────────┘
                                                                         ↓
                                              9.1 WF-SUPER (daily logs + field)
                                                                         ↓
                                              9.2 Schedule tie-in (variance detection)
                                                                         ↓
                                              9.3 WF-PM (daily PM review + weekly report)
                                                                         ↓
                                              9.4 Bid email → bid_entries pipeline
                                                                         ↓
                                              10  Reporting + Dashboard
                                                                         ↓
                                              11  Mac mini + production hardening
```
