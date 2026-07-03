# Identity & Permissions Model
**Version:** 1.0 | **Date:** 2026-06-26

---

## Roles

| Role | Actor Examples | Authority Level | Description |
|---|---|---|---|
| `owner` | Buck Adams | 5 | Final approval authority within HCI-AI (Buck Adams: PM & Superintendent, Hendrickson Construction, Inc.; Owner, HCI-AI) |
| `administrator` | admin | 5 | System admin; user management |
| `pm` | pm | 3 | Project manager; workflow execution |
| `estimator` | estimator | 3 | Bid preparation and scope review |
| `superintendent` | super | 3 | Field execution; daily logs; safety |
| `accounting` | accounting | 3 | Financial review; payment approvals |
| `contracts` | contracts_team | 2 | Subcontract initiation; compliance |
| `architect` | architect | 2 | RFI and submittal approvals |
| `engineer` | engineer | 2 | Technical RFI approvals; field confirmations |
| `client` | client | 2 | Change order approval; project visibility |
| `ai_agent` | AI | 1 | Draft content; read data |
| `system` | system | 1 | Internal events only |

## Permissions Matrix

| Permission | owner | admin | pm | estimator | super | accounting | contracts | architect | engineer | client | ai_agent |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| approve_budget | ✅ | ✅ | | | | | | | | | |
| approve_award | ✅ | ✅ | | | | | | | | | |
| approve_contract | ✅ | ✅ | | | | | | | | | |
| approve_change_order | ✅ | | | | | | | | | ✅ | |
| approve_exception | ✅ | ✅ | | | | | | | | | |
| issue_commitment | ✅ | | | | | | | | | | |
| approve_payment | | | | | | ✅ | | | | | |
| approve_rfi | | | | | | | | ✅ | ✅ | | |
| approve_submittal | | | | | ✅ | | | ✅ | | | |
| approve_internal | | | ✅ | ✅ | | | | | | | |
| approve_safety | | | | | ✅ | | | | | | |
| draft_sop | | | ✅ | ✅ | | | | | | | |
| confirm_inputs | | | ✅ | ✅ | | | | | | | |
| confirm_field | | | | | ✅ | | | | ✅ | | |
| log_daily | | | | | ✅ | | | | | | |
| request_approval | | | ✅ | | | | | | | | |
| initiate_contract | | | | | | | ✅ | | | | |
| confirm_compliance | | | | | | | ✅ | | | | |
| draft_content | | | | | | | | | | | ✅ |
| read_data | | | | | | | | | | | ✅ |
| view_project | | | ✅ | ✅ | ✅ | ✅ | | ✅ | ✅ | ✅ | |
| view_all | ✅ | ✅ | | | | ✅ | | | | | |
| manage_users | | ✅ | | | | | | | | | |

## API

```
GET  /api/v1/platform/identity/users                    — list all actors
GET  /api/v1/platform/identity/users/{name}             — get actor + permissions
GET  /api/v1/platform/identity/users/{name}/permissions — permission list + authority level
GET  /api/v1/platform/identity/users/{name}/can/{perm}  — single permission check
POST /api/v1/platform/identity/users                    — create/update actor
GET  /api/v1/platform/identity/roles                    — list roles
```

## Usage in Code

```python
from identity.identity_service import IdentityService

# Check permission
if IdentityService.can("Buck Adams", "approve_budget"):
    # proceed

# Require permission (raises PermissionError if denied)
IdentityService.require("pm", "approve_award")

# Get authority level (owner=5, pm=3, ai=1)
level = IdentityService.role_level("Buck Adams")  # → 5
```
