"""
Object storage endpoints — MinIO bucket and object operations.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from typing import Optional
import services.storage as svc

router = APIRouter()


@router.get("/buckets")
def list_buckets():
    """List all MinIO buckets."""
    try:
        return {"buckets": svc.list_buckets()}
    except Exception as e:
        raise HTTPException(503, f"MinIO unavailable: {e}")


@router.get("/buckets/{bucket}")
def list_objects(
    bucket: str,
    prefix: str = Query(default=""),
    limit:  int = Query(default=100, le=1000),
):
    """List objects in a bucket with optional prefix filter."""
    try:
        objects = svc.list_objects(bucket, prefix=prefix, limit=limit)
        return {"bucket": bucket, "prefix": prefix, "count": len(objects), "objects": objects}
    except Exception as e:
        raise HTTPException(503, f"Storage error: {e}")


@router.post("/buckets/{bucket}/upload")
async def upload_object(
    bucket: str,
    file: UploadFile = File(...),
    key_prefix: Optional[str] = Query(default=""),
):
    """Upload a file to a MinIO bucket. Returns the object key."""
    try:
        data = await file.read()
        key = f"{key_prefix}/{file.filename}".lstrip("/") if key_prefix else file.filename
        svc.put_object(bucket, key, data, content_type=file.content_type or "application/octet-stream")
        url = svc.get_presigned_url(bucket, key, expires_minutes=60)
        return {"bucket": bucket, "key": key, "size": len(data), "download_url": url}
    except Exception as e:
        raise HTTPException(503, f"Upload failed: {e}")


@router.get("/buckets/{bucket}/download")
def get_download_url(
    bucket: str,
    key: str = Query(...),
    expires_minutes: int = Query(default=60),
):
    """Get a presigned download URL for an object."""
    try:
        if not svc.object_exists(bucket, key):
            raise HTTPException(404, f"Object {key!r} not found in {bucket}")
        url = svc.get_presigned_url(bucket, key, expires_minutes)
        return {"bucket": bucket, "key": key, "download_url": url, "expires_minutes": expires_minutes}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(503, f"Storage error: {e}")


@router.delete("/buckets/{bucket}/objects")
def delete_object(bucket: str, key: str = Query(...)):
    """Delete an object from a bucket. Permanent — no undo."""
    try:
        if not svc.object_exists(bucket, key):
            raise HTTPException(404, f"Object {key!r} not found in {bucket}")
        svc.delete_object(bucket, key)
        return {"status": "deleted", "bucket": bucket, "key": key}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(503, f"Storage error: {e}")
