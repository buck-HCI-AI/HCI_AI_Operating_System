# ADR-0001 - Repository as AI Engineering Memory

## Status

Approved for implementation

## Date

2026-06-24

## Context

The HCI AI project uses multiple AI systems, including ChatGPT and Claude Code. Chat history is not reliable as long-term project memory. Manual handoffs create repeated explanations, drift, and lost context.

## Decision

The repository will be the permanent engineering memory for the HCI AI Operating System.

AI systems will synchronize by reading and updating repository documentation rather than relying on conversation history.

## Consequences

### Positive

- Less repeated explanation from Buck.
- Better continuity between ChatGPT and Claude Code.
- More durable engineering records.
- Easier recovery from lost chats.
- Cleaner audit trail for decisions and changes.

### Negative

- Requires discipline to update AI_TEAM after work.
- Requires documentation to stay synchronized with implementation.
- Initial setup adds repository overhead.

## Implementation

Create and maintain:

```text
AI_TEAM/
BOOK_00/
docs/AI_COLLABORATION_STANDARD_v1.md
architecture/CURRENT_ARCHITECTURE.md
adr/
workflows/
```

## Owner

Buck

## Architect

ChatGPT

## Implementer

Claude Code
