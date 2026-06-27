# Authoring Pipeline Specification
*HCI AI Operating System — Architecture Governance*
*Version: 1.0 | Date: 2026-06-27 | Author: Claude Code*

---

## 1. Service: Architecture Sync Engine

**Location:** `03_Source_Code/services/architecture_sync/routes.py`
**Mount:** `GET|POST /api/v1/services/architecture-sync/*`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | Current handbook status: volumes, ADRs, queue summary |
| GET | `/conflicts` | List implementation vs handbook conflicts |
| GET | `/review-engine` | Which handbook chapters affected by recent implementation changes |
| POST | `/validate` | Validate a draft chapter (formatting, cross-refs, conflicts) |
| POST | `/publish` | Publish a validated draft (version, move to Published/, update index) |
| POST | `/submit-chapter` | Accept chapter from any source (Drive, Git, API, AI) |
| GET | `/queue` | Current AUTHORING_QUEUE status (chapter-by-chapter) |
| POST | `/sync` | Force full re-sync of all cross-references and diagrams |

---

## 2. Validation Logic

### Chapter Validation Checks (POST /validate)

```python
def validate_chapter(content: str, volume: int, chapter: str) -> ValidationResult:
    checks = [
        check_frontmatter(content),          # Required: Volume, Title, Status, Author, Date
        check_section_numbering(content, volume),  # Sections must start with {volume}.
        check_no_ca_overwrite(content, volume),    # Philosophy sections not overwritten
        check_cross_references(content),           # ADR refs, Volume refs, code paths exist
        check_no_credentials(content),             # No secrets in content
        check_conflict_detection(content, volume), # Implementation divergence detection
    ]
    return ValidationResult(passed=all(c.passed for c in checks), checks=checks)
```

### Conflict Detection Logic

For each implementation reference in the chapter:
1. Read the referenced code file
2. Compare described behavior with actual implementation
3. Flag if: endpoints differ, schemas differ, algorithms differ
4. Generate ADR recommendation if conflict detected

---

## 3. Publish Logic

### POST /publish flow

```python
def publish_chapter(volume: int, chapter: str) -> PublishResult:
    # 1. Read from Drafts/
    draft = read_draft(volume, chapter)

    # 2. Validate (must pass)
    validation = validate_chapter(draft.content, volume, chapter)
    if not validation.passed:
        return PublishResult(error="Validation failed", checks=validation.checks)

    # 3. Version
    version = next_version(volume, chapter)  # SemVer increment

    # 4. Move to Published/
    write_published(volume, chapter, version, draft.content)

    # 5. Update master index
    update_master_index(volume, chapter, version, status="PUBLISHED")

    # 6. Update AUTHORING_QUEUE
    update_authoring_queue(volume, chapter, status="PUBLISHED", version=version)

    # 7. Update CHANGELOG
    append_changelog(f"v{version} — Published {volume}.{chapter}: {draft.title}")

    # 8. Cross-reference scan
    update_cross_references(volume, chapter)

    # 9. Generate diagram if applicable
    if has_diagram_spec(volume, chapter):
        generate_diagram(volume, chapter)

    # 10. Notify
    send_ntfy(f"Chapter {volume}.{chapter} published — v{version}")

    return PublishResult(version=version, status="published")
```

---

## 4. Architecture Review Engine

### Trigger: Every Implementation Commit

After each code commit, the review engine determines which handbook chapters were affected:

```python
def review_implementation_change(changed_files: list[str]) -> ReviewReport:
    affected_volumes = []
    for f in changed_files:
        affected_volumes.extend(FILE_TO_VOLUME_MAP.get(f, []))

    return ReviewReport(
        affected_volumes=list(set(affected_volumes)),
        adrs_to_update=[adr for adr in ADRS if adr.references_any(changed_files)],
        handbook_sections_to_check=[...],
        conflicts_detected=[...],
        recommendations=[...]
    )
```

### File → Volume Mapping

| File Pattern | Handbook Volume |
|-------------|----------------|
| `services/project_brain/*` | Vol III, Vol II |
| `services/predictive_engine/*` | Vol V, Vol II |
| `services/connectors/*` | Vol VI, Vol VII |
| `api/routers/executive.py` | Vol V |
| `api/routers/superintendent.py` | Vol IV |
| `api/routers/pm.py` | Vol IV |
| `api/routers/leadership.py` | Vol IV, Vol V |
| `services/system_auditor/*` | Vol VIII, ADR-005 |
| `services/architecture_sync/*` | ADR-006 |
| `05_Database/migrations/*` | Vol II, Vol VIII |
| `workflows/n8n/*` | Vol VII |

---

## 5. Authoring Automation n8n Workflow

**Workflow Name:** `ARCH-001-Authoring-Pipeline`
**Trigger:** File created in `Handbook/Drafts/` (file watcher)

```
File watcher (Drafts/)
    ↓  {filename, content}
HTTP Request → POST /architecture-sync/validate
    ↓  {validation_result}
IF passed:
    HTTP Request → POST /architecture-sync/publish
    HTTP Request → POST ntfy (chapter published)
ELSE:
    Write Drafts/{filename}.validation_report.md
    HTTP Request → POST ntfy (validation failed, see report)
```

---

## 6. Source Integration Adapters (Future)

Each adapter normalizes to the same chapter payload:

```json
{
  "source": "google_drive | git | api | manual | ai_author",
  "volume": 3,
  "chapter": "3.2",
  "title": "Per-Project Intelligence",
  "content": "...",
  "author": "ChatGPT",
  "submitted_at": "2026-06-27T14:00:00Z",
  "dry_run": true
}
```

The pipeline processes identically regardless of source — no adapter-specific logic in the validation or publish flow.
