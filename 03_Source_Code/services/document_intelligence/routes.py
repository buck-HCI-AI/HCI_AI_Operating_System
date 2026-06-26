"""Document Intelligence routes — /api/v1/services/document-intelligence"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, Query, UploadFile, File
from typing import Optional
from document_intelligence_svc import DocumentIntelligenceService

router = APIRouter()

@router.get("")
def service_info():
    return DocumentIntelligenceService.info()

@router.get("/search")
def search_documents(
    q: str,
    project: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
):
    return DocumentIntelligenceService.search_documents(q, project, category)

@router.get("/classify")
def classify_document(filename: str, content_preview: str = ""):
    return DocumentIntelligenceService.classify_document(filename, content_preview)

@router.post("/ingest")
def ingest_document(path: str, source_system: str = "api", project_hint: Optional[str] = None):
    return DocumentIntelligenceService.ingest_document(path, source_system, project_hint)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_hint: Optional[str] = None,
):
    """Accept file upload, run through the 6-stage ingestion pipeline."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ingestion"))
    from ingest import ingest_bytes
    data = await file.read()
    return ingest_bytes(data, file.filename, source_system="api_upload", project_hint=project_hint)
