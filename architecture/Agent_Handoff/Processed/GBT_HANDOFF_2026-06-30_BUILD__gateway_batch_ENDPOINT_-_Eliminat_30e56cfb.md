---
source_agent: claude_browser
destination_agent: claude_code
document_type: implementation_request
priority: urgent
status: pending
related_system: 
title: BUILD /gateway/batch ENDPOINT - Eliminate 3-Call GBT Limit
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

BUILD THIS NOW - HIGHEST PRIORITY

POST /gateway/batch
Accepts array of operations, executes all server-side, returns combined result.
GBT makes 1 tool call -> gateway runs 5+ operations -> 1 Allow click = everything done.

Request body:
{
  session_id: "S12",
  operations: [
    {op: "driveWrite", params: {filename: "x.md", content: "y", folder_id: "root"}},
    {op: "sendHandoff", params: {title: "t", body: "b", destination_agent: "claude_code"}},
    {op: "bidLevel", params: {project_id: 1, dry_run: true}},
    {op: "ntfyPush", params: {title: "t", body: "b", priority: "high"}},
    {op: "emailDraft", params: {to_name: "x", to_email: "x@x.com", subject: "s", body_html: "<p>b</p>"}}
  ]
}

Response:
{
  results: [
    {op: "driveWrite", status: "ok", file_id: "abc"},
    {op: "sendHandoff", status: "queued", request_id: "def"},
    ...
  ],
  summary: "5/5 operations completed"
}

Session warmup log should be AUTOMATICALLY included in every batch call - add it internally, never use a call slot.
Also auto-include ntfy push with batch summary on completion.

This is the single highest-ROI build. Do it first.
