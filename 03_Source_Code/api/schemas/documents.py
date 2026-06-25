"""Document metadata schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    id: str
    title: str
    document_category: str
    original_filename: str
    storage_bucket: Optional[str] = None
    storage_object_key: Optional[str] = None
    checksum_sha256: Optional[str] = None
    project_number: Optional[str] = None
    csi_division: Optional[str] = None
    version_label: Optional[str] = None
    document_date: Optional[str] = None
    processing_status: Optional[str] = None
    embedding_status: Optional[str] = None
    source_system: Optional[str] = None
    created_at: Optional[datetime] = None


class DocumentListResponse(BaseModel):
    total: int
    items: list[DocumentResponse]


class DocumentIngestResponse(BaseModel):
    status: str
    document_id: str
    chunks: Optional[int] = None
    qdrant_collection: Optional[str] = None
    minio_object_key: Optional[str] = None
    classification: Optional[dict] = None
