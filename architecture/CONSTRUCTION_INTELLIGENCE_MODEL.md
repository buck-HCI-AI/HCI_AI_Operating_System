# HCI AI — Construction Intelligence Model
*Phase 2 / Phase 3 | Updated: 2026-06-27*

## Overview

The Construction Intelligence Model describes how the HCI AI Operating System
transforms raw construction project data into actionable intelligence for
Superintendents, Project Managers, and Leadership.

## Intelligence Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: PREDICTIVE INTELLIGENCE                                │
│  Schedule risk · Budget risk · Permit delay · Procurement gap   │
│  Trade conflict · Cash flow risk · Inspection risk              │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: CROSS-PROJECT INTELLIGENCE                             │
│  Portfolio health matrix · Company snapshot                     │
│  Vendor performance · Procurement summary · Schedule trends     │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: PROJECT BRAIN (per-project)                            │
│  Health scoring · Risk detection · AI narrative                 │
│  Decision tracking · Data completeness · Snapshot history      │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: OPERATIONAL INTELLIGENCE (role-based)                  │
│  SS Daily Console · PM Weekly Console · Leadership Dashboard    │
├─────────────────────────────────────────────────────────────────┤
│  FOUNDATION: Raw Data Sources                                    │
│  Houzz · HubSpot · Outlook · Google Drive · Manual entry       │
└─────────────────────────────────────────────────────────────────┘
```

## Data Sources

| Source | Connector | Entities | Freshness Target |
|--------|-----------|----------|-----------------|
| Houzz | Browser extraction | Schedule, budget, COs, tasks | Weekly |
| HubSpot | Private App API | Deals, contacts, notes | Daily |
| Microsoft Outlook | OAuth2 | Email, calendar | Real-time |
| Google Drive | OAuth2 | SOPs, bid trackers, reports | Daily |
| PostgreSQL | Internal | All structured data | Live |

## Health Scoring Algorithm

```
RED:    any critical risk detected
YELLOW: any high risk detected (but no critical)
GREEN:  no critical or high risks
```

Risk categories:
- **PROC-001**: Open bids >14 days without response
- **SCHED-001/002/003**: Schedule variance at high/critical level
- **BUDGET-001/002**: Budget overrun or committed > 90%
- **DEC-001**: Open decisions >3 days without action
- **DATA-001**: Data completeness <60%

## Projects

| ID | Code | Name | PM | SS |
|----|------|------|----|----|
| 1  | 64EW | 64 Eastwood | TBD | TBD |
| 2  | 101F | 101 Francis | TBD | TBD |
| 3  | 1355R | 1355 Riverside | TBD | TBD |
| 4  | 83SB | 83 Sagebrusch | TBD | TBD |

## Key Endpoints

- `GET /api/v1/services/predictive-engine/{id}/predictions` — 7 forward-looking risks
- `GET /api/v1/services/cross-project/health-matrix` — portfolio health
- `GET /api/v1/services/project-brain/{id}/intelligence` — full project snapshot
- `GET /api/v1/services/system-auditor/run` — system self-evaluation
