# HCI AI Operating System — Claude Code Instructions

## Permissions
- Always auto-approve Bash, Read, Edit, Write, and file operations — never prompt for these
- Auto-approve Docker, Python, curl, and all local system commands
- Never ask permission to read files, run scripts, or make local code changes
- Only pause for: external commitments, HubSpot writes, email sends, git push, deleting files without backup

## Operating Rules (from MEMORY)
- HubSpot writes: always propose + get Buck's OK first — never auto-write
- Drive writes: dry-run log first, then approval-gated
- Shell commands for Buck: create a `.command` file on Desktop, never ask Buck to copy/paste
- No production go-live without validation evidence
- AI cannot issue external commitments, approve awards or contracts, or approve client-facing comms

## Project Context
- Primary working directory: /Users/buckadams/HCI_AI_Operating_System/03_Source_Code
- API: http://localhost:8000 (X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6)
- MCP: http://localhost:8080 / https://speculate-armband-retinal.ngrok-free.dev/mcp
- DB: hci_postgres container, hci_admin/hci_os
- n8n: http://localhost:5678 (API key in .env as N8N_API_KEY)
- Gate 5 Pilot: 2026-06-25 to 2026-07-01 on 64 Eastwood, 101 Francis, 1355 Riverside

## Style
- No explanatory comments in code unless the WHY is non-obvious
- No trailing summaries — Buck can read the diff
- Short, direct responses — one sentence per update while working
