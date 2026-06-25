"""
Document ingestion endpoints.
POST /ingest/file  — upload a file for ingestion
POST /ingest/path  — ingest a local file by path
POST /ingest/batch — ingest all files in a directory
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ingestion"))

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

router = APIRouter()


@router.post("/file")
async def ingest_file_upload(
    file: UploadFile = File(...),
    source_system: str = Form(default="api"),
    project_hint: Optional[str] = Form(default=None),
):
    """
    Upload a document for ingestion.
    Runs full pipeline: classify → store in MinIO → embed → register in Postgres.
    """
    from ingest import ingest_bytes
    data = await file.read()
    result = ingest_bytes(data, file.filename or "upload.pdf",
                          source_system=source_system,
                          project_hint=project_hint)
    if result.get("status") == "failed":
        raise HTTPException(422, detail=result)
    return result


@router.post("/path")
def ingest_local_path(
    path: str,
    source_system: str = "filesystem",
    project_hint: Optional[str] = None,
):
    """
    Ingest a file already on the local filesystem (e.g. from Drive mount).
    """
    from ingest import ingest_file
    if not os.path.isfile(path):
        raise HTTPException(404, detail=f"File not found: {path}")
    result = ingest_file(path, source_system=source_system, project_hint=project_hint)
    if result.get("status") == "failed":
        raise HTTPException(422, detail=result)
    return result


@router.post("/batch")
def ingest_batch(
    directory: str,
    source_system: str = "batch",
    project_hint: Optional[str] = None,
    recursive: bool = True,
):
    """
    Ingest all supported files in a directory tree.
    Returns summary: total, ingested, duplicate, failed counts.
    """
    from ingest import ingest_directory
    if not os.path.isdir(directory):
        raise HTTPException(404, detail=f"Directory not found: {directory}")
    return ingest_directory(directory, source_system=source_system,
                            project_hint=project_hint, recursive=recursive)
