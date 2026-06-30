---
source_agent: claude_browser
destination_agent: claude_code
document_type: capability_update
priority: high
status: pending
related_system: 
title: PLANS FOLDER SMART SCAN - Discipline Taxonomy + Archive Support
created_at: 2026-06-30
summary: Handoff from claude_browser via GBT Gateway
---

PLANS FOLDER SMART SCAN SYSTEM - BUILD THIS

PURPOSE: When Buck says "review plans for [project]" he needs to specify scope. Build a system that:
1. Scans the project's 04_Drawings Shared Drive folder recursively
2. Classifies every PDF by discipline and version status
3. Accepts a scope filter from Buck/Field GPT
4. Returns the right set of file IDs for analysis

FOLDER TAXONOMY TO BUILD:
Each project's 04_Drawings folder contains subfolders. Map them to these disciplines:
- ARCHITECTURAL: files with "arch", "A-", "architectural", "floor plan", "elevation", "section" in name
- STRUCTURAL: files with "struct", "S-", "structural", "beam", "foundation", "framing" in name
- MEP/MECHANICAL: files with "mech", "M-", "plumbing", "P-", "electrical", "E-", "HVAC" in name
- CIVIL/SITE: files with "civil", "C-", "site", "grading", "utility" in name
- INTERIOR/FINISHES: files with "interior", "ID-", "finish", "FF&E", "interior design", "DD" in name
- DETAILS: files with "detail", "D-", "section", "markup", "mark-up", "redline" in name
- ROOFING: files with "roof", "R-" in name
- LANDSCAPE: files with "landscape", "L-", "planting" in name
- PERMITS: files with "permit", "permit set", "approved" in name
- PROGRESS SETS: files with "progress", "WIP", "draft", "%" in name (e.g., "50% DD", "90% CD")
- ARCHIVE: files in subfolders named "Archive", "Superseded", "Old", "Prior", "Archived", or with "VOID" in filename
- CURRENT: everything NOT in an archive folder (default)

SCAN FUNCTION:
def scan_drawings_folder(project_code, scope="current", disciplines=None):
  # scope: "current" | "archived" | "all"  
  # disciplines: list like ["structural", "architectural"] or None for all
  # Returns: list of {file_id, filename, discipline, version_status, modified_date}

SCOPE FILTER BEHAVIOR:
- "current" -> exclude anything in Archive subfolders or with VOID in name
- "archived" -> only Archive subfolders
- "all" -> everything including archived

DISCIPLINE FILTER EXAMPLES:
- "structural" -> S-*, struct*, beam*, framing*
- "architectural" -> A-*, arch*, floor plan*, elevation*
- "finishes" or "interior" -> ID-*, finish*, FF&E*, interior design*
- "details" -> detail*, markup*, redline*
- "roofing" -> roof*, R-*
- "all" -> no discipline filter applied

FIELD GPT COMMANDS TO SUPPORT:
Buck can say to Field GPT:
- "Review current plans for 101F" -> scope=current, disciplines=all
- "Review structural and architectural for 64EW" -> scope=current, disciplines=[structural, architectural]
- "Check archived roof plans for 101F" -> scope=archived, disciplines=[roofing]
- "Full review all plans 1355R" -> scope=all, disciplines=all
- "Review finishes plans for 101F" -> scope=current, disciplines=[interior, finishes]
- "Review details only for 64EW" -> scope=current, disciplines=[details]

KNOWN DRIVE FOLDERS:
- 64EW 04_Drawings: 1iAVNLnJtEHKkYHs7KKceU35Ydny8FcVZ (Shared Drive)
  Files found: Architectuals 2026-05-12.pdf (1nt6MjXNMP-0d9TTH6T8EN02skdeAoGEF), Structurals.pdf (1-tt7njs7AYHmA8POGaLNWVaTcso6kpdh), 2025-184 PROGRESS 06-16-2026.pdf (1KslSlQsT8wVUmmTCwdN20-bVq8QzFagu)
- 101F 04_Drawings: need to locate folder ID - check Shared Drive "101 Francis"
  Files found: 260608_101 Francis-Aspen_KB Studio-Interior Design-50% DD_DRAFT.pdf, 101 francis Beams and Ducting layout.pdf

GATEWAY ENDPOINT TO BUILD:
GET /gateway/project/{code}/plans?scope=current&disciplines=structural,architectural
Returns: [{file_id, filename, discipline, version_status, size_mb, modified}]

Also: GET /gateway/project/{code}/plans/summary -> folder tree with file counts by discipline

