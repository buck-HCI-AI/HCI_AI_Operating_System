# 06_NEXT_SESSION.md
**Handoff notes — what the next session must do first.**
Last updated: 2026-06-24 (end of Session 3)

---

## System State at Session End

Everything is live and auto-starting. No manual docker or server commands needed at startup.

| Layer | Status |
|---|---|
| FastAPI (port 8000) | ✅ auto-starts via launchd on login |
| WF-007 Bid Leveling | ✅ auto-runs at login + 7AM via launchd |
| WF-003 Morning Brief | ✅ auto-runs at login + 7AM via launchd |
| PostgreSQL / Qdrant / Redis | ✅ running in Docker |
| WF-001 through WF-005 | ✅ built, manual trigger via POST |
| GitHub | ✅ main branch, all committed |

---

## Claude Code: Start Here

### Step 1 — Health check
```bash
curl -s http://localhost:8000/health | python3 -m json.tool
cat /tmp/hci_morning_startup.log
```

### Step 2 — Confirm morning brief arrived
Check buck@ahmaspen.com inbox for "HCI Morning Brief" email.
If not received: `curl -X POST http://localhost:8000/workflows/wf003/morning-brief -H "Content-Type: application/json" -d '{"send":true}'`

### Step 3 — Tomorrow's priority tasks (in order)

1. **Preliminary project schedules in Drive**
   - Create a schedule template document in Google Drive for each of the 3 active projects
   - Structure: phases, milestones, key dates — ready for Buck to populate from MS Project

2. **Bid leveling follow-up**
   - Pull current bid leveling output: `curl -s http://localhost:8000/projects/3/summary`
   - Review WF-007 output in Outlook drafts
   - Identify packages with multiple bids ready for award recommendation

3. **Houzz browser automation (Playwright)**
   - Install Playwright: `pip3 install playwright && playwright install chromium`
   - Build login + daily log entry script for Houzz Pro
   - Wire into WF-004 so one log entry hits both HCI OS + Houzz

---

## ChatGPT: Start Here

Read in order:
1. `AI_TEAM/00_STATUS.md`
2. `AI_TEAM/04_ARCHITECTURE.md`
3. `BOOK_00/README.md`

**Open architecture questions for this session:**
- Houzz Playwright automation: script structure and error recovery strategy
- MS Project → Drive schedule template: what format (Google Doc, Sheet, or Slides)?
- Agent layer design (Phase 4): which agent should be built first?

Write decisions to `AI_TEAM/03_DECISIONS.md`.
