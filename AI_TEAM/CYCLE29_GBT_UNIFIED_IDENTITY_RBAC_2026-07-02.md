# CYCLE 29 — GBT SPRINT 7 PRIORITY 2
# Unified Identity and RBAC Architecture
**HCI AI OS | Hendrickson Construction, Inc.**
**Date:** 2026-07-02
**Cycle:** 29
**Type:** Sprint 7 Priority 2 — Unified Identity + RBAC

---

## OVERVIEW

HCI AI OS now has 35+ routers. Each router must not invent its own auth rules.
This spec defines one identity layer that answers:
- Who are you?
- What role do you have?
- Which project can you access?
- Which action are you allowed to perform?

---

## 1) ROLES

### Role Enum
```
super_admin          -- Buck
project_manager
superintendent
field_worker
client
vendor_contact
ai_agent
```

### Role Intent
| Role | Purpose |
|------|---------|
| super_admin | Buck / final authority / full access |
| project_manager | Manage assigned projects |
| superintendent | Field operations for assigned projects |
| field_worker | Submit field data only |
| client | Curated client portal only |
| vendor_contact | Vendor/subcontractor-facing access |
| ai_agent | GBT, Claude Code, Browser Claude, n8n service access |

---

## 2) PERMISSION MATRIX

### Router Access
| Router | Buck | PM | Super | Field | Client | Vendor | AI Agent |
|--------|------|----|----|-------|--------|--------|----------|
| /executive | ✅ | Read assigned | ❌ | ❌ | ❌ | ❌ | ✅ read |
| /projects | ✅ | Assigned | Assigned read | Limited | Own project | ❌ | ✅ |
| /brain | ✅ | Assigned | Assigned limited | ❌ | ❌ | ❌ | ✅ |
| /rfis | ✅ | CRUD assigned | Create/read assigned | Create | ❌ | ❌ | ✅ |
| /procurement | ✅ | CRUD assigned | Read assigned | ❌ | ❌ | ❌ | ✅ |
| /finance | ✅ | Assigned read/write | ❌ | ❌ | ❌ | ❌ | ✅ |
| /vendors | ✅ | Read/write | Read | ❌ | ❌ | Own data | ✅ |
| /photos | ✅ | Assigned | Assigned | Submit only | Own project | ❌ | ✅ |
| /punch | ✅ | Assigned | Assigned | Submit only | Own project | ❌ | ✅ |
| /warranty | ✅ | Assigned | Assigned | Submit only | Own project | ❌ | ✅ |
| /mobile | ✅ | ✅ | ✅ | ✅ submit | ❌ | ❌ | ✅ |
| /predict | ✅ | Assigned | Assigned read | ❌ | ❌ | ❌ | ✅ |
| /client | ✅ | Assigned | ❌ | ❌ | Own project | ❌ | ✅ |
| /weather | ✅ | Assigned | Assigned | ❌ | ❌ | ❌ | ✅ |
| /cost | ✅ | Assigned read/write | ❌ | ❌ | ❌ | ❌ | ✅ |
| /schedule | ✅ | Assigned | Assigned read | ❌ | ❌ | ❌ | ✅ |
| /auth | ✅ | ✅ own | ✅ own | ✅ own | ✅ own | ✅ own | ✅ |
| /gateway | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### Special Permission Rules
- **Clients** can only see their own project — never see other project data, internal notes, financial details
- **Vendors** can only see their own performance data, their own POs
- **Field workers** can submit (POST) but cannot read other users' submissions
- **AI agents** use api_key not JWT — all AI agents have read access across assigned scopes
- **Buck** (super_admin) can impersonate any role for support/testing via /auth/impersonate

---

## 3) POSTGRESQL DDL

### users table
```sql
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    
    -- project scoping
    assigned_project_ids TEXT[] NOT NULL DEFAULT '{}',
    
    -- vendor scoping (for vendor_contact role)
    vendor_id UUID,
    
    -- client scoping (for client role)
    client_project_id TEXT,
    
    -- impersonation (super_admin only)
    impersonation_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    
    password_hash TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_users_role CHECK (
        role IN (
            'super_admin',
            'project_manager',
            'superintendent',
            'field_worker',
            'client',
            'vendor_contact',
            'ai_agent'
        )
    )
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(active);
CREATE INDEX IF NOT EXISTS idx_users_client_project ON users(client_project_id);
```

