# BOOK_00 § 16 — Directive History and Source Artifacts

All source PDFs are in `01_Engineering_Library/`. This appendix records what each directive contributed and where it was consolidated.

---

## Directive Registry

| Directive | PDF | Consolidated Into |
|-----------|-----|-------------------|
| Workflow 00 — AI Collaboration Layer | `Workflow_00_AI_Collaboration_Layer_Directive_for_Claude_Code_v1.pdf` | BOOK_00 §01, AI_TEAM/ structure |
| Infrastructure Phase 1 | (master directive) | BOOK_00 §02, §03, WF-001 through WF-006 |
| Data Architecture and Document Storage | `HCI_AI_Data_Architecture_and_Document_Storage_Master_Directive_for_Claude_Code_v1.pdf` | BOOK_00 §03, §04, database/schema/ |
| Development Storage and Knowledge Ingestion | `HCI_AI_Master_Directive_Development_Storage_and_Knowledge_Ingestion_v1.pdf` | BOOK_00 §04, §05, infrastructure/ |
| API Layer v1 | `HCI_AI_API_Layer_v1_Master_Directive_for_Claude_Code.pdf` | BOOK_00 §06, 03_Source_Code/api/ |
| Construction Intelligence Service Layer | `HCI_AI_Construction_Intelligence_Service_Layer_Master_Directive_for_Claude_Code_v1.pdf` | BOOK_00 §07, 03_Source_Code/services/ |
| Workflow Consolidation and BOOK_00 Implementation | `HCI_AI_Workflow_Consolidation_and_BOOK00_Implementation_Directive_for_Claude_Code_v1.pdf` | This book (BOOK_00 v2), docs/ inventory files |

---

## Architecture Decision Records

ADRs are in `BOOK_00/adr/`. Each records a significant choice, what was considered, and why.

| ADR | Decision |
|-----|----------|
| ADR-0001 | Repository as shared AI memory (not chat history) |
| ADR-0002 (implied) | Python/FastAPI over n8n for intelligence services |
| ADR-0003 (implied) | Self-hosted stack (Postgres + Qdrant + Redis + MinIO) over cloud |
| ADR-0004 (implied) | Claude Haiku for synthesis (fast, cheap vs. Opus quality tradeoff) |
| ADR-0005 (implied) | service.py renamed to {name}_svc.py to prevent Python sys.modules collision |

---

## Key Technical Decisions Recorded

| Decision | Reason | Date |
|----------|--------|------|
| Renamed service.py → {name}_svc.py | Python caches 'service' module name; all 9 services collide | 2026-06-25 |
| resolve_project_id() on BaseIntelligenceService | projects table has no project_number column; short codes match via numeric prefix | 2026-06-25 |
| importlib loading for service routes | Prevents sys.modules collision when 9 services have same-named modules | 2026-06-25 |
| HubSpot write rule | Never auto-update; always ask Buck first | 2026-06-20 |
| .command files on Desktop | Buck can't easily use Terminal; double-click is the interface | 2026-06-22 |
| bid_entries.vendor_id = NULL | Bids were imported from notes text; FK not populated during initial sync | 2026-06-25 |

---

## Legacy Locations (Superseded)

These files/folders existed before BOOK_00 consolidation. Their content is now in BOOK_00. Do not add new specs to these locations:

| Old Location | Content Moved To |
|-------------|-----------------|
| `architecture/DATA_ARCHITECTURE.md` | BOOK_00 §03 |
| `architecture/DOCUMENT_INTELLIGENCE_ARCHITECTURE.md` | BOOK_00 §05 |
| `BOOK_00/architecture/CURRENT_ARCHITECTURE.md` | BOOK_00 §02, AI_TEAM/04_ARCHITECTURE.md |
| `workflows/WORKFLOW_01_DOCUMENT_INGESTION.md` | BOOK_00 §05, §09 |
| `workflows/WORKFLOW_02_REGISTRY_WRITEBACK.md` | BOOK_00 §09 |
| `BOOK_00/workflows/WORKFLOW_00_AI_COLLABORATION_LAYER.md` | BOOK_00 §01 |
| `docs/API_LAYER_v1.md` | BOOK_00 §06 |
| `docs/CONSTRUCTION_INTELLIGENCE_SERVICE_LAYER_v1.md` | BOOK_00 §07 |
| `docs/KNOWLEDGE_INGESTION_ENGINE_v1.md` | BOOK_00 §05 |
| `docs/STORAGE_LAYER_CONFIGURATION_v1.md` | BOOK_00 §04 |
