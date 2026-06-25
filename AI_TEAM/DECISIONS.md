# DECISIONS.md
**Engineering decisions log — why we did what we did**
Most recent first.

---

## DEC-006 — Claude Code Operating Charter adopted (2026-06-24)
**Decision:** Adopt `HCI_AI_Claude_Code_Operating_Charter_v0.1` as the governing document for Claude Code's role and behavior.
**Rationale:** Formalizes division of labor (ChatGPT = architect, Claude Code = implementer, Buck = owner/decider). Required AI_TEAM file set established.
**Impact:** AI_TEAM/ directory created with 6 required files. Session startup/shutdown protocol now mandatory.

---

## DEC-005 — Repo named HCI_AI_Operating_System (2026-06-24)
**Decision:** Repository at `/Users/buckadams/HCI_AI_Operating_System/` (not `HCI_OS`).
**Rationale:** Local Architecture PDF specifies this exact name. Renamed after initial creation.
**Impact:** All path references use `HCI_AI_Operating_System`.

---

## DEC-004 — Integration layer uses direct Python + n8n SQLite decryption (2026-06-24)
**Decision:** Python integrations decrypt OAuth tokens from n8n SQLite rather than calling n8n credential API or storing tokens separately.
**Rationale:** n8n credential API doesn't expose raw tokens. Avoids duplicate credential management. Keeps n8n as the single credential store.
**Impact:** `credentials.py` uses CryptoJS EVP AES-256-CBC decryption. Key stored in `.env`.

---

## DEC-003 — HubSpot auth: use value field directly (2026-06-24)
**Decision:** HubSpot credential `value` field already contains the full `Bearer pat-na2-...` string. Do NOT prepend `"Bearer "`.
**Rationale:** n8n stores it with prefix. Adding `f"Bearer {token}"` caused 401 errors.
**Impact:** All HubSpot API calls use `Authorization: {cred["value"]}` directly.

---

## DEC-002 — WF-007 Send Draft nodes reference upstream node directly (2026-06-24)
**Decision:** `Send Draft to Buck` nodes use `$('Level Bids & Build Report').first().json.html` instead of `$json.html`.
**Rationale:** The `Upload BT xlsx` node runs after the leveling node and returns only `{id, name}`, wiping `$json`. Referencing the upstream node by name preserves the data.
**Impact:** WF-007 Send Draft bug resolved. Emails now contain correct subject and HTML body.

---

## DEC-001 — Build sequence: n8n first, Postgres/Qdrant/Redis next (2026-06-24)
**Decision:** n8n was already live when repo was created. Postgres/Qdrant/Redis are next before FastAPI/Agents.
**Rationale:** Constitution build sequence: Docker → Postgres → Qdrant → Redis → FastAPI → OpenClaw → n8n → Agents. n8n already done; data layer is the gap.
**Impact:** NEXT_TASK.md TASK-001 = `docker-compose up -d postgres qdrant redis`.
