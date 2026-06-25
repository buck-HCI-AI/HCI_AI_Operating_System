# Workflow 00 - AI Collaboration Layer

## Purpose

Create the collaboration layer that allows ChatGPT and Claude Code to work from the same repository state.

## Trigger

Any engineering work on the HCI AI Operating System.

## Inputs

- Repository state
- AI_TEAM status files
- Book 00
- Architecture documents
- ADRs
- Current backlog
- Buck decisions

## Process

### 1. Start Session

Read AI_TEAM and Book 00.

### 2. Confirm Active Work

Review active work, blockers, roadmap, and decisions.

### 3. Execute Role

ChatGPT performs architecture and documentation work.
Claude Code performs implementation work.

### 4. Update Repository

Any changes must update relevant docs.

### 5. End Session

Update AI_TEAM status, changelog, blockers, and next-session file.

## Outputs

- Updated repository files
- Updated AI_TEAM status
- Updated changelog
- Updated next-session instructions
- Updated decisions/ADR if needed

## Success Criteria

Buck can start any future session with:

> Read AI_TEAM and continue.

and the AI can continue without manual context reconstruction.
