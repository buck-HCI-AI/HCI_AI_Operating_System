"""
Drawing Reader Service — answers questions about architectural/structural
drawing sets by reading the actual PDF directly with Claude's native PDF
support, instead of relying on semantic text search (which fails for
drawings: sheet numbers like "A3.332" live in title-block graphics, not
extractable body text, and drawing content is mostly graphical).

Built 2026-07-08 after a real demo failure: Adam asked Field GBT to identify
a wood column assembly on sheet A3.332. Field GBT correctly refused to guess
(Drive search couldn't find the sheet, and it can't open Drive share-links
requiring account permission - a GPT Actions platform limitation, not fixable
here) but the underlying gap was real: there was no way to just point at the
actual drawing-set PDF and ask it a question.

Scope: this reads whatever PDF looks most relevant from a project's
04_Drawings Drive folder and asks Claude directly - it does not (yet) do
sheet-boundary OCR/indexing (that's the bigger follow-up scoped in
STRATEGIC_BACKLOG.md). For projects whose drawing sets are a reasonable
page count this works directly; Claude's PDF support caps out around 100
pages / 32MB per request, so very large sets need the "reduced file size"
variant when one exists, and per-request questions should describe a sheet
or area of the building whenever possible.
"""
import os, sys, re, base64, requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bid_leveling"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from base import BaseIntelligenceService
from drive_bid_reader import get_google_token

BASE_URL = "https://www.googleapis.com/drive/v3"

# Keyword -> preference boost when picking which PDF in 04_Drawings to read,
# based on words in the question. Architectural sheet numbers are "A#.###",
# structural are "S#.###" - if the question names a sheet letter, prefer the
# matching discipline's file.
DISCIPLINE_HINTS = {
    "architectural": ["a1.", "a2.", "a3.", "a4.", "a5.", "architectural", "column", "wall", "finish", "trim", "elevation"],
    "structural": ["s1.", "s2.", "s3.", "s4.", "s5.", "structural", "framing", "beam", "footing", "foundation"],
    "civil": ["c1.", "c2.", "civil", "site", "grading", "utility"],
}


def _list_folder(folder_id: str, token: str) -> list:
    r = requests.get(f"{BASE_URL}/files", headers={"Authorization": f"Bearer {token}"}, params={
        "q": f"'{folder_id}' in parents and trashed=false",
        "fields": "files(id,name,mimeType,size)",
        "pageSize": 200, "supportsAllDrives": "true", "includeItemsFromAllDrives": "true",
    }, timeout=30)
    return r.json().get("files", [])


def _find_drawings_folder(drive_folder_id: str, token: str) -> str | None:
    items = _list_folder(drive_folder_id, token)
    for it in items:
        if it["mimeType"] == "application/vnd.google-apps.folder" and re.match(r"^0?4[_\s-]*drawings?$", it["name"], re.IGNORECASE):
            return it["id"]
    return None


def _pick_candidate_pdf(files: list, question: str) -> dict | None:
    q = question.lower()
    discipline = None
    for disc, hints in DISCIPLINE_HINTS.items():
        if any(h in q for h in hints):
            discipline = disc
            break

    pdfs = [f for f in files if f["mimeType"] == "application/pdf"]
    if not pdfs:
        return None

    def score(f):
        name = f["name"].lower()
        s = 0
        if discipline and discipline in name:
            s += 10
        if "reduced" in name or "reduced file size" in name:
            s += 3  # prefer smaller file for the API call when a choice exists
        if "permit" in name or "old" in name or "superseded" in name:
            s -= 5
        return s

    # Group by base name (strip "_reduced file size" variants) so we compare
    # apples to apples, then within the winning group prefer the reduced one.
    pdfs.sort(key=score, reverse=True)
    return pdfs[0]


def _download_bytes(file_id: str, token: str) -> bytes:
    url = f"{BASE_URL}/files/{file_id}?alt=media&supportsAllDrives=true"
    req = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=60)
    return req.content


class DrawingReaderService(BaseIntelligenceService):
    SERVICE_NAME = "drawing_reader"
    STATUS = "active"

    @staticmethod
    def ask(project_code: str, question: str) -> dict:
        row = DrawingReaderService.pg_one(
            "SELECT id, name, drive_folder_id FROM projects WHERE UPPER(project_code)=UPPER(%s)",
            (project_code,)
        )
        if not row:
            return {"error": f"Unknown project code: {project_code}"}
        if not row.get("drive_folder_id"):
            return {"error": f"{project_code} has no Drive folder configured"}

        token = get_google_token("drive")
        drawings_folder = _find_drawings_folder(row["drive_folder_id"], token)
        if not drawings_folder:
            return {"error": f"{project_code} has no 04_Drawings folder in Drive yet - "
                              f"nothing to read. This is a real structural gap, not a search failure."}

        files = _list_folder(drawings_folder, token)
        candidate = _pick_candidate_pdf(files, question)
        if not candidate:
            return {"error": f"{project_code}'s 04_Drawings folder has no PDF files to read"}

        size = int(candidate.get("size") or 0)
        if size > 30 * 1024 * 1024:
            return {
                "error": f"'{candidate['name']}' is {size / 1024 / 1024:.0f}MB - too large to read directly "
                         f"(Claude's PDF limit is ~32MB). Ask for a reduced-file-size version, or narrow the "
                         f"question to a specific discipline (architectural/structural/civil) so a smaller "
                         f"file can be picked."
            }

        pdf_bytes = _download_bytes(candidate["id"], token)

        import anthropic
        from config import settings
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        prompt = (
            f"This is the drawing set '{candidate['name']}' for {row['name']} ({project_code}).\n\n"
            f"Question: {question}\n\n"
            "Answer only from what you can actually see in this document. If the specific sheet or "
            "detail referenced isn't in this file, say so plainly and name what discipline/sheet set "
            "would actually contain it, rather than guessing from adjacent sheets. Cite the sheet "
            "number and page you're reading from when you do have an answer."
        )
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1536,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "document", "source": {
                        "type": "base64", "media_type": "application/pdf",
                        "data": base64.b64encode(pdf_bytes).decode(),
                    }},
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        # response.content[0] isn't reliably a text block - a ThinkingBlock
        # (extended thinking) can come first and has no .text attribute,
        # which crashed every call with "'ThinkingBlock' object has no
        # attribute 'text'" (found live 2026-07-10 via a real Field GPT
        # drawing-extraction job failure, job 990eda01-e38). Filter for the
        # actual text block(s) instead of assuming position.
        text_blocks = [b.text for b in response.content if getattr(b, "type", None) == "text"]
        if not text_blocks:
            return {"error": "Claude returned no text content for this drawing question "
                              f"(response had {len(response.content)} block(s), none were text)"}
        answer = "".join(text_blocks).strip()

        return {
            "project": row["name"],
            "project_code": project_code,
            "question": question,
            "answer": answer,
            "source_file": candidate["name"],
            "source_file_id": candidate["id"],
        }
