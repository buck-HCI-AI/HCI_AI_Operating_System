# CYCLE 32 — GBT SPRINT 7 PRIORITY 4
# QuickBooks Integration Architecture
**HCI AI OS | Hendrickson Construction, Inc.**
**Date:** 2026-07-02
**Cycle:** 32
**Type:** Sprint 7 Priority 4 — QuickBooks Integration
**Status:** Implementation-ready, pending Buck QuickBooks authorization

---

## CHIEF ARCHITECT PRINCIPLE

> "QuickBooks is the accounting system of record. HCI AI OS should not replace it. HCI AI OS should consume QuickBooks actuals, connect them to project intelligence, and use them for budget-to-actual and forecast analysis."
>
> "No automatic accounting writes. No HCI → QB write occurs without explicit Buck approval."

---

## BUCK ACTION REQUIRED

Before implementation begins, Buck must:
1. Log into QuickBooks Online
2. Visit: https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0
3. Create an Intuit Developer App (or use existing HCI app)
4. Get: Client ID + Client Secret
5. Set redirect URI to: https://[HCI-API-URL]/integrations/quickbooks/callback
6. Share Client ID + Client Secret with Code via environment variables:
   - QB_CLIENT_ID
   - QB_CLIENT_SECRET
   - QB_ENVIRONMENT (sandbox or production)

---

## 1) QUICKBOOKS OAUTH 2.0 FLOW

QuickBooks Online uses OAuth 2.0. Buck (or authorized QB admin) must grant consent before HCI AI OS can access company accounting data. Intuit returns an authorization code, which the app exchanges for access and refresh tokens tied to a QuickBooks company realmId.

### Required Architecture
```
Buck authorizes Intuit app
        ↓
Intuit redirects to HCI callback with code + realmId
        ↓
HCI exchanges code for access_token + refresh_token
        ↓
Tokens stored encrypted in quickbooks_connections table
        ↓
WF-QB-001 refreshes token before sync
        ↓
HCI pulls accounting actuals from QB
```

### Required Endpoints (to build)
```
GET  /integrations/quickbooks/connect     -- Redirect Buck to Intuit auth page
GET  /integrations/quickbooks/callback    -- Receive code + realmId from Intuit
POST /integrations/quickbooks/disconnect  -- Revoke and clear tokens
GET  /integrations/quickbooks/status      -- Check connection health
POST /integrations/quickbooks/sync        -- Manual sync trigger (super_admin only)
GET  /integrations/quickbooks/sync-log    -- View sync history
```

---

## 2) DATA SYNC STRATEGY

### QB → HCI (Read Only)

| QB Entity | Maps To HCI | Purpose |
|-----------|------------|---------|
| Vendor | vendors table | Vendor master sync |
| Bill / Expense | budget_line_items.actual_cost_to_date | Actuals tracking |
| Purchase | budget_line_items.actual_cost_to_date | PO actuals |
| Payment | budget_line_items | Payment tracking |
| Invoice | Financial reporting | Client billing |
| Account (Chart of Accounts) | Cost code mapping | Budget structure |
| Customer | client reference | Project-client link |

### HCI → QB (Restricted)
- **NEVER automatic**
- Only with explicit Buck approval per transaction
- Approved operations: customer/project mapping, approved invoice draft creation
- No automatic accounting writes

### Sync Frequency
- Daily sync: WF-QB-001 runs at 04:30 local time (before morning brief)
- Manual sync: available from Mission Control (super_admin only)
- Token refresh: before each sync, if expires_at < now + 10 minutes

---

## 3) DDL

### quickbooks_connections table
```sql
CREATE TABLE IF NOT EXISTS quickbooks_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    realm_id TEXT NOT NULL UNIQUE,  -- QB company ID
    company_name TEXT,
    
    access_token TEXT,              -- encrypted at rest
    refresh_token TEXT,             -- encrypted at rest
    
    access_token_expires_at TIMESTAMPTZ NOT NULL,
    refresh_token_expires_at TIMESTAMPTZ,
    
    status TEXT NOT NULL DEFAULT 'active',
    -- active | expired | revoked | error
    
    authorized_by TEXT,             -- Buck's user_id
    authorized_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_sync_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### quickbooks_sync_log table
```sql
CREATE TABLE IF NOT EXISTS quickbooks_sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    connection_id UUID REFERENCES quickbooks_connections(id),
    project_id TEXT,
    realm_id TEXT,
    
    qb_entity_type TEXT NOT NULL,
    -- Vendor | Bill | Purchase | Payment | Invoice | Account
    
    qb_entity_id TEXT,
    
    sync_direction TEXT NOT NULL DEFAULT 'QB_TO_HCI',
    -- QB_TO_HCI | HCI_TO_QB
    
    operation TEXT NOT NULL,
    -- fetch | upsert | refresh_token | map | error
    
    status TEXT NOT NULL,
    -- success | failed | skipped | retrying
    
    message TEXT,
    records_processed INTEGER NOT NULL DEFAULT 0,
    
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    error_detail TEXT,
    
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_qb_sync_direction CHECK (
        sync_direction IN ('QB_TO_HCI', 'HCI_TO_QB')
    ),
    CONSTRAINT chk_qb_sync_status CHECK (
        status IN ('success', 'failed', 'skipped', 'retrying')
    )
);

