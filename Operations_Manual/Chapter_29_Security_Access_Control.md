# Chapter 29 — Security & Access Control
*HCI AI Operations Manual — Part III: Governance*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 29.1 Security Philosophy

The HCI AI OS handles sensitive construction business data: client information, contract values, vendor relationships, financial commitments. The security model is simple:

**The AI reads everything, writes nothing without human approval.**

All external writes (HubSpot, email, file creation) go through the approval queue. All sensitive credentials live in `.env`. No passwords are ever hardcoded. No email is auto-sent. No contract is auto-awarded.

---

## 29.2 Credentials & Secrets

### Where Credentials Live

**`.env` file** — `/Users/buckadams/HCI_AI_Operating_System/.env`

This file contains all credentials. It is:
- Excluded from git (`.gitignore` entry)
- Backed up to the external drive (encrypted — keep drive physically secure)
- Never committed to GitHub
- Never shared in conversation logs

**Current secrets stored:**
```
DB_PASSWORD=          # PostgreSQL hci_admin password
HUBSPOT_ACCESS_TOKEN= # HubSpot Private App token
HCI_API_KEY=          # Gateway API key for write endpoints
N8N_API_KEY=          # n8n API JWT
OPENAI_API_KEY=       # OpenAI API (for AI summaries)
ANTHROPIC_API_KEY=    # Anthropic API (for Claude calls)
GOOGLE_CREDENTIALS=   # Google service account JSON path
MS_CLIENT_ID=         # Microsoft Azure App ID
MS_CLIENT_SECRET=     # Microsoft App secret
MS_TENANT_ID=         # Microsoft tenant
MS_REFRESH_TOKEN=     # Outlook OAuth refresh token
NGROK_AUTHTOKEN=      # ngrok authentication
```

### Rules for Credentials

1. **Never hardcode** — always read from `os.environ["KEY_NAME"]`
2. **Never log** — credentials must never appear in log files or API responses
3. **Never commit** — `.env` stays local only
4. **Never share** — do not paste credentials in conversation with AI
5. **Rotate if exposed** — if a key appears in any log or response, rotate it immediately

---

## 29.3 API Key Authentication

**API Key:** `hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6`

This key gates all write operations on the gateway. Anyone with this key can:
- Send tasks to Claude Code via `/gateway/agent/handoff`
- Create approval items
- Write files to Drive
- Trigger batch operations

**Do NOT share this key** with clients, trade partners, or anyone outside the AI team (Buck, GBT, Claude Code).

**Rotation procedure:**
1. Generate new key: `python3 -c "import secrets; print('hci-' + secrets.token_hex(16))"`
2. Update `.env` → `HCI_API_KEY=new_key`
3. Restart FastAPI: `launchctl stop com.hci.api-server && launchctl start com.hci.api-server`
4. Update GBT onboarding doc with new key
5. Update Claude Code's CLAUDE.md with new key
6. Test: `curl -X POST .../gateway/agent/handoff -H "X-API-Key: new_key" ...`

---

## 29.4 Access Control by Role

| Role | System Access | What They Can Do |
|------|-------------|-----------------|
| Buck Adams (PM & SS, Hendrickson Construction; HCI-AI Owner) | Full admin | Approve/reject everything, access all data, override any AI decision |
| Claude Code | API + local filesystem | Read all data, write code, create approval items, post handoffs |
| GBT (ChatGPT) | Gateway read endpoints + handoff write | Read all project data, send tasks to Claude Code, cannot directly write to DB or files |
| Browser Claude | GitHub + specific Drive paths | Program repository governance, file management |
| n8n | API localhost:8000 | Call all API endpoints as authenticated service |
| Jim Hendrickson (SS) | ntfy (receive) | Receive daily brief on phone |
| Trade Partners | Client portal (read-only) | `/gateway/role/client/{code}` — their project data only |

---

## 29.5 Network Security

### What Is Exposed Publicly (via ngrok)

The ngrok tunnel exposes the FastAPI gateway at the static URL. **Only `/gateway/*` routes are intended for external access.** However, the full API is technically reachable if someone knows the URL.

**Mitigations:**
- API key required for all write operations
- Read endpoints return only non-PII project intelligence
- No admin endpoints exposed (no DROP, no schema changes, no user management)
- ngrok free tier has rate limiting built in

**For production hardening (post-Gate 5):** Consider restricting non-gateway routes to localhost-only.

### What Is NOT Exposed

- PostgreSQL (port 5432 — Docker network only, not published to host network)
- Redis (port 6379 — Docker network only)
- Qdrant (port 6333 — localhost only, not in ngrok)
- n8n (port 5678 — localhost only)
- MCP Server (port 8080 — localhost only, Claude Code only)

---

## 29.6 Data Classification

| Data Type | Classification | Storage | Who Can See |
|-----------|--------------|---------|-------------|
| Contract values | Confidential | DB only | Buck, AI team only |
| Vendor emails/phones | Confidential | DB only | Buck, AI team only |
| Client contact info | Confidential | DB + HubSpot | Buck, AI team only |
| Project health scores | Internal | DB + gateway | AI team + Jim (SS) |
| RFIs, submittals | Internal | DB | AI team + assigned roles |
| Daily logs | Internal | DB | AI team + Jim |
| Bid amounts | Confidential | DB | Buck, AI team only |
| Lessons learned | Internal | DB + Qdrant | AI team |
| Historical costs | Confidential | DB + Qdrant | Buck, AI team only |

**Client-facing portal (`/gateway/role/client/{code}`):** Shows only project health, open RFIs, and change orders for their specific project. No financials, no vendor details, no internal risk notes.

---

## 29.7 Incident Response — Security

**If API key is exposed or you suspect unauthorized access:**

1. Immediately rotate the key (Section 29.3)
2. Check gateway_request_log for the last 24 hours
3. Check if any approval_queue items were created by unknown sources
4. Check HubSpot audit log for unexpected changes
5. Report to Buck — do not attempt to cover up or handle silently
6. Document in CHANGELOG.md with [SECURITY] tag

**If `.env` is exposed:**
1. Rotate ALL credentials, not just the one exposed
2. Revoke HubSpot Private App and create new
3. Revoke and refresh Microsoft OAuth tokens
4. Update Google service account credentials
5. Generate new ngrok auth token

---

## 29.8 Git & Code Security

- `.env` is in `.gitignore` — verified working
- No credentials in code comments
- No credentials in commit messages
- All DB passwords come from `os.environ`
- API key validation done in middleware (never in individual routes)
- No `--no-verify` bypass unless Buck explicitly requests

---

*Cross-reference: Chapter 24 (Approval Queue), Chapter 26 (Emergency), Chapter 31 (Change Management)*
