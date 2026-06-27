# Chief Architect Authoring Pipeline
*HCI AI Operating System — Architecture Governance*
*Version: 1.0 | Date: 2026-06-27 | Author: Claude Code*

---

## Pipeline Overview

```
Chief Architect (ChatGPT + Buck)
        ↓  [Author chapter in any format]
Handbook/Drafts/{Volume}_{Chapter}.md
        ↓  [Architecture Sync Engine validates]
POST /api/v1/services/architecture-sync/validate
        ↓  [Validation report + cross-references generated]
Review (if conflicts detected → ADR created, Chief Architect notified)
        ↓  [Chief Architect approves]
POST /api/v1/services/architecture-sync/publish
        ↓  [Version numbered, moved to Handbook/Published/]
Handbook index updated
CHANGELOG.md updated
Implementation cross-references updated
Diagrams auto-generated
        ↓  [ntfy notification to Buck]
Executive Dashboard mission updated
```

---

## Delivery Methods (Future Integration)

The pipeline accepts chapters from any source without architecture change:

| Source | Mechanism | Handler |
|--------|-----------|---------|
| Manual file drop | Place `.md` in `Handbook/Drafts/` | n8n file watcher → `/validate` |
| Google Drive | Drive MCP → fetch → write to Drafts/ | n8n Drive webhook → `/validate` |
| Git push | GitHub webhook → pull → write to Drafts/ | n8n webhook → `/validate` |
| API call | `POST /api/v1/services/architecture-sync/submit-chapter` | Direct to `/validate` |
| AI author (ChatGPT) | Webhook from ChatGPT export | n8n webhook → `/validate` |

---

## Chapter Lifecycle

```
NOT_STARTED → IN_PROGRESS → DRAFT_READY → UNDER_REVIEW → PUBLISHED
                                    ↓
                              CONFLICT_DETECTED → ADR_CREATED → CHIEF_ARCHITECT_RESOLVED
                                                                        ↓
                                                                 PUBLISHED (with ADR)
```

---

## Validation Rules (Enforced by Sync Engine)

Every submitted chapter must pass:

1. **Frontmatter present** — Volume, Title, Status, Version, Date, Author
2. **Section numbering correct** — e.g., Vol 3 sections = 3.1, 3.2...
3. **Chief Architect sections not overwritten** — Philosophy sections by CA are write-protected
4. **Cross-references valid** — Referenced ADRs, volumes, and code paths must exist
5. **No credential exposure** — Scan for API keys, passwords
6. **Conflict detection** — Flag if chapter contradicts implemented architecture

---

## Role Responsibilities

| Role | Responsibility | NOT Responsible For |
|------|---------------|---------------------|
| Chief Architect (ChatGPT) | Author philosophy, vision, intelligence models, governance | Implementation details |
| Buck Adams | Review + approve all Chief Architect content | Day-to-day implementation |
| Claude Code | Validate, publish, synchronize, maintain, cross-reference | Authoring philosophy |
| n8n | Trigger pipeline automation, deliver notifications | Content decisions |

---

## Non-Negotiable Rules

1. Claude Code NEVER overwrites Chief Architect authored content
2. If implementation conflicts with the handbook: create ADR, flag in Review Queue, wait for resolution
3. Every published chapter gets a version number (SemVer: Major.Minor)
4. Every implementation milestone updates the relevant handbook sections
5. The handbook is the constitutional reference — implementation follows architecture