### sessions table
```sql
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    jwt_id TEXT NOT NULL UNIQUE,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    
    ip_address TEXT,
    user_agent TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_jwt_id ON sessions(jwt_id);
CREATE INDEX IF NOT EXISTS idx_sessions_revoked ON sessions(revoked);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
```

### api_keys table (for AI agents)
```sql
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    agent_name TEXT NOT NULL UNIQUE,
    key_hash TEXT NOT NULL UNIQUE,
    
    role TEXT NOT NULL DEFAULT 'ai_agent',
    scopes JSONB NOT NULL DEFAULT '[]'::jsonb,
    
    active BOOLEAN NOT NULL DEFAULT TRUE,
    last_used_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    
    CONSTRAINT chk_api_keys_role CHECK (
        role = 'ai_agent'
    )
);

CREATE INDEX IF NOT EXISTS idx_api_keys_agent_name ON api_keys(agent_name);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(active);
```

### Optional: auth_audit_log table
```sql
CREATE TABLE IF NOT EXISTS auth_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    user_id UUID REFERENCES users(id),
    api_key_id UUID REFERENCES api_keys(id),
    
    action TEXT NOT NULL,  -- login, logout, token_refresh, impersonate_start, impersonate_end, permission_denied
    router TEXT,
    method TEXT,
    path TEXT,
    
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auth_audit_user ON auth_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_audit_timestamp ON auth_audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_auth_audit_action ON auth_audit_log(action);
```

---

## 4) AUTH MIDDLEWARE

### FastAPI Dependency Injection Pattern
```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

# JWT Bearer for human users
security_bearer = HTTPBearer()

# API Key Header for AI agents
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_bearer)
) -> UserContext:
    """Decode JWT, validate session, return UserContext"""
    token = credentials.credentials
    payload = decode_jwt(token)
    user = await get_user_by_id(payload["sub"])
    if not user.active:
        raise HTTPException(status_code=401, detail="User inactive")
    return UserContext(user=user, role=user.role)

async def get_current_agent(
    api_key: str = Security(api_key_header)
) -> UserContext:
    """Validate API key, return AI agent context"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    agent = await get_agent_by_key_hash(hash_key(api_key))
    if not agent or not agent.active:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return UserContext(agent=agent, role="ai_agent")

async def get_current_principal(
    user: UserContext = Depends(get_current_user_or_agent)
) -> UserContext:
    """Unified: accepts either JWT user or API key agent"""
    return user
```

### Role Enforcement Pattern
```python
def require_role(*roles: str):
    """Dependency factory for role-based access"""
    async def checker(principal: UserContext = Depends(get_current_principal)):
        if principal.role not in roles and principal.role != "super_admin":
            raise HTTPException(status_code=403, detail="Insufficient role")
        return principal
    return checker

def require_project_access(project_id_param: str = "project_id"):
    """Dependency factory for project-scoped access"""
    async def checker(
        project_id: str,
        principal: UserContext = Depends(get_current_principal)
    ):
        if principal.role == "super_admin":
            return principal
        if project_id not in principal.assigned_project_ids:
            raise HTTPException(status_code=403, detail="Not assigned to project")
        return principal
    return checker
```

### Router Usage Pattern
```python
# Example: /executive router
@router.get("/brief/today")
async def get_morning_brief(
    principal: UserContext = Depends(require_role("super_admin", "project_manager", "ai_agent"))
):
    # principal.role confirmed, project scope enforced if needed
    ...

# Example: /client router  
@router.get("/overview")
async def get_client_overview(
    principal: UserContext = Depends(require_role("client", "super_admin"))
):
    # Client sees ONLY their assigned project
    project_id = principal.client_project_id
    ...
```

---

## 5) /auth ROUTER

