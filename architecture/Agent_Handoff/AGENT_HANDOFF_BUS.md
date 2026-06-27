# HCI Agent Handoff Bus
*Adopted: 2026-06-27 | Directive: Build Agent Handoff Bus.docx*

> **Mission:** Buck no longer manually relays documents between AI agents.
> Agents drop work into the handoff inbox. The system routes it automatically.

---

## How It Works

```
Browser Claude / ChatGPT
  └─→ Save output as handoff file (use template)
  └─→ Place in Architecture/Agent_Handoff/Inbox/
  
n8n AUTO-HANDOFF-PROCESSOR (watches Inbox/ → triggers on new file)
  └─→ python3 handoff_processor.py
  └─→ Validates header → routes → moves to Processed/ or Failed/
  └─→ Updates HANDOFF_INDEX.md
  └─→ Sends ntfy notification
```

---

## Directory Structure

```
Architecture/Agent_Handoff/
  ├── Inbox/           ← Drop handoff files here
  ├── Processing/      ← Processor working directory
  ├── Processed/       ← Successfully processed files
  ├── Failed/          ← Files that failed validation
  ├── Archive/         ← Long-term storage
  ├── templates/       ← Standard formats for each agent
  ├── HANDOFF_INDEX.md ← Auto-maintained log
  ├── AGENT_HANDOFF_BUS.md (this file)
  └── handoff_processor.py ← The processor
```

---

## Standard Handoff Format (YAML frontmatter)

Every handoff file MUST begin with this header:

```markdown
---
source_agent: [browser_claude | chatgpt_chief_architect | claude_code | n8n | buck]
destination_agent: [claude_code | chatgpt_chief_architect | executive_inbox | all]
document_type: [see types below]
priority: [urgent | high | medium | low]
status: pending
created_at: YYYY-MM-DD
related_project: [64EW | 101F | 1355R | all]
related_system: [houzz_pro | hubspot | hci_ai_os | google_drive | all]
intended_action: [ingest_to_platform_intelligence | implement_directive | publish_to_handbook | add_to_backlog | post_to_executive_inbox]
requires_approval: [true | false]
summary: One-sentence description of this handoff
---

[Content of the handoff follows here]
```

---

## Supported Handoff Types

| document_type | Source Agent | Routes To |
|---------------|-------------|-----------|
| `browser_discovery` | Browser Claude | Architecture/Platform_Intelligence/ |
| `houzz_export` | Browser Claude | Architecture/Platform_Intelligence/Houzz/ |
| `hubspot_export` | Browser Claude | Architecture/Platform_Intelligence/HubSpot/ |
| `platform_opportunity_report` | Browser Claude | Architecture/Platform_Intelligence/ |
| `business_process_architecture` | Browser Claude / CA | Architecture/Platform_Intelligence/ |
| `chief_architect_directive` | ChatGPT | Architecture/Handbook/Drafts/ |
| `architecture_chapter` | ChatGPT | Architecture/Handbook/Drafts/ |
| `implementation_request` | ChatGPT / Buck | Appended to STRATEGIC_BACKLOG.md |
| `approval_request` | Any | POST to Executive Inbox API |
| `executive_brief` | ChatGPT | Architecture/Handbook/Published/ |

---

## Agent Workflows

### Browser Claude
Old way: Paste large reports into chat → Buck manually moves them → Claude Code ingests
New way: 
1. Save discovery output as a `.md` file with handoff header
2. Use `browser_discovery` or `platform_opportunity_report` type
3. Place in `Agent_Handoff/Inbox/`
4. n8n detects and processes automatically

### ChatGPT (Chief Architect)
Old way: Buck copies CA output from ChatGPT → pastes to Claude Code
New way:
1. CA authors chapter or directive
2. Buck saves as `.md` file using template
3. Places in `Agent_Handoff/Inbox/`
4. Processor validates → routes to Drafts/ → Architecture Sync Engine publishes

### Buck (Manual Drop)
Buck can drop any document with the handoff header into Inbox/ and the system handles the rest.

---

## Running the Processor Manually

```bash
# Dry run (validate only, no file moves)
python3 Architecture/Agent_Handoff/handoff_processor.py --dry-run

# Process a specific file
python3 Architecture/Agent_Handoff/handoff_processor.py --file path/to/file.md

# Process all files in Inbox/ (production)
python3 Architecture/Agent_Handoff/handoff_processor.py
```

---

## Production Rules

- Processing handoffs may update docs, indexes, backlogs, and draft records automatically
- Any production data writes (HubSpot, Houzz, DB) still require approval (`requires_approval: true`)
- `approval_request` type always requires human review regardless of `requires_approval` flag

---

## Templates

See `Architecture/Agent_Handoff/templates/` for standard format per document type:
- `browser_discovery_template.md`
- `chief_architect_directive_template.md`
- `architecture_chapter_template.md`
- `implementation_request_template.md`
