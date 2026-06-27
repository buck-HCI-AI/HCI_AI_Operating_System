# Bid Leveling Service

**Path:** `services/bid_leveling/`  
**API prefix:** `/api/v1/services/bid-leveling/`  
**Tests:** `tests/test_bid_leveling.py` — 22/22 PASS  
**Built:** 2026-06-26  

---

## What It Does

Reads HCI bid tracking Google Sheets, generates per-division bid leveling Excel files (matching the 101 Francis format), and manages the `00_Bids/##_Division/` Drive folder structure — for ALL projects with a configured sheet and Drive folder.

Also exposes raw Google Sheets/Drive read-write endpoints so ChatGPT (GBT) and other AI agents can access bid data and write files directly through the HCI AI API.

---

## Data Flow

```
projects table (gsheet_bid_tracker, drive_folder_id)
    ↓
Google Sheets (Bid Tracking | Sheet1 tab)
    ↓
parse_bid_data() → divisions + vendors + amounts
    ↓
read_division_summary() → leveling status + recommendations
    ↓
read_package_detail() → package breakdown
    ↓
generate_division_excel() → .xlsx bytes (3 sheets per file)
    ↓
[dry_run=True]  → return analysis report, no writes
[dry_run=False] → approval_queue.enqueue() → await Buck approval → execute_upload()
```

---

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/projects` | List all projects with sheet + Drive configured |
| GET | `/projects/{id}/summary` | Division summary from HCI Division Summary tab |
| GET | `/projects/{id}/data` | Full raw bid data (for AI agent consumption) |
| POST | `/projects/{id}/run` | Run bid leveling workflow |
| POST | `/run-all` | Run all configured projects |
| POST | `/projects/{id}/execute-upload/{queue_id}` | Execute an approved queue item |
| POST | `/drive/create-folder` | Create folder in Drive (GBT / AI write) |
| POST | `/drive/upload-file` | Upload any file to Drive (GBT / AI write) |
| GET | `/drive/list/{folder_id}` | List Drive folder contents (GBT / AI read) |
| GET | `/sheets/read` | Read Google Sheets range (GBT / AI read) |
| POST | `/sheets/write` | Write to Google Sheets range (GBT / AI write) |

---

## Run Endpoint

```bash
# Dry run (default) — no writes, returns analysis
curl -X POST -H "X-API-Key: ..." -H "Content-Type: application/json" \
  -d '{"dry_run": true}' \
  http://localhost:8000/api/v1/services/bid-leveling/projects/3/run

# Filter to specific divisions only
curl -X POST -H "X-API-Key: ..." -H "Content-Type: application/json" \
  -d '{"dry_run": true, "divisions": ["15", "16"]}' \
  http://localhost:8000/api/v1/services/bid-leveling/projects/3/run

# Live run — generates Excel files and queues all uploads for Buck approval
curl -X POST -H "X-API-Key: ..." -H "Content-Type: application/json" \
  -d '{"dry_run": false}' \
  http://localhost:8000/api/v1/services/bid-leveling/projects/3/run
