# CYCLE9_GBT_GEMINI_N8N_WORKFLOW — WF-PLAN-001
## Date: 2026-07-01 | Cycle: 9 Part 2 of 3 | Source: GBT Chief Architect

## Design Principle
This workflow deliberately limits Gemini's role.
Gemini is NOT the plan engine. Gemini is the first-pass reviewer.
It may only: summarize, classify, identify possible issues, draft observations.
It must NOT: calculate quantities, extract dimensions as authoritative,
perform takeoffs, determine code compliance, compare other sheets,
perform cross-sheet references, interpret schedules as authoritative,
create official RFIs, make engineering decisions, infer missing info.
If uncertain: say UNKNOWN. Return ONLY valid JSON.

---

## Trigger
Runs after: POST /plans/ingest (background task completes PDF storage)

---

## n8n Workflow: WF-PLAN-001

```
PDF Uploaded
  |
  v
Node 1: Webhook / Gateway Trigger
  Receives: plan_document_id, storage_path
  |
  v
Node 2: Read PDF Binary
  Read file from /tmp/hci_plan_uploads/
  |
  v
Node 3: Render Pages (PyMuPDF HTTP service)
  POST http://localhost:8001/render
  Input: { pdf_path, dpi: 150 }
  Output: [{ page: 1, image: "base64..." }, ...]
  |
  v
Node 4: Split in Batches
  One page at a time.
  Never send an entire drawing set.
  |
  v
Node 5: Gemini HTTP Request
  POST https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent
  Authorization: Bearer {{GEMINI_API_KEY}}
  |
  v
Node 6: JSON Validator
  Reject if: invalid JSON, missing required sections, hallucinated fields
  Retry once.
  |
  v
Node 7: Aggregate Results
  Collect all per-page JSON into array
  |
  v
Node 8: Build Drawing Index
  Map each page result to drawing_index_entry
  |
  v
Node 9: Detect RFI Candidates
  Filter pages where possible_rfis.length > 0
  |
  v
Node 10: Flag Review Required
  If possible_rfis > 0 OR revision_flags > 0
  Create "Review Required" notification
  |
  v
Node 11: Complete
  PATCH /plans/{id} status -> COMPLETE
  Store: gemini_summary, sheet_count, flagged_rfis
```

---

## Gemini System Prompt (Node 5)

```
You are the HCI AI Plan Review Assistant.
You are reviewing ONE construction drawing sheet.
Your role is intentionally limited.

You MAY:
- summarize the sheet
- identify discipline
- identify likely revision notes
- identify title block information
- identify obvious scope
- identify possible RFIs
- identify possible bid package impacts
- classify sheet type

You MUST NOT:
- calculate dimensions
- calculate quantities
- perform material takeoffs
- determine code compliance
- compare other sheets
- perform cross-sheet references
- interpret schedules as authoritative
- create official RFIs
- make engineering decisions
- infer missing drawing information

If uncertain, say UNKNOWN.
Return ONLY valid JSON. Nothing else.
```

---

## Gemini Request Body (Node 5)

```json
{
  "contents": [{
    "parts": [
      { "text": "[SYSTEM PROMPT ABOVE]" },
      { "inline_data": { "mime_type": "image/png", "data": "{{base64_page}}" } },
      { "text": "Return your analysis as JSON matching this exact schema." }
    ]
  }],
  "generationConfig": {
    "temperature": 0.1,
    "responseMimeType": "application/json"
  }
}
```

---

## Output Contract — Required JSON Schema

Every processed sheet produces exactly one object with these top-level keys:

```json
{
  "sheet_summary": {
    "sheet_number": "A2.1",
    "sheet_title": "Main Floor Plan",
    "discipline": "Architectural",
    "sheet_type": "Floor Plan",
    "summary": "Overall layout of first floor...",
    "confidence": 0.91
  },
  "drawing_index_entry": {
    "sheet_number": "A2.1",
    "sheet_title": "Main Floor Plan",
    "discipline": "Architectural",
    "revision_number": "Rev 2",
    "revision_date": "2026-06-15",
    "scale": "1/4 inch = 1 foot",
    "confidence": 0.88
  },
  "revision_flags": [
    {
      "description": "Cloud markup near kitchen",
      "location": "lower right quadrant",
      "confidence": 0.75
    }
  ],
  "possible_rfis": [
    {
      "description": "Dimension missing at stair opening",
      "location": "Grid C-4",
      "urgency": "high",
      "confidence": 0.82
    }
  ],
  "bid_package_impacts": [
    {
      "package": "Millwork",
      "reason": "Cabinet layout revised",
      "confidence": 0.83
    }
  ]
}
```

No additional keys accepted. Strict schema enforced by Node 6 JSON Validator.

---

## Failure Path

If Gemini returns invalid JSON:
- Retry once with same prompt
- If still invalid: mark page status = FAILED, log error, continue to next page
- At end: if >50% pages failed, set plan_document status = FAILED
- Log processing_errors to plan_documents table

---

## GBT Ruling
"This strict schema keeps Gemini constrained to the roles of summarization,
classification, flagging, and drafting, leaving deterministic extraction,
quantity takeoffs, schedule interpretation, and cross-sheet intelligence
to later components in the Plan Reader pipeline."

## Status
- Cycle 9 Part 2: COMPLETE
- Part 3 to follow: CPM schema + research_queries DDL + GET /plans/{id}/summary
