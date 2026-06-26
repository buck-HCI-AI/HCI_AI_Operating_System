# Unified Search Architecture
**Version:** 1.0 | **Date:** 2026-06-26

---

## Overview

The HCI AI Unified Search Gateway routes queries to the right backend based on detected intent, merges results, scores them, and returns citations and confidence values.

## Architecture

```
User Query
    │
    ▼
SearchGateway.search()
    │
    ├─ _detect_sources(query)
    │       │
    │       ├─ keyword patterns → [vendors, projects, sops, bids, risks]
    │       └─ default → all sources
    │
    ├─ _best_keyword(query)  — extract most useful single token (stops stopwords)
    │
    ├─ Postgres Backends (structured)
    │       ├─ _search_vendors()   → vendors table
    │       ├─ _search_projects()  → projects table
    │       ├─ _search_sops()      → sop_instances + sop_definitions
    │       ├─ _search_bids()      → bid_packages
    │       └─ _search_risks()     → risk_register
    │
    └─ Qdrant Backends (semantic)
            ├─ qdrant_documents
            ├─ qdrant_lessons
            └─ qdrant_costs
    │
    ▼
_normalize_result() — uniform output: {source, score, confidence, text, citation, related_project, payload}
    │
    ▼
Merge + threshold filter (score_threshold=0.3)
    │
    ▼
Sorted results returned
```

## Intent Detection

Source routing is automatic based on keyword patterns in the query:

| Pattern Words | Routes To |
|---|---|
| `vendor`, `sub`, `subcontractor`, `contractor`, `supplier` | vendors |
| `project`, `job`, `site` | projects |
| `sop`, `workflow`, `procedure` | sops |
| `bid`, `proposal`, `estimate`, `cost` | bids, qdrant_costs |
| `risk`, `issue`, `problem` | risks |
| (no match) | all sources |

## Result Schema

Every result — regardless of backend — returns:

```json
{
  "source": "vendors",
  "score": 0.85,
  "confidence": 0.85,
  "text": "Durgin Electric — Electrical",
  "citation": "vendors.id=12",
  "related_project": "1355 Riverside",
  "payload": { ... }
}
```

## Extended Search: Decisions + Lessons

`search_with_decisions()` performs a full search and appends:
- `related_decisions`: matching records from `decision_records`
- `lessons_learned`: semantic Qdrant search over lessons collection

Use `POST /api/v1/platform/search/full` for this extended view.

## API

```
POST /api/v1/platform/search          — unified search (auto-routes by intent)
GET  /api/v1/platform/search/vendors  — vendor name/trade/contact search
GET  /api/v1/platform/search/sops     — SOP instance search by project or number
GET  /api/v1/platform/search/lessons  — semantic lessons learned search (Qdrant)
GET  /api/v1/platform/search/decisions— past decisions for a topic
POST /api/v1/platform/search/full     — search + related decisions + lessons
```

## Keyword Extraction

`_best_keyword(query)` strips stopwords (`a, the, for, in, of, to, at, by, or, and, is, are, with, any`) and returns the first non-stop token. This ensures multi-word queries like `"concrete subcontractor"` produce a useful LIKE match (`%concrete%`) rather than a multi-word string that matches nothing.

## Confidence Scoring

| Source | Confidence Logic |
|---|---|
| Postgres exact match | 0.95 |
| Postgres LIKE match | 0.8 |
| Qdrant semantic | Score from embedding distance |
| Decision records | 0.9 |

Results below `score_threshold` (default 0.3) are filtered out before return.
