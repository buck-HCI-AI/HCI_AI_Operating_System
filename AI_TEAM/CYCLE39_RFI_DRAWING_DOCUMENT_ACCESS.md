# CYCLE 39 — RFI & Drawing Document Access
**GBT Cycle:** 39
**Sprint:** 8
**Priority:** P1 — Field Operations Blocker
**Status:** SPEC — Pending Code Implementation
**Date:** 2026-07-02
**Author:** Browser Claude (BC)

---

## Problem Statement

Field GPT (HCI Field GPT) can connect to project brain data but cannot access RFI logs, RFI PDFs, drawing sheet references, or architect responses. This was confirmed by Buck from the desktop session on 1355 Riverside (1355R).

Current gateway has NO /rfis or /drawings endpoints. Field GPT cannot complete RFI reviews — a core superintendent workflow.

**Reported gap (verbatim from field):**
- Architect RFI log: NOT accessible
- RFI PDFs: NOT accessible
- Drawing sheet numbers and detail references: NOT accessible
- Architect responses: NOT accessible
- Drawing revisions showing resolved questions: NOT accessible

---

## Architecture Decision

**ADR-S8-001: Document Access Pattern (existing)**
- Field GPT accesses RFI/drawing documents via gateway ONLY — never direct Drive API
- All document metadata stored in DB; file content via signed URL from gateway
- Gateway acts as single access control layer

---

## Endpoints Required

### 1. GET /gateway/project/{code}/rfis
Returns all RFIs for a project with status and response summary.

