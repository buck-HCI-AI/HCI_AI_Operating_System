"""
Document metadata endpoints.
CRUD against the PostgreSQL documents table + presigned download URLs from MinIO.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import services.db as db
import services.storage as storage

router = APIRouter()


@router.get("")
def list_documents(
    project_number: Optional[str] = Query(default=None),
    category:       Optional[str] = Query(default=None),
    status:         Optional[str] = Query(default=None),
    limit:          int           = Query(default=50, le=200),
    offset:         int           = Query(default=0),
):
    """List documents with optional filters. Requires new UUID schema."""
    if not db.table_exists("documents"):
        return {"items": [], "total": 0,
                "note": "documents table not yet created — apply database/schema/002_document_storage_schema.sql"}

    conditions, params = ["1=1"], []
    if project_number:
        # join to projects to filter by project_number
        conditions.append("""
            project_id IN (SELECT id FROM projects WHERE project_number = %s)
        """)
        params.append(project_number)
    if category:
        conditions.append("document_category = %s")
        params.append(category)
    if status:
        conditions.append("processing_status = %s")
        params.append(status)

    where = " AND ".join(conditions)
    total = db.query_one(f"SELECT COUNT(*) as n FROM documents WHERE {where}", params)["n"]
    rows  = db.query(
        f"SELECT * FROM documents WHERE {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
        params + [limit, offset]
    )
    return {"total": total, "limit": limit, "offset": offset, "items": rows}


@router.get("/{document_id}")
def get_document(document_id: str):
    """Get a single document by ID."""
    if not db.table_exists("documents"):
        raise HTTPException(404, "documents table not yet created")
    row = db.query_one("SELECT * FROM documents WHERE id = %s", (document_id,))
    if not row:
        raise HTTPException(404, f"Document {document_id} not found")
    return row


@router.get("/{document_id}/download")
def get_download_url(document_id: str, expires_minutes: int = 60):
    """Get a presigned MinIO download URL for the document's raw file."""
    if not db.table_exists("documents"):
        raise HTTPException(404, "documents table not yet created")
    row = db.query_one(
        "SELECT storage_bucket, storage_object_key FROM documents WHERE id = %s",
        (document_id,)
    )
    if not row:
        raise HTTPException(404, f"Document {document_id} not found")
    if not row.get("storage_object_key"):
        raise HTTPException(404, "No file stored for this document")
    try:
        url = storage.get_presigned_url(
            row["storage_bucket"], row["storage_object_key"], expires_minutes
        )
        return {"download_url": url, "expires_minutes": expires_minutes}
    except Exception as e:
        raise HTTPException(503, f"Storage unavailable: {e}")


@router.patch("/{document_id}/status")
def update_document_status(document_id: str, processing_status: str):
    """Update document processing status."""
    if not db.table_exists("documents"):
        raise HTTPException(404, "documents table not yet created")
    db.execute(
        "UPDATE documents SET processing_status = %s WHERE id = %s",
        (processing_status, document_id)
    )
    return {"status": "updated", "document_id": document_id, "processing_status": processing_status}
