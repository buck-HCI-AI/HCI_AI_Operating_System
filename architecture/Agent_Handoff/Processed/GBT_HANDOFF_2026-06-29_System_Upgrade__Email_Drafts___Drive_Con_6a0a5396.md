---
source_agent: claude_code
destination_agent: ChatGPT
document_type: implementation_request
priority: medium
status: pending
related_system: 
title: System Upgrade: Email Drafts + Drive Content Now Live
created_at: 2026-06-29
summary: New email draft and Drive text endpoints active; HubSpot writes done; all fixes complete
---

SYSTEM UPGRADE COMPLETE 2026-06-29

New gateway capabilities:

1. EMAIL DRAFTS  POST /gateway/email/draft
   Fields: to_name, to_email, subject, body_html, reply_to_message_id (optional)
   Creates draft in Buck's Outlook — does NOT send. Buck reviews then sends.
   Use this to draft RFI emails, bid request follow-ups, and client updates.

2. DRIVE FILE TEXT CONTENT  GET /gateway/drive/file/{file_id}/content
   Returns full text from Google Docs, Sheets, Slides, DOCX, XLSX.
   Use this to read SOWs, schedules, bid templates, field reports directly.
   PDFs still require Claude Code MCP session (note will say so).

3. PLAN ANALYSIS TRIGGER
   Send a directive to claude_code inbox via POST /gateway/agent/handoff
   with destination_agent: claude_code
   Body: "Run project_plan_analysis.py --project 101F"
   Claude picks it up next session, analyzes plans, returns findings to your inbox.

FIXES DONE TODAY:
- 246GW Superintendent: set to Buck Adams (placeholder)
- HubSpot 1355R 13A Fire Sprinkler: advanced to Leveling
- HubSpot notes logged: 1355R 11A Appliances + 64EW 03 Concrete leveling complete
- AI Model Auto-Updater workflow: now ACTIVE (Mondays 7am)
- AUTO-CONTINUOUS-DISCOVERY: now ACTIVE (HubSpot hourly + Houzz nightly)

YOUR INBOX HAS 3 PENDING ITEMS:
Please execute them and return outputs to claude_code inbox.

