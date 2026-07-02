# PERPLEXITY_INTEGRATION_SPEC.md
## HCI AI OS — Perplexity AI Integration Specification

**Chief Architect:** GBT (Cycle 8)
**Captured by:** Browser Claude
**Date:** 2026-07-01
**Context:** We already have Perplexity access. This spec defines exactly how to wire it in today.
**Status:** Implementation-ready for Claude Code — Sprint 4

---

## Architectural Rule

> **"Perplexity answers are evidence. They are not project facts until reviewed."**

Treat Perplexity as a **Research Service, never as the operational source of truth.** Results are stored as linked research artifacts with review status. Only after a PM or Estimator accepts findings should relevant information be incorporated into project records.

---

## Pipeline Architecture

```
PM / Estimator / Superintendent
           ↓
Gateway POST /research/query
           ↓
n8n WF-RS-001 Construction Research
           ↓
Perplexity API /chat/completions
           ↓
Structured JSON Response
           ↓
Gateway
           ↓
Mission Control / Project Brain (linked, not imported)
```

---

## Model Selection

### Default: `sonar`

Use for all standard construction research:
- Building code questions
- Product research
- Manufacturer documentation
- AHJ requirements
- Material availability
- General construction research

**Reasons:** Lower latency, lower cost, excellent web grounding, suitable for most operational questions.

### Escalate to: `sonar-pro`

Use only when research quality matters more than speed:
- Multi-code comparison (IRC vs IBC vs local amendment)
- Structural engineering references
- Product substitution analysis requiring deep spec review
- Technical specification review
- Large research reports
- Executive white papers

> **Do not make sonar-pro the default.** Reserve it for complex queries.

---

## n8n Workflow: WF-RS-001 Construction Research

**Workflow Name:** WF-RS-001 Construction Research
**Trigger:** HTTP Request
**Gateway endpoint:** POST /gateway/research/query

### Input Schema

```json
{
  "project": "101F",
  "requestor": "estimator",
  "topic": "material_cost",
  "query": "Current Denver copper pipe pricing 2-inch Type L",
  "priority": "normal"
}
```

**topic values:** `material_cost`, `building_code`, `product_research`, `ahj`, `vendor`, `schedule`, `general`
**priority values:** `normal` (sonar), `high` (sonar-pro)

### Node 1 — Validate

Required fields: `project`, `requestor`, `query`
Reject if missing. Return 400 with reason.

### Node 2 — Determine Model

```
IF topic IN ['building_code', 'product_research'] AND priority == 'high'
  model = 'sonar-pro'
ELSE
  model = 'sonar'
```

### Node 3 — HTTP Request to Perplexity

```
POST https://api.perplexity.ai/chat/completions
Authorization: Bearer {{PERPLEXITY_API_KEY}}
Content-Type: application/json
```

```json
{
  "model": "sonar",
  "messages": [
    {
      "role": "system",
      "content": "You are the HCI Construction Research Service. Return concise, factual answers. Requirements: Prefer manufacturer documentation. Prefer government code sources. Prefer AHJ sources. Prefer industry standards. Cite every source. Separate FACTS from OPINION. Never estimate building code requirements. If uncertain, say uncertain. Return markdown."
    },
    {
      "role": "user",
      "content": "{{query}}"
    }
  ],
  "temperature": 0.1
}
```

> **Use temperature 0.1 for consistency.** Never 0.7+ for research queries.

### Node 4 — Structure Response

```json
{
  "research_id": "RS-{{uuid}}",
  "project": "{{project}}",
  "requestor": "{{requestor}}",
  "query": "{{query}}",
  "topic": "{{topic}}",
  "provider": "Perplexity",
  "model": "{{model_used}}",
  "timestamp": "{{iso_timestamp}}",
  "response": "{{perplexity_content}}",
  "sources": ["{{citation_1}}", "{{citation_2}}"],
  "status": "Needs Review",
  "project_brain_linked": false
}
```

### Node 5 — Store in research_queries Table

Write the structured response to PostgreSQL `research_queries` table.
Do NOT write to Project Brain automatically.

### Node 6 — Return to Requestor

Return the structured JSON to the caller via the gateway.
Mission Control displays the result with a "Review" button.
PM/Estimator reviews and clicks "Accept" to link to Project Brain.

---

## Standard System Prompt

Use this fixed system prompt for all construction research queries:

