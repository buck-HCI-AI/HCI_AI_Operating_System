# PLAN_READER_ARCHITECTURE_SPEC.md
## HCI AI OS — Construction Plan Reader Architecture

**Chief Architect:** GBT (Cycle 8)
**Captured by:** Browser Claude
**Date:** 2026-07-01
**Context:** We already have Gemini in n8n doing initial plan reading. This spec defines what Gemini should do, its limits, and the full multi-engine pipeline beyond it.

---

## Chief Architect Ruling

> "Keep Gemini in n8n, but constrain it to: **summarize, classify, flag, and draft.** Do not ask Gemini alone to be the plan reader."

> "The real HCI Plan Reader should be a pipeline: **PyMuPDF/pdfplumber + Unstructured + OpenCV/OCR + Gemini + Qdrant + Autodesk APS** when source models exist."

> "That gives HCI both AI reasoning and deterministic construction-document extraction."

---

## Part 1: What Gemini in n8n Should Be Doing Today

Gemini should be the **first-pass drawing reviewer, not the authoritative plan engine.**

### A. Sheet-Level Summaries

For each uploaded plan PDF, Gemini should return:
- Sheet number
- Sheet title
- Discipline (Architectural, Structural, MEP, Civil, etc.)
- Issue/revision date
- Drawing set name
- Visible revision markers
- General scope shown on the sheet
- Obvious construction concerns

```json
{
  "project": "101F",
  "drawing_set": "Permit Set",
  "sheets": [
    {
      "sheet": "A2.1",
      "title": "Floor Plan",
      "discipline": "Architectural",
      "date": "2026-06-14"
    }
  ]
}
```

### B. Drawing Index Extraction

Gemini identifies the drawing index sheet and extracts the structured sheet list.

### C. Revision Comparison Support

Gemini can compare two PDFs or two rendered sheet images and describe likely changes: added notes, removed notes, changed dimensions, revised room names, changed detail references, updated schedules.

> Note: Gemini should not be trusted alone for final change detection.

### D. RFI Candidate Detection

Gemini reads the sheet and flags:
- Conflicting notes
- Missing details
- Spec/drawing conflicts
- Unclear scope items
- Conditions needing field clarification

### E. Bid Package Impact Classification

Gemini reads each sheet and returns which bid packages are affected:

```json
{
  "sheet": "P3.1",
  "title": "Plumbing Fixture Schedule",
  "bid_packages": ["Plumbing", "HVAC", "Rough Framing"],
  "confidence": 0.78
}
```

---

## Part 2: Gemini's Limits

**Do not use Gemini for:**

1. **Precise dimension extraction** — Gemini reads text and images but cannot reliably extract numeric dimensions from CAD drawings with accuracy.
2. **Structured schedule extraction** — Door/window/finish/equipment schedules require deterministic table parsers (pdfplumber) not visual AI.
3. **Scanned/low-quality drawings** — Gemini struggles with low-DPI scans, handwritten markups, dense linework, stamps, rotated text.
4. **Sheet-to-sheet cross-referencing** — Gemini cannot reliably resolve detail references across multiple sheets in a set.
5. **OCR uncertainty** — Rotated notes, dense schedules, handwritten markups, and overlapping linework produce errors.
6. **Legal/contract authority** — Gemini should assist review, not declare scope complete or issue official interpretations.

> **The rule: Gemini describes and flags. It does not quantify, certify, or govern.**

---

## Part 3: What to Wire In Beyond Gemini

GBT recommendation: build a **multi-engine drawing pipeline**, not replace Gemini.

### Tool 1 — Autodesk Platform Services (APS) Model Derivative API

**Use when:** HCI receives Revit, DWG, IFC, or model-based files from the design team.

**Why:**
- Extracts object hierarchy from BIM models
- Extracts object properties (room names, areas, materials, equipment specs)
- Renders drawings/views from the model
- Supports model derivative workflows (2D/3D views, viewable manifests)

**API:** Autodesk Platform Services (APS) — formerly Forge.
**Auth:** OAuth 2.0 two-legged (client credentials) for server-to-server.
**Endpoint:** `https://developer.api.autodesk.com/modelderivative/v2/designdata/{urn}/manifest`

**Use cases:**
- Extract room data from Revit model
- Get equipment list from MEP model
- Extract door/window schedule from architectural model
- Generate PDF views of each discipline

**When to use:** When design team uses Revit/AutoCAD and can share the source file. Do not require this of all projects.

---

### Tool 2 — Unstructured (hi_res PDF partitioning)

**What it is:** Python library for document partitioning. Separates titles, tables, text blocks, and layout elements from PDFs.

**Why:** Better than asking Gemini to read every page cold. Gives structured document chunks that LLMs can review.

**Install:** `pip install unstructured[pdf]`
**Strategy:** `hi_res` (enables correct document element classification and table extraction)

**Use cases:**
- Schedules (door, window, finish, equipment)
- Sheet notes
- Drawing indexes
- Specification tables
- Finish schedules

```python
from unstructured.partition.pdf import partition_pdf

elements = partition_pdf(
    filename="A2.1_floor_plan.pdf",
    strategy="hi_res",
    infer_table_structure=True
)

tables = [e for e in elements if e.category == "Table"]
text_blocks = [e for e in elements if e.category == "NarrativeText"]
```

---

### Tool 3 — PyMuPDF + pdfplumber

**Use:** Locally, in FastAPI plan-ingestion service. Deterministic PDF extraction.

**PyMuPDF** (`pip install pymupdf`) for:
- Page rendering to high-resolution images (for Gemini/vision analysis)
- Text block coordinates and bounding boxes
- Annotations extraction
- Embedded vector/text extraction

