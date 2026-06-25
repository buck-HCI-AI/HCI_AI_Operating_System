# Current Architecture - HCI AI Operating System

## Purpose

This file documents the active architecture baseline for HCI AI.

## System Mission

Build the permanent AI Operating System for Hendrickson Construction.

## Architecture Model

```text
Buck
  -> ChatGPT: architecture, governance, documentation, review
  -> Claude Code: implementation, repository changes, automation
  -> Repository: shared engineering memory
```

## Shared Repository Memory

The repository maintains:

- `AI_TEAM/` - live engineering state.
- `BOOK_00/` - canonical engineering manual.
- `docs/` - standards and product documentation.
- `architecture/` - current and future architecture.
- `adr/` - architecture decision records.
- `workflows/` - workflow definitions and operating procedures.

## External Systems

- HubSpot: CRM, vendor, bid, and deal data.
- Google Drive: document source of truth for project files.
- Outlook / Microsoft 365: communication source.
- n8n: automation layer.
- GitHub / repository: software and documentation source of truth.
- PostgreSQL: structured application data target.
- Qdrant: vector memory / semantic search target.
- FastAPI: API services target.
- Claude Code: implementation agent.
- ChatGPT: architecture and governance agent.

## System Boundaries

ChatGPT does not continuously monitor the repository.
Claude Code does not define final architecture alone.
The repository bridges both systems.

## Architecture Risks

- Documentation drift.
- Duplicate standards.
- AI-generated changes without human approval.
- Workflow automation before SOPs and registries are stable.

## Architecture Controls

- AI_TEAM update rule.
- Book 00 synchronization rule.
- ADR process.
- Human approval gates.
- Definition of Done.
