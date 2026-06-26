# Live Pilot Project Matrix

**Sprint:** MVP Sprint 1  
**Status:** Active — 3 pilots configured  

---

## Pilot Project Registry

| Code  | Project        | DB ID | HubSpot Deal  | Drive Folder                    | Houzz ID        |
|-------|----------------|-------|---------------|---------------------------------|-----------------|
| 64EW  | 64 Eastwood    | 1     | 332246098523  | HCI AI - Master /64 Eastwood    | 64-eastwood     |
| 101F  | 101 Francis    | 2     | 332313009897  | HCI AI - Master /101 Francis    | 101-francis     |
| 1355R | 1355 Riverside | 3     | 1355-riverside| HCI AI - Master /1355 Riverside | 1355-riverside  |

---

## Workflow Enablement Matrix

| Workflow                   | 64EW | 101F | 1355R | Mode     |
|----------------------------|------|------|-------|----------|
| Project Brain Init         | ✅   | ✅   | ✅    | Read     |
| Bid Management             | ✅   | ✅   | ✅    | Dry-run  |
| Daily Log / Field Intel    | ✅   | ✅   | ✅    | Dry-run  |
| PM Weekly Review           | ✅   | ✅   | ✅    | Read     |
| Schedule/Status Intel      | ✅   | ✅   | ✅    | Read     |
| Executive Reporting        | ✅   | ✅   | ✅    | Read     |

All write workflows are in dry-run mode pending Gate 5 go-live approval.

---

## Connector Registry (per pilot)

Each pilot project has 3 registered connectors:

| Project | Source         | Status     | Read-Only |
|---------|---------------|------------|-----------|
| 64EW    | hubspot        | registered | TRUE      |
| 64EW    | google_drive   | registered | TRUE      |
| 64EW    | houzz          | registered | TRUE      |
| 101F    | hubspot        | registered | TRUE      |
| 101F    | google_drive   | registered | TRUE      |
| 101F    | houzz          | registered | TRUE      |
| 1355R   | hubspot        | registered | TRUE      |
| 1355R   | google_drive   | registered | TRUE      |
| 1355R   | houzz          | registered | TRUE      |

Write access requires explicit Buck approval per connector per project.

---

## Gate 5 Pilot Dates

- Pilot window: 2026-06-25 → 2026-07-01
- Go-live authorization: Pending
- Projects: 101 Francis, 64 Eastwood, 1355 Riverside

---

## Project Role Definitions

**64 Eastwood:** Historical reference. Used to validate intelligence extraction against known project data. Completed or near-complete — no new field data expected.

**101 Francis:** Active PM / bid / daily ops pilot. Primary test bed for Bid Management and Daily Log workflows.

**1355 Riverside:** Primary advanced pilot. All 6 workflows exercised. Highest priority for go-live authorization.