**pdfplumber** (`pip install pdfplumber`) for:
- Tables with coordinate-aware extraction
- Text layout preservation
- Title block region reading

```python
import fitz  # PyMuPDF

doc = fitz.open("plan_set.pdf")
for page_num, page in enumerate(doc):
    # Render high-res image for Gemini
    mat = fitz.Matrix(3, 3)  # 3x scale = 216 DPI
    pix = page.get_pixmap(matrix=mat)
    pix.save(f"page_{page_num}.png")
    
    # Extract text blocks with coordinates
    blocks = page.get_text("dict")["blocks"]
```

```python
import pdfplumber

with pdfplumber.open("plan_set.pdf") as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        text = page.extract_text()
```

---

### Tool 4 — OpenCV + Tesseract/PaddleOCR

**Use for:** Scanned drawings and image-heavy sheets.

**OpenCV** handles:
- Line detection (identify drawing borders, title blocks)
- Contour detection
- Title block region cropping
- Image preprocessing (deskew, denoise, enhance contrast)

**Tesseract OCR** (`pip install pytesseract`) for standard scanned text.
**PaddleOCR** for higher-accuracy OCR on dense technical drawings.

```python
import cv2
import pytesseract

img = cv2.imread("scanned_sheet.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
denoised = cv2.fastNlMeansDenoising(gray)
text = pytesseract.image_to_string(denoised, config="--psm 6")
```

**Use cases:**
- Scanned plan sets (not digital PDFs)
- Handwritten superintendent markup photos
- Title block OCR when embedded text is missing
- Detail bubble and callout detection

---

### Tool 5 — Qdrant (Multimodal Plan Memory)

**Already in HCI AI OS.** Use it for drawing memory.

**Store:**
- Sheet summaries (text embeddings)
- Extracted text per sheet
- Title block metadata
- Detail references
- RFI candidates
- Bid package impacts
- Image embeddings of sheet thumbnails (via CLIP or OpenAI embeddings)

**Queries enabled:**
- "Show me every sheet mentioning waterproofing."
- "Which sheets changed in the latest architectural set?"
- "Find similar stair details from prior projects."
- "What RFIs were raised from sheets like this?"

> This turns plan reading into **Project Brain memory** — searchable across all projects over time.

---

## Part 4: Full Pipeline Architecture

```
Shared Drive / n8n plan upload trigger
        ↓
n8n detects new/changed PDF in Google Drive / SharePoint
        ↓
FastAPI POST /plans/ingest
        ↓
PyMuPDF renders pages + extracts text blocks
        ↓
Unstructured hi_res extracts layout + tables
        ↓
Gemini performs sheet summary + issue detection
        ↓
OpenCV/OCR handles scanned or low-quality sheets
        ↓
Qdrant stores searchable plan memory
        ↓
Project Brain updates drawing index + plan review record
        ↓
Mission Control flags new issues/RFI candidates
```

### Minimum JSON Output Per Sheet

```json
{
  "project_code": "101F",
  "sheet_number": "A2.1",
  "sheet_title": "Main Level Floor Plan",
  "discipline": "Architectural",
  "revision": "ASI-02",
  "date": "2026-07-01",
  "key_notes": [],
  "detail_references": [],
  "schedule_references": [],
  "possible_rfis": [],
  "affected_bid_packages": [],
  "confidence": 0.82,
  "source_file": "101F_PermitSet_2026-07-01.pdf"
}
```

---

## Part 5: Recommended Implementation Order

**Phase 1 — Make Gemini Useful and Bounded (Now)**
- Sheet summaries
- Drawing index extraction
- Discipline classification
- RFI candidates
- Bid package impact classification
- Store outputs in Project Brain

**Phase 2 — Add Deterministic PDF Extraction (Sprint 4)**
- PyMuPDF for page rendering
- pdfplumber for schedule/table extraction
- Unstructured hi_res for layout partitioning
- Title block parsing

**Phase 3 — Add Visual/Layout Intelligence (Sprint 4-5)**
- OpenCV image preprocessing
- OCR fallback (Tesseract or PaddleOCR)
- Revision cloud detection candidates
- Detail bubble / callout detection

**Phase 4 — Add Autodesk APS (When source models available)**
- Revit/DWG/IFC ingestion via APS Model Derivative API
- Object metadata extraction
- Model-derived quantity takeoffs

**Phase 5 — Build the Drawing Graph**
- Sheet-to-sheet detail references
- Room-to-finish relationships
- Spec-to-drawing links
- Bid-package-to-sheet links
- RFI-to-sheet history

---

## Claude Code Sprint 4 Checklist

- [ ] Constrain Gemini in n8n to: sheet summaries, drawing index, discipline classification, RFI candidates, bid package impacts
- [ ] Create FastAPI POST /plans/ingest endpoint
- [ ] Add PyMuPDF page renderer (3x scale for Gemini vision input)
- [ ] Add pdfplumber schedule/table extractor
- [ ] Add Unstructured hi_res PDF partitioner
- [ ] Define minimum JSON output schema per sheet
- [ ] Store sheet JSON in Project Brain (drawing index)
- [ ] Store sheet embeddings in Qdrant for plan memory search
- [ ] Add n8n trigger: detect new PDF in Google Drive / SharePoint
- [ ] Wire trigger to FastAPI /plans/ingest
- [ ] Test with Project 101F drawing set
- [ ] Add OpenCV + OCR for scanned sheets (Phase 3, can defer)
- [ ] Evaluate Autodesk APS when design team uses Revit (Phase 4)

---

*Architecture designed by GBT Cycle 8 | Captured by Browser Claude | 2026-07-01*
