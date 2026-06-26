#!/usr/bin/env python3
"""
Knowledge Ingestion Engine — 6-stage pipeline:
  Capture → Classify → Store → Index → Register → Archive

Entry points:
  ingest_file(path, source_system, project_hint)  — file on local filesystem
  ingest_bytes(data, filename, source_system, project_hint)  — from API upload

Each stage is fault-tolerant: failure logs the event but doesn't block downstream
stages unless the failure is unrecoverable (e.g. can't read the file at all).
"""
import os, sys, hashlib, datetime, uuid, tempfile
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

import extractor as _extractor
import classifier as _classifier

# ── Qdrant collection routing by document category ─────────────────────────
COLLECTION_ROUTE: Dict[str, str] = {
    "drawings":              "hci_project_documents",
    "specifications":        "hci_project_documents",
    "bids":                  "hci_project_documents",
    "contracts":             "hci_project_documents",
    "change_orders":         "hci_project_documents",
    "rfis":                  "hci_project_documents",
    "submittals":            "hci_project_documents",
    "meeting_minutes":       "hci_project_documents",
    "daily_reports":         "hci_project_documents",
    "budgets":               "hci_project_documents",
    "schedules":             "hci_project_documents",
    "client_correspondence": "hci_project_documents",
    "vendor_correspondence": "hci_vendor_intelligence",
    "procurement":           "hci_procurement",
    "sop":                   "hci_sops",
    "historical_project":    "hci_historical_costs",
    "template":              "hci_project_documents",
    "registry":              "hci_project_documents",
    "photos":                "hci_project_documents",
    "unknown":               "hci_project_documents",
}

CHUNK_SIZE    = 800
CHUNK_OVERLAP = 100
EMBED_MODEL   = "BAAI/bge-small-en-v1.5"


# ── helpers ────────────────────────────────────────────────────────────────

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _chunk_text(text: str) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def _pg_connect():
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        dbname=os.environ.get("POSTGRES_DB", "hci_os"),
        user=os.environ.get("POSTGRES_USER", "hci_admin"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
    )


def _minio_client():
    from minio import Minio
    endpoint = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
    # strip http:// or https:// prefix if present
    endpoint = endpoint.replace("http://", "").replace("https://", "")
    return Minio(
        endpoint,
        access_key=os.environ.get("MINIO_ROOT_USER", "hci_admin"),
        secret_key=os.environ.get("MINIO_ROOT_PASSWORD", ""),
        secure=False,
    )


def _object_key(classification: Dict, filename: str) -> str:
    """Build MinIO object key: {project}/{category}/{yyyy}/{yyyymmdd}_{filename}"""
    project   = classification.get("project_number") or "UNASSIGNED"
    category  = classification.get("document_category") or "unknown"
    doc_date  = classification.get("document_date") or datetime.date.today().isoformat()
    date_part = doc_date.replace("-", "")
    base      = os.path.splitext(filename)[0]
    ext       = os.path.splitext(filename)[1].lower()
    year      = doc_date[:4]
    return f"{project}/{category}/{year}/{date_part}_{base}{ext}"


def _log_event(conn, document_id: Optional[str], stage: str, status: str, detail: str = ""):
    """Write to document_processing_events if the table exists."""
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM pg_tables WHERE tablename='document_processing_events' AND schemaname='public'"
        )
        if not cur.fetchone():
            return
        cur.execute("""
            INSERT INTO document_processing_events
                (document_id, event_type, event_status, error_details, source_system)
            VALUES (%s, %s, %s, %s, 'ingestion_engine')
        """, (document_id, stage, status, detail or None))
        conn.commit()
    except Exception:
        pass


# ── Stage implementations ──────────────────────────────────────────────────

def _stage_capture(path: str) -> tuple[bytes, str]:
    """Stage 1: Read and validate file. Returns (bytes, filename)."""
    if not _extractor.allowed(path):
        ext = os.path.splitext(path)[1]
        raise ValueError(f"Extension {ext!r} not in allowed list")
    if not _extractor.within_size_limit(path):
        raise ValueError(f"File exceeds {_extractor.MAX_FILE_SIZE_MB} MB limit")
    with open(path, "rb") as f:
        data = f.read()
    return data, os.path.basename(path)


