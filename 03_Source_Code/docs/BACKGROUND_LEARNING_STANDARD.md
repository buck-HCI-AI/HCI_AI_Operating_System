# Background Learning Standard

**Service:** `services/background_learning/background_learning_service.py`  
**API prefix:** `/api/v1/services/background-learning/`  
**Mode:** Read-only at all times  

---

## Purpose

Automatically discover, classify, and index documents from external sources (Drive, HubSpot, Houzz, Outlook) into the Project Brain — without ever writing back to the source systems or executing any changes without Buck approval.

---

## Pipeline Statuses (13)

```
Discovered
  └─ Access Confirmed
      └─ Indexed
          └─ Classified
              └─ Extracted
                  └─ Embedded
                      └─ Linked to Project Brain
                          └─ Intelligence Candidate Created
                              └─ Human Review Needed
                                  ├─ Approved
                                  ├─ Rejected
                                  └─ Archived
Error (any stage)
```

---

## Source Systems

| System        | Discovery Method              | Table Read            |
|---------------|-------------------------------|-----------------------|
| `hubspot`     | `discover_from_hubspot()`     | `hubspot_deals`       |
| `google_drive`| `discover_from_drive()`       | `drive_sync_log`      |
| `houzz`       | `discover_from_houzz()`       | `houzz_projects`      |
| `outlook`     | Manual `discover()` calls     | (not yet automated)   |

---

## Document Type Classification

Keywords matched against source name (case-insensitive):

| Type        | Keywords                                           |
|-------------|----------------------------------------------------|
| drawing     | drawing, dwg, plan, floor plan, elevation, section |
| spec        | spec, specification, division, csi                 |
| bid         | bid, proposal, quote, pricing, estimate            |
| budget      | budget, cost, gcmax, allowance, contingency        |
| schedule    | schedule, gantt, timeline, milestone               |
| meeting     | meeting, minutes, agenda, preconstruction, oac     |
| photo       | photo, image, jpg, jpeg, png                       |
| rfi         | rfi, request for information                       |
| submittal   | submittal, shop drawing, product data              |
| contract    | contract, agreement, subcontract                   |
| closeout    | closeout, punch list, warranty, as-built           |
| daily_log   | daily log, field report                            |
| other       | (default)                                          |

---

## Project Inference

Auto-infers project from source name and URL:

| Keywords                         | Project        | Confidence |
|----------------------------------|----------------|------------|
| eastwood, 64ew                   | 64 Eastwood    | 0.85       |
| francis, 101f, 101 w             | 101 Francis    | 0.85       |
| riverside, 1355                  | 1355 Riverside | 0.85       |
| sagebrusch, 83sb                 | 83 Sagebrusch  | 0.70       |
| (no match)                       | None           | 0.30       |

---

## API Endpoints

| Method | Path                                    | Description                        |
|--------|-----------------------------------------|------------------------------------|
| GET    | `/services/background-learning/`        | Service info                       |
| POST   | `/services/background-learning/discover`| Register one item                  |
| POST   | `/services/background-learning/discover/hubspot` | Bulk HubSpot discovery  |
| POST   | `/services/background-learning/discover/drive`   | Bulk Drive discovery    |
| POST   | `/services/background-learning/discover/houzz`   | Bulk Houzz discovery    |
| POST   | `/services/background-learning/discover/all`     | Run all sources         |
| GET    | `/services/background-learning/records` | Query records (filterable)         |
| POST   | `/services/background-learning/records/{id}/advance` | Advance pipeline status |
| POST   | `/services/background-learning/records/{id}/classify` | Auto-classify and advance |
| GET    | `/services/background-learning/summary` | Status counts                      |

---

## Safety Rules

- Never modifies, deletes, renames, moves, or writes back to any source system
- All intelligence candidates that trigger write actions go to `approval_queue`
- `review_status='Pending'` means Buck has not seen this item yet
- `confidence < 0.5` items require higher scrutiny before approval
