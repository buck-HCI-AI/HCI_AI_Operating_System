# Autonomy Backlog
## HCI AI Operating System v2.1 — Recurring Manual Tasks → Automation Opportunities

**Authority:** Chief Architect Directive — v2.1 (Item 8)  
**Owner:** Buck Adams  
**Updated:** 2026-06-27  
**Purpose:** Every time Buck does something manually that a system could do, it goes here.

---

## How This Works

1. Claude Code detects a recurring manual pattern
2. An automation opportunity is logged here
3. Buck reviews and approves the automation
4. Claude Code implements it in the next sprint
5. ROI is tracked (hours saved per week)

---

## Active Opportunities

### AUTO-OPP-001 — Morning Status Check
**Current state:** Buck opens Claude Code, asks "what's the status?"  
**Frequency:** Daily  
**Time cost:** 5–10 minutes  
**Automation:** Morning Brief push notification at 07:00 + Executive Dashboard  
**Implementation:** Sprint 3 (`/api/v1/executive/morning-brief` + n8n email)  
**Estimated savings:** 5 min/day × 5 days = 25 min/week  
**Status:** DESIGNED — Sprint 3

---

### AUTO-OPP-002 — Agent Coordination
**Current state:** Buck tells Claude Code what Browser Claude did, tells Browser Claude what Claude Code needs  
**Frequency:** Every multi-agent session  
**Time cost:** 15–30 minutes per session  
**Automation:** MISSION_QUEUE.md + EVENT_BUS_ARCHITECTURE.md + AI_TEAM/06_NEXT_SESSION.md  
**Implementation:** COMPLETE — v2.0  
**Estimated savings:** 20 min/session × 3 sessions/week = 60 min/week  
**Status:** COMPLETE ✅

---

### AUTO-OPP-003 — Approval Queue Review
**Current state:** Buck reviews approval queue manually in conversation  
**Frequency:** Daily  
**Time cost:** 10–20 minutes  
**Automation:** EXECUTIVE_INBOX.md surfacing only OWNER-level items (5 vs. 1,016)  
**Implementation:** COMPLETE — v2.0  
**Estimated savings:** 15 min/day × 5 days = 75 min/week  
**Status:** COMPLETE ✅

---

### AUTO-OPP-004 — Directive Delivery
**Current state:** Buck writes a .docx directive, opens Claude Code, pastes path  
**Frequency:** Several times per session  
**Time cost:** 2–5 minutes per directive  
**Automation:** Watch Desktop folder for new .docx files — auto-read at session start  
**Implementation:** Session start protocol in DIRECTIVE_CLAUDE_CODE.md + could add file watcher  
**Estimated savings:** 3 min/directive × 5 directives/week = 15 min/week  
**Status:** PARTIALLY AUTOMATED — session start protocol exists; file watcher pending Sprint 4

---

### AUTO-OPP-005 — Git Push Authorization
**Current state:** Buck must explicitly authorize each git push  
**Frequency:** Per session (1–3 times)  
**Time cost:** 1–2 minutes per push  
**Automation:** Scheduled auto-push after commit if no OWNER-level pending items — only non-sensitive branches  
**Risk:** Medium — requires careful scoping  
**Implementation:** Sprint 4 — auto-push policy with safe guard conditions  
**Estimated savings:** 2 min × 3/week = 6 min/week  
**Status:** OPEN — awaiting Buck approval

---

### AUTO-OPP-006 — Houzz Daily Data Pull
**Current state:** Browser Claude extracts Houzz data manually when directed  
**Frequency:** Should be daily  
**Time cost:** 30–60 minutes of Browser Claude session per run  
**Automation:** HZ-004 n8n trigger (already built, deactivated) fires at 17:30 daily  
**Prerequisite:** Browser Claude data load completes (Phase 3)  
**Implementation:** Activate HZ-004 after first successful manual extraction  
**Estimated savings:** Turns manual extraction into zero-touch daily sync  
**Status:** BLOCKED — waiting on Browser Claude data load

---

### AUTO-OPP-007 — Vendor Registry Maintenance
**Current state:** Mining engine queues vendor candidates; Buck reviews individually in conversation  
**Frequency:** Weekly  
**Time cost:** 20–40 minutes  
**Automation:** Batch approval cards — mining engine groups obvious duplicates, Buck approves batch  
**Implementation:** EXECUTIVE_INBOX.md batch format + `/api/v1/executive/batch-approve`  
**Estimated savings:** 30 min/week  
**Status:** DESIGNED — Sprint 3

