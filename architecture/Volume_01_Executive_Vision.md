# Volume I — Executive Vision
*HCI AI Construction Operating System Architecture Handbook*

---

> ⚠️ **Chief Architect Input Required**
> This volume defines the mission, vision, design principles, and operating philosophy.
> Content must be authored by ChatGPT (Chief Architect) and Buck Adams.
> Claude Code will cross-reference implementation and flag any conflicts once authored.

---

## Sections to be Authored

### 1.1 Mission
*[Chief Architect: Define the mission of the HCI AI Operating System]*

### 1.2 Vision
*[Chief Architect: Define the long-term vision for AI-powered construction intelligence]*

### 1.3 Design Principles
*[Chief Architect: Core principles that guide every architectural decision]*

### 1.4 Operating Philosophy
*[Chief Architect: How the system thinks and behaves]*

### 1.5 AI-First Construction Company
*[Chief Architect: What it means to be an AI-first construction company]*

### 1.6 What Success Looks Like
*[Chief Architect: Measurable success criteria for the platform]*

### 1.7 How AI Should Think Like Hendrickson Construction
*[Chief Architect: Domain-specific reasoning model for construction]*

### 1.8 Human + AI Collaboration Model
*[Chief Architect: Division of authority, autonomy boundaries, escalation model]*

### 1.9 Continuous Improvement Philosophy
*[Chief Architect: How the platform improves itself over time]*

---

## Implementation Notes (Claude Code)

The following governance constraints are already implemented and should inform the philosophy:

- **Buck Adams retains final authority** on: awards, budgets, commitments, contracts,
  client communications, production go-lives, HubSpot writes
- **AI acts autonomously** on: read operations, analysis, report generation, internal
  DB writes, drafting recommendations, approval queue management
- **Approval gate enforced via**: `approval_queue` table, `executive_inbox` table,
  `APPROVAL_GATES.md` policy registry
- **Dry-run by default**: no production writes without validation evidence
- **Security**: API key auth on all endpoints, .env never committed to git

These constraints form the practical boundary of the Human + AI Collaboration Model.
The philosophy authored by the Chief Architect should align with these constraints.