**Response shape:**
```json
{
  "project_code": "1355R",
    "rfi_count": 3,
      "rfis": [
          {
                "rfi_id": "RFI-001",
                      "subject": "Axis B framing conflict",
                            "status": "open",
                                  "submitted_date": "2026-06-28",
                                        "due_date": "2026-07-05",
                                              "drawing_reference": "A2.1",
                                                    "detail_reference": "3/A2.1",
                                                          "spec_section": "06100",
                                                                "architect_response": null,
                                                                      "response_date": null,
                                                                            "resolved_by_revision": null
                                                                                }
                                                                                  ]
                                                                                  }
                                                                                  ```

                                                                                  ### 2. GET /gateway/project/{code}/rfis/{rfi_id}
                                                                                  Single RFI detail with full context and document link.

                                                                                  **Response includes:**
                                                                                  - Full RFI text
                                                                                  - Drawing sheet reference
                                                                                  - Architect response (if received)
                                                                                  - Signed URL to RFI PDF (if stored in Drive/MinIO)
                                                                                  - Whether resolved by later drawing revision

                                                                                  ### 3. GET /gateway/project/{code}/drawings
                                                                                  Drawing log — sheet list with revision tracking.

                                                                                  **Response shape:**
                                                                                  ```json
                                                                                  {
                                                                                    "project_code": "1355R",
                                                                                      "drawing_count": 48,
                                                                                        "drawings": [
                                                                                            {
                                                                                                  "sheet": "A2.1",
                                                                                                        "title": "Floor Plan - Level 1",
                                                                                                              "current_revision": "C",
                                                                                                                    "revision_date": "2026-06-15",
                                                                                                                          "open_rfis": ["RFI-001"],
                                                                                                                                "notes": null
                                                                                                                                    }
                                                                                                                                      ]
                                                                                                                                      }
                                                                                                                                      ```
                                                                                                                                      
                                                                                                                                      ### 4. GET /gateway/project/{code}/drawings/{sheet}
                                                                                                                                      Single drawing detail — revision history + linked RFIs.
                                                                                                                                      
                                                                                                                                      ---
                                                                                                                                      
                                                                                                                                      ## Database Tables Required
                                                                                                                                      
                                                                                                                                      If not already present, Code to create:
                                                                                                                                      
                                                                                                                                      ```sql
                                                                                                                                      CREATE TABLE rfis (
                                                                                                                                        id SERIAL PRIMARY KEY,
                                                                                                                                          project_id INTEGER REFERENCES projects(id),
                                                                                                                                            rfi_number VARCHAR(20) NOT NULL,
                                                                                                                                              subject TEXT NOT NULL,
                                                                                                                                                status VARCHAR(20) DEFAULT 'open',
                                                                                                                                                  submitted_date DATE,
                                                                                                                                                    due_date DATE,
                                                                                                                                                      drawing_reference VARCHAR(50),
                                                                                                                                                        detail_reference VARCHAR(50),
                                                                                                                                                          spec_section VARCHAR(20),
                                                                                                                                                            body TEXT,
                                                                                                                                                              architect_response TEXT,
                                                                                                                                                                response_date DATE,
                                                                                                                                                                  resolved_by_revision VARCHAR(10),
                                                                                                                                                                    drive_file_id VARCHAR(255),
                                                                                                                                                                      created_at TIMESTAMPTZ DEFAULT NOW(),
                                                                                                                                                                        updated_at TIMESTAMPTZ DEFAULT NOW()
                                                                                                                                                                        );
                                                                                                                                                                        
                                                                                                                                                                        CREATE TABLE drawings (
                                                                                                                                                                          id SERIAL PRIMARY KEY,
                                                                                                                                                                            project_id INTEGER REFERENCES projects(id),
                                                                                                                                                                              sheet VARCHAR(20) NOT NULL,
                                                                                                                                                                                title TEXT,
                                                                                                                                                                                  current_revision VARCHAR(10),
                                                                                                                                                                                    revision_date DATE,
                                                                                                                                                                                      discipline VARCHAR(20),
                                                                                                                                                                                        drive_file_id VARCHAR(255),
                                                                                                                                                                                          created_at TIMESTAMPTZ DEFAULT NOW(),
                                                                                                                                                                                            updated_at TIMESTAMPTZ DEFAULT NOW()
                                                                                                                                                                                            );
                                                                                                                                                                                            ```
                                                                                                                                                                                            
                                                                                                                                                                                            ---
                                                                                                                                                                                            
                                                                                                                                                                                            ## GPT Integration
                                                                                                                                                                                            
                                                                                                                                                                                            Once live, add to HCI Field GPT Actions schema:
                                                                                                                                                                                            - `getProjectRFIs` -> GET /gateway/project/{code}/rfis
                                                                                                                                                                                            - `getProjectRFIDetail` -> GET /gateway/project/{code}/rfis/{rfi_id}
                                                                                                                                                                                            - `getProjectDrawings` -> GET /gateway/project/{code}/drawings
                                                                                                                                                                                            - `getProjectDrawingDetail` -> GET /gateway/project/{code}/drawings/{sheet}
                                                                                                                                                                                            
                                                                                                                                                                                            ---
                                                                                                                                                                                            
                                                                                                                                                                                            ## Success Criteria
                                                                                                                                                                                            
                                                                                                                                                                                            - [ ] GET /gateway/project/1355R/rfis returns RFI-001 with architect status
                                                                                                                                                                                            - [ ] Field GPT can answer: "What is the status of RFI-001 on 1355 Riverside?"
                                                                                                                                                                                            - [ ] Drawing sheet cross-reference works (A2.1 -> linked RFIs)
                                                                                                                                                                                            - [ ] 109/109 existing tests still pass
                                                                                                                                                                                            - [ ] ADR-S8-001 respected: no direct Drive API calls from GPT
                                                                                                                                                                                            
                                                                                                                                                                                            ---
                                                                                                                                                                                            
                                                                                                                                                                                            ## Directive Reference
                                                                                                                                                                                            
                                                                                                                                                                                            - Gateway directive posted: request_id f8e2b1ab
                                                                                                                                                                                            - Related: CYCLE37_SPRINT8_PREVIEW.md, CYCLE38_COMPANY_WIDE_REPORTING.md
                                                                                                                                                                                            - ADR: ADR-S8-001 (Document Access Pattern)
                                                                                                                                                                                            - Code channel: Post implementation report to ai_messages when complete
                                                                                                                                                                                            
                                                                                                                                                                                            ---
                                                                                                                                                                                            
                                                                                                                                                                                            *Generated by Browser Claude - 2026-07-02 - Per never-stop directive*
