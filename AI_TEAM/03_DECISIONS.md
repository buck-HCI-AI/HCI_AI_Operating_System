# 03_DECISIONS.md
**Engineering decisions log — why we did what we did**
Most recent first.

---

## DEC-008 — infrastructure/ is canonical IaC, root docker-compose.yml is legacy (2026-06-25)
**Decision:** All Docker infrastructure lives in `infrastructure/docker-compose.yml`. Root `docker-compose.yml` (n8n only now) is legacy and will be absorbed or removed when services migrate.
**Rationale:** Infrastructure Phase 1 directive requires `infrastructure/` directory as portable, version-controlled IaC. Root compose was pre-existing partial work.
**Impact:** New services added to `infrastructure/docker-compose.yml` only. Mac mini M4 Pro setup starts from `infrastructure/`.

---

## DEC-007 — MinIO added as object store (2026-06-25)
**Decision:** MinIO added as the fourth infrastructure service alongside Postgres, Redis, Qdrant.
**Rationale:** Infrastructure Phase 1 directive specifies MinIO for bid PDFs, drawings, AI artifacts, backups, site photos.
**Impact:** 4 buckets created on init: `hci-documents`, `hci-ai-artifacts`, `hci-backups`, `hci-images`. Console at localhost:9001.

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

## DEC-007 — Workflow Consolidation: two automation stacks coexist (2026-06-25)
**Decision:** Python/FastAPI workflows (WF-001 through WF-006) and n8n (WF-007) run in parallel. Do not merge them. n8n WF-007 migrates to Postgres in Phase 9.4; new workflows are Python only.
**Rationale:** WF-007 is live and working. Rewriting it in Python before Postgres has bid data would break Buck's daily bid leveling with no benefit.
**Impact:** New workflows = Python. WF-007 = n8n until Phase 9.4.

---

## DEC-006 — service.py renamed to {name}_svc.py (2026-06-25)
**Decision:** Each service implementation file is named `{service_name}_svc.py`, not `service.py`.
**Rationale:** Python's sys.modules caches the first module loaded as 'service'. All 9 services had the same filename, causing import collisions when loaded by FastAPI.
**Impact:** All routes.py files import from `{name}_svc` not `service`.

---

## DEC-005 — resolve_project_id() instead of project_number column (2026-06-25)
**Decision:** Added `resolve_project_id(project_number)` to BaseIntelligenceService. Extracts numeric prefix from short code ("64EW" → "64"), matches on projects.name ILIKE.
**Rationale:** The projects table has no project_number column. Short codes like "64EW" are user-facing identifiers only.
**Impact:** All intelligence services use resolve_project_id() for project lookup.

---

## DEC-004 — BOOK_00 as single source of truth (2026-06-25)
**Decision:** BOOK_00 is the master specification. PDFs in 01_Engineering_Library/ are source artifacts. docs/ has inventory/sequence/overlap docs. AI_TEAM/ has live state. No architecture docs outside these locations.
**Rationale:** Specs were scattered across architecture/, BOOK_00/architecture/, docs/, workflows/, AI_TEAM/ — creating confusion about what was authoritative.
**Impact:** All future specs go in BOOK_00 sections. AI_TEAM/ is status, not spec.

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
