# 02_ACTIVE_WORK.md
**What is being implemented right now — cleared at session end**
Last updated: 2026-06-24

---

## Current Sprint: AI_TEAM Structure + Collaboration Framework

**Status:** COMPLETING
**Owner:** Claude Code

### Completed this session

- [x] Read and adopted `HCI_AI_Claude_Code_Operating_Charter_v0.1`
- [x] Read and adopted `HCI_AI_Repository_Collaboration_Proposal_v1.0`
- [x] Migrated AI_TEAM files to numbered scheme (00–08)
- [x] Created BOOK_00 canonical engineering manual (seed)
- [x] Committed governing PDFs to `01_Engineering_Library/`
- [x] Committed Collaboration Proposal PDF

### In Progress

- [ ] Final commit of this session's work

---

## Last Active Task Before This Session

**Session 1 completed (2026-06-24 morning):**
- Processed Adam's email (Tolteck masonry bid $7,150 for 64 Eastwood)
- Ran WF-007 bid leveling for 64EW and 101F
- Fixed WF-007 Send Draft bug (upstream node reference)
- Created 4 x 101F bid request emails (Pella Windows + 3 roofers)
- Logged all emails as HubSpot engagements

---

## Handoff Notes for ChatGPT

When reviewing this repo, the immediate open engineering question is:

**"What is the right schema for the memory ingestion pipeline?"**

Specifically:
- How should HubSpot contact/company data map to Qdrant `vendor_memory`?
- What embedding strategy for bid descriptions (short text vs. concatenated context)?
- Should the FastAPI layer sit between n8n and Postgres, or should n8n write to Postgres directly via the Postgres n8n node?

These decisions belong to ChatGPT (Architect). Once decided, Claude Code implements.