CREATE INDEX IF NOT EXISTS idx_qb_sync_project ON quickbooks_sync_log(project_id);
CREATE INDEX IF NOT EXISTS idx_qb_sync_entity ON quickbooks_sync_log(qb_entity_type, qb_entity_id);
CREATE INDEX IF NOT EXISTS idx_qb_sync_status ON quickbooks_sync_log(status);
CREATE INDEX IF NOT EXISTS idx_qb_sync_created ON quickbooks_sync_log(created_at DESC);
```

---

## 4) SYNC DIRECTION RULE

```
QuickBooks = accounting actuals, source of truth
HCI AI OS  = project intelligence, forecasting, and variance analysis
```

### QB → HCI (Daily, automated)
- Vendors → vendors table (create/update, never delete)
- Bills/Expenses/Purchases → budget_line_items.actual_cost_to_date
- Payments → budget_line_items payment tracking
- Chart of Accounts → cost code master reference
- Invoices → financial reporting views

### HCI → QB (Manual, Buck approval only)
- No automated writes
- Approved customer/project mapping
- Approved invoice draft creation
- Manual only, never triggered by automation

---

## 5) WF-QB-001 — DAILY QUICKBOOKS SYNC

**Workflow name:** WF-QB-001 QuickBooks Actual Cost Sync
**Trigger:** Daily at 04:30 local time. Optional manual run from Mission Control.

**Steps:**
1. Load active QuickBooks connection
2. Check token expiration
3. Refresh token if needed (access_token_expires_at < now + 10 minutes)
4. Sync vendors
5. Sync chart of accounts
6. Sync bills / expenses / purchases
7. Sync payments
8. Sync invoices
9. Map QB records to HCI projects
10. Update budget_line_items.actual_cost_to_date
11. Recalculate budget variance summaries
12. Log sync results to quickbooks_sync_log
13. Emit domain event: QB_SYNC_COMPLETED
14. If failures: write to dead letter queue + notify Mission Control

---

## 6) ERROR HANDLING

### Failed Sync
- Write quickbooks_sync_log.status = 'failed'
- Preserve raw error payload
- Do NOT overwrite existing financial data with partial/failed sync
- Mission Control shows sync failure

### Token Expired / Revoked
- Set quickbooks_connections.status = 'expired' or 'revoked'
- Notify Buck/accounting via Mission Control
- Disable QB sync until reauthorized

### Rate Limits (Intuit API)
- Use exponential backoff
- Retry transient failures
- Do not run parallel full sync jobs for same realm_id

### Data Mapping Failure
- If QB record cannot map to HCI project or cost line: store as unmapped in sync log, do not discard
- Surface "unmapped accounting records" in Mission Control for Buck to resolve

---

## 7) IMPLEMENTATION ACCEPTANCE CRITERIA

QuickBooks Integration Phase 1 is complete when:
- OAuth connect/callback/status endpoints exist
- Tokens are encrypted at rest
- `quickbooks_sync_log` table exists
- `quickbooks_connections` table exists
- WF-QB-001 can refresh token and run daily sync
- QB actuals update `budget_line_items.actual_cost_to_date`
- Budget summaries recalculate after sync
- Failed syncs are logged and visible in Mission Control
- No HCI → QB write occurs without explicit Buck approval

---

## NOTE ON BUILDERTREND

HCI does NOT use Buildertrend. All project management, field reporting, and construction OS functions are built in-house in HCI AI OS. QuickBooks is the only external financial system.

---

*Cycle 32 complete. QuickBooks Integration spec committed.*
*Implementation blocked pending: Buck QB OAuth authorization + Client ID/Secret.*
*When Buck provides credentials → Code can implement immediately.*
*Next: CYCLE 33 — Telegram Integration*
