# HCI AI Go-Live Readiness Checklist v1
**Date:** 2026-06-26 | **Gate 5 Pilot Active:** June 25 – July 1, 2026

---

## Workflow Readiness Matrix

| Workflow | Status | Approval Gate | Rollback | Monitoring | Verdict |
|----------|--------|--------------|----------|------------|---------|
| Bid Leveling (API service) | Tested 22/22 pass | dry_run=true default; live run → approval queue | Delete queued Excel files | Approval queue | **GO** |
| Executive Report | Live, tested | Read-only | N/A | N/A | **GO** |
| MCP Server (26 tools) | Live, tested via ngrok | Write tools → approval queue | Disable launchd plist | /tmp/hci_mcp_server_err.log | **GO** |
| Read tools (all 18 read MCP tools) | Tested | None required | N/A | MCP logs | **GO** |
| Project Brain Init | Live | Read-only | N/A | API logs | **GO** |
| Schedule Intelligence | Live | Read-only | N/A | API logs | **GO** |
| Risk Intelligence | Live | Read-only | N/A | API logs | **GO** |
| Procurement Status | Live | Read-only | N/A | API logs | **GO** |
| Vendor Intelligence | Live | Read-only | N/A | API logs | **GO** |
| Operating Rules | Live | Read-only | N/A | API logs | **GO** |
| Approval Queue | Live | Write → Buck approval | Remove from queue | Queue log | **GO** |
| Bid Receipt Processing v5 (n8n) | Active — DUPLICATE EXISTS | Reads Drive + Sheets; logs tracker | Disable n8n trigger | n8n execution log | **HOLD — resolve duplicate first** |
| WF-007 AI Bid Leveling Engine (n8n) | Active | Human approval for output | Disable trigger | n8n execution log | **STAGING** (verify no conflict with API service) |
| WF-003 Historical Cost Queue | Active | Auto-write to Sheets | Disable trigger | n8n execution log | **REVIEW** — verify target sheet is correct |
| WF-004 Lessons Learned Engine | Active | Auto-write to Sheets | Disable trigger | n8n execution log | **REVIEW** — DB has 0 rows, verify writing correct location |
| WF-005 SOP Registry Sync | Active | Auto-write | Disable trigger | n8n execution log | **REVIEW** — verify sync target |
| WF-006 Executive Alerts | Active | Notification only | Disable trigger | n8n execution log | **GO** |
| WF-011 Site Superintendent Daily Briefing | Active | Draft only | Disable trigger | n8n execution log | **GO** |
| WF-008 Bid Follow-Up Engine | Inactive | Draft only — no auto-send | Disable trigger | n8n execution log | **STAGING ONLY** |
| WF-009 New Job Setup | Inactive | Creates folders / tracker rows | Disable trigger | n8n execution log | **STAGING ONLY** |
| WF-010 Outlook Email Router | Inactive | Classification + routing | Disable trigger | n8n execution log | **STAGING ONLY** |
| HubSpot write-back | Blocked | ALL writes require approval | Remove from queue | Approval queue | **BLOCKED BY DESIGN** |
| Drive write (live) | Approval-gated | Approval queue | Remove from queue | Approval queue | **GO** (approval required) |
| Email send | Approval-gated | Approval queue | Remove from queue | Approval queue | **GO** (approval required) |
| Award recommendation | Approval-gated | Buck sign-off required | Remove from queue | Approval queue | **GO** (approval required) |

---

## Pre-Go-Live Checklist (Buck Must Complete Before Full Production)

### Immediate (before July 1 pilot end)
- [ ] Identify canonical Registry Workbook (2 copies — pick one, archive other)
- [ ] Resolve duplicate Bid Receipt Processing v5 in n8n
- [ ] Investigate TMP-cl-84994d and ChatGPT Chrome Bridge workflows
- [ ] Review 9 items in approval queue — approve or reject each
- [ ] Link HubSpot deal IDs to 64EW, 101F, 1355R in project registry

### Before Full Production Go-Live
- [ ] Fix SOP service endpoint (404)
- [ ] Confirm 349 Draw Drive / 606 Starwood Olson / 843 Cemetery Lane project records
- [ ] Verify n8n workflow WF-003/004/005 are writing to correct sheet targets
- [ ] Test WF-008/009/010 in staging against real project data
- [ ] Populate Lessons Learned and Business Process Library (both 0 rows)
- [ ] Set N8N_API_KEY in .env for remote n8n management
- [ ] Resolve Qdrant unhealthy health check

### Mac Mini Migration (Sept 2026)
- [ ] Move ngrok to static domain or cloud-hosted URL
- [ ] Configure MCP as permanent ChatGPT Business workspace connector
- [ ] Remove ngrok dependency from all directives and schema files

---

## Current Pilot Status (Gate 5)
- Pilot active: 2026-06-25 → 2026-07-01
- Projects: 64 Eastwood, 101 Francis, 1355 Riverside
- Mode: Read-only + approval-gated writes
- Approval queue: 9 items pending Buck's review

---

*Checklist prepared by Claude Code, 2026-06-26. No production changes made during audit.*