### Endpoints
| Method | Path | Description | Auth Required |
|--------|------|-------------|--------------|
| POST | /auth/login | Email+password → JWT | No |
| POST | /auth/refresh | Refresh JWT | JWT (valid) |
| POST | /auth/logout | Revoke session | JWT |
| GET | /auth/me | Get current user context | JWT or API key |
| POST | /auth/impersonate | Buck auth-as any user | super_admin only |
| POST | /auth/impersonate/end | End impersonation | super_admin only |
| GET | /auth/users | List all users | super_admin only |
| POST | /auth/users | Create user | super_admin only |
| PATCH | /auth/users/{id} | Update user | super_admin only |
| DELETE | /auth/users/{id}/deactivate | Deactivate user | super_admin only |
| POST | /auth/api-keys | Create AI agent key | super_admin only |
| GET | /auth/api-keys | List API keys | super_admin only |
| DELETE | /auth/api-keys/{id}/revoke | Revoke API key | super_admin only |

### Buck Impersonation Flow
```
POST /auth/impersonate {"target_user_id": "uuid"}
→ Returns impersonation JWT with original_user_id stored
→ Buck can act as that user for support/debugging
POST /auth/impersonate/end
→ Returns Buck's original JWT
→ All impersonation actions logged to auth_audit_log
```

---

## 6) PYDANTIC SCHEMAS

```python
class UserRole(str, Enum):
    super_admin = "super_admin"
    project_manager = "project_manager"
    superintendent = "superintendent"
    field_worker = "field_worker"
    client = "client"
    vendor_contact = "vendor_contact"
    ai_agent = "ai_agent"

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    role: UserRole
    assigned_project_ids: List[str] = []
    vendor_id: Optional[UUID] = None
    client_project_id: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: UserRole
    assigned_project_ids: List[str]
    active: bool
    created_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class UserContext(BaseModel):
    user_id: UUID
    email: str
    role: UserRole
    assigned_project_ids: List[str]
    client_project_id: Optional[str]
    vendor_id: Optional[UUID]
    is_impersonating: bool = False
    original_user_id: Optional[UUID] = None
```

---

## 7) TEST GATES

### Migration Tests
- users table created with correct columns
- sessions table created with FK to users
- api_keys table created
- role CHECK constraint enforces valid roles
- invalid role rejected at DB level

### Auth Flow Tests
- login with valid credentials returns JWT
- login with invalid password returns 401
- expired JWT returns 401
- revoked session returns 401
- inactive user returns 401

### Role Tests
- super_admin can access all routers
- project_manager cannot access /executive reports for unassigned projects
- superintendent cannot write to /finance
- client cannot see other clients' projects
- client cannot see internal notes or financial data
- field_worker can POST to /mobile but cannot GET others' submissions
- vendor_contact can only see own vendor data
- ai_agent with valid api_key accesses read-scoped routes

### Impersonation Tests
- only super_admin can impersonate
- impersonation JWT carries original_user_id
- impersonation end restores original session
- all impersonation events logged to auth_audit_log

### API Key Tests
- valid api_key accepted in X-API-Key header
- revoked api_key returns 401
- expired api_key returns 401
- api_key with wrong scope returns 403

---

## 8) INTEGRATION NOTES

### Retrofit Plan for Existing Routers
All existing routers must be updated to add:
```python
principal: UserContext = Depends(get_current_principal)
```
Priority order (match implementation sprint order):
1. /vendors — add project_manager + super_admin only for writes
2. /procurement — add project_manager + super_admin
3. /photos — add field_worker submit + all read
4. /punch — lifecycle: superintendent creates, PM approves
5. /warranty — client read-only for own project
6. /finance — super_admin + PM only
7. /brain — ai_agent full, others scoped
8. /mobile — all authenticated users submit
9. /predict — PM + super_admin + ai_agent
10. /client — client sees own project only
11. /executive — super_admin + ai_agent

### JWT Configuration
```
Algorithm: HS256
Access token TTL: 8 hours (field crew full day)
Refresh token TTL: 30 days
Secret: stored in environment variable JWT_SECRET
```

### AI Agent Keys in Use
| Agent | Key Name | Scopes |
|-------|---------|--------|
| Browser Claude (BC) | bc_agent | read:all, write:gateway |
| Claude Code | code_agent | read:all, write:all |
| GBT (ChatGPT) | gbt_agent | read:specs |
| n8n workflows | n8n_agent | read:all, write:field |

---

*Cycle 29 complete. Unified Identity + RBAC spec committed.*
*Sprint 7 Priority 2 done.*
*Next: CYCLE 30 — Event Bus + Event Sourcing*