```

**Dry run response fields:**
```json
{
  "project": "1355 Riverside",
  "mode": "dry_run",
  "divisions_found": 17,
  "total_bids": 86,
  "bids_folder": {"action": "would_create: '1355 Riverside 00_Bids'"},
  "division_folders": {"16": {"action": "would_create: '16_Electrical'"}},
  "excel_actions": [
    {
      "division": "16",
      "name": "Electrical",
      "filename": "1355_Riverside_Div16_Electrical_Bid_Leveling.xlsx",
      "bids_found": 10,
      "folder_action": "would_create: '16_Electrical'",
      "file_action": "would_upload to folder: TBD"
    }
  ]
}
```

---

## Excel File Format

Each division generates a single `.xlsx` file with 3 sheets:

**Sheet 1: Bid Summary**
- HCI-branded header (blue/gold)
- Division info block: Budget, Leveling Status, Recommended/Low Bid, Risk, Outstanding, Next Action
- Bid comparison table: SUBCONTRACTOR | DATE SENT | DATE REC'D | BID AMOUNT | STATUS | CONTACT | NOTES

**Sheet 2: Package Detail**
- PKG | TRADE PACKAGE | BUDGET | LEVELING STATUS | VENDOR/BIDDER | # BIDS | RECOMMENDED | OUTSTANDING | PRIORITY

**Sheet 3: Outstanding Items**
- Consolidated list of all outstanding issues from division summary + individual bid notes + package issues

**Filename convention:**
`{Project_Name}_Div{##}_{Division_Name}_Bid_Leveling.xlsx`

Example: `1355_Riverside_Div16_Electrical_Bid_Leveling.xlsx`

---

## Drive Folder Structure

```
{Project} Drive Folder/
  {Project} 00_Bids/
    01_General Requirements/
    02_Site Work/
    03_Concrete/
    ...
    16_Electrical/
      1355_Riverside_Div16_Electrical_Bid_Leveling.xlsx
```

**Known 00_Bids folders (pre-existing):**
- 101 Francis: `1YJatvTnK0-vxiHmI0FxVE8e9jUubVcef` (10 division folders already exist)
- 1355 Riverside: created on first live run
- 64 Eastwood: created on first live run

---

## Safety Controls

1. **dry_run=True (default):** No writes. Returns full analysis of what would happen.
2. **dry_run=False:** Generates Excel files and queues uploads via approval queue. Nothing actually writes to Drive until Buck approves.
3. **execute-upload:** Only works on items with `status=approved`. Buck must approve via the approval queue first.
4. **No auto-execution:** The approval queue never auto-executes.

**Approval flow:**
```
run(dry_run=False) → queued_items: [123, 124, ...]
    ↓
GET /api/v1/services/approval-queue/items/123
    ↓
POST /api/v1/services/approval-queue/items/123/approve
    ↓
POST /api/v1/services/bid-leveling/projects/3/execute-upload/123
    ↓ (now actually writes to Drive)
    → file uploaded to correct division folder
```

---

## Google Sheets Tab Name Variants

| Data | 101 Francis / 64 Eastwood | 1355 Riverside |
|------|--------------------------|----------------|
| Bid tracking data | `Bid Tracking` | `Sheet1` |
| Division summary | `HCI Division Summary` | `HCI 16 Div Summary` |
| Package detail | `Bid Leveling Detail` | `Bid Leveling Detail` |

The service auto-detects and tries both variants.

---

## AI Agent Access (GBT / ChatGPT)

GBT can use these endpoints for full read/write bid leveling access:

```
# Read all bid data for a project
GET /api/v1/services/bid-leveling/projects/{id}/data

# Read a specific sheet range
GET /api/v1/services/bid-leveling/sheets/read?sheet_id=SHEET_ID&range_name=Sheet1!A1:Z200

# Write to a sheet
POST /api/v1/services/bid-leveling/sheets/write
  {"sheet_id": "...", "range_name": "Sheet1!A1", "values": [["Value1", "Value2"]]}

# List a Drive folder
GET /api/v1/services/bid-leveling/drive/list/FOLDER_ID

# Create a Drive folder
POST /api/v1/services/bid-leveling/drive/create-folder
  {"parent_folder_id": "...", "folder_name": "My Folder"}

# Upload a file to Drive (content in base64)
POST /api/v1/services/bid-leveling/drive/upload-file
  {"folder_id": "...", "filename": "file.xlsx", "content_b64": "...", "mime_type": "..."}
```

API key: `hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c`
Base URL: `http://localhost:8000` (or via ngrok for external access)

---

## ROI Baseline

| Metric | Manual | AI-Assisted | Saved |
|--------|--------|-------------|-------|
| Bid leveling workflow per project | 90 min | 5 min | 85 min |
| Excel file generation per division | 20 min | <1 min | 19 min |
| Folder structure setup | 15 min | <1 min | 14 min |

---

## Project Configuration

Projects must have both columns populated in the `projects` table:
- `gsheet_bid_tracker`: Google Sheets file ID of the bid tracking spreadsheet
- `drive_folder_id`: Google Drive folder ID of the project's root Drive folder

Current pilot project configuration:
| Project | drive_folder_id | gsheet_bid_tracker |
|---------|----------------|-------------------|
| 64 Eastwood | `1ovKLTSyZhmi4RpP5RD6sdhY0oYjwUCJv` | `1yAmLo3IIp3Vqs3BQJ6QB2O4as0KqXMZxcVvjzGBZDcQ` |
| 101 Francis | `1athsij_coRIngqnIe8SSHQbB51_RyZAs` | `1JExX5CeVBedTEFitM8B6hveF4Prhk0Oy6BZSBu058LE` |
| 1355 Riverside | `1u4DMaAul951QAZgsp5lAKyQwv2EQNHJt` | `1-64X4XGc4P_GmYl7DRt8nGsBNfaVdP_G3qwfBLJSsnA` |