```
You are the HCI Construction Research Service.

Return concise, factual answers.

Requirements:
- Prefer manufacturer documentation.
- Prefer government code sources.
- Prefer AHJ sources.
- Prefer industry standards.
- Cite every source.
- Separate FACTS from OPINION.
- Never estimate building code requirements.
- If uncertain, say uncertain.
- Return markdown.
```

---

## Top 3 Use Cases to Wire In First

### Use Case 1: Material Cost Intelligence (Highest Priority)

**Who uses it:** Estimator
**Trigger:** Estimator asks during bid prep or procurement
**Example queries:**
- "Current Denver steel pricing per ton"
- "Copper pipe pricing trends Q3 2026"
- "LVL lumber lead times from Boise Cascade"
- "Drywall availability shortage update"
- "Ready-mix concrete pricing Colorado Springs"

**Estimator benefit:** Better ROM estimates, better procurement timing, market awareness.

**User prompt template:**
```
What is the current market price for [MATERIAL] in [LOCATION]?
Include: price range, unit, date of data, regional factors, and any shortage conditions.
Cite sources.
```

---

### Use Case 2: Building Code / AHJ Research

**Who uses it:** PM, Estimator, Superintendent
**Trigger:** Code question during design review, permit application, or field issue
**Example queries:**
- "2024 IRC stair riser requirements"
- "Aspen Colorado snow load requirements"
- "Pitkin County permitting process for additions"
- "Colorado energy code window U-value requirements"
- "Fire separation requirements between garage and living space IRC 2021"

> Every answer includes citations and the reminder: **verify with the authority having jurisdiction before acting.**

**User prompt template:**
```
What are the [CODE/REQUIREMENT] requirements for [JURISDICTION/CONDITION]?
Cite the specific code section. Note if local amendments commonly apply.
Flag any uncertainty.
```

---

### Use Case 3: Product Research & Substitutions

**Who uses it:** Estimator, PM
**Trigger:** Submitted product not available; specified product discontinued; value engineering request
**Example queries:**
- "Approved equal to Tremco Vulkem 116 waterproofing membrane"
- "Simpson Strong-Tie LUS connector alternatives"
- "Pella window substitution options for specified product"
- "VOC requirements for interior paint Colorado"
- "Lead time on Carrier commercial rooftop units 2026"

**PM benefit:** Faster submittal review, better vendor alternatives, fewer delays.

---

## Storage Policy

**DO NOT** automatically write Perplexity responses into the Project Brain as facts.

**DO:**
- Store responses as linked research artifacts in `research_queries` table
- Display in Mission Control with review status
- Require explicit PM/Estimator acceptance before linking to Project Brain
- Retain all citations and source URLs

```sql
CREATE TABLE research_queries (
  id SERIAL PRIMARY KEY,
  research_id TEXT UNIQUE NOT NULL,
  project TEXT NOT NULL,
  requestor TEXT NOT NULL,
  topic TEXT,
  query TEXT NOT NULL,
  provider TEXT DEFAULT 'Perplexity',
  model TEXT,
  timestamp TIMESTAMP DEFAULT NOW(),
  response TEXT,
  sources JSONB,
  status TEXT DEFAULT 'Needs Review',
  reviewed_by TEXT,
  reviewed_at TIMESTAMP,
  project_brain_linked BOOLEAN DEFAULT FALSE
);
```

---

## Future Research Topics (After Stable)

Once the initial three use cases are stable, expand into:
- Vendor financial health research
- Product recalls and safety alerts
- Tariff and supply chain impacts
- Sustainability certifications
- OSHA updates and compliance
- Insurance requirements by jurisdiction
- Construction technology trends

---

## Claude Code Sprint 4 Implementation Checklist

- [ ] Create WF-RS-001 Construction Research workflow in n8n
- [ ] Add POST /gateway/research/query to FastAPI gateway
- [ ] Store PERPLEXITY_API_KEY in environment (not in code)
- [ ] Integrate /chat/completions endpoint with model selection logic (sonar vs sonar-pro)
- [ ] Implement standardized system prompt (see above)
- [ ] Create research_queries table in PostgreSQL
- [ ] Store all research results with status: "Needs Review"
- [ ] Link approved research to Project Brain entries (never auto-import)
- [ ] Add regression tests: successful request, API failure/retry, source citation present, research-is-advisory enforcement
- [ ] Wire Material Cost Intelligence use case first
- [ ] Wire Building Code / AHJ use case second
- [ ] Wire Product Substitution use case third
- [ ] Test with a real estimating question on Project 101F

---

*Architecture designed by GBT Cycle 8 | Captured by Browser Claude | 2026-07-01*
