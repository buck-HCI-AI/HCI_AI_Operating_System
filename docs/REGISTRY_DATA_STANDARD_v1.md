# Registry Data Standard v1.0

## The Three Core Registries

### 1. Vendor Registry (`vendors` table)

Every subcontractor and supplier HCI works with. Single source of truth for who can bid, who is preferred, and who is blacklisted.

**Required fields on create:**
- `vendor_name`
- `primary_trade`
- `csi_division_id`
- `preferred_status` (approved / preferred / probation / blacklisted)

**Sync sources:**
- HubSpot CRM (daily) — `hubspot_company_id` FK
- Manual entry

**Never duplicate:** Check `hubspot_company_id` and `vendor_name` before inserting.

### 2. CSI Division Registry (`csi_divisions` table)

16-division MasterFormat. Seeded once, rarely changes. Every bid package, vendor, cost record, and document references a CSI division.

**Do not add custom codes** without Buck approval. Use division notes for sub-categories.

### 3. Project Registry (`projects` table)

Every active and completed HCI project. `project_number` is the system key (64EW, 101F, 1355R, 83SB).

**project_aliases** are critical for fuzzy matching:
- `64EW` → aliases: `['64 Eastwood Dr', 'Eastwood']`
- `1355R` → aliases: `['1355 Riverside Dr', 'Riverside']`

## Data Quality Rules

1. No duplicate vendors by `hubspot_company_id`.
2. No duplicate contacts by `hubspot_contact_id`.
3. Every `vendor_trade_mapping` must reference a valid `csi_division_id`.
4. `preferred_status` must be one of: preferred | approved | probation | blacklisted.
5. `performance_rating` range: 1.0–5.0. NULL if never rated.
6. `insurance_status` must be verified annually — set `insurance_expiry` date.

## HubSpot Sync Rule

HubSpot is read-only from the AI system. Never write back to HubSpot from these tables without Buck's explicit approval. The `source_system = 'hubspot'` and `source_reference = hubspot_id` fields track the origin.
