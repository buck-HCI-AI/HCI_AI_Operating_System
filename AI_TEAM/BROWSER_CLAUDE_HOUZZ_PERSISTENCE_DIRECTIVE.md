# Browser Claude Directive — Houzz Persistence Bridge
**Date:** 2026-06-27  
**From:** Claude Code (Lead Implementation Engineer)  
**To:** Browser Claude  
**Authority:** Chief Architect Directive — "This is a significant milestone" (2026-06-27)

---

## What Changed

The HCI backend now has a **Houzz ingestion endpoint**. Instead of holding extracted data in memory, you MUST POST it to this endpoint immediately after extraction. The endpoint is idempotent — you can re-post the same data safely.

---

## The Endpoint

```
POST http://localhost:8000/api/v1/services/houzz/ingest
Header: X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
Header: Content-Type: application/json
```

> **NOTE:** The API key changed. Old key is revoked. Use the key above.

---

## Payload Format

```json
{
  "source": "browser_claude",
  "extraction_notes": "101 Francis — Schedule module, extracted 2026-06-27",
  "projects": [
    {
      "houzz_project_id": "houzz-internal-id",
      "name": "101 Francis",
      "client_name": "HCI",
      "status": "active",
      "address": "101 Francis St",
      "project_type": "Full Interior Remodel"
    }
  ],
  "daily_logs": [
    {
      "houzz_log_id": "unique-log-id-from-houzz",
      "project_id": "houzz-internal-id",
      "log_date": "2026-06-15",
      "content": "Full text of the daily log entry",
      "author": "Buck Adams",
      "crew_size": 5,
      "weather": "Sunny, 75°F"
    }
  ],
  "schedule_items": [
    {
      "houzz_item_id": "unique-item-id-from-houzz",
      "project_id": "houzz-internal-id",
      "title": "Rough Framing",
      "start_date": "2026-06-10",
      "end_date": "2026-06-20",
      "status": "complete",
      "completion_pct": 100.0,
      "task_type": "framing",
      "parent_item_id": null,
      "assignee": null,
      "notes": null
    }
  ]
}
```

---

## Rules

1. **POST after every extraction batch** — do not hold data in memory.
2. **Use the actual Houzz-internal IDs** for `houzz_project_id`, `houzz_log_id`, `houzz_item_id`. If Houzz doesn't expose IDs in the UI, construct a deterministic one: `"{project_slug}-log-{date}"` or `"{project_slug}-sched-{title_slug}"`.
3. **project_id in logs/items must match houzz_project_id in projects** — post projects first, or include them in the same payload.
4. **Dates must be YYYY-MM-DD format.**
5. **Re-posting duplicates is safe** — the endpoint upserts and returns duplicate counts.

---

## Expected Response

```json
{
  "status": "ok",
  "total_imported": 30,
  "imported": {
    "projects": {"attempted": 1, "imported": 1, "skipped": 0, "duplicate": 0},
    "daily_logs": {"attempted": 29, "imported": 29, "skipped": 0, "duplicate": 0},
    "schedule_items": {"attempted": 65, "imported": 65, "skipped": 0, "duplicate": 0}
  },
  "validation_errors": []
}
```

If `validation_errors` is non-empty, fix the issues and re-post. If `status` is `"partial"`, some records failed — check `validation_errors` for details.

---

## Check Status After Posting

```
GET http://localhost:8000/api/v1/services/houzz/status
Header: X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
```

Returns row counts per table. You should see non-zero counts after successful ingestion.

---

## Extraction Status (as of 2026-06-27)

| Project | Daily Logs Found | Schedule Items Found | Persisted? |
|---|---|---|---|
| 101 Francis | 29 | 36 | ❌ NOT YET — extract + POST |
| 1355 Riverside | 0 found | — | — |
| 64 Eastwood | NOT IN HOUZZ | — | — |

**Priority:** Extract 101 Francis daily logs and schedule items and POST to the ingest endpoint.

## Known Houzz Project ID (from previous extraction)

The real Houzz project ID for 101 Francis is: **`3218059`**

Use this in your POST payload:
```json
{
  "projects": [
    {
      "houzz_project_id": "3218059",
      "name": "101 Francis",
      "client_name": "Adnan Rawjee",
      "status": "open",
      "address": "101 W Francis St, Aspen, CO 81611",
      "project_type": "Full Interior Remodel"
    }
  ],
  "daily_logs": [ ... use "project_id": "3218059" on each log ... ],
  "schedule_items": [ ... use "project_id": "3218059" on each item ... ]
}
```

**Expected response after successful POST:**
```json
{
  "status": "ok",
  "total_imported": 66,
  "imported": {
    "projects":       {"attempted": 1, "imported": 1},
    "daily_logs":     {"attempted": 29, "imported": 29},
    "schedule_items": {"attempted": 36, "imported": 36}
  }
}
```

After posting, confirm counts at:
`GET http://localhost:8000/api/v1/services/houzz/status`

---

## Architecture (for context)

- **You (Browser Claude):** Extractor only — browse Houzz, collect data, POST to endpoint.
- **Ingestion endpoint:** Validates, upserts to houzz_* tables.
- **HouzzMiner:** Analyzer only — reads from houzz_* tables (already populated) and generates intelligence.
- **You never write directly to the database.** Always go through the endpoint.

---

*Directive issued by Claude Code | HCI AI Operating System | Hendrickson Construction, Inc.*
