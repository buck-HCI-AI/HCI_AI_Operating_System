---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: ACTION REQUIRED: 1355R Structural Plan Analysis — Draft RFIs and SOWs
created_at: 2026-06-29
summary: Handoff from ChatGPT via GBT Gateway
---

Claude Code ran Opus vision analysis on all 7 sheets of the 1355R structural S drawing set (Silver Town Structures, PE Heini Brutsaert, License #44252, (970) 379-8310). Raw findings are at /tmp/1355R_opus_structural_analysis.json.

KEY FINDINGS FOR GBT ACTION:

1. OPEN ITEMS ON DRAWINGS (red markup):
   - S.2.003 Main Level, Grid H-J/9-10: "EXISTING POST? confirm" (red circle) — field verify required before framing closes
   - S.2.005 Roof Framing, Detail 10/S6.2: "verify" (red text) — unresolved connection detail
   - S.2.005: "119°-10" ARC? R=27-7" — engineer put a question mark on this geometry. Unresolved by design.

2. SPECS CONFIRMED (use in SOWs):
   - Snow 75 PSF, Floors 40 PSF, Decks 75 PSF, Wind 115 mph Exp B, Seismic Zone C
   - Slab: 4" conc w/ #4 @ 1-6" OC both ways over 4" compacted soil/gravel
   - Foundation walls: 8" conc, #4 @ 1-4" vert, 2-#5 cont top and bottom
   - LVL: 11-7/8" TJI 360 and 560 @ 16" OC (two series — match exactly)
   - Steel: W12x65 @ grid E-F/2, W10x22 @ G/6 (main level); W10x15, W10x26 bent, W10x30, C12x33.9 (roof)
   - HSS columns: full schedule S through P on drawing
   - DF #1 sawn lumber: 4x10, 4x8, 6x12
   - Underpinning: 6-step procedure, 2-week cure wait between phases (4+ week minimum before new foundation work)

3. GAPS REQUIRING RFIs TO HEINI BRUTSAERT (970) 379-8310:
   - Steel grade not stated on roof framing sheet (A992? A36?)
   - Hanger "MHUSS.50/10 x SKL 15" is non-standard Simpson designation — confirm exact model
   - Bracket dimension [129-4.5"] on W10x15 is unexplained
   - No roofing assembly spec anywhere in 7-sheet structural set
   - CHECKED BY blank on all 7 sheets — no formal QC
   - Underpinning 4-week sequence not in any schedule yet

ACTION REQUESTED FROM GBT:
1. Draft formal RFIs to Heini Brutsaert at Silver Town Structures covering the above gaps
2. Draft trade SOWs for Concrete, Steel, Framing incorporating confirmed specs above
3. Review if the underpinning 4-week sequence is reflected in the current 1355R project schedule
4. Confirm: does 1355R have an active permit yet? (Claude Code voided test RFI-001 — no permit issued)

Full Opus analysis: /tmp/1355R_opus_structural_analysis.json
Plan reader endpoint: POST /gateway/plan/read (Sonnet default, Opus on request)
SE contact: Heini Brutsaert, Silver Town Structures, (970) 379-8310
