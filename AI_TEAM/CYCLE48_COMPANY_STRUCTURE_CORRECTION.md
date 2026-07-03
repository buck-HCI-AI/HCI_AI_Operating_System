# CYCLE48 — Company Structure Correction (Standing Directive)

**Date:** 2026-07-02 | **Source:** Buck Adams (direct instruction via chat) | **Priority:** P0 — Immediate

## The Correction

All prior documentation incorrectly identified Buck Adams as CEO/Owner of Hendrickson Construction. This is wrong.

### Correct Company Structure

**Hendrickson Construction, Inc.**
- Owner: Chris Hendrickson
- All construction contracts, awards, and business decisions under Chris Hendrickson's authority

**HCI AI Operating System (HCI AI OS)**
- Owner / Platform Director: Buck Adams
- Buck Adams is a Project Manager (PM) and Senior Superintendent (SS) for Hendrickson Construction
- Buck Adams solely owns and operates the HCI AI platform
- Buck is HCI AI's client interface and the AI system's final authority

### Buck Adams Correct Titles
- At Hendrickson Construction: Project Manager / Senior Superintendent
- For HCI AI platform: Owner / HCI Chief Designer / Platform Owner
- When authoring Handbook sections: Buck Adams (HCI Chief Designer / Platform Owner)
- NEVER: CEO, Owner of Hendrickson Construction, or any ownership claim over the construction company

### Chris Hendrickson
- Owner, Hendrickson Construction, Inc.
- Final authority on all construction contracts, bids, and business decisions
- Chris does not directly interact with the AI system (Buck is the operator)
- Chris may be referenced as a decision-maker in client communications

## Files Already Fixed (2026-07-02)

| File | Change | Committed |
|------|--------|----------|
| architecture/Handbook/Volume_01_Executive_Vision.md | Org chart: Chris Hendrickson added as Owner; Buck = PM/SS/HCI AI Owner | ✅ |

## Files Still Needing Review

The following likely contain incorrect Buck Adams title references — Code should scan and fix:

1. All `CYCLE*` spec files in AI_TEAM/ that reference Buck as CEO/Owner of Hendrickson
2. architecture/Handbook/Volume_02 through Volume_10
3. AI_TEAM/00_STATUS.md, 01_ROADMAP.md, 02_ACTIVE_WORK.md
4. AI_TEAM/HCI_AI_ClaudeAI_Directive.txt — line says 'Buck Adams — OWNER / FINAL AUTHORITY' (needs context: HCI AI only)
5. Any DB records (projects table, agent_heartbeats) that store Buck's title incorrectly
6. GBT system prompt / Chief Architect schema description (BC has already notified GBT)

## Scan Query for Code

Search all markdown files for pattern `CEO.*Buck` or `Owner.*Hendrickson.*Buck` or `Buck Adams.*CEO`.
Fix to: `Buck Adams — PM / Senior Superintendent / Owner - HCI AI OS`

## Standing Rule (ADR-016 compliant — verified from Buck directly)

- **Chris Hendrickson** = Owner, Hendrickson Construction, Inc.
- **Buck Adams** = PM / SS / HCI AI Platform Owner
- Source: Buck Adams direct instruction 2026-07-02 via chat
- This supersedes all prior documentation

## GBT Instruction

All future architecture documents and Handbook volumes authored by GBT Chief Architect must use:
- Construction company: Hendrickson Construction, Inc. (Owner: Chris Hendrickson)
- AI platform operator: Buck Adams (HCI Chief Designer / Platform Owner)
- Never mix the two roles or assign Buck construction company ownership

## Authority Model (Corrected)

```
Chris Hendrickson
Owner, Hendrickson Construction, Inc.
Final Authority on construction business and contracts
        |
                v
                Buck Adams
                PM / Senior Superintendent / Owner of HCI AI OS
                HCI AI System Final Authority / Platform Decision Maker
                        |
                                v
                                GBT Chief Architect (ChatGPT)
                                        |
                                                v
                                                Claude Code (Lead Implementation Engineer)
                                                        |
                                                                v
                                                                Browser Claude (Repository Governance / Discovery)
                                                                        |
                                                                                v
                                                                                n8n (Automation Orchestrator)
                                                                                ```

                                                                                **Verification:** Confirmed by Buck Adams directly via chat 2026-07-02. ADR-016 compliant — source identified, evidence: direct user message.