def _stage_classify(filename: str, content: str, project_hint: Optional[str]) -> Dict[str, Any]:
    """Stage 2: Classify the document."""
    aliases = _classifier.load_project_aliases_from_db()
    result = _classifier.classify(filename, content, aliases)
    if project_hint and not result["project_number"]:
        result["project_number"] = project_hint
    return result


def _stage_store(data: bytes, checksum: str, classification: Dict, filename: str) -> Optional[str]:
    """Stage 3: Dedupe check then upload raw file to MinIO.
    Returns object_key on success, None if MinIO unavailable."""
    # Dedupe check in Postgres
    try:
        conn = _pg_connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM pg_tables WHERE tablename='documents' AND schemaname='public'"
        )
        if cur.fetchone():
            cur.execute(
                "SELECT id FROM documents WHERE checksum_sha256 = %s LIMIT 1",
                (checksum,)
            )
            existing = cur.fetchone()
            conn.close()
            if existing:
                return f"__duplicate__{existing[0]}"
        else:
            conn.close()
    except Exception:
        pass

    # Upload to MinIO
    object_key = _object_key(classification, filename)
    try:
        import io
        client = _minio_client()
        client.put_object(
            "hci-raw-documents",
            object_key,
            io.BytesIO(data),
            length=len(data),
            content_type="application/octet-stream",
        )
        return object_key
    except Exception:
        return None


def _stage_index(content: str, classification: Dict, document_id: str,
                 object_key: Optional[str]) -> int:
    """Stage 4: Chunk → embed → upsert Qdrant. Returns chunk count."""
    if not content.strip():
        return 0

    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    from fastembed import TextEmbedding

    chunks  = _chunk_text(content)
    embedder = TextEmbedding(EMBED_MODEL)
    vectors = list(embedder.embed(chunks))

    collection = COLLECTION_ROUTE.get(
        classification.get("document_category", "unknown"),
        "hci_project_documents"
    )

    client = QdrantClient(
        host=os.environ.get("QDRANT_HOST", "localhost"),
        port=int(os.environ.get("QDRANT_PORT", 6333))
    )

    # Generate stable integer IDs from document_id hash + chunk index
    base_id = abs(hash(document_id)) % (10**9)
    points = []
    for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
        points.append(PointStruct(
            id=base_id + i,
            vector=list(vec),
            payload={
                "document_id":       document_id,
                "chunk_index":       i,
                "project_number":    classification.get("project_number") or "",
                "document_category": classification.get("document_category") or "unknown",
                "csi_division":      classification.get("csi_division") or "",
                "version_label":     classification.get("version_label") or "v1",
                "document_date":     classification.get("document_date") or "",
                "original_filename": classification.get("original_filename") or "",
                "storage_object_key": object_key or "",
                "text":              chunk,
            }
        ))

    client.upsert(collection_name=collection, points=points)
    return len(chunks)


def _stage_register(filename: str, checksum: str, object_key: Optional[str],
                    classification: Dict, chunk_count: int, document_id: str) -> Optional[str]:
    """Stage 5: Write metadata row to Postgres documents table.
    Returns the document id (input id if table doesn't exist yet)."""
    try:
        conn = _pg_connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM pg_tables WHERE tablename='documents' AND schemaname='public'"
        )
        if not cur.fetchone():
            conn.close()
            return document_id  # new UUID schema not yet applied — skip, data is in Qdrant

        # Map project_number to project_id via numeric prefix ILIKE (no project_number column)
        project_id = None
        if classification.get("project_number"):
            import re
            m = re.match(r'^(\d+)', str(classification["project_number"]).upper())
            prefix = m.group(1) if m else classification["project_number"]
            cur.execute(
                "SELECT id FROM projects WHERE name ILIKE %s OR address ILIKE %s LIMIT 1",
                (f"{prefix}%", f"{prefix}%")
            )
            row = cur.fetchone()
            if row:
                project_id = row[0]

        title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()

        cur.execute("""
            INSERT INTO documents (
                title, document_category, original_filename, normalized_filename,
                checksum_sha256, storage_bucket, storage_object_key,
                embedding_status, processing_status, extracted_text_available,
                version_label, document_date, csi_division_id,
                source_system, project_id, metadata
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                'embedded', 'extracted', TRUE,
                %s, %s, %s,
                %s, %s, %s::jsonb
            )
            ON CONFLICT (checksum_sha256, storage_bucket) DO NOTHING
            RETURNING id
        """, (
            title,
            classification.get("document_category") or "unknown",
            filename,
            object_key or filename,
            checksum,
            "hci-raw-documents",
            object_key or "",
            classification.get("version_label") or "v1",
            classification.get("document_date"),
            classification.get("csi_division"),
            "ingestion_engine",
            project_id,
            f'{{"chunk_count": {chunk_count}}}',
        ))
        row = cur.fetchone()
        conn.commit()
        conn.close()
        return str(row[0]) if row else document_id
    except Exception:
        return document_id