---

### AUTO-OPP-008 — Sprint Board Updates
**Current state:** Claude Code updates TASKS.md manually during session  
**Frequency:** Multiple times per session  
**Time cost:** Minimal — but interrupts flow  
**Automation:** `post_mission.py` updates TASKS.md automatically on mission completion  
**Implementation:** Sprint 4  
**Estimated savings:** 5 min/session × 3 sessions/week = 15 min/week  
**Status:** DESIGNED — Sprint 4

---

### AUTO-OPP-009 — Downloads Folder Cleanup
**Current state:** Buck drops files in Downloads; Claude Code reorganizes when asked  
**Frequency:** Weekly  
**Time cost:** 5–10 minutes  
**Automation:** File watcher on Downloads — auto-sort HCI files to HCI AI/ subfolders on drop  
**Implementation:** launchd file watcher + Python sort script  
**Estimated savings:** 5 min/week  
**Status:** OPEN — low priority

---

### AUTO-OPP-010 — HubSpot Deal Stage Updates
**Current state:** Buck manually updates HubSpot deal stages when project milestones are hit  
**Frequency:** Variable — 1–3 times per week  
**Time cost:** 5–10 minutes  
**Automation:** Mining engine detects milestone completion → queues Gate H write → Buck approves with one tap  
**Implementation:** Sprint 3 (HubSpotMiner enhancement)  
**Estimated savings:** 5 min × 2/week = 10 min/week (still requires approval, but one-tap not conversation)  
**Status:** OPEN — Sprint 3

---

### AUTO-OPP-011 — Drive Bid File Organization
**Current state:** Bid files land in Google Drive; manual organization  
**Frequency:** Daily during active bid periods  
**Time cost:** 10–15 minutes  
**Automation:** DriveMiner detects new bid files → creates folder structure → queues upload  
**Implementation:** Sprint 4 (DriveMiner enhancement)  
**Estimated savings:** 10 min/day during bid periods  
**Status:** OPEN — Sprint 4

---

### AUTO-OPP-012 — Weekly PM Review
**Current state:** Manual weekly review per project  
**Frequency:** Weekly (already partially automated)  
**Time cost:** 30 min/project × 3 projects = 90 min/week  
**Automation:** WF-001 through WF-007 already automate parts; expand to full PM brief  
**Implementation:** Sprint 3 — enhance existing WF-001 output  
**Estimated savings:** 60 min/week  
**Status:** PARTIALLY AUTOMATED — expanding Sprint 3

---

## ROI Summary (Projected)

| Opportunity | Status | Est. Savings/Week |
|---|---|---|
| AUTO-OPP-001 Morning status | Sprint 3 | 25 min |
| AUTO-OPP-002 Agent coordination | ✅ Done | 60 min |
| AUTO-OPP-003 Approval review | ✅ Done | 75 min |
| AUTO-OPP-004 Directive delivery | Partial | 15 min |
| AUTO-OPP-005 Git push | Open | 6 min |
| AUTO-OPP-006 Houzz daily sync | Blocked | 30+ min |
| AUTO-OPP-007 Vendor batch approval | Sprint 3 | 30 min |
| AUTO-OPP-008 Sprint board | Sprint 4 | 15 min |
| AUTO-OPP-009 Downloads sort | Open | 5 min |
| AUTO-OPP-010 HubSpot one-tap | Sprint 3 | 10 min |
| AUTO-OPP-011 Drive bid org | Sprint 4 | 10 min |
| AUTO-OPP-012 PM review | Sprint 3 | 60 min |
| **TOTAL PROJECTED** | | **~341 min/week (~5.7 hrs)** |
| **Already captured (v2.0)** | | **~135 min/week (~2.25 hrs)** |

---

## How to Add New Opportunities

Any agent can add an opportunity to this file using this format:

```markdown
### AUTO-OPP-NNN — [Title]
**Current state:** What Buck does manually today
**Frequency:** How often
**Time cost:** How long it takes
**Automation:** What the system would do instead
**Implementation:** Sprint target + which file/service
**Estimated savings:** X min/week
**Status:** OPEN | DESIGNED | BLOCKED | IN PROGRESS | COMPLETE
```

---

*Autonomy Backlog | HCI AI Operating System v2.1 | Hendrickson Construction, Inc.*  
*Updated continuously. Buck reviews monthly. Claude Code implements after approval.*