def _stage_archive(document_id: str, result: Dict):
    """Stage 6: Final status update and event log."""
    try:
        conn = _pg_connect()
        _log_event(conn, document_id, "complete", "completed",
                   f"chunks={result.get('chunks', 0)}, "
                   f"collection={result.get('qdrant_collection', '')}")
        conn.close()
    except Exception:
        pass


# ── Public API ─────────────────────────────────────────────────────────────

def ingest_file(path: str, source_system: str = "filesystem",
                project_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Ingest a file from the local filesystem. Returns result dict.

    Result keys:
      status: 'ingested' | 'duplicate' | 'failed'
      document_id, chunks, qdrant_collection, minio_object_key,
      classification, error (on failure)
    """
    document_id = str(uuid.uuid4())
    result: Dict[str, Any] = {"document_id": document_id, "path": path}

    # Stage 1: Capture
    try:
        data, filename = _stage_capture(path)
    except Exception as e:
        return {**result, "status": "failed", "stage": "capture", "error": str(e)}

    checksum = _sha256(data)
    result["checksum"] = checksum

    # Stage 2: Extract text (needed for classification)
    content = _extractor.extract(path)

    # Stage 3: Classify
    classification = _stage_classify(filename, content, project_hint)
    result["classification"] = classification

    # Stage 4: Store raw in MinIO
    object_key = _stage_store(data, checksum, classification, filename)
    if object_key and object_key.startswith("__duplicate__"):
        existing_id = object_key.replace("__duplicate__", "")
        return {**result, "status": "duplicate", "existing_document_id": existing_id}
    result["minio_object_key"] = object_key

    # Stage 5: Index in Qdrant
    try:
        chunk_count = _stage_index(content, classification, document_id, object_key)
        collection = COLLECTION_ROUTE.get(
            classification.get("document_category", "unknown"), "hci_project_documents"
        )
        result["chunks"] = chunk_count
        result["qdrant_collection"] = collection
    except Exception as e:
        result["index_error"] = str(e)
        chunk_count = 0

    # Stage 6: Register in Postgres
    db_id = _stage_register(filename, checksum, object_key, classification, chunk_count, document_id)
    result["document_id"] = db_id

    # Stage 7: Archive (log completion)
    _stage_archive(db_id, result)

    result["status"] = "ingested"
    return result


def ingest_bytes(data: bytes, filename: str, source_system: str = "api",
                 project_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Ingest document from raw bytes (API upload path).
    Writes to a temp file and delegates to ingest_file.
    """
    ext = os.path.splitext(filename)[1].lower()
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        return ingest_file(tmp_path, source_system=source_system, project_hint=project_hint)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def ingest_directory(directory: str, source_system: str = "batch",
                     project_hint: Optional[str] = None,
                     recursive: bool = True) -> Dict[str, Any]:
    """
    Batch-ingest all supported files in a directory.
    Returns summary dict with per-file results.
    """
    import glob
    pattern = os.path.join(directory, "**", "*") if recursive else os.path.join(directory, "*")
    files = [f for f in glob.glob(pattern, recursive=recursive)
             if os.path.isfile(f) and _extractor.allowed(f)]

    results = {"total": len(files), "ingested": 0, "duplicate": 0, "failed": 0, "files": []}
    for path in files:
        r = ingest_file(path, source_system=source_system, project_hint=project_hint)
        results["files"].append({"path": path, "status": r["status"]})
        results[r.get("status", "failed")] = results.get(r.get("status", "failed"), 0) + 1
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 ingest.py <file_path> [project_hint]")
        sys.exit(1)
    path = sys.argv[1]
    hint = sys.argv[2] if len(sys.argv) > 2 else None
    result = ingest_file(path, project_hint=hint)
    import json
    print(json.dumps(result, indent=2, default=str))
